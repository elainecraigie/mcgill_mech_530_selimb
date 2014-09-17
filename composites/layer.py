import readcsv
import math
import numpy
import floatformat
from scipy import linalg as scilin

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
		self.q_on_found = False; self.s_on_found = False;
		self.q_off_found = False; self.s_off_found = False;
		self.getQ_on()
		self.getQ_off()
		self.getS_on()
		self.getS_off()
		
	def print_param(self, mode = 'w'):
		"""Print material properties and geometry parameters."""
		if mode == 'a':
			the_separator = '--' * 10 + '\n' + '--' * 10 + '\n'
		else:
			the_separator = ''

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
		array_names = self._parse_request(the_names)
		multiple = True if len(array_names) > 1 else False
		# mag = lambda num: abs(math.log10(abs(float(num))))
		# engineering_formatter = lambda x: "%10.3e" % x if mag(x) >= 3 else "%10.3f" % x
		# print engineering_formatter(float(4.6))
		numpy.set_printoptions(formatter = {'float_kind':floatformat.floatformat}, suppress = True)
		title = "{0:s} [{1:s}] : "
		for array_name in array_names:
			try:
				array = getattr(self,array_name)
			except AttributeError:
				print """***
				No array '%s' defined for Layer object.
				***""" % array_name
				raise

			print title.format(array_name,self.units_dict[array_name])
			print array


	def set_array(self,input_names,input_array_list):
		"""Assign matrix to layer
		Arguments:
		the_name : name of the matrix/matrices
			Possible valid inputs:
				-QS
				-Q_on
				-offQS
		the_matrix: LIST of numpy arrays. 
								number of matrices must match number of names

		*Mixed requests are not supported, 
		e.g. Q_on and S_off
		"""
		import sys
		#matrix_names is a tuple (method name, unit, array name)
		assert(type(input_array_list)==list)
		array_names = self._parse_request(input_names)
		if (len(array_names) != len(input_array_list)):
			print "-----------------------------------"
			print "Matrices to be set : %s" % array_names[:]
			print "Do not match number of arrays given : %d" % (len(input_array_list))
			print "-----------------------------------"
			raise AssertionError
		else:
			pass

		global do_debug
		if do_debug:
			print "All array names : ", array_names
			print "All input arrays : ", input_array_list
			
		for n in range(len(array_names)):
			array_name = array_names[n]
			array = input_array_list[n]
			assert(type(array)==numpy.ndarray)
			if do_debug:
				print "Array_name : ", array_name
				print "Input array : ", array
			setattr(self,array_name,array)

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
		self.q_on_found = True
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
		self.s_on_found = True
		return S_on

	def getQ_off(self):
		"""Return off-axis Q matrix"""
		assert(self.q_on_found)
		u = self._get_u(self._q_on)
		A = self._get_A(u)
		b = numpy.array([[1],[u[1]],[u[2]]])
		q_off = A.dot(b)
		# 11,22,12,66,16,26
		self._q_off = q_off
		self.Q_off = self._make_off_array(q_off)
		return self.Q_off

	def getS_off(self):

		"""Return off-axis S matrix"""
		assert(self.s_on_found)
		u = self._get_u(self._s_on)
		A = self._get_A(u)
		b = numpy.array([[1],[u[1]],[u[2]]])
		s_off = A.dot(b)
		# print q_off
		self._s_off = s_off
		self.S_off = self._make_off_array(s_off)
		return self.S_off

	
	def _parse_request(self,the_name):
		"""Used to parse request of arrays to be printed/modified/obtained.
		Returns a list of array_names.
		"""
		prefix_list = ['S','Q']; suffix_list = ['on','off']
		the_prefix = []; the_suffix = []
		#Parse the input string to account for variations
		for a_prefix in prefix_list:
			if a_prefix in the_name:
				the_prefix.append(a_prefix)

		sufix_found = False
		for a_suffix in suffix_list:
			if a_suffix in the_name:
				sufix_found = True
				the_suffix.append(a_suffix)
		#If neither 'on' or 'off' was found, assume user wants both.
		if not sufix_found:
			the_suffix= suffix_list

		method_list = []
		for a_prefix in the_prefix:
			for a_suffix in the_suffix:
				array_name = '%s_%s' % (a_prefix,a_suffix)
				method_list.append(array_name)

		return method_list

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

	def _get_u(self,q_or_s):
		"""Expects dictionary q or s with keys:
		xx, xy, yy, ss"""
		#For conciseness
		do_debug = False
		q = q_or_s
		u=[]
		u1 = (3*q['xx'] + 3*q['yy'] + 2*q['xy'] + 4*q['ss'])/8.0
		u2 = (q['xx'] - q['yy'])/2.0
		u3 = (q['xx'] + q['yy'] - 2*q['xy'] - 4*q['ss'])/8.0
		u4 = (q['xx'] + q['yy'] + 6*q['xy'] - 4*q['ss'])/8.0
		u5 = (q['xx'] + q['yy'] - 2*q['xy'] + 4*q['ss'])/8.0
		u = [u1, u2, u3, u4, u5]
		if do_debug:
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
	print "Nothing here yet."
	
				





