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
fig = plt.figure(figsize=(15,4))
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

def _get_limits( ax ):
    """ Return X and Y limits for the passed axis as [[xlow,xhigh],[ylow,yhigh]]
    """
    return [list(ax.get_xlim()), list(ax.get_ylim())]

def _set_limits( ax, lims ):
    """ Set X and Y limits for the passed axis
    """
    ax.set_xlim(*(lims[0]))
    ax.set_ylim(*(lims[1]))
    return

def pre_zoom( fig ):
    """ Initialize history used by the re_zoom() event handler.
        Call this after plots are configured and before pyplot.show().
    """
    global oxy
    oxy = [_get_limits(ax) for ax in fig.axes]
    # :TODO: Intercept the toolbar Home, Back and Forward buttons.
    return

def re_zoom(event):
    """ Pyplot event handler to zoom all plots together, but permit them to
        scroll independently.  Created to support eyeball correlation.
        Use with 'motion_notify_event' and 'button_release_event'.
    """
    global oxy
    for ax in event.canvas.figure.axes:
        navmode = ax.get_navigate_mode()
        if navmode is not None:
            break
    scrolling = (event.button == 1) and (navmode == "PAN")
    if scrolling:                   # Update history (independent of event type)
        oxy = [_get_limits(ax) for ax in event.canvas.figure.axes]
        return
    if event.name != 'button_release_event':    # Nothing to do!
        return
    # We have a non-scroll 'button_release_event': Were we zooming?
    zooming = (navmode == "ZOOM") or ((event.button == 3) and (navmode == "PAN"))
    if not zooming:                 # Nothing to do!
        oxy = [_get_limits(ax) for ax in event.canvas.figure.axes]  # To be safe
        return
    # We were zooming, but did anything change?  Check for zoom activity.
    changed = None
    zoom = [[0.0,0.0],[0.0,0.0]]    # Zoom from each end of axis (2 values per axis)
    for i, ax in enumerate(event.canvas.figure.axes): # Get the axes
        # Find the plot that changed
        nxy = _get_limits(ax)
        if (oxy[i] != nxy):         # This plot has changed
            changed = i
            # Calculate zoom factors
            for j in [0,1]:         # Iterate over x and y for each axis
                # Indexing: nxy[x/y axis][lo/hi limit]
                #           oxy[plot #][x/y axis][lo/hi limit]
                width = oxy[i][j][1] - oxy[i][j][0]
                # Determine new axis scale factors in a way that correctly
                # handles simultaneous zoom + scroll: Zoom from each end.
                zoom[j] = [(nxy[j][0] - oxy[i][j][0]) / width,  # lo-end zoom
                           (oxy[i][j][1] - nxy[j][1]) / width]  # hi-end zoom
            break                   # No need to look at other axes
    if changed is not None:
        for i, ax in enumerate(event.canvas.figure.axes): # change the scale
            if i == changed:
                continue
            for j in [0,1]:
                width = oxy[i][j][1] - oxy[i][j][0]
                nxy[j] = [oxy[i][j][0] + (width*zoom[j][0]),
                          oxy[i][j][1] - (width*zoom[j][1])]
            _set_limits(ax, nxy)
        event.canvas.draw()         # re-draw the canvas (if required)
        pre_zoom(event.canvas.figure)   # Update history
    return
# End re_zoom()

pre_zoom( fig )  
plt.connect('motion_notify_event', re_zoom)  # for right-click pan/zoom
plt.connect('button_release_event', re_zoom) # for rectangle-select zoom

plt.show()
