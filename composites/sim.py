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
		self.solved = False
		self.loaded = False
	
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

		self.loaded = True
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

		self.loaded = True
		if do_return:
			return self.k,self.e_k

	def _compute_off_strain(self):
		# pos = ['bot','top']{
				# self.off_strain = {}
				# for layer in self.laminate.layers:
				# 	index = layer.index
				# 	self.off_strain['%s_%s' % (index,pos[0])] = self.e0 + self.e_k[index*2]
				# 	self.off_strain['%s_%s' % (index,pos[1])] = self.e0 + self.e_k[index*2+1]}
		self.off_strain = numpy.empty((self.laminate.num_of_layers(),2,3), dtype = float)
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
		Q_on = self.laminate.layers[0].Q_on
		trans = lambda x:numpy.vstack(x).T 
		og_shape = numpy.shape(self.on_strain)
		self.on_stress = Q_on.dot(trans(self.on_strain)).T.reshape(og_shape)

	def _compute_off_stress(self):
		self.off_stress = numpy.empty_like(self.on_stress)
		for layer in self.laminate.layers:
			off_stress_bot = transform_stress(self.on_stress[layer.index,0,:],
																			'on',
																			layer.theta)
			off_stress_top = transform_stress(self.on_stress[layer.index,1,:],
																			'on',
																			layer.theta)
			self.off_stress[layer.index,:,:] = numpy.vstack((off_stress_bot,
																										off_stress_top
																										))

	def solve(self):
		if not self.loaded:
			print "Nothing to solve. Apply loads before solving."
			return

		self._compute_off_strain()
		self._compute_on_strain()
		self._compute_on_stress()
		self._compute_off_stress()
		self.solved = True

	def return_results(self, in_latex = True):
		if not self.solved:
			self.solve()

		import numpy as np
		import pandas as pd
		import sympy
		from sympy import latex as stex


		off_strain = np.vstack(self.off_strain) 
		on_strain = np.vstack(self.on_strain)
		on_stress = np.vstack(self.on_stress)
		off_stress = np.vstack(self.off_stress)
		stacks = np.round(np.hstack((off_strain,
                   							on_strain,
                   							on_stress,
                   							)),
                			decimals = 4
                			)
		if in_latex:
			make_columns = lambda *args: [stex('$%s$'%arg) for arg in args]
			columns = make_columns('\epsilon_1','\epsilon_2','\epsilon_6',
	                       '\epsilon_x','\epsilon_y','\epsilon_s',
	                       '\sigma_x','\sigma_y','\sigma_s')
			# columns.append('Ply Number')
			rows = [ stex('%i (%i$^\circ$) - %s' % (layer.index,layer.theta,pos)) \
					 for layer in self.laminate.layers for pos in ['Bot','Top']]
		else:
			columns = ('epsilon_1','epsilon_2','epsilon_6',
	               'epsilon_x','epsilon_y','epsilon_s',
	               'sigma_x','sigma_y','sigma_s')
			rows = [ '%i (%i) - %s' % (layer.index,layer.theta,pos) \
					 for layer in self.laminate.layers for pos in ['Bot','Top']]
					 
		d_onstrain = pd.DataFrame(data = stacks
                          		,columns=columns
                          		,dtype = float
                          	)

		d_onstrain['Ply Number'] = rows
		d_onstrain.set_index('Ply Number',inplace = True)

		# pieces = [d_onstrain[i:i+2] for i in range(0
		# 																					,len(off_strain)
		# 																					,2)
							# ]
		# rows = [stex('Ply %i (%i$^\circ$)' % (layer.index,layer.theta)) \
		# 			 for layer in self.laminate.layers \
		# 			 ]
		return d_onstrain
		# return pd.concat(pieces,keys = rows)
			
if __name__ == '__main__':
	# sigma_on = transform_strain([0.0659,-0.0471,-0.0832],'off',30, do_debug = True)
	# print sigma_on
	layups = ['0/90/0/90s','0/45/0/-45s','0/45/0/90s','0/-45/0/45s','p45s']
	for layup in layups:
		sim = Sim(laminate = Laminate(layup,1))
		sim.apply_M([1,0,0]*ureg.GN)
		sim.solve()
		df =  sim.return_results(False)
		print '----' * 10
		print '----' * 10
		print "layup = %s " % layup
		print df['sigma_x'],df['sigma_y'],df['sigma_s']
