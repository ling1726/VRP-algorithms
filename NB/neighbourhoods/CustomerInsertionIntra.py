import random

import NB.util as util
from NB.Solution.route import Route
from NB.neighbourhoods.Neighbourhood import Neighbourhood


class CustomerInsertionIntra(Neighbourhood):
    def generate_neighbourhood(self, x):
        """
        Picks customer in route at random and inserts it in every slot in route
        :param x:Solution class object
        :return:
        """
        neighbourhood = []
        for i in range(len(x.routes)):
            neighbour = x.clone()
            route_removed_customer = neighbour.routes[i]
            # pick random cutomer
            route_removed_customer = Route(route_removed_customer.strip_chargers())
            neighbour.routes[i] = route_removed_customer
            customer = route_removed_customer.nodes[random.randint(0, len(route_removed_customer.nodes)- 1)]
            # remove customer from the route
            route_removed_customer.remove_node(customer)

            # insert it in every slot in the route
            for j in range(len(neighbour.routes[i].nodes)):
                neighbour_inserted = neighbour.clone()
                new_route = neighbour_inserted.routes[i]
                new_route.add_node_at(customer, j)
                checked = util.check_combination(new_route.nodes)
                if checked:
                    new_route.nodes = checked
                    new_route.update()
                    neighbour_inserted.update_cost()
                    neighbourhood.append(neighbour_inserted)
                    print("managed insertion INTRA", "neigbourhood 1")

        return neighbourhood
