#!/usr/bin/env python
from arff import *
from util import *
from copy import deepcopy

def discretize(data, n=10):
    trans = transpose(data)
    for i in range(len(trans)-1):
        if isnumeric(trans[i][0]):
            scol = sorted(trans[i])
            for j in range(len(trans[i])):
                trans[i][j] = (scol.index(trans[i][j]) / (len(scol) / n))+1
                if trans[i][j] == n + 1:
                    trans[i][j] = n
    return transpose(trans)

def discretize_class_values(data, n=10):
    trans = transpose(data)
    scol = sorted(trans[-1])
    for i in range(len(trans[-1])):
        trans[-1][i] = (scol.index(trans[-1][i]) / (len(scol) / n))
    return transpose(trans)

if __name__ == "__main__":
    arff1 = Arff("data/coc81-dem.arff")
    arff2 = Arff("data/nasa93-dem.arff")
    data = discretize(arff1.data+arff2.data, 7)
    for datum in data:
        print datum
            
