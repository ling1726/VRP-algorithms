import argparse
from operator import itemgetter

import NB.instance.instance as instance
from NB import util
from NB.Solution.route import Route
from NB.instance.instance import *

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            if (node1.demand + node2.demand > instance.loadCapacity):
                logger.debug("discarded because of too high demand: %f for maximum %f" % (node1.demand + node2.demand, instance.loadCapacity))
                forbiddenArcs.add((node1.id, node2.id))
                continue
            if (node1.windowStart + node1.serviceTime + (getValDistanceMatrix(node1, node2) / instance.averageVelocity) > node2.windowEnd):
                logger.debug("discarded because after serving %s, at earliest time + servicetime + traveltime exceeds latest servicetime of %s" % (node1, node2))
                forbiddenArcs.add((node1.id, node2.id))
                continue
            if (node1.windowStart + node1.serviceTime + (getValDistanceMatrix(node1, node2) / instance.averageVelocity) +
                         node2.serviceTime + (getValDistanceMatrix(node2, instance.depot) / instance.averageVelocity) >
                         instance.depot.windowEnd):
                logger.debug("discarded because after serving  %s, %s can't be served in time to make it back to the depot" %(node1, node2))
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
                    ''' There might be a situation where returning to the same charger makes an arc viable, so i commented this out
                    if charge1Key == charge2Key:
                        continue
                    '''
                    charge2 = chargers[charge2Key]
                    if (instance.fuelConsumptionRate * (getValDistanceMatrix(charge1, node1) +
                                                   getValDistanceMatrix(node1, node2) +
                                                   getValDistanceMatrix(node2, charge2)) <= instance.fuelCapacity):
                        allowedArc = True
                        break

            if not allowedArc:
                logger.debug("discarded because there is no drivable route from any charger to %s, %s and back to any charger, without going over the fuel capacity" % (node1, node2))
                forbiddenArcs.add((node1.id, node2.id))

    logger.info("Preprocessing finished")
    return forbiddenArcs


def datareading(path):
    instance.setFileName(path)
    instance.parse()
    pass

# from here on down this is the savings algorithm
def _create_initial_routes():
    routes = []
    for node in nodes.values():
        if type(node) is Charger:
            continue
        if _get_route_consumption([node]) > instance.fuelCapacity:
            next_charger = _find_nearest_charger(node)
            if _get_route_consumption([node, next_charger]) > instance.fuelCapacity:
                logger.error("Customer %s not reachable in this fashion" % (node))
            route = Route([next_charger, node])
        else:
            route = Route([node])
        routes.append(route)
    return routes

# this assumes that every visit to any charger charges the vehicle fully
def _get_route_consumption(nodes):
    part_route = [instance.depot]
    max_length = 0
    for node in nodes:
        part_route.append(node)
        if type(node) is Charger:
            part_length = util.calculate_plain_route_cost(part_route)
            if part_length > max_length:
                max_length = part_length
            part_route = []
    part_route.append(instance.depot)
    part_length = util.calculate_route_cost(part_route)
    if part_length > max_length:
        max_length = part_length
    return max_length * instance.averageVelocity


def _calculate_savings(routes, blacklist):
    #savings are kept as list of tuples (first_node, second_node, savings_value) to be more easily sorted
    savings = []
    for route1 in routes:
        for route2 in routes:
            if (route1.end.id, route2.start.id) in blacklist:
                continue
            if route1 == route2:
                continue
            a = instance.getValDistanceMatrix(route1.end, nodes.get('S0'))
            b = instance.getValDistanceMatrix(nodes.get('S0'), route2.start)
            c = instance.getValDistanceMatrix(route1.end, route2.start)
            new_savings_value = a + b - c
            savings.append((route1.end, route2.start, new_savings_value))

    logger.info("savings calculated")
    return [sav for sav in savings if sav[2] > 0]


def _get_routes(sav, routes):
    found1 = False
    found2 = False
    for route in routes:
        if route.end == sav[0]:
            route1 = route
            found1 = True
        if route.start == sav[1]:
            route2 = route
            found2 = True
        if found1 and found2:
            break
    if(found1 and found2):
        logger.debug("this routes found: %s, %s" % (route1, route2))
        return (route1, route2)
    else:
        logger.debug("No route found")
        return (None, None)


def _find_nearest_charger(node):
    min_distance = math.inf
    min_charger = None
    for charger in chargers.values():
        this_distance = instance.getValDistanceMatrix(node, charger)
        if this_distance < min_distance:
            min_distance = this_distance
            min_charger = charger
    return min_charger


def _check_combination(route1, route2):
    # Here we need to check if this solution is feasable
    # For now we just the newly created route and calculate the consumption, capacity etc...
    # There might be a better way to do this
    test_route = route1.get_nodes() + route2.get_nodes()

    current_consumption = util.calculate_route_cost([test_route[0]]) * instance.averageVelocity
    current_capacity = test_route[0].demand
    current_time = max(instance.averageVelocity * instance.getValDistanceMatrix(instance.depot, test_route[0]), test_route[0].windowStart)

    #TODO: CONSUMPTIONCHECK AND ADDING OF CHARGERS WHERE NEEDED

    for i in range(len(test_route)-1):

        # Check Time Windows
        next_time = current_time + test_route[i].serviceTime + instance.averageVelocity * instance.getValDistanceMatrix(test_route[i], test_route[i+1])
        if next_time > test_route[i+1].windowEnd:
            logger.debug("Rejected combination of %s and %s, because we exceeded time window at %s" % (route1, route2, test_route[i+1]))
            return []
        current_time = max(next_time, test_route[i+1].windowStart)

        # Check Capacity Constraints
        next_capacity = current_capacity + test_route[i+1].demand
        if next_capacity > instance.loadCapacity:
            logger.debug("Rejected combination of %s and %s, because we exceeded maximal capacity at %s" % (route1, route2, test_route[i + 1]))
            return []
        current_capacity = next_capacity

        '''This is just debug stuff
        print("our current route is:")
        print(test_route)
        print("from:")
        print(route1)
        print(route2)
        print("and we are at this node: %s" % test_route[i])
        charger = 0
        cust = 0
        for node in test_route:
            if type(node) is Charger:
                charger += 1
            if type(node) is Customer:
                cust += 1
        print()
        print("Chargers: %d\nCustomers: %d" % (charger, cust))
        print()
        print("currentCapacity: %d\nDemand of next Node: %d\nnextCapacity: %d" % (current_capacity, test_route[i+1].demand, next_capacity))
        input()'''

    #TODO: Check feasibility of return to depot (Capacity, and Time Windows)

    return test_route

def solving(blacklist):
    # Here we will use savings criteria (paralell) for now. This might be switched afterwards
    routes = _create_initial_routes()
    savings = _calculate_savings(routes, blacklist)
    savings.sort(key=itemgetter(2), reverse=True)
    for sav in savings:
        route1, route2 = _get_routes(sav, routes)
        if route1 is None or route2 is None or route1 == route2:
            continue
        new_route = _check_combination(route1, route2)
        if new_route != []:
            routes.remove(route1)
            routes.remove(route2)
            new_route = Route(route1.get_nodes() + route2.get_nodes())
            routes.append(new_route)
    return routes

def startProgram(args):
    datareading(args.instance)
    blacklist = preprocessing()
    solution = solving(blacklist)

    # print solution to debug.txt
    file = open("debug.txt", "w")
    for r in solution:
        file.write("%s" % len(r.get_nodes()))
        file.write("\n")
    file.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Runs simple Sequential Heuristic on instance file')
    parser.add_argument('--instance', '-i', metavar='INSTANCE_FILE', required=True, help='The instance file')
    args = parser.parse_args()
    startProgram(args)