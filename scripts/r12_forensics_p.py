#!/usr/bin/env python3
"""R12 part P: r11-vs-r12 spoke widths (identical method); star body run-length bottom/gap;
fine ASCII of star; tray strip signed colors."""
from PIL import Image
import numpy as np

R12 = '/home/z/my-project/critic_shots/r12/'
R11 = '/home/z/my-project/critic_shots/r11/'

def load(p):
    return np.asarray(Image.open(p).convert('RGB')).astype(int)

def centroid_bright(im):
    lum = im.mean(axis=2)
    m = np.zeros_like(lum, dtype=bool)
    m[190:357, :] = lum[190:357, :] > 235
    ys, xs = np.where(m)
    return int(round(xs.mean())), int(round(ys.mean()))

def ring_runs(im, cx, cy, r, th=200):
    lum = im.mean(axis=2)
    n = 3600
    a = np.linspace(0, 2*np.pi, n, endpoint=False)
    hits = np.zeros(n, bool)
    for i, ang in enumerate(a):
        for d in (-2,-1,0,1,2):
            x = int(round(cx + (r+d)*np.cos(ang))); y = int(round(cy + (r+d)*np.sin(ang)))
            if 0 <= x < 720 and 0 <= y < 1440 and lum[y, x] > th:
                hits[i] = True; break
    runs = []
    i = 0
    while i < n:
        if hits[i]:
            j = i
            while j < n and hits[j]:
                j += 1
            runs.append((i, j)); i = j
        else:
            i += 1
    if len(runs) > 1 and runs[0][0] == 0 and runs[-1][1] == n:
        runs[-1] = (runs[-1][0], runs[-1][1]+runs[0][1]); runs = runs[1:]
    return [round((b-a)/n*2*np.pi*r,1) for a,b in runs]

print("=== SPOKE WIDTHS: identical method on r11 and r12 (07_clear) ===")
for tag in ('r11','r12'):
    im = load((R11 if tag=='r11' else R12)+'07_clear.png')
    cx, cy = centroid_bright(im)
    print(f"[{tag}] center=({cx},{cy})")
    for r in (88.2, 96.6):
        ch = ring_runs(im, cx, cy, r)
        small = sorted(c for c in ch if 2 < c <= 20)
        print(f"   r={r}: chords={ch}")
        print(f"      spoke-like(2-20px): n={len(small)} mean={np.mean(small) if small else 0:.1f} values={small}")

# ============ STAR BODY via run-length (star is thick, rays are thin) ============
print("\n=== STAR BODY run-length analysis (07_clear, x280-460) ===")
def star_rows_runs(im, tag):
    lum = im.mean(axis=2)
    R, G, B = im[:,:,0], im[:,:,1], im[:,:,2]
    gold = (R > 200) & (G > 140) & (B < 200) & (R - B > 60)
    print(f"--- {tag} ---")
    last_body = None; first_body = None
    for y in range(215, 356):
        row = gold[y, 280:460]
        # max run length
        best = 0; cur = 0
        for v in row:
            cur = cur + 1 if v else 0
            best = max(best, cur)
        n = row.sum()
        if best >= 8:  # thick = star body
            if first_body is None: first_body = y
            last_body = y
            if y % 6 == 0 or y in (340,341,342,343,344,345,346,347,348,349,350,351,352,353):
                print(f"   y={y} gold_n={n} max_run={best}")
    print(f"   => body rows (max_run>=8): {first_body}..{last_body}")
    return first_body, last_body

f12, l12 = star_rows_runs(load(R12+'07_clear.png'), 'r12')
f11, l11 = star_rows_runs(load(R11+'07_clear.png'), 'r11')
print("\nr12 body:", f12, l12, " r11 body:", f11, l11)
print("band top (solid gold row): 354 (both)")
if l12 is not None:
    print(f"r12 gap = {354 - l12 - 1} px below star body; r11 gap = {354 - l11 - 1 if l11 else '?'} px")

# ============ FINE ASCII of r12 star (x280-460, y215-360, 3px cells) ============
im = load(R12+'07_clear.png')
R, G, B = im[:,:,0], im[:,:,1], im[:,:,2]
def cls(r,g,b):
    l=(r+g+b)/3
    if r>200 and g>150 and b<120: return '#'
    if r>230 and g>210 and b>150: return '@'
    if l>200: return 'W'
    if l>150: return '+'
    if l>100: return 'o'
    if l>60: return '.'
    if l>35: return ':'
    return ' '
print("\n=== r12 STAR fine ASCII (3px cells) x280-460 ===")
for y in range(215, 360, 3):
    print(f"{y:4d} {''.join(cls(R[y,x],G[y,x],B[y,x]) for x in range(280, 461, 3))}")

# ============ tray strip signed colors ============
print("\n=== HERO tray strip signed colors (x=360) rows 830..900 ===")
a = load(R11+'01_hero.png'); b = load(R12+'01_hero.png')
for y in range(830, 901, 2):
    ca = tuple(a[y,360]); cb = tuple(b[y,360])
    print(y, "r11:", ca, " r12:", cb, " d:", tuple(np.array(cb)-np.array(ca)))
