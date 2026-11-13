#!/usr/bin/env python3
"""R14 pass 12: R13-vs-R14 pixel diff (where did changes land?) + shadow-on-band fine scan."""
import os
from PIL import Image

R14 = "/home/z/my-project/critic_shots/r14"
R13 = "/home/z/my-project/critic_shots/r13"
def lum(px): return 0.299*px[0]+0.587*px[1]+0.114*px[2]

print("=== A. R13 vs R14 DIFF (hero): classify changed px by zone ===")
a = Image.open(os.path.join(R13,"01_hero.png")).convert("RGB")
b = Image.open(os.path.join(R14,"01_hero.png")).convert("RGB")
W,H = a.size
zones = {
  "board-area (24-696,190-866)": (24,190,696,866),
  "board-empty-only (background strips)": None,  # computed later
  "top strip (0-720,0-190)": (0,0,720,190),
  "tray (0-720,860-1142)": (0,860,720,1142),
  "streak strip (100-620,1225-1262)": (100,1225,620,1262),
  "rest": None,
}
diffpx=[]
for y in range(0,H,1):
    for x in range(0,W,1):
        pa=a.getpixel((x,y)); pb=b.getpixel((x,y))
        if pa!=pb:
            diffpx.append((x,y,pa,pb))
print(f"  total changed px: {len(diffpx)} / {W*H}")
# classify
def inzone(p,z):
    return z[0]<=p[0]<z[2] and z[1]<=p[1]<z[3]
counts={}
for (x,y,pa,pb) in diffpx:
    for name,z in zones.items():
        if z and inzone((x,y),z):
            counts[name]=counts.get(name,0)+1
            break
    else:
        counts["rest"]=counts.get("rest",0)+1
for k,v in sorted(counts.items(), key=lambda kv:-kv[1]):
    print(f"  {k}: {v}")
# diff spatial pattern in board area: are diffs at well centers (vignette) or on diagonal lines?
bd=[(x,y,pa,pb) for (x,y,pa,pb) in diffpx if 24<=x<696 and 190<=y<866]
print(f"  board-area diffs: {len(bd)}")
# histogram of diff delta lum
import collections
deltas=collections.Counter()
for (x,y,pa,pb) in bd:
    d=lum(pb)-lum(pa)
    deltas[round(d)]+=1
print("  delta-lum histogram (board area):", dict(sorted(deltas.items())))
# check: are board diffs restricted to empty wells? sample some diff points and check if inside a well
def well_of(x,y):
    c=(x-66)//84; r=(y-232)//84
    cx=66+c*84; cy=232+r*84
    if abs(x-cx)<=34 and abs(y-cy)<=34: return (c,r)
    return None
inwell=0; outwell=0; outpts=[]
for (x,y,pa,pb) in bd:
    w=well_of(x,y)
    if w: inwell+=1
    else:
        outwell+=1; outpts.append((x,y,pa,pb))
print(f"  board diffs inside wells: {inwell}, outside wells (rims/gaps): {outwell}")
if outpts:
    print(f"  sample outside-well diffs: {outpts[:10]}")
    # are they on a diagonal line? fit
    xs=[p[0] for p in outpts]; ys=[p[1] for p in outpts]
    mx=sum(xs)/len(xs); my=sum(ys)/len(ys)
    sxy=sum((u-mx)*(v-my) for u,v in zip(xs,ys)); sxx=sum((u-mx)**2 for u in xs)
    print(f"  outside-well diff slope: {sxy/sxx if sxx else 0:+.3f}; bbox x[{min(xs)}..{max(xs)}] y[{min(ys)}..{max(ys)}]")

# diagonal structure among outside-well diffs? cluster by y-x
if outpts:
    ymx=collections.Counter()
    for (x,y,pa,pb) in outpts:
        ymx[y-x]+=1
    top=ymx.most_common(8)
    print(f"  y-x clustering (diagonal lines would share constant y-x): {top}")

print("\n=== B. SHADOW fine scan: dark px on band & gap (07_clear vs R13) ===")
for tag, path in [("R14", os.path.join(R14,"07_clear.png")), ("R13", os.path.join(R13,"07_clear.png"))]:
    im=Image.open(path).convert("RGB")
    for (y0,y1,thr,label) in [(344,351,120,"gap strip y344-350"),(351,359,160,"band y351-358"),(359,367,140,"band lower y359-366")]:
        dark=0; xs=[]; ys=[]
        for y in range(y0,y1):
            for x in range(280,545):
                l=lum(im.getpixel((x,y)))
                if l<thr:
                    dark+=1; xs.append(x); ys.append(y)
        if dark:
            print(f"  {tag} {label} dark(<{thr}): {dark} bbox x[{min(xs)}..{max(xs)}] y[{min(ys)}..{max(ys)}] centroid=({sum(xs)/len(xs):.0f},{sum(ys)/len(ys):.0f})")
        else:
            print(f"  {tag} {label} dark(<{thr}): 0")

# star bbox for offset math
im=Image.open(os.path.join(R14,"07_clear.png")).convert("RGB")
spts=[]
for y in range(190, 348):
    for x in range(280, 545):
        r,g,b = im.getpixel((x,y))[:3]
        mx,mn=max(r,g,b),min(r,g,b)
        if mx>60 and (mx-mn)/mx>0.45:
            spts.append((x,y))
xs=[p[0] for p in spts]; ys=[p[1] for p in spts]
print(f"\n  R14 star bbox x[{min(xs)}..{max(xs)}] y[{min(ys)}..{max(ys)}]; bottom edge by row:")
for y in range(330,348):
    row=[x for (x,yy) in spts if yy==y]
    if row: print(f"    y={y}: xs {min(row)}..{max(row)}")
