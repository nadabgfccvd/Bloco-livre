#!/usr/bin/env python3
"""R14 pass 10: bevel hunt on piece faces + y535 structure; tray/HUD ascii; crops."""
import os, math
from PIL import Image

R14 = "/home/z/my-project/critic_shots/r14"
R13 = "/home/z/my-project/critic_shots/r13"
CHARS = " .:-=+*#%@"
def lum(px): return 0.299*px[0]+0.587*px[1]+0.114*px[2]

# ---------- A. piece-face internal structure (bevel line?) ----------
imh = Image.open(os.path.join(R14,"01_hero.png")).convert("RGB")
imh13 = Image.open(os.path.join(R13,"01_hero.png")).convert("RGB")
print("=== A. PIECE face internal lines (hero piece at well(3,2): cx=318? no: 66+3*84=318, cy=232+2*84=400) ===")
def face_lines(im, cx, cy, rad=30, label=""):
    print(f"  {label} face at ({cx},{cy}):")
    # horizontal profile at mid: look for line-like bumps
    for dy in (-20,-10,0,10,20):
        row=[lum(im.getpixel((x,cy+dy))) for x in range(cx-rad,cx+rad)]
        # find local maxima that stand out
        peaks=[]
        for i in range(2,len(row)-2):
            if row[i]>row[i-2]+6 and row[i]>row[i+2]+6 and row[i]>60:
                peaks.append((cx-rad+i, round(row[i])))
        print(f"    dy={dy:+3d}: mean={sum(row)/len(row):6.1f} peaks={peaks[:6]}")
face_lines(imh, 318, 400, 30, "R14")
face_lines(imh13, 318, 400, 30, "R13")

# diagonal scan within face: for each diag offset, count bright px along the two diagonals
def diag_scan(im, cx, cy, label):
    best=[]
    for k in range(-30,31,1):
        # diagonal A: points (cx+t, cy+t+k) t=-25..25
        valsA=[lum(im.getpixel((cx+t, cy+t+k))) for t in range(-25,26) if 0<=cy+t+k<1440]
        # anti-diagonal B: (cx+t, cy-t+k)
        valsB=[lum(im.getpixel((cx+t, cy-t+k))) for t in range(-25,26) if 0<=cy-t+k<1440]
        if len(valsA)>40:
            ma=sum(valsA)/len(valsA); mb=sum(valsB)/len(valsB)
            best.append((k, round(ma,1), round(mb,1)))
    highs=[b for b in best if b[1]>100 or b[2]>100]
    print(f"  {label}: diag means (k, diagA, diagB) top: {sorted(best,key=lambda b:max(b[1],b[2]),reverse=True)[:5]}")
print("  diagonal streak scan on piece face:")
diag_scan(imh, 318, 400, "R14")
diag_scan(imh13, 318, 400, "R13")

# ---------- B. what is the y~535 horizontal structure? ----------
print("\n=== B. y535 horizontal structure (hero) ===")
for y in [533,535,537]:
    row=[lum(imh.getpixel((x,y))) for x in range(24,696,4)]
    bright=[24+4*i for i,v in enumerate(row) if v>55]
    print(f"  y={y}: n>55lum={len(bright)} xs={bright[:20]}")
# compare r13
for y in [533,535,537]:
    row=[lum(imh13.getpixel((x,y))) for x in range(24,696,4)]
    bright=[24+4*i for i,v in enumerate(row) if v>55]
    print(f"  R13 y={y}: n>55lum={len(bright)} xs={bright[:20]}")

# ---------- C. gap-area diagonal chain search (background only, no pieces) ----------
print("\n=== C. diagonal chain search in empty background region y700-860 ===")
def chains(im, label):
    found=0; samples=[]
    for x0 in range(30, 660):
        for y0 in range(700, 850):
            # chain of 12 px along +1,+1
            ok=0
            for t in range(12):
                x,y = x0+t, y0+t
                l=lum(im.getpixel((x,y)))
                if 45<l<95:
                    nb=[lum(im.getpixel((x+dx,y+dy))) for dx in (-3,3) for dy in (-3,3) if not(dx==0 and dy==0)]
                    if l - sum(nb)/len(nb) > 12: ok+=1
            if ok>=10:
                found+=1; samples.append((x0,y0))
    print(f"  {label}: 12px diagonal chains found: {found} samples={samples[:8]}")
chains(imh, "R14-hero")
chains(imh13, "R13-hero")

# ---------- D. tray + HUD ascii ----------
def ascii_map(im, x0,y0,x1,y1, step=4):
    out=[]
    for y in range(y0,y1,step):
        line=[]
        for x in range(x0,x1,step):
            vals=[lum(im.getpixel((min(x+dx,719),min(y+dy,1439)))) for dy in range(step) for dx in range(step)]
            v=sum(vals)/len(vals)
            line.append(CHARS[min(int(v/256*len(CHARS)),len(CHARS)-1)])
        out.append("".join(line))
    return out
def show(im,label,x0,y0,x1,y1,step=4):
    print(f"\n=== {label} x[{x0}..{x1}] y[{y0}..{y1}] ===")
    for i,l in enumerate(ascii_map(im,x0,y0,x1,y1,step)):
        print(f"{y0+i*step:4d}|{l}")
show(imh, "HERO tray", 0, 860, 720, 1150, 6)
show(imh, "HERO bottom HUD", 0, 1150, 720, 1440, 6)
