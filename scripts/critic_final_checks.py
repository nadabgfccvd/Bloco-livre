#!/usr/bin/env python3
"""Final checks: main-screen bottom strip, tray piece shadows, board corner shape,
danger state in 06_full, HUD font stroke weight, neon empty tile color oddity."""
import cv2, numpy as np, os, subprocess

SRC = '/home/z/my-project/critic_shots/r1'

def hexc(bgr):
    b, g, r = [int(round(float(x))) for x in bgr]
    return '#%02X%02X%02X' % (r, g, b)

imgm = cv2.imread(os.path.join(SRC, '01_main_classic.png'))
print('### MAIN SCREEN bottom strip y1040-1080 (what is the micro text?)')
strip = imgm[1040:1080, :]
g = cv2.cvtColor(strip, cv2.COLOR_BGR2GRAY)
m = (g > 70).astype(np.uint8)
n, lab, st, cen = cv2.connectedComponentsWithStats(m*255, 8)
comps = [(st[i,0], st[i,1], st[i,2], st[i,3], hexc(strip[st[i,1]+st[i,3]//2, st[i,0]+st[i,2]//2])) for i in range(1, n) if st[i,2] > 3]
print('   bright comps:', comps)
# OCR the strip 6x
big = cv2.resize(strip, None, fx=6, fy=6, interpolation=cv2.INTER_CUBIC)
cv2.imwrite('/tmp/critic_crops/_bottom6x.png', big)
for psm in ('6', '7', '11'):
    r = subprocess.run(['tesseract', '/tmp/critic_crops/_bottom6x.png', 'stdout', '--psm', psm],
                       capture_output=True, text=True)
    t = r.stdout.strip()
    if t:
        print(f'   OCR psm{psm}: {t!r}')

print('\n### TRAY PIECE SHADOW test (02_skin0): under right tray piece x514-687, y1063-1090')
img0 = cv2.imread(os.path.join(SRC, '02_skin0.png'))
under = cv2.cvtColor(img0[1063:1090, 514:687], cv2.COLOR_BGR2GRAY)
side = cv2.cvtColor(img0[1063:1090, 200:400], cv2.COLOR_BGR2GRAY)
print(f'   under-piece L mean {under.mean():.1f} vs empty-side L mean {side.mean():.1f} (shadow would make under darker by 10+)')

print('\n### BOARD CONTAINER corners (02_skin0): does the board tile have rounded corners?')
# look at board tile corner at (38,188)
tl = img0[185:200, 36:50]
if tl.shape[0] > 2 and tl.shape[1] > 2:
    print('   board TL 12x12 px colors:', [hexc(tl[y, x]) for y in (0, 5, min(11, tl.shape[0]-1)) for x in (0, 5, min(11, tl.shape[1]-1))])
# empty cell tile corner: pick an empty cell e.g. row0 col0 center
print('   empty cell seam check row0col0:', hexc(img0[199, 46]), hexc(img0[199, 80]), hexc(img0[199, 112]))

print('\n### DANGER STATE check (06_full): vignette / red tint at page edges?')
imgf = cv2.imread(os.path.join(SRC, '06_full.png'))
hsv = cv2.cvtColor(imgf, cv2.COLOR_BGR2HSV)
top = hsv[0:40, :]; mid = hsv[700:740, :]; bot = hsv[1400:1440, :]
print(f'   top strip H={top[...,0].mean():.0f} S={top[...,1].mean():.0f} V={top[...,2].mean():.0f}')
print(f'   mid strip H={mid[...,0].mean():.0f} S={mid[...,1].mean():.0f} V={mid[...,2].mean():.0f}')
print(f'   bottom strip H={bot[...,0].mean():.0f} S={bot[...,1].mean():.0f} V={bot[...,2].mean():.0f}')

print('\n### HUD FONT stroke weight (02_skin0, "PONTOS" label)')
lab = img0[46:68, 20:118]
gl = cv2.cvtColor(lab, cv2.COLOR_BGR2GRAY)
th = gl > 100
ink = th.sum()
# skeleton-ish: count rows where ink present to estimate cap height & stem width
cols = th.sum(axis=0)
stems = [c for c in cols if c > 0]
print(f'   ink px {ink}, max col run {max(stems) if stems else 0} (cap height ~ {th.sum(axis=1).max()} px)')
# stroke width via distance: average run length of ink in a horizontal cut
runs = []
for y in range(gl.shape[0]):
    row = gl[y] > 100
    c = 0
    for v in row:
        if v: c += 1
        elif c: runs.append(c); c = 0
    if c: runs.append(c)
runs = np.array(runs) if runs else np.array([0])
print(f'   mean horizontal ink run {runs.mean():.1f}px  p90 {np.percentile(runs,90):.0f}px  (thin/light font <3px at this size)')

print('\n### NEON empty tile color consistency (03_skin1)')
imgn = cv2.imread(os.path.join(SRC, '03_skin1.png'))
print('   neon empty cell (row1,col0):', hexc(imgn[188+80+10+8, 38+12]), ' board bg:', hexc(imgn[200, 60]), ' page:', hexc(imgn[5, 5]))

print('\n### SCORE POPUP / floating text in 07_clear (any large bright text mid-board)?')
imgc = cv2.imread(os.path.join(SRC, '07_clear.png'))
mid = imgc[170:860, 30:700]
gm = cv2.cvtColor(mid, cv2.COLOR_BGR2GRAY)
big_bright = (gm > 200).sum()
print(f'   bright(>200) px in board zone: {big_bright} ({100*big_bright/gm.size:.2f}%)')
hsv_c = cv2.cvtColor(mid, cv2.COLOR_BGR2HSV)
print(f'   mean S in board zone: {hsv_c[...,1].mean():.0f}  (celebration flash would spike S/V here)')
