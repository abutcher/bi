#!/opt/local/bin/python2.6
from arff import *
from util import *
from quadrant import *
from instance import *
from gridclus2 import *
from which2 import *
from bore2 import *

arff1 = Arff("data/jedit4.0.arff")
#arff2 = Arff("data/coc81-dem.arff")
#datar = arff1.data+arff2.data
datar = arff1.data
#datar = remove_column(datar, -1)
#datar = remove_column(datar,-1)
#arff1.headers = arff1.headers[0:-2]
dc = DataCollection(discretize(datar, 7))
ic = InstanceCollection(dc)
print "EAST: ", ic.east
print "WEST:, ", ic.west
ic.normalize_coordinates()
trainXY = log_y(log_x(deepcopy(ic.instances)))
quadrants = QuadrantTree(trainXY).leaves()
clusters = GRIDCLUS(quadrants)

dall = dc.datums
rall = which2n(arff1.headers, dall)
cluster_rules = []

for cluster in clusters:
    if len(cluster.datums()) < 20:
        cluster_rules.append([])
    else:
        cluster_rules.append(which2n(arff1.headers, cluster.datums()))
    #print "C%d done, size=%d." % (clusters.index(cluster), len(cluster.datums()))

print "ALL BEST RULE"
print rall[0].describe()
print ""
for cluster in clusters:
    print "Cluster %d" % clusters.index(cluster)
    if len(cluster.datums()) < 20:
        print "Length less than 20."
    else:
        cluster_rules[clusters.index(cluster)] = sorted(cluster_rules[clusters.index(cluster)], key=lambda r: r.score, reverse=True)
        print cluster_rules[clusters.index(cluster)][0].describe()
print ""
