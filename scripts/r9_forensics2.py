#!/usr/bin/env python3
"""R9 raw-color forensics, calibrated. Board 8x8 x24-696 y190-866 cell84; tray y880-1110; streak y1240-1250."""
import os
from PIL import Image
from collections import Counter

R9 = '/home/z/my-project/critic_shots/r9/07_clear.png'
R8 = '/home/z/my-project/critic_shots/r8/07_clear.png'
im9 = Image.open(R9).convert('RGB'); im8 = Image.open(R8).convert('RGB')
W, H = im9.size
p9, p8 = im9.load(), im8.load()
OUT = '/tmp/critic_crops_r9'; os.makedirs(OUT, exist_ok=True)

print('=== RAW COLUMN PROFILE x=360 (y150-500 step4) r9 ===')
prev = None
for y in range(150, 500, 4):
    c = p9[360, y]
    print('%4d (%3d,%3d,%3d) sum=%d %s' % (y, c[0], c[1], c[2], sum(c), '' if prev is None or sum(abs(c[i]-prev[i]) for i in range(3))<40 else '<<CHANGE'))
    prev = c

print('=== RAW COLUMN PROFILE x=60 (y280-500 step8) r9 ===')
for y in range(280, 500, 8):
    c = p9[60, y]; print('%4d (%3d,%3d,%3d)' % (y, c[0], c[1], c[2]))

print('=== RAW ROW PROFILE y=394 (x0-719 step24) r9 ===')
for x in range(0, 720, 24):
    c = p9[x, 394]; print('%4d (%3d,%3d,%3d)' % (x, c[0], c[1], c[2]))

# band rows: rows where center differs strongly from left-margin page bg (x=8)
def band_rows(p):
    runs = []; cur = None
    for y in range(120, 560):
        bgc = p[8, y]
        d = 0
        for x in (120, 240, 360, 480, 600):
            c = p[x, y]
            d = max(d, abs(c[0]-bgc[0]) + abs(c[1]-bgc[1]) + abs(c[2]-bgc[2]))
        if d > 90:
            if cur is None: cur = [y, y]
            else: cur[1] = y
        elif cur is not None:
            runs.append(tuple(cur)); cur = None
    if cur: runs.append(tuple(cur))
    return runs
b9 = band_rows(p9); b8 = band_rows(p8)
print('=== BAND ROWS (vs x=8 margin) ===')
print('  r9:', [(a, b, b-a+1) for a, b in b9])
print('  r8:', [(a, b, b-a+1) for a, b in b8])

# text: within band rows, pixels much darker than band
by0, by1 = (b9[0][0], b9[0][1]) if b9 else (321, 466)
bc = p9[360, (by0+by1)//2]
dark = [(x, y) for y in range(by0, by1+1) for x in range(0, W)
        if sum(p9[x, y]) < sum(bc) - 150]
if dark:
    xs = [a for a, _ in dark]; ys = [b for _, b in dark]
    tyc = (min(ys)+max(ys))/2; bandc = (by0+by1)/2
    print('=== TEXT (dark-on-band) ===')
    print('  bbox x%d-%d y%d-%d (h%d)  text center y %.1f  band center y %.1f  offset %+.1f px' % (
        min(xs), max(xs), min(ys), max(ys), max(ys)-min(ys)+1, tyc, bandc, tyc-bandc))
else:
    print('=== TEXT: none found dark-on-band; trying bright-on-dark ===')
    bright = [(x, y) for y in range(by0, by1+1) for x in range(0, W) if sum(p9[x, y]) > sum(bc) + 150]
    if bright:
        xs = [a for a, _ in bright]; ys = [b for _, b in bright]
        print('  bbox x%d-%d y%d-%d center y %.1f band center %.1f offset %+.1f' % (
            min(xs), max(xs), min(ys), max(ys), (min(ys)+max(ys))/2, (by0+by1)/2, (min(ys)+max(ys))/2 - (by0+by1)/2))

# star + spokes: bright saturated pixels above/below band center region
def gold_bright(p, y0, y1):
    pts = [(x, y) for y in range(y0, y1) for x in range(0, W)
           if p[x, y][0] > 200 and p[x, y][1] > 150 and p[x, y][2] < 150 and p[x, y][0]-p[x, y][2] > 90]
    return pts
for (y0, y1, tag) in [(120, by0+5, 'above band'), (by1-5, 700, 'below band')]:
    pts = gold_bright(p9, y0, y1)
    print('=== GOLD-BRIGHT pts %s (y%d-%d): %d ===' % (tag, y0, y1, len(pts)))
    if pts:
        xs = [a for a, _ in pts]; ys = [b for _, b in pts]
        print('  envelope x%d-%d y%d-%d' % (min(xs), max(xs), min(ys), max(ys)))
        # cluster by y gaps
        pts.sort(key=lambda t: t[1])
        clusters = []; s = pts[0][1]; prev = s
        for y in [b for _, b in pts][1:]:
            if y - prev > 8: clusters.append((s, prev)); s = y
            prev = y
        clusters.append((s, prev))
        print('  y-clusters:', clusters)
        for cy0, cy1 in clusters:
            sub = [(x, y) for x, y in pts if cy0 <= y <= cy1]
            sxs = [a for a, _ in sub]; sys_ = [b for _, b in sub]
            print('    cluster y%d-%d: x%d-%d n=%d centroid (%.0f,%.0f) w%d h%d' % (
                cy0, cy1, min(sxs), max(sxs), len(sub), sum(sxs)/len(sub), sum(sys_)/len(sub),
                max(sxs)-min(sxs)+1, max(sys_)-min(sys_)+1))

# spoke radial scan around measured star centroid (use biggest above-band cluster)
pts = gold_bright(p9, 120, by0+5)
import math
if pts:
    ys = [b for _, b in pts]
    # assume star = widest cluster; recompute centroid of central 80% x-range
    xs = [a for a, _ in pts]
    sx, sy = sum(xs)/len(xs), sum(ys)/len(ys)
    print('=== RADIAL SCAN from (%.0f,%.0f), r=40..120 step2, gold-bright test ===' % (sx, sy))
    hits = {}
    for deg in range(0, 360, 15):
        rad = math.radians(deg)
        far = 0
        for r in range(40, 121, 2):
            x = int(sx + r*math.cos(rad)); y = int(sy + r*math.sin(rad))
            if 0 <= x < W and 0 <= y < H:
                c = p9[x, y]
                if c[0] > 200 and c[1] > 150 and c[2] < 150 and c[0]-c[2] > 90: far = r
        if far: hits[deg] = far
    print('  rays:', sorted(hits.items()))

# hairlines: thin dark horizontal rows in tray/streak zone x24-696
def hairlines(p, y0, y1, x0=24, x1=696, thr=320):
    rows = []
    for y in range(y0, y1):
        n = 0; tot = 0
        for x in range(x0, x1, 4):
            if sum(p[x, y]) < thr: n += 1
            tot += 1
        if n/tot > 0.7: rows.append(y)
    if not rows: return []
    runs = []; s = rows[0]; prev = s
    for y in rows[1:]:
        if y - prev <= 1: prev = y
        else: runs.append((s, prev)); s = y; prev = y
    runs.append((s, prev))
    return [(a, b, b-a+1) for a, b in runs if 1 <= b-a+1 <= 8]
print('=== HAIRLINES (thin dark rows, y866-1260) ===')
print('  r9:', hairlines(p9, 866, 1260))
print('  r8:', hairlines(p8, 866, 1260))
print('=== HAIRLINES (y1150-1300 whole width) ===')
print('  r9:', hairlines(p9, 1150, 1300, 0, W))
print('  r8:', hairlines(p8, 1150, 1300, 0, W))
# vertical hairlines in tray
def vlines(p, y0, y1, x0=0, x1=W, thr=320):
    cols = []
    for x in range(x0, x1):
        n = 0; tot = 0
        for y in range(y0, y1, 4):
            if sum(p[x, y]) < thr: n += 1
            tot += 1
        if n/tot > 0.7: cols.append(x)
    if not cols: return []
    runs = []; s = cols[0]; prev = s
    for x in cols[1:]:
        if x - prev <= 1: prev = x
        else: runs.append((s, prev)); s = x; prev = x
    runs.append((s, prev))
    return [(a, b, b-a+1) for a, b in runs if 1 <= b-a+1 <= 8]
print('=== V-HAIRLINES tray y880-1110 ===')
print('  r9:', vlines(p9, 884, 1106))
print('  r8:', vlines(p8, 884, 1106))

# board rows 4-7 emptiness
print('=== BOARD ROWS 4-7 (32 cells below band) r9 ===')
stds = []; means = []
for row in range(4, 8):
    for col in range(8):
        x0 = 24 + col*84 + 14; y0 = 190 + row*84 + 14
        vals = [p9[x, y] for y in range(y0, y0+56, 4) for x in range(x0, x0+56, 4)]
        lum = [sum(v)/3 for v in vals]
        m = sum(lum)/len(lum)
        sd = (sum((l-m)**2 for l in lum)/len(lum))**0.5
        stds.append(sd); means.append((row, col, round(m), round(sd, 1)))
print('  max cell std: %.1f  (empty if < ~6)' % max(stds))
print('  worst cells:', sorted(means, key=lambda t: -t[3])[:6])
print('  all 32 uniform:', max(stds) < 6)
# gap band->row4 clean?
gap = [p9[x, y] for y in range(by1+2, 524, 6) for x in range(30, 690, 20)]
gs = [sum(c)/3 for c in gap]
print('  gap y%d-524 mean lum %.0f std %.1f' % (by1+2, sum(gs)/len(gs), (sum((g-sum(gs)/len(gs))**2 for g in gs)/len(gs))**0.5))

# streak strip content
print('=== STREAK STRIP y1240-1250 r9 vs r8 ===')
for tag, p in (('r9', p9), ('r8', p8)):
    row = [p[x, 1245] for x in range(24, 696, 12)]
    print('  %s y1245 colors:' % tag, row[:12])

# crops for the record
im9.crop((0, 300, W, 480)).resize((W, 360)).save(OUT+'/c8_band_text_2x.png')
im9.crop((250, 240, 470, 400)).resize((440, 320)).save(OUT+'/c9_star_2x.png')
im9.crop((0, 850, W, 1000)).save(OUT+'/c10_traytop_r9.png')
im8.crop((0, 850, W, 1000)).save(OUT+'/c11_traytop_r8.png')
im9.crop((0, 1200, W, 1300)).save(OUT+'/c12_streak_r9.png')
im8.crop((0, 1200, W, 1300)).save(OUT+'/c13_streak_r8.png')
print('crops saved:', sorted(os.listdir(OUT)))
