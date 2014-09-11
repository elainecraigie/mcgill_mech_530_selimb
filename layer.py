import readcsv
import math
import numpy
from floatformat import floatformat
from scipy import linalg as scilin
class Layer(object):
	"""Layer(materialID, orientation) -> layer
	"""
	def __init__(self, materialID, orientation):
		self.PROPS = readcsv.readcsv(materialID,'materialprops.csv')
		self.theta = orientation

	def print_param(self,file=None,mode = 'w'):
		"""Print material properties and geometry parameters. 
		If file name specified, prints to a txt file. 
		"""
		if mode == 'a':
			the_separator = '--' * 10 + '\n' + '--' * 10 + '\n'
		else:
			the_separator = ''

		if file is not None:
			with open(file,mode) as f:
				for i in readcsv.iter_csvdict(self.PROPS):
					f.write(i+'\n')
				f.write(the_separator)

		else:
			for i in readcsv.iter_csvdict(self.PROPS):
				print "%r" % i
			print(the_separator)

	def make_array(self, the_dict):
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

	def getQ_on(self):
		"""Return on-axis Q matrix AND corresponding unit"""
		m = pow(1-self.PROPS['nux']*self.PROPS['nuy'],-1)
		q={}
		q['xx'] = m*self.PROPS['ex']
		q['yy'] = m*self.PROPS['ey']
		q['yx'] = m*self.PROPS['nux']*self.PROPS['ey']
		q['xy'] = m*self.PROPS['nuy']*self.PROPS['ex']
		q['ss'] = self.PROPS['es']
		Q_on = self.make_array(q)
		unit = 'MPa'
		self.Q_on = Q_on 
		return Q_on

		# raise NotImplementedError, "Not implemented yet"

	def getQ_off(self):
		"""Return off-axis Q matrix"""
		raise NotImplementedError, "Not implemented yet"

	def getS_on(self):
		"""Return on-axis S matrix"""
		s = {}
		s['xx'] = 1/self.PROPS['ex']
		s['xy'] = -self.PROPS['nuy']/self.PROPS['ey']
		s['yx'] = -self.PROPS['nux']/self.PROPS['ex']
		s['yy'] = 1/self.PROPS['ey']
		s['ss'] = 1/self.PROPS['es']
		S_on = self.make_array(s)
		unit = '1/MPa'
		self.S_on = S_on
		return S_on

	def getS_off(self):
		"""Return off-axis S matrix"""
		raise NotImplementedError, "Not implemented yet"

	def get_matrix(self, the_name, do_print = False):
		"""Compute and print desired arrays

		Possible valid inputs:
			-QS
			-Q_on
			-offQS

		*Mixed requests are not supported, 
		e.g. Q_on and S_off
		"""
		methods = self._parse_request(the_name)
		multiple = True if len(methods) > 1 else False
		# mag = lambda num: abs(math.log10(abs(float(num))))
		# engineering_formatter = lambda x: "%10.3e" % x if mag(x) >= 3 else "%10.3f" % x
		# print engineering_formatter(float(4.6))
		numpy.set_printoptions(formatter = {'float_kind':floatformat}, suppress = True)
		title = "{0:s} [{1:s}] : "
		results = []
		for array_name,method_unit,method_name in methods:
			try:
				method_to_call = getattr(self, method_name)
			except AttributeError:
				print """***
				No method %s defined for Layer object.
				***""" % method_name
				raise
			result_array=method_to_call()
			if do_print:
				print title.format(array_name,method_unit)
				print result_array
			if multiple:
				results.append(result_array)
			else:
				results = result_array

		return results


	def _parse_request(self,the_name):
		"""Used by Layer.print_array() to parse array
		Returns a list of tuples with method names, array name
		and corresponding units.
		"""
		units={'Q':'GPa','S':'1/GPa'}
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
				method_name = 'get%s_%s' % (a_prefix,a_suffix)
				method_unit = units[a_prefix]
				array_name = '%s_%s' % (a_prefix,a_suffix)
				method_list.append((array_name,method_unit,method_name))

		return method_list


if __name__ == "__main__":
	import sys
	if len (sys.argv) == 3:
		my_layer = Layer(sys.argv(1), sys.argv(2))
	else:
		my_layer = Layer(2,45)
	my_layer.print_param()
	# my_layer.print_param('testinput.txt')
	Q_on_1 = my_layer.getQ_on()
	S_on_1 = my_layer.getS_on()
	Q_on_inv = scilin.inv(Q_on_1)
	assert(Q_on_inv.all() == S_on_1.all())
	Q_on_2,S_on_2 = my_layer.get_matrix('QSon', do_print = True)
	assert (Q_on_1.all() == Q_on_2.all() and S_on_1.all() == S_on_2.all())
				





