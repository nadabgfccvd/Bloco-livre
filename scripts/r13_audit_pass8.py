"""R13 forensic - PASS 8: header/tray star diff, micro-line geometry, ticks, confetti bimodal."""
import numpy as np
from PIL import Image
from scipy import ndimage

R12 = '/home/z/my-project/critic_shots/r12/'
R13 = '/home/z/my-project/critic_shots/r13/'
X0, X1, Y0, Y1, CELL = 24, 696, 190, 866, 84

def arr(path):
    return np.asarray(Image.open(path).convert('RGB')).astype(np.float64)

def lum(a):
    return a.mean(axis=2)

# ---------- 1. HEADER STAR diff (x559-674 y123-169) ----------
print("=" * 100)
print("1. HEADER STAR ZONE diff r12 vs r13 (all shots)")
print("=" * 100)
for shot in ['01_hero.png','02_skin0.png','03_skin1.png','04_skin2.png','05_skin3.png','06_full.png','07_clear.png']:
    a12, a13 = arr(R12 + shot), arr(R13 + shot)
    zone12 = a12[123:170, 559:675]; zone13 = a13[123:170, 559:675]
    d = np.abs(zone13 - zone12).max()
    print(f"{shot}: header-star zone max delta={d:.1f}")

# tray star (next preview) — search tray area for warm blob
print("\n  tray warm blobs (r13 vs r12):")
for shot in ['01_hero.png','02_skin0.png']:
    for tag, base in [('r12', R12), ('r13', R13)]:
        a = arr(base + shot)
        z = a[860:1142, 24:696]
        r, g, b = z[..., 0], z[..., 1], z[..., 2]
        warm = ((r > 150) & (r > b + 50) & (g > 100) & (g < r))
        lbl, n = ndimage.label(warm)
        if n:
            sizes = ndimage.sum(warm, lbl, range(1, n + 1))
            big = sizes[sizes > 50]
            print(f"   {shot} {tag}: {len(big)} warm blobs>50px sizes={sorted(big.astype(int).tolist())[:8]}")
        else:
            print(f"   {shot} {tag}: none")

# ---------- 2. MICRO-TEXTURE LINE GEOMETRY (fit lines on delta>4 px) ----------
print("\n" + "=" * 100)
print("2. MICRO-LINE GEOMETRY per empty well (01_hero): fit slope to changed px")
print("=" * 100)
a12, a13 = arr(R12 + '01_hero.png'), arr(R13 + '01_hero.png')
count_lines = 0
wells_with = 0
angles = []
for gy in range(8):
    for gx in range(8):
        bx, by = X0 + gx * CELL, Y0 + gy * CELL
        dl = lum(a13[by:by+CELL, bx:bx+CELL]) - lum(a12[by:by+CELL, bx:bx+CELL])
        m = dl > 4
        npx = m.sum()
        if npx < 30:
            continue
        wells_with += 1
        ys, xs = np.where(m)
        # fit line via PCA on the points
        pts = np.stack([xs, ys]).astype(float)
        c = pts.mean(axis=1)
        u, s, vt = np.linalg.svd(pts - c[:, None], full_matrices=False)
        direction = vt[0]
        angle = np.degrees(np.arctan2(direction[1], direction[0])) % 180
        # residual: line thinness
        resid = np.abs((pts - c[:, None])[0] * direction[1] - (pts - c[:, None])[1] * direction[0]).mean()
        angles.append(angle)
        if count_lines < 6:
            print(f"  well({gx},{gy}): {npx}px changed>4 | PCA line angle={angle:6.1f} deg | resid={resid:5.2f} | bbox x[{xs.min()},{xs.max()}] y[{ys.min()},{ys.max()}]")
            count_lines += 1
print(f"  wells with >30 changed px: {wells_with}/64; angle histogram: {np.histogram(angles, bins=[0,20,45,70,90,110,135,160,181])[0].tolist()} (deg bins)")

# ---------- 3. STREAK TICKS precise ----------
print("\n" + "=" * 100)
print("3. STREAK TICKS (01_hero): tick x-positions and widths on track (x352-596) and on fill")
print("=" * 100)
a = arr(R13 + '01_hero.png')
strip = lum(a[1238:1252, 24:696])
prof = strip.mean(axis=0)
# on dark track x=352..596: bumps above 26
tickzone = prof[352 - 24:596 - 24]
above = tickzone > 26
runs = []
inr = False
for i, v in enumerate(above):
    if v and not inr: st = i; inr = True
    elif not v and inr: runs.append((st + 352, i + 352, (tickzone[st:i]).max())); inr = False
if inr: runs.append((st + 352, len(above) + 352, tickzone[st:].max()))
print(f"  ticks on track x[352,596]: {len(runs)} runs: {[(r[0], r[1], round(r[2],1)) for r in runs]}")
# on fill x136..342: dips below 155
fillzone = prof[136 - 24:342 - 24]
below = fillzone < 150
runs2 = []
inr = False
for i, v in enumerate(below):
    if v and not inr: st = i; inr = True
    elif not v and inr: runs2.append((st + 136, i + 136, fillzone[st:i].min())); inr = False
if inr: runs2.append((st + 136, len(fillzone) + 136, fillzone[st:].min()))
print(f"  dips on fill x[136,342]: {len(runs2)}: {[(r[0], r[1], round(r[2],1)) for r in runs2]}")
# right zone x600-696 (label?)
rightzone = prof[600 - 24:672]
print(f"  right zone x[600,696] mean={rightzone.mean():.1f} max={rightzone.max():.1f} (label/LED?)")

# what is at rows 6-13 x640-696? (text?)
sub = a[1244:1252, 600:696]
r, g, b = sub[..., 0], sub[..., 1], sub[..., 2]
print(f"  right-zone colors: unique={len(np.unique((sub//8).astype(int).reshape(-1,3), axis=0))}, mean rgb={sub.reshape(-1,3).mean(axis=0).round(1)}")

# ---------- 4. CONFETTI bimodal sizes + aspect (rotation variety) ----------
print("\n" + "=" * 100)
print("4. CONFETTI bimodal size + aspect ratio (07_clear, whole screen, vivid non-gold 3-60px)")
print("=" * 100)
def census(path, tag):
    a = arr(path)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx = a.max(axis=2); mn = a.min(axis=2)
    vivid = ((mx - mn) > 45) & (mx > 70)
    non_gold = ~((r > 170) & (g > 120) & (b < r - 40))
    m = vivid & non_gold
    lbl, n = ndimage.label(m)
    items = []
    if n:
        objs = ndimage.find_objects(lbl)
        for i, sl in enumerate(objs):
            size = int((lbl[sl] == i + 1).sum())
            if 3 <= size <= 60:
                h = sl[0].stop - sl[0].start; w = sl[1].stop - sl[1].start
                items.append((size, w, h))
    sizes = [it[0] for it in items]
    small = [s for s in sizes if s <= 8]
    big = [s for s in sizes if 9 <= s <= 20]
    huge = [s for s in sizes if s > 20]
    ar = [max(it[1], it[2]) / max(1, min(it[1], it[2])) for it in items]
    print(f"{tag}: items={len(items)} | small(3-8)={len(small)} big(9-20)={len(big)} >20={len(huge)}")
    print(f"   aspect ratio: med={np.median(ar):.2f} p90={np.percentile(ar,90):.2f} | elongated>1.6: {sum(1 for x in ar if x>1.6)}/{len(ar)}")
    return items

census(R12 + '07_clear.png', 'r12')
census(R13 + '07_clear.png', 'r13')

# ---------- 5. STAR bottom vs well band (does spike kiss band?) ----------
print("\n" + "=" * 100)
print("5. STAR-to-BAND clearance (r13 hero cell (0,1)): star bottom row vs well bottom rim")
print("=" * 100)
a = arr(R13 + '01_hero.png')
bx, by = X0, Y0 + CELL
cell = a[by:by+CELL, bx:bx+CELL]
L = lum(cell)
r, g, b = cell[..., 0], cell[..., 1], cell[..., 2]
warm_col = ((r > 150) & (r > b + 50) & (g > 100) & (g < r))
rowfrac = warm_col.mean(axis=1)
star_rows = np.where(rowfrac > 0.15)[0]
print(f"  star rows {star_rows.min()}-{star_rows.max()}")
# find bottom rim: bright band rows near bottom of well
for row in range(60, 84):
    print(f"   row {row}: lum={L[row].mean():6.1f} warmfrac={rowfrac[row]:.3f}", end='')
    if row % 2 == 1: print()
print()
# vertical profile column at star center
cidx = int(np.where(warm_col.any(axis=0))[0].mean())
print(f"  star center col ~{cidx}; vertical lum at that col rows 55-84: {np.round(L[55:84, cidx], 1).tolist()}")
