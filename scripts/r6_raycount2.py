#!/usr/bin/env python3
"""Ray count refinement: rays likely exist only in an annulus NEAR the board (r 260..340),
alternating. Sample r 250..330 only, angle 0..360 step 1.5deg, threshold >2 of 14 samples.
Also lower the gold tolerance: rays alpha 110 over navy bg = dim gold (~140,120,70).
"""
import sys, math
sys.path.insert(0, '/home/z/my-project/scripts')
from r6_forensics_lib import *

im = load('07_clear.png'); p = px(im)
cx, cy = 359, 528

def warm_dim(c):
    return c[0] > 100 and c[0] > c[2] + 30 and c[1] > c[2]*0.8

for (r0, r1, thr) in [(250, 340, 4), (340, 480, 5), (480, 700, 8)]:
    prof = {}
    for a10 in range(0, 3600, 3):
        a = a10/10
        n = 0
        for r in range(r0, r1, 8):
            x = int(cx + r*math.cos(math.radians(a)))
            y = int(cy - r*math.sin(math.radians(a)))
            if 0 <= x < 720 and 0 <= y < 1440 and warm_dim(p[x,y]):
                n += 1
        prof[a10] = n
    sectors = []
    cur = None
    for a10 in sorted(prof):
        if prof[a10] >= thr:
            if cur is None: cur = [a10, a10]
            else: cur[1] = a10
        else:
            if cur: sectors.append((cur[0]/10, (cur[1])/10)); cur = None
    if cur: sectors.append((cur[0]/10, cur[1]/10))
    print(f'r {r0}-{r1} thr {thr}: {len(sectors)} sectors')
    for s in sectors: print(f'   {s[0]:6.1f}..{s[1]:6.1f}')
