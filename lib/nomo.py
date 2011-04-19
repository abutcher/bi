#!/opt/local/bin/python2.6

from arff import *
from copy import deepcopy
from discretize import *
from instance import *
from util import *
import operator
import math

import matplotlib
matplotlib.use('WXagg')
import matplotlib.pyplot as plt
import pylab

class Nomogram:
    """
    The Nomogram class accepts a goal for the target class as either a
    discrete value or a numeric comparison, i.e. < 5000.  In the case
    of effort scores, you are part of the target class if your effort
    score is < 5000.  class_type helps us make the distinction, passed
    in as either DISCRETE or NUMERIC strings. This will help us make a
    Nomogram for good (low scoring) or bad (high scoring) in terms of
    effort.
    """
    
    def __init__(self, headers, instances, class_type, goal):

        self.ops = {"<": operator.lt, ">": operator.gt} # Operators we support for goal.

        self.headers = headers
        self.datums = discretize([inst.datum for inst in instances], 3)
        self.you = random_element(self.datums)
        self.class_type = class_type
        self.goal = goal
        self.seen_goal = {}
        self.seen_ngoal = {}
        self.buildSeen()
        self.scoreAttributes()

    def buildSeen(self):
        for datum in self.datums:
            for i in range(len(datum) - 1): # Ignore class column
                if self.matchesGoal(datum, self.goal):
                    if (self.headers[i], datum[i]) not in self.seen_goal.keys():
                        self.seen_goal[self.headers[i], datum[i]] = 1
                    else:
                        self.seen_goal[self.headers[i], datum[i]] += 1
                else:
                    if (self.headers[i], datum[i]) not in self.seen_ngoal.keys():
                        self.seen_ngoal[self.headers[i], datum[i]] = 1
                    else:
                        self.seen_ngoal[self.headers[i], datum[i]] += 1
                
    def matchesGoal(self, datum, goal):
        if self.class_type == "DISCRETE":
            return datum[-1] == goal
        elif self.class_type == "NUMERIC":
            op = goal.split(' ')[0]
            comp = goal.split(' ')[1]
            return self.ops[op](float(datum[-1]), float(comp))

    def scoreAttributes(self):
        combos = {}
        for datum in self.datums:
            for i in range(len(datum) - 1): # Ignore class column
                if (self.headers[i], datum[i]) not in combos.keys():
                    combos[self.headers[i], datum[i]] = self.likelyhood(self.headers[i], datum[i])
        self.attr_scores = [[] for header in self.headers]
        for header in self.headers:
            for key in combos.keys():
                if header in key:
                    self.attr_scores[self.headers.index(header)].append((key,combos[key]))
        self.attr_scores = sorted(self.attr_scores[0:-2], key=lambda score: max([elem[1] for elem in score]) - min([elem[1] for elem in score]))
        subplot = plt.subplot(111)
        
        for score in self.attr_scores:
            #print sorted(score, key=lambda elem: elem[1])
            x = np.array([elem[1] for elem in sorted(score, key=lambda elem: elem[1])])
            y = np.array([self.attr_scores.index(score) + 1 for elem in score])
            rank = np.array([elem[0][1] for elem in sorted(score, key=lambda elem: elem[1])])
            #y = np.array([self.headers[attr_scores.index(score)] for elem in score])
            subplot.plot(x, y, "b.-", label=rank[0])

        for e in range(len(self.you)-2):
            ranges = self.attr_scores[[self.attr_scores[i][0][0][0] for i in range(len(self.attr_scores))].index(self.headers[e])]
            for r in ranges:
                if (self.headers[e], self.you[e]) in r:
                    x = r[1]
            y = [self.attr_scores[i][0][0][0] for i in range(len(self.attr_scores))].index(self.headers[e]) + 1
            subplot.plot(x, y, "g^", markersize=10)
            
        pylab.yticks([i+1 for i in range(len(self.attr_scores))], [self.attr_scores[i][0][0][0] for i in range(len(self.attr_scores))])
        plt.show()

    def good_bad(self):
        tcount = 0
        tnotcount = 0
        for datum in self.datums:
            if self.matchesGoal(datum, self.goal):
                tcount += 1
            else:
                tnotcount += 1
        return float(tcount) / float(tnotcount)

    def likelyhood(self, header, elem):
        tcount = 0
        tnotcount = 0
        if (header, elem) not in self.seen_goal.keys():
            tcount = 1
        else:
            tcount = self.seen_goal[header, elem]
        if (header, elem) not in self.seen_ngoal.keys():
            tnotcount = 1
        else:
            tnotcount = self.seen_ngoal[header, elem]
        return math.log(((float(tcount) / float(tnotcount)) / self.good_bad()) + 0.0001)
        
def main():
    arff = Arff("data/coc81.arff")
    dc = DataCollection(arff.data)
    ic = InstanceCollection(dc)
    ic.normalize_coordinates()
    trainXY = log_y(log_x(deepcopy(ic.instances)))
    nomo = Nomogram(arff.headers, trainXY, "NUMERIC", "< 2000")
    
if __name__ == "__main__":
    main()
