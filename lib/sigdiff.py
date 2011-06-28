#!/opt/local/bin/python2.6

from scipy import stats

cr = [0, 0, 0, 0, 2, 3, 14] 
cb = [0, 0, 1, 3, 4, 4, 14]
cl = [0, 0, 0, 0, 0, 0, 4]
cc = [0, 0, 0, 0, 0, 0, 3]

sr = [3, 3, 3, 5, 7, 7, 14]
sb = [0, 2, 4, 6, 7, 10, 29]
sl = [0, 0, 0, 3, 3, 4, 14]
sc = [0, 0, 0, 0, 2, 3, 14]

wr = [100, 100, 100, 100, 100, 100, 100]
wb = [17, 23, 30, 32, 40, 57, 60]
wl = [0, 2, 17, 21, 23, 39, 43]
wc = [0, 3, 6, 7, 9, 11, 57]

if stats.mannwhitneyu(cb, cr)[1] > 0.5:
    print "cb diff from cr"

if stats.mannwhitneyu(cl, cb)[1] > 0.5:
    print "cl diff from cb"    
    
if stats.mannwhitneyu(cc, cl)[1] > 0.5:
    print "cc diff from cl"

if stats.mannwhitneyu(sb, sr)[1] > 0.5:
    print "sb diff from sr"

if stats.mannwhitneyu(sl, sb)[1] > 0.5:
    print "sl diff from sb"

if stats.mannwhitneyu(sc, sl)[1] > 0.5:
    print "sc diff from sl"

if stats.mannwhitneyu(wb, wr)[1] > 0.5:
    print "wb diff from wr"

if stats.mannwhitneyu(wl, wb)[1] > 0.5:
    print "wl diff from wb"

if stats.mannwhitneyu(wc, wl)[1] > 0.5:
    print "wc diff from wl"    
