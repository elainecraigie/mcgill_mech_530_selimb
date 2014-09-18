#ASSUME THAT A THERE IS NO "element" pTHETA_n, only pTHETA or THETA_n
import sys
def parse_layup(layup_input):
	"""Returns orientation list given layup string following convention. 

	-Separate angles with /.
	-Use '_n' to repeat an angle n times.
	-prefix angle with 'p' or 'm' for plus-mins or minus-plus respectively. 
	-Append with s (no extra /) for symmetric

	Example : '90_2/p40/p20/0s' -> [90,90,40,-40,20,-20,0]s
	"""

	layup = layup_input
	orientation=[]
	symmetric = False
	if layup.endswith('s'):
		layup=layup[:-1]
		if 's' in layup:
			print "s must be added at the very end. You wrote : %s" % layup_input
			sys.exit(1)
		symmetric = True
	layup_slash = layup.split('/')

	for i in layup_slash:
		check_p = False
		#check for repetition
		rep = i.split('_')
		if len(rep)==2:
			orientation.extend([int(rep[0])] * int(rep[1]))
			continue
		elif len(rep)==1:
			pass
			# orientation.append(int(rep))
		else:
			print "%r is not a valid orientation" % i
			sys.exit(1)

		#check for plus or minus. step not reached if i contains '_'
		if 'p' in i:
			val = int(i.split('p')[1])
			orientation.extend([val,-val])
		elif 'm' in i:
			val = int(i.split('m')[1])
			orientation.extend([-val,val])
		else:
			orientation.append(int(i))

	if symmetric:
		orientation.extend(orientation[::-1])

	return orientation, symmetric

def parse_request(the_string):
	"""Used to parse request of arrays to be printed/modified/obtained.
	Returns a list of array_names.
	"""
	prefix_list = ['S','Q']; suffix_list = ['on','off']
	the_prefix = []; the_suffix = []
	prefix_found = False
	#Parse the input string to account for variations
	for a_prefix in prefix_list:
		if a_prefix in the_string:
			the_prefix.append(a_prefix)
			prefix_found = True

	if not prefix_found:
		raise AssertionError("Could not parse %s request" % the_string)

	sufix_found = False
	for a_suffix in suffix_list:
		if a_suffix in the_string:
			sufix_found = True
			the_suffix.append(a_suffix)
	#If neither 'on' or 'off' was found, assume user wants both.
	if not sufix_found:
		the_suffix= suffix_list

	array_list = []
	for a_prefix in the_prefix:
		for a_suffix in the_suffix:
			array_name = '%s_%s' % (a_prefix,a_suffix)
			array_list.append(array_name)

	return array_list


if __name__ == "__main__":
	the_layup = parse_layup('90_2/p40/p20/0s')
	the_answer = [90,90,40,-40,20,-20,0,0,-20,20,-40,40,90,90]
	assert (the_layup == the_answer)
	
