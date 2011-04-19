#!/opt/local/bin/python2.6

import matplotlib
matplotlib.use('WXagg')
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib import cm, colors

from arff import *
from quadrant import *
from instance import *
from util import *
from NaiveBayes import *
from gridclus2 import *

from copy import deepcopy
from scipy import linspace, polyval, polyfit, sqrt, stats, randn

class Widget:

    def __init__(self, title, instances, quadrants, clusters):
        self.title = title
        self.instances = instances
        self.quadrants = quadrants
        self.clusters = clusters
        
        self.overlay = False
        self.trend = False

        self.fig = plt.figure()

        # Button axes
        self.axtrends = self.fig.add_axes([0.75, 0.4, 0.2, 0.05])
        self.btrends = Button(self.axtrends, 'Trends')
        self.btrends.on_clicked(self.trends)

        self.axalerts = self.fig.add_axes([0.75, 0.3, 0.2, 0.05])
        self.balerts = Button(self.axalerts, 'Alerts')
        self.balerts.on_clicked(self.alerts)

        self.axoverlays = self.fig.add_axes([0.75, 0.2, 0.2, 0.05])
        self.boverlays = Button(self.axoverlays, 'Overlays')
        self.boverlays.on_clicked(self.overlays)

        # Axes are defined [left, bottom, width, height]
        self.canvas = self.fig.add_axes([0.1, 0.1, 0.6, 0.8])
        self.draw_canvas_instances()
        self.draw_canvas_quadrants_vanilla()
        
        self.info = self.fig.add_axes([0.75, 0.5, 0.2, 0.4])
        plt.setp(self.info, xticks=[], yticks=[])

        cid = self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        
    def draw_canvas_instances(self):
        for instance in self.instances:
            self.canvas.plot(instance.coord.x,
                             instance.coord.y,
                             "o",
                             markersize=2,
                             alpha=0.5)

    def draw_canvas_quadrants_vanilla(self):
        for quadrant in self.quadrants:
            self.color_quadrants([quadrant], 'white')

    def draw_canvas_quadrants_overlay(self):
        # What I'm doing here is making 8 ranges for effort scores
        # based on the scores from all quadrants. There are then 8
        # colors with which to color each quadrant. Going from really
        # green to really red. Good = really green, bad = really red.

        effort = [quadrant.qmedian() for quadrant in self.quadrants]
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

        greens = self.make_n_colors(cm.Greens_r, 80)
        reds = self.make_n_colors(cm.Reds, 240)

        for quadrant in self.quadrants:
            if quadrant.qmedian() < range1:
                self.color_quadrants([quadrant], greens[0])
            elif quadrant.qmedian() < range2:
                self.color_quadrants([quadrant], greens[19])
            elif quadrant.qmedian() < range3:
                self.color_quadrants([quadrant], greens[39])
            elif quadrant.qmedian() < range4:
                self.color_quadrants([quadrant], greens[59])
            elif quadrant.qmedian() < range5:
                self.color_quadrants([quadrant], reds[60])
            elif quadrant.qmedian() < range6:
                self.color_quadrants([quadrant], reds[120])
            elif quadrant.qmedian() < range7:
                self.color_quadrants([quadrant], reds[180])
            else:
                self.color_quadrants([quadrant], reds[239])

    def annotate_quadrant(self, quadrant):
        xmin = quadrant.xmin
        xmax = quadrant.xmax
        ymin = quadrant.ymin
        ymax = quadrant.ymax        
        self.canvas.bar(xmin, (ymax-ymin), width=(xmax-xmin), bottom=ymin, facecolor='purple', visible=True, linewidth=0.5)
            
    def clear_canvas(self):
        self.canvas.clear()
        
    def clear_info(self):
        self.info.clear()
        plt.setp(self.info, xticks=[], yticks=[])
        
    def draw_info(self, quadrant):
        if quadrant != None:
            variance = quadrant.qvariance()
            size = len(quadrant.instances)
            med_effort = median(transpose(quadrant.datums())[-1])
            print "variance: %.2f" % (variance)
            print "size: %d" % (size)
            print "median effort: %.2f" % (med_effort)
            plt.text(.06, .8, "Var: %.2f" % variance)
            plt.text(.06, .6, "MEf: %.2f" % med_effort)
            plt.text(.06, .4, "Size: %d" % size)
        
    def color_quadrants(self, quadrants, color):
        for i in range(len(quadrants)):
            xmin = quadrants[i].xmin
            xmax = quadrants[i].xmax
            ymin = quadrants[i].ymin
            ymax = quadrants[i].ymax
            self.canvas.bar(xmin, (ymax-ymin), width=(xmax-xmin), bottom=ymin, facecolor=color, visible=True, linewidth=0.5)

    def onclick(self, event):
        print 'button=%d, x=%d, y=%d, xdata=%f, ydata=%f'%(
            event.button, event.x, event.y, event.xdata, event.ydata)
        picked_quadrant = None
        for quadrant in self.quadrants:
            if event.xdata > quadrant.xmin and event.xdata < quadrant.xmax and event.ydata > quadrant.ymin and event.ydata < quadrant.ymax:
                picked_quadrant = quadrant
        self.clear_info()
        self.draw_info(picked_quadrant)
        plt.draw()
        
    def trends(self, event):
        xlim = self.canvas.get_xlim()
        ylim = self.canvas.get_ylim()
        self.clear_canvas()
        self.canvas.set_xlim(xlim)
        self.canvas.set_ylim(ylim)

        if self.overlay == True:
            self.draw_canvas_quadrants_overlay()
        else:
            self.draw_canvas_quadrants_vanilla()
        
        if self.trend == True:
            self.draw_canvas_instances()
            self.trend = False
        else:
            one = random_element(self.instances)
            two = random_element(self.instances)
            three = random_element(self.instances)
            four = random_element(self.instances)

            self.canvas.plot(one.coord.x,
                             one.coord.y,
                             "go",
                             markersize=3)
            self.canvas.plot(two.coord.x,
                             two.coord.y,
                             "go",
                             markersize=3)
            self.canvas.plot(three.coord.x,
                             three.coord.y,
                             "go",
                             markersize=3)
            self.canvas.plot(four.coord.x,
                             four.coord.y,
                             "go",
                             markersize=3)

            x = np.array([one.coord.x, two.coord.x, three.coord.x, four.coord.x])
            y = np.array([one.coord.y, two.coord.y, three.coord.y, four.coord.y])
            (ar,br)=polyfit( x, y, 1)
            xr = polyval([ar,br], x)
            self.canvas.plot(x, xr, 'b.-')

            self.trend = True
            
        plt.draw()

    def alerts(self, event):
        datums = []
        for cluster in self.clusters:
            for instance in cluster.instances():
                datums.extend([instance.datum[0:-2] + ["cluster_%d" % self.clusters.index(cluster)]])

        #for quadrant in self.quadrants:
        #    for instance in quadrant.instances:
        #        datums.extend([instance.datum[0:-2] + ["quadrant_%d" % self.quadrants.index(quadrant)]])
        """
        you_are_here = random_element(datums)
        datums.remove(you_are_here)
        
        got = NaiveBayesClassify(you_are_here, datums)
        want = you_are_here[-1]
        
        print got
        print want

        if self.clusters[int(got.split('_')[-1])].is_neighbor(self.clusters[int(want.split('_')[-1])]):
            print "adjacent..."
        """
        right = 0
            
        for datum in datums:
            datums.remove(datum)
            got = NaiveBayesClassify(datum, datums)
            want = datum[-1]
            if got == want or self.clusters[int(got.split('_')[-1])].is_neighbor(self.clusters[int(want.split('_')[-1])]):
                right += 1
            datums.append(datum)
            
        print right, '/', len(datums)
        
        plt.draw()

    def overlays(self, event):
        xlim = self.canvas.get_xlim()
        ylim = self.canvas.get_ylim()
        self.clear_canvas()
        self.canvas.set_xlim(xlim)
        self.canvas.set_ylim(ylim)
        self.draw_canvas_instances()

        if self.overlay == True:
            self.draw_canvas_quadrants_vanilla()
            self.overlay = False
        else:
            self.draw_canvas_quadrants_overlay()
            self.overlay = True
        plt.draw()
        
    def show(self):
        plt.show()

    def make_n_colors(self, cmap_name, n):
        cmap = cm.get_cmap(cmap_name, n)
        return cmap(np.arange(n))

def main():
    arff = Arff('data/china.arff')
    dc = DataCollection(arff.data)
    ic = InstanceCollection(dc)
    ic.normalize_coordinates()

    trainXY = log_y(log_x(deepcopy(ic.instances)))
    quadrants = QuadrantTree(trainXY).leaves()
    clusters = GRIDCLUS(quadrants)

    widget = Widget( 'china', trainXY, quadrants, clusters)
    widget.show()

if __name__ == '__main__':
    main()
