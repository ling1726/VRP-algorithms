from NB import instance

def calculate_route_cost(route):
    cost = 0
    cost += instance.getValDistanceMatrix(instance.depot, route[0])
    for i in range(len(route))-1:
        cost += instance.getValDistanceMatrix(route[i], route[i+1])
    cost += instance.getValDistanceMatrix(route[-1],instance.depot)
    return cost