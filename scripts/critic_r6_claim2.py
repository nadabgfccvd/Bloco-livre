#!/usr/bin/env python3
"""R6 CLAIM 1 + 2 refined: star crown components, ellipse fit, halo/rays."""
import os
import numpy as np
from PIL import Image

S = '/home/z/my-project/critic_shots/r6'

a = np.asarray(Image.open(os.path.join(S, '07_clear.png')).convert('RGB'), dtype=np.int16)
r, g, b = a[...,0], a[...,1], a[...,2]
lum = a.mean(axis=2)

# gold mask tuned to exclude cream halo (halo is cream 152..176 with high B)
gold_strict = (r > 185) & (g > 130) & (b < 110) & (r >= g + 45) & (lum > 130)

# Board bounds
BX0, BX1 = 186, 609
# Board vertical bounds: rows containing the well grid. From ASCII: wells appear
# from about y=280 to y=1130. Find precise top/bottom via row edges on empty board:
edge_rows = np.abs(np.diff(lum[:, 200:600].mean(axis=1)))
cand = np.argsort(edge_rows)[::-1][:20]
print('strong row edges on empty board (y, strength):', sorted([(int(y), int(edge_rows[y])) for y in cand]))

gz = gold_strict[250:1150, BX0:BX1]
ys, xs = np.nonzero(gz)
print('strict gold px in board zone:', int(gz.sum()))

# connected components via scipy if available, else pure python BFS
mask = np.zeros_like(gz, dtype=np.int32)
try:
    from scipy import ndimage
    lab, n = ndimage.label(gz)
    sizes = ndimage.sum(gz, lab, range(1, n+1))
    coms = []
    for k in range(1, n+1):
        if sizes[k-1] < 20:
            continue
        yy, xx = np.nonzero(lab == k)
        coms.append((int(sizes[k-1]), int(xx.min()+BX0), int(xx.max()+BX0),
                     int(yy.min()+250), int(yy.max()+250),
                     int(xx.mean()+BX0), int(yy.mean()+250)))
    coms.sort(reverse=True)
    print(f'{len(coms)} strict gold components (size, x0,x1,y0,y1, cx,cy):')
    for c in coms[:30]:
        print('   ', c)
    # ellipse fit: stars that are "crown" = on ellipse around board center
    cx_board, cy_board = (BX0+BX1)/2, None
    # compute board center y from well grid
except ImportError:
    print('scipy missing')
