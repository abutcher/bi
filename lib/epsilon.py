#!/opt/local/bin/python2.6

from arff import *
from util import *
from quadrant import *
from instance import *
from gridclus2 import *
from which2 import *

arff1 = Arff("data/nasa93-dem.arff")
arff2 = Arff("data/coc81-dem.arff")
dc = DataCollection(discretize(arff1.data+arff2.data, 7))
ic = InstanceCollection(dc)
ic.normalize_coordinates()
trainXY = log_y(log_x(deepcopy(ic.instances)))
quadrants = QuadrantTree(trainXY).leaves()
clusters = GRIDCLUS(quadrants)

print "here, E0, there, E1, E1/E0, P(there | r)"
for cluster in clusters:
    if len(cluster.datums()) > 16: # Not enough support
        neighbors = []
        for other_cluster in clusters:
            if cluster is not other_cluster:
                if cluster.is_neighbor(other_cluster):
                    neighbors.append(other_cluster)
        neighbors = sorted(neighbors, key=lambda c: c.cmedian())
        lowest_neighbor = neighbors[0]

        here = clusters.index(cluster)
        e0 = cluster.cmedian()
        there = clusters.index(lowest_neighbor)
        e1 = lowest_neighbor.cmedian()
        e1_e0 = e1 / e0

        best_rule = which2n(arff1.headers, cluster.datums())[0]

        num = 0
        for thisors in best_rule.ands:
            this_num = 0
            for value in thisors.values:
                l = [datum[arff1.headers.index(thisors.forr)] for datum in lowest_neighbor.datums()]
                this_num += l.count(value)
            num += this_num
        num = float(num)
        if e0 > e1:
            print "%d, %.2f, %d, %.2f, %.2f, %.2f" % (here, e0, there, e1, e1_e0, num/len(lowest_neighbor.datums()))
