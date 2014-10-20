"""
This module provides a Laminate class.
A Laminate is given a layup and a materialID and optionally a core thickness.
Laminate composes itself of necessary layers.
In-plane and flexural compliance/modulus matrices are calculated.  
Loads and stuff are applied within applyloads module
"""

def make_array(a):
		"""Expecting vector with following values
		11,22,12,66,16,26
		"""
		indices = ['11','22','12','66','16','26']
		import numpy
		# vec = {indices[i]:a[i] for i in range(len(a))}
		arr = numpy.ones((3,3),numpy.float)
		arr[0,:] = a[0],a[2],a[4]
		arr[1,:] = a[2],a[1],a[5]
		arr[2,:] = a[4],a[5],a[3]
		return arr

def make_vec(the_array):
	"""Expect numpy array
	"""
	vec=[]
	vec.append(the_array[0,0]) 
	vec.append(the_array[1,1]) 
	vec.append(the_array[0,1]) 
	vec.append(the_array[2,2]) 
	vec.append(the_array[0,2]) 
	vec.append(the_array[1,2]) 
	return vec

from parsetools import parse_layup, parse_request
import layer
do_display = False

class Laminate(object):
	"""Laminate(layup, materialID, compute = <method>) -> Laminate 
composed of layers with various orientations but the same material properties. 

Arguments:
	-layup : layup as a string. See parselayup.py
	-materialID : ID of the wanted material
	-core_thick : Thickness of the honeycomb core in meters
		Note: There must be an even number of plies for the core to be properly 
		taken into account.
	-compute = 'dumb' or 'smart'. Smart uses symmetry if possible.
	"""
	def __init__(self, layup, materialID, core_thick = 0.0, compute = None):

		self.layup, self.symmetric = parse_layup(layup)
		self.layers = [] 

		counter = 0
		for orientation in self.layup:
			new_layer = layer.Layer(materialID,orientation)
			new_layer.set_index(counter)
			counter += 1
			self.layers.append(new_layer)

		self.total_ply_thickness = len(self.layup)*self.layers[0].PROPS['h0']/1000
		if core_thick != 0.0:
			assert(core_thick>0.0)
			self.has_core = True
		else:
			self.has_core = False

		self.zc = float(core_thick)
		self.total_thickness = self.total_ply_thickness + self.zc
		self._assign_h()
		self.computed = False
		if compute is not None:
			self.compute_all()

	def num_of_layers(self):
		return len(self.layers)
		
	def _assign_h(self):
		import numpy
		h = self.total_thickness/2.0 #Total thickness of ply
		h0 = self.layers[0].PROPS['h0']/1000.0 #Thickness of one ply
		zc = self.zc #Thickness of core
		mid_ply_index = len(self.layers)/2

		z_bot = -h
		z_top = z_bot + h0

		self.z_array = numpy.zeros((len(self.layers),2))
		counter = 0
		for layer in self.layers:
			if self.has_core and layer.index == mid_ply_index:
				#This is the ply right above the core. 
				z_bot+=zc
				z_top+=zc
			else:
				pass

			layer.set_z(z_bot,z_top)
			self.z_array[counter] = [z_bot,z_top]

			z_bot+=h0
			z_top+=h0
			counter+=1

		# print self.z_array

	def compute_all(self, method = 'smart'):
		"""method takes 'dumb' or 'smart'
		Dumb method merely calls compute_all() on all layers
		Smart method :
			-Computes Q_on, S_on only once and assigns it all other layers
			-If symmetric, only computes Q_off, S_off for half the layers.

		Returns True if computations were done.
		Returns False if compute_all was already executed and nothing is done.
		""" 
		do_debug = False
		if self.computed:
			return False
		if method is 'dumb':
			for layer in self.layers:
				layer.compute_all()

		elif method is 'smart':
			if self.symmetric:
				length = len(self.layers)/2
			else:
				length = len(self.layers)

			for i in range(length):
				if i == 0:
					self.layers[i].compute_all()
					on_changes = {'Q_on':self.layers[0].Q_on,
												'S_on':self.layers[0].S_on
												}
					off_changes = {'Q_off':self.layers[0].Q_off,
												'S_off':self.layers[0].S_off
												}

				else:
					self.layers[i].set(on_changes)
					modified = self.layers[i].compute_all()
					assert (len(modified) == 2)

					if do_debug:
						print modified

					off_changes = {modified[0]:getattr(self.layers[i],modified[0]),
												modified[1]:getattr(self.layers[i],modified[1])
												}

				if self.symmetric:
					off_changes.update(on_changes)
					opposite_layer = self.layers[-i-1]
					opposite_layer.set(off_changes)

			#End of symmetry loop

		else:
			raise AssertionError("Method %s is not defined" % method)

		self._compute_A()
		self._compute_D()
		self.computed = True
		return True

	def _compute_A(self):
		import numpy
		import scipy
		h0 = self.layers[0].PROPS['h0']/1000
		U1,U2,U3,U4,U5 = self.layers[0].U_Q
		thetas = numpy.radians(self.layup)
		V1 = h0*numpy.cos(2*thetas).sum()
		V2 = h0*numpy.cos(4*thetas).sum()
		V3 = h0*numpy.sin(2*thetas).sum()
		V4 = h0*numpy.sin(4*thetas).sum()
		the_array = numpy.array([[U1,V1,V2],
														 [U1,-V1,V2],
														 [U4,0,-V2],
														 [U5,0,-V2],
														 [0,V3/2,V4],
														 [0,V3/2,-V4]
														 ])
		vec = numpy.array([self.total_ply_thickness,U2,U3])
		self.A_vec = the_array.dot(vec)
		self.A = make_array(self.A_vec)
		self.a = scipy.linalg.inv(self.A)
		a = self.a
		self.a_vec = make_vec(a)

	def _compute_D(self):
		import numpy
		import scipy
		do_debug = False
		z_diff = self.z_array[:,1]**3-self.z_array[:,0]**3
		thetas = numpy.radians(self.layup)
		U1,U2,U3,U4,U5 = self.layers[0].U_Q
		h_star = z_diff.sum()/3.0
		V1 = 1.0/3.0*(numpy.cos(2*thetas)*z_diff).sum()
		V2 = 1.0/3.0*(numpy.cos(4*thetas)*z_diff).sum()
		V3 = 1.0/3.0*(numpy.sin(2*thetas)*z_diff).sum()
		V4 = 1.0/3.0*(numpy.sin(4*thetas)*z_diff).sum()
		the_array = numpy.array([[U1,V1,V2],
														 [U1,-V1,V2],
														 [U4,0,-V2],
														 [U5,0,-V2],
														 [0,V3/2,V4],
														 [0,V3/2,-V4]
														 ])
		vec = numpy.array([h_star,U2,U3])
		self.D_vec = the_array.dot(vec) 
		self.D = make_array(self.D_vec) #**9 to obtain Nm

		self.d = scipy.linalg.inv(self.D)
		d = self.d                      #**-6 to obtain (kNm)-1
		self.d_vec = make_vec(d)

		if do_debug:
			return_string = ''
			return_string = "z : %r" % self.z_array
			return_string += "V1 : %r" %V1; return_string += '\n'
			return_string += "V2 : %r" %V2; return_string += '\n'
			return_string += "V3 : %r" %V3; return_string += '\n'
			return_string += "V4 : %r" %V4; return_string += '\n'
			return_string += "Big array : %r" %the_array; return_string += '\n'
			return_string += "vector %r" %vec; return_string += '\n'
			print "Writing"
			open('D_values.txt','w').write(return_string)

	def print_param(self, display = do_display):
		return_string = self.layers[0].print_param(display)

		if display:
			print "Asked for display inside laminate.print_param"
			print return_string

		return return_string

	def print_orientation(self, display = do_display):
		str_layup_1 = "%s" % self.layup
		title = "Orientation [degrees] : \n"

		return_string = title + str_layup_1
		
		if display:
			print "Asked for display inside print_orientation"
			print return_string

		return return_string

	def print_array(self,names, num_of_layers = 'all', display = do_display):
		"""This prints the arrays that belong to each individual layer.
		"""
		return_string = ''
		if num_of_layers == 'all':
			length = len(self.layers)
		else:
			length = int(num_of_layers)

		if length == 1:
			separator = ''
			caption = False
		else:
			separator = '--' * 20 + '\n'
			caption = True

		counter = 1
		for layer in self.layers[:length]:
				return_string += separator
				if caption:
					return_string += "Layer number : %d" % counter + '\n'
					return_string += "Orientation  : %d [degrees]" % layer.theta + '\n'
				return_string += layer.print_array(names, display)
				return_string += '\n'
				counter += 1

		if display:
			print "Asked for display inside laminate.print_array"
			print return_string

		return return_string

	def print_A(self, display = do_display):
		from floatformat import floatformat
		import numpy
		numpy.set_printoptions(formatter = {'float_kind':floatformat}, 
													suppress = True
													)
		return_string = ''
		return_string += "A [GN/m] : \n"
		return_string += str(self.A)
		return_string += '\n'
		return_string += "a [m/GN] : \n"
		return_string += str(self.a)

		return return_string

	def print_D(self, display = do_display):
		from floatformat import floatformat
		import numpy
		numpy.set_printoptions(formatter = {'float_kind':floatformat}, 
													suppress = True
													)
		return_string = ''
		return_string += "D [kNm] : \n"
		return_string += str(self.D*10**6)
		return_string += '\n'
		return_string += "d [1/MNm] : \n"
		return_string += str(self.d*10**-3)

		return return_string


if __name__ == "__main__":
	import numpy
	# materialID = 1
	# layups = ['30/-30/30/-30s','-30/30/-30/30s','30_2/-30_2s']
	# for layup in layups:
	# 	lam = Laminate(layup,materialID)
	# 	lam.compute_all()
	# 	print lam.print_orientation()
	# 	print lam.D[1,1]
	laminate = Laminate('0_2/p25/0_2s',
                               materialID = 5, #5
                               core_thick = 0.01)
	laminate.compute_all()



						