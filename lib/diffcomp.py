#!/usr/bin/env python

from arff import *
from quadrant import *
from instance import *
from util import *
from copy import deepcopy
from scipy import stats

def main():
    files = ["data/albrecht.arff", "data/china.arff", "data/coc81.arff", "data/cocomo_sdr.arff", "data/desharnais_1_1.arff", "data/finnish.arff", "data/kemerer.arff", "data/maxwell.arff", "data/nasa93.arff", "data/telecom1.arff"]

    diffs = []

    for f in files:
        arff = Arff(f)
        dc = DataCollection(arff.data)
        ic = InstanceCollection(dc)
        ic.normalize_coordinates()
        
        trainXY = log_y(log_x(deepcopy(ic.instances)))
        quadrants = QuadrantTree(trainXY).leaves()

        diff = []
        for quadrant in quadrants:
            neighbors = neighbor_search(quadrant, quadrants)
            if neighbors != None:
                for neighbor in neighbors:
                    maxm = max(quadrant.qmedian(), neighbor.qmedian())
                    minm = min(quadrant.qmedian(), neighbor.qmedian())
                    diffs.append(((maxm-minm)/maxm)*100)
        diff = sorted(diffs)
        diffs.append(diff)

    ranks = []
    current = 0
    for i in range(len(diffs) - 1):
        if stats.mannwhitneyu(diffs[i], diffs[i+1])[1] < 0.5:
            ranks.append(current)
        else:
            current += 1
            ranks.append(current)

    for i in range(len(ranks)):
        print ranks[i], files[i].split("/").split(".")[0]

def neighbor_search(quadrant, quadrants):
    neighbors = []
    for other_quadrant in quadrants:
        if quadrant.is_adjacent(other_quadrant):
            neighbors.append(other_quadrant)
    return neighbors


if __name__ == "__main__":
    main()
