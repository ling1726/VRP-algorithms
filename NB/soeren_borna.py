import argparse
import os
from operator import itemgetter

import subprocess

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
    for node1Key in instance.nodes:
        node1 = nodes[node1Key]
        for node2Key in instance.nodes:
            if node1Key == node2Key:
                continue
            node2 = instance.nodes[node2Key]
            if (node1.demand + node2.demand > instance.loadCapacity):
                logger.debug("discarded because of too high demand: %f for maximum %f" % (
                    node1.demand + node2.demand, instance.loadCapacity))
                forbiddenArcs.add((node1.id, node2.id))
                continue
            if (node1.windowStart + node1.serviceTime + (
                        getValDistanceMatrix(node1, node2) / instance.averageVelocity) > node2.windowEnd):
                logger.debug(
                    "discarded because after serving %s, at earliest time + servicetime + traveltime exceeds latest servicetime of %s" % (
                        node1, node2))
                forbiddenArcs.add((node1.id, node2.id))
                continue
            if (node1.windowStart + node1.serviceTime + (
                        getValDistanceMatrix(node1, node2) / instance.averageVelocity) +
                    node2.serviceTime + (getValDistanceMatrix(node2, instance.depot) / instance.averageVelocity) >
                    instance.depot.windowEnd):
                logger.debug(
                    "discarded because after serving  %s, %s can't be served in time to make it back to the depot" % (
                        node1, node2))
                forbiddenArcs.add((node1.id, node2.id))
                continue

            # next comparison is only if both nodes are customers
            if node1.id.startswith("S") or node2.id.startswith("S"):
                continue

            allowedArc = False
            # TODO: Check if we need to use instance.chargers
            for charge1Key in instance.chargers:
                if allowedArc:
                    break
                charge1 = instance.chargers[charge1Key]
                for charge2Key in instance.chargers:
                    ''' There might be a situation where returning to the same charger makes an arc viable, so i commented this out
                    if charge1Key == charge2Key:
                        continue
                    '''
                    charge2 = instance.chargers[charge2Key]
                    if (instance.fuelConsumptionRate * (getValDistanceMatrix(charge1, node1) +
                                                            getValDistanceMatrix(node1, node2) +
                                                            getValDistanceMatrix(node2,
                                                                                 charge2)) <= instance.fuelCapacity):
                        allowedArc = True
                        break

            if not allowedArc:
                logger.debug(
                    "discarded because there is no drivable route from any charger to %s, %s and back to any charger, without going over the fuel capacity" % (
                        node1, node2))
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
        # if type(node) is Charger:
        #     continue
        if _get_route_consumption([node]) > instance.fuelCapacity:
            next_charger = _find_nearest_charger(node)
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
                new_route = [next_charger,node]
            route = Route(new_route)
        else:
            route = Route([node])
        routes.append(route)
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


def _find_nearest_charger(node):
    min_distance = math.inf
    min_charger = None
    for charger in chargers.values():
        this_distance = instance.getValDistanceMatrix(node, charger)
        if this_distance < min_distance and not charger.equal_to(node):
            min_distance = this_distance
            min_charger = charger
    return min_charger


def add_charger(test_route, charger_index, use_heurisitic):
    """
    Method looks backward for the first feasible charger insertion
    :param test_route:
    :param charger_index: desired charged index
    :return: if inserted charger is depot or charger can not be added to make route feasible returns empty list,
            otherwise feasible route
    """
    tmp_route = test_route[:]
    for i in reversed(range(1, charger_index)):
        charger_org = _find_nearest_charger(test_route[i])
        charger_temp = charger_org.generate_clone()
        # insert charger
        tmp_route.insert(i + 1, charger_temp)
        feasible_insertion = instance.fuelCapacity >= _get_route_consumption(tmp_route[:charger_index + 2]) * instance.fuelConsumptionRate
        if feasible_insertion:
            break
        del tmp_route[i+1]

    # if feasible insertion is not found or it is depot or it is charger right before the depot
    if charger_org == instance.depot:# or type(tmp_route[-2]) is Charger :
         tmp_route = []
    elif not feasible_insertion and use_heurisitic:
        #heurisic insertion
         edge = _most_consuming_edge(tmp_route[:charger_index])
         nearest_charger = _nearest_charger(tmp_route[edge[0]], tmp_route[edge[1]]).generate_clone()
         #nearest_charger = _find_nearest_charger(tmp_route[edge[0]])
         tmp_route.insert(edge[1],nearest_charger)
    elif not feasible_insertion and tmp_route == test_route:
        tmp_route = []

    return tmp_route

def _most_consuming_edge(route):
    max_dist = 0
    node_indexes = None
    for i in range(len(route)-1):
        temp_dist = instance.getValDistanceMatrix(route[i], route[i+1])
        if temp_dist > max_dist:
            max_dist = temp_dist
            node_indexes = (i, i+1)
    return node_indexes

def _nearest_charger(node1, node2):
    min_dist = None
    min_charger = None

    for charger in chargers.values():
        if charger.equal_to(node1) or charger.equal_to(node2):
            continue
        dist = instance.getValDistanceMatrix(node1, charger)
        dist += instance.getValDistanceMatrix(charger, node2)
        if min_dist is None or dist < min_dist:
            min_dist = dist
            min_charger = charger
    return min_charger

def _make_fuel_consumption_feasible(route1, route2, use_heuristic=False):
    test_route = route1.get_nodes() + route2.get_nodes()

    # for testing, we add the depots
    test_route.insert(0, instance.depot)
    test_route.append(instance.depot)
     # fuel consumption test, INCLUDING Insertion of Chargers where necessary (If possible)
    i = 0
    current_fuel = instance.fuelCapacity
    while i < len(test_route) - 1:
        if type(test_route[i]) is Charger:
            # record the time we need to spend at this charger
            test_route[i].load_time = (instance.fuelCapacity - current_fuel) * instance.inverseFuellingRate
            current_fuel = instance.fuelCapacity
        next_fuel = current_fuel - instance.getValDistanceMatrix(test_route[i],
                                                                 test_route[i + 1]) * instance.fuelConsumptionRate
        if next_fuel < 0:
            test_route = add_charger(test_route, i + 1, use_heuristic)
            # Use implicit falseness off empty list
            if not test_route or len(test_route) > 100:
                logger.debug(
                    "Rejected combination of %s and %s, because theres no good way to insert a charger" % (
                        route1, route2))
                return []
            i = 0
            current_fuel = fuelCapacity
        else:
            current_fuel = next_fuel
            i += 1

    return test_route

def _check_combination(route1, route2):
    # Here we need to check if this solution is feasible
    # For now we just the newly created route and calculate the consumption, capacity etc...
    # There might be a better way to do this

    test_route = _make_fuel_consumption_feasible(route1,route2)
    current_capacity = 0
    current_time = 0

    for i in range(len(test_route) - 1):

        # Check Time Windows

        # add time used to charge if the current node is a charger
        if type(test_route[i]) is Charger:
            current_time += test_route[i].load_time

        next_time = current_time + test_route[i].serviceTime + instance.averageVelocity * instance.getValDistanceMatrix(
            test_route[i], test_route[i + 1])
        if next_time > test_route[i + 1].windowEnd:
            logger.debug("Rejected combination of %s and %s, because we exceeded time window at %s" % (
                route1, route2, test_route[i + 1]))
            return []
        current_time = max(next_time, test_route[i + 1].windowStart)

        # Check Capacity Constraints
        next_capacity = current_capacity + test_route[i + 1].demand
        if next_capacity > instance.loadCapacity:
            logger.debug("Rejected combination of %s and %s, because we exceeded maximal capacity at %s" % (
                route1, route2, test_route[i + 1]))
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

    if test_route:
        # After this check we remove depots again because we work with savings
        del test_route[0]
        del test_route[-1]
    return test_route

def _delete_only_charger_routes(routes):
    tmp_routes = routes[:]
    for route in routes:
        have_customer = False
        for node in route.get_nodes():
            if type(node) is Customer:
                have_customer = True
                break
        if not have_customer:
            tmp_routes.remove(route)
    return tmp_routes

def solving(blacklist):
    # Here we will use savings criteria (paralell) for now. This might be switched afterwards
    routes = _create_initial_routes()
    savings = _calculate_savings(routes, blacklist)
    routes = _delete_only_charger_routes(routes)

    savings.sort(key=itemgetter(2), reverse=True)
    for sav in savings:
        route1, route2 = _get_routes(sav, routes)
        if route1 is None or route2 is None or route1 == route2:
            continue
        new_route = _check_combination(route1, route2)
        if new_route:
            routes.remove(route1)
            routes.remove(route2)
            new_route_object = Route(new_route)
            routes.append(new_route_object)
    logger.info("Final routes calculated")
    return routes

import os
def startProgram(args):
    fold="../data/instances"
    for file_parse in os.listdir(fold):
    # for i in range(0,1):
    #     file_parse = "rc106_21.txt"
        if file_parse=="r102_21.txt":
            continue
        if file_parse.startswith(".") or file_parse.endswith("sol"):
            continue
        datareading(file_parse)
        blacklist = preprocessing()
        solution = solving(blacklist)
        total_cost = 0
        for s in solution:
            total_cost+=s.calc_cost()
        if args.verify:
            tempFile = instance.filename + '.sol'
            f = open(tempFile, mode='w')
            f.write(str(round(total_cost,3))+"\n")
            for r in solution:
                sol_line = "D0, "
                for c in r.get_nodes():
                    sol_line += str(c).split("_")[0]
                    sol_line += ", "
                sol_line += "D0\n"
                f.write(sol_line)
            f.close()

            subprocess.call(['java', '-jar', '../data/verifier/EVRPTWVerifier.jar', '-d', instance.filename, tempFile])
            #os.remove(tempFile)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Runs simple Sequential Heuristic on instance file')
    parser.add_argument('--instance', '-i', metavar='INSTANCE_FILE', required=True, help='The instance file')
    parser.add_argument('--verify', '-v', action = 'store_true', help='Uses the EVRPTWVerifier to verify the solution')
    args = parser.parse_args()
    startProgram(args)
