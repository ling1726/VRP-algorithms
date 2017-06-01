import NB.instance.instance as instance

def calculate_route_cost(route, start=instance.depot, end=instance.depot):
    cost = 0

    if not route:
        return cost

    cost += instance.getValDistanceMatrix(start, route[0])
    for i in range(len(route)-1):
        cost += instance.getValDistanceMatrix(route[i], route[i+1])
    cost += instance.getValDistanceMatrix(route[-1], end)
    return cost