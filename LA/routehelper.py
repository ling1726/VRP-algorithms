import instance.instance as inst
import twhelper as tw
import pickle

closestChargers = {}
chargersWithoutS0 = []

def depotReachable(route, node):
    res = route.battery - _b(node, inst.depot)
    if route.last() != node: res -= _b(route.last(), node)
    return 0 <= res 

def chargable(route, charger, node):
    res = route.battery - _b(node, charger)
    if route.last() != node: res -= _b(route.last(), node)
    return 0 <= res and _sufficientTimeForCharging(route, node)

def cost(route):
    return sum(_d(route.nodes[i], route.nodes[i+1]) for i in range(len(route.nodes[1:])))

def cost_n(nodes):
    return sum(_d(nodes[i], nodes[i+1]) for i in range(len(nodes[1:])))

def closestCharger(node):
    return min(inst.chargers.values(), key=lambda x: _b(node, x))

def closestChargerBetweenTwoNodes(node1, node2):
    charger = min(chargersWithoutS0, key=lambda x: _b(node1,x) + _b(x, node2))
    cost = _b(node1,charger) + _b(charger, node2)
    return charger,cost

def minCostCharger(node1, node2):
    return closestChargers[(node1.id,node2.id)][0]

def chargerCostTuple(node1,node2):
    return closestChargers[(node1.id,node2.id)]

def _sufficientTimeForCharging(route, node):
    if route.last() != node:
        route = _cp(route)
        route.insert(node)
    cc = closestCharger(route.last())
    return tw.feasible(route.nodes + [cc, inst.depot])

def _t(node1, node2):
    return _d(node1, node2) * inst.averageVelocity

def _b(node1, node2):
    return _d(node1,node2) * inst.fuelConsumptionRate

def _d(node1, node2):
    return inst.getValDistanceMatrix(node1, node2)

def _cp(o):
    return pickle.loads(pickle.dumps(o,-1)) 

def precomputeClosestCharger():
    global closestCharger, chargersWithoutS0
    chargersWithoutS0 = [s for s in inst.chargers.values() if s.id != 'S0']
    for n in inst.nodes.values():
        for m in inst.nodes.values():
            c = closestChargerBetweenTwoNodes(n,m)
            closestChargers[(n.id,m.id)] = c
            closestChargers[(m.id,n.id)] = c
            
