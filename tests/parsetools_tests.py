from nose.tools import *
from composites.parsetools import *

def test_layup_one():
	the_layup,symmetry = parse_layup('90_2/p40/p20/0s')
	the_answer = [90,90,40,-40,20,-20,0,0,-20,20,-40,40,90,90]
	assert_equal(the_layup, the_answer)
	assert(symmetry == True)

def test_layup_two():
	the_layup,symmetry = parse_layup('m90/30_2/p90/45')
	the_answer = [-90,90,30,30,90,-90,45]
	assert_equal(the_layup,the_answer)
	assert(symmetry == False)

def test_parse_request():
	ret = parse_request('QS')
	assert (ret == ['S_on','S_off','Q_on','Q_off'])

	ret = parse_request('QSoff')
	assert (ret == ['S_off','Q_off'])

	ret = parse_request('QSon')
	assert (ret == ['S_on','Q_on'])

	ret = parse_request('Q')
	assert (ret == ['Q_on','Q_off'])

@raises(AssertionError)
def test_parse_request_no_qs():
	ret = parse_request('Pon')

@raises(AssertionError)
def test_parse_request_nothing():
	ret = parse_request('P')

	