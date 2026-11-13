#!/usr/bin/env python3
# Brutal-AACritic forensic pass on Bloco Livre R4 screenshots.
import numpy as np
from PIL import Image

D = '/home/z/my-project/critic_shots/r4/'

def load(name):
    im = Image.open(D + name).convert('RGB')
    return im, np.asarray(im).astype(np.int32)

def top_colors(a, k=6, q=8):
    flat = a.reshape(-1, 3)
    quant = (flat // q) * q
    colors, counts = np.unique(quant, axis=0, return_counts=True)
    idx = np.argsort(-counts)[:k]
    return [(tuple(int(x) for x in colors[i]), round(100.0 * counts[i] / len(quant), 1)) for i in idx]

def lum(a):
    return (0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2])

def stats(name):
    im, a = load(name)
    h, w, _ = a.shape
    sat = a.max(axis=2) - a.min(axis=2)
    l = lum(a)
    tc = top_colors(a)
    print(f"  {name}: {w}x{h} | uniq(exact)={len(np.unique(a.reshape(-1,3),axis=0))} | "
          f"meanRGB=({a[...,0].mean():.0f},{a[...,1].mean():.0f},{a[...,2].mean():.0f}) | "
          f"sat>40: {(sat>40).mean()*100:.1f}% | lum p5-p95: {np.percentile(l,5):.0f}-{np.percentile(l,95):.0f}")
    for c, p in tc:
        print(f"     #{c[0]:02X}{c[1]:02X}{c[2]:02X} {p}%")
    return a

print("=" * 72)
print("1) ALL SHOTS - palette / tonal fingerprint")
imgs = {}
for n in ['01_main_classic.png', '02_skin0.png', '03_skin1.png', '04_skin2.png',
          '05_skin3.png', '06_full.png', '07_clear.png']:
    imgs[n] = stats(n)

a01 = imgs['01_main_classic.png']; a06 = imgs['06_full.png']; a07 = imgs['07_clear.png']
H, W, _ = a01.shape

print("=" * 72)
print("2) DEAD BAND y1120-1288 (claimed: 49 uniq, 81% dominance, streak strip)")
for nm, a in [('01 calm', a01), ('06 full', a06), ('07 clear', a07)]:
    band = a[1120:1288]
    uq = np.unique(band.reshape(-1, 3), axis=0)
    flat = band.reshape(-1, 3)
    cq, cc = np.unique((flat // 8) * 8, axis=0, return_counts=True)
    dom = 100.0 * cc.max() / len(flat)
    # hue spread inside band (is it a flat strip or a real rendered streak strip)
    sat = band.max(axis=2) - band.min(axis=2)
    print(f"  {nm}: exact_uniq={len(uq)} dom_color={dom:.1f}% sat>30 rows: "
          f"{(sat > 30).mean() * 100:.1f}% | row-var of mean lum: {band.mean(axis=(0,2)).std():.1f}")

print("=" * 72)
print("3) DANGER TINT 06_full vs 01_calm (claimed 15.3/ch bg, wells #7A3038, red border)")
# background family = calm bg color(s) from 01 top-3 quantized
bgc = np.array([190, 198, 208])  # will refine: take most common quant color of 01 margins
flat = a01.reshape(-1, 3); cq, cc = np.unique((flat // 8) * 8, axis=0, return_counts=True)
bgc = cq[np.argmax(cc)].astype(int)
def bg_mask(a, c, tol=42):
    d = np.abs(a - c.reshape(1, 1, 3)).sum(axis=2)
    return d < tol
m1, m6 = bg_mask(a01, bgc), bg_mask(a06, bgc)
print(f"  bg ref #{bgc[0]:02X}{bgc[1]:02X}{bgc[2]:02X} | bg px calm={m1.mean()*100:.1f}% full={m6.mean()*100:.1f}%")
if m6.sum() > 500 and m1.sum() > 500:
    d = a06[m6].mean(axis=0) - a01[m1].mean(axis=0)
    print(f"  bg shift full vs calm: R{d[0]:+.1f} G{d[1]:+.1f} B{d[2]:+.1f} (mean/ch {np.abs(d).mean():.1f})")
# global channel drift on matched bg px
well = lambda a: ((a[...,0] > 70) & (a[...,0] < 160) & (a[...,1] < 80) & (a[...,2] < 90) &
                 (a[...,0] - a[...,1] > 35) & (a[...,1] - a[...,2] > -25))
print(f"  warm-dark 'well' px: calm={well(a01).sum()} full={well(a06).sum()} "
      f"({100*well(a06).sum()/max(1,well(a06).sum()+well(a01).sum()):.0f}% of all in full)")
for nm, a in [('calm', a01), ('full', a06)]:
    ring = np.concatenate([a[:26].reshape(-1,3), a[-26:].reshape(-1,3),
                           a[:, :26].reshape(-1,3), a[:, -26:].reshape(-1,3)])
    r = ring.mean(axis=0)
    print(f"  {nm} border mean #{r[0]:.0f},{r[1]:.0f},{r[2]:.0f} | red-bias(R-(G+B)/2)={r[0]-(r[1]+r[2])/2:.1f}")
# danger gradient: bottom vs top bg warmth in full
if m6.sum() > 500:
    ys = np.where(m6.any(axis=1))[0]
    print(f"  full bg rows span {ys.min()}-{ys.max()}; warm well rows span "
          f"{np.where(well(a06).any(axis=1))[0].min() if well(a06).any() else -1}-"
          f"{np.where(well(a06).any(axis=1))[0].max() if well(a06).any() else -1}")

print("=" * 72)
print("4) CELEBRATION 07_clear (confetti 4821 bright px, board-zone only, banner)")
gold = lambda a: (a[...,0] > 165) & (a[...,1] > 110) & (a[...,2] < 120) & (a[...,0] - a[...,2] > 60)
bright = lambda a: (a.max(axis=2) > 205) & (a.max(axis=2) - a.min(axis=2) > 55)
satpx = lambda a: (a.max(axis=2) - a.min(axis=2) > 60) & (a.max(axis=2) > 90)
bm, gm, sm = bright(a07), gold(a07), satpx(a07)
print(f"  bright confetti px={bm.sum()} gold px={gm.sum()} saturated px={sm.sum()}")
for nm, a in [('07 clear', a07), ('01 calm', a01)]:
    b = bright(a)
    if b.any():
        ys, xs = np.where(b)
        print(f"  {nm} bright bbox x{xs.min()}-{xs.max()} y{ys.min()}-{ys.max()}")
    # HUD leak: bright px in top HUD band
    print(f"     bright px in top 22% (HUD): {b[:int(H*0.22)].sum()} | mid: {b[int(H*0.22):int(H*0.75)].sum()} | bottom: {b[int(H*0.75):].sum()}")
# banner: dense bright cluster at board centre
cy, cx = int(H * 0.5), int(W * 0.5)
reg = bm[cy-160:cy+160, cx-260:cx+260]
ctrl = bm[int(H*0.75):int(H*0.75)+320, :W//2]
print(f"  banner-zone bright density {100*reg.mean():.2f}% vs ctrl {100*ctrl.mean() if ctrl.size else 0:.2f}%")
# is board empty in the still?
blk = lambda a: (a.max(axis=2) - a.min(axis=2) > 45) & (a.max(axis=2) > 70)
print(f"  block-ish px inside board area: calm={blk(a01)[300:1100, :].sum()} clear={blk(a07)[300:1100, :].sum()}")
print(f"  gold at board edges (ring 36px inside board bbox x): "
      f"{gold(a07)[400:1080, 36:W-36][:, :36].sum() + gold(a07)[400:1080, 36:W-36][:, -36:].sum()} px")

print("=" * 72)
print("5) NUMERAL HIERARCHY (PONTOS/RECORDE 0.52*cell matched)")
for nm, a in [('01', a01), ('06', a06)]:
    top = a[:400]
    l = lum(top)
    thr = l.max() - 90
    rows = (l > thr).sum(axis=1)
    on = rows > 8
    bands, y = [], 0
    while y < len(on):
        if on[y]:
            y0 = y
            while y < len(on) and on[y]:
                y += 1
            bands.append((y0, y))
        else:
            y += 1
    hs = [b[1] - b[0] for b in bands]
    print(f"  {nm} HUD text bands y{[b for b in bands]} heights={hs}")

print("=" * 72)
print("6) AO / NEIGHBOR-DEPENDENT TOP SHADOW (0x8C vs 0x3D -> 2.3x)")
sat01 = a01.max(axis=2) - a01.min(axis=2)
block = (sat01 > 45) & (a01.max(axis=2) > 70)
sub = block[:, :, ] if False else block[:1120]  # board zone above dead band
occ_l, open_l = [], []
for x in range(0, W, 3):
    col = sub[:, x]
    ys = np.where(col)[0]
    if len(ys) < 5:
        continue
    runs = []
    start = ys[0]
    for i in range(1, len(ys)):
        if ys[i] != ys[i - 1] + 1:
            runs.append((start, ys[i - 1])); start = ys[i]
    runs.append((start, ys[-1]))
    for i, (s, e) in enumerate(runs):
        top4 = lum(a01[s:s + 4, x]).mean()
        stacked = i > 0 and (s - runs[i - 1][1]) <= 8
        (occ_l if stacked else open_l).append(top4)
    # bottom-of-block shadow: rows just below a run end
if occ_l and open_l:
    print(f"  top-of-block lum: stacked-above={np.mean(occ_l):.1f} open-above={np.mean(open_l):.1f} "
          f"ratio={np.mean(open_l) / np.mean(occ_l):.2f}x (expect ~2.3x), n={len(occ_l)}/{len(open_l)}")
else:
    print("  AO: insufficient run data")

print("=" * 72)
print("7) SKIN CHECKS (pixel gray #4A4E58 hue-neutral; tray clip)")
a05 = imgs['05_skin3.png']
flat = a05.reshape(-1, 3); cq, cc = np.unique((flat // 8) * 8, axis=0, return_counts=True)
g = cq[np.argmax(cc)].astype(int)
print(f"  05_pixel dominant #{g[0]:02X}{g[1]:02X}{g[2]:02X} hue-spread(ch max-min)={g.max()-g.min()} "
      f"(claim #4A4E58, spread 14)")
for nm in ['02_skin0.png', '03_skin1.png', '04_skin2.png', '05_skin3.png']:
    a = imgs[nm]
    sat = a.max(axis=2) - a.min(axis=2)
    hsv_h = (np.arctan2(1.732 * (a[...,1]-a[...,2]), 2*a[...,0]-a[...,1]-a[...,2]) + np.pi) / (2 * np.pi)
    hs = hsv_h[sat > 60]
    if len(hs) > 100:
        hist, _ = np.histogram(hs, bins=12, range=(0, 1))
        print(f"  {nm}: sat>60 {100*(sat>60).mean():.1f}% | hue hist {list(hist)}")
    else:
        print(f"  {nm}: sat>60 {100*(sat>60).mean():.1f}% (near-achromatic skin)")

print("=" * 72)
print("8) MACRO AESTHETIC PROXIES")
for nm, a in imgs.items():
    l = lum(a)
    gx = np.abs(np.diff(l, axis=1)).mean(); gy = np.abs(np.diff(l, axis=0)).mean()
    print(f"  {nm}: edge-energy {gx + gy:.2f} | tonal-range p1-p99 {np.percentile(l,1):.0f}-{np.percentile(l,99):.0f}")
