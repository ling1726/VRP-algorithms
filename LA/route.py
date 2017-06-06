import instance.instance as inst
import twhelper as tw

class Route(object):

    def __init__(self, depot):
        self.depot = depot
        self.nodes = [depot]
        self.battery = inst.fuelCapacity
        self.capacity = inst.loadCapacity
        self.distance = 0.

    def feasibleInsertion(self, customer):
        if not self.feasible(customer):
            # find closest feasible charger
            success = self.insertClosestFeasibleCharger(customer)
            if not success: return False
        self.insert(customer)
        return True

    def feasible(self, node):
        futureBattery = self.battery - (inst._distanceMatrix[(self.nodes[-1].id, node.id)]*inst.fuelConsumptionRate)
        futureCapacity = self.capacity - node.demand
        if futureBattery < 0 or futureCapacity < 0 or not tw.feasible(self.nodes + [node]): return False
        return True

    def getCost(self):
        return self.distance * inst.fuelConsumptionRate

    def insert(self, customer):
        self.distance += inst._distanceMatrix[(self.nodes[-1].id, customer.id)]
        self.battery = self.battery - (inst._distanceMatrix[(self.nodes[-1].id, customer.id)]*inst.fuelConsumptionRate)
        self.capacity = self.capacity - customer.demand
        self.nodes.append(customer)

    #Inserting first feasible charger not the closest one?
    def insertClosestFeasibleCharger(self, customer):
        success = False
        for charger in inst.chargers.values():
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
