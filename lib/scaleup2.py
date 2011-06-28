#!/opt/local/bin/python2.6

from arff import *
from util import *
from quadrant import *
from instance import *
from gridclus2 import *
from which2 import *
from scipy import stats
from copy import deepcopy
import random
import sys

ant = ["data/ant-1.3.arff", "data/ant-1.4.arff", "data/ant-1.5.arff", "data/ant-1.6.arff", "data/ant-1.7.arff"]
ivy = ["data/ivy-1.1.arff", "data/ivy-1.4.arff", "data/ivy-2.0.arff"]
jedit = ["data/jedit3.2.arff", "data/jedit4.0.arff", "data/jedit4.1.arff", "data/jedit4.2.arff", "data/jedit4.3.arff"]
lucene = ["data/lucene2.0.arff", "data/lucene2.2.arff", "data/lucene2.4.arff"]
poi = ["data/poi-1.5.arff", "data/poi-2.0.arff", "data/poi-2.5.arff", "data/poi-3.0.arff"]
tomcat = ["data/tomcat.arff"]
velocity = ["data/velocity1.4.arff", "data/velocity1.5.arff", "data/velocity1.6.arff"]
xalan = ["data/xalan2.4.arff", "data/xalan2.5.arff", "data/xalan2.6.arff", "data/xalan2.7.arff"]
xerces = ["data/xerces1.2.arff", "data/xerces1.3.arff", "data/xerces1.4.arff"]

files = jedit + xerces + lucene + velocity + ant + poi + ivy

arffs = [Arff(file) for file in files]
files = sorted(files, key=lambda f: len(arffs[files.index(f)].data))

braw = []
bglob = []
blocal = []
bcross = []

for i in range(8):
    unknown = random_element(files)
    other_sets = []
    while len(other_sets) < 2:
        set = random_element(files)
        if len(other_sets) == 0:
            other_sets.append(set)
        elif set not in other_sets and set != unknown and set.split('/')[1].split('.')[0] not in [s.split('/')[1].split('.')[0] for s in other_sets]:
            other_sets.append(set)

    u = Arff(unknown)
    k = Arff(unknown)
    for datum in u.data:
        datum[-1] = '?'
    a = Arff(other_sets)
    a.name += u.name
    
    """
    a.data = remove_column(a.data, 0)
    a.headers.remove("dataset")

    a.data = remove_column(a.data, 0)
    a.headers.remove("name")

    if not a.numsets > 1:
        a.data = remove_column(a.data, 0)
        a.headers.remove("version")
    """

    dc = DataCollection(discretize(u.data+a.data, 7))
    kc = DataCollection(discretize(k.data+a.data, 7))
    ic = InstanceCollection(dc)
    ic.normalize_coordinates()
    trainXY = log_y(log_x(deepcopy(ic.instances)))
    quadrants = QuadrantTree(trainXY).leaves()
    clusters = GRIDCLUS(quadrants)
    dall = deepcopy(dc.datums)

    raw = []
    # Dependent vars for all rows
    for datum in u.data+a.data:
        raw.append(datum[-1])

    best_all_rule = which2n(a.headers, dall)[0]
    #print best_all_rule.describe()
    
    glob = []
    # Dependent vars matching best all rule
    for datum in dall:
        if best_all_rule.ruleMatch(a.headers, datum):
            glob.append(datum[-1])

    cluster_rules = []
    for cluster in clusters:
        if len(cluster.datums()) > 20 and cluster.neighbor_count(clusters) > 0 and len(filter(lambda d: d[-1] != '?', cluster.datums())) > 20:
            best_cluster_rule = which2n(a.headers, cluster.datums())[0]
            cluster_rules.append((cluster, best_cluster_rule))

    local = []
    # Datums matching neighbor in local space
    for c in cluster_rules:
        here = c[0]
        rule = c[1]
        neighbors = here.neighbors(clusters)
        neighbors = sorted(neighbors, key=lambda c: c.cmedian())
        there = neighbors[0]
        if here.cmedian() > there.cmedian():
            for datum in there.datums():
                if rule.ruleMatch(a.headers, datum):
                    local.append(datum[-1])

    localu = []
    # Datums matching neighbor in local space that are unknown
    for c in cluster_rules:
        here = c[0]
        rule = c[1]
        neighbors = here.neighbors(clusters)
        neighbors = sorted(neighbors, key=lambda c: c.cmedian())
        there = neighbors[0]
        if here.cmedian() > there.cmedian():
            for datum in filter(lambda d: d[-1] == '?', there.datums()):
                if rule.ruleMatch(a.headers, datum):
                    this = None
                    for k in kc.backup:
                        if datum[0:-2] == k[0:-2]:
                            this = k
                    localu.append(this[-1])

    raw = filter(lambda l: l != '?', raw)    
    local = filter(lambda l: l != '?', local)
    glob = filter(lambda g: g != '?', glob)

    """
    all_local = []
    # All rules matching the local clusters
    for cluster in clusters:
        neighbors = []
        for other_cluster in clusters:
            if cluster is not other_cluster:
                if cluster.is_neighbor(other_cluster):
                    neighbors.append(other_cluster)
        neighbors = sorted(neighbors, key=lambda c: c.cmedian())
        print len(neighbors)
        there = neighbors[0]
        for datum in cluster.datums() + there.datums():
            if best_all_rule.ruleMatch(a.headers, datum):
                all_local.append(datum[-1])
    """
    
    if stats.mannwhitneyu(raw, glob)[1] > 0.05:
        print "Raw is not equivalent to global."
    if stats.mannwhitneyu(glob, local)[1] > 0.05:
        print "Global is not equivalent to local."
    if stats.mannwhitneyu(local, localu)[1] > 0.05:
        print "Local is not equivalent to cross."        
        
    print "\\parbox{0.6in}{%s (defects)}" % a.name
    print "\\begin{tabular}{|r|r|rr|r|}"
    print "\\multicolumn{4}{l}{} \\\\\\cline{3-4}"
    print "\\multicolumn{2}{c|}{~} & \\multicolumn{2}{c|}{treated}\\\\\\hline"

    print "percentile & raw & global & local & cross\\\\\\hline"
        
    try:
        rawn = [stats.scoreatpercentile(raw, 0), stats.scoreatpercentile(raw, 25), stats.scoreatpercentile(raw, 50), stats.scoreatpercentile(raw, 75), stats.scoreatpercentile(raw, 100)]
        globn = [stats.scoreatpercentile(glob, 0), stats.scoreatpercentile(glob, 25), stats.scoreatpercentile(glob, 50), stats.scoreatpercentile(glob, 75), stats.scoreatpercentile(glob, 100)]
        localn = [stats.scoreatpercentile(local, 0), stats.scoreatpercentile(local, 25), stats.scoreatpercentile(local, 50), stats.scoreatpercentile(local, 75), stats.scoreatpercentile(local, 100)]
        localun = [stats.scoreatpercentile(localu, 0), stats.scoreatpercentile(localu, 25), stats.scoreatpercentile(localu, 50), stats.scoreatpercentile(localu, 75), stats.scoreatpercentile(localu, 100)]
        print "%.2f & %.2f & %.2f & %.2f & %.2f\\\\" % (0, (100*((rawn[0]-rawn[0])/(rawn[4]-rawn[0]))), (100*((globn[0]-rawn[0])/(rawn[4]-rawn[0]))), (100*((localn[0]-rawn[0])/(rawn[4]-rawn[0]))), (100*((localun[0]-rawn[0])/(rawn[4]-rawn[0]))))
        print "%.2f & %.2f & %.2f & %.2f & %.2f \\\\" % (0.25, (100*((rawn[1]-rawn[0])/(rawn[4]-rawn[0]))), (100*((globn[1]-rawn[0])/(rawn[4]-rawn[0]))), (100*((localn[1]-rawn[0])/(rawn[4]-rawn[0]))), (100*((localun[1]-rawn[0])/(rawn[4]-rawn[0]))))
        print "%.2f & %.2f & %.2f & %.2f & %.2f \\\\" % (0.5, (100*((rawn[2]-rawn[0])/(rawn[4]-rawn[0]))), (100*((globn[2]-rawn[0])/(rawn[4]-rawn[0]))), (100*((localn[2]-rawn[0])/(rawn[4]-rawn[0]))), (100*((localun[2]-rawn[0])/(rawn[4]-rawn[0]))))
        print "%.2f & %.2f & %.2f & %.2f & %.2f \\\\" % (0.75, (100*((rawn[3]-rawn[0])/(rawn[4]-rawn[0]))), (100*((globn[3]-rawn[0])/(rawn[4]-rawn[0]))), (100*((localn[3]-rawn[0])/(rawn[4]-rawn[0]))), (100*((localun[3]-rawn[0])/(rawn[4]-rawn[0]))))
        print "%.2f & %.2f & %.2f & %.2f & %.2f \\\\ \\hline" % (1, (100*((rawn[4]-rawn[0])/(rawn[4]-rawn[0]))), (100*((globn[4]-rawn[0])/(rawn[4]-rawn[0]))), (100*((localn[4]-rawn[0])/(rawn[4]-rawn[0]))), (100*((localun[4]-rawn[0])/(rawn[4]-rawn[0]))))
        print "75th-25th & %.2f & %.2f & %.2f & %.2f \\\\ \\hline" % ( (100*((rawn[3]-rawn[0])/(rawn[4]-rawn[0])))-(100*((rawn[1]-rawn[0])/(rawn[4]-rawn[0]))), (100*((globn[3]-rawn[0])/(rawn[4]-rawn[0])))-(100*((globn[1]-rawn[0])/(rawn[4]-rawn[0]))), (100*((localn[3]-rawn[0])/(rawn[4]-rawn[0])))-(100*((localn[1]-rawn[0])/(rawn[4]-rawn[0]))), (100*((localun[3]-rawn[0])/(rawn[4]-rawn[0])))-(100*((localun[1]-rawn[0])/(rawn[4]-rawn[0]))))
    except:
        print "There are no datums chosen somewhere..."
    print "\\end{tabular}"
    print "\\begin{tabular}{r@{~=~}l}"
    print "min&%d\\\\" % 0.0
    print "max&%d\\\\" % 100.0
    print "num datums & %d\\\\" % len(dall)
    print "\\end{tabular}"
    print ""

    braw += raw
    bglob += glob
    blocal += local
    bcross += localu


if stats.mannwhitneyu(braw, bglob)[1] > 0.05:
    print "BRaw is not equivalent to bglobal."
if stats.mannwhitneyu(bglob, blocal)[1] > 0.05:
    print "BGlobal is not equivalent to blocal."
if stats.mannwhitneyu(blocal, bcross)[1] > 0.05:
    print "BLocal is not equivalent to bcross."        
