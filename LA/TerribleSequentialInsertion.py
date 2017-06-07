import sys
import os
import subprocess
import argparse
import logging
import math
from route import Route
import instance.instance as inst 
import routehelper as rh
import copy

import twhelper as tw

logging.basicConfig(level=logging.ERROR)                                                                       
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
        infeasibleCustomers = []
        for customer in self.customers:
            if not route.feasibleInsertion(customer):
                infeasibleCustomers.append(customer)
        if len(route.nodes) > 1 and not rh.depotReachable(route, route.last()):
            route.insertCharger(rh.closestCharger(route.last()))
        
            #for tryAgainCustomer in infeasibleCustomers:
             #   chargerRoute.feasibleInsertion(tryAgainCustomer, False)
            #if not rh.depotReachable(route, route.last()) or len(route.nodes) + 1 < len(chargerRoute.nodes):
             #   route = chargerRoute
        
        if len(route.nodes) == 1: #Empty route
            for c in infeasibleCustomers:
                route.insertCharger(rh.closestChargerBetweenTwoNodes(inst.depot, c))
                print("Inserted charger %s for customer %s" % (rh.closestChargerBetweenTwoNodes(inst.depot, c).id,customer.id))
                if route.feasibleInsertion(c): 
                    print("Inserted the bastard %s" % c.id) 
                    if not rh.depotReachable(route, c):
                        print("Can't reach depot tho")
                    route.insertCharger(rh.closestChargerBetweenTwoNodes(inst.depot, c))
                    break
                else: print("Couldn't insert %s" % c.id)
        route.insert(self.depot)
        self.cost += route.getCost()
        return route
        
    def solve(self):
        while(len(self.customers)>0):
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
    parser.add_argument('--all', '-a', action = 'store_true', help='Runs the algorithms on all instances')

    args = parser.parse_args()
    instanceFiles = [args.instance]
    if args.all:
        instanceFiles = os.listdir('../data/instances/')
        

    for instanceFile in instanceFiles:
        if not instanceFile.endswith('.txt'): continue
        inst.setFileName(instanceFile)
        inst.parse()
        sol = Solution()
        sol.sortCustomersByAngle()
        sol.solve()
        print(sol.cost)
        #if not args.verify: print(sol)

        if args.verify:
            tempFile = './solutions/'+ instanceFile + '.sol'
            with open(tempFile, mode='w') as f:
                f.write(str(sol))
            subprocess.call(['time', 'java', '-jar', '../data/verifier/EVRPTWVerifier.jar', '-d', inst.filename, tempFile])
            #os.remove(tempFile)
        inst.reset_data()
