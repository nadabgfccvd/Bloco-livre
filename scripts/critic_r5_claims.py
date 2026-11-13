#!/usr/bin/env python3
"""R5 forensics part 3: per-claim measurement suite.

Board geometry (measured from edge scans): board x in [185, 608], y in [280, 1120]
approx on classic shots; cell_w=42.5, cell_h=49.5. HUD occupies y<185.
All numbers printed for the art-director audit.
"""
import os
import numpy as np
from PIL import Image

SHOTS = '/home/z/my-project/critic_shots/r5'
CROPS = '/tmp/critic_crops_r5'
os.makedirs(CROPS, exist_ok=True)

def load(n): return Image.open(os.path.join(SHOTS, n)).convert('RGB')
def arr(n): return np.asarray(load(n), dtype=np.int16)

# Board geometry measured earlier on 02_skin0:
BX0, BX1 = 186, 608      # left rail to right rail
CELL_W = (BX1 - BX0) / 10.0
# vertical: find precise top/bottom from long rail rows
def board_ybounds(a):
    # board side rails are at x 186 and 608; use column at x=186 to find run
    col = a[:, 186]
    d = np.abs(np.diff(col.astype(np.int32), axis=0))
    return col, d

# ---------------------------------------------------------------- utilities
def rgb_pct(a, mask):
    n = int(mask.sum())
    if n == 0: return None, 0
    m = a[mask]
    return (round(m[:,0].mean(),1), round(m[:,1].mean(),1), round(m[:,2].mean(),1)), n

def sat_non_gold(a, y_limit=185):
    """claim 3: saturated non-gold pixels in the HUD strip y<y_limit."""
    r, g, b = a[...,0].astype(np.int16), a[...,1].astype(np.int16), a[...,2].astype(np.int16)
    mx = np.maximum(np.maximum(r,g),b); mn = np.minimum(np.minimum(r,g),b)
    sat = mx - mn
    satmask = (sat > 60) & (mx > 90)
    gold = (r > 150) & (g > 100) & (b < 140) & (r >= g + 30) & (g > b)
    hud = np.zeros(satmask.shape, bool); hud[:y_limit, :] = True
    non_gold_hud = satmask & ~gold & hud
    return int(non_gold_hud.sum()), int(satmask[:y_limit].sum()), int(gold[:y_limit].sum())

# ---------------------------------------------------------------- CLAIM 4: numeral sizes in HUD
def measure_hud_numerals(name):
    a = arr(name)
    # HUD text zone: find bright text pixels (luma > 140) in y<200
    lum = a.mean(axis=2)
    txt = (lum > 150)
    ys, xs = np.nonzero(txt)
    if len(ys) == 0: print(name, 'no bright text'); return
    # cluster rows into lines
    order = np.argsort(ys)
    ys_s = ys[order]; xs_s = xs[order]
    lines = []
    cur = [ys_s[0]]
    for y in ys_s[1:]:
        if y - cur[-1] <= 2: cur.append(y)
        else:
            lines.append((cur[0], cur[-1])); cur = [y]
    lines.append((cur[0], cur[-1]))
    print(f'--- {name} bright text lines (y0,y1,h) x-extent:')
    for (y0, y1) in lines:
        if y1 - y0 < 2: continue
        m = txt[y0:y1+1]
        xs2 = np.nonzero(m.any(axis=0))[0]
        print(f'    y {y0}-{y1} h={y1-y0+1} x {xs2.min()}..{xs2.max()}')

# ---------------------------------------------------------------- CLAIM 1: payoff frame
def claim1():
    a = arr('07_clear.png')
    lum = a.mean(axis=2)
    # board zone empty-well check: fraction of board area that matches well bg
    board = a[335:1075, 186:609]
    # cluster board colors: count distinct near-uniform colors
    from collections import Counter
    small = board[::7, ::7].reshape(-1, 3)
    cnt = Counter(map(tuple, small.tolist()))
    top = cnt.most_common(8)
    tot = sum(cnt.values())
    print('--- CLAIM1 board top colors (rgb, share):')
    for c, n in top:
        print(f'    {c}  {100*n/tot:.1f}%')
    # banner: find the big bright band across board center
    rows = board.mean(axis=(1,2))
    bright_rows = np.nonzero(rows > rows.mean() + 30)[0]
    print('    board bright rows (banner):',
          (335+bright_rows.min(), 335+bright_rows.max()) if len(bright_rows) else None)
    # gold stars ring: gold pixels OUTSIDE the board rails
    r, g, b = a[...,0].astype(np.int16), a[...,1].astype(np.int16), a[...,2].astype(np.int16)
    gold = (r>170)&(g>110)&(b<120)&(r>=g+40)&(g>b+20)&(r<250)
    ys, xs = np.nonzero(gold)
    outside = (xs < 186) | (xs > 609)
    print(f'    gold px total={gold.sum()} outside-board={int(outside.sum())}')
    if outside.sum():
        # cluster outside-gold blobs by connected-ish bins
        oy = ys[outside]; ox = xs[outside]
        hist, edges = np.histogram(oy, bins=24, range=(0,1440))
        print('    outside-gold rows histogram (24 bins):', hist.tolist())
        # angular positions around board center
        cy, cx = 705, 397
        ang = np.degrees(np.arctan2(oy - cy, ox - cx)) % 360
        h2, _ = np.histogram(ang, bins=12, range=(0,360))
        print('    outside-gold 12-sector angular histogram:', h2.tolist())

# ---------------------------------------------------------------- CLAIM 2: danger
def claim2():
    calm = arr('01_main_classic.png')
    danger = arr('06_full.png')
    # background = pixels outside board & panels: sample corners + margins
    def bg_stats(a, tag):
        samples = np.concatenate([a[0:120, 0:120].reshape(-1,3), a[0:120, 600:720].reshape(-1,3),
                                 a[1300:1440, 0:120].reshape(-1,3), a[1300:1440, 600:720].reshape(-1,3),
                                 a[600:900, 0:80].reshape(-1,3), a[600:900, 640:720].reshape(-1,3)])
        m = samples.mean(axis=0)
        print(f'    {tag} bg mean RGB = {m.round(1).tolist()}')
        return m
    m1 = bg_stats(calm, 'calm(01)')
    m2 = bg_stats(danger, 'danger(06)')
    d = m2 - m1
    print('    danger-calm delta per channel:', d.round(1).tolist(),
          'R-dominant:', bool(d[0] >= d[1] and d[0] >= d[2]))
    # also compare same-calm-frame vs full frame wells
    well_calm = calm[400:1000, 200:600][ (calm[400:1000, 200:600].mean(axis=2) < 90) ]
    well_dang = danger[400:1000, 200:600][ (danger[400:1000, 200:600].mean(axis=2) < 90) ]
    print('    dark-zone means calm vs danger:',
          well_calm.mean(axis=0).round(1).tolist(), well_dang.mean(axis=0).round(1).tolist())

# ---------------------------------------------------------------- CLAIM 6: tonal range of skin
def claim6():
    for name, tag in [('02_skin0.png','classico'), ('03_skin1.png','neon'),
                      ('04_skin2.png','gema'), ('05_skin3.png','pixel')]:
        a = arr(name)
        board = a[335:1075, 186:609]
        lum = board.mean(axis=2)
        p1, p50, p99 = np.percentile(lum, [1, 50, 99])
        # gloss: brightest interior pixels
        hi = board[lum > 200]
        print(f'--- {tag}: board lum p1={p1:.0f} p50={p50:.0f} p99={p99:.0f} '
              f'hi-px mean RGB={hi.mean(axis=0).round(0).tolist() if len(hi) else "none"} n={len(hi)}')
        # block body vs shadow: take a colored block color and look at its dark edge
        r, g, b = board[...,0].astype(np.int16), board[...,1].astype(np.int16), board[...,2].astype(np.int16)
        colmask = (board.max(axis=2) - board.min(axis=2)) > 60
        if colmask.sum() > 50:
            cm = board[colmask]
            # darkest decile of colored-block pixels approximates shadow dim
            l = cm.mean(axis=1)
            order = np.argsort(l)
            dark = cm[order[:max(1, len(order)//10)]]
            mid = cm[order[len(order)//2-1:len(order)//2+1]]
            print(f'    colored-block shadow decile RGB={dark.mean(axis=0).round(0).tolist()} '
                  f'mid RGB={mid.mean(axis=0).round(0).tolist()} '
                  f'ratio={(dark.mean()/np.maximum(mid.mean(),1)).round(2).tolist()}')

# ---------------------------------------------------------------- CLAIM 5: AO under blocks
def claim5():
    for name in ['02_skin0.png', '01_main_classic.png']:
        a = arr(name)
        # AO appears as darkened wells directly BELOW occupied cells.
        # Detect: rows below first occupied row in each column darker than well average
        board = a[335:1075, 186:609].astype(np.float32)
        lum = board.mean(axis=2)
        well_bg = np.median(lum)
        # find occupied: bright-ish or colored cells
        r,g,b = board[...,0], board[...,1], board[...,2]
        colored = (board.max(axis=2) - board.min(axis=2)) > 50
        bright = lum > 80
        occupied = colored | bright
        colocc = occupied.any(axis=0)
        # For each occupied column, look at rows directly under the lowest occupied cell
        depths = []
        for c in range(occupied.shape[1]):
            if not colocc[c]: continue
            rows = np.nonzero(occupied[:, c])[0]
            low = rows.max()
            if low + 3 < occupied.shape[0]:
                strip = lum[low+2:low+8, c]
                depths.append(float(np.mean(strip)))
        if depths:
            print(f'--- {name}: under-block strip mean lum={np.mean(depths):.1f} '
                  f'well-median={well_bg:.1f} delta={np.mean(depths)-well_bg:.1f} '
                  f'AO depth px ~= {(np.mean(depths)-well_bs if False else 0)}')
        # AO vertical extent: measure how far the darkening persists below blocks
        # take one clearly occupied region bottom row
        occ_rows = np.nonzero(occupied.any(axis=1))[0]
        if len(occ_rows):
            bottom = occ_rows.max()
            strip = lum[bottom:bottom+15, :]
            strip_bg = np.median(strip)
            print(f'    bottom occ row={bottom} (y={335+bottom}); lum profile next 15 rows:',
                  strip.mean(axis=1).round(1).tolist())
well_bs = None

# ---------------------------------------------------------------- run all
if __name__ == '__main__':
    print('================ CLAIM 1 ================')
    claim1()
    print('================ CLAIM 2 ================')
    claim2()
    print('================ CLAIM 6 ================')
    claim6()
    print('================ CLAIM 5 ================')
    claim5()
    print('================ CLAIM 3 ================')
    for n in ['01_main_classic.png','02_skin0.png','03_skin1.png','04_skin2.png','05_skin3.png','06_full.png','07_clear.png']:
        ng, tot, gold = sat_non_gold(arr(n))
        print(f'--- {n}: sat non-gold px in y<185 = {ng} (total sat={tot}, gold={gold})')
    print('================ CLAIM 4 ================')
    measure_hud_numerals('01_main_classic.png')
