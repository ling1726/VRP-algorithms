# Object representation of a route
import NB.instance.instance as instance
import math
from NB import util


class Route(object):
    def __init__(self, init_nodes=[]):

        self.nodes = init_nodes[:]
        if len(init_nodes) > 0:
            self.start = init_nodes[0]
            self.end = init_nodes[-1]
        else:
            self.start = None
            self.end = None
        self.cost = 0
        self.weight_point = None

    def add_node_at(self, new_node, index=-1):
        self.nodes.insert(index, new_node)
        self.start = self.nodes[0]
        self.end = self.nodes[-1]
        self.changed = True

    def remove_node(self, node):
        self.nodes.remove(node)
        self.start = self.nodes[0]
        self.end = self.nodes[-1]
        self.changed = True

    def calc_cost(self):
        return util.calculate_route_cost(self.nodes,instance.depot, instance.depot)

    def add_node_at_best(self, new_node):
        # Tupel saving the index of the minimum cost of inserting a customer at that index AND the minimum cost
        mincost = (None, math.inf)
        for i in range(len(self.nodes)):
            nodes_c = self.nodes[:]
            nodes_c.insert(i, new_node)
            new_cost = util.calculate_route_cost(nodes_c)
            if mincost[1] > new_cost:
                mincost[1] = new_cost
                mincost[0] = i
        self.nodes.insert(mincost[0], new_node)

    def update(self):
        """
        Call this method after changes are made to update its cost and weight point
        :return:
        """
        self.cost = self.calc_cost()
        self.weight_point = util.calculate_weight_point()

    def get_nodes(self):
        return self.nodes[:]

    def __str__(self):
        return str([str(i) for i in self.nodes])

