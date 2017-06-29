import sys
import math
import logging
import instance.instance as inst
import Solver as terrible
from neighbor import SimpleNeighborhood as neigh
from random import random
import random as rand
from time import time
import numpy as np
logger = logging.getLogger(__name__)

class SimulatedAnnealing(object):

    def __init__(self, routes, cost):
        self.neighborhood = neigh.SimpleNeighborhood()
        self.routes = routes #initial solution
        self.cost = cost # initial solution
        self.maxTries = 5000
        self.T0 = 14
        self.seed = None
        self.paramsError = False
        
    def  solve(self):
        t = 0
        startTime = time()
        for i in range(sys.maxsize):
            currentTime = time()
            T = self.schedule_boltzmann(t)
            if math.isclose(T, 0, abs_tol=0.0001) or i > self.maxTries: break
            newSolution = self.neighborhood.generate_neighbor(self.routes, self.cost)
            delta = newSolution["newTotalCost"] - self.cost
            if delta < 0 or (i < self.maxTries/2 and random() < self.acceptance_probability(delta, T)):
                self.routes[newSolution["chosenRoutesIndexes"][0]] = newSolution["chosenRoutes"][0]
                self.routes[newSolution["chosenRoutesIndexes"][1]] = newSolution["chosenRoutes"][1]
                self.cost = newSolution["newTotalCost"]
            if delta != 0: t += 1
        return ('SAT',currentTime - startTime, i-1, self.cost, self.seed)

    def schedule_boltzmann(self, t):
        return self.T0 / math.log(t+2)

    def acceptance_probability(self, delta, T):
        return math.exp(-delta/math.ceil(T))

    def neighbor(self, current):
        return self.neighborhood.generate_neighbor(current)
    
    def set_seed(self, s):
        self.seed = s
        rand.seed(s)
        np.random.seed(s)

    def set_params(self,relocationP, crossoverP, exchangeP, orExchangeP, twoExchangeP, chargerSwapP, cutoff):
        if not self.neighborhood.set_params(relocationP, crossoverP, exchangeP, orExchangeP, twoExchangeP, chargerSwapP):
            self.paramsError = True
        else: self.paramsError = False
        self.maxTries = cutoff

    def set_cutoff(self, l):
        self.maxTries = l

    def set_temp(self, t):
        self.T0 = t

    def cost(self, solution):
        return solution.cost
        
