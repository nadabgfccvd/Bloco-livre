#!/usr/bin/env python3
"""R6 CLAIM 2 precise: find star blobs by dilating gold mask, then per-blob stats."""
import os
import numpy as np
from PIL import Image

S = '/home/z/my-project/critic_shots/r6'
a = np.asarray(Image.open(os.path.join(S, '07_clear.png')).convert('RGB'), dtype=np.int16)
r, g, b = a[...,0], a[...,1], a[...,2]
lum = a.mean(axis=2)

# gold: bright saturated warm, excludes cream halo & cream text
gold = (r > 175) & (g > 120) & (b < 115) & (r >= g + 45) & (lum > 120)

# dilate by 2 to merge star internals
from scipy import ndimage
gd = ndimage.binary_dilation(gold, iterations=3)
lab, n = ndimage.label(gd)
print('components after dilation:', n)
sizes = ndimage.sum(gold, lab, range(1, n+1))
coms = []
for k in range(1, n+1):
    if sizes[k-1] < 15:
        continue
    yy, xx = np.nonzero(lab == k)
    coms.append((int(sizes[k-1]), int(xx.min()), int(xx.max()), int(yy.min()), int(yy.max()),
                 int(xx.mean()), int(yy.mean())))
coms.sort(reverse=True)
print(f'{len(coms)} gold star blobs (goldpx, x0,x1, y0,y1, cx,cy):')
for c in coms:
    print('   ', c)

# board geometry: 8x8 wells, rails x 186..609 -> but board interior cells: find cell pitch
# From R5: cell_w=42.5? Here 10 cols were wrong. Check: (609-186)/8 = 52.9. Hmm.
# Let's measure the well lattice from the empty board's wells (dark squares with borders).
# Wells: rows y 280..1130 => 850px / 8 = 106 -> too big; maybe 8 cols x 8 rows but cell ~106?
# Actually R5 script said cell_w=42.5 with 10 cols => 425 wide. Board is 423 wide. So 10 cols.
# Vertical: 8 rows of ~49.5 -> 396. But board looks y280..1130 = 850 tall. That suggests
# wells are bigger vertically OR there are more rows. Count well rows from ASCII: need edges.

# Count horizontal separators: rows with high edge strength in the middle band
mid = lum[300:1130, 200:600]
rowedges = np.abs(np.diff(mid.mean(axis=1)))
seps = [(300+y, int(rowedges[y])) for y in np.argsort(rowedges)[::-1][:30]]
print('top row-edge candidates y300..1130:', sorted(seps))
