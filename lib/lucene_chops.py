#!/opt/local/bin/python2.6

from arff import *
from instance import *
from quadrant import *
from util import *
from copy import deepcopy
from gridclus2 import *
from discretize import *

def main():
    arff = Arff("data/lucene2.4.arff")
    first_splits = [[] for i in range(5)]

    for datum in arff.data:
        if datum[arff.headers.index('#bug')] == 0.0:
            first_splits[0].append(datum)
        elif datum[arff.headers.index('#bug')] == 1.0:
            first_splits[1].append(datum)
        elif datum[arff.headers.index('#bug')] == 2.0:
            first_splits[2].append(datum)
        elif datum[arff.headers.index('#bug')] == 3.0:
            first_splits[3].append(datum)
        elif datum[arff.headers.index('#bug')] == 4.0:
            first_splits[4].append(datum)            

    disc = discretize(arff.data)
    dc = DataCollection(disc)
    ic = InstanceCollection(dc)
    ic.normalize_coordinates()

    trainXY = log_y(log_x(deepcopy(ic.instances)))
    quadrants = QuadrantTree(trainXY).leaves()
    clusters = GRIDCLUS(quadrants)

    for cluster in clusters:
        print "C: ", len(cluster.datums())

    clusters_orig = []
    for cluster in clusters:
        l = []
        for datum in cluster.datums():
            l.append(arff.data[disc.index(datum)])
        clusters_orig.append(l)
        
    print len(clusters_orig), len(first_splits)
        
    result = [[] for i in range(len(clusters_orig))]
        
    for i in range(len(clusters_orig)):
        for j in range(len(first_splits)):
            sumt = 0.0
            for k in range(len(clusters_orig[i])):
                if clusters_orig[i][k] in first_splits[j]:
                    sumt += 1.0
            result[i].append(sumt / (len(clusters_orig[i]) + len(first_splits[j])))

    for r in result:
        for c in r:
            print "%.2f" % c, ",",
        print "\n"

if __name__ == "__main__":
    main()
