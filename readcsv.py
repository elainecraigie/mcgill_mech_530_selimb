#TODO

units_dict = {
'ID' : '-',
'fiber/matrix': '-',
'name': '-',
'ex' :'GPA',
'ey' :'GPA',
'es' :'GPA',
'nux':	'-',
'xt' :'MPA',
'xc' :'MPA',	
'yt'	:'MPA',
'yc'	:'MPA',
'sc'	:'MPA',
'h0': 'mm',
'nuy': '-'
}
#DONT THINK I NEED THIS
# class CsvDict(dict):
# 	"""dot.notation access to dictionary attributes"""

# 	# def __init__(self, materialID,file_name):
# 	# 	ret = readcsv(materialID,file_name)
# 	# 	self.headers = ret.pop('headers') #A list
# 	# 	self.rows = ret #A dictiona
# 	def __getattr__(self, attr):
# 		return self.get(attr)
#   __setattr__= dict.__setitem__
#   __delattr__= dict.__delitem__

def makeint(my_dict):
	for key, value in my_dict.iteritems():
		try:
			my_dict[key] = int(value)
		except ValueError: #Not an int. Could be a float
			try:
				my_dict[key] = float(value)
			except ValueError: #Must be a string. Let it go. 
				pass
		except TypeError: #This happens for lists like my_dict['headers'].
			pass
	# return my_dict  ## NOT NEEDED

def readcsv(materialID,file_name):
	"""Look for ID in materialprops.csv and return the row as a dict.
	Values are all integers (if possible) 
	Dict also contains key 'headers' which contains headers in csv-order -- 
	useful if you want to print contents in order.

	***Also computes nuy"""
	material_found = False
	# try:
	#   import sys
	# 	materialID = sys.argv[1]
	# except IndexError:
	# 	print "You must specify a material ID as first and only command-line argument"
	# 	sys.exit(1)

	with open(file_name,'r') as f:
		import csv
		reader = csv.DictReader(f)
		headers = reader.fieldnames
		for row in reader:
			#Row of units has no ID.
			if int(row['ID']) == int(materialID):
				material_found = True
				row['headers'] = headers
				makeint(row)
				row['nuy'] = row['nux']*row['ey']/row['ex']
				row['headers'].append('nuy')
				return row#, the_units

		if not material_found:
			print "Material %s could not be found in %s" % ( materialID, 
																											'materialprop.csv')
			import sys
			sys.exit(1)

class iter_csvdict():
	"""Iterator which prints return of readcsv() in order
	Units are optional
	"""
	def __init__(self,input_csvdict):
		self.csvdict = input_csvdict
		self.length = len(self.csvdict['headers'])

	def __iter__(self):
		
		self.headers = self.csvdict['headers']
		self.index = 0
		self.max_str_length = self._getlongeststring()
		return self

	def next(self):
		from floatformat import floatformat
		if self.index == self.length:
			raise StopIteration
		header = self.headers[self.index]
		value = self.csvdict[header]
		unit = units_dict[header]
		self.index += 1
		try:
			formatted_value = floatformat(num = value,
																	 tot_length = self.max_str_length,
																	 )
			if header == 'ID':
				formatted_value = "%*d" % (self.max_str_length,value)
			# return '%12s : %*.3e [%s]' % (header, self.max_str_length, value, unit)
		except ValueError:
			formatted_value = "%*s" % (self.max_str_length, value)
			# return '%12s : %*s [%s]' % (header, self.max_str_length, value, unit)

		return '%12s : %s  [%s]' % (header, formatted_value, unit)

	def _getlongeststring(self):
		"""Code from 
		http://stackoverflow.com/questions/9281788/get-longest-element-in-dict
		"""
		maks=max(self.csvdict, key=lambda k: len(str(self.csvdict[k])))
		return int(len(self.csvdict[maks]))	

if __name__ == "__main__":
	PROPS = readcsv('2','materialprops.csv')
	for i in iter_csvdict(PROPS):
		print i
	# assert len(PROPS) == len(UNITS)