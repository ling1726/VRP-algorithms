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
import graphviz as gv
import statistics 

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

        #No more feasible customers in the route. Last customer must charge first
        #before going to a) the depot or b) visiting additional customers
        if not route.empty() and not rh.depotReachable(route, route.last()):
            route.insertCharger(rh.closestCharger(route.last()))
            
            #With the charger added, try to insert previously infeasible customers
            for ic in infeasibleCustomers:
                route.feasibleInsertion(ic, False)

        elif route.empty():#Handle infeasability case
            for c in infeasibleCustomers:
                route.insertCharger(rh.closestChargerBetweenTwoNodes(inst.depot, c))
                if route.feasibleInsertion(c): 
                    route.insertCharger(rh.closestChargerBetweenTwoNodes(inst.depot, c))
                    break

        route.insert(self.depot)
        return route
        
    def solve(self):
        while(len(self.customers)>0):
            route = self.createRoute()
            self.cost += route.getCost()
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



def _visualize_solution(solution):
    g1 = gv.Digraph(format='svg', engine="neato")
    color_step = int(16777215/len(solution.routes)+1)
    color = 0
    for n in inst.nodes.values():
        if n.id.startswith('C'):
            pos = str(n.x/10) + "," + str(n.y/10) + "!"
            g1.node(n.id, shape="box", color="red", fixedsize="true", width=".2", height=".2", fontsize="9", pos=pos)
        elif n.id.startswith('S0'): continue
        else:
            pos = str(n.x/10) + "," + str(n.y/10) + "!"
            g1.node(n.id, color="blue", fixedsize="true", width=".2", height=".2", fontsize="9", pos=pos)
    for r in solution.routes:
        ad_route = []
        ad_route.extend(r.nodes)
        this_color = "#"+'{:06x}'.format(color)
        for i in range(len(ad_route)-1):
            a = ad_route[i].id.split("_")[0]
            b = ad_route[i+1].id.split("_")[0]

            g1.edge(a, b, penwidth=".7", arrowsize=".2", color=this_color)
        color += color_step

    g1.format = 'svg'
    filename = g1.render(filename='img/'+inst.filename.split('/')[3])

        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Runs simple Sequential Heuristic on instance file')
    parser.add_argument('--instance', '-i', metavar='INSTANCE_FILE', required=True, help='The instance file')
    parser.add_argument('--verify', '-v', action = 'store_true', help='Uses the EVRPTWVerifier to verify the solution')
    parser.add_argument('--all', '-a', action = 'store_true', help='Runs the algorithms on all instances')
    parser.add_argument('--novisual', '-z', action = 'store_true', help='Turns off the visualization')
    args = parser.parse_args()
    instanceFiles = [args.instance]
    if args.all:
        instanceFiles = os.listdir('../data/instances/')
        
    stats = []
    for instanceFile in instanceFiles:
        if not instanceFile.endswith('.txt'): continue
        inst.setFileName(instanceFile)
        inst.parse()
        sol = Solution()
        sol.sortCustomersByAngle()
        sol.solve()
        if not args.novisual: visualize_solution(sol)
        print(sol.cost)
        stats.append(sol.cost)
        if not args.verify: print(sol)

        if args.verify:
            tempFile = './solutions/'+ instanceFile + '.sol'
            with open(tempFile, mode='w') as f:
                f.write(str(sol))
            subprocess.call(['java', '-jar', '../data/verifier/EVRPTWVerifier.jar', inst.filename, tempFile])
            #os.remove(tempFile)
        inst.reset_data()
    print("Mean: %.2f Median: %.2f Var: %.2f StdDev: %.2f" % (statistics.mean(stats), statistics.median(stats), statistics.variance(stats), statistics.stdev(stats)))
