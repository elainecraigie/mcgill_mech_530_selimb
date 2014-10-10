from nose.tools import *
from composites.laminate import Laminate
from composites.parsetools import parse_request


def array_assert(x,y,precision = 6):
		import numpy
		from numpy.testing import assert_array_almost_equal
		a = numpy.array(x, dtype = float)
		b = numpy.array(y, dtype = float)
		assert_array_almost_equal(a,b,decimal = precision)

def setup():
	global my_laminate
	my_laminate = Laminate('90_2/p40/p20/0s',2)

def test_number_of_plies():
	global my_laminate
	assert(len(my_laminate.layers)==14)
	assert(my_laminate.num_of_layers() == 14)

def test_index():
	global my_laminate
	for i in range(14):
		assert(my_laminate.layers[i].index == i)

def test_total_thickness():
	global my_laminate
	assert(my_laminate.total_thickness == 0.125*14/1000)
	assert(not my_laminate.has_core)

def test_core_thickness():
	my_laminate = Laminate('90_2/p40/p20/0s',2, core_thick = 0.01)
	assert(my_laminate.total_ply_thickness == 0.125*14/1000)
	assert(my_laminate.total_thickness == 0.125*14/1000 + 0.01)
	assert(my_laminate.has_core)

def test_z_no_core():
	global my_laminate
	assert (my_laminate.layers[0].z_bot == -0.000875)
	assert (my_laminate.layers[13].z_top == 0.000875)
	assert (my_laminate.layers[6].z_top == my_laminate.layers[7].z_bot)

def test_z_w_core():
	my_laminate = Laminate('90_2/p40/p20/0s',2, core_thick = 1)
	# print "%.9f" % (my_laminate.layers[0].z_bot)
	print "%.9f" % (my_laminate.layers[13].z_top)
	array_assert (my_laminate.layers[0].z_bot, float(-0.500875))
	array_assert (my_laminate.layers[13].z_top, float(0.500875000))
	print -my_laminate.layers[6].z_top
	print my_laminate.layers[7].z_bot
	array_assert (float(my_laminate.layers[6].z_top), 
							-1.0*float(my_laminate.layers[7].z_bot))

def test_print_param():
	global my_laminate
	my_laminate.print_param()

def test_Q_on_uniform():
	global my_laminate
	my_laminate.compute_all(method = 'dumb')
	Q_on_old = my_laminate.layers[0].Q_on
	for layer in my_laminate.layers:
		Q_on_new = layer.Q_on
		array_assert(Q_on_new,Q_on_old)
		Q_on_old = Q_on_new

def test_S_on_uniform():
	global my_laminate
	my_laminate.compute_all(method = 'dumb')
	S_on_old = my_laminate.layers[0].S_on
	for layer in my_laminate.layers:
		S_on_new = layer.S_on
		array_assert(S_on_new,S_on_old)
		S_on_old = S_on_new

def test_orientation_order():
	global my_laminate
	str_layup_all = "%s" % my_laminate.layup

	list_layup = []
	for layer in my_laminate.layers:
			list_layup.append(layer.theta)
	str_layup_individual = "%s" % list_layup
	assert(str_layup_all == str_layup_individual)

def test_props():
	global my_laminate
	props_0 = my_laminate.layers[0].PROPS

	for layer in my_laminate.layers:
		assert(layer.PROPS == props_0)

def test_smart_vs_dumb():
	my_dumb = Laminate('90_2/p40/p20/0s',2)
	my_dumb.compute_all(method='dumb')

	my_smart = Laminate('90_2/p40/p20/0s',2)
	my_smart.compute_all(method='smart')
	print len(my_smart.layers)
	for i in range(len(my_smart.layers)):
		for j in parse_request('QS'):
			smart = getattr(my_smart.layers[i],j)
			dumb = getattr(my_dumb.layers[i],j)
			array_assert(smart,dumb)

def test_smart_q_s_on_uniform():
	my_smart = Laminate('90_2/p40/p20/0s',2)
	my_smart.compute_all(method='smart')

	Q_on_0 = my_smart.layers[0].Q_on
	S_on_0 = my_smart.layers[0].S_on
	for layer in my_smart.layers:
		array_assert(layer.Q_on, Q_on_0)
		array_assert(layer.S_on,S_on_0)

def test_cross_ply():
	import numpy
	my_lam = Laminate('0/90/0/90/0/90/0/90',2)
	my_lam.compute_all()

	should_be_zero = numpy.absolute(numpy.array([my_lam.A_vec[-2:],
																							my_lam.a_vec[-2:]
																							]).reshape(4,))
	zeros = [0]*4
	print should_be_zero
	print zeros
	array_assert(should_be_zero,zeros) 

def test_angle_ply():
	import numpy
	my_lam = Laminate('p45s',2)
	my_lam.compute_all()

	should_be_zero = numpy.absolute(numpy.array([my_lam.A_vec[-2:],
																							my_lam.a_vec[-2:]
																							]).reshape(4,))
	zeros = [0]*4
	print should_be_zero
	print zeros
	array_assert(should_be_zero,zeros) 

def test_values_p56_30degrees():
	import numpy
	my_lam = Laminate('p30',1)
	my_lam.compute_all()

	A = numpy.array(my_lam.A_vec)/my_lam.total_thickness
	A_desired = [109.3,23.6, 32.46, 36.73, 0, 0]
	a = numpy.array(my_lam.a_vec)*my_lam.total_thickness*1000
	a_desired = [15.42, 71.36, -21.18, 27.22, 0, 0]
	array_assert(A,A_desired,precision = 1)
	array_assert(a,a_desired,precision = 1)

def test_values_p56_75degrees():
	import numpy
	my_lam = Laminate('m75',1)
	my_lam.compute_all()
	print my_lam.layup
	print my_lam.A_vec

	A = numpy.array(my_lam.A_vec)/my_lam.total_thickness
	A_desired = [11.9,160.4, 12.75, 17.02, 0, 0]
	a = numpy.array(my_lam.a_vec)*my_lam.total_thickness*1000
	a_desired = [91.21, 6.80, -7.24, 58.73, 0, 0]
	array_assert(A,A_desired,precision = 1)
	array_assert(a,a_desired,precision = 1)

def test_quasi_isotropic():
	import numpy
	my_lam = Laminate('0/p60s',1)
	my_lam.compute_all()

	A = my_lam.A_vec
	array_assert(A[0],A[1])
	array_assert(A[-1],0.0)
	array_assert(A[-2],0.0)
	array_assert((A[0]-A[2])/2, A[3])

def test_d_cross_m_4():
	import numpy
	layup = '0_4/90_4s'
	my_cross = Laminate(layup,1)
	my_cross.compute_all()
	D_desired = numpy.array([[106.9,1.93,0.0],
													[1.93,21.18,0.0],
													[0.0,0.0,4.78]
													])
	d_desired = numpy.array([[9.36,-0.85,0],
													[-0.85,47.27,0],
													[0.0,0.0,209.2]
													])
	array_assert(my_cross.D*10**9 , D_desired,precision = 1)
	array_assert(my_cross.d*10**-6 , d_desired,precision = 1)

def test_computed():
	layup = '0_4/90_4s'
	my_lam = Laminate(layup,1)
	assert(my_lam.computed == False)
	assert(my_lam.compute_all() == True)
	assert(my_lam.compute_all() == False)




		



