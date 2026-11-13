#!/usr/bin/env python3
"""Decode banner text: dark letters on gold fan y100..125. Cluster dark pixels into letters."""
import sys
sys.path.insert(0, '/home/z/my-project/scripts')
from r6_forensics_lib import *
from r6_occupancy import cell_filled, XCELLS, YCELLS

im = load('07_clear.png'); p = px(im)
print('== dark letter clusters on gold fan (y 96..130) ==')
cols = {}
for y in range(96, 132):
    for x in range(0, 720):
        c = p[x,y]
        if lum(c) < 85 and c[2] < 60:
            cols.setdefault(x, []).append(y)
xs = sorted(cols)
cl = []
for x in xs:
    if cl and x - cl[-1][-1] <= 7: cl[-1].append(x)
    else: cl.append([x])
print('letter clusters:', [(c[0], c[-1]) for c in cl])
tot = sum(len(c) for c in cl)
print('letter count approx:', len(cl), 'total dark columns:', tot)

# also r5 main occupancy
im5 = load('01_main_classic.png', R5)
filled = sum(cell_filled(im5, x0,x1,y0,y1) for (y0,y1) in YCELLS for (x0,x1) in XCELLS)
print('R5 01_main piece cells:', filled, '/64')
