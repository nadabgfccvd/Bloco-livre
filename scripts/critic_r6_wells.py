#!/usr/bin/env python3
"""R6 step 3: well-grid geometry from the clear (empty-board) frame.
The empty board in 07_clear shows 8x8 wells; find the well lattice."""
import os
import numpy as np
from PIL import Image

SHOTS = '/home/z/my-project/critic_shots/r6'

def arr(n):
    return np.asarray(Image.open(os.path.join(SHOTS, n)).convert('RGB'), dtype=np.int16)

a = arr('07_clear.png')
lum = a.mean(axis=2)

# The board interior: wells on dark bg. Find rows/cols where lum variance spikes.
# First locate board bounds roughly from previous runs: use x in 190..605, y in 300..1120
# Better: detect the well pattern by looking at a central strip.
# Take columns x=200..600 and compute per-row std of lum over that range.
strip = lum[:, 200:600]
rowstd = strip.std(axis=1)
# print rows with high std (well separators / stars)
top = np.argsort(rowstd)[::-1][:30]
top = sorted(top.tolist())
print('rows with highest std in x200..600:', [(r, round(float(rowstd[r]),1)) for r in top])

# Column-wise std over a board middle band y=500..900
band = lum[500:900, :]
colstd = band.std(axis=0)
topc = np.argsort(colstd)[::-1][:30]
topc = sorted(topc.tolist())
print('cols with highest std in y500..900:', [(c, round(float(colstd[c]),1)) for c in topc])

# Check the well background color at a few sample points
for (x, y) in [(220, 400), (300, 400), (500, 400), (220, 1000), (400, 700), (590, 1000)]:
    print(f'px({x},{y}) rgb = {a[y, x].tolist()}')
