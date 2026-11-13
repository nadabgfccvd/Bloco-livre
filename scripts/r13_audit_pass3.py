"""R13 forensic - PASS 3: precise star, changed-wells (vignette+texture), confetti, streak anatomy."""
import numpy as np
from PIL import Image

R12 = '/home/z/my-project/critic_shots/r12/'
R13 = '/home/z/my-project/critic_shots/r13/'
SHOTS = ['01_hero.png','02_skin0.png','03_skin1.png','04_skin2.png','05_skin3.png','06_full.png','07_clear.png']
X0, X1, Y0, Y1, CELL = 24, 696, 190, 866, 84
STREAK_Y0, STREAK_Y1 = 1238, 1252

def arr(path):
    return np.asarray(Image.open(path).convert('RGB')).astype(np.float64)

def lum(a):
    return a.mean(axis=2)

# ---------- 1. CHANGED WELLS (r12->r13): which cells changed = empty bg wells ----------
print("=" * 100)
print("1. CHANGED WELLS r12->r13 (empty wells got vignette + micro-texture)")
print("=" * 100)
for shot in SHOTS[:6]:
    a12, a13 = arr(R12 + shot), arr(R13 + shot)
    changed = []
    emptystds13, emptystds12 = [], []
    for gy in range(8):
        for gx in range(8):
            bx, by = X0 + gx * CELL, Y0 + gy * CELL
            d = np.abs(a13[by:by+CELL, bx:bx+CELL] - a12[by:by+CELL, bx:bx+CELL]).max()
            if d > 10:
                changed.append((gx, gy, d))
                emptystds13.append(lum(a13[by+4:by+80, bx+4:bx+80]).std())
                emptystds12.append(lum(a12[by+4:by+80, bx+4:bx+80]).std())
    if emptystds13:
        print(f"{shot}: {len(changed)}/64 wells changed | empty-well std r12={np.mean(emptystds12):5.2f} r13={np.mean(emptystds13):5.2f} "
              f"(n={len(emptystds13)}) | max delta={max(c[2] for c in changed):.0f}")
    else:
        print(f"{shot}: 0 wells changed (board fully covered or identical)")

# ---------- 2. DIAGONAL MICRO-LINES in a confirmed empty well ----------
print("\n" + "=" * 100)
print("2. MICRO-TEXTURE: diagonal lines in confirmed empty wells")
print("=" * 100)
a12, a13 = arr(R12 + '01_hero.png'), arr(R13 + '01_hero.png')
found = 0
for gy in range(8):
    for gx in range(8):
        bx, by = X0 + gx * CELL, Y0 + gy * CELL
        d = np.abs(a13[by:by+CELL, bx:bx+CELL] - a12[by:by+CELL, bx:bx+CELL]).max()
        if d > 10 and found < 3:
            found += 1
            w13 = lum(a13[by+4:by+80, bx+4:bx+80])
            w12 = lum(a12[by+4:by+80, bx+4:bx+80])
            delta = w13 - w12
            # diagonal line detection: along each anti-diagonal band, find runs above median
            med = np.median(delta)
            hi = delta > med + 3
            # a diagonal line (going down-right) => constant (x-y); check diag sums
            diag_hits = {}
            H, W = delta.shape
            for off in range(-H + 1, W):
                vals = [hi[i, i - off] for i in range(max(0, off), min(H, W + off)) if 0 <= i - off < W]
                if vals and sum(vals) > len(vals) * 0.35 and len(vals) > 8:
                    diag_hits[off] = sum(vals)
            # anti-diagonal (down-left): constant (x+y)
            anti_hits = {}
            for s in range(H + W):
                vals = [hi[i, s - i] for i in range(max(0, s - W + 1), min(H, s + 1))]
                if vals and sum(vals) > len(vals) * 0.35 and len(vals) > 8:
                    anti_hits[s] = sum(vals)
            print(f"well({gx},{gy}) delta mean={delta.mean():5.2f} max={delta.max():5.1f} "
                  f"diag-lines={len(diag_hits)} (offs {list(diag_hits)[:6]}) antidiag-lines={len(anti_hits)} (sums {list(anti_hits)[:6]})")

# ---------- 3. VIGNETTE on empty wells only ----------
print("\n" + "=" * 100)
print("3. VIGNETTE: empty-well luminance by position (r13 vs r12), 01_hero")
print("=" * 100)
for shot in ['01_hero.png', '03_skin1.png']:
    a12, a13 = arr(R12 + shot), arr(R13 + shot)
    grid = np.zeros((8, 8)); grid12 = np.zeros((8, 8)); mask = np.zeros((8, 8), bool)
    for gy in range(8):
        for gx in range(8):
            bx, by = X0 + gx * CELL, Y0 + gy * CELL
            d = np.abs(a13[by:by+CELL, bx:bx+CELL] - a12[by:by+CELL, bx:bx+CELL]).max()
            if d > 10:
                grid[gy, gx] = lum(a13[by+8:by+CELL-8, bx+8:bx+CELL-8]).mean()
                grid12[gy, gx] = lum(a12[by+8:by+CELL-8, bx+8:bx+CELL-8]).mean()
                mask[gy, gx] = True
    corner = [grid[0, 0], grid[0, 7], grid[7, 0], grid[7, 7]]
    corner12 = [grid12[0, 0], grid12[0, 7], grid12[7, 0], grid12[7, 7]]
    c12 = grid[0:2, 0:2].mean(); mid = grid[3:5, 3:5].mean()
    c122 = grid12[0:2, 0:2].mean(); mid12 = grid12[3:5, 3:5].mean()
    print(f"{shot}: empties={mask.sum()} | corner wells r13={[f'{v:.1f}' for v in corner]} r12={[f'{v:.1f}' for v in corner12]}")
    print(f"   corner2x2 r13={c12:6.1f} r12={c122:6.1f} | center r13={mid:6.1f} r12={mid12:6.1f} | corner/center r13={c12/mid:.3f} r12={c122/mid12:.3f}")

# ---------- 4. STAR: search header area (y<190) and full board for warm blob 40-70px ----------
print("\n" + "=" * 100)
print("4. STAR + SHADOW (warm bright blob, body ~59px, shadow +6px offset alpha110 #0E0A06)")
print("=" * 100)
for shot in SHOTS:
    a = arr(R13 + shot)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    L = lum(a)
    # star: warm (r>g>b), bright
    warm = (r > 150) & (r > b + 40) & (g > 100) & (g < r) & (L > 140)
    # exclude board pieces zone: search only y<190 (header) first
    ys, xs = np.where(warm[0:190])
    label = "header"
    if len(ys) < 40:
        ys, xs = np.where(warm)
        label = "full"
    if len(ys) < 40:
        print(f"{shot}: no warm blob ({len(ys)} px)"); continue
    # cluster: largest connected-ish via bbox on sorted x
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    print(f"{shot} [{label}]: warm blob x[{x0},{x1}] y[{y0},{y1}] size={x1-x0}x{y1-y0} px={len(ys)}")

# ---------- 5. CONFETTI on 07_clear ----------
print("\n" + "=" * 100)
print("5. CONFETTI (07_clear): saturated non-gold pixels, hue clusters")
print("=" * 100)
for tag, base in [('r12', R12), ('r13', R13)]:
    a = arr(base + '07_clear.png')
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx = a.max(axis=2); mn = a.min(axis=2)
    sat = (mx - mn) > 60
    mxv = mx > 90
    non_gold = ~((r > 170) & (g > 120) & (b < 110))  # exclude gold pieces / star
    m = sat & mxv & non_gold
    n = m.sum()
    # hue clustering
    hues = {}
    cyan = ((b > 140) & (g > 120) & (r < 120) & m).sum()
    purple = ((r > 120) & (b > 120) & (g < 110) & m).sum()
    green = ((g > 130) & (r < 120) & (b < 130) & m).sum()
    pink = ((r > 150) & (b > 100) & (g < 120) & m).sum()
    print(f"{tag}: saturated bright non-gold px={n:6d} | cyan={cyan:5d} purple={purple:5d} green={green:5d} pink={pink:5d} "
          f"| covered rows: {sorted(set((np.where(m)[0] // 100).tolist()))[:12]}")
