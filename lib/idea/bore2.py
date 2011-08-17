import arff
import argparse
from discretize import *

class Bore:
    def __init__(self, data, headers, goal, b=0.2, bins=10):
        random.shuffle(data, random.random)
        self.data = data #discretize(data, bins)
        self.headers = headers
        self.goal = goal.lower()
        self.best = []
        self.rest = []
        self.brsplit(b)
        self.bfreq = self.freqtable(self.best)
        self.rfreq = self.freqtable(self.rest)
        self.score()

    def brsplit(self, x):
        for i in range(len(self.data)):
            if (self.data[i][-1].lower() in self.goal.lower()) and (len(self.best) < round((x*len(self.data)))):
                self.best.append(self.data[i])
            else:
                self.rest.append(self.data[i])

    def freqtable(self, data):
        freqtable=[]
        trans = transpose(data)
        for column in trans:
            d = {}
            for item in column:
                if item not in d.keys():
                    d[item] = 1
                else:
                    d[item] += 1
            freqtable.append(d)
        return freqtable

    def score(self):
        trans = transpose(self.data)
        scores = []
        for header in self.headers[0:-2]:
            for item in trans[self.headers.index(header)]:
                if "%s %s %s" % (self.headers.index(header), header,str(item)) not in [score[0] for score in scores]:
                    scores.append(("%s %s %s" % (self.headers.index(header), header,str(item)), [self.like(item, self.bfreq[self.headers.index(header)])**2/
                                   (self.like(item, self.bfreq[self.headers.index(header)]) +
                                    self.like(item, self.rfreq[self.headers.index(header)]))]))
                else:
                    scores[[score[0] for score in scores].index("%s %s %s" % (self.headers.index(header),header,str(item)))][1].append(
                        self.like(item, self.bfreq[self.headers.index(header)])**2 /
                        (self.like(item, self.bfreq[self.headers.index(header)]) +
                         self.like(item, self.rfreq[self.headers.index(header)])))
        scores = sorted(scores, key=lambda colscore: median(colscore[1]), reverse=True)
        #for score in scores:
        #    print "%s %.2f" % (score[0], median(score[1]))
        self.scores = scores

    def like(self, item, d):
        if item not in d.keys():
            return 0
        p = d[item]
        pn = 0.0
        for k in d.keys():
            pn += d[k]
        return p/pn

    def top_rules(self, n):
        return [score[0] for score in self.scores][0:n]
