import NB.util as util
from NB.Solution.route import Route
from NB.neighbourhoods.Neighbourhood import Neighbourhood


class SwapCustomersInter(Neighbourhood):
    def __init__(self, selection_function):
        self.selection_function = selection_function

    def generate_neighbourhood(self, x):
        """
        Generates neighbourhood of given solution x by swapping chargers from different routes. From each route it
        selects the customer using selection function. It creates neighbourhood by swapping customers
        :param x: Solution class object
        :return:
        """
        selected_customers = [self.selection_function(route) for route in x.routes]
        neighbourhood = []
        for i in range(len(selected_customers)):
            for j in range(i + 1, len(selected_customers)):
                neighbour = x.clone()
                # remove node from one route, add on rand index to other
                route1 = neighbour.routes[i]
                route1 = Route(route1.strip_chargers())
                route1.remove_node(selected_customers[i])

                route2 = neighbour.routes[j]
                route2 = Route(route2.strip_chargers())
                route2.remove_node(selected_customers[j])

                for index_route1 in range(len(route1.nodes) + 1):
                    for index_route2 in range(len(route2.nodes) + 1):
                        new_neighbour = neighbour.clone()
                        route1 = new_neighbour.routes[i]
                        route2 = new_neighbour.routes[j]
                        route1.add_node_at(selected_customers[j], index_route1)
                        # route1.add_node_at_best(farthest_customers[j])
                        checked = util.check_combination(route1.nodes)
                        # combination is not feasible
                        if not checked:
                            continue
                        route1.nodes = checked
                        route1.update()

                        route2.add_node_at(selected_customers[i], index_route2)
                        # route2.add_node_at_best(farthest_customers[i])
                        checked = util.check_combination(route2.nodes)
                        # combination is not feasible
                        if not checked:
                            continue
                        route2.nodes = checked
                        route2.update()
                        print("managed to do swap", "neigbourhood 3")
                        new_neighbour.update_cost()
                        neighbourhood.append(new_neighbour)
        return neighbourhood

