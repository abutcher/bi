#!/opt/local/bin/python2.6

from arff import *
from util import *
from quadrant import *
from instance import *
from gridclus2 import *
from which2 import *
from scipy import stats

arff1 = Arff("data/xalan2.7.arff")
#arff2 = Arff("data/coc81-dem.arff")
datar = arff1.data
#datar = remove_column(datar, -1)
#datar = remove_column(datar,-1)
#arff1.headers = arff1.headers[0:-2]
dc = DataCollection(discretize(datar, 7))
ic = InstanceCollection(dc)
ic.normalize_coordinates()
trainXY = log_y(log_x(deepcopy(ic.instances)))
quadrants = QuadrantTree(trainXY).leaves()
clusters = GRIDCLUS(quadrants)

dall = dc.datums

raw = []
print "Dependent vars for all rows"
for datum in dall:
    print datum[-1]
    raw.append(datum[-1])
print ""

support20 = []
print "Dependent vars for all clusters with more than 20 support"
for cluster in clusters:
    if len(cluster.datums()) > 20:
        for datum in cluster.datums():
            print datum[-1]
            support20.append(datum[-1])
best_all_rule = which2n(arff1.headers, dall)[0]

glob = []
print "Dependent vars matching best all rule"
for datum in dall:
    if best_all_rule.ruleMatch(arff1.headers, datum):
        print datum[-1]
        glob.append(datum[-1])
print ""

cluster_rules = []
for cluster in clusters:
    if len(cluster.datums()) > 20:
        best_cluster_rule = which2n(arff1.headers, cluster.datums())[0]
        cluster_rules.append((cluster, best_cluster_rule))

local = []
print "Datums matching neighbor in local space"
for c in cluster_rules:
    here = c[0]
    rule = c[1]
    neighbors = []
    for other_cluster in clusters:
        if here is not other_cluster:
            if here.is_neighbor(other_cluster):
                neighbors.append(other_cluster)
    neighbors = sorted(neighbors, key=lambda c: c.cmedian())
    there = neighbors[0]
    if here.cmedian() > there.cmedian():
        for datum in there.datums():
            if rule.ruleMatch(arff1.headers, datum):
                print datum[-1]
                local.append(datum[-1])

all_local = []
print "All rules matching the local clusters"
for cluster in clusters:
    neighbors = []
    for other_cluster in clusters:
        if cluster is not other_cluster:
            if cluster.is_neighbor(other_cluster):
                neighbors.append(other_cluster)
    neighbors = sorted(neighbors, key=lambda c: c.cmedian())    
    there = neighbors[0]
    for datum in cluster.datums() + there.datums():
        if best_all_rule.ruleMatch(arff1.headers, datum):
            print datum[-1]
            all_local.append(datum[-1])

print stats.mannwhitneyu(raw, local)[1]
if stats.mannwhitneyu(raw, local)[1] > 0.5:
    print "RAW IS SIGNIFICANTLY DIFFERENT FROM LOCAL"
    
