#!/usr/bin/env python3
"""R12 part K: ASCII render of hero header + full-screen map to understand layout."""
from PIL import Image
import numpy as np

R12 = '/home/z/my-project/critic_shots/r12/'

def load(p):
    return np.asarray(Image.open(p).convert('RGB')).astype(int)

imh = load(R12 + '01_hero.png')
R, G, B = imh[:,:,0], imh[:,:,1], imh[:,:,2]

def cls(r, g, b):
    lum = (r+g+b)/3
    if r>200 and g>150 and b<120: return '#'      # gold
    if r>200 and g>200 and b>150: return '@'      # pale/white
    if lum>170: return 'W'
    if lum>120: return '+'
    if lum>75: return 'o'
    if lum>45: return '.'
    if lum>28: return ':'
    return ' '

print("=== HERO header y150..450, x20..700, 8px cells (each char = 8x8 block) ===")
for y in range(150, 450, 8):
    line = []
    for x in range(20, 700, 8):
        r, g, b = R[y, x], G[y, x], B[y, x]
        line.append(cls(r, g, b))
    print(f"{y:4d} {''.join(line)}")

print("\n=== HERO full y450..1300 step 12, x20..700 step 10 ===")
for y in range(450, 1300, 12):
    line = []
    for x in range(20, 700, 10):
        r, g, b = R[y, x], G[y, x], B[y, x]
        line.append(cls(r, g, b))
    print(f"{y:4d} {''.join(line)}")
