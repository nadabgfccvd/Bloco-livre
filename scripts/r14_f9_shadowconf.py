#!/usr/bin/env python3
"""R14 pass 9: shadow-on-band, isolated confetti A/B (r13 shards vs r14 squares), bevel trace, tray/HUD."""
import os, math
from PIL import Image
from collections import deque

R14 = "/home/z/my-project/critic_shots/r14"
R13 = "/home/z/my-project/critic_shots/r13"
def lum(px): return 0.299*px[0]+0.587*px[1]+0.114*px[2]

# ---------- A. shadow on band: luminance by x on band rows y352-358, clear shot ----------
im = Image.open(os.path.join(R14,"07_clear.png")).convert("RGB")
print("=== A. BAND top rows: luminance by x-segment (looking for shadow blob under star) ===")
for y in [352, 353, 354, 355, 356, 357, 358]:
    segs=[]
    for x0 in range(24, 696, 56):
        vals=[lum(im.getpixel((x,y))) for x in range(x0, x0+56)]
        segs.append(int(sum(vals)/len(vals)))
    print(f"  y={y}: {' '.join(f'{v:3d}' for v in segs)}")

# control: r13 clear shot same rows
im13 = Image.open(os.path.join(R13,"07_clear.png")).convert("RGB")
print("  R13 control:")
for y in [352, 353, 354, 355, 356, 357, 358]:
    segs=[]
    for x0 in range(24, 696, 56):
        vals=[lum(im13.getpixel((x,y))) for x in range(x0, x0+56)]
        segs.append(int(sum(vals)/len(vals)))
    print(f"  y={y}: {' '.join(f'{v:3d}' for v in segs)}")

# r13 star bottom / band top for gap A/B
print("\n=== A2. R13 star bottom & band top (x300-560 sat scan) ===")
for y in range(320, 360):
    sat=0; xs=[]
    for x in range(280, 580):
        r,g,b = im13.getpixel((x,y))[:3]
        mx,mn=max(r,g,b),min(r,g,b)
        if mx>60 and (mx-mn)/mx>0.45:
            sat+=1; xs.append(x)
    vals=[lum(im13.getpixel((x,y))) for x in range(40,680,8)]
    print(f"  y={y}: satpx={sat:3d} boardRowMeanL={sum(vals)/len(vals):6.1f}")

# ---------- B. isolated confetti component A/B ----------
print("\n=== B. CONFETTI component A/B (zone y120..348, excl. gold + star body) ===")
def confetti_components(path, label):
    im = Image.open(path).convert("RGB")
    W,H=im.size
    pts=set()
    for y in range(120, 348):
        for x in range(0, W):
            r,g,b = im.getpixel((x,y))[:3]
            mx,mn=max(r,g,b),min(r,g,b)
            if mx>60 and (mx-mn)/mx>0.45 and not (r>150 and g>110 and b<110 and (r-b)>60):
                pts.add((x,y))
    # remove star body: star is the huge component; find components first
    seen=set(); comps=[]
    for p in sorted(pts):
        if p in seen: continue
        q=deque([p]); seen.add(p); comp=[]
        while q:
            c=q.popleft(); comp.append(c)
            for d in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)):
                n=(c[0]+d[0],c[1]+d[1])
                if n in pts and n not in seen:
                    seen.add(n); q.append(n)
        comps.append(comp)
    big=[c for c in comps if len(c)>800]      # star + banner art
    small=[c for c in comps if 12<=len(c)<=800]
    tiny=[c for c in comps if len(c)<12]
    print(f"  {label}: total sat px={len(pts)}; big comps(>800, star/banner)={[len(c) for c in sorted(big,key=len,reverse=True)]}")
    print(f"  mid comps(12-800px)={len(small)}  tiny(<12)={len(tiny)}")
    # aspect stats for mid comps = confetti candidates
    aspects=[]; widths=[]; heights=[]; fills=[]
    for c in small:
        xs=[p[0] for p in c]; ys=[p[1] for p in c]
        w=max(xs)-min(xs)+1; h=max(ys)-min(ys)+1
        aspects.append(w/h); widths.append(w); heights.append(h)
        fills.append(len(c)/(w*h))
    if aspects:
        aspects_s=sorted(aspects)
        n=len(aspects)
        print(f"  confetti candidates: n={n} aspect min/med/max={aspects_s[0]:.2f}/{aspects_s[n//2]:.2f}/{aspects_s[-1]:.2f}")
        print(f"    aspect histogram: <0.5:{sum(1 for a in aspects if a<0.5)} 0.5-0.85:{sum(1 for a in aspects if 0.5<=a<0.85)} 0.85-1.2:{sum(1 for a in aspects if 0.85<=a<1.2)} 1.2-1.8:{sum(1 for a in aspects if 1.2<=a<1.8)} >=1.8:{sum(1 for a in aspects if a>=1.8)}")
        print(f"    mean fill={sum(fills)/len(fills):.2f}  mean w={sum(widths)/len(widths):.0f} h={sum(heights)/len(heights):.0f}")
        # list the 12 biggest mid comps
        for c in sorted(small,key=len,reverse=True)[:12]:
            xs=[p[0] for p in c]; ys=[p[1] for p in c]
            w=max(xs)-min(xs)+1; h=max(ys)-min(ys)+1
            print(f"      comp n={len(c):4d} bbox=({min(xs)},{min(ys)})-({max(xs)},{max(ys)}) w={w} h={h} aspect={w/h:.2f} fill={len(c)/(w*h):.2f}")
    return len(pts)

confetti_components(os.path.join(R14,"07_clear.png"), "R14-clear")
confetti_components(os.path.join(R13,"07_clear.png"), "R13-clear")

# ---------- C. bevel line trace (empty background only, hero shot) ----------
print("\n=== C. BEVEL diagonal trace (hero, empty-area bright-delta pixels) ===")
imh = Image.open(os.path.join(R14,"01_hero.png")).convert("RGB")
# bright pixels (lum 50-90) on dark background (<40) along a diagonal: scan for px with lum>55 where 8-neighborhood mean < 40
cand=[]
for y in range(196, 864):
    for x in range(30, 690):
        l=lum(imh.getpixel((x,y)))
        if 50<l<95:
            nb=[lum(imh.getpixel((x+dx,y+dy))) for dx in (-6,0,6) for dy in (-6,0,6) if not (dx==0 and dy==0)]
            mn=sum(nb)/len(nb)
            if mn<42 and l-mn>18:
                cand.append((x,y))
print(f"  isolated bright-on-dark px: {len(cand)}")
if cand:
    # fit: are they on a line? group by x, print y for x sample
    xs=sorted(set(p[0] for p in cand))
    print(f"  x range {xs[0]}..{xs[-1]}")
    pts_by_x={}
    for x,y in cand: pts_by_x.setdefault(x,[]).append(y)
    sample=xs[::40]
    print("  x: median y ->", {x:int(sorted(pts_by_x[x])[len(pts_by_x[x])//2]) for x in sample})
    ys=[p[1] for p in cand]
    print(f"  y range {min(ys)}..{max(ys)}  n={len(cand)}")
    # slope estimate
    import statistics
    xsA=[p[0] for p in cand]; ysA=[p[1] for p in cand]
    mx=sum(xsA)/len(xsA); my=sum(ysA)/len(ysA)
    sxy=sum((a-mx)*(b-my) for a,b in zip(xsA,ysA)); sxx=sum((a-mx)**2 for a in xsA)
    slope=sxy/sxx if sxx else 0
    print(f"  fitted slope dy/dx={slope:+.3f} (diagonal would be ~+1.0 or -1.0)")
