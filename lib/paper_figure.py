#!/opt/local/bin/python2.6
import numpy as np
import matplotlib
matplotlib.use('WXAgg')
import matplotlib.pyplot as plt
from matplotlib import cm, colors

from arff import *
from quadrant import *
from instance import *
from util import *
from gridclus2 import *

from copy import deepcopy

def make_n_colors(cmap_name, n):
    cmap = cm.get_cmap(cmap_name, n)
    return cmap(np.arange(n))

# SET UP
arff = Arff('data/china.arff')
dc = DataCollection(arff.data)
ic = InstanceCollection(dc)
ic.normalize_coordinates()
trainXY = log_y(log_x(deepcopy(ic.instances)))
quadrants = QuadrantTree(trainXY).leaves()
clusters = GRIDCLUS(quadrants)

# MAKE 3 AREAS
plt.figure(figsize=(15,4))
plt.subplots_adjust(wspace=0.1)


# POINTS
plt.subplot(1,3,1)
plt.xticks(visible=False)
plt.yticks(visible=False)
x = np.array([inst.coord.x for inst in trainXY])
y = np.array([inst.coord.y for inst in trainXY])
plt.plot(x,y,"bo",markersize=2,alpha=0.5)


# QUADRANTS
plt.subplot(1,3,2)
plt.xticks(visible=False)
plt.yticks(visible=False)
x = np.array([inst.coord.x for inst in trainXY])
y = np.array([inst.coord.y for inst in trainXY])
plt.plot(x,y,"bo",markersize=2,alpha=0.5)

for i in range(len(quadrants)):
    xmin = quadrants[i].xmin
    xmax = quadrants[i].xmax
    ymin = quadrants[i].ymin
    ymax = quadrants[i].ymax
    plt.bar(xmin, (ymax-ymin), width=(xmax-xmin), bottom=ymin, facecolor='white', visible=True, linewidth=0.5)

# CLUSTERS
plt.subplot(1,3,3)
plt.xticks(visible=False)
plt.yticks(visible=False)
x = np.array([inst.coord.x for inst in trainXY])
y = np.array([inst.coord.y for inst in trainXY])
plt.plot(x,y,"bo",markersize=2,alpha=0.5)

effort = [clus.cmedian() for clus in clusters]
range_length = int(len(effort)/8)

effort = sorted(effort)

range1 = effort[range_length]
range2 = effort[range_length*2]
range3 = effort[range_length*3]
range4 = effort[range_length*4]
range5 = effort[range_length*5]
range6 = effort[range_length*6]
range7 = effort[range_length*7]
range8 = effort[-1]

greens = make_n_colors(cm.Greens_r, 80)
reds = make_n_colors(cm.Reds, 240)

for cluster in clusters:
    for quadrant in cluster.quadrants:

        xmin = quadrant.xmin
        xmax = quadrant.xmax
        ymin = quadrant.ymin
        ymax = quadrant.ymax
    
        if cluster.cmedian() < range1:
            plt.bar(xmin, (ymax-ymin), width=(xmax-xmin), bottom=ymin, facecolor=greens[0], visible=True, linewidth=0)                    
        elif cluster.cmedian() < range2:
            plt.bar(xmin, (ymax-ymin), width=(xmax-xmin), bottom=ymin, facecolor=greens[19], visible=True, linewidth=0)                    
        elif cluster.cmedian() < range3:
            plt.bar(xmin, (ymax-ymin), width=(xmax-xmin), bottom=ymin, facecolor=greens[39], visible=True, linewidth=0)                    
        elif cluster.cmedian() < range4:
            plt.bar(xmin, (ymax-ymin), width=(xmax-xmin), bottom=ymin, facecolor=greens[59], visible=True, linewidth=0)                    
        elif cluster.cmedian() < range5:
            plt.bar(xmin, (ymax-ymin), width=(xmax-xmin), bottom=ymin, facecolor=reds[60], visible=True, linewidth=0)                    
        elif cluster.cmedian() < range6:
            plt.bar(xmin, (ymax-ymin), width=(xmax-xmin), bottom=ymin, facecolor=reds[120], visible=True, linewidth=0)                    
        elif cluster.cmedian() < range7:
            plt.bar(xmin, (ymax-ymin), width=(xmax-xmin), bottom=ymin, facecolor=reds[180], visible=True, linewidth=0)                    
        else:
            plt.bar(xmin, (ymax-ymin), width=(xmax-xmin), bottom=ymin, facecolor=reds[239], visible=True, linewidth=0)                    

plt.show()
