#!/usr/bin/env python3
"""R6 CLAIM 2b: star blob detection with bridge-closing; find distinct stars."""
import os
import numpy as np
from PIL import Image
from scipy import ndimage

S = '/home/z/my-project/critic_shots/r6'
a = np.asarray(Image.open(os.path.join(S, '07_clear.png')).convert('RGB'), dtype=np.int16)
r, g, b = a[...,0], a[...,1], a[...,2]
lum = a.mean(axis=2)

gold = (r > 175) & (g > 120) & (b < 115) & (r >= g + 45) & (lum > 120)
# close gaps up to ~6px
gd = ndimage.binary_closing(gold, structure=np.ones((7,7)))
lab, n = ndimage.label(gd)
sizes = ndimage.sum(gold, lab, range(1, n+1))
coms = []
for k in range(1, n+1):
    if sizes[k-1] < 12: continue
    yy, xx = np.nonzero(lab == k)
    coms.append((int(sizes[k-1]), int(xx.min()), int(xx.max()), int(yy.min()), int(yy.max()),
                 int(xx.mean()), int(yy.mean())))
coms.sort(key=lambda c: -c[0])
print(f'{len(coms)} gold blobs after closing (goldpx, x0,x1,y0,y1,cx,cy):')
for c in coms[:40]:
    print('   ', c)

# also try raw label on gold without closing to see fragmentation
lab2, n2 = ndimage.label(gold)
sizes2 = ndimage.sum(gold, lab2, range(1, n2+1))
big = [s for s in sizes2 if s >= 12]
print(f'raw gold: {n2} comps, {len(big)} >= 12px, sizes sorted:', sorted([int(s) for s in sizes2 if s>=12], reverse=True)[:40])
