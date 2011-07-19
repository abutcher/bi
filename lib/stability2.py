#!/opt/local/bin/python2.6

from arff import *
from util import *
from instance import *
from quadrant import *
from gridclus2 import *
from discretize import *
from copy import deepcopy
from which2 import *
import argparse
from discretize import *

def main():
    args = parse_options()
    arff = Arff(args.train[0])

    arff.headers.remove("name")
    arff.data = remove_column(arff.data, 0)
    o_len = len(arff.data)

    print "Length of original data is:", len(arff.data)

    for i in range(6):

        print "Removed up to %.2f percent of the data." % (i*0.1)

        if i != 0:
            arff.data = remove_x_percent(arff.data, 0.1, o_len)
        print "Current length of data:", len(arff.data)

        random.shuffle(arff.data, random.random)
        train = discretize(arff.data, 7)
        test = train[0:9]

        d_rules = [[] for t in test]

        for i in range(args.xval):
            dc = DataCollection(train) 
            ic = InstanceCollection(dc)
            ic.normalize_coordinates()

            testXY = []
            for datum in test:
                for instance in ic.instances:
                    if instance.datum == datum:
                        testXY.append(instance)
                        ic.instances.remove(instance)

            testXY = log_x(log_y(deepcopy(testXY)))
            trainXY = log_x(log_y(deepcopy(ic.instances)))

            quad_tree = QuadrantTree(trainXY)
            quadrants = QuadrantTree(trainXY).leaves()
            clusters = GRIDCLUS(quadrants)

            for instance in testXY:
                Closest = [sys.maxint, None]
                for cluster in [cluster for cluster in clusters if len(cluster.datums()) > 20]:
                    for quadrant in cluster.quadrants:
                        if distance(instance.Coord(), quadrant.center()) < Closest[0]:
                            Closest[0] = distance(instance.Coord(), quadrant.center())
                            Closest[1] = cluster
                rules = which2n(arff.headers, Closest[1].datums())
                d_rules[testXY.index(instance)].append(rules[0])

        for rule_list in d_rules:
            unique_rules = []
            rule_strings = [rule.describe_short() for rule in rule_list]
            for rule in rule_list:
                if rule.describe_short() not in unique_rules:
                    unique_rules.append(rule.describe_short())
            print d_rules.index(rule_list)
            for rule in unique_rules:
                count = float(rule_strings.count(rule))
                all = float(len(rule_strings))
                print rule, (count/all)*100
            print ""
    
def parse_options():
    """Place new options that you would like to be parsed here."""
    parser = argparse.ArgumentParser(description='Perform IDEA on given train and test sets.')
    parser.add_argument('--train',
                        dest='train',
                        metavar='FILE',
                        type=str,
                        nargs='+',
                        help='Specify arff file[s] from which to construct the training set.')
    parser.add_argument('--xval',
                        dest='xval',
                        metavar='INT',
                        type=int,
                        help='Specify the number of folds for cross validation.')
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    main()
