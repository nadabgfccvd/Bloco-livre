"""R13 forensic analysis - PASS 1: global stats + region std-devs, r12 vs r13."""
import numpy as np
from PIL import Image

R12 = '/home/z/my-project/critic_shots/r12/'
R13 = '/home/z/my-project/critic_shots/r13/'
SHOTS = ['01_hero.png','02_skin0.png','03_skin1.png','04_skin2.png','05_skin3.png','06_full.png','07_clear.png']

# Geometry
X0, X1, Y0, Y1 = 24, 696, 190, 866      # board 8x8, cell 84
CELL = 84
TRAY_Y0, TRAY_Y1 = 860, 1142
STREAK_Y0, STREAK_Y1 = 1238, 1252

def arr(path):
    return np.asarray(Image.open(path).convert('RGB')).astype(np.float64)

def region_stats(a, x0, y0, x1, y1):
    r = a[y0:y1, x0:x1]
    g = r.mean(axis=2)
    return dict(mean=g.mean(), std=g.std(), h=r.shape[0], w=r.shape[1])

def luminance(a, x0, y0, x1, y1):
    r = a[y0:y1, x0:x1]
    g = r.mean(axis=2)
    return g.mean()

def color_count(a, x0, y0, x1, y1, quant=8):
    r = a[y0:y1, x0:x1].astype(int)
    q = (r // quant) * quant
    flat = q[..., 0] * 4096 + q[..., 1] * 64 + q[..., 2]
    return len(np.unique(flat))

print("=" * 100)
print("GLOBAL + REGION COMPARISON  r12 vs r13")
print("=" * 100)
for shot in SHOTS:
    a12 = arr(R12 + shot)
    a13 = arr(R13 + shot)
    print(f"\n--- {shot} ---")
    print(f"  GLOBAL   mean r12={a12.mean():6.2f}  r13={a13.mean():6.2f}   "
          f"diffpixels={np.abs(a13-a12).mean():6.2f}  changed>8: {(np.abs(a13-a12).max(axis=2)>8).mean()*100:5.1f}%")
    # board
    s12 = region_stats(a12, X0, Y0, X1, Y1); s13 = region_stats(a13, X0, Y0, X1, Y1)
    print(f"  BOARD    std r12={s12['std']:6.2f} r13={s13['std']:6.2f}   "
          f"mean r12={s12['mean']:6.2f} r13={s13['mean']:6.2f}   colors r12={color_count(a12,X0,Y0,X1,Y1):3d} r13={color_count(a13,X0,Y0,X1,Y1):3d}")
    # tray
    s12t = region_stats(a12, X0, TRAY_Y0, X1, TRAY_Y1); s13t = region_stats(a13, X0, TRAY_Y0, X1, TRAY_Y1)
    print(f"  TRAY     std r12={s12t['std']:6.2f} r13={s13t['std']:6.2f}   mean r12={s12t['mean']:6.2f} r13={s13t['mean']:6.2f}")
    # streak strip
    s12s = region_stats(a12, X0, STREAK_Y0, X1, STREAK_Y1); s13s = region_stats(a13, X0, STREAK_Y0, X1, STREAK_Y1)
    print(f"  STREAK   std r12={s12s['std']:6.2f} r13={s13s['std']:6.2f}   "
          f"mean r12={s12s['mean']:6.2f} r13={s13s['mean']:6.2f}   colors r12={color_count(a12,X0,STREAK_Y0,X1,STREAK_Y1):3d} r13={color_count(a13,X0,STREAK_Y0,X1,STREAK_Y1):3d}")
    # header (above board)
    s12h = region_stats(a12, 0, 0, 720, 190); s13h = region_stats(a13, 0, 0, 720, 190)
    print(f"  HEADER   std r12={s12h['std']:6.2f} r13={s13h['std']:6.2f}   mean r12={s12h['mean']:6.2f} r13={s13h['mean']:6.2f}")
    # footer (below streak)
    s12f = region_stats(a12, 0, 1252, 720, 1440); s13f = region_stats(a13, 0, 1252, 720, 1440)
    print(f"  FOOTER   std r12={s12f['std']:6.2f} r13={s13f['std']:6.2f}   mean r12={s12f['mean']:6.2f} r13={s13f['mean']:6.2f}")

print("\n" + "=" * 100)
print("BOARD VIGNETTE CHECK: corner vs center luminance (empty wells area)")
print("=" * 100)
for shot in SHOTS:
    a = arr(R13 + shot)
    # corner patch inside board (avoid cells with pieces: use small patches at 4 corners of board frame)
    tl = luminance(a, X0+2, Y0+2, X0+30, Y0+30)
    tr = luminance(a, X1-30, Y0+2, X1-2, Y0+30)
    bl = luminance(a, X0+2, Y1-30, X0+30, Y1-2)
    br = luminance(a, X1-30, Y1-30, X1-2, Y1-2)
    cx = luminance(a, 360-30, 526-30, 360+30, 526+30)
    a12 = arr(R12 + shot)
    tl12 = luminance(a12, X0+2, Y0+2, X0+30, Y0+30)
    tr12 = luminance(a12, X1-30, Y0+2, X1-2, Y0+30)
    cx12 = luminance(a12, 360-30, 526-30, 360+30, 526+30)
    print(f"{shot}: r13 corners TL={tl:5.1f} TR={tr:5.1f} BL={bl:5.1f} BR={br:5.1f} center={cx:5.1f} | "
          f"r12 TL={tl12:5.1f} TR={tr12:5.1f} CX={cx12:5.1f}")
