import argparse
import os
import subprocess
from operator import itemgetter

import graphviz as gv

import NB.instance.instance as instance
import NB.util as util
from NB.Solution.route import Route
from NB.construction_heuristic import _create_initial_routes, _calculate_savings, _get_routes
from NB.instance.instance import *

# Logger
# logging.basicConfig(level=logging.ERROR)
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


def construction_heuristic(blacklist):
    # Here we will use savings criteria (paralell) for now. This might be switched afterwards
    routes = _create_initial_routes()
    savings = _calculate_savings(routes, blacklist)
    routes = util._delete_only_charger_routes(routes)

    savings.sort(key=itemgetter(2), reverse=True)
    for sav in savings:
        route1, route2 = _get_routes(sav, routes)
        if route1 is None or route2 is None or route1 == route2:
            continue
        new_route = util._check_combination(route1.get_nodes() + route2.get_nodes())
        if new_route:
            routes.remove(route1)
            routes.remove(route2)
            new_route_object = Route(new_route)
            routes.append(new_route_object)
    logger.info("Final routes calculated")

    for r in routes:
        # TODO: check if route violates time windows!!
        nodes = r.get_nodes()
        if len(nodes) == 2 and type(nodes[0]) is Customer and type(nodes[1]) is Charger:
            start_time = max(instance.getValDistanceMatrix(instance.depot, nodes[0]) * instance.averageVelocity,
                             nodes[0].windowStart)
            a = instance.getValDistanceMatrix(nodes[0], nodes[1]) * instance.averageVelocity
            b = instance.getValDistanceMatrix(nodes[1], instance.depot) * instance.averageVelocity
            endtime = start_time + nodes[0].serviceTime + a + b + nodes[1].load_time
            if endtime > instance.depot.windowEnd:
                print(instance.filename)
                rev = list(reversed(nodes))
                r.nodes = rev
        r.update()
    return routes


def variable_neighbourhood_descent(solution):
    neighbourhoods = []
    current_best = solution
    for i in range(len(neighbourhoods)):
        neighbourhood = neighbourhoods[i]
        tmp = sorted(neighbourhood.generate_neighbourhood(current_best), key=lambda x: x.cost)
        if tmp.cost < current_best.cost:
            current_best = tmp
            i = 0

    return current_best

def _visualize_solution(instance, solution):
    g1 = gv.Digraph(format='svg', engine="neato")
    color_step = int(16777215 / len(solution) + 1)
    color = 0
    for n in instance.nodes.values():
        if type(n) == Customer:
            pos = str(n.x / 10) + "," + str(n.y / 10) + "!"
            g1.node(n.id, shape="box", color="red", fixedsize="true", width=".2", height=".2", fontsize="9", pos=pos)
        else:
            pos = str(n.x / 10) + "," + str(n.y / 10) + "!"
            g1.node(n.id, color="blue", fixedsize="true", width=".2", height=".2", fontsize="9", pos=pos)
    for r in solution:
        ad_route = [instance.depot]
        ad_route.extend(r.get_nodes()[:])
        ad_route.append(instance.depot)
        this_color = "#" + '{:06x}'.format(color)
        for i in range(len(ad_route) - 1):
            a = ad_route[i].id.split("_")[0]
            b = ad_route[i + 1].id.split("_")[0]

            g1.edge(a, b, penwidth=".7", arrowsize=".2", color=this_color)
        color += color_step

    filename = g1.render(filename='img/' + instance.filename)


def write_solution(solution):
    total_cost = 0
    for s in solution:
        total_cost += s.calc_cost()
    print(instance.filename)
    print(total_cost)
    print()
    if args.verify:
        tempFile = instance.filename + '.sol'
        f = open(tempFile, mode='w')
        f.write(str(round(total_cost, 3)) + "\n")
        for r in solution:
            sol_line = "D0, "
            for c in r.get_nodes():
                sol_line += str(c).split("_")[0]
                sol_line += ", "
            sol_line += "D0\n"
            f.write(sol_line)
        f.close()

        p2 = subprocess.check_output(
            ['java', '-jar', '../data/verifier/EVRPTWVerifier.jar', '-d', instance.filename, tempFile])
        print(p2)
        # os.remove(tempFile)


def startProgram(args):
    fold = "../data/instances"
    for file_parse in os.listdir(fold):
        # for i in range(0,1):
        #     file_parse = "rc106_21.txt"
        if file_parse.startswith(".") or file_parse.endswith("sol"):
            continue
        datareading(file_parse)
        blacklist = preprocessing()
        solution = construction_heuristic(blacklist)
        solution = variable_neighbourhood_descent(solution)
        _visualize_solution(instance, solution)
        write_solution(solution)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Runs simple Sequential Heuristic on instance file')
    parser.add_argument('--instance', '-i', metavar='INSTANCE_FILE', required=True, help='The instance file')
    parser.add_argument('--verify', '-v', action='store_true', help='Uses the EVRPTWVerifier to verify the solution')
    args = parser.parse_args()
    startProgram(args)
