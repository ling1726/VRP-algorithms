import copy

from NB.Solution.route import Route
from NB.instance.customer import Customer


class Solution(object):
    def __init__(self, routes):
        self.routes = routes
        self.cost = self.calc_cost()

    def calc_cost(self):
        cost = 0
        for route in self.routes:
            cost += route.cost
        return cost

    def add_route(self, route):
        self.routes.append(route)
        self.calc_cost()

    def update_cost(self):
        self.cost = self.calc_cost()

    def get_cost(self):  #
        return self.cost

    def clone(self):
        new_routes = []
        for route in self.routes:
            new_route = []
            for node in route.nodes:
                if type(node) is Customer:
                    new_route.append(copy.deepcopy(node))
            new_route = route.clone()
            new_routes.append(new_route)

        return Solution(new_routes)

    def __str__(self):
        return str(self.cost, str([str(x) for x in self.routes]))
