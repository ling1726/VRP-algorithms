import instance.instance as inst
import copy
import sys

class SimpleNeighborhood(object):

    def __init__(self):
        pass
    # current should be a route object, so we can handle costs and so on
    def generate_neighbor(self, current):
        nxt = copy.deepcopy(current)
        #TODO
        return nxt

    def exchange(self, nxt):

