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
        return self.distance

    def assign(self, i, node):
        old = self.nodes[i]
        self.nodes[i] = node
        self.distance += rh._d(self.nodes[i-1],node) + rh._d(node, self.nodes[i+1]) - (rh._d(self.nodes[i-1],old) + rh._d(old, self.nodes[i+1])) 

    def insert_at(self, i, node):
        self.distance += - rh._d(self.nodes[i-1], self.nodes[i]) + rh._d(self.nodes[i-1], node) + rh._d(node, self.nodes[i])                                                               
        self.nodes.insert(i, node)

    def remove_at(self, i):
        self.distance += rh._d(self.nodes[i-1], self.nodes[i+1]) - rh._d(self.nodes[i-1], self.nodes[i]) - rh._d(self.nodes[i], self.nodes[i+1])                                                               
        del self.nodes[i]
    
    def insert(self, customer):
        dist = inst._distanceMatrix[(self.nodes[-1].id, customer.id)]
        self.distance += dist
        self.battery = self.battery - (dist*inst.fuelConsumptionRate)
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

    def hasNoCustomers(self):
        return len(self.nodes) == 2 

    def hasCustomer(self):
        return any(n.id.startswith('C') for n in self.nodes)
    
    def clear(self):
        self.nodes.clear()
        self.nodes.append(self.depot)
        self.battery = inst.fuelCapacity
        self.capacity = inst.loadCapacity
        self.distance = 0.

    def __str__(self):
        return str([node.id for node in self.nodes])

