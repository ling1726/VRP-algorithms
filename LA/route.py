import instance.instance as inst
import twhelper as tw
import routehelper as rh
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
        if not rh.depotReachable(self, customer) and not rh.chargable(self, rh.closestCharger(customer), customer): return False
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
        logger.info("Inserting %s charger" % charger.id)
        if not self.feasible(charger): logger.error("Error inserting charger %s. Not feasible." % charger.id)
        self.insert(charger)
        self.battery = inst.fuelCapacity
    """
    #Inserting first feasible charger not the closest one?
    def insertClosestFeasibleCharger(self, customer):
        success = False
        for charger in self.chargers:
            if self.nodes[-1].id == charger.id: continue
            if not self.feasible(charger): continue
            currentBattery = self.battery
            currentDistance = self.distance
            currentCapacity = self.capacity
            self.insertCharger(charger)
            if not self.feasible(customer):
                # rollback the charger insert
                self.battery = currentBattery
                self.distance = currentDistance
                self.capacity = currentCapacity
                del self.nodes[-1]
                continue
            else: return True
        return False

    def insertCharger(self, charger):
        futureBattery = self.battery - (inst._distanceMatrix[(self.nodes[-1].id, charger.id)]*inst.fuelConsumptionRate)
        current = self.nodes[-1]
        self.distance += inst._distanceMatrix[(current.id, charger.id)] # add distance
        self.battery = inst.fuelCapacity # refill battery
        self.nodes.append(charger)
    """
    def last(self):
        return self.nodes[-1]

    def __str__(self):
        return str([node.id for node in self.nodes])
    """
    #Currently not used
    def depotReachable(self, customer, remainingBattery):                       
        if customer.id == self.depot.id: return True                            
        depotReachable = inst._distanceMatrix[(customer.id, self.depot.id)]*inst.fuelConsumptionRate <= remainingBattery    
        if depotReachable: return True                                          
        # if we can't reach the depot then try to reach a charging station      
        # charger = self.getClosestFeasibleCharger(self.depot)                  
        # if charger != None: return True                                       
        return False
    """
