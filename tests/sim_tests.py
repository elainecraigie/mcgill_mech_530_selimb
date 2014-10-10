from nose.tools import *
from composites.sim import transform_stress,transform_strain, Sim, ureg, Q_
import numpy
from numpy.testing import assert_array_almost_equal
from composites.laminate import Laminate

# def setup():
# 	global my_sim
# 	my_sim = Sim(Laminate('45/90',2))

def array_assert(x,y,precision = 6):
		import numpy
		from numpy.testing import assert_array_almost_equal
		a = numpy.array(x, dtype = float)
		b = numpy.array(y, dtype = float)
		assert_array_almost_equal(a,b,decimal = precision)

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

def test_Sim_not_a_kw():
	try:
		sim = Sim(5)
	except TypeError:
		pass
	else:
		raise AssertionError

def test_Sim_laminate():
	my_lam = Laminate('45/90',2)
	sim = Sim(laminate = my_lam)

def test_Sim_layup_id():
	my_lam = Laminate('45/90',2)
	sim = Sim(layup = '45/90',materialID = 2)

def test_Sim_wrong_key():
	try:
		Sim(layup = '45/90')
	except KeyError:
		pass
	else:
		raise AssertionError

def test_Sim_wrong_key_2():
	try:
		Sim(blah = '45/90')
	except KeyError:
		pass
	else:
		raise AssertionError

def test_Sim_ass_3():
	my_sim = Sim(layup = 'p10/90/0_2/p50s', materialID = 1)
	my_sim.apply_N(numpy.array([[0.4500],[-0.1100],[-0.1300]])*ureg.MNperm)
	array_assert(my_sim.e0,numpy.array([   0.0025,-0.0019,-0.0038]),
												precision = 4)

def test_apply_M_k_Sim_p96():
	global my_sim_p96
	my_sim_p96 = Sim(layup = '0_4/90_4s',materialID = 1)
	P = -100 * ureg.N
	L = 0.1 * ureg.meter
	b = 0.01 * ureg.meter
	moment = P*L/(4*b)
	M = Q_([moment.magnitude,0,0],moment.units)
	k,e = my_sim_p96.apply_M(M,True)
	assert(e.shape == (my_sim_p96.laminate.num_of_layers(),2,3))
	array_assert(k,[-2.34,0.213,0],precision = 2)

def test_strain_Sim_p96_manual():
	global my_sim_p96
	global e1, e2, e6
	z_top = my_sim_p96.laminate.layers[-1].z_top
	array_assert(z_top,1*10**-3)
	e1 = z_top*my_sim_p96.k[0]
	e2 = z_top*my_sim_p96.k[1]
	e6 = z_top*my_sim_p96.k[2]
	array_assert([e1,e2,e6],[-2.34*10**-3,0.212*10**-3,0],precision = 5)

def test_strain_Sim_p96():
	global my_sim_p96
	array_assert(my_sim_p96.e_k[-1,1,:],[-2.34*10**-3,0.212*10**-3,0],precision = 5)


def test_stress_Sim_p96():
	global my_sim_p96
	global e1, e2, e6
	sigma = my_sim_p96.laminate.layers[-1].Q_on.dot([e1,e2,e6])
	print my_sim_p96.laminate.layers[-1].Q_on
	print [e1,e2,e6]
	print sigma
	array_assert(sigma,[-0.424,-0.00457,0],precision = 3)

def test_compute_off_strain_p96():
	global my_sim_p96
	my_sim_p96._compute_off_strain()
	array_assert(my_sim_p96.off_strain[-1,1,:]*10**3,[-2.34,0.212,0],precision = 2)

def test_compute_on_strain_p96():
	global my_sim_p96
	my_sim_p96._compute_on_strain()
	array_assert(my_sim_p96.on_strain[-1,1,:]*10**3,[-2.34,0.212,0],precision = 2)







