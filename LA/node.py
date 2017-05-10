# This class SHOULD NEVER be instantiated
# BUT logic common to both types of nodes can be placed here e.g. distance
class Node(object):
    def __init__(self):
        self.id = ''
        self.x = 0.0
        self.y = 0.0
        self.demand = 0.0
        self.serviceTime = 0.0
        self.windowStart = 0.0
        self.windowEnd = 0.0

