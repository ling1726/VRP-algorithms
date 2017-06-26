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

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        return self.id

    def __repr__(self):
        return self.id
    def __eq__(self, other):
        if type(self) != type(other):
            return False
        else:
            return self.id.__eq__(other.id)
