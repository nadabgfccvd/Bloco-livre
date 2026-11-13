#!/usr/bin/env python3
"""R6 forensic step 1: locate board geometry per shot, basic scene stats."""
import os
import numpy as np
from PIL import Image

SHOTS = '/home/z/my-project/critic_shots/r6'
CROPS = '/tmp/critic_crops_r6'
os.makedirs(CROPS, exist_ok=True)

def arr(n):
    return np.asarray(Image.open(os.path.join(SHOTS, n)).convert('RGB'), dtype=np.int16)

def gray(n):
    return np.asarray(Image.open(os.path.join(SHOTS, n)).convert('L'), dtype=np.int16)

def stats(tag, a):
    lum = a.mean(axis=2)
    print(f'{tag}: mean RGB = {a[...,0].mean():.1f} {a[...,1].mean():.1f} {a[...,2].mean():.1f} '
          f'lum p1={np.percentile(lum,1):.0f} p50={np.percentile(lum,50):.0f} '
          f'p99={np.percentile(lum,99):.0f} p99.9={np.percentile(lum,99.9):.0f}')

def find_rails(g, tag):
    """Find vertical rails: columns whose absolute horizontal diff is high and persistent."""
    colmag = np.abs(np.diff(g.astype(np.int32), axis=1)).sum(axis=0)
    # top candidates
    idx = np.argsort(colmag)[::-1][:12]
    idx = sorted(idx.tolist())
    print(f'--- {tag}: top edge columns (x, strength):', [(i, int(colmag[i])) for i in idx])

for n in ['01_main_classic.png', '02_skin0.png', '03_skin1.png', '04_skin2.png',
          '05_skin3.png', '06_full.png', '07_clear.png']:
    stats(n, arr(n))
    find_rails(gray(n), n)

# vertical extent of board on classic: use column at left rail
a = arr('02_skin0.png')
g = gray('02_skin0.png')
# scan a column in the middle of the board for horizontal edges (rows)
midcol = g[:, 380].astype(np.int32)
rowmag = np.abs(np.diff(midcol))
toprows = sorted(np.argsort(rowmag)[::-1][:14].tolist())
print('02_skin0 strong horizontal edges at x=380 (y, strength):',
      [(r, int(rowmag[r])) for r in toprows])

# Same for main classic and danger
for n in ['01_main_classic.png', '06_full.png', '07_clear.png']:
    g2 = gray(n)
    midcol = g2[:, 380].astype(np.int32)
    rowmag = np.abs(np.diff(midcol))
    tr = sorted(np.argsort(rowmag)[::-1][:14].tolist())
    print(f'{n} strong horizontal edges at x=380 (y, strength):',
          [(r, int(rowmag[r])) for r in tr])
