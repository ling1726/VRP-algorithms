import instance.instance as inst
import copy
import twhelper as tw
import random

class SimpleNeighborhood(object):

    def __init__(self):
        pass
    # current should be a route object, so we can handle costs and so on
    def generate_neighbor(self, routes, cost):
        chosenRouteIndexes = random.sample(range(0, len(routes)), 2)
        # the routes on which we apply the operator
        chosenRoutes = [copy.deepcopy(routes[chosenRouteIndexes[0]]), copy.deepcopy(routes[chosenRouteIndexes[1]])]
        initialCost = chosenRoutes[0].getCost() + chosenRoutes[1].getCost() # previous cost of the two routes

        # TODO use a random number generator to pick neighbourhoods
        neighbourhood = random.randint(0, 5)
        # for now there is only one neighbourhood implemented
        newCost = self.relocation(chosenRoutes, initialCost)

        newTotalCost = cost - initialCost + newCost

        return {"chosenRoutesIndexes": chosenRouteIndexes, "chosenRoutes": chosenRoutes, "newTotalCost": newTotalCost }

    def twoExchange(self, chosenRoutes, initialCost): pass

    def crossover(self, chosenRoutes, initialCost): pass

    def exchange(self, chosenRoutes, initialCost): pass

    def orExchange(self, chosenRoutes, initialCost): pass

    def relocation(self, chosenRoutes, initialCost):
        if chosenRoutes[0].hasNoCustomers() or chosenRoutes[1].hasNoCustomers(): return initialCost
        initialRoutes = copy.deepcopy(chosenRoutes)
        for i in range(1, len(chosenRoutes[0].nodes)-1): # indexes ignore the depot
            for j in range(1, len(chosenRoutes[1].nodes)-1):
                # do not exchange anything for a charger
                success = self.doRelocation(chosenRoutes, i, j)

                # check for cost and feasibility
                newCost = chosenRoutes[0].getCost() + chosenRoutes[1].getCost()
                feasible = tw.feasible(chosenRoutes[0].nodes) and tw.feasible(chosenRoutes[1].nodes)
                if feasible and success:
                    print("XXXXXXXXXXXXXXX")
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

    def rollbackMove(self, chosenRoutes, initialRoutes):
        chosenRoutes[0].clear()
        chosenRoutes[1].clear()
        for i in range(1, len(initialRoutes[0].nodes)):
            chosenRoutes[0].insert(initialRoutes[0].nodes[i])
        for i in range(1, len(initialRoutes[1].nodes)):
            chosenRoutes[1].insert(initialRoutes[1].nodes[i])