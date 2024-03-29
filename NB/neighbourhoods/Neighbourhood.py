import random
import copy

class Neighbourhood:

    def generate_neighbourhood(self, x):
        """
        Abstract method for strategy pattern
        :param x: solution class object
        :return:
        """
        pass

    def generate_random_solution(self, x):
        """
        Abstract method for strategy pattern
        :param x: solution class object
        :return:
        """
        neighbourhood = self.generate_neighbourhood(x)
        if neighbourhood:
            return neighbourhood[random.randint(0, len(neighbourhood)-1)]
        else: 
            return copy.deepcopy(x)
