#TODO : Implement z_core

from parsetools import parse_layup, parse_request
import layer
do_display = True

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
		do_debug = False
		if method is 'dumb':
			for layer in self.layers:
				layer.compute_all()

		elif method is 'smart':
			if self.symmetric:
				length = len(self.layers)/2
			else:
				length = len(self.layers)

			for i in range(length):
				if i == 0:
					self.layers[i].compute_all()
					on_changes = {'Q_on':self.layers[0].Q_on,
												'S_on':self.layers[0].S_on
												}
					off_changes = {'Q_off':self.layers[0].Q_off,
												'S_off':self.layers[0].S_off
												}

				else:
					self.layers[i].set(on_changes)
					modified = self.layers[i].compute_all()
					assert (len(modified) == 2)

					if do_debug:
						print modified

					off_changes = {modified[0]:getattr(self.layers[i],modified[0]),
												modified[1]:getattr(self.layers[i],modified[1])
												}

				if self.symmetric:
					off_changes.update(on_changes)
					opposite_layer = self.layers[-i-1]
					opposite_layer.set(off_changes)

			#End of symmetry loop

		else:
			raise AssertionError("Method %s is not defined" % method)

	def print_param(self, display = do_display):
		return_string = self.layers[0].print_param(display)

		if display:
			print "Asked for display inside laminate.print_param"
			print return_string

		return return_string

	def print_orientation(self, display = do_display):
		str_layup_1 = "%s" % self.layup
		title = "Orientation [degrees] : \n"

		return_string = title + str_layup_1
		
		if display:
			print "Asked for display inside print_orientation"
			print return_string

		return return_string

	def print_array(self,names, num_of_layers = 'all', display = do_display):
		return_string = ''
		if num_of_layers == 'all':
			length = len(self.layers)
		else:
			length = int(num_of_layers)

		if length == 1:
			separator = ''
		else:
			separator = '--' * 20 + '\n'

		counter = 1
		for layer in self.layers[:length]:
				return_string += separator
				return_string += "Layer number : %d" % counter + '\n'
				return_string += "Orientation  : %d [degrees]" % layer.theta + '\n'
				return_string += layer.print_array(names, display)
				return_string += '\n'
				counter += 1

		if display:
			print "Asked for display inside laminate.print_array"
			print return_string

		return return_string

if __name__ == "__main__":
	import time
	start = time.clock()
	my_dumb = Laminate('90_2/p40/p20/0s',2)
	my_dumb.compute_all(method='dumb')
	dumbtime = time.clock() - start

	start = time.clock()
	my_smart = Laminate('90_2/p40/p20/0s',2)
	my_smart.compute_all(method='smart')
	smarttime = time.clock() - start

	print dumbtime
	print smarttime
	print smarttime/dumbtime


						