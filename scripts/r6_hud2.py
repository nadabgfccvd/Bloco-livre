#!/usr/bin/env python3
"""HUD full analysis: identify what the clusters are.
Row 30..53 = a text line (probably title / label). Row 141..178 = another element (PONTOS value?).
Distinguish label rows vs value rows, and PONTOS vs RECORDE by horizontal position.
Also measure darker-but-bright text (labels may not be white-bright: use lum>110).
"""
import sys
sys.path.insert(0, '/home/z/my-project/scripts')
from r6_forensics_lib import *

im = load('01_main_classic.png'); p = px(im)
def textmask(c, thr=110):
    return lum(c) > thr

# per-row text spans with lower threshold
for name in ['01_main_classic.png', '07_clear.png']:
    im = load(name); p = px(im)
    print('==', name, '==')
    spans_by_row = {}
    for y in range(0, 200):
        xs = [x for x in range(0, 720) if textmask(p[x,y])]
        if xs:
            # cluster xs
            cl = []
            for x in xs:
                if cl and x - cl[-1][-1] <= 8: cl[-1].append(x)
                else: cl.append([x])
            spans_by_row[y] = [(c[0], c[-1]) for c in cl if len(c) > 2]
    # summarize contiguous row bands
    bands = []
    for y in sorted(spans_by_row):
        if bands and y - bands[-1][1] <= 2:
            bands[-1][1] = y; bands[-1][2].append(y)
        else:
            bands.append([y, y, [y]])
    for b in bands:
        y0, y1, rowsl = b
        # union of spans
        allspans = []
        for y in rowsl:
            for s in spans_by_row.get(y, []):
                allspans.append(s)
        # merge
        allspans.sort()
        merged = []
        for s in allspans:
            if merged and s[0] - merged[-1][1] <= 10: merged[-1] = (merged[-1][0], max(merged[-1][1], s[1]))
            else: merged.append(list(s))
        print(f'   band y {y0}..{y1} h={y1-y0+1}: spans {[(m[0],m[1]) for m in merged]}')
