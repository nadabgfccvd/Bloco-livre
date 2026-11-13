#!/usr/bin/env python3
"""Verify '% do tabuleiro' label + pips + stars in streak strip; and tray dim claim (134 vs 165 lum).
Tray measured: main 67.0 vs clear 40.0 => ratio 0.598 (40% dim, not 55%; or "dimmed TO 55%"?
55% dim would give lum 0.45*67=30; 0.598 means dim to 60% brightness => ~40% reduction).
Claim '134 vs 165 lum' — our tray zone numbers are 40 vs 67 for full tray zone; maybe they
measured a different sub-region (piece cells). Measure piece-area luminance in tray for both.
Also count stars (gold) in strip: main had gold 221px.
"""
import sys
sys.path.insert(0, '/home/z/my-project/scripts')
from r6_forensics_lib import *
from collections import Counter

imc = load('07_clear.png'); imm = load('01_main_classic.png')

# tray piece area: find bright piece cells in tray zone y 950..1110
def tray_pieces(im):
    p = px(im)
    cells = []
    for y in range(955, 1105, 6):
        for x in range(10, 710, 6):
            c = p[x,y]
            if lum(c) > 60 and (max(c)-min(c)) > 40:
                cells.append((x,y,c))
    return cells

for tag, im in [('main', imm), ('clear', imc)]:
    cells = tray_pieces(im)
    print(tag, 'tray colored cells sampled:', len(cells))
    if cells:
        lums = [lum(c[2]) for c in cells]
        print('   mean lum', sum(lums)/len(lums))

# strip pips: count discrete bright blobs rows 1203..1215 x 603..665 (combo pips?) and stars zone
im = load('01_main_classic.png'); p = px(im)
print()
print('== right-side strip elements (x 595..710, y 1195..1260) color sample ==')
cc = Counter()
for y in range(1195, 1260):
    for x in range(595, 715):
        c = p[x,y]
        if lum(c) > 90: cc[c] += 1
print(cc.most_common(8))

# count star shapes (gold) in strip zone
gold = 0
for y in range(1118, 1300):
    for x in range(0, 720):
        if is_goldish(p[x,y]): gold += 1
print('gold px in strip (main):', gold)

# pips along the bar? 25% pips claim: check dark ticks crossing the bar track
print()
print('== bar track: is there a full-width dim track behind the 18px green fill? ==')
for y in (1245,):
    row = [p[x,y] for x in range(0, 720)]
    # print compressed luminance signature of x 120..680
    sig = ''.join(str(min(9, lum(c)//26)) for c in row[120:680:4])
    print('lum signature x120..680:', sig)
