import numpy
from __init__ import Q_,ureg
from laminate import Laminate
from sim import Sim
from readcsv import units_dict

def max_stress_R(input_stress,properties):
	R = {}
	on_stress = numpy.vstack(input_stress)
	xt = numpy.vectorize(lambda x: properties['xt']/x if x>0 else 0.1)
	xc = numpy.vectorize(lambda x: numpy.abs(properties['xc']/x) if x<0 else 0.1)
	yt = numpy.vectorize(lambda x: properties['yt']/x if x>0 else 0.1)
	yc = numpy.vectorize(lambda x: numpy.abs(properties['yc']/x) if x<0 else 0.1)
	s  = numpy.vectorize(lambda x: numpy.abs(properties['sc']/x))
	xt(numpy.array([1,-1,50,10]))
	print on_stress[:,0]
	print properties['xt']
	R['FT'] = xt(on_stress[:,0]) 
	R['FC'] = xc(on_stress[:,0]) 
	R['MT'] = yt(on_stress[:,1])
	R['MC'] = yc(on_stress[:,1]) 
	R['S'] = s(on_stress[:,2])

	return R

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
		self.strength = {i:PROPS[i]/1000.0 for i in required} #Strength in MPa
		# self.strength = {i:PROPS[i] for i in required}
		self.sim = input_sim

	def compute_max_stress(self):
		print max_stress_R(self.stress,self.strength)

if __name__ == '__main__':
	from sim import make_test_sim

	sim = make_test_sim()
	fail = FailureAnalysis(sim)
	print fail.stress
	print fail.compute_max_stress()


