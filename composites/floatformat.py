import math
# import re
def floatformat(num, tot_length = None, precision = 3):
	"""Documentation required.

	Default total string length = 10 because that's sufficient for printing
	numpy arrays

	no_d stands for no digits after decimal
	"""

	###############################################################
	#################    MAHDI REQUEST          ###################
	Mahdi = True
	if Mahdi:
		if tot_length is None:
			tot_length = 8
		return "%*.*f" % (tot_length, 4, float(num))
	###############################################################
	
	if num == 0.0 :
		return ' '*(tot_length-3)+'0.0'
	try:
		num = float(num)
		precision = int(precision)
		tot_length = int(tot_length)
	except:
		raise

	###############################################################
	#ALWAYS USE ENGINEERING WITH INPUT PRECISION###################
	engineering = False
	if engineering:
		if tot_length is None:
			tot_length = 10
		if num == 0.0 :
			return ' '*(tot_length-3)+'0.0'
		return "%*.*e" % (tot_length, precision, float(num))
	###############################################################
	

	left,right = str(num).split('.')
	mag = int(math.log10(abs(num)))
	if mag >= 2 or mag <= -2: #Really big or really small numbers
		str_num = "%*.*e" % (tot_length, precision, num)
	elif left == '0': #e.g 0.01234
		# if mag > 2:
		# 	str_num = "%*.*e" % (tot_length, precision, num)
		# else:
		str_num = "%*.*f" % (tot_length, precision + mag, num)
	elif not any(right.split('0')): #e.g 1234.00000
		# if mag > 3:
		# 	str_num = "%*.*e" % (tot_length, precision, num)
		# else:
		str_num = "%*.*f" % (tot_length, 1, num)
	else:
		str_num = "%*.*f" % (tot_length, precision, num)

	return str_num

if __name__ == '__main__':
	import sys
	val = floatformat(sys.argv[1])
	print val

