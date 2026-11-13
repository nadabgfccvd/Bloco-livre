#!/usr/bin/env python3
"""Deep per-skin metrics + produce crops for close inspection."""
import cv2, numpy as np, os, subprocess, json

SRC = '/home/z/my-project/critic_shots/r1'
OUT = '/tmp/critic_crops'
os.makedirs(OUT, exist_ok=True)
FILES = ['01_main_classic.png', '02_skin0.png', '03_skin1.png',
         '04_skin2.png', '05_skin3.png', '06_full.png', '07_clear.png']
TAGS = ['main', 'skin0', 'skin1', 'skin2', 'skin3', 'full', 'clear']
BOARD = (38, 188, 644, 645)  # x0,y0,w,h
TRAY_Y = (880, 1070)
HUD_Y = (40, 165)

def hexc(bgr):
    b, g, r = [int(round(float(x))) for x in bgr]
    return '#%02X%02X%02X' % (r, g, b)

def save_zoom(img, x0, y0, w, h, name, zoom, extra=''):
    crop = img[y0:y0+h, x0:x0+w]
    z = cv2.resize(crop, (crop.shape[1]*zoom, crop.shape[0]*zoom),
                   interpolation=cv2.INTER_NEAREST if extra == 'px' else cv2.INTER_CUBIC)
    cv2.imwrite(f'{OUT}/{name}.png', z)
    return f'{OUT}/{name}.png'

def cell_grid(img, n=8):
    x0, y0, w, h = BOARD
    cw, ch = w/n, h/n
    cells = []
    for i in range(n):
        row = []
        for j in range(n):
            cx, cy = x0 + j*cw, y0 + i*ch
            cell = img[int(cy)+4:int(cy+ch)-4, int(cx)+4:int(cx+cw)-4]
            row.append(cell)
        cells.append(row)
    return cells, cw, ch

def occupied_mask(img, n=8):
    cells, cw, ch = cell_grid(img, n)
    labs = []
    for row in cells:
        for c in row:
            if c.ndim != 3 or c.shape[-1] != 3 or c.shape[0] < 2 or c.shape[1] < 2:
                labs.append(0.0)
                continue
            labs.append(float(cv2.cvtColor(c, cv2.COLOR_BGR2LAB)[..., 0].mean()))
    labs = np.array(labs)
    thr = np.median(labs) + 5
    return labs.reshape(n, n) > thr, labs.reshape(n, n)

def block_metrics(img, tag, n=8):
    occ, labs = occupied_mask(img, n)
    cells, cw, ch = cell_grid(img, n)
    bcol = []
    gradsV = gradsH = bevelL = bevelR = tex = np.array([])
    v_list, h_list, bl_list, br_list, t_list, edge_w = [], [], [], [], [], []
    for i in range(n):
        for j in range(n):
            if not occ[i, j]: continue
            c = cells[i][j]
            if c.size == 0: continue
            if c.ndim == 2:
                g = c.astype(np.float32)
            elif c.ndim == 3 and c.shape[-1] == 3 and c.shape[0] >= 2 and c.shape[1] >= 2:
                g = cv2.cvtColor(c, cv2.COLOR_BGR2GRAY).astype(np.float32)
            else:
                g = None
            if g is None: continue
            bcol.append(c.reshape(-1, 3).mean(axis=0) if c.ndim == 3 else np.array([g.mean()]*3))
            qh = max(2, int(g.shape[0]*0.22)); qw = max(2, int(g.shape[1]*0.22))
            v_list.append(g[:qh].mean() - g[-qh:].mean())
            h_list.append(g[:, :qw].mean() - g[:, -qw:].mean())
            bl_list.append(g[:qh, :qw].mean() - g.mean())
            br_list.append(g[-qh:, -qw:].mean() - g.mean())
            t_list.append(g.std())
            # edge sharpness: max gradient magnitude position spread
            gx = cv2.Sobel(g, cv2.CV_32F, 1, 0)
            edge_w.append(float(np.percentile(np.abs(gx), 99))
                          - float(np.percentile(np.abs(gx), 50)))
    bcol = np.array(bcol)
    res = dict(nblocks=int(occ.sum()))
    if len(bcol):
        # cluster block colors
        d = bcol.astype(np.float32)
        crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.4)
        k = min(7, len(d)) if len(d) >= 2 else 1
        _, lab, cen = cv2.kmeans(d, k, None, crit, 3, cv2.KMEANS_PP_CENTERS)
        cnt = np.bincount(lab.flatten(), minlength=k)
        keep = cnt >= max(2, int(len(d)*0.05))
        cens = cen[keep]; cnts = cnt[keep]
        cols = [hexc(c) for c in cens]
        res['block_colors'] = list(zip(cols, cnts.tolist()))
        # pairwise DeltaE between block color clusters (Lab)
        labc = cv2.cvtColor(cens[None].astype(np.float32), cv2.COLOR_BGR2LAB)[0]
        pairs = []
        for a in range(len(labc)):
            for b in range(a+1, len(labc)):
                de = float(np.linalg.norm(labc[a] - labc[b]))
                pairs.append((de, cols[a], cols[b]))
        pairs.sort()
        res['min_color_dE'] = round(pairs[0][0], 1) if pairs else None
        res['closest_pair'] = (pairs[0][1], pairs[0][2]) if pairs else None
        res['n_distinct(dE>15)'] = int(sum(1 for p in pairs if p[0] > 15) and len([1 for p in pairs if p[0] > 15]) // max(1, len(cols)-1) or 0)
    if v_list:
        res['grad_top_minus_bottom'] = round(float(np.mean(v_list)), 1)
        res['grad_left_minus_right'] = round(float(np.mean(h_list)), 1)
        res['cornerTL_minus_mean'] = round(float(np.mean(bl_list)), 1)
        res['cornerBR_minus_mean'] = round(float(np.mean(br_list)), 1)
        res['inblock_std'] = round(float(np.mean(t_list)), 1)
        res['edge_99-50'] = round(float(np.mean(edge_w)), 1)
    # empty cell color + contrast
    empt = []
    for i in range(n):
        for j in range(n):
            if occ[i, j]: continue
            c = cells[i][j]
            if c.size: empt.append(c.reshape(-1, 3).mean(axis=0))
    if empt:
        e = np.array(empt).mean(axis=0)
        res['empty_color'] = hexc(e)
        if len(bcol):
            bl = cv2.cvtColor(np.array([bcol.mean(axis=0), e])[None].astype(np.float32), cv2.COLOR_BGR2LAB)[0]
            res['dE_block_vs_empty'] = round(float(np.linalg.norm(bl[0]-bl[1])), 1)
    # grid line visibility: variance across horizontal scan through empty band
    x0, y0, w, h = BOARD
    strip = img[y0+int(h*0.62):y0+int(h*0.70), x0:x0+w].astype(np.float32)
    gstrip = cv2.cvtColor(strip, cv2.COLOR_BGR2GRAY)
    prof = gstrip.mean(axis=0)
    res['empty_row_contrast_range'] = round(float(prof.max() - prof.min()), 1)
    return res, occ

def corner_radius_est(img, tag):
    """Estimate rounded-corner radius of an occupied cell: compare filled area vs bbox."""
    occ, _ = occupied_mask(img)
    cells, cw, ch = cell_grid(img)
    idx = [(i, j) for i in range(8) for j in range(8) if occ[i, j]]
    if not idx: return None
    i, j = idx[0]
    cell = cells[i][j]
    g = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
    # find the face: threshold against cell min
    face = (g > g.min() + 25).astype(np.uint8)*255
    n, lab, st, cen = cv2.connectedComponentsWithStats(face, 8)
    if n <= 1: return None
    big = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
    x, y, bw, bh, area = st[big]
    fill = area/(bw*bh)
    # fill 1.0 = square, ~0.95 = r≈10% side
    return dict(face=(int(bw), int(bh)), fill=round(float(fill), 3))

print('#'*72)
print('# PER-SKIN BOARD/BLOCK FORENSICS')
print('#'*72)
SHOTS = {'skin0': '02_skin0.png', 'skin1': '03_skin1.png',
         'skin2': '04_skin2.png', 'skin3': '05_skin3.png',
         'full': '06_full.png', 'clear': '07_clear.png'}
results = {}
for tag, fn in SHOTS.items():
    img = cv2.imread(os.path.join(SRC, fn))
    m, occ = block_metrics(img, tag)
    cr = corner_radius_est(img, tag)
    m['corner'] = cr
    results[tag] = m
    print(f'\n== {tag} ({fn})')
    for k, v in m.items():
        print(f'   {k}: {v}')

# ---- glow / bloom for neon: bright pixel halo ----
print('\n#'*1)
print('## BLOOM check (halo around saturated blocks)')
img = cv2.imread(os.path.join(SRC, '03_skin1.png'))
x0, y0, w, h = BOARD
bi = img[y0:y0+h, x0:x0+w]
hsv = cv2.cvtColor(bi, cv2.COLOR_BGR2HSV)
bright = (hsv[..., 2] > 235).mean()
blur = cv2.GaussianBlur(hsv[..., 2], (21, 21), 0)
halo = ((blur > 90) & (hsv[..., 2] < 90)).mean()
print(f'neon board: pure-bright px {bright*100:.2f}%  halo(brightened surroundings) {halo*100:.2f}%')
img0 = cv2.imread(os.path.join(SRC, '02_skin0.png'))
bi0 = img0[y0:y0+h, x0:x0+w]
hsv0 = cv2.cvtColor(bi0, cv2.COLOR_BGR2HSV)
blur0 = cv2.GaussianBlur(hsv0[..., 2], (21, 21), 0)
halo0 = ((blur0 > 90) & (hsv0[..., 2] < 90)).mean()
print(f'classic board: halo {halo0*100:.2f}% (should be ~0)')

# ---- pixel skin chunkiness: gradient sharpness ----
print('\n## EDGE SHARPNESS (pixel-art should have crisp 1px ramp in board coords)')
for tag, fn in [('skin3', '05_skin3.png'), ('skin0', '02_skin0.png')]:
    img = cv2.imread(os.path.join(SRC, fn))
    occ, _ = occupied_mask(img)
    cells, cw, ch = cell_grid(img)
    ws = []
    for i in range(8):
        for j in range(8):
            if not occ[i, j]: continue
            c = cells[i][j]
            g = cv2.cvtColor(c, cv2.COLOR_BGR2GRAY).astype(np.float32)
            gx = np.abs(cv2.Sobel(g, cv2.CV_32F, 1, 0)).sum(axis=0)
            tot = gx.sum()
            if tot <= 0: continue
            # fraction of x-gradient energy in the single strongest column
            ws.append(float(gx.max()/tot))
    print(f'{tag}: strongest-column gradient energy fraction = '
          f'{np.mean(ws)*100 if ws else 0:.1f}% '
          f'(1px hard edge ~ 60-90%, soft AA edge ~ 15-35%)')

# ---- celebration particles in 07 ----
print('\n## CELEBRATION PARTICLES in 07_clear')
img = cv2.imread(os.path.join(SRC, '07_clear.png'))
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
bright = ((hsv[..., 2] > 150) & (hsv[..., 1] > 60)).astype(np.uint8)*255
# exclude HUD/board/tray zones
bright[:170, :] = 0; bright[860:1080, :] = 0; bright[1090:, :] = 0
bright[188:840, 30:695] = 0
n, lab, st, cen = cv2.connectedComponentsWithStats(bright, 8)
parts = []
for i in range(1, n):
    x, y, bw, bh, area = st[i]
    if 4 <= bw <= 60 and 4 <= bh <= 60:
        parts.append((x, y, bw, bh, area, hexc(img[y+bh//2, x+bw//2])))
print(f'particle-like comps: {len(parts)}')
for p in parts[:25]:
    print('   ', p)
# scan whole page too
bright2 = ((hsv[..., 2] > 150) & (hsv[..., 1] > 60)).astype(np.uint8)*255
bright2[:170, :] = 0
n2, lab2, st2, cen2 = cv2.connectedComponentsWithStats(bright2, 8)
parts2 = [st2[i] for i in range(1, n2) if 4 <= st2[i, 2] <= 40 and 4 <= st2[i, 3] <= 40]
print(f'page-wide particle-like comps (excl HUD): {len(parts2)}')

# ---- shadows under board? ----
print('\n## SHADOW under board / tray pieces')
img = cv2.imread(os.path.join(SRC, '02_skin0.png'))
for name, (a, b) in [('below-board y833-880', (833, 880)), ('above-board y150-188', (150, 188))]:
    strip = cv2.cvtColor(img[a:b, 38:682], cv2.COLOR_BGR2GRAY)
    print(f'{name}: L mean {strip.mean():.1f} min {strip.min():.1f}')

# ---- typography stroke analysis: HUD crop OCR upscale ----
print('\n## HUD OCR (3x upscale)')
img = cv2.imread(os.path.join(SRC, '02_skin0.png'))
hud = img[HUD_Y[0]:HUD_Y[1], :]
hud3 = cv2.resize(hud, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
cv2.imwrite('/tmp/critic_crops/_ocr_hud.png', hud3)
r = subprocess.run(['tesseract', '/tmp/critic_crops/_ocr_hud.png', 'stdout', '--psm', '11', 'tsv'],
                   capture_output=True, text=True)
for line in r.stdout.splitlines()[1:]:
    f = line.split('\t')
    if len(f) >= 12 and f[11].strip() and float(f[10]) > 50:
        print(f'   "{f[11]}" conf {f[10]} box x={int(f[6])/3:.0f} y={int(f[7])/3:.0f} '
              f'w={int(f[8])/3:.0f} h={int(f[9])/3:.0f}')

# ---- dead-space map ----
print('\n## VERTICAL COMPOSITION (720x1440)')
img = cv2.imread(os.path.join(SRC, '02_skin0.png'))
g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
rowact = (g > 60).mean(axis=1)
bands = []
s = None
for i, v in enumerate(rowact):
    if v > 0.01 and s is None: s = i
    elif v <= 0.01 and s is not None:
        if i - s > 20: bands.append((s, i))
        s = None
if s is not None: bands.append((s, 1440))
print('   active content bands:', bands)
print(f'   bottom dead zone: {1440 - 1070}px = {(1440-1070)/1440*100:.0f}% of screen height')

# ---- tray geometry ----
print('\n## TRAY geometry')
for tag, fn in [('skin0', '02_skin0.png'), ('full', '06_full.png'), ('clear', '07_clear.png')]:
    img = cv2.imread(os.path.join(SRC, fn))
    tray = img[TRAY_Y[0]:TRAY_Y[1], :]
    g = cv2.cvtColor(tray, cv2.COLOR_BGR2GRAY)
    edge = cv2.Canny(g, 40, 140)
    prof = edge.sum(axis=0).astype(np.float32)
    pk = [i for i in range(3, len(prof)-3) if prof[i] >= prof[i-3] and prof[i] >= prof[i+3] and prof[i] > 3]
    print(f'   {tag}: edge peaks x:', pk[:20])

json.dump(results, open('/tmp/critic_crops/skin_metrics.json', 'w'), indent=1, default=str)
print('\nMETRICS DONE')
