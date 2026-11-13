#!/usr/bin/env python3
"""Banner band check on 07_clear: we found gold rows y100..179 (mean cx 360.8) spanning full width.
That's the BANNER (claims: banner band #F6C445 with white hairline, underlay rows 466..698).
Where is the banner really? And what's at rows 466..698? Let's map gold mass per row and column.
"""
import sys
sys.path.insert(0, '/home/z/my-project/scripts')
from r6_forensics_lib import *

im = load('07_clear.png'); p = px(im)
print('== goldish pixels per row (stride 3) ==')
for y in range(0, 1440, 6):
    n = sum(1 for x in range(0, 720, 3) if is_goldish(p[x,y]))
    if n > 30:
        xs = [x for x in range(0,720,3) if is_goldish(p[x,y])]
        print(f'y={y:4d}: n={n:4d} x {min(xs):3d}..{max(xs):3d}')
