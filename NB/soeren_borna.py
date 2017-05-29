import argparse

import NB.instance.instance as instance
from NB.Solution.route import Route
from NB.instance.instance import *


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

    return forbiddenArcs


def datareading(path):
    instance.setFileName(path)
    instance.parse()
    pass

# start savings
def _create_initial_routes():
    routes = []
    for node in nodes.values():
        route = Route([node])
        routes.append(route)
    return routes


def _calculate_savings(routes, blacklist):
    #savings are kept as list of tuples (first_node, second_node, savings_value) to be more easily sorted
    savings = []
    for route1 in routes:
        for route2 in routes:
            #if (node1.id, node2.id) in blacklist:
                #continue
            a = instance.getValDistanceMatrix(route1.end, nodes.get('S0'))
            b = instance.getValDistanceMatrix(nodes.get('S0'), route2.start)
            c = instance.getValDistanceMatrix(route1.end, route2.start)
            new_savings_value = a + b - c
            savings.append((route1.end, route2.start, new_savings_value))

    logger.info("savings calculated")
    return savings


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


def _check_combination(route1, route2):
    # Here we need to check if this solution is feasable
    # For now we just the newly created route and calculate the consumption, capacity etc...
    # There might be a better way to do this
    test_route = route1.get_nodes() + route2.get_nodes()
    return False


def _combine_routes(route1, route2):
    pass


def solving(blacklist):
    # Here we will use savings criteria (paralell) for now. This might be switched afterwards
    routes = _create_initial_routes()
    savings = _calculate_savings(routes, blacklist)
    for sav in savings:
        route1, route2 = _get_routes(sav, routes)
        feasibility = _check_combination(route1, route2)
        if feasibility:
            routes.remove(route1)
            routes.remove(route2)
            routes.append(_combine_routes(route1, route2))

# from here we can:
#   - read in the data
#   - create the instance object
#   - call the solving strategy

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dummy Data Import
logger.debug("Using dummy inport, Abolute path specific to computer")
path_soeren = "c103_21.txt"



def startProgram(args):
    datareading(args.instance)
    blacklist = preprocessing()
    solving(blacklist)
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Runs simple Sequential Heuristic on instance file')
    parser.add_argument('--instance', '-i', metavar='INSTANCE_FILE', required=True, help='The instance file')
    args = parser.parse_args()
    startProgram(args)