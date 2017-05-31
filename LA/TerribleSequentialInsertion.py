import sys
import os
import subprocess
import argparse
import logging
import math
from route import Route
import instance.instance as inst 

logging.basicConfig(level=logging.INFO)                                                                       
logger = logging.getLogger(__name__) 

class Solution(object):
    def __init__(self):
        self.routes = [] #routes is a Python list of Route objects [Route, Route, ...]
        self.cost = 0.
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

    def createRoute(self):
        route = Route(self.depot)
        for customer in self.customers:
            route.feasibleInsertion(customer)
        route.insert(self.depot) #Route must end at the depot
        self.cost += route.getCost()
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
        routeStr = str.join('\n', [str.join(', ',[str(customer) for customer in route.nodes]) for route in self.routes])
        return '#solution for %s\n%.3f\n%s' % (inst.filename, self.cost, routeStr)

        

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Runs simple Sequential Heuristic on instance file')
    parser.add_argument('--instance', '-i', metavar='INSTANCE_FILE', required=True, help='The instance file')
    parser.add_argument('--verify', '-v', action = 'store_true', help='Uses the EVRPTWVerifier to verify the solution')
    args = parser.parse_args()
    inst.setFileName(args.instance)
    inst.parse()
    sol = Solution()
    sol.sortCustomersByAngle()
    sol.solve()
    print(sol)

    if args.verify:
        tempFile = inst.filename + '.sol'
        with open(tempFile, mode='w') as f:
            f.write(str(sol))
        subprocess.call(['java', '-jar', '../data/verifier/EVRPTWVerifier.jar', inst.filename, tempFile])
        os.remove(tempFile)
