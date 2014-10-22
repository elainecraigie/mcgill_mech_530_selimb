import numpy
from __init__ import Q_,ureg
from laminate import Laminate
from sim import Sim
from readcsv import units_dict



class FailureAnalysis(object):
	def __init__(self, input_sim):
		try:
			self.stress = input_sim.get_stress()
		except AttributeError:
			message =  ("Can't obtain stresses from input sim : %r -- type : %s" 
						% (sim,type(sim)))
			raise AttributeError(message)

		except input_sim.WorkflowError:
			raise WorkflowError("Could not get stresses from input sim")

		PROPS = input_sim.laminate.layers[0].PROPS
		required = ['xt','xc','yc','yt','sc']
		self.strength = {i:PROPS[i] for i in required}

	
if __name__ == '__main__':
	from sim import make_test_sim

	sim = make_test_sim()
	fail = FailureAnalysis(sim)

