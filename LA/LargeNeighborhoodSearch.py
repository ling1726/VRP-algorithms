import instance.instance as inst
import sys
import pickle
import random
import math
import route as rt
import twhelper as tw
import routehelper as rh
import SimulatedAnnealing as sa
from time import time

class LargeNeighborhoodSearch(object):

    def __init__(self, routes, cost):
        self.routes = routes
        self.cost = cost

    def solve(self):
        best = (self._cp(self.routes), self.cost)
        current = (self._cp(self.routes), self.cost)
        noImprovement = 0
        startTime = time()
        diversify = False
        diversificationNeeded = 1
        for counter in range(sys.maxsize):
            currentTime = time()
            if currentTime - startTime > 90:
                print("Timeout")
                break
            if noImprovement > 3:
                print("Local minima")
                break

            nxt = self.anneal(current)
            print("Best: %.2f Current: %.2f Next: %.2f" % (best[1], current[1], nxt[1]) )
            
            if self.accept(nxt, current): 
                current = nxt
                noImprovement = 0
            else: noImprovement += 1
            if nxt[1] < best[1]: best = self._cp(nxt)

            if noImprovement > diversificationNeeded:
                noImprovement = 0
                diversificationNeeded +=1
                print("Diversification step...")
                current = self.rebuild(nxt)
                current = self.rebuildWithChargers(current)
            else: diversify = False
        print("%d seconds..." % (currentTime-startTime))    
        self.routes = best[0]
        self.cost = best[1]
        
    #Add min chargers en route
    def rebuild(self, sol):
        splitCount = random.randint(1, len(sol[0])//2)
        for route in self.randomly(sol[0]):
            if len(route.nodes) < 4: continue
            splitIndex = len(route.nodes)//2
            for i in range(splitIndex, 0, -1):
                firstPart = route.nodes[:i+1] + [inst.depot]
                secondPart = [inst.depot] + route.nodes[i+1:]
                if tw.feasible(firstPart) and tw.feasible(secondPart):
                    firstRoute = rt.Route(inst.depot)
                    for n in firstPart[1:]: firstRoute.insert(n)
                    secondRoute = rt.Route(inst.depot)
                    for n in secondPart[1:]: secondRoute.insert(n)
                    sol[0].remove(route)
                    sol[0].append(firstRoute)
                    sol[0].append(secondRoute)
                    sol = (sol[0], sol[1] - route.getCost() + firstRoute.getCost() + secondRoute.getCost()) 
                    splitCount -= 1
                    break
            if not splitCount: break
        return sol
    
    def rebuildWithChargers(self, sol):
        counter = random.randint(1, len(sol[0])//2)
        for route in self.randomly(sol[0]):
            if len(route.nodes) < 4: continue
            cost = self.doMinChargerInsert(route)
            sol = (sol[0], sol[1] + cost)
            if cost > 0: counter -=1
        return sol
    
    
    def doMinChargerInsert(self, chosenRoute):                                                 
        minCost = sys.maxsize                                                                  
        minInd = None                                                                          
        minCharger = None                                                                      
        r = chosenRoute.nodes
        cost = 0
        for j in range(1,len(r)):                                                              
            if r[j-1].id.startswith("S") or r[j].id.startswith("S"): continue                  
            chargerTuple = rh.chargerCostTuple(r[j-1], r[j])                                   
            detourCost = chargerTuple[1] - tw.batterySpent(r[j-1], r[j])
            if detourCost < inst.fuelCapacity * 0.05 and tw.feasible(r[:j] + [chargerTuple[0]] + r[j:]):#chargerTuple[1] < minCost:   
                initialCost = chosenRoute.getCost()
                chosenRoute.insert_at(j, chargerTuple[0])
                cost += chosenRoute.getCost() - initialCost
                r = chosenRoute.nodes                                                                    
        return cost

    def anneal(self, current):
        SA = sa.SimulatedAnnealing(self._cp(current[0]), current[1])
        SA.solve()
        return (SA.routes, SA.cost)

    def accept(self, nxt, current):
        return nxt[1] < current[1]
    
    def randomly(self, sequence):
        shuffled = list(sequence)
        random.shuffle(shuffled)
        return iter(shuffled)

    def _cp(self, o):
        return pickle.loads(pickle.dumps(o,-1))   
