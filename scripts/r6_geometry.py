#!/usr/bin/env python3
"""Map UI geometry: find board bounds, wells, HUD, tray, streak strip on main classic shot."""
import sys
sys.path.insert(0, '/home/z/my-project/scripts')
from r6_forensics_lib import *

im = load('01_main_classic.png')
p = px(im)
w, h = im.size

# Column profile over middle of screen to find board vertical edges
print('== column mean color, y 240..820 (suspected board zone) ==')
for x in range(0, w, 24):
    rs=gs=bs=n=0
    for y in range(240, 820, 4):
        c = p[x, y]; rs+=c[0]; gs+=c[1]; bs+=c[2]; n+=1
    print(f'x={x:4d} rgb=({rs//n:3d},{gs//n:3d},{bs//n:3d})')

print()
print('== vertical borders: strong horizontal color transitions ==')
prev = None
for y in range(100, h, 2):
    rs=gs=bs=n=0
    for x in range(40, 680, 8):
        c = p[x, y]; rs+=c[0]; gs+=c[1]; bs+=c[2]; n+=1
    m = (rs/n, gs/n, bs/n)
    if prev:
        d = abs(m[0]-prev[0])+abs(m[1]-prev[1])+abs(m[2]-prev[2])
        if d > 26:
            print(f'y={y:4d} rgb={tuple(round(v,1) for v in m)}  (delta {d:.0f})')
    prev = m
