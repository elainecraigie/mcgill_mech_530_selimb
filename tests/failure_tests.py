from composites.failure import FailureAnalysis
from composites.sim import Sim, ureg, Q_, make_test_sim

def test_init():
	sim = make_test_sim()
	fail = FailureAnalysis(sim)

	