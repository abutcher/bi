#!/usr/bin/env python

from arff import *
from quadrant import *
from instance import *
from util import *
from copy import deepcopy

def main():
    arff = Arff("data/desharnais_1_1.arff")
    dc = DataCollection(arff.data)
    ic = InstanceCollection(dc)
    ic.normalize_coordinates()

    trainXY = log_y(log_x(deepcopy(ic.instances)))
    quadrants = QuadrantTree(trainXY).leaves()

    diffs = []
    for quadrant in quadrants:
        neighbors = neighbor_search(quadrant, quadrants)
        if neighbors != None:
            for neighbor in neighbors:
                maxm = max(quadrant.qmedian(), neighbor.qmedian())
                minm = min(quadrant.qmedian(), neighbor.qmedian())
                diffs.append(((maxm-minm)/maxm)*100)
    diffs = sorted(diffs)
    for diff in diffs:
        print diff


def neighbor_search(quadrant, quadrants):
    neighbors = []
    for other_quadrant in quadrants:
        if quadrant.is_adjacent(other_quadrant):
            neighbors.append(other_quadrant)
    return neighbors


if __name__ == "__main__":
    main()
