#!/usr/bin/env python3
"""07_clear 'piece cells 13/64' — the star ring overlaps cell detection (stars are bright).
Cross-check: measure filled cells EXCLUDING gold pixels (pieces are colored, stars gold).
"""
import sys
sys.path.insert(0, '/home/z/my-project/scripts')
from r6_forensics_lib import *
from r6_occupancy import XCELLS, YCELLS

im = load('07_clear.png'); p = px(im)
filled = 0
for r,(y0,y1) in enumerate(YCELLS):
    line = ''
    for c,(x0,x1) in enumerate(XCELLS):
        # non-gold, non-empty bright pixels = piece
        hits = 0
        for y in range(y0+10, y1-10, 6):
            for x in range(x0+10, x1-10, 6):
                cc = p[x,y]
                if not is_goldish(cc) and lum(cc) > 60:
                    hits += 1
        f = hits > 8
        filled += f
        line += '#' if f else '.'
    print(line)
print('non-gold bright cells:', filled, '/64')
