#!/usr/bin/env python3
"""Final claim 2 check: banner symmetric, underlay centered cx.
The gold wedge y 390..479 sweeps right-to-left; com_x moves 385->463->332->181.
That is a DIAGONAL sweep, definitely NOT centered/symmetric on 358.
But wait: maybe the wedge is the 'banner underlay' with slide offset FIXED = the claim says
'no slide offset'. A centered underlay would keep com_x ~358. It doesn't.
However maybe the actual BANNER (the ribbon) is the y100..179 fan? Let's check its symmetry:
the fan above the board y60..179: x extents 48..669 at y174 — center (48+669)/2 = 358.5. SYMMETRIC!
And it grows from a point at top y60 x297..444 (center 370). So the fan is a ray burst centered.
Check fan horizontal symmetry per row: min/max mirrored about 358/360?
"""
import sys
sys.path.insert(0, '/home/z/my-project/scripts')
from r6_forensics_lib import *

im = load('07_clear.png'); p = px(im)
print('== top fan/rays symmetry about x=359 ==')
for y in range(55, 185, 5):
    xs = [x for x in range(0, 720) if is_goldish(p[x,y])]
    if xs:
        lo, hi = min(xs), max(xs)
        print(f'   y={y:3d}: lo={lo:3d} hi={hi:3d} center={(lo+hi)/2:6.1f} width={hi-lo+1:4d} mirror_gap_L={359-lo} R={hi-359}')

# vertical center of the fan
print()
print('== rays: count alternating? radial gold spokes above board ==')
import math
cx, cy = 359, 190  # origin at board top edge
spokes = {}
for y in range(20, 190):
    for x in range(0, 720):
        if is_goldish(p[x,y]):
            a = round(math.degrees(math.atan2(-(y-cy), x-cx)) % 360)
            spokes.setdefault(a//6, []).append(1)
ang_hist = {k: len(v) for k,v in spokes.items()}
# print coarse 15-deg histogram
print('15-deg bins above-board gold:')
for b in range(0, 360, 15):
    n = sum(ang_hist.get(a//6,0) for a in range(b, b+15) if (a//6) in ang_hist)
    print(f'   {b:3d}-{b+15:3d}: {n:5d} {"#"*min(20,n//100)}')
