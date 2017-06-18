import sys
import os
import subprocess
import argparse
import logging
import math
import statistics
import graphviz as gv
from copy import deepcopy

import instance.instance as inst
# import SimulatedAnnealing as sa
from route import Route
from helper import routehelper as rh
from helper import twhelper as tw


logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class Construction(object):
    def __init__(self):
        self.routes = [] #routes is a Python list of Route objects [Route, Route, ...]
        self.cost = 0.
        self.distanceMatrix = inst._distanceMatrix
        self.customers = list(deepcopy(inst.customers).values())
        self.chargers = list(deepcopy(inst.chargers).values())[:]
        self.depot = inst.depot

        self. translateByDepot(self.depot)
        self.sortCustomersByAngle()

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

    def construct(self):
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
        return self

    def solve(self):
        return self.construct()


    def __str__(self):
        routeStr = str.join('\n', [str.join(', ',[str(customer) for customer in route.nodes]) for route in self.routes])
        return '#solution for %s\n%.3f\n%s' % (inst.filename, self.cost, routeStr)



