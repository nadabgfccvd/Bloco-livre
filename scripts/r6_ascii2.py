#!/usr/bin/env python3
"""ASCII render with color classification (gold vs blue vs dark) to 'see' the crown layout,
plus the banner area rows 466..698 and tray/streak zones, plus R6 vs R5 diff metrics.
"""
import sys
sys.path.insert(0, '/home/z/my-project/scripts')
from r6_forensics_lib import *

def color_ascii(name, root, box, gw=72):
    im = load(name, root).crop(box)
    p = px(im); w, h = im.size
    sx = w/gw; sy = sx*2  # keep aspect
    gh = int(h/sy)
    print(f'== {name} {box} color map: g=gold c=cyan b=blue w=white r=red .=dark ==')
    for gy in range(gh):
        row = ''
        for gx in range(gw):
            x0, y0 = int(gx*sx), int(gy*sy)
            # sample cell avg
            rs=gs=bs=n=0
            for dy in (0, int(sy/2)):
                for dx in (0, int(sx/2)):
                    x, y = min(x0+dx, w-1), min(y0+dy, h-1)
                    c = p[x,y]; rs+=c[0]; gs+=c[1]; bs+=c[2]; n+=1
            r, g, b = rs/n, gs/n, bs/n
            if r>200 and g>150 and b<120 and r>b+60: ch='g'
            elif b>120 and g>110 and b>r+40 and g>r+25: ch='c'
            elif r>150 and g<90 and b<90: ch='r'
            elif r>200 and g>200 and b>190: ch='w'
            elif b>r+15 and b>60: ch='b'
            elif lum((r,g,b))<35: ch='.'
            else: ch=':'
            row += ch
        print(row)
    print()

# board with crown on clear
color_ascii('07_clear.png', R6, (0, 190, 720, 880))
# r5 same
color_ascii('07_clear.png', R5, (0, 190, 720, 880))
