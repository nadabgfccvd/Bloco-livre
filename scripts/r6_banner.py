#!/usr/bin/env python3
"""Banner geometry + star crown + rays forensics on 07_clear.png.
- Banner band #F6C445 (246,196,69) with white hairline: find rows where band color dominates.
- Banner symmetry: center of banner band mass vs board center cx=358.
- Star crown: ellipse rx=3*cell (cell~84 => rx~252), ry=2.6*cell (~219) around board center (358, ~528).
  Count gold star clusters INSIDE board area.
- Rays: 12 alternating rays alpha 110 radiating behind board — detect warm pixels above board.
"""
import sys
sys.path.insert(0, '/home/z/my-project/scripts')
from r6_forensics_lib import *
from collections import Counter

im = load('07_clear.png'); p = px(im); w,h = im.size
BOARD = (20, 190, 696, 866)
BCX = (20+696)//2  # 358

# 1) banner rows: find rows y where many pixels are close to gold band or bright gold
band_rows = []
for y in range(100, 900):
    goldish = 0; total = 0; xs = []
    for x in range(0, w, 4):
        c = p[x, y]; total += 1
        if is_goldish(c, tol=60):
            goldish += 1; xs.append(x)
    if goldish > total*0.55:
        cx_mean = sum(xs)/len(xs) if xs else 0
        band_rows.append((y, goldish/total, cx_mean))
if band_rows:
    ys = [r[0] for r in band_rows]
    print(f'banner band rows: y {min(ys)}..{max(ys)}  ({len(band_rows)} rows), mean cx {sum(r[2] for r in band_rows)/len(band_rows):.1f}')
else:
    print('no banner band rows found with >55% gold coverage')

# 2) find white hairline: rows adjacent to band with near-white pixels
hair = []
for y in range(100, 900):
    whiteish = sum(1 for x in range(0, w, 4) if p[x,y][0]>225 and p[x,y][1]>225 and p[x,y][2]>215)
    if whiteish > 30: hair.append((y, whiteish))
print('near-white rows (hairline candidates):', hair[:12])

# 3) banner underlay claim: rows 466..698 center 582 — measure center of the banner mass rows 466..698
tot_x = 0; n_x = 0
for y in range(466, 699):
    for x in range(0, w, 3):
        c = p[x,y]
        if is_goldish(c, tol=60):
            tot_x += x; n_x += 1
print(f'underlay rows 466..698: gold px (3-stride) = {n_x}, cx = {tot_x/n_x if n_x else 0:.1f}  (board cx=358, screen cx=360)')

# 4) star crown inside board: find bright gold clusters within board
# major star + 12 stars on ellipse around board center
bright_gold = Counter()
for y in range(190, 866):
    for x in range(20, 696):
        c = p[x,y]
        if c[0] > 200 and c[1] > 150 and c[2] < 120:
            bright_gold[(x//8*8, y//8*8)] += 1
clusters = [k for k,v in bright_gold.items() if v > 12]
print('bright gold cluster cells (8px bins, >12px):', len(clusters))
if clusters:
    xs = [c[0] for c in clusters]; ys = [c[1] for c in clusters]
    print(f'  cluster bbox x {min(xs)}..{max(xs)}  y {min(ys)}..{max(ys)}')
    # board center y ~ (190+866)/2 = 528
    cy = (190+866)/2
    spread_x = (max(xs)-min(xs))/2; spread_y = (max(ys)-min(ys))/2
    print(f'  spread rx~{spread_x:.0f} ry~{spread_y:.0f}  (claimed rx=252, ry=219) center~({(min(xs)+max(xs))/2:.0f},{(min(ys)+max(ys))/2:.0f}) vs board center (358,{cy:.0f})')

# 5) rays above board: warm pixels above y=110..190
print()
print('== ray detection above board (y 60..190) ==')
# angular histogram around board center (358, 528)
import math
cx, cy = 358, 528
ang_bins = Counter()
for y in range(30, 190):
    for x in range(0, 720, 2):
        c = p[x,y]
        if is_goldish(c, tol=60):
            a = math.degrees(math.atan2(-(y-cy), x-cx)) % 360
            ang_bins[int(a//15)*15] += 1
for a in sorted(ang_bins):
    bar = '#' * min(30, ang_bins[a]//50)
    print(f'  {a:3d}-{a+15:3d} deg: {ang_bins[a]:6d} {bar}')
