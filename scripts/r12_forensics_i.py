#!/usr/bin/env python3
"""R12 part I: locate the actual star shape; it's likely around x26-185 y280-348 (left), per gold map.
Also compare to r11 same region, plus x619-692 right cluster. And what is at y196-264 x26-185?"""
from PIL import Image
import numpy as np

R12 = '/home/z/my-project/critic_shots/r12/'
R11 = '/home/z/my-project/critic_shots/r11/'

def load(p):
    return np.asarray(Image.open(p).convert('RGB')).astype(int)

imh = load(R12 + '01_hero.png')
R, G, B = imh[:,:,0], imh[:,:,1], imh[:,:,2]
gold = (R > 200) & (G > 150) & (B < 200) & (R - B > 80)

# Cluster gold by (row, col) connected regions roughly: split by columns
ys, xs = np.where(gold)
m = (ys >= 190) & (ys < 365)

# three column groups
for lo, hi, label in [(0, 200, 'LEFT x<200'), (200, 620, 'CENTER 200-620'), (620, 720, 'RIGHT x>620')]:
    sel = m & (xs >= lo) & (xs < hi)
    if sel.sum():
        print(f"{label}: n={sel.sum()} rows {ys[sel].min()}..{ys[sel].max()} cols {xs[sel].min()}..{xs[sel].max()}")

# LEFT cluster detail: row profile
sel = m & (xs < 200)
if sel.sum():
    import collections
    cnt = collections.Counter(ys[sel])
    print("\nLEFT cluster row histogram (every row with count):")
    tot = 0
    for y in sorted(cnt):
        print(y, cnt[y])

# CENTER cluster: is there anything? The claim says star center around x360.
selc = m & (xs >= 200) & (xs < 620)
print("\nCENTER n=", selc.sum())
if selc.sum():
    cnt = collections.Counter(ys[selc])
    print("CENTER rows:", sorted(cnt))
    print("CENTER cols:", sorted(set(xs[selc]))[:20], "...")

# RIGHT cluster rows
selr = m & (xs >= 620)
if selr.sum():
    print("\nRIGHT rows:", sorted(set(ys[selr]))[:30])
