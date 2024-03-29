import argparse
import re
import statistics
import subprocess
import time

import graphviz as gv

import NB.instance.instance as instance
from NB import util
from NB.construction_heuristic import construction_heuristic
from NB.instance.instance import *
from NB.neighbourhoods.CustomerInsertionIntra import CustomerInsertionIntra
from NB.neighbourhoods.CustomerRelocateInter import CustomerRelocateInter
from NB.neighbourhoods.SwapCustomersInter import SwapCustomersInter

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


def variable_neighbourhood_search(solution):
    neighbourhoods = [CustomerInsertionIntra(), CustomerRelocateInter(util.get_longest_waiting_customer),
                      SwapCustomersInter(util.get_longest_waiting_customer)]
    iteration_count = 0
    best_all = solution
    while iteration_count < 10:
        k = 0
        current_best = solution
        while k < len(neighbourhoods):
            # Shaking
            neighbourhood_method = neighbourhoods[k]
            tmp = neighbourhood_method.generate_random_solution(current_best)
            tmp = variable_neighbourhood_descent(tmp)
            k += 1
            if tmp.cost < current_best.cost:
                print("VNS Found better for:", current_best.cost - tmp.cost, "in neighbourhood", k)
                print("---------------------------------------------------")
                current_best = tmp
                k = 0
        iteration_count += 1
        if current_best.cost < best_all.cost:
            best_all = current_best
        print("-----------------END OF ITERATION------------------")

    util.check_violates_tw(best_all.routes)
    best_all.update_cost()
    return best_all


def variable_neighbourhood_descent(solution):
    neighbourhoods = [CustomerInsertionIntra(), CustomerRelocateInter(util.get_farthest_customer),
                      SwapCustomersInter(util.get_farthest_customer)]
    current_best = solution
    i = 0
    while i < len(neighbourhoods):
        neighbourhood = neighbourhoods[i]
        neighbourhood = neighbourhood.generate_neighbourhood(current_best)
        i += 1
        if neighbourhood:
            tmp = sorted(neighbourhood, key=lambda x: x.cost)[0]
            if tmp.cost < current_best.cost:
                # print("VND Found better for:", current_best.cost - tmp.cost)
                # print("---------------------------------------------------")
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


def write_solution(solution, file_parse, constr_sol, time_ex, i, results_file):
    print(instance.filename)
    print(solution.cost)
    print()
    rf = open(results_file, "a")
    rf.write(file_parse + "," + str(constr_sol.cost) + "," + str(solution.cost) + "," + str(
        100 * (constr_sol.cost - solution.cost) / constr_sol.cost) + "," + str(time_ex) + "\n")
    rf.close()

    tempFile = file_parse + str(i) + '.sol'
    f = open(tempFile, mode='w')
    f.write(str(round(solution.cost, 3)) + "\n")
    for r in solution.routes:
        sol_line = "D0, "
        for c in r.get_nodes():
            sol_line += str(c).split("_")[0]
            sol_line += ", "
        sol_line += "D0\n"
        f.write(sol_line)
    f.close()

    p2 = subprocess.check_output(
        ['java', '-jar', '../data/verifier/EVRPTWVerifier.jar', '-d', tempFile, tempFile])
    rf = open("resulting.txt", "a")
    rf.write(str(p2) + "\n")
    rf.close()
    print(p2[-13:-2])


def check_string(file_parse):
    with open("results_test.csv") as f:
        found = False
        for line in f:  # iterate over the file one line at a time(memory efficient)
            if re.search("{0}".format(file_parse), line):  # if string found is in current line then print it
                found = True
    return found


def create_statistics(results_file, number_of_runs):
    with open(results_file) as f:
        results = {}
        for line in f:
            split = line.split(",")
            results_list = results.get(split[0], [])
            if not results_list:
                results[split[0]] = results_list
                for i in range(4):
                    results_list.append([])
            for i in range(4):
                results_list[i].append(float(split[i + 1]))
        for key in results:
            string = key
            for j in range(4):
                string += "," + str(sum(results[key][j]) / number_of_runs) + "," + str(
                    statistics.pstdev(results[key][j]))
            print(string)


def start_program(args, i):
    datareading(args.instance)
    # blacklist = preprocessing()
    blacklist = []
    solution_constr = construction_heuristic(blacklist)
    start = time.time()
    solution = variable_neighbourhood_search(solution_constr)
    end = time.time()
    print("Construction heuristic:", solution.cost, " metha better for:", solution_constr.cost - solution.cost,
          "time :", end - start)
    _visualize_solution(instance, solution.routes)
    write_solution(solution, args.instance, solution_constr, end - start, i)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Runs simple Sequential Heuristic on instance file')
    parser.add_argument('--instance', '-i', metavar='INSTANCE_FILE', required=True, help='The instance file')
    parser.add_argument('--verify', '-v', action='store_true', help='Uses the EVRPTWVerifier to verify the solution')
    parser.add_argument('--results_file', '-r', default="results.csv",
                        help='Write construction cost, methaheuristic cost, improvement, and time')
    parser.add_argument('--runs', default=1, help='Number of runs')
    args = parser.parse_args()
    # because of statistics
    for i in range(args.runs):
        start_program(args, i)
    create_statistics(args.results_file, args.runs)
