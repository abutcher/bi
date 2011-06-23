#!/usr/bin/env python

from arff import *
from util import *
from quadrant import *
from instance import *
from gridclus2 import *
from discretize import *

def gaps(c, o):
    d = 0.0
    for cq in c.quadrants:
        for oq in o.quadrants:
            d += ( float(len(cq.datums())) / float(len(c.datums())) ) * distance(cq.center(), oq.center())
    return d

def most_feared(cluster, other_clusters):
    score = 0.0
    feared = None
    for other_cluster in other_clusters if other_cluster != cluster:
        if other_cluster.cmedian()/gaps(cluster, other_cluster) > score:
            Feared = other_cluster
    return other_cluster

if __name__=="__main__":
    arff = Arff("data/china.arff")
    dc = DataCollection(discretize(arff.data, 7))
    ic = InstanceCollection(dc)
    ic.normalize_coordinates()
    trainXY = log_y(log_x(ic.instances))
    quadrants = QuadrantTree(trainXY).leaves()
    clusters = GRIDCLUS(quadrants)
    print gaps(clusters[0], clusters[-1])
