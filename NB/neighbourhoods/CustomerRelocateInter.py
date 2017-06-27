import random

import NB.util as util
from NB.Solution.route import Route
from NB.neighbourhoods.Neighbourhood import Neighbourhood


class CustomerRelocateInter(Neighbourhood):
    def generate_neighbourhood(self, x):
        """
        Picks customer who is the farthest away from all other customers in his route and inserts it in other routes and also
        in empty route.
        :param x:
        :return:
        """
        farthest_customers = [util.get_farthest_customer(route) for route in x.routes]
        neighbourhood = []
        for i in range(len(farthest_customers)):
            neighbour_removed = x.clone()
            # remove node from one route, and insert to all others
            route1 = neighbour_removed.routes[i]
            route1.remove_node(farthest_customers[i])
            for j in range(len(x.routes)):
                neighbour = neighbour_removed.clone()
                extended_route = neighbour.routes[j]
                extended_route.add_node_at(farthest_customers[i], random.randint(0, len(extended_route.nodes)))
                #extended_route.add_node_at_best(farthest_customers[i])
                checked = util.check_combination(extended_route.nodes)
                # combination is not feasible
                if not checked:
                    continue
                print("managed insertion")
                extended_route.nodes = checked
                extended_route.update()

                neighbour.update_cost()
                neighbourhood.append(neighbour)
            #insert it as new route
            new_route = Route([farthest_customers[i]])
            checked = util.make_fuel_consumption_feasible(new_route.nodes)
            new_route.nodes = checked
            new_route.update()

            neighbour_removed.update_cost()
            neighbour_removed.add_route(new_route)


        return neighbourhood
