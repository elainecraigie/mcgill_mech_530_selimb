from nose.tools import *
from composites.layer import *
import numpy
from scipy import linalg as scilin
from composites.sim import transform_stress,transform_strain


def array_assert(x,y, precision = 6):
		import numpy
		from numpy.testing import assert_array_almost_equal
		a = numpy.array(x, dtype = float)
		b = numpy.array(y, dtype = float)
		assert_array_almost_equal(a,b,decimal = precision)

def setup():
	global my_layer
	my_layer = Layer(2,45)
	my_layer.compute_all()

def test_z():
	global my_layer
	my_layer.set_z(4,5)
	assert([4,5]==my_layer.get_z())

def test_compute_all_force():
	global my_layer
	modified = my_layer.compute_all(force = True)
	assert(len(modified)==4)
	all_arrays = ['Q_on','S_on','S_off','S_off']
	counter = 0
	for array in all_arrays:
		if array in modified:
			counter += 1

	assert(counter == 4)

def test_compute_all_partial():
	my_layer = Layer(2,45)
	my_layer.set({})
	new_Q_off = numpy.ones([3,3])
	new_S_on = numpy.zeros([3,3])
	my_changes = {'Q_off':new_Q_off,
								'Son':new_S_on}
	my_layer.set(my_changes)

	modified = my_layer.compute_all()
	modified_desired = ['Q_on','S_off']
	assert(modified == modified_desired or modified == modified_desired[::-1])

def test_all_found_when_setup():
	global my_layer
	assert(my_layer.Q_on_found)
	assert(my_layer.Q_off_found)
	assert(my_layer.S_on_found)
	assert(my_layer.S_off_found)

def test_is_found():
	global my_layer
	assert(my_layer.is_found() is True)
	
def test_print_param():
	import os
	global my_layer
	# my_layer = Layer(2,45)
	my_layer.print_param()

@raises(AttributeError)
def test_set_non_dict():
	my_layer = Layer(2,45)
	my_layer.compute_all()
	A = numpy.ones([3,3])
	my_layer.set(['Q',A])

@raises(AssertionError)
def test_set_non_array():
	my_layer = Layer(2,45)
	my_layer.compute_all()
	A = numpy.ones([3,3])
	B = [[1,2,3],[4,5,6],[7,8,9]]
	my_layer.set({'Qon':A,'Son':B})

@raises(AssertionError)
def test_set_mul_array():
	my_layer = Layer(2,45)
	my_layer.compute_all()
	A = numpy.ones([3,3])
	B = numpy.ones([3,3])
	my_layer.set({'Qon':(A,B)})

def test_set():
	my_layer = Layer(2,45)
	new_Q_on = numpy.ones([3,3])
	my_layer.set({'Qon':new_Q_on})
	assert(my_layer.Q_on_found)
	array_assert (my_layer.Q_on, new_Q_on)

def test_set_multiple():
	my_layer = Layer(2,45)
	new_Q_off = numpy.ones([3,3])
	new_S_on = numpy.zeros([3,3])
	my_changes = {'Q_off':new_Q_off,
								'Son':new_S_on}
	my_layer.set(my_changes)
	assert(my_layer.Q_off_found)
	assert(my_layer.S_on_found)

def test_u_values_2_book():
	global my_layer
	u1 = 59.66; u2=64.90; u3=14.25; u4=16.96; u5=21.35;
	udesired = [u1,u2,u3,u4,u5]
	uactual = my_layer._compute_u('Q')
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

def test_u_values_1_book():
	my_layer = Layer(1,45)
	my_layer.compute_all()
	u1 = 76.37; u2=85.73; u3=19.71; u4=22.61; u5=26.88;
	udesired = [u1,u2,u3,u4,u5]
	uactual = my_layer._compute_u('Q')
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

def test_inverse_on():
	global my_layer
	S_on_inv = scilin.inv(my_layer.S_on)
	Q_on = my_layer.Q_on
	array_assert (Q_on, S_on_inv)

def test_inverse_off():
	global my_layer
	S_off_inv = scilin.inv(my_layer.S_off)
	Q_off = my_layer.Q_off
	array_assert (Q_off, S_off_inv)

def test_q_off_values_book():
	global my_layer
	q_off_desired = numpy.array([[45.41],[45.41],[31.21], [35.6], [32.45], [32.45]])
	array_assert(my_layer._q_off, q_off_desired, 2)

#Values from 
#http://www.efunda.com/formulae/solid_mechanics/composites/calc_ufrp_cs_arbitrary.cfm
def test_s_off_values_internet():
	S_desired = numpy.array([[  0.05102,  -0.02438,  -0.06186],
       [ -0.02438,   0.09256,  -0.01009],
       [ -0.06186,  -0.01009,   0.1326]])
	my_layer = Layer(0,30)
	my_layer.compute_all()
	array_assert(my_layer.S_off,S_desired,4)

def test_q_off_values_internet():
	Q_desired = numpy.array([[77.27, 24.48, 37.92],
										[24.48, 18.65, 12.84],
										[37.92, 12.84, 26.22]])
	my_layer = Layer(0,30)
	my_layer.compute_all()
	array_assert(my_layer.Q_off,Q_desired,2)

def test_off_stress_to_off_strain():
	off_stress = numpy.array([10,20,30]) #input
	angle = 40
	my_layer = Layer(2,angle)
	my_layer.compute_all()

	off_strain_fast = my_layer.S_off.dot(off_stress)

	on_stress = transform_stress(off_stress,'off',angle)
	on_strain = my_layer.S_on.dot(on_stress)
	off_strain = transform_strain(on_strain,'on',angle)

	array_assert(off_strain,off_strain_fast)


def test_by_hand():
	import numpy
	from math import cos, sin, radians
	load = numpy.array([1,0,0])
	angle = 30
	tet = radians(float(angle))
	my_layer = Layer(2,angle)
	my_layer.compute_all()

	off_strain_fast = my_layer.S_off.dot(load)
	
	#On-axis stress
	on_stress_auto = transform_stress(load, 'off',angle)
	
	m = cos(tet)	
	n = sin(tet)
	sigma_x = m**2*load[0] + n**2*load[1] + 2*m*n*load[2]
	sigma_y = n**2*load[0] + m**2*load[1] -2*m*n*load[2]
	sigma_s = -m*n*load[0] + m*n*load[1]+(m**2 - n**2)*load[2]
	sigma_on = numpy.array([sigma_x, sigma_y, sigma_s])

	array_assert(sigma_on,on_stress_auto)

	#On-axis strain
	on_strain_auto = my_layer.S_on.dot(on_stress_auto)
	
	ex = my_layer.PROPS['ex']
	ey = my_layer.PROPS['ey']
	es = my_layer.PROPS['es']
	nuy = my_layer.PROPS['nuy']
	nux = my_layer.PROPS['nux']
	epsx = sigma_on[0]/ex + sigma_on[1]*(-nuy)/ey
	epsy = sigma_on[0]*(-nux)/ex + sigma_on[1]/ey 
	epss = + sigma_on[2]/es
	eps_on = numpy.array([epsx,epsy,epss])

	array_assert(eps_on,on_strain_auto)
	print eps_on
	print on_strain_auto

	#Off-axis strain
	off_strain_auto = transform_strain(on_strain_auto,'on',angle)

	m = cos(-tet)
	n = sin(-tet)
	eps1 = m**2*epsx+n**2*epsy+m*n*epss
	eps2 = n**2*epsx+m**2*epsy-m*n*epss
	eps6 = -2*m*n*epsx + 2*m*n*epsy + (m**2-n**2)*epss
	eps_off = numpy.array([eps1,eps2,eps6])

	print eps_off
	print off_strain_auto
	array_assert(eps_off,off_strain_auto)

	#Long auto vs short auto
	print off_strain_auto
	print off_strain_fast
	array_assert(off_strain_auto,off_strain_fast)




	







