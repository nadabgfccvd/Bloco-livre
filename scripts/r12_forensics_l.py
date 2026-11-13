#!/usr/bin/env python3
"""R12 part L: ASCII render of 07_clear burst zone + hero title zone; measure burst spokes precisely
around bright core; also title text zone in header y150-190."""
from PIL import Image
import numpy as np

R12 = '/home/z/my-project/critic_shots/r12/'
R11 = '/home/z/my-project/critic_shots/r11/'

def load(p):
    return np.asarray(Image.open(p).convert('RGB')).astype(int)

im7 = load(R12 + '07_clear.png')
R, G, B = im7[:,:,0], im7[:,:,1], im7[:,:,2]

def cls(r, g, b):
    lum = (r+g+b)/3
    if r>200 and g>150 and b<120: return '#'
    if r>230 and g>230 and b>200: return '@'
    if lum>200: return 'W'
    if lum>150: return '+'
    if lum>100: return 'o'
    if lum>60: return '.'
    if lum>35: return ':'
    return ' '

print("=== 07_clear y190..560, x100..620, 8px cells ===")
for y in range(190, 560, 8):
    line = []
    for x in range(100, 620, 8):
        line.append(cls(R[y,x], G[y,x], B[y,x]))
    print(f"{y:4d} {''.join(line)}")
