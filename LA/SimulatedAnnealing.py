import sys
import math
import logging
import instance.instance as inst
import Solver as terrible
from neighbor import SimpleNeighborhood as neigh

logger = logging.getLogger(__name__)

class SimulatedAnnealing(object):

    def __init__(self):
        self.neighborhood = neigh.SimpleNeighborhood()

    def solve(self):
        current = self.initial_solution()
        nxt = self.neighbor(current)
        for t in range(sys.maxsize):
            T = self.schedule(t)
            if T == 0: break
            nxt = self.neighbor()
            delta = self.cost(nxt) - self.cost(current)
            if delta > 0 or random.random() < math.exp(delta/T):
                current=nxt
        return nxt

    def initial_solution(self):
        sol = terrible.Solution()
        sol.sortCustomersByAngle()
        return sol.solve()

    def schedule(self, t):
        alpha = 0.95 
        T0 = 10
        return T0 * math.pow(alpha, t)

    def neighbor(self, current):
        return self.neighborhood.generate_neighbor(current)
    
    def cost(self, solution):
        return solution.cost
        
