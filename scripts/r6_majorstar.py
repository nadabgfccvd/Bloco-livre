#!/usr/bin/env python3
"""The '12 gold stars' CONFIRMED at ring radius 219-268 (ellipse rx 253 ry 220 fits r by angle:
0deg:268 measured vs 254 predicted; 90deg:219 vs 220; angles 30/60: 262/229 vs 244/227 — close).
Angles: 32.5, 55.9, 89.6, 123.5, 153.1, 179.8, 208.7, 236.7, 270.4, 303.9, 333.4, 359.9
=> spacing 24-30 deg, 12 evenly spaced. 
'Major star': inner comp 15634 at (351,438) r=90 ang=94 — that's a big blob above center;
is it star-shaped? Check its shape profile: width per row.
Also the 1469 at (360,372) r=156 — another star higher up (13th/14th star?).
"""
import sys
sys.path.insert(0, '/home/z/my-project/scripts')
from r6_forensics_lib import *

im = load('07_clear.png'); p = px(im)

def gold_at(x, y):
    c = p[x,y]
    return c[0] > 180 and c[1] > 130 and c[2] < 150 and c[0] > c[2]+40

# shape profile of the big blob at (351,438), bbox x 91..618 y 396..479
print('== big blob (claimed major star?) width per row ==')
for y in range(392, 484, 3):
    xs = [x for x in range(80, 640) if gold_at(x, y)]
    if xs:
        print(f'   y={y}: w={max(xs)-min(xs)+1:4d}  x {min(xs)}..{max(xs)}')

print()
print('== 2nd inner comp at (360,372) bbox x 325..394 y 339..406 ==')
for y in range(336, 410, 3):
    xs = [x for x in range(320, 400) if gold_at(x, y)]
    if xs:
        print(f'   y={y}: w={max(xs)-min(xs)+1:4d}  x {min(xs)}..{max(xs)}')

# star-shape test on a ring star (486,719) bbox 447..526, 680..758
print()
print('== ring star (486,719) width per row ==')
for y in range(678, 760, 3):
    xs = [x for x in range(440, 530) if gold_at(x, y)]
    if xs:
        print(f'   y={y}: w={max(xs)-min(xs)+1:4d}')
