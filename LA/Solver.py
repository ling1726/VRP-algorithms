import sys
import os
import subprocess
import argparse
import logging
from Construction import Construction
import statistics 
import graphviz as gv
from copy import deepcopy

import instance.instance as inst 
import SimulatedAnnealing as SA


logging.basicConfig(level=logging.ERROR)                                                                       
logger = logging.getLogger(__name__) 

class Solution(object):
    def __init__(self):
        # solution attributes
        self.routes = []
        self.cost = 0.

    def constructInitialSolution(self):
        constructionSolution = Construction()
        constructionSolution.solve()
        self.routes = deepcopy(constructionSolution.routes)
        self.cost = constructionSolution.cost

    def saSolution(self):
        sa = SA.SimulatedAnnealing(self.routes, self.cost)
        sa.solve()

        self.routes = deepcopy(sa.routes)
        self.cost = sa.cost
        
    def solve(self):
        self.constructInitialSolution()
        return self.saSolution()
        


    def __str__(self):
        routeStr = str.join('\n', [str.join(', ',[str(customer) for customer in route.nodes]) for route in self.routes])
        return '#solution for %s\n%.3f\n%s' % (inst.filename, self.cost, routeStr)



def _visualize_solution(solution):
    g1 = gv.Digraph(format='svg', engine="neato")
    color_step = int(16777215/len(solution.routes)+1)
    color = 0
    for n in inst.nodes.values():
        if n.id.startswith('C'):
            pos = str(n.x/10) + "," + str(n.y/10) + "!"
            g1.node(n.id, shape="box", color="red", fixedsize="true", width=".2", height=".2", fontsize="9", pos=pos)
        elif n.id.startswith('S0'): continue
        else:
            pos = str(n.x/10) + "," + str(n.y/10) + "!"
            g1.node(n.id, color="blue", fixedsize="true", width=".2", height=".2", fontsize="9", pos=pos)
    for r in solution.routes:
        ad_route = []
        ad_route.extend(r.nodes)
        this_color = "#"+'{:06x}'.format(color)
        for i in range(len(ad_route)-1):
            a = ad_route[i].id.split("_")[0]
            b = ad_route[i+1].id.split("_")[0]

            g1.edge(a, b, penwidth=".7", arrowsize=".2", color=this_color)
        color += color_step

    g1.format = 'svg'
    filename = g1.render(filename='img/'+inst.filename.split('/')[3])

        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Runs simple Sequential Heuristic on instance file')
    parser.add_argument('--instance', '-i', metavar='INSTANCE_FILE', required=True, help='The instance file')
    parser.add_argument('--verify', '-v', action = 'store_true', help='Uses the EVRPTWVerifier to verify the solution')
    parser.add_argument('--all', '-a', action = 'store_true', help='Runs the algorithms on all instances')
    parser.add_argument('--visual', '-z', action = 'store_true', help='Turns off the visualization')
    #parser.add_argument('--method', '-m', choices = ['constr', 'sa'], help='Choice of algorithm. Default is constructive method.')
    args = parser.parse_args()
    instanceFiles = [args.instance]
    if args.all:
        instanceFiles = os.listdir('../data/instances/')
        
    stats = []
    for instanceFile in instanceFiles:
        if not instanceFile.endswith('.txt'): continue
        inst.setFileName(instanceFile)
        inst.parse()
        sol = Solution()
        sol.solve()
        stats.append(sol.cost)

        if args.visual: _visualize_solution(sol)
        if not args.verify: print(sol)
        if args.verify:
            tempFile = instanceFile + '.sol'
            with open(tempFile, mode='w') as f:
                f.write(str(sol))
            subprocess.call(['java', '-jar', '../data/verifier/EVRPTWVerifier.jar', '-d',inst.filename, tempFile])
            os.remove(tempFile)
        inst.reset_data()
    if args.all:
        print("Mean: %.2f Median: %.2f Var: %.2f StdDev: %.2f" % (statistics.mean(stats), statistics.median(stats), statistics.variance(stats), statistics.stdev(stats)))
