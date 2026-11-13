#!/usr/bin/env python3
"""Last gaps:
1) 07_clear: exact estrela-mor geometry at the right place. Find biggest
   symmetric 4/5-point star cluster between banner and board bottom.
2) 06_full: red elements at top (y180-230 red rows seen) — danger banner?
3) hero: text at y30-52 — PONTOS digits size, and label size (values vs labels)
4) manifest claim: compare r6/r7 skin files byte-identical? (they were 0% diff
   in content; check filenames registered = launcher activities proxy:
   count distinct layout structures across 7 shots (identical bottom UI rows)."""
import os
from PIL import Image
import numpy as np
from scipy import ndimage

R7 = "/home/z/my-project/critic_shots/r7"
R6 = "/home/z/my-project/critic_shots/r6"
def load(p): return np.asarray(Image.open(p).convert("RGB")).astype(int)
CELL=85.0

# 1) star on clear: search region y516..1255 (board area, no pieces = clear board?)
a = load(os.path.join(R7,"07_clear.png"))
r,g,b = a[...,0],a[...,1],a[...,2]
lum = 0.299*r+0.587*g+0.114*b
print("1) board area content on clear shot:")
occ_rows = []
for y in range(516, 1255, 85):
    seg = lum[y:y+85, 24:696]
    print(f"   y{y}: mean lum {seg.mean():.1f}, max {seg.max():.0f}, bright(>170) px {(seg>170).sum()}")

# star: biggest bright cluster in y516-1255
m = lum>170
mm = m.copy(); mm[:516,:]=False
lbl,n = ndimage.label(mm)
sizes = ndimage.sum(mm,lbl,range(1,n+1))
print("   bright clusters in board zone:")
for i in np.argsort(sizes)[::-1][:8]:
    if sizes[i]<30: break
    ys_,xs_ = np.where(lbl==i+1)
    bw=xs_.max()-xs_.min()+1; bh=ys_.max()-ys_.min()+1
    seg = a[ys_.min():ys_.max()+1, xs_.min():xs_.max()+1]
    print(f"   sz={int(sizes[i]):5d} {bw}x{bh}px ({bw/CELL:.2f} cell) at ({xs_.min()},{ys_.min()}) rgb={seg.reshape(-1,3).mean(axis=0).round(0)}")

# 2) 06_full red rows y180-230
a6 = load(os.path.join(R7,"06_full.png"))
r6_,g6_,b6_ = a6[...,0],a6[...,1],a6[...,2]
red = (r6_>150)&(r6_-g6_>60)&(r6_-b6_>60)
rows_ = np.where(red.sum(axis=1)>100)[0]
print(f"\n2) 06_full red rows>100px: {rows_.min() if len(rows_) else '-'}..{rows_.max() if len(rows_) else '-'} n={len(rows_)}")
if len(rows_):
    y0,y1 = rows_.min(), rows_.max()
    seg = a6[y0:y1+1]
    # red components
    lbl,n = ndimage.label(red[y0:y1+1])
    sizes = ndimage.sum(red[y0:y1+1],lbl,range(1,n+1))
    for i in np.argsort(sizes)[::-1][:6]:
        if sizes[i]<50: break
        ys_,xs_ = np.where(lbl==i+1)
        print(f"   red comp sz={int(sizes[i])} {xs_.max()-xs_.min()+1}x{ys_.max()-ys_.min()+1} at ({xs_.min()+0},{ys_.min()+y0})")
# text in red zone?
whiter = (a6[...,0]>220)&(a6[...,1]>220)&(a6[...,2]>220)
seg = whiter[y0:y1+1,:]
rowsw = np.where(seg.sum(axis=1)>10)[0]
print(f"   white text rows in red zone: {rowsw.tolist()[:10] if len(rowsw) else 'none'}")

# 3) HUD hero: y30-52 group. Split glyph columns into words; measure cap heights
ah = load(os.path.join(R7,"01_hero.png"))
lumh = 0.299*ah[...,0]+0.587*ah[...,1]+0.114*ah[...,2]
whiteh = lumh>150
seg = whiteh[0:130,:]
rows_ = np.where(seg.sum(axis=1)>6)[0]
print("\n3) hero HUD groups:")
groups=[]
if len(rows_):
    s=rows_[0]; p=rows_[0]
    for y in rows_[1:]:
        if y-p>3: groups.append((s,p)); s=y
        p=y
    groups.append((s,p))
for gs,ge in groups:
    h=ge-gs+1
    s2 = whiteh[gs:ge+1,:]
    cols_ = np.where(s2.sum(axis=0)>0)[0]
    # word groups (gap > 12px)
    words=[]
    if len(cols_):
        s=cols_[0]; p=cols_[0]
        for x in cols_[1:]:
            if x-p>12: words.append((s,p)); s=x
            p=x
        words.append((s,p))
    print(f"  y{gs}..{ge} h={h}px words: {[(w[0],w[1],w[1]-w[0]+1) for w in words]}")

# 4) file identity: R6 skin files vs R7 skin files (bytes)
import hashlib
print("\n4) R6 vs R7 file identity (md5):")
for name in ["02_skin0.png","03_skin1.png","04_skin2.png","05_skin3.png","06_full.png","07_clear.png"]:
    h6 = hashlib.md5(open(os.path.join(R6,name),'rb').read()).hexdigest()[:10]
    h7 = hashlib.md5(open(os.path.join(R7,name),'rb').read()).hexdigest()[:10]
    print(f"   {name}: R6={h6} R7={h7} {'IDENTICAL' if h6==h7 else 'DIFFERENT'}")

# 5) cross-shot identity: hero vs skins board layouts — is hero board distinct?
h_hero = hashlib.md5(open(os.path.join(R7,'01_hero.png'),'rb').read()).hexdigest()[:10]
print(f"   01_hero.png md5 {h_hero}")
# board zone crops hash: compare hero board to skin0 board
def board_hash(p):
    im = Image.open(p).convert("RGB").crop((24,123,696,1254))
    return hashlib.md5(im.tobytes()).hexdigest()[:10]
for fn in ["01_hero.png","02_skin0.png","06_full.png","07_clear.png"]:
    print(f"   board-zone md5 {fn}: {board_hash(os.path.join(R7,fn))}")
for fn in ["01_main_classic.png","02_skin0.png","06_full.png","07_clear.png"]:
    print(f"   board-zone md5 R6 {fn}: {board_hash(os.path.join(R6,fn))}")
