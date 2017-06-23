import instance.instance as inst
import pickle
import twhelper as tw
import random

class SimpleNeighborhood(object):

    def __init__(self):
        pass
    

    # current should be a route object, so we can handle costs and so on
    def generate_neighbor(self, routes, cost):
        chosenRouteIndexes = random.sample(range(0, len(routes)), 2)
        chosenRoutes = [self._cp(routes[chosenRouteIndexes[0]]), self._cp(routes[chosenRouteIndexes[1]])]
        initialCost = chosenRoutes[0].getCost() + chosenRoutes[1].getCost() # previous cost of the two routes

        # What neighbourhood should we pick?
        neighbourhood = random.randint(0, 2)

        newCost = 10000000 # if unmodified the new cost should be so high that it has to be rejected
        if neighbourhood == 0:
            newCost = self.crossover(chosenRoutes, initialCost)
        elif neighbourhood == 1:
            newCost = self.relocation(chosenRoutes, initialCost)

        newTotalCost = cost - initialCost + newCost

        return {"chosenRoutesIndexes": chosenRouteIndexes, "chosenRoutes": chosenRoutes, "newTotalCost": newTotalCost }

    # TODO
    def twoExchange(self, chosenRoutes, initialCost): pass
    # TODO
    def exchange(self, chosenRoutes, initialCost): pass
    # TODO
    def orExchange(self, chosenRoutes, initialCost): pass

    def crossover(self, chosenRoutes, initialCost):
        if chosenRoutes[0].hasNoCustomers() or chosenRoutes[1].hasNoCustomers(): return initialCost
        #initialRoutes = copy.deepcopy(chosenRoutes)
        initialRoutes = self._cp(chosenRoutes)
        for i in range(1, len(chosenRoutes[0].nodes) - 2):
            for j in range(1, len(chosenRoutes[1].nodes) - 2):
                success = self.doCrossover(chosenRoutes, i, j)

                newCost = chosenRoutes[0].getCost() + chosenRoutes[1].getCost()
                feasible = tw.feasible(chosenRoutes[0].nodes) and tw.feasible(chosenRoutes[1].nodes)
                if feasible and success:
                    return newCost # stop if a feasible solution is found
                self.rollbackMove(chosenRoutes, initialRoutes)
        return initialCost

    def doCrossover(self, chosenRoutes, i, j):
        # don't exchange anything with a charger
        if chosenRoutes[0].nodes[i].id.startswith("S") or chosenRoutes[1].nodes[j].id.startswith("S"): return False
        tmp = chosenRoutes[0].nodes[i+1:] # keep a buffer for replacing
        chosenRoutes[0].nodes[i+1:] = chosenRoutes[1].nodes[j+1:]
        chosenRoutes[1].nodes[j+1:] = tmp # replace with buffer
        return True



    def relocation(self, chosenRoutes, initialCost):
        if chosenRoutes[0].hasNoCustomers() or chosenRoutes[1].hasNoCustomers(): return initialCost
        initialRoutes = self._cp(chosenRoutes)
        for i in range(1, len(chosenRoutes[0].nodes)-1): # indexes ignore the depot
            for j in range(1, len(chosenRoutes[1].nodes)-1):
                # do not exchange anything for a charger
                success = self.doRelocation(chosenRoutes, i, j)

                # check for cost and feasibility
                newCost = chosenRoutes[0].getCost() + chosenRoutes[1].getCost()
                feasible = tw.feasible(chosenRoutes[0].nodes) and tw.feasible(chosenRoutes[1].nodes)
                if feasible and success:
                    return newCost # stop if a feasible solution is found
                self.rollbackMove(chosenRoutes, initialRoutes)
        return initialCost

    def doRelocation(self, chosenRoutes, i, j):
        # don't exchange anything with a charger
        if chosenRoutes[0].nodes[i].id.startswith("S") or chosenRoutes[1].nodes[j].id.startswith("S"): return False
        # insert new node
        chosenRoutes[1].nodes.insert(j, chosenRoutes[0].nodes[i])
        #remove old node
        del chosenRoutes[0].nodes[i]
        return True

    def rollbackMove(self, chosenRoutes, initialRoutes):
        chosenRoutes[0].clear()
        chosenRoutes[1].clear()
        for i in range(1, len(initialRoutes[0].nodes)):
            chosenRoutes[0].insert(initialRoutes[0].nodes[i])
        for i in range(1, len(initialRoutes[1].nodes)):
            chosenRoutes[1].insert(initialRoutes[1].nodes[i])

    def _cp(self, o):
        return pickle.loads(pickle.dumps(o,-1))
