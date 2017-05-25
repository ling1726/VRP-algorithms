from LA.instance import *


# Schneider: The Electric Vehicle-Routing Problem with Time
# Windows and Recharging Stations
# returns forbiddenArcs ass set of node ids tuples. (node1.id,node2.id)
def preprocessing():
    forbiddenArcs = set()
    # arcs (v,w) and (w,v) are not the same because of time windows
    for node1Key in nodes:
        node1 = nodes[node1Key]
        for node2Key in nodes:
            if node1Key == node2Key:
                continue
            node2 = nodes[node2Key]

            if (node1.demand + node2.demand > loadCapacity) or \
                    (node1.windowStart + node1.serviceTime + getValDistanceMatrix(node1, node2) / averageVelocity >
                         node2.windowEnd) or \
                    (node1.windowStart + node1.serviceTime + getValDistanceMatrix(node1, node2) / averageVelocity +
                         node2.serviceTime + getValDistanceMatrix(node2, nodes["S0"]) / averageVelocity >
                         nodes["S0"].windowEnd):
                forbiddenArcs.add((node1.id, node2.id))
                continue

            #next comparison is only if both nodes are customers
            if node1.id.startswith("S") or node2.id.startswith("S"):
                continue

            allowedArc = False
            for charge1Key in chargers:
                if allowedArc:
                    break
                charge1 = chargers[charge1Key]
                for charge2Key in chargers:
                    if charge1Key == charge2Key:
                        continue
                    charge2 = chargers[charge2Key]
                    if (fuelConsumptionRate * (getValDistanceMatrix(charge1, node1) +
                                                   getValDistanceMatrix(node1, node2) +
                                                   getValDistanceMatrix(node2, charge2)) <= fuelCapacity):
                        allowedArc = True
                        break

            if not allowedArc:
                forbiddenArcs.add((node1.id, node2.id))

    return forbiddenArcs
6
