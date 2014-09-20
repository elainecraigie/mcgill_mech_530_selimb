from nose.tools import *
from composites.transform import transform_stress,transform_strain
import numpy
from numpy.testing import assert_array_almost_equal

def array_assert(x,y):
		import numpy
		from numpy.testing import assert_array_almost_equal
		a = numpy.array(x, dtype = float)
		b = numpy.array(y, dtype = float)
		assert_array_almost_equal(a,b,decimal = 6)

def test_stress_off_to_on_to_off():
	off_axis_og = [420,-165,-135]
	on_axis = transform_stress(off_axis_og,'off','30')
	off_axis = transform_stress(on_axis,'on','30')
	array_assert(off_axis_og,off_axis)

def test_strain_off_to_on_to_off():
	off_axis_og = [420,-165,-135]
	on_axis = transform_strain(off_axis_og,'off','30')
	off_axis = transform_strain(on_axis,'on','30')
	array_assert(off_axis_og,off_axis)

def test_stress_on_to_off_to_on():
	on_axis_og = [420,-165,-135]
	off_axis = transform_stress(on_axis_og,'on','45.3')
	on_axis = transform_stress(off_axis,'off','45.3')
	array_assert(on_axis_og,on_axis)

def test_strain_on_to_off_to_on():
	on_axis_og = [420,-165,-135]
	off_axis = transform_strain(on_axis_og,'on','45.3')
	on_axis = transform_strain(off_axis,'off','45.3')
	array_assert(on_axis_og,on_axis)

def test_stress_zero():
	on_axis = numpy.array([420,-165,-135])
	off_axis = transform_stress(on_axis,'on',0)
	array_assert(off_axis, on_axis)

def test_strain_zero():
	on_axis = numpy.array([420,-165,-135])
	off_axis = transform_strain(on_axis,'on',0)
	array_assert(off_axis, on_axis)

def test_stress_ninety():
	on_axis = numpy.array([200,200,100],dtype=float)
	off_axis = transform_stress(on_axis,'on',90)
	off_axis[2] *= -1
	array_assert(on_axis, off_axis)

def test_strain_ninety():
	on_axis = numpy.array([200,200,100],dtype=float)
	off_axis = transform_strain(on_axis,'on',90)
	off_axis[2] *= -1
	array_assert(on_axis, off_axis)

# def test_example():
# 	off_axis = numpy.array([100,20,30])
# 	on_axis_actual = transform(off_axis,'on',18.44)
# 	on_axis_desired = numpy.array([110,10,50])
# 	on_axis_actual[0] = 3
# 	if on_axis_actual.all() == on_axis_desired.all():
# 		print on_axis_actual.all()
# 		print on_axis_desired.all()
# 		print on_axis_actual.all() == on_axis_desired.all()
# 		raise AssertionError("%r not equal %r" % (on_axis_desired,on_axis_actual))


