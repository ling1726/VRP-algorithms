import instance.instance as inst
from helper import twhelper as tw
from helper import routehelper as rh
import logging

logging.basicConfig(level=logging.ERROR)                                                                                 
logger = logging.getLogger(__name__) 

class Route(object):

    def __init__(self, depot):
        self.depot = depot
        self.nodes = [depot]
        self.battery = inst.fuelCapacity
        self.capacity = inst.loadCapacity
        self.distance = 0.
        self.chargers = list(inst.chargers.values())

    def translateByDepot(self, depot):
        for charger in self.chargers:
            charger.translateByDepot(depot)
    
    
    def feasibleInsertion(self, customer, relaxedInsertion = True):
        if not self.feasible(customer): return False

        #Customer cannot reach the depot AND cannot reach a charging station -> no way the route can be feasible
        #relaxedInsertion being False "turns off" the chargability check, meaning the customer must be able to reach the depot
        if not rh.depotReachable(self, customer) and not (relaxedInsertion and rh.chargable(self, rh.closestCharger(customer), customer)): return False
        self.insert(customer)
        return True

    def feasible(self, node):
        futureBattery = self.battery - (inst._distanceMatrix[(self.nodes[-1].id, node.id)]*inst.fuelConsumptionRate)
        futureCapacity = self.capacity - node.demand
        if futureBattery < 0 or futureCapacity < 0 or not tw.feasible(self.nodes + [node]): return False
        return True

    def getCost(self):
        return rh.cost(self)

    def insert(self, customer):
        self.distance += inst._distanceMatrix[(self.nodes[-1].id, customer.id)]
        self.battery = self.battery - (inst._distanceMatrix[(self.nodes[-1].id, customer.id)]*inst.fuelConsumptionRate)
        self.capacity = self.capacity - customer.demand
        self.nodes.append(customer)

    def insertCharger(self, charger):
        if not self.feasible(charger): logger.error("Error inserting charger %s. Not feasible." % charger.id)
        self.insert(charger)
        self.battery = inst.fuelCapacity

    def last(self):
        return self.nodes[-1]

    def empty(self):
        return len(self.nodes) <= 1

    def __str__(self):
        return str([node.id for node in self.nodes])

