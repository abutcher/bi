from NaiveBayes import *
from knn import *
from util import distance
import sys
from runtime import *
import math

# This contains functions for defect prediction statistics.  If you're looking
# for related functions such as MRE() that aren't in this file, check util.py.

#@print_timing
def PerformIDEACluster(clusters,test,dataset="Unknown", treatment="IDEACLUSTER", disregardY=False):
    Stats = DefectStats()
    if type(test[0].klass()) is str:
        for instance in test:
            Closest = [sys.maxint, None]
            for cluster in clusters:
                for quadrant in cluster.quadrants:
                    if distance(instance.Coord(), quadrant.center()) < Closest[0]:
                        Closest[0] = distance(instance.Coord(), quadrant.center())
                        Closest[1] = cluster
            train = []
            for quadrant in Closest[1].quadrants:
                train.extend(quadrant.ClassCoords())
            Stats.Evaluate(NaiveBayesClassify(instance.Coord(),train, disregardY), instance.klass())
        Stats.StatsLine(dataset, treatment)
    del Stats

#@print_timing
def PerformBaseline(data,test,dataset="Unknown",treatment="None"):
    Stats = DefectStats()
    if type(test[0].klass()) is str:
        train = [ inst.datum for inst in data ]
        for instance in test:
            Stats.Evaluate(NaiveBayesClassify(instance.datum, train), instance.klass())
        Stats.StatsLine(dataset,treatment)
    del Stats

def PrintHeaderLine():
    print "dataset,treatment,CLASS,TotalNumOfClass,A,B,C,D,pd,pf,precision,accuracy,HarmonicMean"

class DefectStats:
    # TRUE && FALSE is [a,b,c,d]

    def __init__(self):
        self.TRUE = [0,0,0,0]
        self.FALSE = [0,0,0,0]

    def Evaluate(self,Got, Want):
        if Got.lower() == Want.lower():
            if Got.lower() == "true" or Got.lower() == "yes":
                #print "true match"
                self.incf("TRUE","d")
                self.incf("FALSE","a")
            elif Got.lower() == "false" or Got.lower() == "no":
                #print "false match"
                self.incf("FALSE","d")
                self.incf("TRUE","a")
        elif Got.lower() != Want.lower():
            if Got.lower() == "true" or Got.lower() == "yes":
                #print "got true mismatch"
                self.incf("TRUE","c")
                self.incf("FALSE","b")
            elif Got.lower() == "false" or Got.lower() == "no":
                #print "got false mismatch"
                self.incf("FALSE","c")
                self.incf("TRUE","b")

    def incf(self,CLASS, pos):
        if CLASS is "TRUE":
            if pos is "a":
                self.TRUE[0] = self.TRUE[0] + 1
                #print(self.TRUE)
            elif pos is "b":
                self.TRUE[1] = self.TRUE[1] + 1
                #print(self.TRUE)
            elif pos is "c":
                self.TRUE[2] = self.TRUE[2] + 1
                #print (self.TRUE)
            elif pos is "d":
                self.TRUE[3] = self.TRUE[3] + 1
                #print (self.TRUE)
        elif CLASS is "FALSE":
            if pos is "a":
                self.FALSE[0] = self.FALSE[0] + 1
            elif pos is "b":
                self.FALSE[1] = self.FALSE[1] + 1
            elif pos is "c":
                self.FALSE[2] = self.FALSE[2] + 1
            elif pos is "d":
                self.FALSE[3] = self.FALSE[3] + 1

    def precision(self,CLASS):
        try:
            return float(self.__D__(CLASS)) / float((self.__C__(CLASS) + self.__D__(CLASS)))
        except:
            return 0.0

    def accuracy(self,CLASS):
        try:
            return float((self.__A__(CLASS) + self.__D__(CLASS))) / float((self.__A__(CLASS) + self.__B__(CLASS) + self.__C__(CLASS) + self.__D__(CLASS)))
        except:
            return 0.0

    def pd(self,CLASS):
        try:
            return float(self.__D__(CLASS)) / float((self.__B__(CLASS) + self.__D__(CLASS)))
        except:
            return 0.0

    def pf(self,CLASS):
        try:
            return float(self.__C__(CLASS)) / float((self.__A__(CLASS) + self.__C__(CLASS)))
        except:
            return 0.0

    def ClassCount(self,CLASS):
        try:
            return float(self.__B__(CLASS) + self.__D__(CLASS))
        except:
            return 0.0

    def HarmonicMean(self,CLASS):
        try:
            return float((2 * (1 - self.pf(CLASS)) * self.pd(CLASS))) / float(((1 - self.pf(CLASS)) + self.pd(CLASS)))
        except:
            return 0.0

    def Count(self, CLASS):
        return self.__A__(CLASS) + self.__B__(CLASS) + self.__C__(CLASS) + self.__D__(CLASS)

    def StatsLine(self, dataset,treatment):
        print "%s,%s,%s,%d, %d,%d,%d,%d,%.3f,%.3f,%.3f,%.3f,%.3f" % (dataset,treatment,"TRUE",self.ClassCount("TRUE"),self.__A__("TRUE"),self.__B__("TRUE"),self.__C__("TRUE"), self.__D__("TRUE"), self.pd("TRUE"), self.pf("TRUE"), self.precision("TRUE"), self.accuracy("TRUE"), self.HarmonicMean("TRUE"))
        print "%s,%s,%s,%d,%d, %d,%d,%d,%.3f,%.3f,%.3f,%.3f,%.3f" % (dataset, treatment, "FALSE",self.ClassCount("FALSE"),self.__A__("FALSE"),self.__B__("FALSE"), self.__C__("FALSE"), self.__D__("FALSE"), self.pd("FALSE"), self.pf("FALSE"), self.precision("FALSE"), self.accuracy("FALSE"), self.HarmonicMean("FALSE"))


    # Private classes for grabbing A,B,C, and D
    def __A__(self,CLASS):
        if CLASS is "TRUE":
            return self.TRUE[0]
        elif CLASS is "FALSE":
            return self.FALSE[0]

    def __B__(self,CLASS):
        if CLASS is "TRUE":
            return self.TRUE[1]
        elif CLASS is "FALSE":
            return self.FALSE[1]

    def __C__(self,CLASS):
        if CLASS is "TRUE":
            return self.TRUE[2]
        elif CLASS is "FALSE":
            return self.FALSE[2]

    def __D__(self,CLASS):
        if CLASS is "TRUE":
            return self.TRUE[3]
        elif CLASS is "FALSE":
            return self.FALSE[3]

class EffortStats:

    def __init__(self):
        self.mre_list = []
        self.pred_25_list = []
        self.pred_30_list = []

    def Evaluate(self, got, want):
        self.mre_list.append(math.fabs(got - want) / want)
        if self.within_x_percent(got, want, .25):
            self.pred_25_list.append(got)
        if self.within_x_percent(got, want, .30):
            self.pred_30_list.append(got)

    def MDMRE(self):
        return median(self.mre_list)

    def PRED25(self):
        return (float(len(self.pred_25_list))/float(len(self.mre_list)))*100

    def PRED30(self):
        return (float(len(self.pred_30_list))/float(len(self.mre_list)))*100

    def within_x_percent(self, got, want, x):
        upper = want * (1 + x)
        lower = want * (1 - x)

        if got > lower and got < upper:
            return True
        else:
            return False
