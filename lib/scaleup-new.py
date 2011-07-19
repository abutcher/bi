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

xalan = ["data/xalan-2.4.arff", "data/xalan-2.5.arff", "data/xalan-2.6.arff", "data/xalan-2.7.arff"]
jedit = ["data/jedit-3.2.arff", "data/jedit-4.0.arff", "data/jedit-4.1.arff", "data/jedit-4.2.arff"]
xerces = ["data/xerces-1.2.arff", "data/xerces-1.3.arff", "data/xerces-1.4.arff"]
lucene = ["data/lucene-2.0.arff", "data/lucene-2.2.arff", "data/lucene-2.4.arff"]
velocity = ["data/velocity-1.4.arff", "data/velocity-1.5.arff", "data/velocity-1.6.arff"]

#files = [xalan[-1], jedit[-1], xerces[-1], lucene[-1], velocity[-1]]
files = velocity + lucene + jedit + xalan + xerces
#files = [xerces[0]]
#files = ["data/lucene-2.4.arff"]
#files = ["data/velocity-1.4.arff"]

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
#    a.data = remove_column(a.data, 0)
#    a.headers.remove("dataset")

    a.data = remove_column(a.data, 0)
    a.headers.remove("name")

    if not a.numsets > 1:
        a.data = remove_column(a.data, 0)
        a.headers.remove("version")

    dc = DataCollection(discretize(a.data, 6))
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
        if len(cluster.datums()) > 25:# and cluster.neighbor_count(clusters) > 0:
            best_cluster_rules = which2n(a.headers, cluster.datums())
            cluster_rules.append((cluster, best_cluster_rules))

    local = []
    # Datums matching neighbor in local space
    for c in cluster_rules:
        here = c[0]
        there =  most_feared(here, clusters)

        if here.cmedian() > there.cmedian():
            tmp = deepcopy(here)
            here = deepcopy(there)
            there = deepcopy(tmp)

        #neighbors = here.neighbors(clusters)
        #neighbors = sorted(neighbors, key=lambda c: c.cmedian(), reverse=True)
        #there = neighbors[0]

        combined = there.datums() + here.datums()
        rules = which2n(a.headers, combined)

        if here.cmedian() < there.cmedian():
            cnt = 0
            localc = []
            while not localc and cnt != len(rules) - 1:
                print "looping"
                localc = [d[-1] for d in there.datums() if rules[cnt].ruleMatch(a.headers, d)]
                #print len(localc)
                cnt += 1
            local += localc
            #for datum in there.datums():
            #   if rule.ruleMatch(a.headers, datum):
            #        print "appending local datum"
            #        local.append(datum[-1])

    print "Raw", len(dall)
    print "Global", len(glob)
    print "Local", len(local)

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


    print "CLUSTERS %d, %d > 20" % (len(clusters), len([c for c in clusters if len(c.datums()) > 20]))
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
