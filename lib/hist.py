#!/opt/local/bin/python2.6

import matplotlib
matplotlib.use('WXAgg')
import matplotlib.pyplot as plt
from arff import *

xalan = ["data/xalan-2.4.arff", "data/xalan-2.5.arff", "data/xalan-2.6.arff", "data/xalan-2.7.arff"]
jedit = ["data/jedit-3.2.arff", "data/jedit-4.0.arff", "data/jedit-4.1.arff", "data/jedit-4.2.arff"]
xerces = ["data/xerces-1.2.arff", "data/xerces-1.3.arff", "data/xerces-1.4.arff"]
lucene = ["data/lucene-2.0.arff", "data/lucene-2.2.arff", "data/lucene-2.4.arff"]
velocity = ["data/velocity-1.4.arff", "data/velocity-1.5.arff", "data/velocity-1.6.arff"]

files = velocity + lucene + jedit + xalan + xerces

for f in files:

    fig = plt.figure()
    ax = fig.add_subplot(111)

    a = Arff(f)
    c = [d[-1] for d in a.data]

    ax.hist(c, max(c))

    plt.savefig('hist/%s.png' % f)
