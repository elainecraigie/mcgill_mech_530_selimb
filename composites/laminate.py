#TODO : Implement z_core

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
do_display = True

class Laminate(object):
	"""Laminate(layup, materialID, compute = <method>) -> Laminate 
composed of layers with various orientations but the same material properties. 

Arguments:
	-layup : layup as a string. See parselayup.py
	-materialID : ID of the wanted material
	-compute = 'dumb' or 'smart'. Smart uses symmetry if possible.
	"""
	def __init__(self, layup, materialID, compute = None):
		self.layup, self.symmetric = parse_layup(layup)
		self.layers = [] 
		for orientation in self.layup:
			new_layer = layer.Layer(materialID,orientation)
			self.layers.append(new_layer)
		if compute is not None:
			self.compute_all()

		self.total_thickness = len(self.layup)*self.layers[0].PROPS['h0']/1000

	def compute_all(self, method = 'smart'):
		"""method takes 'dumb' or 'smart'
		Dumb method merely calls compute_all() on all layers
		Smart method :
			-Computes Q_on, S_on only once and assigns it all other layers
			-If symmetric, only computes Q_off, S_off for half the layers.
		""" 
		do_debug = False
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
		vec = numpy.array([self.total_thickness,U2,U3])
		self.A_vec = the_array.dot(vec)
		self.A = make_array(self.A_vec)
		self.a = scipy.linalg.inv(self.A)
		a = self.a
		self.a_vec = make_vec(a)

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


if __name__ == "__main__":
	# import scipy
	# my_lam = Laminate('90_2/p40/p20/0s',2)
	# my_lam.compute_all(method='smart')
	# my_lam.compute_A()
	# print my_lam.A
	# print my_lam.a
	# print scipy.linalg.inv(my_lam.a)
	my_cross = Laminate('0/90/0/90/0/90/0/90',2)
	my_cross.compute_all()
	print my_cross.A
	print my_cross.a

	# print dumbtime
	# print smarttime
	# print smarttime/dumbtime


						