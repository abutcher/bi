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
from timer import *

ant = ["data/ant-1.3.arff", "data/ant-1.4.arff", "data/ant-1.5.arff", "data/ant-1.6.arff", "data/ant-1.7.arff"]
ivy = ["data/ivy-1.1.arff", "data/ivy-1.4.arff", "data/ivy-2.0.arff"]
jedit = ["data/jedit3.2.arff", "data/jedit4.0.arff", "data/jedit4.1.arff", "data/jedit4.2.arff", "data/jedit4.3.arff"]
lucene = ["data/lucene2.0.arff", "data/lucene2.2.arff", "data/lucene2.4.arff"]
poi = ["data/poi-1.5.arff", "data/poi-2.0.arff", "data/poi-2.5.arff", "data/poi-3.0.arff"]
tomcat = ["data/tomcat.arff"]
velocity = ["data/velocity1.4.arff", "data/velocity1.5.arff", "data/velocity1.6.arff"]
xalan = ["data/xalan2.4.arff", "data/xalan2.5.arff", "data/xalan2.6.arff", "data/xalan2.7.arff"]
xerces = ["data/xerces1.2.arff", "data/xerces1.3.arff", "data/xerces1.4.arff"]

files = ant + ivy + jedit + lucene + poi + tomcat + velocity + xalan + xerces
arffs = [Arff(file) for file in files]
files = sorted(files, key=lambda f: len(arffs[files.index(f)].data))

for f in files:
    a = Arff(f)
    a.data = discretize(a.data, 7)
    #s = "%d" % len(a.data)

    dc = DataCollection(discretize(a.data, 7))
    ic = InstanceCollection(dc)
    ic.normalize_coordinates()
    trainXY = log_y(log_x(deepcopy(ic.instances)))
    quadrants = QuadrantTree(trainXY).leaves()
    clusters = GRIDCLUS(quadrants)

    for cluster in filter(lambda c: len(c.datums()) > 20, clusters):
        s = "%d" % len(cluster.datums())
        with Timer(s):
            best_all_rule = which2n(a.headers, cluster.datums())
