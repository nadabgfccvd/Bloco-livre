#!/usr/bin/env python3
"""Ray count: find gaps (dark spokes) in the upper half arc. Between 0..180 deg the gold spans
with minima at 45-60 and 90-105 -> alternating bright/dark spokes. Count distinct bright spokes
by scanning angular profile at fine resolution around origin (359, 528) for radius band 300..700.
"""
import sys, math
sys.path.insert(0, '/home/z/my-project/scripts')
from r6_forensics_lib import *

im = load('07_clear.png'); p = px(im)
cx, cy = 359, 528

# radial profile: for r in 300..700 step 4, sample angle 0..360 step 2deg, count gold
prof = {}
for a10 in range(0, 3600, 5):
    a = a10/10
    n = 0
    for r in range(280, 700, 6):
        x = int(cx + r*math.cos(math.radians(a)))
        y = int(cy - r*math.sin(math.radians(a)))
        if 0 <= x < 720 and 0 <= y < 1440:
            if is_goldish(p[x,y]): n += 1
    prof[a10] = n

# find contiguous bright angular sectors
sectors = []
cur = None
for a10 in sorted(prof):
    if prof[a10] > 3:
        if cur is None: cur = [a10, a10]
        else: cur[1] = a10
    else:
        if cur: sectors.append((cur[0]/10, cur[1]/10, cur[1]-cur[0])); cur = None
if cur: sectors.append((cur[0]/10, cur[1]/10, cur[1]-cur[0]))
print('bright angular sectors (deg, width*0.1):')
for s in sectors: print(f'   {s[0]:6.1f} .. {s[1]:6.1f}  width {s[2]/10:.1f} deg')
print('sector count:', len(sectors))
