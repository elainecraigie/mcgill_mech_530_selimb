import readcsv
import math
import numpy
import floatformat
from scipy import linalg as scilin
from parsetools import parse_request

global do_debug
do_debug = False
class Layer(object):
	"""Layer(materialID, orientation) -> layer
	"""
	def __init__(self, materialID, orientation):
		self.PROPS = readcsv.readcsv(materialID,'materialprops.csv')
		self.theta = orientation
		self.units_dict={'Q_on':'GPa',
										'Q_off':'GPa',
										'S_on':'1/GPa',
										'S_off':'1/GPa'}
		self.Q_on_found = False; self.S_on_found = False;
		self.Q_off_found = False; self.S_off_found = False;

	def compute_all(self,force = False):
		"""Takes into account which arrays have already been marked as found, 
		unless 'force' parameter is set to True.
		"""
		modified=[]
		if not self.Q_on_found or force:
			self.getQ_on()
			modified.append('Q_on')
		if not self.Q_off_found or force:	
			self.getQ_off()
			modified.append('Q_off')
		if not self.S_on_found or force:		
			self.getS_on()
			modified.append('S_on')
		if not self.S_off_found or force:
			self.getS_off()
			modified.append('S_off')
		
		if modified == []:
			return None
		else:
			return modified
		
	def is_found(self):
		"""Returns True if all matrices have been marked as found.
		Else, returns the names of the matrices that are still not found.
		"""
		all_found = True
		missing = []
		if not self.Q_on_found:
			all_found = False
			missing.append('Q_on')
		if not self.Q_off_found:
			all_found = False
			missing.append('Q_off')
		if not self.S_on_found:
			all_found = False
			missing.append('S_on')
		if not self.S_off_found:
			all_found = False
			missing.append('S_off')
		if all_found:
			return True
		else:
			return missing

	def print_param(self):
		"""Print material properties and geometry parameters."""
		the_separator = '--' * 10 + '\n' + '--' * 10 + '\n'

		for i in readcsv.iter_csvdict(self.PROPS):
			print "%r" % i
		print(the_separator)

	def print_array(self, the_names):
		"""Compute and print desired arrays

		Possible valid inputs:
			-QS
			-Q_on
			-offQS

		*Mixed requests are not supported, 
		e.g. Q_on and S_off
		"""
		array_names = parse_request(the_names)
		multiple = True if len(array_names) > 1 else False
		# mag = lambda num: abs(math.log10(abs(float(num))))
		# engineering_formatter = lambda x: "%10.3e" % x if mag(x) >= 3 else "%10.3f" % x
		# print engineering_formatter(float(4.6))
		numpy.set_printoptions(formatter = {'float_kind':floatformat.floatformat}, suppress = True)
		title = "{0:s} [{1:s}] : "
		for array_name in array_names:
			if not getattr(self,array_name+'_found'):
				raise AssertionError("Array %s has not been computed yet" % array_name)

			array = getattr(self,array_name)
			print title.format(array_name,self.units_dict[array_name])
			print array

	def set(self,input_dict):
		"""Assign matrix to layer
		Argument must be a dict.
			-Keys must be something like Q_on, S_off, QSon, QS
			-Values are numpy arrays. If a key with multiple request is provided, an
			equal amount of arrays must be provided (as list)
		"""
		do_debug = True
		for a_key,an_array in input_dict.iteritems():
			array_names = parse_request(a_key)
			if len(array_names)==1:
				array_name=array_names[0]
			else:
				raise AssertionError("""Key %s provides more than one array name %s
					""" % (a_key,array_names))
			
			assert(type(an_array)==numpy.ndarray)
			setattr(self,array_name,an_array)
			setattr(self,array_name+'_found',True)
			if do_debug:
				print "Array names : ", array_name
				print "Input array : ", an_array
				print "set to found : %s" % array_name+'_found'

	def getQ_on(self):
		"""Return on-axis Q matrix."""
		m = pow(1-self.PROPS['nux']*self.PROPS['nuy'],-1)
		q={}
		q['xx'] = m*self.PROPS['ex']
		q['yy'] = m*self.PROPS['ey']
		q['yx'] = m*self.PROPS['nux']*self.PROPS['ey']
		q['xy'] = m*self.PROPS['nuy']*self.PROPS['ex']
		q['ss'] = self.PROPS['es']
		self._q_on = q
		Q_on = self._make_on_array(q)
		self.Q_on = Q_on 
		self.Q_on_found = True
		return Q_on

	def getS_on(self):
		"""Return on-axis S matrix"""
		s = {}
		s['xx'] = 1/self.PROPS['ex']
		s['xy'] = -self.PROPS['nuy']/self.PROPS['ey']
		s['yx'] = -self.PROPS['nux']/self.PROPS['ex']
		s['yy'] = 1/self.PROPS['ey']
		s['ss'] = 1/self.PROPS['es']
		self._s_on = s
		S_on = self._make_on_array(s)
		self.S_on = S_on
		self.S_on_found = True
		return S_on

	def getQ_off(self):
		"""Return off-axis Q matrix"""
		assert(self.Q_on_found)
		u = self._get_u('Q')
		A = self._get_A(u)
		b = numpy.array([[1],[u[1]],[u[2]]])
		q_off = A.dot(b)
		# 11,22,12,66,16,26
		self._q_off = q_off
		self.Q_off = self._make_off_array(q_off)
		self.Q_off_found = True
		return self.Q_off

	def getS_off(self):

		"""Return off-axis S matrix"""
		assert(self.S_on_found)
		u = self._get_u('S')
		A = self._get_A(u)
		b = numpy.array([[1],[u[1]],[u[2]]])
		s_off = A.dot(b)
		# print q_off
		self._s_off = s_off
		self.S_off = self._make_off_array(s_off)
		self.S_off_found = True
		return self.S_off

	# def _parse_request(self,the_name):
	# 	"""Used to parse request of arrays to be printed/modified/obtained.
	# 	Returns a list of array_names.
	# 	"""
	# 	prefix_list = ['S','Q']; suffix_list = ['on','off']
	# 	the_prefix = []; the_suffix = []
	# 	prefix_found = False
	# 	#Parse the input string to account for variations
	# 	for a_prefix in prefix_list:
	# 		if a_prefix in the_name:
	# 			the_prefix.append(a_prefix)
	# 			prefix_found = True

	# 	if not prefix_found:
	# 		raise AssertionError("Could not parse %s request" % the_name)

	# 	sufix_found = False
	# 	for a_suffix in suffix_list:
	# 		if a_suffix in the_name:
	# 			sufix_found = True
	# 			the_suffix.append(a_suffix)
	# 	#If neither 'on' or 'off' was found, assume user wants both.
	# 	if not sufix_found:
	# 		the_suffix= suffix_list

	# 	array_list = []
	# 	for a_prefix in the_prefix:
	# 		for a_suffix in the_suffix:
	# 			array_name = '%s_%s' % (a_prefix,a_suffix)
	# 			array_list.append(array_name)

	# 	return array_list

	def _make_on_array(self, the_dict):
		"""make_array(dict containing Aij) -> numpy array(3,3)
		Elements not supplied will have value = 0

		Array looks like this : 
		[xx xy xs
		 yx yy ys
		 sx sy ss]
		"""
		numpy_return_array = numpy.empty((3,3),numpy.float)
		listofindex = ['xx','xy','xs', 'yx','yy','ys','sx','sy','ss']
		column = 0
		row = 0
		# #DEBUGGIN PURPOSE
		# the_dict['xy'] =  1
		for column in range(3):
			for row in range(3):
				index = listofindex.pop(0)
				val = the_dict.setdefault(index,0)
				numpy_return_array[column,row] = val

		return numpy_return_array

	def _make_off_array(self, a):
		"""Expecting vector with following values
		11,22,12,66,16,26
		"""
		arr = numpy.ones((3,3),numpy.float)
		arr[0,:] = a[0],a[2],a[4]
		arr[1,:] = a[2],a[1],a[5]
		arr[2,:] = a[4],a[5],a[3]
		return arr

	def _get_u(self,array_prefix):
		"""Expects dictionary q or s with keys:
		xx, xy, yy, ss
		"""
		do_debug = True
		if array_prefix == 'Q':
			A = self.Q_on 
		elif array_prefix == 'S':
			A = self.S_on
		else:
			raise AssertionError("""Must call _get_u with 'Q' or 'S', not %s
													""" % array_prefix)
		u = []
		u1 = (3.0*A[0,0] + 3.0*A[1,1] + 2.0*A[0,1] + 4.0*A[2,2])/8.0
		u2 = (A[0,0] - A[1,1])/2.0
		u3 = (A[0,0] + A[1,1] - 2.0*A[0,1] - 4.0*A[2,2])/8.0
		u4 = (A[0,0] + A[1,1] + 6.0*A[0,1] - 4.0*A[2,2])/8.0
		u5 = (A[0,0] + A[1,1] - 2.0*A[0,1] + 4.0*A[2,2])/8.0
		u = [u1, u2, u3, u4, u5]

		if do_debug:
			print "A : ", A
			print "u : ", u
		return u

	def _get_A(self,u):
		"""I call "A" the matrix that multiples [1,u2,u3] to obtain the S or Q
		vector"""
		from math import cos,sin,radians
		tet = radians(self.theta)
		A = numpy.array([[u[0], cos(2*tet), cos(4*tet)],  #11
										 [u[0], -cos(2*tet), cos(4*tet)], #22
										 [u[3], 0          ,-cos(4*tet)], #12
										 [u[4], 0         , -cos(4*tet)], #66
										 [0, sin(2*tet)/2, sin(4*tet)], #16
										 [0, sin(2*tet)/2, -sin(4*tet)] #26
										 ])
		return A

if __name__ == "__main__":
	my_layer = Layer(2,45)
	my_layer.compute_all()
	
				





