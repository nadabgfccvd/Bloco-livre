"""R13 forensic - PASS 7: streak full anatomy, star cell pixel diff, confetti positions, piece layout diff."""
import numpy as np
from PIL import Image
from scipy import ndimage

R12 = '/home/z/my-project/critic_shots/r12/'
R13 = '/home/z/my-project/critic_shots/r13/'
X0, X1, Y0, Y1, CELL = 24, 696, 190, 866, 84
STREAK_Y0, STREAK_Y1 = 1238, 1252

def arr(path):
    return np.asarray(Image.open(path).convert('RGB')).astype(np.float64)

def lum(a):
    return a.mean(axis=2)

# ---------- 1. STREAK FULL ANATOMY ----------
print("=" * 100)
print("1. STREAK ANATOMY (01_hero): x-profile every 8px + vertical anatomy at key x")
print("=" * 100)
a = arr(R13 + '01_hero.png')
strip = lum(a[STREAK_Y0:STREAK_Y1, X0:X1])
prof = strip.mean(axis=0)
print("x-profile (x, mean-lum over 14 rows):")
for x in range(0, 672, 8):
    seg = prof[x:x+8].mean()
    bar = '#' * int(seg / 4)
    print(f"  x={24+x:3d}: {seg:6.1f} {bar}")
print("\nfull-res profile x=110..130 and x=315..335 (fill edges):")
print(" ", np.round(prof[110:130], 1).tolist())
print(" ", np.round(prof[315:335], 1).tolist())
print("\nfull-res profile x=595..640 (ticks?):")
print(" ", np.round(prof[595:640], 1).tolist())
print("\nvertical (14 rows) at x=120, 200, 300, 318, 322, 620, 640, 660, 680, 690, 694:")
for x in [120, 200, 300, 318, 322, 620, 640, 660, 671, 680, 686]:
    xc = min(x, strip.shape[1] - 1)
    print(f"  x={24+xc}: {np.round(strip[:, xc], 1).tolist()}")

# ---------- 2. STAR CELL PIXEL DIFF r12 vs r13 ----------
print("\n" + "=" * 100)
print("2. STAR CELL DIFF (01_hero, cell (0,1): x24-108 y274-358)")
print("=" * 100)
a12, a13 = arr(R12 + '01_hero.png'), arr(R13 + '01_hero.png')
bx, by = X0 + 0 * CELL, Y0 + 1 * CELL
d = np.abs(a13[by:by+CELL, bx:bx+CELL] - a12[by:by+CELL, bx:bx+CELL]).max(axis=2)
print(f"max channel delta in star cell: {d.max():.1f}; px>10: {(d>10).sum()}; px>25: {(d>25).sum()}")
# where?
ys, xs = np.where(d > 10)
if len(ys):
    print(f"  changed px bbox: x[{bx+xs.min()},{bx+xs.max()}] y[{by+ys.min()},{by+ys.max()}]")
# also star in 02_skin0 cell(0,2), 06_full cell(2,0)
for shot, cell in [('02_skin0.png', (0, 2)), ('06_full.png', (2, 0))]:
    a12, a13 = arr(R12 + shot), arr(R13 + shot)
    bx, by = X0 + cell[0] * CELL, Y0 + cell[1] * CELL
    d = np.abs(a13[by:by+CELL, bx:bx+CELL] - a12[by:by+CELL, bx:bx+CELL]).max(axis=2)
    print(f"{shot} star cell {cell}: max delta={d.max():.1f} px>10: {(d>10).sum()} px>25: {(d>25).sum()}")

# ---------- 3. PIECE LAYOUT DIFF: per-cell signature ----------
print("\n" + "=" * 100)
print("3. PIECE LAYOUT r12 vs r13 (per-cell max delta, hero): which cells moved?")
print("=" * 100)
a12, a13 = arr(R12 + '01_hero.png'), arr(R13 + '01_hero.png')
grid = []
for gy in range(8):
    row = []
    for gx in range(8):
        bx, by = X0 + gx * CELL, Y0 + gy * CELL
        dd = np.abs(a13[by:by+CELL, bx:bx+CELL] - a12[by:by+CELL, bx:bx+CELL]).max()
        # content in r13?
        cellL = lum(a13[by:by+CELL, bx:bx+CELL])
        piece = 'P' if cellL.std() > 30 else '.'
        row.append(f"{piece}{int(min(dd,99)):02d}")
    grid.append(' '.join(row))
print("cell = [P if std>30 else .][maxdelta 00-99]:")
for r in grid:
    print('  ' + r)

# ---------- 4. CONFETTI POSITIONS (small blobs 3-60px, whole screen) ----------
print("\n" + "=" * 100)
print("4. CONFETTI small blobs (3-60px) positions r12 vs r13 (07_clear)")
print("=" * 100)
def confetti_census(path, tag):
    a = arr(path)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    # vivid: any strong hue dominance
    mx = a.max(axis=2); mn = a.min(axis=2)
    vivid = ((mx - mn) > 45) & (mx > 70)
    # exclude warm gold (pieces/star): r>g>b with r>170
    non_gold = ~((r > 170) & (g > 120) & (b < r - 40))
    m = vivid & non_gold
    lbl, n = ndimage.label(m)
    boxes = []
    if n:
        objs = ndimage.find_objects(lbl)
        for i, sl in enumerate(objs):
            size = int((lbl[sl] == i + 1).sum())
            if 3 <= size <= 60:
                cy = (sl[0].start + sl[0].stop) / 2
                cx = (sl[1].start + sl[1].stop) / 2
                col = a[sl][lbl[sl] == i + 1].mean(axis=0)
                boxes.append((size, int(cx), int(cy), col))
    print(f"{tag}: {len(boxes)} small vivid non-gold blobs (3-60px)")
    # summarize by hue
    def hue_name(c):
        r, g, b = c
        if b > r and b > g: return 'cyan/blue'
        if g > r and g > b: return 'green'
        if r > b > g or (r > g and b > g and r - g < 40): return 'pink/magenta'
        return 'other'
    from collections import Counter
    cnt = Counter(hue_name(bb[3]) for bb in boxes)
    print(f"   by hue: {dict(cnt)}")
    ys = [bb[2] for bb in boxes]
    xs = [bb[1] for bb in boxes]
    if ys:
        print(f"   y range {min(ys)}-{max(ys)}  x range {min(xs)}-{max(xs)}")
        # spatial spread: std of positions
        print(f"   pos std y={np.std(ys):6.1f} x={np.std(xs):6.1f}  (collapsed-at-origin bug would give ~0)")
    return boxes

confetti_census(R12 + '07_clear.png', 'r12')
confetti_census(R13 + '07_clear.png', 'r13')

# ---------- 5. 07_clear: what is the big pink thing? banner text? ----------
print("\n" + "=" * 100)
print("5. 07_clear content map: row-band luminance + big pink bbox")
print("=" * 100)
for tag, base in [('r12', R12), ('r13', R13)]:
    a = arr(base + '07_clear.png')
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    pink = (r > 110) & (b > 60) & (g < r - 25)
    big = pink.copy()
    lbl, n = ndimage.label(big)
    if n:
        sizes = ndimage.sum(big, lbl, range(1, n + 1))
        i = int(np.argmax(sizes)) + 1
        sl = ndimage.find_objects(lbl)[i - 1]
        print(f"{tag}: biggest pink blob {int(sizes[i-1])}px at y[{sl[0].start},{sl[0].stop}] x[{sl[1].start},{sl[1].stop}]")
    # board content: how many pieces remain?
    pieces = 0
    for gy in range(8):
        for gx in range(8):
            bx, by = X0 + gx * CELL, Y0 + gy * CELL
            if lum(a[by:by+CELL, bx:bx+CELL]).std() > 30:
                pieces += 1
    print(f"   cells with std>30 (pieces): {pieces}/64; board mean={lum(a[Y0:Y1, X0:X1]).mean():.1f}")
