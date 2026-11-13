#!/usr/bin/env python3
"""Streak strip forensics (y 1118..1440) on 01_main_classic.
Claims: occupancy bar w*0.62 (446px), green->amber->red by dangerFrac, 25% pips, '% do tabuleiro' label,
combo pips + stars; 138 unique colors vs 19 in R5.
Also compare R5 same strip.
"""
import sys
sys.path.insert(0, '/home/z/my-project/scripts')
from r6_forensics_lib import *
from collections import Counter

def strip_report(root, name, tag):
    im = load(name, root); p = px(im)
    print('====', tag, '====')
    # unique colors in strip zone
    colors = Counter()
    for y in range(1118, 1440):
        for x in range(0, 720):
            colors[p[x,y]] += 1
    print(f'unique colors in strip: {len(colors)}')
    print('top colors:', colors.most_common(8))
    # find horizontal bar: rows where saturation/hue varies across a wide span
    # detect colored (non-background) pixels: green / amber / red
    def classify(c):
        r,g,b = c
        if g > 100 and g > r + 30 and g > b + 30: return 'green'
        if r > 130 and g > 70 and b < 90 and r > b + 60 and g > b + 20: return 'amber'
        if r > 120 and r > g + 40 and r > b + 40: return 'red'
        return None
    rows = Counter()
    for y in range(1118, 1440):
        cnt = Counter()
        for x in range(0, 720):
            k = classify(p[x,y])
            if k: cnt[k] += 1
        if cnt:
            rows[y] = dict(cnt)
    ys = sorted(rows)
    if ys:
        print('colored rows y:', ys[0], '..', ys[-1], 'count', len(ys))
        # aggregate
        agg = Counter()
        for y in ys: 
            for k,v in rows[y].items(): agg[k] += v
        print('color totals:', dict(agg))
    # horizontal extent of colored bar at the densest row
    if ys:
        best = max(ys, key=lambda y: sum(rows[y].values()))
        xs = [x for x in range(0,720) if classify(p[x,best])]
        if xs:
            print(f'bar row y={best}: x {min(xs)}..{max(xs)} width {max(xs)-min(xs)+1} (claimed w*0.62={int(720*0.62)})')
    # pips: bright spots
    pip_rows = Counter()
    for y in range(1118, 1440):
        n = sum(1 for x in range(0,720) if lum(p[x,y]) > 140)
        if n > 8: pip_rows[y] = n
    print('bright rows (pips/label):', sorted(pip_rows.items())[:12], '...' if len(pip_rows)>12 else '')

strip_report(R6, '01_main_classic.png', 'R6 main')
strip_report(R6, '06_full.png', 'R6 full (danger)')
strip_report(R5, '01_main_classic.png', 'R5 main')
strip_report(R5, '06_full.png', 'R5 full')
