#!/usr/bin/env python3
"""R14 pass 4: ASCII render of key regions + region-mapped confetti + piece bevel scan."""
import os, sys
from PIL import Image

R14 = "/home/z/my-project/critic_shots/r14"
R13 = "/home/z/my-project/critic_shots/r13"

def lum(px): return 0.299*px[0]+0.587*px[1]+0.114*px[2]

CHARS = " .:-=+*#%@"

def ascii_map(im, x0,y0,x1,y1, step=4, mode="lum"):
    """Downsample region to ascii. mode lum | sat"""
    W,H = im.size
    out=[]
    for y in range(y0,y1,step):
        line=[]
        for x in range(x0,x1,step*1):
            # block sample
            vals=[]
            for dy in range(step):
                for dx in range(step):
                    xx,yy = x+dx,y+dy
                    if xx<W and yy<H:
                        px = im.getpixel((xx,yy))
                        if mode=="lum":
                            vals.append(lum(px))
                        else:
                            mx,mn=max(px[:3]),min(px[:3])
                            vals.append(255 if (mx>50 and (mx-mn)/max(mx,1)>0.4) else 0)
            v = sum(vals)/max(len(vals),1)
            idx = int(v/256*len(CHARS))
            line.append(CHARS[min(idx,len(CHARS)-1)])
        out.append("".join(line))
    return out

def show(im, label, x0,y0,x1,y1, step=4, mode="lum"):
    print(f"\n=== {label} region x[{x0}..{x1}] y[{y0}..{y1}] step={step} mode={mode} ===")
    for i,line in enumerate(ascii_map(im,x0,y0,x1,y1,step,mode)):
        print(f"{y0+i*step:4d}|{line}")

im = Image.open(os.path.join(R14,"01_hero.png")).convert("RGB")
# Top zone: title / star / band
show(im, "HERO top (star zone)", 0, 120, 720, 420, step=4)
