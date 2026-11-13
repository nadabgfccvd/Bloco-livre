#!/usr/bin/env python3
"""R6 CLAIM 1: gold-family celebration forensics on 07_clear.png."""
import os
import numpy as np
from PIL import Image

S = '/home/z/my-project/critic_shots/r6'
C = '/tmp/critic_crops_r6'
os.makedirs(C, exist_ok=True)

a = np.asarray(Image.open(os.path.join(S, '07_clear.png')).convert('RGB'), dtype=np.int16)

# Board geometry: rails at x=186 and x=609. Vertical bounds: use well pattern.
# From R5: board x [186,608], wells grid inside. Confirm current bounds via rails:
# rails x=186/609 constant across shots. For vertical bounds use the well lattice below.

# ------------------------------------------------ G1/G2 gradient check
# Banner: the wide bright band across board center. Find its pixels:
lum = a.mean(axis=2)
r, g, b = a[...,0], a[...,1], a[...,2]

# warm gold mask (loose): warm and bright
warm = (r > 150) & (g > 90) & (b < r - 40) & (lum > 100)
ys, xs = np.nonzero(warm)
print('warm px count in whole frame:', warm.sum())
# Where are they concentrated?
hist_y, edges_y = np.histogram(ys, bins=24, range=(0, 1440))
print('warm px y-histogram (24 bins of 60px):', hist_y.tolist())

# Concentration inside vs outside board x-range
inside = (xs >= 186) & (xs <= 608)
print('warm inside board x-range:', int(inside.sum()), ' outside:', int((~inside).sum()))

# ---------------- exact colors: histogram of warm pixels
wm = a[warm]
vals, counts = np.unique(wm.reshape(-1, len(wm.shape) and wm.shape[1]), axis=0, return_counts=True) if False else (None, None)
# do proper unique on colors
cols = wm // 16  # quantize to reduce
cols = (wm.astype(np.int32) // 8).astype(np.int32)
packed = cols[...,0]*4096 + cols[...,1]*64 + cols[...,2]
u, cnt = np.unique(packed, return_counts=True)
order = np.argsort(cnt)[::-1][:15]
print('top warm color bins (r,g,b each //8*8, count):')
for i in order:
    p = int(u[i]); rr = (p // 4096) * 8; gg = ((p // 64) % 64) * 8; bb = (p % 64) * 8
    print(f'   approx RGB ({rr},{gg},{bb}) count={cnt[i]}')

# ---------------- find the banner band: rows where warm density peaks
rowdens = warm.sum(axis=1)
peak_rows = np.argsort(rowdens)[::-1][:20]
peak_rows = sorted(peak_rows.tolist())
print('rows with most warm px:', peak_rows)
print('row warm density around peak:', [int(rowdens[y]) for y in range(min(peak_rows), max(peak_rows)+1, 8)])

# Banner bounding box: warm mask restricted to y in 430..640
band = warm[420:660, :]
ys2, xs2 = np.nonzero(band)
if len(ys2):
    print(f'banner-ish band y420-660: bbox x {186+0 if False else xs2.min()}..{xs2.max()} '
          f'y {420+ys2.min()}..{420+ys2.max()} count={len(ys2)}')

# Sample the banner core color (excluding text/white)
core = a[560:640, 300:500]
cr, cg, cb = core[...,0], core[...,1], core[...,2]
banner_mask = (cr > 150) & (cb < cr - 40)
if banner_mask.sum():
    print('banner core mean RGB:', core[banner_mask].mean(axis=0).round(1).tolist(),
          'n=', int(banner_mask.sum()))

# White filet: near-white pixels in banner zone
white = (r > 215) & (g > 215) & (b > 200)
zone = white[420:660, 186:609]
print('white filet px in banner zone:', int(zone.sum()))

# ---------------- Gold star count: connected components of gold in board zone
gold = (r > 170) & (g > 120) & (b < 120) & (r >= g + 40) & (lum > 110)
gz = gold[280:1140, 186:609]  # board zone
ys3, xs3 = np.nonzero(gz)
print('gold px in board zone:', int(gz.sum()))

# simple flood fill labeling
def components(mask, min_size=8):
    from scipy import ndimage
    lab, n = ndimage.label(mask)
    sizes = ndimage.sum(mask, lab, range(1, n+1))
    keep = [i+1 for i, s in enumerate(sizes) if s >= min_size]
    coms = []
    for k in keep:
        m = lab == k
        yy, xx = np.nonzero(m)
        coms.append((int(sizes[k-1]), int(xx.min()), int(xx.max()), int(yy.min()), int(yy.max())))
    return coms

try:
    coms = components(gz, 12)
    coms.sort(reverse=True)
    print(f'gold components in board zone (size, x0..x1, y0..y1) top 25 of {len(coms)}:')
    for c in coms[:25]:
        print('   ', c)
except ImportError:
    print('no scipy; skip components')
