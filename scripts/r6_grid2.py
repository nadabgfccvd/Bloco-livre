#!/usr/bin/env python3
"""Occupancy grid for any board shot, using measured geometry.
Grid: x lines ~ 104,188,272,356,440,524,608,692 ; y lines ~ 363,448,532,617,701,786 + top/bottom beyond.
Full board spans y ~ 279..871 (8 rows of ~84) — verify by extending scan below.
Empty cell reference colors: (41,52,73) and (50,64,90). Anything clearly brighter/saturated = filled.
"""
import sys
sys.path.insert(0, '/home/z/my-project/scripts')
from r6_forensics_lib import *

XS = [104, 188, 272, 356, 440, 524, 608, 692]
YS = [363, 448, 532, 617, 701, 786]  # 6 found; need 8 -> find top and bottom lines

def find_more_lines(im, y_from=150, y_to=920):
    p = px(im)
    found = []
    for y in range(y_from, y_to):
        rs=gs=bs=n=0
        for x in range(112, 690, 4):
            c = p[x,y]; rs+=c[0]; gs+=c[1]; bs+=c[2]; n+=1
        m = (rs/n, gs/n, bs/n)
        if abs(m[0]-24)<8 and abs(m[1]-32)<8 and abs(m[2]-46)<8:
            found.append(y)
    # group
    groups=[]
    for y in found:
        if groups and y-groups[-1][-1] <= 2: groups[-1].append(y)
        else: groups.append([y])
    return [ (g[0]+g[-1])//2 for g in groups ]

def occupancy(im, tag):
    ys = find_more_lines(im)
    print(tag, 'row line centers:', ys)
    # build 8 rows from line list; if 8 lines interior => rows between them
    return ys

for name in ['06_full.png', '01_main_classic.png', '07_clear.png']:
    im = load(name)
    occupancy(im, name)
