import NB.instance.instance as instance
from NB.Solution.route import Route
from NB.instance.instance import *
import NB.util as util

def _create_initial_routes():
    routes = []
    for node in instance.nodes.values():
        '''
        # if type(node) is Charger:
        #     continue
        if _get_route_consumption([node]) > instance.fuelCapacity:
            next_charger = _find_nearest_charger(node).generate_clone()
            if _get_route_consumption([next_charger, node]) > instance.fuelCapacity:
                logger.error("Customer %s not reachable in this fashion" % (node))

                new_route = _make_fuel_consumption_feasible(Route([node]), Route([]), True)
                # # we need to set the time needed to charge
                # new_route.append(instance.depot)
                # new_route.insert(0,instance.depot)
                # dist = 0
                # for j in range(1,len(new_route)):
                #     if type(new_route[j]) is Charger and new_route[j]!= instance.depot:
                #         fuel_used = dist*instance.fuelConsumptionRate
                #         node.load_time = (instance.fuelCapacity - fuel_used) * instance.inverseFuellingRate
                #         dist = 0
                #     else:
                #         dist+=instance.getValDistanceMatrix(new_route[j-1], new_route[j])
                new_route.pop()
                new_route.pop(0)
            else:
                new_route = [node, next_charger]
            route = Route(new_route)
        else:
            route = Route([node])

        current_fuel = instance.fuelCapacity - instance.getValDistanceMatrix(instance.depot, route[0])
        for i in range(len(route)-1):'''
        new_route = util._make_fuel_consumption_feasible([node], True)
        new_route.pop()
        new_route.pop(0)
        route = Route(new_route)
        routes.append(route)


    #print(routes)
    return routes


# this assumes that every visit to any charger charges the vehicle fully and returns the maximum consumption of any part of this route between to chargers
def _get_route_consumption(nodes):
    last_charger = instance.depot
    max_length = 0
    part_route = []
    for node in nodes:
        if type(node) is Charger:
            part_length = util.calculate_route_cost(part_route, start=last_charger, end=node)
            if part_length > max_length:
                max_length = part_length
            part_route = []
            last_charger = node
        else:
            part_route.append(node)
    part_length = util.calculate_route_cost(part_route, start=last_charger, end=instance.depot)
    if part_length > max_length:
        max_length = part_length
    return max_length * instance.fuelConsumptionRate


def _calculate_savings(routes, blacklist):
    # savings are kept as list of tuples (first_node, second_node, savings_value) to be more easily sorted
    savings = []
    for route1 in routes:
        for route2 in routes:
            if (route1.end.id, route2.start.id) in blacklist:
                continue
            if route1 == route2:
                continue
            if type(route2.start) is Charger:
                continue
            a = instance.getValDistanceMatrix(route1.end, nodes.get('S0'))
            b = instance.getValDistanceMatrix(nodes.get('S0'), route2.start)
            c = instance.getValDistanceMatrix(route1.end, route2.start)
            new_savings_value = a + b - c
            savings.append((route1.end, route2.start, new_savings_value))

    logger.info("Savings calculated")
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
    if (found1 and found2):
        logger.debug("this routes found: %s, %s" % (route1, route2))
        return (route1, route2)
    else:
        logger.debug("No route found")
        return (None, None)
