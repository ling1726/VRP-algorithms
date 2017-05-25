from instance.instance import *


# Schneider: The Electric Vehicle-Routing Problem with Time
# Windows and Recharging Stations
# returns forbiddenArcs ass set of node ids tuples. (node1.id,node2.id)
def preprocessing():
    forbiddenArcs = set()
    # arcs (v,w) and (w,v) are not the same because of time windows
    for node1 in nodes:
        for node2 in nodes:
            if node1.id == node2.id:
                continue

            if (node1.demand + node2.demand > loadCapacity) or \
                    (node1.windowStart + node1.serviceTime + getValDistanceMatrix(node1, node2) / averageVelocity >
                         node2.windowEnd) or \
                    (node1.windowStart + node1.serviceTime + getValDistanceMatrix(node1, node2) / averageVelocity +
                         node2.serviceTime + getValDistanceMatrix(node2.id, nodes["S0"]) / averageVelocity >
                         nodes["S0"].windowEnd):
                forbiddenArcs.add((node1.id, node2.id))
                continue

            other_chargers = set(chargers)
            for charge1 in chargers:
                other_chargers.remove(charge1)
                for charge2 in other_chargers:
                    if (fuelConsumptionRate * (getValDistanceMatrix(charge1, node1) +
                                                   getValDistanceMatrix(node1, node2) +
                                                   getValDistanceMatrix(node2, charge2)) > fuelCapacity):
                        forbiddenArcs.add((node1.id, node2.id))
                        continue

    return forbiddenArcs
