import logging
import math

from LA.charger import Charger
from LA.customer import Customer

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
    parsed = False


# parse the set file name
def parse():
    global nodes, customers, chargers, parsed, averageVelocity, fuelCapacity, loadCapacity, inverseFuellingRate, fuelConsumptionRate
    if not filename: raise Exception('you are trying to parse before setting the filename!')
    reset_data()

    with open(filename, 'r') as infile:
        for line in infile:
            if line.startswith("StingID"): continue  # skip first line or empty line
            tokens = line.split()
            if len(tokens) == 0: continue
            if tokens[1] == 'f' or tokens[1] == 'c':
                node = None
                if tokens[1] == 'f':
                    node = Charger()
                else:
                    node = Customer()

                node.id = tokens[0]
                node.x = tokens[2]
                node.y = tokens[3]
                node.demand = tokens[4]
                node.windowStart = tokens[5]
                node.windowEnd = tokens[6]
                node.serviceTime = tokens[7]

                nodes[node.id] = node  # add a new node
                if tokens[1] == 'f':
                    chargers[node.id] = node
                else:
                    customers[node.id] = node

            if tokens[0] == 'Q': fuelCapacity = float(tokens[5].strip('/'))
            if tokens[0] == 'C': loadCapacity = float(tokens[4].strip('/'))
            if tokens[0] == 'r': fuelConsumptionRate = float(tokens[4].strip('/'))
            if tokens[0] == 'g': inverseFuellingRate = float(tokens[4].strip('/'))
            if tokens[0] == 'v': averageVelocity = float(tokens[3].strip('/'))

    parsed = True  # set parsed status as true
    fillDistanceMatrix()

def getValDistanceMatrix(node1, node2):
    return _distanceMatrix[(min(node1.id, node2.id),max(node1.id,node2.id))]


def putDistanceMatrix(node1, node2, value):
    _distanceMatrix[(min(node1.id, node2.id),max(node1.id,node2.id))] = value


def fillDistanceMatrix():
    other_nodes = set(nodes)
    for node1 in nodes:
        other_nodes.remove(node1)
        for node2 in other_nodes:
            putDistanceMatrix(node1, node2, math.hypot(node1.x - node2.x, node1.y - node2.y))
