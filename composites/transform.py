"""Transforms strain/stress from off-axis to on-axis and vice-versa.
Arguments:
	-values : List or vector of stresses or strains [1,2,6] or [x,y,s]
	-Input_axis : 'on' or 'off'
		The opposite will be returned
	-Angle:
		In degrees. Angle positive in counter-clockwise rotation.
		Don't input modified angle.
"""
import numpy
from math import cos,sin,radians

def transform_stress(values,input_axis,angle):
	if input_axis == 'on':
		angle = radians(-1*float(angle))
	elif input_axis == 'off':
		angle = radians(float(angle))
	else:
		raise AssertionError("%s not valid for transform" % input_axis)

	# A = numpy.array([[1, cos(2*angle), sin(2*angle)],
	# 								[1, -cos(2*angle), -sin(2*angle)],
	# 								[0, -sin(2*angle), cos(2*angle)]
	# 								])
	p = float((values[0]+values[1])/2.0)
	q = float((values[0]-values[1])/2.0)
	r = float(values[2])
	# b = numpy.array([p,q,r])
	A = numpy.array([[p,q,r],[p,-q,-r],[0,r,-q]])
	b = numpy.array([1,cos(2*angle),sin(2*angle)]) 
	ret_array = A.dot(b)
	return ret_array

if __name__ == '__main__':
	sigma_on = transform([420,-165,-135],'off',30)

def transform_strain(values,input_axis,angle):
	if input_axis == 'on':
		angle = radians(-1*float(angle))
	elif input_axis == 'off':
		angle = radians(float(angle))
	else:
		raise AssertionError("%s not valid for transform" % input_axis)
	p = float((values[0]+values[1])/2.0)
	q = float((values[0]-values[1])/2.0)
	r = float(values[2]/2.0)
	A = numpy.array([[p,q,r],[p,-q,-r],[0, 2*r, -2*q]])
	b = numpy.array([1, cos(2*angle), sin(2*angle)])
	ret_array = A.dot(b)
	return ret_array
