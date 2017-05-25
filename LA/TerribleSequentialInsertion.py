import sys
import argparse
import logging
import math
from random import randint
import instance.instance as inst 
#from LA.instance import instance as inst #IF ABOVE DOESNT WORK TRY UNCOMMENTING THIS ONE

_randomPoint = None
logging.basicConfig(level=logging.INFO)                                                                       
logger = logging.getLogger(__name__) 

class Solution(object):
    def __init__(self, routes):
        self.Routes = routes #routes is a nested Python list [[Node..][Node..]] of Node objects
        self.NumVehicles = len(routes)
        self.Cost = 0.0
        self.calculateCost(routes)

    def calculateCost(self, routes):
        for route in routes:
            for i, point in enumerate(route[1:]):
                self.Cost += inst.getValDistanceMatrix(route[i], point)

    def __str__(self):
        routeStr = str.join('\n', ['['+str.join(',',[str(customer) for customer in route])+']' for route in self.Routes])
        return 'Number of vehicles: %d\nDistance cost: %f\nRoutes:%s' % (self.NumVehicles, self.Cost, routeStr)


def sequentialInsertion(sortedCustomers):
    """
    TODO: Add predefined number of possible active routes. Once the predefined number is met all
    remaining customers are added to a single last route. That may potentially be infeasible.
    """
    routes = []
    depot = inst.nodes['S0']
    activeRoute = [depot, depot]
    for customer in sortedCustomers:
        index = findBestInsertionPoint(activeRoute, customer)
        if not index: #No feasible insert point found
            routes.append(activeRoute)
            activeRoute = [depot, depot] #New route
            activeRoute.insert(1, customer)
        else:
            activeRoute.insert(index, customer)
    routes.append(activeRoute) #Append last route
    return routes


def findBestInsertionPoint(route, customer):
    if len(route) == 2: #Hackish, but the asymetric dist matrix is messing up the [0,0] active route case.
        return 1
    minInsertCost = sys.maxsize
    minInsertIndex = None
    for insertIndex in range(1, len(route)):
        pred = route[insertIndex-1]
        succ = route[insertIndex]
        insertCost = inst.getValDistanceMatrix(pred, customer) + inst.getValDistanceMatrix(customer, succ) - inst.getValDistanceMatrix(pred, succ) 
        if insertCost < minInsertCost and insertionFeasible(route, insertCost, customer, pred, succ):
            minInsertCost = insertCost
            minInsertIndex = insertIndex
    return minInsertIndex


def insertionFeasible(route, insertCost, customer, pred, succ):
    #check:capacity & check:e_i <= e_c <= e_j & check:battery capacity/distance. Use list comprehension
    #Very inefficient impl
    capacityOK = float(customer.demand) + sum([float(point.demand) for point in route]) < float(inst.loadCapacity)
    timeWindowsOK = float(pred.windowStart) <= float(customer.windowStart) and float(customer.windowStart) <= float(succ.windowStart)
    batteryCapacityOK = float(inst.fuelConsumptionRate) * (Solution([route]).Cost + insertCost) <= float(inst.fuelCapacity) #avg velocity here?
    return capacityOK and timeWindowsOK and batteryCapacityOK


def _sortCustomersByAngle(customers):
    _initRandomPoint()
    return sorted(customers, key = _computeAngle)


def _initRandomPoint():
    global _randomPoint
    _randomPoint = (randint(0,100), randint(0,100))
    logger.info("Random point generated: (%d,%d)" % (_randomPoint[0], _randomPoint[1]))


def _computeAngle(customer):
    global _randomPoint
    customerPoint = (float(customer.x), float(customer.y))
    depotPoint = (float(inst.nodes['S0'].x), float(inst.nodes['S0'].y))
    d13 = _dist(depotPoint, customerPoint)
    d12 = _dist(depotPoint, _randomPoint)
    d23 = _dist(_randomPoint, customerPoint)
    return math.degrees(math.acos((math.pow(d12,2) + math.pow(d13,2) - math.pow(d23,2))/(2*d12*d13)))


def _dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def WorkWork(args):
    inst.setFileName(args.instance)
    inst.parse()
    customersSortedByAngle = _sortCustomersByAngle(inst.customers.values())
    routes = sequentialInsertion(customersSortedByAngle)
    sol = Solution(routes)
    print(sol)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Runs simple Sequential Heuristic on instance file')
    parser.add_argument('--instance', '-i', metavar='INSTANCE_FILE', required=True, help='The instance file')
    args = parser.parse_args()
    WorkWork(args)
