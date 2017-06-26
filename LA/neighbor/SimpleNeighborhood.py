import instance.instance as inst
import sys
import pickle
import twhelper as tw
import routehelper as rh
import random
from numpy.random import choice
import numpy.random
class SimpleNeighborhood(object):

    def __init__(self):
        #random.seed(10)#pass
        #numpy.random.seed(10)
        self.n1 = 0
        self.n2 = 0
        self.n3 = 0
        self.n4 = 0
        self.n5 = 0
        self.tot = 0
        self.overall = 0

    def generate_neighbor(self, routes, cost):        
        cost -= self.removeRoutesWithoutCustomers(routes)
        chosenRouteIndexes = random.sample(range(0, len(routes)), 2)        
        chosenRoutes = [self._cp(routes[chosenRouteIndexes[0]]), self._cp(routes[chosenRouteIndexes[1]])]
        initialCost = chosenRoutes[0].getCost() + chosenRoutes[1].getCost() # previous cost of the two routes
        newCost = choice([self.relocation, self.crossover, self.exchange, self.orExchange, self.twoExchange],p=[0.3,0.15,0.15,0.25,0.15])(chosenRoutes, initialCost)
        newTotalCost = cost - initialCost + newCost
        if newCost == initialCost: self.tot += 1
        self.overall += 1
        return {"chosenRoutesIndexes": chosenRouteIndexes, "chosenRoutes": chosenRoutes, "newTotalCost": newTotalCost }

    def twoExchange(self, chosenRoutes, initialCost): 
        initialRoutes = self._cp(chosenRoutes)
        for i in range(1, len(chosenRoutes[0].nodes)-2):#for i in self.randomly(range(1, len(chosenRoutes[0].nodes)-2)):
            for j in self.randomly(range(i+1, len(chosenRoutes[0].nodes)-1)):
                success = self.doTwoExchange(chosenRoutes, i,j)
                newCost = chosenRoutes[0].getCost() + chosenRoutes[1].getCost()
                feasible = tw.feasible(chosenRoutes[0].nodes) and tw.feasible(chosenRoutes[1].nodes)
                if feasible and success: return newCost
                self.rollbackMove(chosenRoutes, initialRoutes)
        self.n5 += 1
        return initialCost
    
    def doTwoExchange(self, chosenRoutes, i, j):
        if chosenRoutes[0].nodes[i].id.startswith('S') or chosenRoutes[0].nodes[j].id.startswith('S'): return False
        a = chosenRoutes[0].nodes[:i+1] #from start to i
        b = chosenRoutes[0].nodes[i+1:j+1] #from i+1 to j
        c = chosenRoutes[0].nodes[j+1:] #from j+1 to end
        if chosenRoutes[0].nodes == a + b[::-1] + c: return False
        chosenRoutes[0].nodes[:] = a + b[::-1] + c
        chosenRoutes[0].distance = rh.cost(chosenRoutes[0])
        return True

    def exchange(self, chosenRoutes, initialCost):
        initialRoutes = self._cp(chosenRoutes)
        for i in self.randomly(range(1, len(chosenRoutes[0].nodes)-1)):
            for j in self.randomly(range(1, len(chosenRoutes[1].nodes)-1)):
                success = self.doExchange(chosenRoutes, i,j)
                newCost = chosenRoutes[0].getCost() + chosenRoutes[1].getCost()
                feasible = tw.feasible(chosenRoutes[0].nodes) and tw.feasible(chosenRoutes[1].nodes)
                if feasible and success:
                    return newCost
                self.rollbackMove(chosenRoutes, initialRoutes)
        self.n3 += 1
        return initialCost
    
    def doExchange(self, chosenRoutes, i, j):
        if self._is_charger(chosenRoutes, i, j): return False
        tmp = chosenRoutes[0].nodes[i]
        chosenRoutes[0].assign(i, chosenRoutes[1].nodes[j])
        chosenRoutes[1].assign(j, tmp)
        return True
    
    #Todo: Add closest charger between the or exchange to try and make it feasible
    def orExchange(self, chosenRoutes, initialCost):
        initialRoutes = self._cp(chosenRoutes)
        seqlen = random.randint(1,3)
        for i in self.randomly(range(1, len(chosenRoutes[0].nodes)-seqlen)):
            for j in self.randomly(range(1, len(chosenRoutes[1].nodes)-1)):
                success = self.doOrExchange(chosenRoutes, i,j, seqlen)
                #newCost = chosenRoutes[0].getCost() + chosenRoutes[1].getCost()
                #feasible = tw.feasible(chosenRoutes[0].nodes) and tw.feasible(chosenRoutes[1].nodes)
                feasible0 = tw.feasible(chosenRoutes[0].nodes)
                feasible1 = tw.feasible(chosenRoutes[1].nodes)
                if not feasible0:
                    chosenRoutes[0].insert_at(i, rh.closestChargerBetweenTwoNodes(chosenRoutes[0].nodes[i-1], chosenRoutes[0].nodes[i]))
                if not feasible1 and chosenRoutes[0] != chosenRoutes[1]:
                    chosenRoutes[1].insert_at(j, rh.closestChargerBetweenTwoNodes(chosenRoutes[1].nodes[j-1], chosenRoutes[1].nodes[j]))
                feasible = tw.feasible(chosenRoutes[0].nodes) and tw.feasible(chosenRoutes[1].nodes)
                newCost = chosenRoutes[0].getCost() + chosenRoutes[1].getCost()
                if feasible and success:
                    return newCost
                self.rollbackMove(chosenRoutes, initialRoutes)
        self.n4 += 1
        return initialCost
    

    def doOrExchange(self, chosenRoutes, i, j, seqlen):
        if self._is_charger(chosenRoutes, i, j): return False
        for l in range(seqlen):
            chosenRoutes[1].insert_at(j+l,chosenRoutes[0].nodes[i])
            chosenRoutes[0].remove_at(i)
        return True
    
    def crossover(self, chosenRoutes, initialCost):
        initialRoutes = self._cp(chosenRoutes)
        for i in self.randomly(range(1, len(chosenRoutes[0].nodes) - 2)):
            for j in self.randomly(range(1, len(chosenRoutes[1].nodes) - 2)):
                success = self.doCrossover(chosenRoutes, i, j)
                newCost = chosenRoutes[0].getCost() + chosenRoutes[1].getCost()
                feasible = tw.feasible(chosenRoutes[0].nodes) and tw.feasible(chosenRoutes[1].nodes)
                if feasible and success:
                    return newCost # stop if a feasible solution is found
                self.rollbackMove(chosenRoutes, initialRoutes)
        self.n2 += 1
        return initialCost

    def doCrossover(self, chosenRoutes, i, j):
        # don't exchange anything with a charger
        if self._is_charger(chosenRoutes, i, j): return False
        tmp = chosenRoutes[0].nodes[i+1:] # keep a buffer for replacing
        chosenRoutes[0].nodes[i+1:] = chosenRoutes[1].nodes[j+1:]
        chosenRoutes[1].nodes[j+1:] = tmp # replace with buffer
        chosenRoutes[0].distance = rh.cost(chosenRoutes[0])
        chosenRoutes[1].distance = rh.cost(chosenRoutes[1])
        return True

    def relocation(self, chosenRoutes, initialCost):
        initialRoutes = self._cp(chosenRoutes)
        for i in self.randomly(range(1, len(chosenRoutes[0].nodes)-1)): # indexes ignore the depot
            for j in self.randomly(range(1, len(chosenRoutes[1].nodes)-1)):
                # do not exchange anything for a charger
                success = self.doRelocation(chosenRoutes, i, j)
                # check for cost and feasibility
                newCost = chosenRoutes[0].getCost() + chosenRoutes[1].getCost()
                feasible = tw.feasible(chosenRoutes[0].nodes) and tw.feasible(chosenRoutes[1].nodes)
                if feasible and success:
                    return newCost # stop if a feasible solution is found
                self.rollbackMove(chosenRoutes, initialRoutes)
        self.n1 += 1
        return initialCost

    def doRelocation(self, chosenRoutes, i, j):
        if chosenRoutes[0].nodes[i].id.startswith("S"): #Try removing charger 
            chosenRoutes[0].remove_at(i)
            return True
        # insert new node
        chosenRoutes[1].insert_at(j, chosenRoutes[0].nodes[i])
        chosenRoutes[0].remove_at(i)
        return True

    def rollbackMove(self, chosenRoutes, initialRoutes):
        chosenRoutes[0].clear()
        chosenRoutes[1].clear()
        for i in range(1, len(initialRoutes[0].nodes)):
            chosenRoutes[0].insert(initialRoutes[0].nodes[i])
        for i in range(1, len(initialRoutes[1].nodes)):
            chosenRoutes[1].insert(initialRoutes[1].nodes[i])

    #Dont call this every time in the inner loop
    def randomly(self, sequence):
        shuffled = list(sequence)
        random.shuffle(shuffled)
        return iter(shuffled)
        
    #Do this only once at the end?
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

    def __str__(self):
        str_repr = "Relocation: %.2f Crossover: %.2f Exchange: %.2f OrExchange: %.2f TwoExchange: %.2f\n" % (self.n1/self.tot,self.n2/self.tot,self.n3/self.tot,self.n4/self.tot,self.n5/self.tot)
        str_repr += "Total %d\n" % self.tot
        str_repr += "Overall calls %d\n" % self.overall
        return str_repr
