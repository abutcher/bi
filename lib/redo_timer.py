#!/opt/local/bin/python2.6

from arff import *
from instance import *
from util import *
from discretize import *

xalan = ["data/xalan-2.4.arff", "data/xalan-2.5.arff", "data/xalan-2.6.arff", "data/xalan-2.7.arff"]
jedit = ["data/jedit-3.2.arff", "data/jedit-4.0.arff", "data/jedit-4.1.arff", "data/jedit-4.2.arff"]
xerces = ["data/xerces-1.2.arff", "data/xerces-1.3.arff", "data/xerces-1.4.arff"]
lucene = ["data/lucene-2.0.arff", "data/lucene-2.2.arff", "data/lucene-2.4.arff"]
velocity = ["data/velocity-1.4.arff", "data/velocity-1.5.arff", "data/velocity-1.6.arff"]

#files = [xalan[-1], jedit[-1], xerces[-1], lucene[-1], velocity[-1]]
files = velocity + lucene + jedit + xalan + xerces
#files = [xerces[0]]
#files = ["data/coc81-dem.arff", "data/nasa93-dem.arff"]
#files = ["data/china.arff"]

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

#    a.data = remove_column(a.data, 0)
#    a.headers.remove("name")

#    if not a.numsets > 1:
#        a.data = remove_column(a.data, 0)
#        a.headers.remove("version")
    print a.name,",", len(a.data)

    dc = DataCollection(discretize(a.data, 6))
    ic = InstanceCollection(dc)
