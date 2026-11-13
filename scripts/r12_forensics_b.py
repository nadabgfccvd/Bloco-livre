#!/usr/bin/env python3
"""R12 forensics part B: map hero layout, find star & band, locate burst center in 07_clear."""
from PIL import Image
import numpy as np

R12 = '/home/z/my-project/critic_shots/r12/'
R11 = '/home/z/my-project/critic_shots/r11/'

def load(p):
    return np.asarray(Image.open(p).convert('RGB')).astype(int)

im = load(R12 + '01_hero.png')
lum = im.mean(axis=2)
H, W = lum.shape

print("=== HERO row structure (mean lum per row, step 4, y0..460) ===")
for y in range(0, 460, 4):
    row = lum[y, :]
    print(y, round(row.mean(),1), round(row.max(),1))
