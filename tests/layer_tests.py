from nose.tools import *
from composites.layer import *
import numpy
from scipy import linalg as scilin

def setup():
	global my_layer
	my_layer = Layer(2,45)
	
def test_print_param():
	import os
	global my_layer
	# my_layer = Layer(2,45)
	my_layer.print_param()

def test_inverse_on():
	global my_layer
	S_on_inv = scilin.inv(my_layer.S_on)
	Q_on = my_layer.Q_on
	assert (Q_on.all() == S_on_inv.all())

def test_inverse_off():
	global my_layer
	S_off_inv = scilin.inv(my_layer.S_off)
	Q_off = my_layer.Q_off
	assert (Q_off.all() == S_off_inv.all())

@raises(AssertionError)
def test_set_non_list():
	global my_layer
	A = numpy.ones([3,3])
	my_layer.set_array('Q',A)

@raises(AssertionError)
def test_set_non_array():
	global my_layer
	A = numpy.ones([3,3])
	B = [[1,2,3],[4,5,6],[7,8,9]]
	my_layer.set_array('QSon',[A,B])
	my_layer.set_array('Qonoff',[A,B])

@raises(AssertionError)
def test_set_unbalanced():
	global my_layer
	A = numpy.ones([3,3])
	B = numpy.ones([3,3])
	my_layer.set_array('Q',[A,B])
	my_layer.set_array('QS',[A,B])
	my_layer.set_array('Qonoff',[A])

def test_parse_request():
	global my_layer
	ret = my_layer._parse_request('QS')
	assert (ret == ['S_on','S_off','Q_on','Q_off'])

	ret = my_layer._parse_request('QSoff')
	assert (ret == ['S_off','Q_off'])

	ret = my_layer._parse_request('QSon')
	assert (ret == ['S_on','Q_on'])

	ret = my_layer._parse_request('Q')
	assert (ret == ['Q_on','Q_off'])

def test_u_values_2():
	global my_layer
	u1 = 59.66; u2=64.90; u3=14.25; u4=16.96; u5=21.35;
	udesired = [u1,u2,u3,u4,u5]
	uactual = my_layer._get_u(my_layer._q_on)
	assert(len(udesired) == len(uactual))
	for i in range(len(udesired)):
		delta_abs = (udesired[i]-uactual[i])
		if delta_abs>5*10.0**-3:
			raise AssertionError("""u%d wrong by %f.
				udesired : %f
				uactual : %f
				""" % (i,delta_abs,udesired[i],uactual[i])
				)
		else:
			pass

def test_u_values_1():
	my_layer = Layer(1,45)
	u1 = 76.37; u2=85.73; u3=19.71; u4=22.61; u5=26.88;
	udesired = [u1,u2,u3,u4,u5]
	uactual = my_layer._get_u(my_layer._q_on)
	assert(len(udesired) == len(uactual))
	for i in range(len(udesired)):
		# print udesired[i]
		# print uactual[i]
		delta_abs = (udesired[i]-uactual[i])
		if delta_abs>5*10.0**-3:
			raise AssertionError("""u%d wrong by %f.
				udesired : %f
				uactual : %f
				""" % (i,delta_abs,udesired[i],uactual[i])
				)
		else:
			pass


def test_q_off_values():
	global my_layer
	q_off_desired = numpy.array([[6.58],[6.58],[4.53], [5.16], [4.71], [4.71]])
	assert(my_layer._q_off.all() == q_off_desired.all())



# test_assign 

# test_u with answers

# test_q_off with answers





