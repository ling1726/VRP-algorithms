import copy

from NB.solution.route import Route
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

    def update_cost(self):
        self.cost = self.calc_cost()

    def get_cost(self):
        return self.cost

    def clone(self):
        new_routes = []
        for route in self.routes:
            new_routes.append(route.clone())

        return Solution(new_routes)

    def __str__(self):
        return str(self.cost, str([str(x) for x in self.routes]))
