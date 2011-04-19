#!/opt/local/bin/python2.6
from arff import *
import numpy as np
import scipy
from timer import *

def hist(population):
    return scipy.histogram(population)[0]

def emd(s, d):
    "Accepts two arrays supply and demand. \
     EX. s: [0, 22, 8, 4], d: [5, 18, 4, 7]"

    total = 0

    for i in range(len(s)):
        if s[i] == d[i]:
            continue
        elif s[i] > d[i] and not i+1 > len(s) - 1:
            # Supply is larger than demand, go ahead and shift extra
            # earth right.
            move = (s[i] - d[i])
            s[i] -= move
            s[i+1] += move
            total += move * 1
        else: # s[i] < d[i]
            # Find closest larger bin. Move from that bin what we
            # can. If equal to the demand, stop. Else, find another
            # bin to keep moving until it is. Keep track of population
            # moved, and how far it had to travel. Multiply those
            # values and add to the total. Move to next bin til
            # finished.
            closestDistance = sys.maxint
            closestIndex = sys.maxint
            for j in range(len(s)):
                if s[j] > d[j] and not s[j] == d[j] and abs(i - j) < closestDistance:
                    closestDistance = abs(i - j)
                    closestIndex = j
            if d[i] - s[i] < s[closestIndex] - d[closestIndex]:
                move = d[i] - s[i]
            else:
                move = s[closestIndex] - d[closestIndex]
            s[closestIndex] -= move
            s[i] += move
            total += move * closestDistance

    # Double check, only good for equal populations
    #for i in range(len(s)):
    #    if s[i] != d[i]:
    #        print "Failure at i = %d : %d is not %d" % (i, s[i], d[i])

    return total

if __name__ == "__main__":
    arff = Arff("data/defect/jm1.arff")

    d1 = arff.data[0:len(arff.data)/2]
    d2 = arff.data[len(arff.data)/2:-1]

    d1 = transpose(d1)
    d2 = transpose(d2)

    with Timer("%d samples, histograms and emd for dependent var" % (len(d1[0]))):
        d1_h = hist(d1[-2])
        d2_h = hist(d2[-2])
        
        print emd(d1_h, d2_h)
