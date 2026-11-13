#!/usr/bin/env python3
"""Danger state: 06_full.png full-strength check.
Claims: hot veil OVER the board alpha 70*k (k=1 at 81%), bg wash + glow behind,
wells warm in full 32%, warm/cool edges 391/930, bg navy-blue.
Also compare vs r5 06_full (should be weaker).
"""
import sys
sys.path.insert(0, '/home/z/my-project/scripts')
from r6_forensics_lib import *

for root, name, tag in [(R6, '06_full.png', 'R6 full'), (R5, '06_full.png', 'R5 full')]:
    im = load(name, root)
    print('====', tag, '====')
    # board zone
    st = stats(im, (20, 190, 696, 866))
    print(f"board: mean_lum {st['mean_lum']:.1f} p10 {st['p10']} p90 {st['p90']} gold {st['gold_px']} warm {st['warm_px']} cool {st['cool_px']}")
    # empty-well cells (rows 7-8 region y 782..866, x all): sample well interior
    p = px(im)
    samples = []
    for (x0,x1) in [(28,100), (248,268)]:
        pass
    # simpler: fixed empty-well coords
    wells = [(60,798),(145,798),(230,798),(315,798),(400,798),(485,798),(570,798),(655,798),
             (60,840),(315,840),(655,840)]
    warmw = coolw = 0
    wsamples = []
    for (x,y) in wells:
        c = p[x,y]
        wsamples.append(c)
        if c[0] > c[2] + 12: warmw += 1
        elif c[2] > c[0] + 12: coolw += 1
    print('empty-well interior samples:', wsamples)
    print(f'wells warm {warmw}/{len(wells)} cool {coolw}')
    # edges: left edge strip x 0..20, right edge strip 676..696? actual screen edge 0..20 and 700..720
    le = stats(im, (0, 190, 20, 866)); re_ = stats(im, (700, 190, 720, 866))
    print(f"left edge: warm {le['warm_px']} cool {le['cool_px']} | right edge: warm {re_['warm_px']} cool {re_['cool_px']}")
    # top bg above board (y 60..110) full width
    bg = stats(im, (0, 60, 720, 110))
    print('top bg mean color:', bg['top_colors'][:3], 'warm', bg['warm_px'], 'cool', bg['cool_px'])
    # screen-wide outside board (below board y 900..1400)
    bt = stats(im, (0, 900, 720, 1400))
    print('below-board zone: mean_lum %.1f warm %d cool %d' % (bt['mean_lum'], bt['warm_px'], bt['cool_px']))
