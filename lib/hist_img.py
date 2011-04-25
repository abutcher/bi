#!/opt/local/bin/python2.6

import matplotlib
matplotlib.use('WXagg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import numpy as np
from arff import *
from util import *
from quadrant import *
from instance import *
from gridclus2 import *

arff = Arff("data/china.arff")
dc = DataCollection(arff.data)
ic = InstanceCollection(dc)
ic.normalize_coordinates()
trainXY = log_y(log_x(deepcopy(ic.instances)))
quadrants = QuadrantTree(trainXY).leaves()
clusters = GRIDCLUS(quadrants)


trans = transpose(random_element(clusters).datums())

print arff.headers

for i in range(len(trans)-1):
    print trans[i][0]
    if type(trans[i][0]) is str:
        trans.remove(trans[i])
        arff.headers.remove(arff.headers[i])

fig = plt.figure(figsize=(16,8))
fig.subplots_adjust(wspace=0.5)
fig.subplots_adjust(hspace=0.5)

axisNum = 0
t = 0
for row in range(6):
    for col in range(5):
        if t < len(trans):
            axisNum += 1
            ax = plt.subplot(5, 4, axisNum)
            x = np.array(trans[t])
            ax.hist(x, 16)
            for label in ax.get_xticklabels():
                label.set_fontsize('xx-small')
            for label in ax.get_yticklabels():
                label.set_fontsize('x-small')
            ax.set_title(arff.headers[t])
            t += 1

plt.show()
