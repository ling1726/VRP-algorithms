from NB import instance

def calculate_route_cost(route):
    cost = 0
    cost += instance._distanceMatrix.get(('S0', route[0]))
    for i in range(len(route))-1:
        cost += instance._distanceMatrix.get(route[i], route[i+1])
    cost += instance._distanceMatrix.get((route[-1], 'S0'))
    return cost