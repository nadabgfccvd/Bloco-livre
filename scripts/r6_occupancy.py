#!/usr/bin/env python3
"""Occupancy measurement for 06_full and 01_main_classic.
Grid rows: line centers at y ~ 275,359,444,529,613,698,782 (+ top edge ~193? no that's HUD zone).
Board top row starts above 275. Cell = ~84.5. Board rows: interior lines 275..782 => 6 interior separators
=> 7 rows between 193..782? y=193 is HUD boundary. Board top edge likely ~190; bottom edge ~866.
We'll assume 8 rows: centers at 275-42=233... Actually rows between lines: [193,275],[275,359],... [782,866].
Cell centers: 234,317,401,486,570,655,740,824 approx (midpoints).
Columns: lines at 104,188,272,356,440,524,608,692 => cells between [104..188],[188..272]... wait 8 cols need 9 lines.
Column lines found at ~104,188,272,356,440,524,608,692 -> that's 8 lines => 7-8 cols; edges at 20 and 696.
Columns between: 20..104, 104..188, ..., 692..696? Use 9 boundaries: 20,104,188,272,356,440,524,608,692,676? no.
Let's use edges 20..696 with separators at 104,188,272,356,440,524,608,692 => col cells: [20,104],[104,188],[188,272],[272,356],[356,440],[440,524],[524,608],[608,692],[692,696]-invalid.
=> 8 full columns + margin. Good: 8x8 grid, cell ~84x84.
"""
import sys
sys.path.insert(0, '/home/z/my-project/scripts')
from r6_forensics_lib import *

X_EDGES = [20, 104, 188, 272, 356, 440, 524, 608, 692, 696]
# drop last partial
XCELLS = [(X_EDGES[i], X_EDGES[i+1]) for i in range(8)]
Y_EDGES = [190, 275, 359, 444, 529, 613, 698, 782, 866]
YCELLS = [(Y_EDGES[i], Y_EDGES[i+1]) for i in range(8)]

EMPTY = {(41,52,73),(50,64,90)}

def cell_filled(im, x0, x1, y0, y1):
    p = px(im)
    # sample 5x5 interior points, median deviation from both empty shades
    xs = [x0 + int((x1-x0)*f) for f in (0.25,0.5,0.75)]
    ys = [y0 + int((y1-y0)*f) for f in (0.3,0.5,0.7)]
    devs = []
    for x in xs:
        for y in ys:
            c = p[x,y]
            d = min(abs(c[0]-41)+abs(c[1]-52)+abs(c[2]-73), abs(c[0]-50)+abs(c[1]-64)+abs(c[2]-90))
            devs.append(d)
    devs.sort()
    return devs[len(devs)//2] > 60  # median deviation threshold

def grid_report(name):
    im = load(name)
    print('==', name, '==')
    filled = 0
    rows = []
    for r,(y0,y1) in enumerate(YCELLS):
        line = ''
        for c,(x0,x1) in enumerate(XCELLS):
            f = cell_filled(im, x0,x1,y0,y1)
            filled += f
            line += '#' if f else '.'
        rows.append(line)
        print('   ', line)
    print('   filled cells:', filled, '/ 64 =', round(filled/64*100,1), '%')
    return filled

grid_report('06_full.png')
print()
grid_report('01_main_classic.png')
print()
grid_report('02_skin0.png')
