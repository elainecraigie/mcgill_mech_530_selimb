"""Provides:
  o functions to transform strain/stress from off-axis to on-axis 
		and vice-versa..
	o Sim class used to apply loads on laminate

Transforms strain/stress from off-axis to on-axis and vice-versa.
"""
import numpy
from math import cos,sin,radians
from __init__ import ureg, Q_
from laminate import Laminate

def transform_stress(values,input_axis,angle, do_debug = False):
	"""
	Transform stress from on-axis to off-axis and vice-versa.

	Arguments:
	-values : List or vector of stresses or strains [1,2,6] or [x,y,s]
	-Input_axis : 'on' or 'off'
		The opposite will be returned
	-Angle:
		In degrees. Angle positive in counter-clockwise rotation.
		Don't input modified angle.
	"""
	if input_axis == 'on':
		angle = radians(-1*float(angle))
	elif input_axis == 'off':
		angle = radians(float(angle))
	else:
		raise AssertionError("%s not valid for transform" % input_axis)

	# A = numpy.array([[1, cos(2*angle), sin(2*angle)],
	# 								[1, -cos(2*angle), -sin(2*angle)],
	# 								[0, -sin(2*angle), cos(2*angle)]
	# 								])
	p = float((values[0]+values[1])/2.0)
	q = float((values[0]-values[1])/2.0)
	r = float(values[2])
	# b = numpy.array([p,q,r])
	A = numpy.array([[p,q,r],[p,-q,-r],[0,r,-q]])
	b = numpy.array([1,cos(2*angle),sin(2*angle)]) 
	if do_debug:
		print "p : %f" % p
		print "q : %f" % q
		print "r : %f" % r
		print "A : ", A
		print "b : ",b
	ret_array = A.dot(b)
	return ret_array

def transform_strain(values,input_axis,angle, do_debug = False):
	"""
	Transform strain from on-axis to off-axis and vice-versa.
	
	Arguments:
	-values : List or vector of stresses or strains [1,2,6] or [x,y,s]
	-Input_axis : 'on' or 'off'
		The opposite will be returned
	-Angle:
		In degrees. Angle positive in counter-clockwise rotation.
		Don't input modified angle.
	"""
	if input_axis == 'on':
		angle = radians(-1*float(angle))
	elif input_axis == 'off':
		angle = radians(float(angle))
	else:
		raise AssertionError("%s not valid for transform" % input_axis)
	p = float((values[0]+values[1])/2.0)
	q = float((values[0]-values[1])/2.0)
	r = float(values[2]/2.0)

	A = numpy.array([[p,q,r],[p,-q,-r],[0, 2*r, -2*q]])
	b = numpy.array([1, cos(2*angle), sin(2*angle)])
	if do_debug:
		print "p : %f" % p
		print "q : %f" % q
		print "r : %f" % r
		print "A : ", A
		print "b : ",b
		
	ret_array = A.dot(b)
	return ret_array

class Sim(object):
	def __init__(self, **kwargs):
		# if isinstance(laminate,Laminate):
		# 	self.laminate = laminate
		# else:
		# 	raise TypeError("Input argument must be of type 'composites.Laminate'")
		x = kwargs
		try:
			self.laminate = x['laminate']
			print "Found it!"
		except AttributeError as e: #['laminate'] does not contain a Laminate
			raise AttributeError("'laminate' must point to 'Laminate' object \n"+e.message)
		except KeyError:
			try:
				self.laminate = Laminate(x['layup'],x['materialID'])
			except KeyError:
				raise KeyError("Could not find keyword args 'laminate' or 'layup' and 'id'")

		self.laminate.compute_all()
		self.e0 = numpy.zeros((3,))   #Average strain from overall in-plane stress 'N'
		self.e_k = None
	
	@ureg.wraps(None, (None,ureg.GNperm))
	def apply_N(self,N_input,do_return = False):
		"""Obtain off-axis strain from applied 3D average load N to laminate.
		Load N must be 3-dimensional AND use units.
		"""
		try:
			N = numpy.array(N_input,dtype=float).reshape(3,)
			self.e0 = self.laminate.a.dot(N)
		except ValueError:
			raise ValueError("Could not reshape %r to a 'float' 3D array" % N_input)

		if do_return:
			return self.e0

	@ureg.wraps(None, (None,ureg.GN,None))
	def apply_M(self,M_input,do_return = False):
		try:
			M = numpy.array(M_input,dtype=float).reshape(3,)
			self.k = self.laminate.d.dot(M)
		except ValueError:
			raise ValueError("Could not reshape %r to a 'float' 3D array" % M_input)

		self.e_k = numpy.empty((self.laminate.num_of_layers(),2,3), dtype = float)
		for layer in self.laminate.layers:
			z_bot,z_top = layer.get_z()
			index = layer.index
			self.e_k[index,:,:] = numpy.vstack((z_bot*self.k, 
																					z_top*self.k)
																				 )

		if do_return:
			return self.k,self.e_k

	def _compute_off_strain(self):
		# pos = ['bot','top']{
				# self.off_strain = {}
				# for layer in self.laminate.layers:
				# 	index = layer.index
				# 	self.off_strain['%s_%s' % (index,pos[0])] = self.e0 + self.e_k[index*2]
				# 	self.off_strain['%s_%s' % (index,pos[1])] = self.e0 + self.e_k[index*2+1]}
		self.off_strain = numpy.empty_like(self.e_k)
		if self.e_k is None:
			self.off_strain[:,:,:] = self.e0
		else:
			self.off_strain[:,:,:] = self.e_k + self.e0

	def _compute_on_strain(self):
		self.on_strain = numpy.empty_like(self.off_strain)
		for layer in self.laminate.layers:
			on_strain_bot = transform_strain(self.off_strain[layer.index,0,:],
																			'off',
																			layer.theta)
			on_strain_top = transform_strain(self.off_strain[layer.index,1,:],
																			'off',
																			layer.theta)
			self.on_strain[layer.index,:,:] = numpy.vstack((on_strain_bot,
																										on_strain_top
																										))

	def _compute_on_stress(self):
		#Black magic
		Q_on = self.laminate.layers[0].Q_on
		temp_shape = ((3,self.laminate.num_of_layers()*2))
		og_shape = shape(self.on_strain)
		self.on_stress = Q_on.dot(self.on_strain.reshape(temp_shape).T.reshape(og_shape)

	def _compute_on_stress(self):
		raise NotImplementedError

	def solve(self):
		raise NotImplementedError

	def return_results(self,do_display = True):
		raise NotImplementedError

		if do_display:
			print off_strain
			print on_strain
			print on_stress
		else:
			return off_strain,on_strain,on_stress

if __name__ == '__main__':
	# sigma_on = transform_strain([0.0659,-0.0471,-0.0832],'off',30, do_debug = True)
	# print sigma_on
	my_sim = Sim(layup = '0_4/90_4s',materialID = 1)
	P = -100 * ureg.N
	L = 0.1 * ureg.meter
	b = 0.01 * ureg.meter
	moment = P*L/(4*b)
	M = Q_([moment.magnitude,0,0],moment.units)
	k,e = my_sim.apply_M(M,do_return = True)
	print my_sim.laminate.num_of_layers()
	print e.shape
	print e
	print '----' * 6
	# my_sim._compute_off_strain()
	print '----' * 6