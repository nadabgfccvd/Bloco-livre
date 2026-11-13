#!/usr/bin/env python3
"""The banner claim needs sorting. The gold mass y60..179 widens downward from a point at top:
that's a set of RAYS converging downward? Actually n grows 50->208 while x-range widens 297..444 ->
48..669. Looks like a fan/rays burst. The 'banner band' #F6C445 NOT FOUND anywhere.
Check: maybe banner is the horizontal gold band INSIDE board at y 396..479 (component 15634,
x 91..618, 80 rows tall). That's the biggest gold component — a band across the board with
text? Check its structure: is it a band with letters (holes)? Sample colors, height, edges,
white hairline at its top/bottom, symmetry about board cx=358.
"""
import sys
sys.path.insert(0, '/home/z/my-project/scripts')
from r6_forensics_lib import *
from collections import Counter

im = load('07_clear.png'); p = px(im)

# The big component: x 91..618, y 396..479
print('== big gold band component x 91..618 y 396..479 ==')
for y in range(390, 485, 4):
    xs = [x for x in range(60, 660) if is_goldish(p[x,y])]
    if len(xs) > 20:
        print(f'   y={y}: n={len(xs):4d} x {min(xs)}..{max(xs)} center {(min(xs)+max(xs))/2:.1f}')

# exact colors inside band
cc = Counter()
for y in range(396, 480):
    for x in range(91, 619):
        cc[p[x,y]] += 1
print('band top colors:', cc.most_common(10))

# holes = dark/letters inside band bbox
print()
print('== dark holes inside band bbox ==')
dark = Counter()
for y in range(396, 480):
    for x in range(91, 619):
        c = p[x,y]
        if lum(c) < 80:
            dark[(x//20*20)] += 1
print('dark columns (20px bins):', sorted(dark.items())[:20])
print('total dark px in band:', sum(dark.values()))

# white hairline around band?
print()
print('== bright rows in y 380..500 ==')
for y in range(380, 500):
    xs = [x for x in range(0,720) if p[x,y][0]>228 and p[x,y][1]>225 and p[x,y][2]>200]
    if len(xs) > 25:
        print(f'   y={y}: n={len(xs)} x {min(xs)}..{max(xs)}')
