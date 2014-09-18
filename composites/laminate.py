#TODO : Implement z_core

from parsetools import parse_layup, parse_request
import layer

class Laminate(object):
	"""Laminate(layup, materialID, compute = <method>) -> Laminate 
composed of layers with various orientations but the same material properties. 

Arguments:
	-layup : layup as a string. See parselayup.py
	-materialID : ID of the wanted material
	-compute = 'dumb' or 'smart'. Smart uses symmetry if possible.
	"""
	def __init__(self, layup, materialID, compute = None):
		self.layup, self.symmetric = parse_layup(layup)
		self.layers = [] 
		for orientation in self.layup:
			new_layer = layer.Layer(materialID,orientation)
			self.layers.append(new_layer)
		if compute is not None:
			self.compute_all()

		self.total_thickness = len(self.layup)*self.layers[0].PROPS['h0']

	def compute_all(self, method = 'dumb'):
		"""method takes 'dumb' or 'smart'
		Dumb method merely calls compute_all() on all layers
		Smart method :
			-Computes Q_on, S_on only once and assigns it all other layers
			-If symmetric, only computes Q_off, S_off for half the layers.
		""" 
		if method is 'dumb':
			for layer in self.layers:
				layer.compute_all()

		elif method is 'smart':
			if self.symmetric:
				length = len(self.layers)/2
			else:
				length = len(self.layers)
			#Compute_all for the first layer

			for layer in self.layers[:length]:
				pass
				
			

		else:
			raise AssertionError("Method %s is not defined" % method)

	def print_param(self):
		self.layers[0].print_param()

	def print_orientation(self):
		str_layup_1 = "%s" % self.layup
		title = "Orientation [degrees] : \n"
		print title + str_layup_1

	def print_array(self,names):
		pass

	# def 

if __name__ == "__main__":
	my_laminate = Laminate('90_2/p40/p20/0s',2)
	# print my_laminate.layup
	# my_laminate.print_param()
	# my_laminate.print_all_param('testinput.txt')
	# # my_laminate.print_param(5)
	# my_laminate.get_orientation()
	# my_laminate.getQ_on()


						