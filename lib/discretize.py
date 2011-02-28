#!/usr/bin/env python
import arff
from util import *

def discretize(data, n=10):
    trans = transpose(data)
    for i in range(len(trans)-1):
        if isnumeric(trans[i][0]):
            scol = sorted(trans[i])
            for j in range(len(trans[i])):
                trans[i][j] = (scol.index(trans[i][j]) / (len(scol) / n))
    return transpose(trans)

def discretize_class_values(data, n=10):
    trans = transpose(data)
    scol = sorted(trans[-1])
    for i in range(len(trans[-1])):
        trans[-1][i] = (scol.index(trans[-1][i]) / (len(scol) / n))
    return transpose(trans)

if __name__ == "__main__":
    arff = arff.Arff("arff/coc81.arff")
    data = discretize_class_values(arff.data)
    for datum in data:
        print datum
            
