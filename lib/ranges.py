#!/opt/local/bin/python2.6

import numpy as np
import matplotlib
matplotlib.use('WXagg')
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button

from copy import deepcopy
from arff import *
from instance import *
from util import *

def main():
    arff = Arff('data/china.arff')
    dc = DataCollection(arff.data)
    ic = InstanceCollection(dc)
    ic.normalize_coordinates()

    testXY = log_y(log_x(random_element(deepcopy(ic.instances))))
    trainXY = log_y(log_x(deepcopy(ic.instances)))

    trans = transpose(ic.datums())
    maxs = [max(elem) for elem in trans]
    mins = [min(elem) for elem in trans]

    norm = []
    for i in range(len(testXY.datum)):
        norm.append(testXY.datum[i]/(maxs[i]+0.000001))

    axes = []
    for i in range(len(trans)):
        axes.append(plt.axes([0.15, 0.05+(i*.05), 0.65, 0.03]))

    sliders = []
    for i in range(len(trans)):
        sliders.append(Slider(axes[i], arff.headers[i], 0.1, maxs[i], valinit=testXY.datum[i]))

    plt.show()

if __name__ == '__main__':
    main()
