#!/usr/bin/env python3
"""R14 pass 7: precise star/gap/shadow + vignette radial + confetti zone count."""
import os, math
from PIL import Image

R14 = "/home/z/my-project/critic_shots/r14"
R13 = "/home/z/my-project/critic_shots/r13"
def lum(px): return 0.299*px[0]+0.587*px[1]+0.114*px[2]

# ---------- A. star precision on 07_clear ----------
im = Image.open(os.path.join(R14,"07_clear.png")).convert("RGB")
W,H = im.size
print("=== A. STAR precise row scan (07_clear) x[300..560] ===")
for y in range(330, 365):
    sat=0; xs=[]
    for x in range(280, 580):
        r,g,b = im.getpixel((x,y))[:3]
        mx,mn = max(r,g,b),min(r,g,b)
        if mx>60 and (mx-mn)/mx>0.45:
            sat+=1; xs.append(x)
    lrow=[lum(im.getpixel((x,y))) for x in range(24,696,8)]
    print(f"  y={y}: satpx={sat:3d} x[{min(xs) if xs else '-'}..{max(xs) if xs else '-'}] boardRowMeanL={sum(lrow)/len(lrow):.0f}")
print("  band top: first y where full-width bright strip")
for y in range(344, 360):
    vals=[lum(im.getpixel((x,y))) for x in range(40,680,4)]
    print(f"  y={y}: mean={sum(vals)/len(vals):6.1f} max={max(vals):.0f} min={min(vals):.0f}")

print("\n=== A2. DROP SHADOW on/under star zone (07_clear) ===")
# dark px (lum<60) in y350-425, x280-580, that are NOT the dark background wells:
# background empty wells in clear shot ~57-70 lum; shadow should be darker (<45)
tot_dark=0; pts=[]
for y in range(350, 430):
    for x in range(260, 600):
        l=lum(im.getpixel((x,y)))
        if l<45:
            tot_dark+=1; pts.append((x,y))
if pts:
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    print(f"  very-dark(<45) px in y350-430 x260-600: {tot_dark} bbox x[{min(xs)}..{max(xs)}] y[{min(ys)}..{max(ys)}]")
    # centroid
    cx=sum(xs)/len(xs); cy=sum(ys)/len(ys)
    print(f"  centroid=({cx:.0f},{cy:.0f})")
# star centroid from saturated px above band
spts=[]
for y in range(190, 348):
    for x in range(280, 580):
        r,g,b = im.getpixel((x,y))[:3]
        mx,mn=max(r,g,b),min(r,g,b)
        if mx>60 and (mx-mn)/mx>0.45 and not (r>150 and g>110 and b<110):
            spts.append((x,y))
if spts:
    sx=sum(p[0] for p in spts)/len(spts); sy=sum(p[1] for p in spts)/len(spts)
    print(f"  star(sat non-gold) px={len(spts)} centroid=({sx:.0f},{sy:.0f}) bbox x[{min(p[0] for p in spts)}..{max(p[0] for p in spts)}] y[{min(p[1] for p in spts)}..{max(p[1] for p in spts)}]")

# ---------- B. confetti count in celebration zone (above band) ----------
print("\n=== B. CONFETTI count y[120..348] (07_clear, whole width) ===")
cnt=0
for y in range(120, 348):
    for x in range(0, W):
        r,g,b = im.getpixel((x,y))[:3]
        mx,mn=max(r,g,b),min(r,g,b)
        if mx>60 and (mx-mn)/mx>0.45 and not (r>150 and g>110 and b<110 and (r-b)>60):
            cnt+=1
print(f"  saturated non-gold px y120-348: {cnt}")

# same for hero (confetti in hero? zone above board only y120-188)
cnt2=0
imh = Image.open(os.path.join(R14,"01_hero.png")).convert("RGB")
for y in range(120, 188):
    for x in range(0, 720):
        r,g,b = imh.getpixel((x,y))[:3]
        mx,mn=max(r,g,b),min(r,g,b)
        if mx>60 and (mx-mn)/mx>0.45 and not (r>150 and g>110 and b<110 and (r-b)>60):
            cnt2+=1
print(f"  hero y120-188 saturated non-gold: {cnt2}")

# r13 clear shot same zone for comparison
imc13 = Image.open(os.path.join(R13,"07_clear.png")).convert("RGB")
cnt3=0
for y in range(120, 348):
    for x in range(0, 720):
        r,g,b = imc13.getpixel((x,y))[:3]
        mx,mn=max(r,g,b),min(r,g,b)
        if mx>60 and (mx-mn)/mx>0.45 and not (r>150 and g>110 and b<110 and (r-b)>60):
            cnt3+=1
print(f"  R13 clear y120-348 saturated non-gold: {cnt3}")

# ---------- C. vignette radial analysis ----------
print("\n=== C. VIGNETTE radial (empty wells only) ===")
def well_center(c,r): return (66+c*84, 232+r*84)
def well_lum(im,c,r,rad=12):
    cx,cy=well_center(c,r)
    vals=[lum(im.getpixel((int(cx+dx),int(cy+dy)))) for dy in range(-rad,rad+1,3) for dx in range(-rad,rad+1,3)]
    return sum(vals)/len(vals)
def is_empty(im,c,r,thr=95):
    return well_lum(im,c,r)<thr

def vignette_report(path,label):
    im=Image.open(path).convert("RGB")
    empt=[]
    for r in range(8):
        for c in range(8):
            L=well_lum(im,c,r)
            if L<95:
                cx,cy=well_center(c,r)
                d=math.hypot(cx-360, cy-526)/84.0  # in cells
                empt.append((d,L))
    if not empt:
        print(f"  {label}: no empty wells"); return
    # bucket by distance
    inner=[L for d,L in empt if d<=2.2]
    outer=[L for d,L in empt if d>=4.0]
    mid=[L for d,L in empt if 2.2<d<4.0]
    fmt=lambda v: f"{sum(v)/len(v):.1f}(n={len(v)})" if v else "-"
    print(f"  {label}: inner(d<=2.2)={fmt(inner)} mid={fmt(mid)} outer(d>=4.0)={fmt(outer)}")
    if inner and outer:
        pct=(sum(outer)/len(outer)-sum(inner)/len(inner))/(sum(inner)/len(inner))*100
        print(f"    outer-vs-inner delta: {pct:+.1f}%")

for s in ["01_hero.png","02_skin0.png"]:
    vignette_report(os.path.join(R14,s), "R14 "+s)
    vignette_report(os.path.join(R13,s), "R13 "+s)
