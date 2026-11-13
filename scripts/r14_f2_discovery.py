#!/usr/bin/env python3
"""R14 pass 2: element discovery — star bbox, gold px, saturated confetti px, streak strip."""
import os
from PIL import Image

R14 = "/home/z/my-project/critic_shots/r14"
SHOTS = ["01_hero.png","02_skin0.png","03_skin1.png","04_skin2.png","05_skin3.png","06_full.png","07_clear.png"]

def rgb2hsv_sat(r,g,b):
    mx,mn = max(r,g,b), min(r,g,b)
    v = mx
    s = 0 if mx==0 else (mx-mn)/mx
    return s, v

def gold_stats(im, region=None):
    """gold-ish: r>150, g>110, b<110, r>b+60 roughly"""
    W,H = im.size
    x0,y0,x1,y1 = region if region else (0,0,W,H)
    cnt=0; xs=[]; ys=[]
    for y in range(y0,y1):
        for x in range(x0,x1):
            r,g,b = im.getpixel((x,y))[:3]
            if r>150 and g>110 and b<110 and (r-b)>60:
                cnt+=1; xs.append(x); ys.append(y)
    if cnt:
        return cnt, (min(xs),min(ys),max(xs),max(ys))
    return 0, None

for s in SHOTS:
    im = Image.open(os.path.join(R14,s)).convert("RGB")
    W,H = im.size
    print(f"\n=== {s} {W}x{H} ===")
    # gold elements anywhere
    cnt, bb = gold_stats(im)
    print(f"  gold px total={cnt} bbox={bb}")
    # column histogram of gold in y<420 (star zone)
    cnt2, bb2 = gold_stats(im, region=(0,120,720,420))
    print(f"  gold px y120-420={cnt2} bbox={bb2}")

    # streak strip y1230-1260 brightness profile
    row_prof=[]
    for y in range(1225,1262,3):
        vals=[]
        for x in range(137,137+446,2):
            r,g,b=im.getpixel((x,y))[:3]
            vals.append(0.299*r+0.587*g+0.114*b)
        row_prof.append((y, round(sum(vals)/len(vals)), round(max(vals)), round(min(vals))))
    print("  streak strip profile (y, mean, max, min):", row_prof)

    # ticks at 25/50/75% of bar
    for pct in (0.25,0.5,0.75):
        tx = 137+int(pct*446)
        bright=0; tot=0
        peak=0
        for y in range(1232,1256):
            for x in range(tx-3,tx+4):
                r,g,b=im.getpixel((x,y))[:3]
                l=0.299*r+0.587*g+0.114*b
                tot+=1
                if l>100: bright+=1
                peak=max(peak,l)
        print(f"  tick @{pct:.0%} x={tx}: bright(>100)px={bright}/{tot} peakL={peak:.0f}")
