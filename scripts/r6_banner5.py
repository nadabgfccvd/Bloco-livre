#!/usr/bin/env python3
"""Star shape verdict:
- Ring star (486,719): widths 2->76->3 over 78 rows: 4-pointed star (diamond/starburst). GOOD.
- 'Major star' at (360,372): widths 2->70->2 over 67 rows: a proper 4-point star, size 1469. 
  That IS a star — but is it 'major'? size 1469 vs ring stars 743-1929. NOT bigger. It sits INSIDE the
  ring at r=156, above center (the '1 major star' claimed INSIDE board over wells).
- The 15634 blob is a wide wedge (w up to 511) sweeping from upper-right down to left — that's the
  banner/wave UNDERLAY or a giant diagonal sweep, not a star.
So 'crown of 12 stars + 1 major star': 12 ring stars CONFIRMED; major star exists at (360,372)
but is smaller than several ring stars (1469 vs 1929) — 'major' is a lie, or the 15634 blob is
the 'major star' and it is NOT star-shaped (it's a diagonal wedge 511px wide).
Banner underlay: claim rows 466..698 center 582. Measured wedge occupies y 392..479, center-of-mass
moves from x~360 (top) to x~104 (bottom) — a diagonal sweep, NOT centered at 582, NOT symmetric.
"""
import sys
sys.path.insert(0, '/home/z/my-project/scripts')
from r6_forensics_lib import *
from collections import Counter

# The wedge: where does banner underlay sit? rows 466..698 claim. Measure gold center of mass per row over y 380..700
im = load('07_clear.png'); p = px(im)
print('== gold center-of-mass per row y 380..720 (banner underlay zone) ==')
for y in range(380, 720, 10):
    xs = [x for x in range(0, 720) if is_goldish(p[x,y])]
    if xs:
        print(f'   y={y:4d}: n={len(xs):4d} com_x={sum(xs)/len(xs):6.1f} span {min(xs)}..{max(xs)}')

# Also HUD top: PONTOS/RECORDE in 07_clear — the white text band y 29..53 has letters x209..504;
# in 07_clear band y29..76 has clusters 383..415 & 424..446 taller (48) = gold 'PARABENS'? measure colors
print()
print('== 07_clear HUD letter colors ==')
cc = Counter()
for y in range(29, 77):
    for x in range(209, 505):
        c = p[x,y]
        if lum(c) > 100: cc[c] += 1
print('bright letters colors:', cc.most_common(6))
