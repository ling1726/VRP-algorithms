import sys
import math
import logging
import instance.instance as inst
import Solver as terrible
from neighbor import SimpleNeighborhood as neigh
from random import random

logger = logging.getLogger(__name__)

class SimulatedAnnealing(object):

    def __init__(self, routes, cost):
        self.neighborhood = neigh.SimpleNeighborhood()
        self.routes = routes #initial solution
        self.cost = cost # initial solution
        self.T0 = 10
        self.maxTries = 10000

    def  solve(self):
        for t in range(sys.maxsize):
            T = self.schedule_boltzmann(t)
            if math.isclose(T, 0, abs_tol=0.0001) or t > self.maxTries: break
            newSolution = self.neighborhood.generate_neighbor(self.routes, self.cost)
            delta = newSolution["newTotalCost"] - self.cost
            if delta < 0 or random() < self.acceptance_probability_relaxed(delta, T): # decide if the new solution should be used
                self.routes[newSolution["chosenRoutesIndexes"][0]] = newSolution["chosenRoutes"][0]
                self.routes[newSolution["chosenRoutesIndexes"][1]] = newSolution["chosenRoutes"][1]
                self.cost = newSolution["newTotalCost"]
        return self

    def schedule(self, t):
        alpha = 0.99
        return self.T0 * math.pow(alpha, t)

    def schedule_boltzmann(self, t):
        return self.T0 / math.log(t+2)

    def acceptance_probability(self, delta, T):
        p = 0
        try:p = 1/(1 + math.exp(delta/T))
        except OverflowError: pass
        return p

    def acceptance_probability_relaxed(self, delta, T):
        p = 0
        try: p = math.exp(-delta/T)
        except OverflowError: pass
        return p

    def neighbor(self, current):
        return self.neighborhood.generate_neighbor(current)
    
    def cost(self, solution):
        return solution.cost
        
