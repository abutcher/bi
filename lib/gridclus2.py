from cluster import *

def GRIDCLUS(quadrants, acceptance=0.4):

    tiles = []
    for quadrant in quadrants:
        tiles.append((quadrant.density(), quadrant))

    tiles = sorted(tiles, key=lambda tile: tile[0], reverse=True)

    clusters = []

    for tile in tiles:
        cluster = []
        starting_point = tile[0]
        neighbors = neighbor_search(tile, tiles, acceptance, starting_point)
        while(neighbors != []):
            for neighbor in neighbors:
                if neighbor in tiles:
                    tiles.remove(neighbor)
            neighbors.extend(neighbor_search(neighbors[0], tiles, acceptance, starting_point))
            cluster.append(neighbors[0])
            neighbors.remove(neighbors[0])
        if cluster != []:
            clusters.append(cluster)

    newclusters = []
    for cluster in clusters:
        newcluster = Cluster()
        for tile in cluster:
            newcluster.add_quadrant(tile[1])
        newclusters.append(newcluster)

    for cluster in newclusters:
        if len(cluster.quadrants) == 0:
            newclusters.remove(cluster)

    return newclusters

def adjacent(a, b):
    if ((a.xmin == b.xmax) or (a.xmax == b.xmin)) or ((a.ymin == b.ymax) or (a.ymax == b.ymin)):
        return True
    else:
        return False        

def should_mark(a, b, acceptance):
    if a != 0 and b != 0 and ((acceptance > (abs(a - b)/a)) or (acceptance > (abs(a-b)/b))):
        return True
    else:
        return False

def neighbor_search(tile, tiles, acceptance, starting_point):
    neighbors = []
    for othertile in tiles:
        if (othertile != tile) and adjacent(tile[1], othertile[1]) and should_mark(starting_point, othertile[0], acceptance):
            neighbors.append(othertile)
    return neighbors
