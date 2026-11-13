#!/usr/bin/env python3
"""R14 pass 5: zoomed ASCII on star/band/shadow zone (hero + clear), high precision."""
import os
from PIL import Image

R14 = "/home/z/my-project/critic_shots/r14"
R13 = "/home/z/my-project/critic_shots/r13"
CHARS = " .:-=+*#%@"

def lum(px): return 0.299*px[0]+0.587*px[1]+0.114*px[2]

def ascii_map(im, x0,y0,x1,y1, step=2, lo=0, hi=255):
    out=[]
    for y in range(y0,y1,step):
        line=[]
        for x in range(x0,x1,step):
            vals=[]
            for dy in range(step):
                for dx in range(step):
                    xx,yy=x+dx,y+dy
                    vals.append(lum(im.getpixel((xx,yy))))
            v=sum(vals)/len(vals)
            idx=int((v-lo)/(hi-lo)*len(CHARS))
            line.append(CHARS[max(0,min(idx,len(CHARS)-1))])
        out.append("".join(line))
    return out

def show(im,label,x0,y0,x1,y1,step=2,lo=0,hi=255):
    print(f"\n=== {label} x[{x0}..{x1}] y[{y0}..{y1}] step={step} range[{lo}-{hi}] ===")
    for i,line in enumerate(ascii_map(im,x0,y0,x1,y1,step,lo,hi)):
        print(f"{y0+i*step:4d}|{line}")

im = Image.open(os.path.join(R14,"01_hero.png")).convert("RGB")
# star zone left side: full detail
show(im, "HERO star zone", 16, 180, 210, 470, step=2)
# amplified contrast version to catch shadow
show(im, "HERO star zone AMPLIFIED", 16, 180, 210, 470, step=2, lo=0, hi=80)
