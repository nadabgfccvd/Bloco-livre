#!/usr/bin/env python3
"""Deeper into the streak strip: the bar is at y 1238..1251.
Check bar horizontal extent across ALL its rows, color gradient along the bar (danger ramp),
pips at 25% marks, label text '% do tabuleiro', combo pips + stars zone.
Also count 'zone colors' = unique saturated colors (claim 138 vs 19).
"""
import sys
sys.path.insert(0, '/home/z/my-project/scripts')
from r6_forensics_lib import *
from collections import Counter

def sat(c):
    return max(c) - min(c)

def zone_colors(root, name, tag):
    im = load(name, root); p = px(im)
    colors = set()
    for y in range(1118, 1440):
        for x in range(0, 720):
            c = p[x,y]
            if sat(c) > 45 and lum(c) > 60:
                # quantize slightly to ignore AA noise? claim says 138 unique -> likely raw count of distinct
                colors.add(c)
    print(f'{tag}: saturated-zone unique colors = {len(colors)}')
    return im

for args in [(R6,'01_main_classic.png','R6 main'), (R6,'06_full.png','R6 full'),
             (R5,'01_main_classic.png','R5 main'), (R5,'06_full.png','R5 full')]:
    zone_colors(*args)

# bar structure on full
im = load('06_full.png'); p = px(im)
print()
print('== bar rows detail (R6 full) ==')
for y in range(1236, 1253):
    xs = [x for x in range(0,720) if sat(p[x,y]) > 45 and max(p[x,y]) > 80]
    if xs:
        # sample colors along
        samples = [p[x,y] for x in range(min(xs), max(xs)+1, max(1,(max(xs)-min(xs))//8))]
        print(f'y={y}: x {min(xs)}..{max(xs)} w={max(xs)-min(xs)+1} samples {samples}')

print()
print('== bar on R6 main ==')
im = load('01_main_classic.png'); p = px(im)
for y in range(1236, 1253):
    xs = [x for x in range(0,720) if sat(p[x,y]) > 45 and max(p[x,y]) > 80]
    if xs:
        samples = [p[x,y] for x in range(min(xs), max(xs)+1, max(1,(max(xs)-min(xs))//8))]
        print(f'y={y}: x {min(xs)}..{max(xs)} w={max(xs)-min(xs)+1} samples {samples}')
