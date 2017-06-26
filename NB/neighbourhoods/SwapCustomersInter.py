import random

import NB.util as util
from NB.Solution.route import Route
from NB.neighbourhoods.Neighbourhood import Neighbourhood


class SwapCustomersInter(Neighbourhood):

    def generate_neighbourhood(self, x):
        """
        Generates neighbourhood of given solution x by swapping chargers from different routes. From each route it
        selects the customer which is the farthest from the route weight point. It creates neighbourhood by swapping
        farthest customers
        :param x: Solution class object
        :return:
        """
        farthest_customers = [util.get_farthest_customer(route) for route in x.routes]
        neighbourhood = []
        for i in range(len(farthest_customers)):
            for j in range(i + 1, len(farthest_customers)):
                neighbour = x.clone()
                # remove node from one route, add on rand index to other
                route1 = neighbour.routes[i]
                route1.remove_node(farthest_customers[i])
                #route1.add_node_at(farthest_customers[j], random.randint(0, len(route1.nodes)))
                route1.add_node_at_best(farthest_customers[j])
                checked = util.check_combination(route1.nodes)
                # combination is not feasible
                if not checked:
                    continue
                route1.update()

                route2 = neighbour.routes[j]
                route2.remove_node(farthest_customers[j])
                #route2.add_node_at(farthest_customers[i], random.randint(0, len(route2.nodes)))
                route2.add_node_at_best(farthest_customers[i])
                checked = util.check_combination(route2.nodes)
                # combination is not feasible
                if not checked:
                    continue
                route2.update()

                neighbour.update_cost()
                neighbourhood.append(neighbour)

        #swaping with nothing
        for i in range(len(farthest_customers)):
            neighbour = x.clone()
            route1 = neighbour.routes[i]
            route1.remove_node(farthest_customers[i])

            new_route = Route([farthest_customers[i]])
            checked = util.check_combination(new_route.get_nodes())
            if not checked:
                continue

            if not route1.nodes:
                del neighbour.routes[i]
            else:
                route1.update()
            new_route.update()

            neighbour.add_route(new_route)
            neighbour.update_cost()
            neighbourhood.append(neighbour)

        return neighbourhood
