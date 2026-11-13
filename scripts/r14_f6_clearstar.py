#!/usr/bin/env python3
"""R14 pass 6: clear-shot star zone ASCII + shape hunt."""
import os
from PIL import Image

R14 = "/home/z/my-project/critic_shots/r14"
CHARS = " .:-=+*#%@"
def lum(px): return 0.299*px[0]+0.587*px[1]+0.114*px[2]

def ascii_map(im, x0,y0,x1,y1, step=2, lo=0, hi=255):
    out=[]
    for y in range(y0,y1,step):
        line=[]
        for x in range(x0,x1,step):
            vals=[lum(im.getpixel((min(x+dx,im.size[0]-1),min(y+dy,im.size[1]-1)))) for dy in range(step) for dx in range(step)]
            v=sum(vals)/len(vals)
            idx=int((v-lo)/(hi-lo)*len(CHARS))
            line.append(CHARS[max(0,min(idx,len(CHARS)-1))])
        out.append("".join(line))
    return out

def show(im,label,x0,y0,x1,y1,step=2,lo=0,hi=255):
    print(f"\n=== {label} x[{x0}..{x1}] y[{y0}..{y1}] step={step} range[{lo}-{hi}] ===")
    for i,line in enumerate(ascii_map(im,x0,y0,x1,y1,step,lo,hi)):
        print(f"{y0+i*step:4d}|{line}")

im = Image.open(os.path.join(R14,"07_clear.png")).convert("RGB")
show(im, "CLEAR full board width top", 16, 180, 704, 400, step=3)
show(im, "CLEAR star zone AMPLIFIED", 200, 180, 520, 400, step=2, lo=0, hi=90)
