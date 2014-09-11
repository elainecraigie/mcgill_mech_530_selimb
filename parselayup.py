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

	return orientation

if __name__ == "__main__":
	the_layup = parse_layup('90_2/p40/p20/0s')
	the_answer = [90,90,40,-40,20,-20,0,0,-20,20,-40,40,90,90]
	assert (the_layup == the_answer)
	
