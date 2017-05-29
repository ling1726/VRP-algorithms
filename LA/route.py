import instance.instance as inst
class Route(object):

    def __init__(self, depot):
        self.depot = depot
        self.nodes = [depot]
        self.battery = inst.fuelCapacity
        self.capacity = inst.loadCapacity

    def calculateCost(self):
        for i, point in enumerate(nodes[1:]):
            self.cost += inst._distanceMatrix[(nodes[i].id, point.id)]

    def feasibleInsertion(self, customer):
        futureCapacity = self.capacity - customer.demand
        futureBattery = self.battery - (inst._distanceMatrix[(self.nodes[-1].id, customer.id)]*inst.fuelConsumptionRate)
        if futureBattery < 0 or futureCapacity < 0: return False
        self.battery = futureBattery
        self.capacity = futureCapacity
        self.nodes.append(customer)
        return True

    def insert(self, customer):
        self.nodes.append(customer)
        

