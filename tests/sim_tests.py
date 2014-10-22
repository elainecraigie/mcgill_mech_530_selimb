# from nose.tools import *
from composites.sim import transform_stress,transform_strain, Sim, ureg, Q_
from composites.sim import make_test_sim
import numpy
from numpy.testing import assert_array_almost_equal
from composites.laminate import Laminate
import warnings

# def setup():
# 	global my_sim
# 	my_sim = Sim(Laminate('45/90',2))

def array_assert(x,y,precision = 6):
		import numpy
		from numpy.testing import assert_array_almost_equal
		a = numpy.array(x, dtype = float)
		b = numpy.array(y, dtype = float)
		assert_array_almost_equal(a,b,decimal = precision)

def array_assert_error(value,desired,tol = 2):
	"""Error is in \%"""
	engformat = lambda x: "%.4e" % x
	numpy.set_printoptions(formatter = {'float_kind':engformat})
	a = numpy.array(value,dtype=float)
	b = numpy.array(desired,dtype=float)
	# warnings.filterwarnings('error')
	# try:
	nonzero = numpy.array(b,dtype=bool)
	err = numpy.array([(a[i]-b[i])/b[i] for i in range(len(a)) if nonzero[i]])
	# err = numpy.abs(numpy.where(cond,(a-b)/b,a*10**15))
	errmax = err.max()*100
	try:
		# raise AssertionError
		assert( errmax <= float(tol))
	except AssertionError:
		message = ''
		message += "value  = %s" % a + '\n'
		message += "desired = %s" % b + '\n'
		message += "error = %s" % err + '\n'
		message += "max_error = %.2f %%" % errmax + '\n'
		message += "tolerance = %.2f %%" % tol
		raise AssertionError(message)


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
	#####From assignment 3####
	laminate_q1 = Laminate('p10/90/0_2/p50s',
                       materialID = 1)
	laminate_q1.compute_all()
	load = numpy.array([450000,-110000,-130000],dtype=float)
	load = load*10**-6
	off_stress_norm = load*10**-3
	off_strain = laminate_q1.a.dot(off_stress_norm).reshape((3,1))
	on_strain = numpy.empty((14,3))
	on_stress = numpy.empty((14,3))
	for i in range(14):
		layer = laminate_q1.layers[i]
		on_strain[i,:] = transform_strain(off_strain,'off',layer.theta)
		on_stress[i,:] = laminate_q1.layers[0].Q_on.dot(on_strain[i,:])
	######
	######From new Sim####
	#####
	my_sim = Sim(layup = 'p10/90/0_2/p50s', materialID = 1)
	my_sim.apply_N(numpy.array([[0.4500],[-0.1100],[-0.1300]])*ureg.MNperm)
	my_sim.solve()
	sim_off_strain = numpy.vstack(my_sim.off_strain)
	sim_on_strain = numpy.vstack(my_sim.on_strain)
	sim_on_stress = numpy.vstack(my_sim.on_stress)
	# sim_off_stress = numpy.vstack(my_sim.off_stress)
	for row in sim_off_strain:
		# print row
		array_assert_error(row,off_strain,tol = 0.001)
	# for row in sim_on_strain:
	# 	array_assert_error(row,on_strain,tol=0.001)
	array_assert(sim_on_strain[0::2,:],on_strain,precision = 10)
	array_assert(sim_on_strain[1::2,:],on_strain,precision = 10)
	array_assert(sim_on_stress[0::2,:],on_stress,precision = 10)
	array_assert(sim_on_stress[1::2,:],on_stress,precision = 10)
	# for row in sim_on_stress:
	# 	print row
	# 	array_assert_error(row,on_stress,tol=0.001)

		
	# array_assert_error(my_sim.on_strain[:,:,:],on_strain)


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
	array_assert(my_sim_p96.off_strain[-1,1,:],
							 [-2.34*10**-3,0.212*10**-3,0],
							 precision = 5
							)

def test_compute_on_strain_p96():
	global my_sim_p96
	my_sim_p96._compute_on_strain()
	array_assert(my_sim_p96.on_strain[-1,1,:]*10**3,[-2.34,0.212,0],precision = 2)

def test_compute_on_stress_p96():
	global my_sim_p96
	my_sim_p96._compute_on_stress()
	desire = numpy.array([-424,-4.57,0])*10**-3
	array_assert_error(my_sim_p96.on_stress[-1,1,:],desire )

def test_compute_off_stress_p96():
	global my_sim_p96
	my_sim_p96._compute_off_stress()
	desire = numpy.array([-424,-4.57,0])*10**-3
	array_assert_error(my_sim_p96.off_stress[-1,1,:],desire)

def test_solve_N():
	sim = Sim(layup = '45/90',materialID = 2)
	assert(not sim.solved)
	try:
		sim.solve()
	except sim.WorkflowError:
		pass
	else:
		raise AssertionError("""Did not get a WorkflowError when solving 
			before applying""")
	assert(not sim.solved)
	sim.apply_N([500,500,500]*ureg.MNperm)
	sim.solve()
	assert(sim.solved)

def test_solve_M():
	sim = Sim(layup = '45/90',materialID = 2)
	assert(not sim.solved)
	try:
		sim.solve()
	except sim.WorkflowError:
		pass
	else:
		raise AssertionError("""Did not get a WorkflowError when solving 
			before applying""")
	assert(not sim.solved)
	sim.apply_M([500,500,500]*ureg.MN)
	sim.solve()
	assert(sim.solved)

def test_apply_units():
	sim = Sim(layup = '45/90',materialID = 2)
	P = Q_(1000,'N'); b = Q_(0.11,'m'); L = Q_(0.51,'m')
	M1 = -P*L/(4*b); N1 = 0.5*P/b;
	M = Q_([M1.magnitude,0,0],M1.units)
	N = Q_([N1.magnitude,0,0],N1.units)
	print type(N1)
	try:
		sim.apply_M(M) 
		sim.apply_N(N) 
		sim.apply_N(N1)
		sim.apply_M(M1)
	except:
		raise

def test_make_test_sim():
	sim = make_test_sim()
	assert(sim.loaded)
	assert(sim.solved)

def test_get_stress():
	sim = make_test_sim()
	sim.get_stress()

 









