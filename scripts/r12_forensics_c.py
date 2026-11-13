#!/usr/bin/env python3
"""R12 forensics part C: full column maps to locate star, band, tray, streak; crops."""
from PIL import Image
import numpy as np

R12 = '/home/z/my-project/critic_shots/r12/'
R11 = '/home/z/my-project/critic_shots/r11/'

def load(p):
    return np.asarray(Image.open(p).convert('RGB')).astype(int)

im = load(R12 + '01_hero.png')
lum = im.mean(axis=2)

print("=== HERO rows 840..1440 step 4 ===")
for y in range(840, 1440, 4):
    row = lum[y, :]
    print(y, round(row.mean(),1), round(row.max(),1))

print("\n=== streak area rows 1230..1260 ===")
for y in range(1230, 1261, 2):
    print(y, round(lum[y,:].mean(),1), round(lum[y,:].max(),1))
