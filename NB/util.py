import NB.instance.instance as instance
from NB.instance.instance import *


def calculate_route_cost(route, start=instance.depot, end=instance.depot):
    cost = 0

    if not route:
        return cost

    cost += instance.getValDistanceMatrix(start, route[0])
    for i in range(len(route) - 1):
        cost += instance.getValDistanceMatrix(route[i], route[i + 1])
    cost += instance.getValDistanceMatrix(route[-1], end)
    return cost


def get_farthest_customer(route):
    farthest_node = None
    farthest_dist = -1

    for node in route.nodes:
        if type(node) is Customer:
            dist = math.hypot(route.weight_point[0] - node.x, route.weight_point[1] - node.y)
            if dist > farthest_dist:
                farthest_dist = dist
                farthest_node = node
    return farthest_node

def get_longest_waiting_customer(route):
    longest_node = None
    longest_wait = -1

    for node in route.nodes:
        if longest_wait < node.waiting_time:
            longest_wait = node.waiting_time
            longest_node = node
    return longest_node

def calculate_weight_point(route):
    return sum([node.x for node in route.nodes]) / len(route.nodes), sum([node.y for node in route.nodes]) / len(route.nodes)


def check_combination(test_route):
    # Here we need to check if this solution is feasible
    # For now we just the newly created route and calculate the consumption, capacity etc...
    # There might be a better way to do this
    test_route = make_fuel_consumption_feasible(test_route)
    current_capacity = 0
    current_time = 0

    waiting_times = []

    for i in range(len(test_route) - 1):

        # Check Time Windows

        # add time used to charge if the current node is a charger
        if type(test_route[i]) is Charger:
            current_time += test_route[i].load_time

        next_time = current_time + test_route[i].serviceTime + instance.averageVelocity * instance.getValDistanceMatrix(
            test_route[i], test_route[i + 1])
        if next_time > test_route[i + 1].windowEnd:
            logger.debug("Rejected combination of %s, because we exceeded time window at %s" % (
                [x for x in test_route], test_route[i + 1]))
            return []
        wait = next_time - test_route[i + 1].windowStart
        if wait > 0:
            waiting_times.append(wait)
        else:
            waiting_times.append(0)
        current_time = max(next_time, test_route[i + 1].windowStart)

        # Check Capacity Constraints
        next_capacity = current_capacity + test_route[i + 1].demand
        if next_capacity > instance.loadCapacity:
            logger.debug("Rejected combination of %s, because we exceeded maximal capacity at %s" % (
                [x for x in test_route], test_route[i + 1]))
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
    for i in range(len(test_route)):
        test_route[i].waiting_time = waiting_times[i]

    return test_route


def _find_nearest_charger(node):
    min_distance = math.inf
    min_charger = None
    for charger in chargers.values():
        this_distance = instance.getValDistanceMatrix(node, charger)
        if this_distance < min_distance and not charger.equal_to(node):
            min_distance = this_distance
            min_charger = charger
    return min_charger

# this assumes that every visit to any charger charges the vehicle fully and returns the maximum consumption of any part of this route between to chargers
def _get_route_consumption(nodes):
    last_charger = instance.depot
    max_length = 0
    part_route = []
    for node in nodes:
        if type(node) is Charger:
            part_length = calculate_route_cost(part_route, start=last_charger, end=node)
            if part_length > max_length:
                max_length = part_length
            part_route = []
            last_charger = node
        else:
            part_route.append(node)
    part_length = calculate_route_cost(part_route, start=last_charger, end=instance.depot)
    if part_length > max_length:
        max_length = part_length
    return max_length * instance.fuelConsumptionRate



def _add_charger(test_route, charger_index, use_heurisitic):
    """
    Method looks backward for the first feasible charger insertion
    :param test_route:
    :param charger_index: desired charged index
    :return: if inserted charger is depot or charger can not be added to make route feasible returns empty list,
            otherwise feasible route
    """
    tmp_route = test_route[:]
    charger_org = None
    feasible_insertion = False
    for i in reversed(range(1, charger_index)):
        charger_org = _find_nearest_charger(test_route[i])
        charger_temp = charger_org.generate_clone()
        # insert charger
        tmp_route.insert(i + 1, charger_temp)
        feasible_insertion = instance.fuelCapacity >= _get_route_consumption(
            tmp_route[:charger_index + 2]) * instance.fuelConsumptionRate
        if feasible_insertion:
            break
        del tmp_route[i + 1]

    # if feasible insertion is not found or it is depot or it is charger right before the depot
    if charger_org and charger_org.equal_to(instance.depot):  # or type(tmp_route[-2]) is Charger :
        tmp_route = []
    elif not feasible_insertion and use_heurisitic:
        # heurisic insertion
        edge = _most_consuming_edge(tmp_route[:charger_index + 1])
        nearest_charger = _nearest_charger(tmp_route[edge[0]], tmp_route[edge[1]]).generate_clone()
        # nearest_charger = _find_nearest_charger(tmp_route[edge[0]])
        tmp_route.insert(edge[1], nearest_charger)
    elif not feasible_insertion and tmp_route == test_route:
        tmp_route = []

    return tmp_route


def _most_consuming_edge(route):
    max_dist = 0
    node_indexes = None
    for i in range(len(route) - 1):
        temp_dist = instance.getValDistanceMatrix(route[i], route[i + 1])
        if temp_dist > max_dist:
            max_dist = temp_dist
            node_indexes = (i, i + 1)
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


def make_fuel_consumption_feasible(test_route, use_heuristic=True):
    # for testing, we add the depots
    test_route.insert(0, instance.depot)
    test_route.append(instance.depot)
    # fuel consumption test, INCLUDING Insertion of Chargers where necessary (If possible)
    i = 0
    current_fuel = instance.fuelCapacity
    while i < len(test_route) - 1:
        if type(test_route[i]) is Charger and not test_route[i].equal_to(instance.depot):
            # record the time we need to spend at this charger
            test_route[i].load_time = (instance.fuelCapacity - current_fuel) * instance.inverseFuellingRate
            current_fuel = instance.fuelCapacity
        next_fuel = current_fuel - instance.getValDistanceMatrix(test_route[i],
                                                                 test_route[i + 1]) * instance.fuelConsumptionRate
        if next_fuel < 0:
            test_route = _add_charger(test_route, i + 1, use_heuristic)
            # Use implicit falseness off empty list
            if not test_route or len(test_route) > 100:
                logger.debug(
                    "Rejected combination of %s, because there is no good way to insert a charger" % (
                        [x for x in test_route]))
                return []
            i = 0
            current_fuel = instance.fuelCapacity
        else:
            current_fuel = next_fuel
            i += 1

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
