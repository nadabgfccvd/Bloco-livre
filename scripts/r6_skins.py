#!/usr/bin/env python3
"""Skin macros: board zone color character per skin + piece variety.
Also generate crops for visual reference.
Also verify: gold in-board 3155px claim — that number is suspiciously low vs our 29680 measured
(unless they count exact #FFE08A? or in a different shot). Count exact palette colors in 07_clear.
"""
import sys
sys.path.insert(0, '/home/z/my-project/scripts')
from r6_forensics_lib import *
from collections import Counter
import os

CROPS = '/tmp/critic_crops_r6'

def skin_macro(name):
    im = load(name)
    st = stats(im, (20, 190, 696, 866))
    colors = Counter()
    p = px(im)
    for y in range(190, 866, 2):
        for x in range(20, 696, 2):
            colors[p[x,y]] += 1
    print(f'== {name} == board mean_lum {st["mean_lum"]:.1f} unique(sampled) {len(colors)}')
    print('   top:', colors.most_common(6))

for n in ['02_skin0.png','03_skin1.png','04_skin2.png','05_skin3.png']:
    skin_macro(n)

# exact gold palette counts in 07_clear board
im = load('07_clear.png'); p = px(im)
targets = {(255,224,138):'FFE08A', (255,247,216):'FFF7D8', (246,196,69):'F6C445'}
cnt = Counter()
for y in range(0, 1440):
    for x in range(0, 720):
        c = p[x,y]
        if c in targets: cnt[targets[c]] += 1
print()
print('07_clear exact palette counts (whole frame):', dict(cnt))

# board-only gold count (in-board = over the wells)
cntb = Counter()
for y in range(190, 866):
    for x in range(20, 696):
        c = p[x,y]
        if is_goldish(c): cntb['goldish'] += 1
        if c in targets: cntb[targets[c]] += 1
print('07_clear in-board gold counts:', dict(cntb))

# halo outside board (edges + above): exact
cnto = Counter()
for y in list(range(0,190)) + list(range(866,1440)):
    for x in range(0,720):
        c = p[x,y]
        if c in targets: cnto[targets[c]] += 1
for y in range(190,866):
    for x in list(range(0,20)) + list(range(696,720)):
        c = p[x,y]
        if c in targets: cnto[targets[c]] += 1
print('07_clear outside-board halo exact counts:', dict(cnto))
goldish_out = 0
for y in list(range(0,190)) + list(range(866,1440)):
    for x in range(0,720):
        if is_goldish(p[x,y]): goldish_out += 1
for y in range(190,866):
    for x in list(range(0,20)) + list(range(696,720)):
        if is_goldish(p[x,y]): goldish_out += 1
print('07_clear outside-board goldish (loose):', goldish_out)
