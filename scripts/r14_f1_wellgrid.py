#!/usr/bin/env python3
"""R14 forensics pass 1: inventory + well luminance grid per shot."""
import os
from PIL import Image

R14 = "/home/z/my-project/critic_shots/r14"
R13 = "/home/z/my-project/critic_shots/r13"
SHOTS = ["01_hero.png","02_skin0.png","03_skin1.png","04_skin2.png","05_skin3.png","06_full.png","07_clear.png"]

CELL = 84
CX, CY = 360.0, 526.0

def well_center(col, row):
    return (66 + col*CELL, 232 + row*CELL)

def lum(px):
    r,g,b = px[:3]
    return 0.299*r + 0.587*g + 0.114*b

def grid(path, label):
    im = Image.open(path).convert("RGB")
    W,H = im.size
    print(f"\n=== {label} {os.path.basename(path)} size={W}x{H} mode=RGB ===")
    rows = []
    for row in range(8):
        line = []
        for col in range(8):
            cx, cy = well_center(col,row)
            # central 28x28 patch of the well (avoid rim)
            vals = []
            for dy in range(-14,15,2):
                for dx in range(-14,15,2):
                    x,y = cx+dx, cy+dy
                    if 0<=x<W and 0<=y<H:
                        vals.append(lum(im.getpixel((int(x),int(y)))))
            m = sum(vals)/len(vals)
            line.append(f"{m:5.0f}")
        rows.append(" ".join(line))
    print("Well center luminance grid (cols 0-7 left->right, rows 0-7 top->bottom):")
    for r_ in rows:
        print("   "+r_)

for s in SHOTS:
    grid(os.path.join(R14,s), "R14")
