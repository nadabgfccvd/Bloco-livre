#!/usr/bin/env python3
"""Identify HUD content: 01_main_classic.
Bands: y29..53 (10 letter clusters = a word ~ 'PONTOS + RECORDE'? spans x 209..504 center ~356),
y64..80 (wide span 154..565 = digits row? 'PONTOS value' and 'RECORDE value'?),
y110..178 (three spans: 24..104, 543..618, 647..674 = buttons/icons?).
Wait claim: PONTOS 0.24*cell (20px) vs RECORDE 0.19*cell (16px). Cell=84.5 => 20.3px vs 16.1px.
Band h=25 includes descenders? Measure cap-height precisely per letter cluster at high threshold.
Also: which band is the label band vs value band? Sample colors of each band.
"""
import sys
sys.path.insert(0, '/home/z/my-project/scripts')
from r6_forensics_lib import *
from collections import Counter

im = load('01_main_classic.png'); p = px(im)

def band_colors(y0, y1, x0, x1):
    cc = Counter()
    for y in range(y0, y1+1):
        for x in range(x0, x1+1):
            c = p[x,y]
            if lum(c) > 90: cc[c] += 1
    return cc.most_common(5)

print('band1 (29..53) colors:', band_colors(29,53,209,504))
print('band2 (64..80) colors:', band_colors(64,80,154,565))
print('band3 left (110..178):', band_colors(110,178,24,104))
print('band3 right (110..178):', band_colors(110,178,543,674))

# letter-by-letter cap heights in band1 using tight mask
def cap_height(x0, x1, y0=20, y1=60, thr=100):
    ys = []
    for y in range(y0, y1):
        hit = any(lum(p[x,y]) > thr for x in range(x0, x1+1))
        if hit: ys.append(y)
    return (ys[0], ys[-1], ys[-1]-ys[0]+1) if ys else None

clusters = [(209,226),(240,254),(265,286),(299,318),(330,352),(383,398),(410,412),(424,445),(458,476),(489,504)]
for (x0,x1) in clusters:
    print(f'letter x{x0}..{x1}:', cap_height(x0,x1))

# band2 digits height
for (x0,x1) in [(154,363),(383,496),(516,565)]:
    print(f'value span x{x0}..{x1}:', cap_height(x0,x1,y0=60,y1=90))
