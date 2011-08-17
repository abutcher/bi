#!/opt/local/bin/python2.6
from arff import *
from discretize import *
from copy import deepcopy
import numpy as np
from util import *

import matplotlib
matplotlib.use('WXAgg')
import matplotlib.pyplot as plt

def empiricalcdf(data, method='Hazen'):
    i = np.argsort(np.argsort(data)) + 1
    nobs = len(data)
    method = method.lower()
    if method == 'hazen':
        cdf = (i-0.5)/nobs
    elif method == 'weibull':
        cdf = i/(nobs+1.)
    elif method == 'california':
        cdf = (i-1.)/nobs
    elif method == 'chegodayev':
        cdf = (i-.3)/(nobs+.4)
    elif method == 'cunnane':
        cdf = (i-.4)/(nobs+.2)
    elif method == 'gringorten':
        cdf = (i-.44)/(nobs+.12)
    else:
        raise 'Unknown method. Choose among Weibull, Hazen, Chegodayev, Cunnane, Gringorten and California.' 
    return cdf

class CDF:
    def __init__(self, datums, you):
        self.datums = datums
        self.datums.append(you)
        self.cdf = empiricalcdf([datum[-1] for datum in self.datums])

        you_y = self.cdf[-1]

        self.scdf = sorted(self.cdf)

        y = [self.scdf[i]*100 for i in range(len(self.scdf))]
        x = [i for i in range(len(self.scdf))]
        
        plt.plot(x,y,"bo", markersize=2)
        plt.plot(self.scdf.index(you_y), you_y*100, "ro", markersize=10)

        plt.show()
        
if __name__ == '__main__':
    arff = Arff('data/china.arff')
    CDF(arff.data, random_element(arff.data))

