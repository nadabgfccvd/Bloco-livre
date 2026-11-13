#!/usr/bin/env python3
"""ASCII render of key regions (since model cannot view images): downsample to ASCII art
so I can 'see' the composition numerically. Also the r5 vs r6 celebration diff.
"""
import sys
sys.path.insert(0, '/home/z/my-project/scripts')
from r6_forensics_lib import *

def ascii_render(name, root, box, gw=72, chars=' .:-=+*#%@'):
    im = load(name, root).convert('L').crop(box).resize((gw, max(1, int((box[3]-box[1])/(box[2]-box[0])*gw*0.5))))
    p = im.load(); w, h = im.size
    print(f'== {name} {box} (lum ASCII) ==')
    for y in range(h):
        row = ''.join(chars[min(9, p[x,y]*10//256)] for x in range(w))
        print(row)
    print()

# celebration top r6 vs r5
ascii_render('07_clear.png', R6, (0, 0, 720, 200))
ascii_render('07_clear.png', R5, (0, 0, 720, 200))
ascii_render('07_clear.png', R6, (0, 200, 720, 900), gw=72)
