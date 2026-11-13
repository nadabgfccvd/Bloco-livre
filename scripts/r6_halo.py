#!/usr/bin/env python3
"""Ray verdict: no 12 discrete rays. The gold burst above board (y60..179) is a symmetric fan
centered on 359 (mirror gaps L/R within 1-6px from y65..175) that WIDENS downward — looks like
a cone/trumpet flare, plus a contiguous bright arc 51..128 deg in r340-480. No alternating
spoke structure found at any annulus. '12 alternating glory rays' = VAPOR (at best a smooth fan).
Halo: '3 layers alpha 96/72/60 outside board, 216px' — measured outside-board goldish = 69104px,
edges lum 119 vs bg 20 — halo EXISTS and is strong; but layering/alpha can't be confirmed as
3 distinct layers. Check radial luminance steps outside board edges.
"""
import sys
sys.path.insert(0, '/home/z/my-project/scripts')
from r6_forensics_lib import *

im = load('07_clear.png'); p = px(im)
print('== radial profile from board edges (left/right/above) ==')
print('left edge x: lum at y=528')
for d in range(0, 24, 2):
    x = 20 - d
    if x >= 0:
        c = p[x, 528]
        print(f'   x={x:3d}: ({c[0]:3d},{c[1]:3d},{c[2]:3d}) lum={lum(c):5.1f}')
print('above board y: at x=359')
for d in range(0, 100, 4):
    y = 190 - d
    if y >= 0:
        c = p[359, y]
        print(f'   y={y:3d}: ({c[0]:3d},{c[1]:3d},{c[2]:3d}) lum={lum(c):5.1f}')
print('below board y: at x=359')
for d in range(0, 90, 4):
    y = 866 + d
    if y < 1440:
        c = p[359, y]
        print(f'   y={y:4d}: ({c[0]:3d},{c[1]:3d},{c[2]:3d}) lum={lum(c):5.1f}')
