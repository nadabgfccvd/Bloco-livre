#!/usr/bin/env python3
"""R12 forensics part A: spoke widths, star/band geometry, hero tray diff vs r11."""
from PIL import Image
import numpy as np

R12 = '/home/z/my-project/critic_shots/r12/'
R11 = '/home/z/my-project/critic_shots/r11/'

def load(p):
    return np.asarray(Image.open(p).convert('RGB')).astype(int)

# ---------- HERO: spoke width scan in 07_clear (burst lives there per claim 4) ----------
burst_center = (360, 323)  # burst center given
cell = 84
r_scan = 1.05 * cell  # ~88.2 px from center

im = load(R12 + '07_clear.png')
H, W, _ = im.shape
lum = im.mean(axis=2)

# Spokes radiate from (360,323). At radius r, sample along the circle: for each angle,
# find angular extent of bright spoke pixels -> chord = angle_extent * r
def spoke_scan(im, center, radius, bright=140):
    lum = im.mean(axis=2)
    cx, cy = center
    angles = np.linspace(0, 2*np.pi, 2880, endpoint=False)
    hits = []
    for a in angles:
        x = int(round(cx + radius*np.cos(a)))
        y = int(round(cy + radius*np.sin(a)))
        if 0 <= x < lum.shape[1] and 0 <= y < lum.shape[0]:
            # 3px radial thickness max sample: take max over +/-2 px radially
            vals = []
            for d in (-2,-1,0,1,2):
                xx = int(round(cx + (radius+d)*np.cos(a)))
                yy = int(round(cy + (radius+d)*np.sin(a)))
                if 0 <= xx < lum.shape[1] and 0 <= yy < lum.shape[0]:
                    vals.append(lum[yy, xx])
            hits.append(np.max(vals) if vals else 0)
        else:
            hits.append(0)
    hits = np.array(hits)
    on = hits > bright
    # find contiguous angular runs
    runs = []
    n = len(on)
    i = 0
    while i < n:
        if on[i]:
            j = i
            while j < n and on[j]:
                j += 1
            # wrap merge
            runs.append((i, j))
            i = j
        else:
            i += 1
    # merge wrap-around
    if len(runs) > 1 and runs[0][0] == 0 and runs[-1][1] == n:
        runs[-1] = (runs[-1][0], runs[-1][1] + runs[0][1])
        runs = runs[1:]
    chords = []
    for (a, b) in runs:
        ang_extent = (b - a) / n * 2 * np.pi
        chord = ang_extent * radius
        chords.append(round(chord, 1))
    return chords, hits

for name, center in [('07_clear', (360,323))]:
    for rr, label in [(1.05*cell, 'r=1.05cell'), (1.15*cell, 'r=1.15cell')]:
        chords, _ = spoke_scan(load(R12+name+'.png'), center, rr)
        print(f"[{name}] spoke chords @ {label} (r={rr:.1f}): {chords}")
        print(f"   count={len(chords)} mean={np.mean(chords) if chords else 0:.1f} max={max(chords) if chords else 0}")

# Also scan hero for any burst (claim: hero unchanged, no burst)
im_h = load(R12+'01_hero.png')
region = im_h[190:870, 24:700].mean(axis=2)
print("hero board max lum:", region.max(), "mean:", region.mean())

# ---------- STAR / BAND geometry in hero ----------
im = load(R12 + '01_hero.png')
lum = im.mean(axis=2)
# star column scan near x 300-420, rows 200-380
col = 360
print("\n--- HERO vertical profile x=360, y=195..380 (lum every 2px) ---")
prof = [(y, round(lum[y, col],1)) for y in range(195, 381, 2)]
print(prof)

# Star body extent: rows where luminance distinctly above local bg in x 290..430
sub = lum[230:360, 280:440]
rows_above = [230+i for i in range(sub.shape[0]) if sub[i].max() > 120]
print("\nstar-ish rows with any bright px (x280-440):", rows_above[0] if rows_above else None, "->", rows_above[-1] if rows_above else None)

# Band top: the band runs across full width; find row band y350-420
print("\n--- HERO column profile x=100 and x=620, y=340..380 ---")
for xc in (100, 620):
    prof = [(y, round(lum[y, xc],1)) for y in range(340, 381, 2)]
    print(f"x={xc}:", prof)

# Band top detection: full-width bright row
bandtop = None
for y in range(300, 420):
    row = lum[y, 40:680]
    if np.percentile(row, 90) > 120:
        bandtop = y; break
print("\nband top (first full-width bright row):", bandtop)

# Star lowest bright pixel (body) above band - measure gap
if rows_above and bandtop:
    gap = bandtop - rows_above[-1]
    print("star bottom row:", rows_above[-1], "band top:", bandtop, "GAP:", gap, "px")

# Star horizontal extent at its widest row
if rows_above:
    ymid = (rows_above[0]+rows_above[-1])//2
    r = lum[ymid, 200:520]
    xs = [200+i for i in range(len(r)) if r[i] > 120]
    print("star widest row", ymid, "x extent:", xs[0] if xs else None, "->", xs[-1] if xs else None, "width:", (xs[-1]-xs[0]) if xs else 0)

# ---------- Claim 3: tray gradient in ALL 7 shots (diff vs r11) ----------
print("\n--- TRAY GRADIENT: r12 - r11, rows 850..900, x 40..680 ---")
names = ['01_hero','02_skin0','03_skin1','04_skin2','05_skin3','06_full','07_clear']
for nm in names:
    a = load(R11 + nm + '.png')
    b = load(R12 + nm + '.png')
    if a.shape != b.shape:
        print(nm, "shape mismatch"); continue
    da = np.abs(a - b).mean(axis=2)
    rows = da[:, 40:680]
    prof = [(y, round(rows[y].mean(),2)) for y in range(850, 901, 5)]
    # extent: rows where mean diff > 2
    ext = [y for y in range(840, 960) if rows[y].mean() > 2]
    print(f"{nm}: diff-rows>{2}: {ext[0] if ext else None}..{ext[-1] if ext else None}  peak={rows[850:900].max():.1f}")
    print("   profile:", prof)
    # total changed pixels anywhere else (outside tray region)
    other = da.copy()
    other[840:960, :] = 0
    ys, xs = np.where(other > 6)
    if len(ys):
        print(f"   other-changed pixels: {len(ys)} rows {ys.min()}..{ys.max()} (maxdiff {other.max():.1f})")
    else:
        print("   other-changed pixels: 0 (board identical)")

# ---------- Claim 4: hero board pixel-identical to r11 ----------
a = load(R11 + '01_hero.png'); b = load(R12 + '01_hero.png')
d = np.abs(a-b).mean(axis=2)
print("\nhero total diff: mean", round(d.mean(),4), "max", round(d.max(),1))
board = d[0:840, :]
print("hero rows 0-840 diff: max", round(board.max(),2), "changed(>6):", int((board>6).sum()))
tray = d[840:1440, :]
print("hero rows 840+ diff: max", round(tray.max(),2), "changed(>6):", int((tray>6).sum()))
