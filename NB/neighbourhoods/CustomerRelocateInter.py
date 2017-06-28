import random

import NB.util as util
from NB.Solution.route import Route
from NB.neighbourhoods.Neighbourhood import Neighbourhood


class CustomerRelocateInter(Neighbourhood):
    def __init__(self, selection_function):
        self.selection_function = selection_function

    def generate_neighbourhood(self, x):
        """
        Picks customer with selection criteria and inserts it in other routes and also
        in empty route.
        :param x:
        :return:
        """
        selected_customers = [self.selection_function(route) for route in x.routes]
        neighbourhood = []
        for i in range(len(selected_customers)):
            if len(x.routes[i].nodes) < 3:
                continue
            neighbour_removed = x.clone()
            # remove node from one route, and insert to all others
            route1 = neighbour_removed.routes[i]
            route1.remove_node(selected_customers[i])
            for j in range(len(x.routes)):
                neighbour = neighbour_removed.clone()
                extended_route = neighbour.routes[j]
                extended_route = Route(extended_route.strip_chargers())
                extended_route.add_node_at(selected_customers[i], random.randint(0, len(extended_route.nodes)))
                # extended_route.add_node_at_best(farthest_customers[i])
                checked = util.check_combination(extended_route.nodes)
                # combination is not feasible
                if not checked:
                    continue
                print("managed insertion INTER", "neigbourhood 2")
                extended_route.nodes = checked
                extended_route.update()

                neighbour.update_cost()
                neighbourhood.append(neighbour)
            # insert it as new route
            new_route = Route([selected_customers[i]])
            checked = util.make_fuel_consumption_feasible(new_route.nodes)
            new_route.nodes = checked
            new_route.update()

            neighbour_removed.update_cost()
            neighbour_removed.add_route(new_route)

        return neighbourhood
