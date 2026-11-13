#!/usr/bin/env python3
"""R12 part Q: hero 01 — does a star exist in hero header? measure hero band & any star/gap;
plus celebration confetti zone; HUD title; skin tray gradients; final score compilation data."""
from PIL import Image
import numpy as np

R12 = '/home/z/my-project/critic_shots/r12/'
R11 = '/home/z/my-project/critic_shots/r11/'

def load(p):
    return np.asarray(Image.open(p).convert('RGB')).astype(int)

# HERO: the "band" in hero — measure its top (rows 350-380) and any floating emblem above.
# From part C: hero band top around y364-366 (bright rise). Star? In hero the region x280-530 y200-350
# was pure flat bg (24,32,46). So hero has NO star. Confirm across r11/r12 hero.
for tag in ('r11','r12'):
    im = load((R11 if tag=='r11' else R12)+'01_hero.png')
    R, G, B = im[:,:,0], im[:,:,1], im[:,:,2]
    gold = (R > 200) & (G > 140) & (B < 200) & (R - B > 60)
    zone = gold[196:356, 220:520]
    print(f"{tag} hero gold px in star zone (y196-356, x220-520):", zone.sum())

# So star/band business is only in 07_clear. In hero, band = "next piece" preview strip?
# From ASCII: hero rows 366-430 show 7 blocks of gold/pale — that's the NEXT-PIECE tray!
# Wait — geometry says tray panel y~860-1142. But hero row 366-430 blocks: that's likely a
# horizontal band under HUD. Re-map hero rows 452-470 (board top) etc.
imh = load(R12+'01_hero.png')
lumh = imh.mean(axis=2)
print("\nhero row means 440..470:", [round(lumh[y,:].mean(),1) for y in range(440,471,2)])

# hero band = rows ~364..436 (the gold strip with 7 pale blocks). Its top:
R, G, B = imh[:,:,0], imh[:,:,1], imh[:,:,2]
gold = (R > 200) & (G > 140) & (B < 200) & (R - B > 60)
for y in range(356, 370):
    print(y, "gold frac x40-680:", round(gold[y, 40:680].mean(),2))

# ===== confetti zone in 07_clear rows 470-500 =====
im7 = load(R12+'07_clear.png')
lum7 = im7.mean(axis=2)
print("\nconfetti rows 470-500: count bright px per row (x40-680):")
for y in range(468, 505, 2):
    print(y, int((lum7[y, 40:680] > 150).sum()))

# ===== celebration banner height =====
ys, xs = np.where(gold)
m = (ys >= 354) & (ys <= 470)
print("\ncelebration banner gold rows extent:", ys[m].min(), "..", ys[m].max())

# ===== skin tray gradient check (02-05): rows 834-893 diffs (already shown >0) — do skins also
# carry the same 3-step gradient? verify step pattern 38/16/28 in one skin:
a = load(R11+'03_skin1.png'); b = load(R12+'03_skin1.png')
d = np.abs(a-b).mean(axis=2)[:, 40:680]
print("\nskin1 gradient steps:", [(y, round(d[y].mean(),1)) for y in (840, 860, 862, 865, 875, 887, 890)])

# ===== board gem layout: count gems per skin and distinct palettes =====
for nm in ['02_skin0','03_skin1','04_skin2','05_skin3']:
    im = load(R12+nm+'.png')
    board = im[190:866, 24:696]
    q = (board//32).reshape(-1,3)
    uniq = np.unique(q, axis=0)
    print(f"\n{nm}: board coarse colors: {len(uniq)}")
    # dominant colors
    from collections import Counter
    c = Counter(map(tuple, (board//32).reshape(-1,3).tolist()))
    for col, n in c.most_common(8):
        print("   ", tuple(v*32 for v in col), n)

# ===== streak bar (hero): width/height exact =====
imh = load(R12+'01_hero.png')
R, G, B = imh[:,:,0], imh[:,:,1], imh[:,:,2]
gold = (R > 200) & (G > 150) & (B < 130)
zone = gold[1230:1260, :]
ys, xs = np.where(zone)
print("\nstreak bar: rows", 1230+ys.min(), "..", 1230+ys.max(), "cols", xs.min(), "..", xs.max(), "height", ys.max()-ys.min()+1, "width", xs.max()-xs.min()+1)
# what's inside streak? sample colors
for x in range(xs.min(), xs.max()+1, 40):
    y = 1245
    print("   x=", x, (R[y,x], G[y,x], B[y,x]))
