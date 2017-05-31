import instance.instance as inst
class Route(object):

    def __init__(self, depot):
        self.depot = depot
        self.nodes = [depot]
        self.battery = inst.fuelCapacity
        self.capacity = inst.loadCapacity
        self.distance = 0.
        self.time = 0.

    def feasibleInsertion(self, customer):
        futureCapacity = self.capacity - customer.demand
        futureBattery = self.battery - (inst._distanceMatrix[(self.nodes[-1].id, customer.id)]*inst.fuelConsumptionRate)
        if futureBattery < 0 or futureCapacity < 0 or not self.timeFeasible(customer) or not self.depotReachable(customer, futureBattery): return False
        self.battery = futureBattery
        self.capacity = futureCapacity
        self.insert(customer)
        return True

    def timeFeasible(self, customer):
        if len(self.nodes) == 1: 
            self.time = max(0, customer.windowStart - inst._distanceMatrix[(self.nodes[-1].id, customer.id)]/inst.averageVelocity) 
        arrivalTime = self.time + inst._distanceMatrix[(self.nodes[-1].id, customer.id)]/inst.averageVelocity
        return customer.windowStart <= arrivalTime and arrivalTime <= customer.windowEnd

    def depotReachable(self, customer, remainingBattery):
        return inst._distanceMatrix[(customer.id, self.depot.id)] <= remainingBattery

    def getCost(self):
        return self.distance * inst.fuelConsumptionRate

    def insert(self, customer):
        self.time += inst._distanceMatrix[(self.nodes[-1].id, customer.id)] / inst.averageVelocity + customer.serviceTime
        self.distance += inst._distanceMatrix[(self.nodes[-1].id, customer.id)]
        self.nodes.append(customer)

