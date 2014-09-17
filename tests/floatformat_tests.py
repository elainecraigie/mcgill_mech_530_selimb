from nose.tools import *
from composites.floatformat import *
import numpy

def test_strings():
	mat = numpy.array([0.000545,'blah',512.4])
	numpy.set_printoptions(formatter = {'float_kind':floatformat}, suppress = True)
	try:
		print mat
	except:
		raise
	else:
		assert True
