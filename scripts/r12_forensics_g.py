#!/usr/bin/env python3
"""R12 part G: resolve star-vs-band with color segmentation; find where star body actually is."""
from PIL import Image
import numpy as np

R12 = '/home/z/my-project/critic_shots/r12/'
imh = load_src = np.asarray(Image.open(R12 + '01_hero.png').convert('RGB')).astype(int)
R, G, B = imh[:,:,0], imh[:,:,1], imh[:,:,2]
lum = imh.mean(axis=2)

# Look at distinct colors in rows 220..380, x 250..560
from collections import Counter
c = Counter()
for y in range(220, 380, 2):
    for x in range(250, 560, 2):
        c[(R[y,x]//16*16, G[y,x]//16*16, B[y,x]//16*16)] += 1
print("top quantized colors y220-380 x250-560:")
for col, n in c.most_common(14):
    print("  ", col, n)

# Star should be bright yellow-white (222,182,60-ish?) vs band maybe darker gold.
# Check the bright cluster x280-523 found earlier at rows 358-442 — that's the BAND itself?
# Let's map vertical profile at x=400 (through star+band):
print("\nx=400 lum y196..470:")
for y in range(196, 470, 3):
    print(y, round(lum[y,400],1), (R[y,400],G[y,400],B[y,400]))

print("\nx=340 lum y196..470:")
for y in range(196, 470, 3):
    print(y, round(lum[y,340],1), (R[y,340],G[y,340],B[y,340]))
