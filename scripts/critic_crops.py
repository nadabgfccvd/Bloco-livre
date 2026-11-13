#!/usr/bin/env python3
"""Produce all required crops + ASCII visualizations + HUD color/bezel checks."""
import cv2, numpy as np, os, subprocess

SRC = '/home/z/my-project/critic_shots/r1'
OUT = '/tmp/critic_crops'
os.makedirs(OUT, exist_ok=True)
BOARD = (38, 188, 644, 645)
SHOTS = {'skin0': '02_skin0.png', 'skin1': '03_skin1.png',
         'skin2': '04_skin2.png', 'skin3': '05_skin3.png',
         'full': '06_full.png', 'clear': '07_clear.png', 'main': '01_main_classic.png'}

def hexc(bgr):
    b, g, r = [int(round(float(x))) for x in bgr]
    return '#%02X%02X%02X' % (r, g, b)

def find_occupied(img):
    x0, y0, w, h = BOARD
    cw, ch = w/8, h/8
    occ = np.zeros((8,8), bool); cols = {}
    for i in range(8):
        for j in range(8):
            c = img[int(y0+i*ch)+6:int(y0+(i+1)*ch)-6, int(x0+j*cw)+6:int(x0+(j+1)*cw)-6]
            if c.shape[0] < 5 or c.shape[1] < 5: continue
            lab = cv2.cvtColor(c, cv2.COLOR_BGR2LAB)
            if lab[...,0].mean() > 38:
                occ[i,j] = True
                cols[(i,j)] = hexc(c.reshape(-1,3).mean(axis=0))
    return occ, cols

def ascii_cell(img, cx, cy, size=72, chars=' .:-=+*#%@'):
    c = img[cy:cy+size, cx:cx+size]
    g = cv2.cvtColor(c, cv2.COLOR_BGR2GRAY)
    g = cv2.resize(g, (36, 36), interpolation=cv2.INTER_AREA)
    lines = []
    for row in g:
        lines.append(''.join(chars[min(9, int(v/25.6))] for v in row))
    return '\n'.join(lines)

# ---------- 1) required crops ----------
crops = []
# block close-up per skin: pick a representative occupied cell (row2,col1 area)
for tag in ['skin0', 'skin1', 'skin2', 'skin3']:
    img = cv2.imread(os.path.join(SRC, SHOTS[tag]))
    occ, cols = find_occupied(img)
    idx = [(i,j) for i in range(8) for j in range(8) if occ[i,j]]
    if not idx: continue
    i, j = idx[len(idx)//2]
    x0, y0, w, h = BOARD
    cx, cy = int(x0 + j*w/8), int(y0 + i*h/8)
    cell = img[cy:cy+80, cx:cx+80]
    z4 = cv2.resize(cell, (320, 320), interpolation=cv2.INTER_NEAREST)
    p = f'{OUT}/block_{tag}_4x.png'
    cv2.imwrite(p, z4)
    crops.append((p, f'block close-up {tag} 4x'))
    print(f'### ASCII luminance — {tag} representative block @({cx},{cy})')
    print(ascii_cell(img, cx, cy))
    print()

img0 = cv2.imread(os.path.join(SRC, '02_skin0.png'))
# HUD crop
hud = img0[30:180, :]
cv2.imwrite(f'{OUT}/hud.png', cv2.resize(hud, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC))
crops.append((f'{OUT}/hud.png', 'HUD 2x'))
# tray crop
tray = img0[860:1080, :]
cv2.imwrite(f'{OUT}/tray.png', cv2.resize(tray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC))
crops.append((f'{OUT}/tray.png', 'tray 2x'))
# board zoom 1 (whole board)
board = img0[188:835, 38:682]
cv2.imwrite(f'{OUT}/board_full.png', board)
crops.append((f'{OUT}/board_full.png', 'board full'))
# board zoom 2 (top-left quadrant 2x)
q = img0[188:520, 38:350]
cv2.imwrite(f'{OUT}/board_quadrant_2x.png', cv2.resize(q, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC))
crops.append((f'{OUT}/board_quadrant_2x.png', 'board quadrant 2x'))
# celebration area in 07
imgc = cv2.imread(os.path.join(SRC, '07_clear.png'))
spark = imgc[900:1040, 480:700]
cv2.imwrite(f'{OUT}/clear_sparkles_4x.png', cv2.resize(spark, None, fx=4, fy=4, interpolation=cv2.INTER_NEAREST))
crops.append((f'{OUT}/clear_sparkles_4x.png', 'sparkle/particle region 4x'))
print('### ASCII — sparkle region in 07_clear (480-700, 900-1040)')
sp = cv2.cvtColor(spark, cv2.COLOR_BGR2GRAY)
sp = cv2.resize(sp, (44, 17), interpolation=cv2.INTER_AREA)
print('\n'.join(''.join(' .:-=+*#%@'[min(9,int(v/25.6))] for v in row) for row in sp))
print()
# main screen micro-text line
imgm = cv2.imread(os.path.join(SRC, '01_main_classic.png'))
micro = imgm[1040:1080, 0:720]
cv2.imwrite(f'{OUT}/main_microtext_4x.png', cv2.resize(micro, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC))
r = subprocess.run(['tesseract', f'{OUT}/main_microtext_4x.png', 'stdout', '--psm', '7'],
                   capture_output=True, text=True)
print('### main-screen micro text OCR (y1040-1080):', repr(r.stdout.strip()))
crops.append((f'{OUT}/main_microtext_4x.png', 'main microtext 4x'))

# ---------- 2) board state maps ----------
print('\n### BOARD STATE MAPS (hex fill color per cell, . = empty)')
for tag in ['skin0', 'skin1', 'skin2', 'skin3', 'full', 'clear']:
    img = cv2.imread(os.path.join(SRC, SHOTS[tag]))
    occ, cols = find_occupied(img)
    print(f'-- {tag}')
    for i in range(8):
        row = []
        for j in range(8):
            row.append(cols.get((i,j), '......') if occ[i,j] else '  .   ')
        print('   ' + ' '.join(row))

# ---------- 3) HUD text colors ----------
print('\n### HUD colors (02_skin0)')
def text_color(img, x, y, w, h):
    reg = img[y:y+h, x:x+w]
    g = cv2.cvtColor(reg, cv2.COLOR_BGR2GRAY)
    bgv = np.percentile(g, 60)
    m = g > bgv + 40
    if m.sum() < 5: m = g > np.percentile(g, 90)
    px = reg[m]
    return hexc(px.mean(axis=0)), int(m.sum())
print('   PONTOS label :', text_color(img0, 20, 46, 97, 22))
print('   score 216    :', text_color(img0, 21, 86, 89, 40))
print('   RECORDE label :', text_color(img0, 514, 47, 114, 22))
print('   rec 216      :', text_color(img0, 562, 80, 66, 30))
print('   combo line   :', text_color(img0, 19, 140, 180, 20))
print('   skin label    :', text_color(img0, 508, 138, 130, 20))

# ---------- 4) bezel / frame / shadow check ----------
print('\n### BOARD EDGE PROFILE (02_skin0, horizontal scanline y=511)')
row = img0[511, 0:720].astype(np.int16)
xs = [0, 20, 34, 36, 38, 40, 44, 50, 76, 116, 120, 124, 676, 680, 682, 684, 700, 719]
print('   ' + '  '.join(f'x{x}={hexc(row[x])}' for x in xs))
print('### BOARD EDGE vertical profile (x=360, y 180..200 and 826..850)')
for yy in [180, 184, 186, 188, 190, 196, 826, 830, 833, 836, 840, 848]:
    print(f'   y{yy}={hexc(img0[yy, 360])}', end='')
print()
print('### shadow strip under board (y 836-878) vs above (y 150-186):')
for name, a, b in [('above', 150, 186), ('below', 836, 878)]:
    strip = cv2.cvtColor(img0[a:b, 60:660], cv2.COLOR_BGR2GRAY)
    print(f'   {name}: mean L {strip.mean():.1f}  p10 {np.percentile(strip,10):.0f} p90 {np.percentile(strip,90):.0f}')

# ---------- 5) neon block structure ----------
img1 = cv2.imread(os.path.join(SRC, '03_skin1.png'))
occ1, _ = find_occupied(img1)
idx = [(i,j) for i in range(8) for j in range(8) if occ1[i,j]]
if idx:
    i, j = idx[0]
    x0, y0, w, h = BOARD
    cx, cy = int(x0 + j*w/8), int(y0 + i*h/8)
    print('\n### ASCII — NEON block (first occupied cell)')
    print(ascii_cell(img1, cx, cy))
    # radial profile of one neon cell
    cell = img1[cy:cy+80, cx:cx+80]
    g = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY).astype(np.float32)
    mid = g[36, :]  # horizontal cut
    print('   horizontal luminance cut through neon cell (80 px):')
    print('   ' + ' '.join(f'{int(v)}' for v in mid[::4]))

# ---------- 6) pixel skin internal pattern ----------
img3 = cv2.imread(os.path.join(SRC, '05_skin3.png'))
occ3, cols3 = find_occupied(img3)
idx = [(i,j) for i in range(8) for j in range(8) if occ3[i,j]]
if idx:
    i, j = idx[0]
    x0, y0, w, h = BOARD
    cx, cy = int(x0 + j*w/8), int(y0 + i*h/8)
    print('\n### ASCII — PIXEL block')
    print(ascii_cell(img3, cx, cy))
    print('   pixel-skin distinct colors on board:', sorted(set(cols3.values())))

# ---------- 7) gem skin cell ----------
img2 = cv2.imread(os.path.join(SRC, '04_skin2.png'))
occ2, cols2 = find_occupied(img2)
idx = [(i,j) for i in range(8) for j in range(8) if occ2[i,j]]
if idx:
    i, j = idx[0]
    x0, y0, w, h = BOARD
    cx, cy = int(x0 + j*w/8), int(y0 + i*h/8)
    print('\n### ASCII — GEMA block')
    print(ascii_cell(img2, cx, cy))

print('\nCROPS WRITTEN:')
for p, d in crops:
    print('  ', p, '—', d, os.path.getsize(p), 'bytes')
