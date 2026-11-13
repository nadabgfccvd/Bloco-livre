#!/usr/bin/env python3
"""Full-board 8x8 occupancy grid for r6 06_full.png + 01_main_classic, using well-separator geometry.
Board: cells separated by dark lines (24,32,46). Grid verticals ~ x=104,188,272,356,440,524,608,692(,~696 edge).
Row lines from y-profile: ~440,526,610,694,778 => cell ~84-86. Find top of grid first.
Empty well colors: 41,52,73 / 50,64,90 (two shades = inner cell / bevel).
"""
import sys
sys.path.insert(0, '/home/z/my-project/scripts')
from r6_forensics_lib import *

im = load('06_full.png'); p = px(im); w,h = im.size

# find all horizontal dark lines in board zone y 300..900
print('== candidate row lines (rows whose mean color is near (24,32,46)) ==')
for y in range(300, 920):
    rs=gs=bs=n=0
    for x in range(112, 690, 4):
        c = p[x,y]; rs+=c[0]; gs+=c[1]; bs+=c[2]; n+=1
    m = (rs/n, gs/n, bs/n)
    if abs(m[0]-24)<8 and abs(m[1]-32)<8 and abs(m[2]-46)<8:
        print(f'y={y} mean=({m[0]:.0f},{m[1]:.0f},{m[2]:.0f})')
