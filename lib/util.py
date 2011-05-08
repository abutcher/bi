import os
import sys
import math
import random
import numpy as np
import arff
import operator

def variance(data):
    if len(data) == 1:
        return 0
    elif type(data[0][-1]) is str:
        return entropy(data)
    else:
        return stddev(transpose(data)[-1], None)

def squash(l):
    big = []
    for i in range(len(l)):
        big += l[i]
    return big

def median(data):
    scores = []
    for i in range(len(data)):
        try:
            scores.append(data[i][-1])
        except:
            scores.append(data[i])
    scores.sort()
    if len(scores) is 1:
        return scores[-1]
    elif len(scores) is 2:
        return (scores[0] + scores[1]) / 2
    elif len(scores) % 2 == 0:
        middle = int(math.floor(len(scores) / 2))
        return (scores[middle] + scores[middle+1]) / 2
    else:
        return scores[len(scores) / 2]

def stratified_cross_val(data, option):
    if type(data[0][-1]) is str:
        data = sort_by_class(data)
    train_count = 0
    test_count = 0
    train = []
    test = []
    for datum in data:
        if train_count < option[0]:
            train_count = train_count + 1
            train.append(datum)
        elif test_count < option[1]:
            test_count = test_count + 1
            test.append(datum)
        if train_count == option[0] and test_count == option[1]:
            train_count = 0
            test_count = 0
    return train,test

def log_datum(data):
    for x in range(len(data)):
        for y in range(len(data[x].datum)-1):
            try:
                data[x].datum[y] = math.log(data[x].datum[y] + 0.0001)
            except:
                data[x].datum[y] = math.log(0.0001)
    return data

def log_x(data):
    if type(data) is list:
        for i in range(len(data)):
            data[i].coord.x = math.log(data[i].coord.x + 0.0001)
    else:
        data.coord.x = math.log(data.coord.x + 0.0001)
    return data

def log_y(data):
    if type(data) is list:
        for i in range(len(data)):
            data[i].coord.y = math.log(data[i].coord.y + 0.0001)
    else:
        data.coord.y = math.log(data.coord.y + 0.0001)
    return data
            
def sort_by_class(instances):
    instances.sort(key=lambda instance: instance.datum[-1])
    return instances

def transpose(lists):
   if not lists: 
       return []
   return map(lambda *row: list(row), *lists)

def separate(these):
    thisgroup = []
    thatgroup = []
    this = randomelement(these)
    these.remove(this)
    that = farthestfrom(this, these)
    these.remove(that)
    these.append(this)
    this = farthestfrom(that, these)
    these.remove(this)
    thisgroup.append(this)
    thatgroup.append(that)
    for instance in these:
        if distance(instance, this) > distance(instance, that):
            thatgroup.append(instance)
        else:
            thisgroup.append(instance)
    these.append(this)
    these.append(that)
    return thisgroup, thatgroup

def random_element(l):
    if len(l) == 0:
        print "LENGTH IS 0 WHAT WERE YOU THINKING!"
    else:
        return l[random.randint(0,len(l)-1)]

def closest_to(this, these, d=sys.maxint):
    for instance in these:
        if distance(this, instance) < d:
            that = instance
            d = distance(this, instance)
    return that

def farthest_from(this, these, d=0.0):
    for instance in these:
        if distance(this, instance) > d:
            that = instance
            d = distance(this, instance)
    return that

def distance(vecone, vectwo, d=0.0):
    for i in range(len(vecone) - 1):
        if isnumeric(vecone[i]):
            d = d + (vecone[i] - vectwo[i])**2
        elif vecone[i] is not vectwo[i]:
            d += 1.0
    return math.sqrt(d)

def isnumeric(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def stddev(values, meanval=None):
    if meanval == None: meanval = mean(values)
    return math.sqrt(sum([(x - meanval)**2 for x in values]) / (len(values)-1))

def mean(values):
    return sum(values) / float(len(values))

def MRE(actual, predicted):
    return math.fabs(actual - predicted) / math.fabs(actual)

def find_min_max(data,indice):
    max_score = -sys.maxint
    min_score = sys.maxint
    for i in range(len(data)):
        if data[i][indice] < min_score:
            min_score = data[i][indice]
        if data[i][indice] > max_score:
            max_score = data[i][indice]
    return min_score, max_score

def find_min_max(data):
    max_score = -sys.maxint
    min_score = sys.maxint
    for i in range(len(data)):
        if data[i][len(data[i])-1] < min_score:
            min_score = data[i][len(data[i])-1]
        if data[i][len(data[i])-1] > max_score:
            max_score = data[i][len(data[i])-1]
    return min_score, max_score

def normalize(data):
    normal_data=[]
    min_score, max_score = find_min_max(data)
    for i in range(len(data)):
        normal_data.append((data[i][len(data[i])-1]-min_score)/(max_score-min_score))
    return normal_data

def equal_frequency_ticks_x(coords, n):
    ticks = []
    sorted_coords = sorted(coords, key=lambda coord: coord.x)
    num_per_grid = int(round(len(coords)) / (n + 1.0))
    for i in range(n):
        ticks.append(coords[num_per_grid*i].x)
    ticks.append(coords[-1].x)
    return ticks

def equal_frequency_ticks_y(coords, n):
    ticks = []
    sorted_coords = sorted(coords, key=lambda coord: coord.y)
    num_per_grid = int(round(len(coords)) / (n + 1.0))
    for i in range(n):
        ticks.append(coords[num_per_grid*i].y)
    ticks.append(coords[-1].y)
    return ticks
    
def equal_width_ticks(data, indice, n):
    ticks = []
    (minn, maxn) = find_min_max(data,indice)
    interval = (maxn - minn)/ float(n)
    for i in range(n+1):
        ticks.append( ( float(i) ) * float(interval))
    return ticks

def entropy (population):
    if (len(population) == 0):
        print "Population is zero?"
    
    columns = transpose(population)
    frequencies = []
    entropy = 0
    for column in columns:
        d = {}
        for item in column:
            if item not in d.keys():
                d[item] = 1
            else:
                d[item] += 1
        frequencies.append(d)
    for piece in population:
        e = 0
        for i in range(len(piece)):
            pn = frequencies[i][piece[i]]
            pd = 0
            for key in frequencies[i].keys():
                pd += frequencies[i][key]
            pn = float(pn)
            pd = float(pd)
            e += (pn/pd) * math.log(pn/pd, 2)
        entropy += e
    return abs(entropy/len(population))

def chopInTwo(data):
    random.shuffle(data, random.random)
    g1 = data[0:int(len(data)/2)]
    g2 = data[int(len(data)/2)+1:-1]
    return g1, g2

