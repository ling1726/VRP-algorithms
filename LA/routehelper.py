import instance.instance as inst
import twhelper as tw
import copy

def depotReachable(route, node):
    res = route.battery - _b(node, inst.depot)
    if route.last() != node: res -= _b(route.last(), node)
    return 0 <= res 

def chargable(route, charger, node):
    res = route.battery - _b(node, charger)
    if route.last() != node: res -= _b(route.last(), node)
    #print("CHARGABEL", 0<= res, node.id)
    return 0 <= res and _sufficientTimeForCharging(route, node)

def cost(route):
    return sum(_d(route.nodes[i], route.nodes[i+1]) for i in range(len(route.nodes[1:])))

def closestCharger(node):
    return min(inst.chargers.values(), key=lambda x: _b(node, x))

def closestChargerBetweenTwoNodes(node1, node2):
    chargersWithoutS0 = [s for s in inst.chargers.values() if s.id != 'S0']
    return min(chargersWithoutS0, key=lambda x: _b(node1,x) + _b(x, node2))

def _sufficientTimeForCharging(route, node):
    if route.last() != node:
        route = copy.deepcopy(route)
        route.insert(node)
    cc = closestCharger(route.last())
    return tw.feasible(route.nodes + [cc, inst.depot])

def _t(node1, node2):
    return _d(node1, node2) * inst.averageVelocity

def _b(node1, node2):
    return _d(node1,node2) * inst.fuelConsumptionRate

def _d(node1, node2):
    return inst.getValDistanceMatrix(node1, node2)
