#!/opt/local/bin/python2.6

from arff import *
from util import *
from quadrant import *
from instance import *
from gridclus2 import *
from which2 import *
from bore2 import *

arff1 = Arff("data/nasa93-dem.arff")
arff2 = Arff("data/coc81-dem.arff")
datar = arff1.data+arff2.data
datar = remove_column(datar, -1)
datar = remove_column(datar,-1)
print len(datar)
arff1.headers = arff1.headers[0:-2]
dc = DataCollection(discretize(datar, 7))
ic = InstanceCollection(dc)
ic.normalize_coordinates()
trainXY = log_y(log_x(deepcopy(ic.instances)))
quadrants = QuadrantTree(trainXY).leaves()
clusters = GRIDCLUS(quadrants)

dall = dc.datums
rall = which2n(arff1.headers, dall)
print "ALL done."
cluster_rules = []

for cluster in clusters:
    print len(cluster.datums())
    if len(cluster.datums()) < 20:
        cluster_rules.append([])
    else:
        cluster_rules.append(which2n(arff1.headers, cluster.datums()))
    print "C%d done, size=%d." % (clusters.index(cluster), len(cluster.datums()))
    
grid = {}
for header in arff1.headers[0:-1]:
    for item in list(set(transpose(dall)[arff1.headers.index(header)])):
        grid[(header, item)] = []

for rule in rall[0:19]:
    for thisors in rule.ands:
        for value in thisors.values:
            if "ALL" not in grid[(thisors.forr, value)]:
                grid[(thisors.forr, value)].append("ALL")

for crules in cluster_rules:
    print "Cluster %d", cluster_rules.index(crules)
    for rule in crules[0:19]:
        print rule.describe()
        for thisors in rule.ands:
            for value in thisors.values:
                if "C%d" % cluster_rules.index(crules) not in grid[(thisors.forr, value)]:
                    grid[(thisors.forr, value)].append("C%d" % cluster_rules.index(crules))

for derp in grid:
    print derp, grid[derp]
