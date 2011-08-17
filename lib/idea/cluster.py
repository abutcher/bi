from copy import deepcopy
from util import *
from NaiveBayes import *
from statistics import *
import numpy as np

class Cluster:

    def __init__(self, quadrants):
        self.quadrants = quadrants
        self.stats = DefectStats()

    def __init__(self):
        self.quadrants = []
        self.mark = False
        self.stats = DefectStats()        
    
    def add_quadrant(self, quadrant):
        self.quadrants.append(quadrant)

    def set_mark(self):
        self.mark = True
        
    def datums(self):
        instances = []
        for quadrant in self.quadrants:
            instances.extend(quadrant.instances)
        return [ inst.datum for inst in instances ]

    def instances(self):
        instances = []
        for quadrant in self.quadrants:
            instances.extend(quadrant.instances)
        return instances

    def is_neighbor(self, other_cluster):
        result = False
        for i in range(len(self.quadrants)):
            for j in range(len(other_cluster.quadrants)):
                a = self.quadrants[i]
                b = other_cluster.quadrants[j]
                if (((a.xmin == b.xmax) or (a.xmax == b.xmin)) or ((a.ymin == b.ymax) or (a.ymax == b.ymin))) and not self == other_cluster:
                    result = True
        return result

    def neighbors(self, other_clusters):
        neighbors = []
        for c in other_clusters:
            if c is not self and self.is_neighbor(c):
                neighbors.append(c)
        return neighbors

    def neighbor_count(self, other_clusters):
        return len(self.neighbors(other_clusters))

    def cmedian(self):
        return np.average([quad.qmedian() for quad in self.quadrants if len(filter(lambda d: d[-1] != '?', quad.datums())) != 0])
        
def cluster_prune(clusters, pct):
    if len(clusters) == 1:
        return clusters
    cvars = []
    for cluster in clusters:
        cvars.append((entropy(cluster.datums()), cluster))
    cvars = sorted(cvars, key=lambda cluster: cluster[0])
    return [ cvar[1] for cvar in cvars[0:(len(cvars))-int(round((len(cvars))*pct))] ]

def classify(datum, datums, input_type=None):
    if input_type is None:
        if type(datums[0][-1]) is str:
            input_type="DEFECT"
        else:
            input_type="EFFORT"
    if input_type == "DEFECT":
        return NaiveBayesClassify(datum,datums)
    elif InputType == "EFFORT":
        neighbors = kNearestNeighbors(datum,datums)
        return median(neighbors)


def prune_clusters_classic_within_max(clusters, cull, t="SCORE"):
    clusters_copy = deepcopy(clusters)
    culled_clusters = []

    if t == "VARIANCE":
        clusters_copy = sorted(clusters_copy, key=lambda clus: variance(clus.datums()), reverse=True)
        maxn = variance(clusters_copy[0].datums())
    elif t == "SCORE":
        clusters_copy = sorted(clusters_copy, key=lambda clus: clus.stats.HarmonicMean("TRUE"))
        maxn = clusters_copy[0].stats.HarmonicMean("TRUE")
    else:
        print "You're a towel!"
            
    for cluster in clusters_copy:
        if t == "SCORE" and (maxn+(maxn*cull)) > cluster.stats.HarmonicMean("TRUE") and (maxn-(maxn*cull)) < cluster.stats.HarmonicMean("TRUE") and len(clusters_copy) - len(culled_clusters) > 1:
            culled_clusters.append(cluster)
        elif t == "VARIANCE":
            if ((maxn+(maxn*cull)) > variance(cluster.datums()) or (maxn-(maxn*cull)) < variance(cluster.datums())) and len(clusters_copy) - len(culled_clusters) > 1:
                culled_clusters.append(cluster)

    for cluster in culled_clusters:
        clusters_copy.remove(cluster)

    return clusters_copy, culled_clusters

def prune_clusters_classic(clusters, cull, type="SCORE"):
    clusters_copy = deepcopy(clusters)
    culled_clusters = []

    if type == "VARIANCE":
        clusters_copy = sorted(clusters_copy, key=lambda clus: entropy(clus.datums()), reverse=True)
    elif type == "SCORE":
        clusters_copy = sorted(clusters_copy, key=lambda clus: clus.stats.HarmonicMean("TRUE"))
    else:
        print "You're a towel!"
            
    for cluster in clusters_copy:
        if len(culled_clusters) < int(math.ceil(len(clusters_copy) * cull)) and len(clusters_copy) - len(culled_clusters) > 1:
            culled_clusters.append(cluster)

    for cluster in culled_clusters:
        clusters_copy.remove(cluster)

    return clusters_copy, culled_clusters

def prune_rogue_clusters(clusters, cull):
    clusters_copy = deepcopy(clusters)
    culled_clusters = []
    neighbors = []

    clusters_copy = sorted(clusters_copy, key=lambda cluster: cluster.stats.HarmonicMean("TRUE"))

    for i in range(len(clusters_copy)):
        neighbor_list = []
        for j in range(len(clusters_copy)):
            if clusters[i].is_neighbor(clusters_copy[j]):
                neighbor_list.append(clusters_copy[j])
        neighbors.append(neighbor_list)

    # Loop through and delete the lowest X% and all of their immediate
    # neighbors, as they may be lying to us...
    for i in range(len(clusters_copy)):
        if i < int(math.ceil(len(clusters_copy) * cull)) and len(clusters_copy) > 1:
            culled_clusters.append(clusters_copy[i])
            clusters_copy.remove(clusters_copy[i])
            for neighbor in neighbors[i]:
                if len(clusters_copy) > 2:
                    culled_clusters.append(neighbor)
                    if neighbor in clusters_copy:
                        clusters_copy.remove(neighbor)

    return clusters_copy, culled_clusters
