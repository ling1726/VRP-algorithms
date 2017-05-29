import sys
import argparse
import logging
import math
from random import randint
from route import Route
import instance.instance as inst 
#from LA.instance import instance as inst #IF ABOVE DOESNT WORK TRY UNCOMMENTING THIS ONE

_randomPoint = None
logging.basicConfig(level=logging.INFO)                                                                       
logger = logging.getLogger(__name__) 

class Solution(object):
    def __init__(self):
        self.routes = [] #routes is a nested Python list [[Node..][Node..]] of Node objects
        self.Cost = 0.0
        self.distanceMatrix = inst._distanceMatrix
        self.customers = list(inst.customers.values())
        self.chargers = list(inst.chargers.values())
        self.depot = inst.depot
        self. translateByDepot(self.depot)

    def translateByDepot(self, depot):
        for customer in self.customers:
            customer.translateByDepot(depot)

    def sortCustomersByAngle(self):
        for customer in self.customers:
            customer.setAngleFromOrigin()
        self.customers.sort(key=lambda x:x.angle)

    def calculateCost(self):
        for route in routes:
                self.Cost += route.calculateCost()

    def createRoute(self):
        route = Route(self.depot)
        for customer in self.customers:
            route.feasibleInsertion(customer)
        return route        

        

    def solve(self):
        while(len(self.customers)>0):
            print(len(self.customers))
            route = self.createRoute()
            newCustomerList = []
            # create a new list without chosen customers
            for customer in self.customers:
                chosen = False
                for chosenCustomer in route.nodes:
                    if chosenCustomer.id == customer.id: chosen = True
                if not chosen: newCustomerList.append(customer)
            self.customers = newCustomerList[:]
            self.routes.append(route)

    def __str__(self):
        routeStr = str.join('\n', ['['+str.join(',',[str(customer) for customer in route.nodes])+']' for route in self.routes])
        return 'Number of vehicles: %d\nDistance cost: %f\nRoutes:%s' % (len(self.routes), self.Cost, routeStr)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Runs simple Sequential Heuristic on instance file')
    parser.add_argument('--instance', '-i', metavar='INSTANCE_FILE', required=True, help='The instance file')
    args = parser.parse_args()
    inst.setFileName(args.instance)
    inst.parse()
    sol = Solution()
    sol.sortCustomersByAngle()
    sol.solve()
    print(sol)
