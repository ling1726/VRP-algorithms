import instance.instance as inst
import sys
import pickle
import twhelper as tw
import routehelper as rh
import random
from numpy.random import choice

class SimpleNeighborhood(object):

    def __init__(self):
        pass

    def generate_neighbor(self, routes, cost):        
        cost -= self.removeRoutesWithoutCustomers(routes) #This is unecessarily expensive
        chosenRouteIndexes = random.sample(range(0, len(routes)), 2)        
        chosenRoutes = [self._cp(routes[chosenRouteIndexes[0]]), self._cp(routes[chosenRouteIndexes[1]])]
        initialCost = chosenRoutes[0].getCost() + chosenRoutes[1].getCost() # previous cost of the two routes
        #newCost = choice([self.relocation, self.crossover, self.exchange, self.orExchange, self.twoExchange],p=[0.5,0.15,0.1,0.15,0.1])(chosenRoutes, initialCost)
        newCost = choice([self.relocation, self.crossover, self.exchange, self.orExchange, self.twoExchange, self.chargerSwap],p=[0.35,0.15,0.1,0.25,0.1,0.05])(chosenRoutes, initialCost)
        newTotalCost = cost - initialCost + newCost
        return {"chosenRoutesIndexes": chosenRouteIndexes, "chosenRoutes": chosenRoutes, "newTotalCost": newTotalCost }

    def twoExchange(self, chosenRoutes, initialCost):
        for i in range(1, len(chosenRoutes[0].nodes)-2):#for i in self.randomly(range(1, len(chosenRoutes[0].nodes)-2)):
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
        if self._is_charger(chosenRoutes, i, j): return False
        r1 = chosenRoutes[0].nodes[:i] + [chosenRoutes[1].nodes[j]] + chosenRoutes[0].nodes[i+1:]
        r2 = chosenRoutes[1].nodes[:j] + [chosenRoutes[0].nodes[i]] + chosenRoutes[1].nodes[j+1:]
        if tw.feasible(r1) and tw.feasible(r2):
            tmp = chosenRoutes[0].nodes[i]
            chosenRoutes[0].assign(i, chosenRoutes[1].nodes[j])
            chosenRoutes[1].assign(j, tmp)
            return True
        return False
    
    def orExchange(self, chosenRoutes, initialCost):
        randomizedR1 = self.randomly(range(1, len(chosenRoutes[1].nodes)-1)) 
        seqlen = random.randint(1,3)
        for i in self.randomly(range(1, len(chosenRoutes[0].nodes)-seqlen)):
            for j in randomizedR1:
                success = self.doOrExchange(chosenRoutes, i,j, seqlen)
                if success:
                    return chosenRoutes[0].getCost() + chosenRoutes[1].getCost()
        return initialCost
    
    def doOrExchange(self, chosenRoutes, i, j, seqlen):
        r1 = chosenRoutes[0].nodes[:i] + chosenRoutes[0].nodes[i+seqlen:] #might have to do -1 on seqlen here
        r2 = chosenRoutes[1].nodes[:j] + chosenRoutes[0].nodes[i:i+seqlen] + chosenRoutes[1].nodes[j:]
        if self._is_charger(chosenRoutes, i, j): return False
        f1 = tw.feasible(r1)
        f2 = tw.feasible(r2)
        if not f1: r1.insert(i, rh.minCostCharger(r1[i-1], r1[i]))
        if not f2: r2.insert(j, rh.minCostCharger(r2[j-1], r2[j]))
                
        if tw.feasible(r2) and tw.feasible(r1):
            for l in range(seqlen):
                chosenRoutes[1].insert_at(j+l,chosenRoutes[0].nodes[i])
                chosenRoutes[0].remove_at(i)
            if not f1: chosenRoutes[0].insert_at(i, rh.minCostCharger(r1[i-1],r1[i]))
            if not f2: chosenRoutes[1].insert_at(j, rh.minCostCharger(r2[j-1],r2[j]))
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
        for i in range(1,len(chosenRoutes[0].nodes)-1):
            if chosenRoutes[0].nodes[i].id.startswith("S"):
                success = self.doChargerSwap(chosenRoutes, i)
                if success: return chosenRoutes[0].getCost() + chosenRoutes[1].getCost()
        return initialCost
    
    def doChargerSwap(self, chosenRoutes, i):
        nodes = chosenRoutes[0].nodes
        charger = nodes[i]
        currentCost = rh.chargerCostTuple(nodes[i-1],nodes[i+1])[1]
        rw = nodes[:i] + nodes[i+1:]
        options = []
        if i > 1:
            pre = rh.chargerCostTuple(nodes[i-2],nodes[i-1])
            if currentCost > pre[1] and tw.feasible(rw[:i-1] + [pre[0]] + rw[i-1:]):
                options.append((pre[0], pre[1], i-1))
        if i < len(nodes) - 2: 
            post = rh.chargerCostTuple(nodes[i+1],nodes[i+2])
            if currentCost > post[1] and tw.feasible(rw[:i+2] + [post[0]] + rw[i+2:]):
                options.append((post[0], post[1], i+2))
        if options == []: return False
        chosenCharger = min(options, key= lambda x: x[1])
        chosenRoutes[0].remove_at(i)
        chosenRoutes[0].insert_at(chosenCharger[2], chosenCharger[0])
        return True

    """
    def rollbackMove(self, chosenRoutes, initialRoutes):
        chosenRoutes[0].clear()
        chosenRoutes[1].clear()
        for i in range(1, len(initialRoutes[0].nodes)):
            chosenRoutes[0].insert(initialRoutes[0].nodes[i])
        for i in range(1, len(initialRoutes[1].nodes)):
            chosenRoutes[1].insert(initialRoutes[1].nodes[i])
    """
    
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

