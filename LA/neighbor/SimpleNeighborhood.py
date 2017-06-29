import instance.instance as inst
import sys
import pickle
import twhelper as tw
import routehelper as rh
import random
from numpy.random import choice
import math

class SimpleNeighborhood(object):

    def __init__(self):
        self.operators = [self.relocation, self.crossover, self.exchange, self.orExchange, self.twoExchange, self.chargerSwap]
        #self.weights = [0.35,0.15,0.1,0.25,0.1,0.05] #3
        #self.weights = [0.3,0.15,0.15,0.2,0.15,0.05] #2
        self.relocationP = 0.25#0.4
        self.crossoverP = 0.15#0.05
        self.exchangeP = 0.15#0.15
        self.orExchangeP = 0.2#0.27
        self.twoExchangeP = 0.15#0.1
        self.chargerSwapP = 0.1#0.05#0.08
        self.weights = [self.relocationP, self.crossoverP, self.exchangeP, self.orExchangeP, self.twoExchangeP, self.chargerSwapP]

    def set_params(self, relocationP, crossoverP, exchangeP, orExchangeP, twoExchangeP, chargerSwapP):
        if sum([relocationP, crossoverP, exchangeP, orExchangeP, twoExchangeP, chargerSwapP]) != 1: return False 
        self.weights = [relocationP, crossoverP, exchangeP, orExchangeP, twoExchangeP, chargerSwapP]
        return True
        

    def generate_neighbor(self, routes, cost):        
        cost -= self.removeRoutesWithoutCustomers(routes) #This is unecessarily expensive
        chosenRouteIndexes = random.sample(range(0, len(routes)), 2)        
        chosenRoutes = [self._cp(routes[chosenRouteIndexes[0]]), self._cp(routes[chosenRouteIndexes[1]])]
        initialCost = chosenRoutes[0].getCost() + chosenRoutes[1].getCost() # previous cost of the two routes
        newCost = choice(self.operators,p=self.weights)(chosenRoutes, initialCost)

        newTotalCost = cost - initialCost + newCost
        return {"chosenRoutesIndexes": chosenRouteIndexes, "chosenRoutes": chosenRoutes, "newTotalCost": newTotalCost }

    def twoExchange(self, chosenRoutes, initialCost):
        for i in self.randomly(range(1, len(chosenRoutes[0].nodes)-2)):
            for j in self.randomly(range(i+1, len(chosenRoutes[0].nodes)-1)):
                success = self.doTwoExchange(chosenRoutes, i,j)
                if success: return chosenRoutes[0].getCost() + chosenRoutes[1].getCost() 
        return initialCost
    
    def doTwoExchange(self, chosenRoutes, i, j):
        if chosenRoutes[0].nodes[i].id.startswith('S') or chosenRoutes[0].nodes[j].id.startswith('S'): return False
        r = chosenRoutes[0].nodes[:i+1] + chosenRoutes[0].nodes[i+1:j+1][::-1] + chosenRoutes[0].nodes[j+1:]
        if chosenRoutes[0].nodes == r or not tw.feasible(r): return False
        chosenRoutes[0].nodes[:] = r[:]
        chosenRoutes[0].distance = rh.cost(chosenRoutes[0])
        return True

    def exchange(self, chosenRoutes, initialCost):
        randomizedR1 = self.randomly(range(1, len(chosenRoutes[1].nodes)-1))
        for i in self.randomly(range(1, len(chosenRoutes[0].nodes)-1)):
            for j in randomizedR1:
                success = self.doExchange(chosenRoutes, i,j)
                if success: return chosenRoutes[0].getCost() + chosenRoutes[1].getCost()
        return initialCost
        
    def doExchange(self, chosenRoutes, i, j):
        if self._is_charger(chosenRoutes, i, j): return False #Check if charger, and if it can be removed
        r1 = chosenRoutes[0].nodes[:i] + [chosenRoutes[1].nodes[j]] + chosenRoutes[0].nodes[i+1:]
        r2 = chosenRoutes[1].nodes[:j] + [chosenRoutes[0].nodes[i]] + chosenRoutes[1].nodes[j+1:]
        if tw.feasible(r1) and tw.feasible(r2):
            tmp = chosenRoutes[0].nodes[i]
            chosenRoutes[0].assign(i, chosenRoutes[1].nodes[j])
            chosenRoutes[1].assign(j, tmp)
            return True
        return False

    def orExchange(self, chosenRoutes, initialCost):
        l = len(chosenRoutes[0].nodes)
        randomizedR1 = self.randomly(range(1, len(chosenRoutes[1].nodes)-1)) 
        seqlen = random.randint(1,min(2, l-2))
        for i in self.randomly(range(1, l-seqlen)):
            for j in randomizedR1:
                success = self.doOrExchange(chosenRoutes, i,j, seqlen)
                if success:
                    return chosenRoutes[0].getCost() + chosenRoutes[1].getCost() 
        return initialCost
    
    def doOrExchange(self, chosenRoutes, i, j, seqlen):
        r1 = chosenRoutes[0].nodes[:i] + chosenRoutes[0].nodes[i+seqlen:] #might have to do -1 on seqlen here
        r2 = chosenRoutes[1].nodes[:j] + chosenRoutes[0].nodes[i:i+seqlen] + chosenRoutes[1].nodes[j:]
        f1 = tw.feasible(r1)
        f2 = tw.feasible(r2)
        if not f1: r1.insert(i, rh.minCostCharger(r1[i-1], r1[i]))
        rng = random.randint(0,1)
        if not f2: r2.insert(j, rh.minCostCharger(r2[j-1 + seqlen * rng], r2[j + seqlen * rng]))
                
        if tw.feasible(r2) and tw.feasible(r1):
            for l in range(seqlen):
                chosenRoutes[1].insert_at(j+l,chosenRoutes[0].nodes[i])
                chosenRoutes[0].remove_at(i)
            if not f1: chosenRoutes[0].insert_at(i, rh.minCostCharger(r1[i-1],r1[i]))
            if not f2: chosenRoutes[1].insert_at(j, rh.minCostCharger(r2[j-1 + seqlen * rng],r2[j + seqlen*rng]))
            return True
        return False

    def crossover(self, chosenRoutes, initialCost):
        randomizedR1 = self.randomly(range(1, len(chosenRoutes[1].nodes) - 2))
        for i in self.randomly(range(1, len(chosenRoutes[0].nodes) - 2)):
            for j in randomizedR1:
                success = self.doCrossover(chosenRoutes, i, j)
                if success: return chosenRoutes[0].getCost() + chosenRoutes[1].getCost()
        return initialCost

    def doCrossover(self, chosenRoutes, i, j):
        # don't exchange anything with a charger
        if self._is_charger(chosenRoutes, i, j): return False
        r1 = chosenRoutes[0].nodes[:i+1] + chosenRoutes[1].nodes[j+1:]
        r2 = chosenRoutes[1].nodes[:j+1] + chosenRoutes[0].nodes[i+1:]
        if tw.feasible(r1) and tw.feasible(r2):
            tmp = chosenRoutes[0].nodes[i+1:] # keep a buffer for replacing
            chosenRoutes[0].nodes[i+1:] = chosenRoutes[1].nodes[j+1:]
            chosenRoutes[1].nodes[j+1:] = tmp # replace with buffer
            chosenRoutes[0].distance = rh.cost(chosenRoutes[0])
            chosenRoutes[1].distance = rh.cost(chosenRoutes[1])
        return True

    def relocation(self, chosenRoutes, initialCost):
        randomizedR1 = self.randomly(range(1, len(chosenRoutes[1].nodes)-1))
        for i in self.randomly(range(1, len(chosenRoutes[0].nodes)-1)): # indexes ignore the depot
            for j in randomizedR1:
                success = self.doRelocation(chosenRoutes, i, j)
                if success: return chosenRoutes[0].getCost() + chosenRoutes[1].getCost()
        return initialCost

    def doRelocation(self, chosenRoutes, i, j):
        r1 = chosenRoutes[0].nodes[:i] + chosenRoutes[0].nodes[i+1:] 
        r2 = chosenRoutes[1].nodes[:j] + [chosenRoutes[0].nodes[i]] +  chosenRoutes[1].nodes[j:] 
        if tw.feasible(r1) and tw.feasible(r2):
            if not chosenRoutes[0].nodes[i].id.startswith("S"):
                chosenRoutes[1].insert_at(j, chosenRoutes[0].nodes[i])
            chosenRoutes[0].remove_at(i)
            return True
        return False
    
    def chargerSwap(self, chosenRoutes, initialCost):
        try: i = next(i for i in range(1,len(chosenRoutes[0].nodes)-1) if chosenRoutes[0].nodes[i].id.startswith("S"))
        except StopIteration: return initialCost
        success = self.doChargerSwap(chosenRoutes[0], i)
        if success: return chosenRoutes[0].getCost() + chosenRoutes[1].getCost()
        return initialCost
    
    def doChargerSwap(self, chosenRoute, i):
        rw = chosenRoute.nodes[:i] + chosenRoute.nodes[i+1:]
        minCost = sys.maxsize
        minInd = None
        minCharger = None
        for j in range(1,len(rw)):
            chargerTuple = rh.chargerCostTuple(rw[j-1], rw[j])
            if tw.feasible(rw[:j] + [chargerTuple[0]] + rw[j:]) and chargerTuple[1] < minCost:
                minCharger = chargerTuple[0]
                minCost = chargerTuple[1]
                minInd = j
        if minInd:
            chosenRoute.remove_at(i)
            chosenRoute.insert_at(minInd, minCharger)
            return True
        return False
    
    def randomly(self, sequence):
        shuffled = list(sequence)
        random.shuffle(shuffled)
        return iter(shuffled)

    def removeRoutesWithoutCustomers(self, routes):
        costReduction = 0
        for i in reversed(range(len(routes))):
            if not routes[i].hasCustomer():
                costReduction += routes[i].getCost()
                del routes[i]
        return costReduction

    def _is_charger(self, chosenRoutes, i, j):
        return chosenRoutes[0].nodes[i].id.startswith("S") or chosenRoutes[1].nodes[j].id.startswith("S")
    
    def _cp(self, o):
        return pickle.loads(pickle.dumps(o,-1))

