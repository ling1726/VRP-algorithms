# This class SHOULD NEVER be instantiated
# BUT logic common to both types of nodes can be placed here e.g. distance
from math import atan2, degrees

class Node(object):
    def __init__(self):
        self.id = ''
        self.x = 0.0
        self.y = 0.0
        self.demand = 0.0
        self.serviceTime = 0.0
        self.windowStart = 0.0
        self.windowEnd = 0.0
        self.angle = 0.0

    def __hash__(self):
        return hash(self.id)

    def setAngleFromOrigin(self):
        self.angle =  degrees(atan2(self.y, self.x))
        if self.angle < 0: self.angle += 360        

    def translateByDepot(self, depot):
        self.x -= depot.x
        self.y -= depot.y

    def __str__(self):
        return self.id
