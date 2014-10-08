import readcsv
import math
import numpy
from floatformat import floatformat
from scipy import linalg as scilin
from parsetools import parse_request

do_display = True
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
			self.computeQ_on()
			modified.append('Q_on')
		if not self.Q_off_found or force:	
			self.computeQ_off()
			modified.append('Q_off')
		if not self.S_on_found or force:		
			self.computeS_on()
			modified.append('S_on')
		if not self.S_off_found or force:
			self.computeS_off()
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

	def print_param(self, display = do_display):
		"""Print material properties and geometry parameters."""
		# the_separator = '--' * 10 + '\n' + '--' * 10 + '\n'
		return_string = ''
		for i in readcsv.iter_csvdict(self.PROPS):
			return_string += "%r" % i + '\n'
			# print return_string
		# print(the_separator)
		if display:
			print "Asked for display inside layer.print_param"
			print return_string

		return return_string

	def print_array(self, the_names, display = do_display):
		"""Compute and print desired arrays

		Possible valid inputs:
			-QS
			-Q_on
			-offQS

		*Mixed requests are not supported, 
		e.g. Q_on and S_off

		If an off-axis matrix is returned, U is also printed. 
		"""
		return_string = ''
		array_names = parse_request(the_names)
		# mag = lambda num: abs(math.log10(abs(float(num))))
		# engineering_formatter = lambda x: "%10.3e" % x if mag(x) >= 3 else "%10.3f" % x
		# print engineering_formatter(float(4.6))
		numpy.set_printoptions(formatter = {'float_kind':floatformat}, 
													suppress = True
													)
		title = "{0:s} [{1:s}] : "
		for array_name in array_names:
			if not getattr(self,array_name+'_found'):
				raise AssertionError("Array %s has not been computed yet" % array_name)

			array = getattr(self,array_name)
			
			return_string += title.format(array_name,self.units_dict[array_name])
			return_string += '\n'
			return_string += str(array)
			

			if 'on' in array_name:
				return_string += '\n'					
				return_string += getattr(self,"u_%s_string" % array_name.split('_')[0])
			else:
				pass #No print of U's.

			return_string += '\n'	

		if display:
			print "Asked for display inside layer.print_array"
			print title.format(array_name,self.units_dict[array_name])
			print array

		return return_string

	def set(self,input_dict):
		"""Assign matrix to layer
		Argument must be a dict.
			-Keys must be something like Q_on, S_off, QSon, QS
			-Values are numpy arrays. If a key with multiple request is provided, an
			equal amount of arrays must be provided (as list)
		"""
		do_debug = False
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

	def computeQ_on(self):
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

	def computeS_on(self):
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

	def computeQ_off(self):
		"""Return off-axis Q matrix"""
		assert(self.Q_on_found)
		u = self._compute_u('Q')
		A = self._compute_A(u,'Q')
		b = numpy.array([[1],[u[1]],[u[2]]])
		q_off = A.dot(b)
		# 11,22,12,66,16,26
		self._q_off = q_off
		self.Q_off = self._make_off_array(q_off)
		self.Q_off_found = True
		return self.Q_off

	def computeS_off(self):

		"""Return off-axis S matrix"""
		assert(self.S_on_found)
		u = self._compute_u('S')
		A = self._compute_A(u,'S')
		b = numpy.array([[1],[u[1]],[u[2]]])
		s_off = A.dot(b)
		# print q_off
		self._s_off = s_off
		self.S_off = self._make_off_array(s_off)
		self.S_off_found = True
		return self.S_off

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

	def _compute_u(self,array_prefix):
		"""Expects dictionary q or s with keys:
		xx, xy, yy, ss
		"""
		do_debug = False
		return_string = ''
		if array_prefix == 'Q':
			ss_factor = 4
			five_factor = 1.0/8.0 
			U_unit = 'GPa'
			A = self.Q_on 
		elif array_prefix == 'S':
			ss_factor = 1
			five_factor = 1.0/2.0
			U_unit = '1/GPa'
			A = self.S_on
		else:
			raise AssertionError("""Must call _compute_u with 'Q' or 'S', not %s
													""" % array_prefix)
		u = []
		u1 = (3.0*A[0,0] + 3.0*A[1,1] + 2.0*A[0,1] + ss_factor*A[2,2])/8.0
		u2 = (A[0,0] - A[1,1])/2.0
		u3 = (A[0,0] + A[1,1] - 2.0*A[0,1] - ss_factor*A[2,2])/8.0
		u4 = (A[0,0] + A[1,1] + 6.0*A[0,1] - ss_factor*A[2,2])/8.0
		u5 = (A[0,0] + A[1,1] - 2.0*A[0,1] + ss_factor*A[2,2])*five_factor
		u = [u1, u2, u3, u4, u5]
		if array_prefix == 'Q':
			self.U_Q = u
		else:
			self.U_S = u
		#String making
		
		if do_debug:
			print "A : ", A
			print "u : ", u		
		
		counter = 1
		return_string += "U's for %s [%s]" % (array_prefix,U_unit) + '\n'
		for a_u in u:
			return_string += "U%d : %7.4f" %(counter, a_u) + '\n'
			counter += 1 
		setattr(self,"u_%s_string" % array_prefix,return_string)
		return u			

	def _compute_A(self,u,array_prefix):
		"""I call "A" the matrix that multiples [1,u2,u3] to obtain the S or Q
		vector"""
		from math import cos,sin,radians
		tet = radians(self.theta)
		if array_prefix == 'Q':
			sn6 = 1
			s66 = 1
		elif array_prefix == 'S':
			sn6 = 2
			s66 = 4
		A = numpy.array([[u[0], cos(2*tet), cos(4*tet)],  #11
										 [u[0], -cos(2*tet), cos(4*tet)], #22
										 [u[3], 0          ,-cos(4*tet)], #12
										 [u[4], 0, -s66*cos(4*tet)], #66
										 [0, sn6*sin(2*tet)/2, sn6*sin(4*tet)], #16
										 [0, sn6*sin(2*tet)/2, -sn6*sin(4*tet)] #26
										 ])
		return A

	def set_index(self,index):
		self.index = index

	def set_z(self,z_bot,z_top):
		self.z_bot = float(z_bot)
		self.z_top = float(z_top)


	def get_z(self):
		return [self.z_bot,self.z_top]


if __name__ == "__main__":
	pass