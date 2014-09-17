#TODO : Implement z_core

import parselayup
import layer

class Laminate(object):
	"""Laminate(layup, materialID) -> Laminate composed of layers
				with various orientations but the same material properties. 
	"""
	def __init__(self, layup, materialID):
		self.layup = parselayup.parse_layup(layup)
		self.layers = [] 
		for orientation in self.layup:
			self.layers.append(layer.Layer(materialID,orientation))

	def print_param(self, ply_number = None, output_file = None, mode = None):
		index = 0
		if ply_number is not None:
			if int(ply_number) >= len(self.layers):
				raise IndexError, """%d is bigger than the number of plies : %d""" % (
								int(ply_number), len(self.layers)) 
			else:
				index = int(ply_number)

		if mode is not None:
			self.layers[index].print_param(file = output_file, mode = mode)
		else:
			self.layers[index].print_param(file = output_file)

	def print_all_param(self, output_file = None):
		for ply in range(0,len(self.layers)):
			self.print_param(ply_number = ply, output_file = output_file, mode = 'a')

	def getQ_on(self):
		old = None
		for layer in self.layers:
			new = layer.getQ_on()
			if old is not None:
				assert (new.all() == old.all())
				old = new
			else:
				old = new

	def get_orientation(self):
		str_layup_1 = "%s" % self.layup
		title = "Orientation [degrees] : \n"
		print title + str_layup_1

		#Assert self.layup against individual orientation of layers in laminate
		#Ensures order is correct.
		list_layup_2 = []
		for layer in self.layers:
			list_layup_2.append(layer.theta)
		str_layup_2 = "%s" % list_layup_2
		assert(str_layup_1 == str_layup_2)



if __name__ == "__main__":
	my_laminate = Laminate('90_2/p40/p20/0s',2)
	# print my_laminate.layup
	# my_laminate.print_param()
	my_laminate.print_all_param('testinput.txt')
	# my_laminate.print_param(5)
	my_laminate.get_orientation()
	my_laminate.getQ_on()


						