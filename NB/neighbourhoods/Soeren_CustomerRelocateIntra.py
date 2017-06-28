import random

from NB import util
from NB.neighbourhoods.Neighbourhood import Neighbourhood

class CustomerRelocateIntra(Neighbourhood):

    def generate_neighbourhood(self, x):

        # random route and cutomer index
        x_clone = x.clone()

        rri = random.randint(0, len(x_clone.routes)-1)
        random_route_nodes = x_clone.routes[rri].get_nodes()
        rci = random.randint(0, len(random_route_nodes)-1)

        neighbourhood = []

        for i in range(len(random_route_nodes)):
            neighbour_removed = x.clone()

            random_route = neighbour_removed.routes[rri]
            move_node = random_route.get_nodes()[rci]
            random_route.remove_node(move_node)

            random_route.add_node_at(move_node, i)

            checked = util.make_fuel_consumption_feasible(random_route.nodes)
            # combination is not feasible
            if not checked:
                continue
            random_route.nodes = checked
            random_route.update()

            neighbour_removed.update_cost()
            neighbourhood.append(neighbour_removed)

        return neighbourhood

    def generate_neighbourhood(self, x):

        # random route and cutomer index
        x_clone = x.clone()

        rri = random.randint(0, len(x_clone.routes)-1)
        neighbourhood = []
        for route in x_clone.routes:
            rci = random.randint(0, len(route.get_nodes())-1)

            for i in range(len(route.get_nodes())):
                neighbour_removed = x.clone()

                route = neighbour_removed.routes[rri]
                move_node = route.get_nodes()[rci]
                route.remove_node(move_node)

                route.add_node_at(move_node, i)

                checked = util.make_fuel_consumption_feasible(route.nodes)
                # combination is not feasible
                if not checked:
                    continue
                route.nodes = checked
                route.update()

                neighbour_removed.update_cost()
                neighbourhood.append(neighbour_removed)

        return neighbourhood
