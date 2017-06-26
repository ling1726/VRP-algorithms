from NB.methaheuristic.Neighbourhood import Neighbourhood
from NB.util import *
import copy
import random

class SwapCustomersInter(Neighbourhood):

    def generate_neighbourhood(self, x):
        """
        Generates neighbourhood of given solution x by swapping chargers from different routes. From each route it
        selects the customer which is the farthest from the route weight point. It creates neighbourhood by swapping
        farthest customers
        :param x: Solution class object
        :return:
        """
        farthest_customers = [x for route in x.routes get_farthest_customer(route)]

        for i in range(len(farthest_customers)):
            for j in range(j + 1,len(farthest_customers)):
                #not deep copy because you have to delete chargers
                neighbour = x.clone()
                #remove node from one route, add on rand index to other
                route1 = neighbour.routes[i]
                route1.remove_node(farthest_customers[i])
                route1.add_node_at(farthest_customers[j],random.randint(0, len(route1.nodes)))
                route1.update()

                route2 = neighbour[j]
                route2.remove_node(farthest_customers[j])
                route2.add_node_at(farthest_customers[i],random.randint(0, len(route2.nodes)))
                route2.update()

