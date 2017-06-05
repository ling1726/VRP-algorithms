import logging
import math

from instance.charger import Charger
from instance.customer import Customer
#from charger import Charger #COMMENT OUT ABOVE, UNCOMMENT THESE TWO FOR SEQINS TO WORK
#from customer import Customer

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# All nodes
nodes = {}

# Only customer nodes
customers = {}

# Only charger nodes
chargers = {}
# filename used for parsing
filename = ''
# to know if instance has been parsed
parsed = False
# key is (id1, id2)
adjacencyMatrix = {}

_distanceMatrix = {}

# the depot
depot = None

fuelCapacity = 0.0
loadCapacity = 0.0
fuelConsumptionRate = 0.0
inverseFuellingRate = 0.0
averageVelocity = 0.0


# set file name for instance
def setFileName(fileName):
    global filename, parsed
    filename = '../data/instances/' + fileName
    logger.info('filename has been set to ' + fileName)
    parsed = False


def reset_data():
    global nodes, chargers, customers, parsed, adjacencyMatrix, _distanceMatrix
    nodes.clear()
    chargers.clear()
    customers.clear()
    adjacencyMatrix.clear()
    _distanceMatrix.clear()
    depot = None
    parsed = False


# parse the set file name
def parse():
    global nodes, customers, chargers, parsed, averageVelocity, fuelCapacity, loadCapacity, inverseFuellingRate, fuelConsumptionRate, depot 
    if not filename: raise Exception('you are trying to parse before setting the filename!')
    reset_data()

    with open(filename, 'r') as infile:
        for line in infile:
            if line.startswith("StingID"): continue  # skip first line or empty line
            tokens = line.split()
            if len(tokens) == 0: continue
            if tokens[1] == 'f' or tokens[1] == 'c' or tokens[1] == 'd':
                node = None
                if tokens[1] == 'f':
                    node = Charger()
                elif tokens[1] == 'd':
                    node = Charger()
                else:
                    node = Customer()
                """
                    Convert node entries to floats and ints here.
                """
                node.id = tokens[0]
                node.x = float(tokens[2])
                node.y = float(tokens[3])
                node.demand = float(tokens[4])
                node.windowStart = float(tokens[5])
                node.windowEnd = float(tokens[6])
                node.serviceTime = float(tokens[7])

                nodes[node.id] = node  # add a new node
                if tokens[1] == 'f':
                    node.demand = 0
                    node.windowStart = 0
                    node.windowEnd = 1000000000
                    chargers[node.id] = node
                elif tokens[1] == 'd':
                    depot = node
                else:
                    customers[node.id] = node

            if tokens[0] == 'Q': fuelCapacity = float(tokens[5].strip('/'))
            if tokens[0] == 'C': loadCapacity = float(tokens[4].strip('/'))
            if tokens[0] == 'r': fuelConsumptionRate = float(tokens[4].strip('/'))
            if tokens[0] == 'g': inverseFuellingRate = float(tokens[4].strip('/'))
            if tokens[0] == 'v': averageVelocity = float(tokens[3].strip('/'))

    parsed = True  # set parsed status as true
    fillDistanceMatrix()

"""
The min/max is there to avoid redundant information due to the arc symmetry?
Also is a dict more efficient than 2-dim numpy array or Python list of lists?
A dict seems less intuitive and more restrictive due to its unordered nature.
"""
def getValDistanceMatrix(node1, node2):
    if node1.id == node2.id:
        return 0
    return _distanceMatrix[(node1.id,node2.id)]


def putDistanceMatrix(node1, node2, value):
    _distanceMatrix[(node1.id, node2.id)] = value
    _distanceMatrix[(node2.id, node1.id)] = value


def fillDistanceMatrix():
    other_nodes = set(nodes)

    for node1 in nodes:
        other_nodes.remove(node1)
        for node2 in other_nodes:
            """
            node1 and node2 are strings not Node objects. Dict lookup is required.
            """
            Node1 = nodes[node1]
            Node2 = nodes[node2]
            """
            x and y are stored as strings, must be converted to floats to do subtraction.
            """
            putDistanceMatrix(Node1, Node2, math.hypot(float(Node1.x) - float(Node2.x), float(Node1.y) - float(Node2.y)))


