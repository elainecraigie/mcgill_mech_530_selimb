from nose.tools import *
from composites.laminate import Laminate
from composites.parsetools import parse_request

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
	my_laminate.compute_all(method = 'dumb')
	Q_on_old = my_laminate.layers[0].Q_on
	for layer in my_laminate.layers:
		Q_on_new = layer.Q_on
		assert(Q_on_old.all() == Q_on_new.all())
		Q_on_old = Q_on_new

def test_S_on_uniform():
	global my_laminate
	my_laminate.compute_all(method = 'dumb')
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

def test_smart_vs_dumb():
	my_dumb = Laminate('90_2/p40/p20/0s',2)
	my_dumb.compute_all(method='dumb')

	my_smart = Laminate('90_2/p40/p20/0s',2)
	my_smart.compute_all(method='smart')
	print len(my_smart.layers)
	for i in range(len(my_smart.layers)):
		for j in parse_request('QS'):
			smart = getattr(my_smart.layers[i],j).all()
			dumb = getattr(my_dumb.layers[i],j).all()
			assert(smart == dumb)

def test_smart_q_s_on_uniform():
	my_smart = Laminate('90_2/p40/p20/0s',2)
	my_smart.compute_all(method='smart')

	Q_on_0 = my_smart.layers[0].Q_on
	S_on_0 = my_smart.layers[0].S_on
	for layer in my_smart.layers:
		assert(layer.Q_on.all() == Q_on_0.all())
		assert(layer.S_on.all() == S_on_0.all())

# def 





		



