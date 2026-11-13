#!/usr/bin/env python3
"""HUD text measurement (PONTOS vs RECORDE cap heights) on 01_main_classic.png.
Claim: PONTOS 0.24*cell (~20px) vs RECORDE 0.19*cell (~16px).
Text = bright pixels (r,g,b all >150) in HUD zone y 0..190.
Find column clusters (two labels) and row extents.
"""
import sys
sys.path.insert(0, '/home/z/my-project/scripts')
from r6_forensics_lib import *

for name in ['01_main_classic.png', '06_full.png', '07_clear.png']:
    im = load(name); p = px(im)
    print('==', name, '==')
    # bright text mask
    cols = {}
    rows = {}
    for y in range(0, 190):
        for x in range(0, 720):
            c = p[x,y]
            if c[0] > 150 and c[1] > 150 and c[2] > 150:
                cols.setdefault(x, []).append(y)
                rows.setdefault(y, []).append(x)
    if not cols:
        print('   no bright text found in HUD'); continue
    xs = sorted(cols)
    # cluster columns into labels
    clusters = []
    for x in xs:
        if clusters and x - clusters[-1][-1] <= 6: clusters[-1].append(x)
        else: clusters.append([x])
    print('   text column clusters:', [(c[0], c[-1], len(c)) for c in clusters])
    ys = sorted(rows)
    print('   text rows range:', ys[0], '..', ys[-1])
    # row profile per cluster
    for c in clusters:
        x0, x1 = c[0], c[-1]
        yy = [y for y in range(0,190) if any(p[x,y][0]>150 and p[x,y][1]>150 and p[x,y][2]>150 for x in range(x0,x1+1))]
        if yy:
            print(f'   cluster x {x0}..{x1}: rows {yy[0]}..{yy[-1]} height {yy[-1]-yy[0]+1}')
