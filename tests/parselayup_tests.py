from nose.tools import *
from composites.parselayup import *

def test_one():
	the_layup = parse_layup('90_2/p40/p20/0s')
	the_answer = [90,90,40,-40,20,-20,0,0,-20,20,-40,40,90,90]
	assert_equal(the_layup, the_answer)

def test_two():
	the_layup = parse_layup('m90/30_2/p90/45')
	the_answer = [-90,90,30,30,90,-90,45]
	assert_equal(the_layup,the_answer)
	