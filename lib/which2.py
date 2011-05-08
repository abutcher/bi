#!/opt/local/bin/python2.6

"""
  which2n (the n stands for numeric)
  
  Class columns should be formatted with a # for minimize, ! for
  maximize.
 
"""

from arff import *
from copy import deepcopy
from discretize import *
import math
from util import *

def which2n(headers, datums):
    round0 = round0n(headers, datums)
    finalRules = roundsn(headers, datums, round0)
    return finalRules

def round0n(headers, datums):
    """ Round 0 returns all possible singleton rules... ((temp 75),
    (weather sunny), (weather rainy)...) """
    return list(set([(headers[i], datum[i]) for datum in datums for i in range(len(datum)-1)]))

def roundsn(headers, datums, round0):
    """ Continually combine rules and score them. If max score doesn't
    increase for n rounds, stop. """
    lives = 5
    rules = []
    round = 1
    max = 0
    
    for r in round0:
        this = Rule()
        this.createFull("bland", r, headers, datums)
        # if this.support > 16:
        rules.append(this)

    while lives > 0:
        this = None
        found = True
        for i in range(20):
            this = combine(twos(explode(normalize(rules))))
            this.score = this.scoren(headers, datums)
            if this in rules:
                found = False
            if not found == True and 5 > this.support:
                rules.insert(0, this)
        rules = prune(rules)
        if rules[0].score > max:
            max = rules[0].score
            lives = 6
        round += 1
        lives -= 1
    return finalPrune(rules)
    
class Rule:
    def __init__(self):
        self.klass = None
        self.support = 0
        self.utils = []
        self.marked = False
        self.avgs = []
        self.ands = []
        self.score = 0

    def createFull(self, klass, rule, headers, datums):
        self.klass = klass
        self.support = 0
        self.utils = []
        self.marked = False
        self.avgs = []
        self.ands = [Ors(rule[0], [rule[1]])]
        self.score = self.scoren(headers, datums)

    def createHalf(self, klass, score):
        self.klass = klass
        self.support = 0
        self.utils = []
        self.marked = False
        self.avgs = []
        self.ands = []
        self.score = score

    """
    def __init__(self, klass, rule, headers, datums):
        self.klass = klass
        self.support = None
        self.utils = []
        self.marked = None
        self.avgs = []
        self.ands = [Ors(rule[0], [rule[1]])]
        self.score = self.scoren(headers, datums)
    """

    def describe(self):
        ands = ""
        for a in self.ands:
            ands += a.describe()
        return "ORS\n" + ands + "Score: " + str(self.score) + "\nAvgs: " + str(self.avgs) + "\nUtils: " + str(self.utils) + "\nSupport: " + str(self.support) + "\n"

    def scoren(self, headers, datums):
        rowlistout = []
        goals = []
        for header in headers:
            if header[0] == "#" or header[0] == "!":
                goals.append(headers.index(header))
        for datum in datums:
            if self.ruleMatch(headers, datum):
                rowlistout.append(datum)
        goalsums = [0 for i in range(len(goals))]
        goalavgs = []
        for row in rowlistout:
            counter = 0
            for g in goals:
                goalsums[counter] += row[g]
                counter += 1
        for this in goalsums:
            if this == 0:
                goalavgs.insert(0, 0)
            else:
                #goalavgs.insert(0, this / len(rowlistout))
                goalavgs.insert(0, len(rowlistout)/len(datums))
        self.support = len(rowlistout)
        self.avgs = goalavgs
        weightedavgs = []
        for i in goals:
            if headers[i][0] == "!":
                if goalavgs[goals.index(i)] == 0:
                    weightedavgs.insert(0, 0)
                else:
                    weightedavgs.insert(0, (goalavgs[goals.index(i)]-min(transpose(datums)[i]))/(max(transpose(datums)[i]) - min(transpose(datums)[i])))
            elif headers[i][0] == "#":
                if goalavgs[goals.index(i)] == 0:
                    weightedavgs.insert(0, 0)
                else:
                    weightedavgs.insert(0, (max(transpose(datums)[i]) - goalavgs[goals.index(i)]) / (max(transpose(datums)[i]) - min(transpose(datums)[i])))
        self.utils = weightedavgs
        return magnitude(weightedavgs)

    def ruleMatch(self, headers, row):
        out = True
        for thisors in self.ands:
            if not row[headers.index(thisors.forr)] in thisors.values:
                out = False
        return out

class Ors:
    def __init__(self, forr, values):
        self.forr = forr
        self.values = values
    def describe(self):
        return "For: " + str(self.forr) + ", Values: " + str(self.values) + "\n"

def magnitude(l):
    return math.sqrt(sum([a**2 for a in l]))

def explode(l):
    out = []
    for this in l:
        for i in range(int(this[0])):
            out.append(this[1])
    return out

def normalize(l):
    out = []
    sum = 0
    for this in l:
        if sum < this.score:
            sum = this.score
    for this in l:
        out.insert(0, [math.floor(100 * (this.score / sum)), this])
    return out

def prune(l):
    out = []
    max = 0
    cntr = 0
    for this in l:
        if not this.support == 0:
            out.insert(0, this)
    out = sorted(out, key=lambda(x): x.score, reverse=True)
    return out

def finalPrune(l):
    for this in deepcopy(l):
        if not this.marked:
            for that in deepcopy(l):
                if not this == that or that.marked:
                    if paretoDominate(that.utils, this.utils):
                        this.marked = True
    return removeMarks(l)

def removeMarks(l):
    for this in l:
        if this.marked:
            l.remove(this)
    return l

def paretoDominate(l1, l2):
    if l1 == []:
        return True
    elif l1[0] < l2[0]:
        return False
    else:
        return paretoDominate(l1[1:], l2[1:])
    
def twos(l):
    r1 = random_element(l)
    r2 = random_element(l)
    if r1 == r2:
        return twos0(l, r1, 19, 361, r1)
    else:
        diff = diffAngle(r1.utils, r2.utils)
        if 15 > diff:
            return [r1, r2]
        else:
            return twos0(l, r1, 19, diff, r2)

def twos0(l, r1, x, minDiff, minR):
    r2 = random_element(l)
    if x <= 0:
        return [r1, r2]
    elif r1 == r2:
        return twos0(l, r1, x - 1, minDiff, minR)
    else:
        diff = diffAngle(r1.utils, r2.utils)
        if 15 > diff:
            return [r1, r2]
        elif diff < minDiff:
            return twos0(l, r1, x - 1, diff, r2)
        else:
            return twos0(l, r1, x - 1, minDiff, r2)

def combine(rlist):
    r1 = rlist[0]
    r2 = rlist[1]
    r3 = Rule()
    r3.createHalf(r1.klass, 0)

    for r1and in r1.ands:
        r3.ands.append(r1and)
    for r2and in r2.ands:
        nomatch = True
        for r3and in r3.ands:
            if r2and.forr == r3and.forr:
                r3and.values = sorted(list(set(r2and.values + r3and.values)))
                nomatch = False
        if nomatch:
            r3.ands.append(r2and)
    r3.ands = sorted(r3.ands, key=lambda(x): x.forr)
    return r3

def diffAngle(a, b):
    k = similarity(a, b)
    if k > 1:
        k = 1.0
    return radians_to_degrees(math.acos(k))

def similarity(a, b):
    return dotProduct(a, b) / (magnitude(a) * magnitude(b))

def dotProduct(a, b):
    if a == None:
        return 0
    elif len(a) == 1:
        return a[0] * b[0]
    else:
        return (a[0] * b[0]) + dotProduct(a[1:], b[1:])

def radians_to_degrees(theta):
    return theta * (180 / math.pi)

if __name__ == "__main__":
    arff = Arff("data/china.arff")
    rules = which2n(arff.headers, discretize(arff.data))
    for rule in rules:
        print rule.describe()
