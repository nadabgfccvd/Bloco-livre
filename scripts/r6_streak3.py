#!/usr/bin/env python3
"""ALL letters same height 23px. Claim PONTOS 0.24cell(20px) vs RECORDE 0.19cell(16px) = FALSE
at label level. BUT the claim might be about VALUE digits: band2 y64..80 h=13..16 vs band1 23.
Check value digit heights: spans x154..363 (PONTOS value), x383..496 (RECORDE value), x516..565 (level?).
Earlier: (65,80,16) for 154..363; (64,76,13) for 383..496. So PONTOS value 16px vs RECORDE value 13px:
that IS a hierarchy, but it's the VALUES, and reversed claim numbers (0.24 vs 0.19 = 20 vs 16).
Measured: labels both 23px; values 16 vs 13px. So hierarchy exists but weakly (3px delta) and not
the claimed sizes. PARTIAL.
Now: streak strip instrument details — pips at 25%? bar 446px claim. R6 main bar only 18px wide
(green, empty board), R6 full bar 363px. Track? Check for track outline (dim gray) around bar.
Also combo pips + stars: bright rows 1203..1214 etc. Analyze those rows' shapes.
"""
import sys
sys.path.insert(0, '/home/z/my-project/scripts')
from r6_forensics_lib import *
from collections import Counter

im = load('01_main_classic.png'); p = px(im)
print('== streak strip bright elements (lum>140) rows 1190..1300 ==')
for y in range(1190, 1300):
    xs = [x for x in range(0,720) if lum(p[x,y]) > 140]
    if len(xs) > 5:
        # cluster
        cl = []
        for x in xs:
            if cl and x - cl[-1][-1] <= 6: cl[-1].append(x)
            else: cl.append([x])
        print(f'   y={y}: {[(c[0],c[-1]) for c in cl if len(c)>1]}')

print()
print('== label text in strip (rows 1260..1400) ==')
for y in range(1260, 1440, 2):
    xs = [x for x in range(0,720) if lum(p[x,y]) > 100]
    if len(xs) > 8:
        cl = []
        for x in xs:
            if cl and x - cl[-1][-1] <= 8: cl[-1].append(x)
            else: cl.append([x])
        print(f'   y={y}: spans {[(c[0],c[-1]) for c in cl if len(c)>2]}')
