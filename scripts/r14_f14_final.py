#!/usr/bin/env python3
"""R14 pass 14 (final): map added-bright px (bevel); confetti rotation evidence; whole-game ascii."""
import os, collections
from PIL import Image

R14 = "/home/z/my-project/critic_shots/r14"
R13 = "/home/z/my-project/critic_shots/r13"
CHARS = " .:-=+*#%@"
def lum(px): return 0.299*px[0]+0.587*px[1]+0.114*px[2]

a = Image.open(os.path.join(R13,"01_hero.png")).convert("RGB")
b = Image.open(os.path.join(R14,"01_hero.png")).convert("RGB")

print("=== A. BEVEL map: added-bright px (delta+12..+45), board area, 8px cells ===")
grid=[[' ']*84 for _ in range(85)]
for y in range(190,866):
    for x in range(24,696):
        d=lum(b.getpixel((x,y)))-lum(a.getpixel((x,y)))
        if 12<=d<=45:
            gx=(x-24)//8; gy=(y-190)//8
            if 0<=gy<85 and 0<=gx<84:
                grid[gy][gx]='#'
for i,row in enumerate(grid):
    line="".join(row)
    if line.strip(): print(f"  y{190+i*8:3d}|{line}")

print("\n=== A2. exact line endpoints: x+y clusters ===")
pts=collections.defaultdict(list)
for y in range(190,866):
    for x in range(24,696):
        d=lum(b.getpixel((x,y)))-lum(a.getpixel((x,y)))
        if 12<=d<=45:
            pts[x+y].append((x,y))
for k in sorted(pts):
    v=pts[k]
    if len(v)>=60:
        xs=[p[0] for p in v]
        print(f"  x+y={k}: n={len(v)} x[{min(xs)}..{max(xs)}]")

print("\n=== B. confetti rotation: edge analysis of 3 comps (clear shot) ===")
im=Image.open(os.path.join(R14,"07_clear.png")).convert("RGB")
def comp_mask(x0,y0,x1,y1):
    m=[]
    for y in range(y0,y1+1):
        row=[]
        for x in range(x0,x1+1):
            r,g,b=im.getpixel((x,y))[:3]
            mx,mn=max(r,g,b),min(r,g,b)
            row.append(1 if (mx>60 and (mx-mn)/mx>0.45) else 0)
        m.append(row)
    return m
def show_mask(m,label):
    print(f"  {label}:")
    for row in m: print("    "+"".join('#' if v else '.' for v in row))
show_mask(comp_mask(22,245,45,268), "comp A (22,245)-(45,268) fill 0.61")
show_mask(comp_mask(111,308,130,327), "comp B (111,308)-(130,327) fill 0.58")

print("\n=== C. whole-game overview ascii (hero, y0-1440 step 12) ===")
def overview(path,label):
    im=Image.open(path).convert("RGB")
    print(f"  --- {label} ---")
    for y in range(0,1440,12):
        line=[]
        for x in range(0,720,6):
            vals=[lum(im.getpixel((min(x+dx,719),min(y+dy,1439)))) for dy in range(12) for dx in range(6)]
            line.append(CHARS[min(int(sum(vals)/len(vals)/256*len(CHARS)),9)])
        print(f"  {y:4d}|"+"".join(line))
overview(os.path.join(R14,"01_hero.png"),"R14 hero")
