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
from gaps import *

xalan = ["data/xalan/xalan2.4.arff", "data/xalan/xalan2.5.arff", "data/xalan/xalan2.6.arff", "data/xalan/xalan2.7.arff"]
jedit = ["data/jedit/jedit3.2.arff", "data/jedit/jedit4.0.arff", "data/jedit/jedit4.1.arff", "data/jedit/jedit4.2.arff"]
xerces = ["data/xerces/xerces1.2.arff", "data/xerces/xerces1.3.arff", "data/xerces/xerces1.4.arff"]
lucene = ["data/lucene/lucene2.0.arff", "data/lucene/lucene2.2.arff", "data/lucene/lucene2.4.arff"]
velocity = ["data/velocity/velocity1.4.arff", "data/velocity/velocity1.5.arff", "data/velocity/velocity1.6.arff"]

files = [xalan[-1], jedit[-1], xerces[-1], lucene[-1], velocity[-1]]

arffs = []
for f in files:
    arffs.append(Arff(f))
    #for of in files:
    #    if f is not of:
    #        arff = Arff([f, of])
    #        if arff not in arffs:
    #            arffs.append(arff)

#for i in range(len(files)):
#    arffs.append(Arff(files[0:i+1]))

arffs = list(set(arffs))
arffs = sorted(arffs, key=lambda a: len(a.data))

for a in arffs:
    a.data = remove_column(a.data, 0)
    a.headers.remove("dataset")

    a.data = remove_column(a.data, 0)
    a.headers.remove("name")

    if not a.numsets > 1:
        a.data = remove_column(a.data, 0)
        a.headers.remove("version")

    dc = DataCollection(discretize(a.data, 5))
    ic = InstanceCollection(dc)
    ic.normalize_coordinates()
    trainXY = log_y(log_x(deepcopy(ic.instances)))
    quadrants = QuadrantTree(trainXY).leaves()
    clusters = GRIDCLUS(quadrants)

    dall = deepcopy(dc.datums)

    """
    random.shuffle(dall, random.random)
    dall = remove_column(dall, 0)
    dall = remove_column(dall, 0)
    a.headers.remove("name")
    a.headers.remove("dataset")
    """

    raw = []
    # Dependent vars for all rows
    for datum in dall:
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
        if len(cluster.datums()) > 20 and cluster.neighbor_count(clusters) > 0:
            #print cluster.neighbor_count(clusters)
            best_cluster_rule = which2n(a.headers, cluster.datums())[0]
            cluster_rules.append((cluster, best_cluster_rule))

    local = []
    # Datums matching neighbor in local space
    for c in cluster_rules:
        here = c[0]
        rule = c[1]

        there =  most_feared(here, clusters)

        """
        neighbors = here.neighbors(clusters)
        neighbors = sorted(neighbors, key=lambda c: c.cmedian())
        there = neighbors[0]
        """
        if here.cmedian() > there.cmedian():
            for datum in there.datums():
                if rule.ruleMatch(a.headers, datum):
                    local.append(datum[-1])
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

    sigdiff = False
    if stats.mannwhitneyu(raw, local)[1] > 0.5:
        sigdiff = True

    print "\\parbox{0.6in}{%s (defects)}" % a.name
    print "\\begin{tabular}{|r|r|rr|}"
    print "\\multicolumn{4}{l}{} \\\\\\cline{3-4}"
    print "\\multicolumn{2}{c|}{~} & \\multicolumn{2}{c|}{treated}\\\\\\hline"

    if sigdiff:
        print "percentile & raw & global & local(*)\\\\\\hline"
    else:
        print "percentile & raw & global & local\\\\\\hline"
    try:
        rawn = [stats.scoreatpercentile(raw, 0), stats.scoreatpercentile(raw, 25), stats.scoreatpercentile(raw, 50), stats.scoreatpercentile(raw, 75), stats.scoreatpercentile(raw, 100)]
        globn = [stats.scoreatpercentile(glob, 0), stats.scoreatpercentile(glob, 25), stats.scoreatpercentile(glob, 50), stats.scoreatpercentile(glob, 75), stats.scoreatpercentile(glob, 100)]
        localn = [stats.scoreatpercentile(local, 0), stats.scoreatpercentile(local, 25), stats.scoreatpercentile(local, 50), stats.scoreatpercentile(local, 75), stats.scoreatpercentile(local, 100)]
        print "%.2f & %.2f & %.2f & %.2f \\\\" % (0, (100*((rawn[0]-rawn[0])/(rawn[4]-rawn[0]))), (100*((globn[0]-rawn[0])/(rawn[4]-rawn[0]))), (100*((localn[0]-rawn[0])/(rawn[4]-rawn[0]))))
        print "%.2f & %.2f & %.2f & %.2f \\\\" % (0.25, (100*((rawn[1]-rawn[0])/(rawn[4]-rawn[0]))), (100*((globn[1]-rawn[0])/(rawn[4]-rawn[0]))), (100*((localn[1]-rawn[0])/(rawn[4]-rawn[0]))))
        print "%.2f & %.2f & %.2f & %.2f \\\\" % (0.5, (100*((rawn[2]-rawn[0])/(rawn[4]-rawn[0]))), (100*((globn[2]-rawn[0])/(rawn[4]-rawn[0]))), (100*((localn[2]-rawn[0])/(rawn[4]-rawn[0]))))
        print "%.2f & %.2f & %.2f & %.2f \\\\" % (0.75, (100*((rawn[3]-rawn[0])/(rawn[4]-rawn[0]))), (100*((globn[3]-rawn[0])/(rawn[4]-rawn[0]))), (100*((localn[3]-rawn[0])/(rawn[4]-rawn[0]))))
        print "%.2f & %.2f & %.2f & %.2f \\\\ \\hline" % (1, (100*((rawn[4]-rawn[0])/(rawn[4]-rawn[0]))), (100*((globn[4]-rawn[0])/(rawn[4]-rawn[0]))), (100*((localn[4]-rawn[0])/(rawn[4]-rawn[0]))))
        print "75th-25th & %.2f & %.2f & %.2f \\\\ \\hline" % ( (100*((rawn[3]-rawn[0])/(rawn[4]-rawn[0])))-(100*((rawn[1]-rawn[0])/(rawn[4]-rawn[0]))), (100*((globn[3]-rawn[0])/(rawn[4]-rawn[0])))-(100*((globn[1]-rawn[0])/(rawn[4]-rawn[0]))), (100*((localn[3]-rawn[0])/(rawn[4]-rawn[0])))-(100*((localn[1]-rawn[0])/(rawn[4]-rawn[0]))))
    except:
        print "There are no local datums chosen..."
    print "\\end{tabular}"
    print "\\begin{tabular}{r@{~=~}l}"
    print "min&%d\\\\" % 0.0
    print "max&%d\\\\" % 100.0
    print "num datums & %d\\\\" % len(dall)
    print "\\end{tabular}"
    print ""
