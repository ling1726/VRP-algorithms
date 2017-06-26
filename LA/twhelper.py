import instance.instance as inst
import instance.charger as charger

dm = None
"""
@return True if route is Time Window feasible, False otherwise.

Route duration is computed from scratch. The result is the best possible (feasible) combination of
departure times + waiting times i.e. if the time windows of the provided route can somehow be made
feasible while preserving the order of insertions, this will do it.
"""
def feasible(route):
    duration = 0
    battery = inst.fuelCapacity
    capacity = inst.loadCapacity
    if route[0].id == "D0" and route[1].id == "D0": return True # if the route has no customers it should be feasible
    for i in range(len(route[1:])):
        node = route[i+1]
        battery -= batterySpent(route[i], node)
        duration += travelTime(route[i], node)
        duration += waitTime(node, duration)
        capacity -= node.demand
        if duration > node.windowEnd or capacity < 0 or battery < 0: return False
        duration += node.serviceTime
        if isinstance(node, charger.Charger): 
            duration += (inst.fuelCapacity - battery) * inst.inverseFuellingRate
            battery = inst.fuelCapacity
    return True

def waitTime(node, duration):
    return max(0, node.windowStart - duration)

def travelTime(previous, node):
    return dm[(previous.id, node.id)]/inst.averageVelocity
    
def batterySpent(previous, node):
    return dm[(previous.id, node.id)] * inst.fuelConsumptionRate

def setDistanceMatrix(distanceMatrix):
    global dm
    dm = distanceMatrix
