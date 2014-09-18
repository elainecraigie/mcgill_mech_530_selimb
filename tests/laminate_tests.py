from nose.tools import *
from composites.laminate import Laminate

def setup():
	global my_laminate
	my_laminate = Laminate('90_2/p40/p20/0s',2)

def test_number_of_plies():
	global my_laminate
	assert(len(my_laminate.layers)==14)

def test_total_thickness():
	global my_laminate
	assert(my_laminate.total_thickness == 0.125*14)

def test_print_param():
	global my_laminate
	my_laminate.print_param()

def test_Q_on_uniform():
	global my_laminate
	my_laminate.compute_all()
	Q_on_old = my_laminate.layers[0].Q_on
	for layer in my_laminate.layers:
		Q_on_new = layer.Q_on
		assert(Q_on_old.all() == Q_on_new.all())
		Q_on_old = Q_on_new

def test_S_on_uniform():
	global my_laminate
	my_laminate.compute_all()
	S_on_old = my_laminate.layers[0].S_on
	for layer in my_laminate.layers:
		S_on_new = layer.S_on
		assert(S_on_old.all() == S_on_new.all())
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
# def test_


		



