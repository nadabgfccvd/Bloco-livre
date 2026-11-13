#!/usr/bin/env python3
"""Verify banner text exists in the gold fan area — look at MEDIUM-dark pixels (alpha-blended text
on gold would be dark gold (28,22,15)-ish as found earlier: dark holes in band bbox x 80..460 y 396..479
had 24815 dark px = THE TEXT ON THE WEDGE! That's the banner text 'PARABENS'/'LIVRE!' etc.
Letters: dark columns 20px bins showed x 80..460 dense. The wedge y 396..479 IS the banner:
a gold ribbon sweeping across the board with dark text on it. Center of wedge text zone ~x270
— left of board center 358. The wedge com moved 385->181: asymmetric diagonal ribbon.
Measure the text letter heights on the wedge."""
import sys
sys.path.insert(0, '/home/z/my-project/scripts')
from r6_forensics_lib import *

im = load('07_clear.png'); p = px(im)
print('== dark text rows on wedge (y 396..479, x 91..618) ==')
rows = {}
for y in range(390, 485):
    n = sum(1 for x in range(91, 619) if lum(p[x,y]) < 80)
    if n > 10: rows[y] = n
ys = sorted(rows)
if ys:
    print(f'text rows {ys[0]}..{ys[-1]} height {ys[-1]-ys[0]+1}')
    for y in ys[::4]: print(f'   y={y}: n={rows[y]}')

# letter clusters in that band
cols = {}
for y in range(390, 485):
    for x in range(91, 619):
        if lum(p[x,y]) < 80:
            cols.setdefault(x, []).append(y)
xs = sorted(cols)
cl = []
for x in xs:
    if cl and x - cl[-1][-1] <= 10: cl[-1].append(x)
    else: cl.append([x])
print('letter clusters:', [(c[0], c[-1]) for c in cl])
print('count:', len(cl))
