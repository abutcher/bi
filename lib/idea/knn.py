from util import *

def kNearestNeighbors(instance, data, k=10):
    Neighbors = []
    # Find nighbors
    for i in range(k):
        try:
            Closest = closestto(instance,data)
            Neighbors.append(Closest)
            data.remove(Closest)
        except:
            # If we have fewer data points than k, break from the loop
            # with the neighbors we have.
            break
    # Add them back in case Python passes by reference
    for neighbor in Neighbors:
        data.append(neighbor)
    return Neighbors
