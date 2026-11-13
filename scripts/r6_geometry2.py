#!/usr/bin/env python3
"""Locate board bounds precisely: horizontal grid lines at y approx 440,526,610,694,778
   => cell height ~84; find left/right board edges and top/bottom.
   Also locate HUD (top), tray, streak strip (bottom)."""
import sys
sys.path.insert(0, '/home/z/my-project/scripts')
from r6_forensics_lib import *

im = load('01_main_classic.png'); p = px(im); w, h = im.size

# The gaps at x=192, 360, 528 (darker columns) inside board zone: those are vertical well separators?
# Check vertical line profile at a single y inside a row of wells
for y in (470, 555, 640):
    print(f'-- vertical profile at y={y} (x 24..696 step 8) --')
    xs = []
    for x in range(24, 700, 4):
        c = p[x, y]
        xs.append((x, c))
    # print compressed
    s = []
    for x, c in xs:
        s.append(f'{x}:{c[0]},{c[1]},{c[2]}')
    print(' '.join(s[:40]))
    print(' '.join(s[40:80]))
    print(' '.join(s[80:]))
    print()

# Detect exact vertical edges of the board: look at row y=470 transitions
print('== transitions at y=470 ==')
prev = None
for x in range(0, w):
    c = p[x, y] if False else p[x, 470]
    if prev:
        d = abs(c[0]-prev[0])+abs(c[1]-prev[1])+abs(c[2]-prev[2])
        if d > 60:
            print(f'x={x} from {prev} to {c}')
    prev = c

# Horizontal grid lines: scan rows 830..950 for bottom of board / tray zone
print()
print('== bottom zone colors (y 840..1110, mean per 12px band) ==')
for y in range(840, 1115, 12):
    rs=gs=bs=n=0
    for x in range(40, 680, 8):
        c = p[x, y]; rs+=c[0]; gs+=c[1]; bs+=c[2]; n+=1
    print(f'y={y:4d} rgb=({rs//n:3d},{gs//n:3d},{bs//n:3d})')
