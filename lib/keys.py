#!/opt/local/bin/python2.6
from arff import *
from copy import deepcopy
from discretize import *


def keys2(data, headers):
    enough = .33
    too_small = 3
    bins = 5

    i = 0
    data = discretize(deepcopy(data), bins)
    datar = []
    datar.append(deepcopy(data))
    score = []
    score.append(median(transpose(data)[-1]))
    treatment = []
    worth_something = []
    
    while True:
        best = sorted(datar[i], key=lambda datum: datum[-1])[0:int(round(len(datar[i])*enough))]

        if len(best) < too_small:
            #print "breaking 0"
            break

        rest = sorted(datar[i], key=lambda datum: datum[-1])[int(round(len(datar[i])*enough))+1:-1]

        B = len(best)
        R = len(rest)
        #print "B", B
        #print "R", R
        wow = -1
        rx = None

        for a in headers[0:-2]: # all independent attributes
            for v in [datum[headers.index(a)] for datum in datar[i]]:
                b = float([datum[headers.index(a)] for datum in best].count(v))
                #print "b", b
                if b > 0:
                    r = float([datum[headers.index(a)] for datum in rest].count(v))
                    #print "r", r
                    if (b/B) > (r/R):
                        tmp = ((b/B)**2)/((b/B) + (r/R))
                        #print "tmp", tmp
                        #worth_something.append(rx)
                        if tmp > wow:
                            wow = tmp
                            rx = (a,v)
                            #print "setting rx"
                            print "RX", rx

        i += 1
        datar.append([datum for datum in datar[i-1] if datum[headers.index(rx[0])] == rx[1]])
        #print len(datar[i])
        score.append(median(transpose(datar[i])[-1]))
        print score
        print treatment
        if len(datar[i]) == 0:
            #print "breaking 1"
            break
        elif len(datar[i]) == len(datar[i-1]):
            #print "breaking 2"
            break
        elif not score[i] < score[i-1]:
            #print "breaking 3"
            break
        else:
            print "setting awesome treatment"
            treatment.insert(0, rx)
        print "looping"
    #print worth_something
    return treatment


if __name__ == "__main__":
    arff = Arff("data/china.arff")
    arff.data = remove_column(arff.data, 0)
    arff.headers.remove("ID")
    #arff.data = remove_column(arff.data, 0)
    #arff.headers.remove("version")    
    print keys2(arff.data, arff.headers)
