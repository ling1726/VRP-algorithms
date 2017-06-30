import sys
import os
import subprocess
import argparse
import logging
from Construction import Construction
import statistics 
import graphviz as gv
import pickle
import statistics
import instance.instance as inst 
import SimulatedAnnealing as SA
import LargeNeighborhoodSearch as LNS
import twhelper as tw
import routehelper as rh
import random 
from random import choice

logging.basicConfig(level=logging.ERROR)                                                                       
logger = logging.getLogger(__name__) 

class Solution(object):
    def __init__(self):
        self.routes = []
        self.cost = 0.
        tw.setDistanceMatrix(inst._distanceMatrix)
        rh.precomputeClosestCharger()

    def constructInitialSolution(self):
        constructionSolution = Construction()
        constructionSolution.solve()
        self.routes = self._cp(constructionSolution.routes)
        self.cost = constructionSolution.cost

    def saSolution(self):
        sa = SA.SimulatedAnnealing(self.routes, self.cost)
        sa.solve()
        self.routes = self._cp(sa.routes)
        self.cost = sa.cost

    def solve(self):
        self.constructInitialSolution()
        self.saSolution()

    def _cp(self, o):
        return pickle.loads(pickle.dumps(o,-1)) 

    def __str__(self):
        routeStr = str.join('\n', [str.join(', ',[str(customer) for customer in route.nodes]) for route in self.routes])
        return '#solution for %s\n%.3f\n%s' % (inst.filename, self.cost, routeStr)

    def __str__(self):
        str_repr = "Result for ParamILS: %s, %d, %d, %.2f, %d" % (self.solved)
        
def next_params(count):
    rp = [0.15, 0.20, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5]                                                               
    xp = [0.05, 0.1, 0.15, 0.2, 0.25]                                                                             
    ep = [0.05, 0.1, 0.15, 0.2, 0.25]                                                                             
    op = [0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5]                                                          
    tp = [0.05, 0.1, 0.15, 0.2, 0.25]                                                                             
    cp = [0.05, 0.1, 0.15, 0.2]
    
    pars = []
    while count:
        chosen = [choice(rp), choice(xp), choice(ep), choice(op), choice(tp), choice(cp)]
        if sum(chosen) == 1 and not chosen in pars:
            print("{rp=%s, xp=%s, ep=%s, op=%s, tp=%s, cp=%s}" % (chosen[0], chosen[1], chosen[2], chosen[3], chosen[4], chosen[5]))     
            pars.append(chosen)
            count -= 1
    return pars
def randomly(sequence):                                                                                      
        shuffled = list(sequence)                                                                                      
        random.shuffle(shuffled)                                                                                       
        return iter(shuffled)                                                                                          
                             
if __name__ == '__main__':
    inst.setFileName(sys.argv[1])
    inst.parse()
    parser = argparse.ArgumentParser(description='Runs simple Sequential Heuristic on instance file')
    parser.add_argument('--cutoff', '-l', metavar='CUTOFF', required=True, help='The instance file')
    parser.add_argument('--temp', '-t', metavar='TEMP', required=True, help='The instance file')
    args = parser.parse_args(sys.argv[6:])
    results = {}
    str_template = "{rp=%s, xp=%s, ep=%s, op=%s, tp=%s, cp=%s}"
    try:
        for c, pars in enumerate(next_params(100)):
            str_repr = str(str_template % tuple(pars))
            print("Configuration #%d: %s" % (c, str_repr))
            for i in range(10):
                sol = Solution()
                sol.constructInitialSolution()
                sa = SA.SimulatedAnnealing(sol.routes, sol.cost)
                #sa.set_seed(int(sys.argv[5]))
                sa.set_params(*pars,int(args.cutoff))
                res = sa.solve()
                try: results[str_repr].append(res)
                except KeyError: results[str_repr] = [res]
                #print("Result for ParamILS: %s, %d, %d, %.2f, %d" % res)
                #print("Result: %s, %d, %d, %.2f" % res[:-1])
                #print("Params: %s\n" % (str_repr))
    except KeyboardInterrupt:
        print("Interrupted")
    print("=========END RESULTS========")
    #sort according to best results
    for k in sorted(results, key=lambda x: statistics.mean([q[3] for q in results[x]]))[:10]:
        v = results[k]
        print("%s: best %.2f worst %.2f avg %.2f runs %d" % (k, min(r[3] for r in v), max(r[3] for r in v), statistics.mean([r[3] for r in v]) ,len(v)))
    
