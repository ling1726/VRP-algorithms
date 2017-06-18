import sys
import math
import logging
import instance.instance as inst
import Solver as terrible
from neighbor import SimpleNeighborhood as neigh

logger = logging.getLogger(__name__)

class SimulatedAnnealing(object):

    def __init__(self, routes, cost):
        self.neighborhood = neigh.SimpleNeighborhood()
        self.routes = routes # initial solution
        self.cost = cost # initial solution
    """
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
    """

    def  solve(self):
        for t in range(sys.maxsize):
            T = self.schedule(t)
            if T == 0: break
            newSolution = self.neighborhood.generate_neighbor(self.routes, self.cost)
            if newSolution["newTotalCost"] < self.cost: # decide if the new solution should be used
                self.routes[newSolution["chosenRoutesIndexes"][0]] = newSolution["chosenRoutes"][0]
                self.routes[newSolution["chosenRoutesIndexes"][1]] = newSolution["chosenRoutes"][1]
        return self

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
        
