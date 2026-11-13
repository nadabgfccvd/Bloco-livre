#!/usr/bin/env python3
"""Pixel-level recon of Bloco Livre screenshots: layout, palette, board grid,
block rendering metrics, OCR, skin deltas, crops for close inspection."""
import cv2, numpy as np, os, json, subprocess

SRC = '/home/z/my-project/critic_shots/r1'
CROPS = '/tmp/critic_crops'
os.makedirs(CROPS, exist_ok=True)

FILES = ['01_main_classic.png', '02_skin0.png', '03_skin1.png',
         '04_skin2.png', '05_skin3.png', '06_full.png', '07_clear.png']
TAGS = ['main', 'skin0', 'skin1', 'skin2', 'skin3', 'full', 'clear']

def hexc(bgr):
    b, g, r = [int(round(float(x))) for x in bgr]
    return '#%02X%02X%02X' % (r, g, b)

def palette(img, k=10):
    small = cv2.resize(img, (180, 360), interpolation=cv2.INTER_AREA)
    data = small.reshape(-1, 3).astype(np.float32)
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.5)
    _, label, center = cv2.kmeans(data, k, None, crit, 3, cv2.KMEANS_PP_CENTERS)
    counts = np.bincount(label.flatten(), minlength=k)
    order = np.argsort(-counts)
    return [(hexc(center[i]), round(float(counts[i]) / counts.sum(), 3)) for i in order]

def page_bg(img):
    h, w = img.shape[:2]
    pts = [(0,0),(0,w-1),(h-1,0),(h-1,w-1),(0,w//2),(h-1,w//2),(h//2,0),(h//2,w-1)]
    cols = np.array([img[y,x] for y,x in pts], dtype=np.int16)
    return cols.mean(axis=0), np.array([cv2.norm((img[y,x]-cols.mean(axis=0)).astype(np.float32)) for y,x in pts]).max()

def largest_component(mask):
    m = (mask.astype(np.uint8)) * 255
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT,(5,5)))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m, 8)
    if n <= 1: return None
    idx = 1 + np.argsort(st[1:, cv2.CC_STAT_AREA])[::-1][0]
    return st[idx]

def edge_map(img):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.Canny(g, 40, 140)

def cell_pitch(edges, x0, x1, y0, y1):
    col = edges[y0:y1, x0:x1].sum(axis=0).astype(np.float32)
    row = edges[y0:y1, x0:x1].sum(axis=1).astype(np.float32)
    def peaks(prof):
        p = [i for i in range(2, len(prof)-2) if prof[i] >= prof[i-2] and prof[i] >= prof[i+2] and prof[i] > prof.mean()]
        return p
    px_, py_ = peaks(col), peaks(row)
    def pitch(ps):
        if len(ps) < 3: return None, len(ps)
        d = np.diff(ps)
        d = d[(d > 8) & (d < 200)]
        if len(d) < 2: return None, len(ps)
        return float(np.median(d)), len(ps)
    pc, nc = pitch(px_); pr, nr = pitch(py_)
    return pc, pr, nc, nr

def ocr(img, tag):
    tmp = f'/tmp/critic_crops/_ocr_{tag}.png'
    cv2.imwrite(tmp, img)
    langs = subprocess.run(['tesseract', '--list-langs'], capture_output=True, text=True).stdout
    lang = 'por' if 'por' in langs else 'eng'
    r = subprocess.run(['tesseract', tmp, 'stdout', '-l', lang, '--psm', '11', 'tsv'],
                       capture_output=True, text=True)
    words = []
    for line in r.stdout.splitlines()[1:]:
        f = line.split('\t')
        if len(f) < 12 or not f[11].strip(): continue
        try: conf = float(f[10])
        except: continue
        if conf > 55:
            x, y, w, h = int(f[6]), int(f[7]), int(f[8]), int(f[9])
            words.append((f[11], x, y, w, h, round(conf)))
    return words, lang

REG = {}
for fn, tag in zip(FILES, TAGS):
    img = cv2.imread(os.path.join(SRC, fn))
    h, w = img.shape[:2]
    print('='*70)
    print(f'FILE {fn}  ({w}x{h})  tag={tag}')
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    print(f'  mean L*={lab[...,0].mean():.1f}  mean Sat={hsv[...,1].mean():.1f}  p90 Sat={np.percentile(hsv[...,1],90):.1f}')
    pal = palette(img)
    print('  PALETTE(page):', ', '.join(f'{c}({p})' for c, p in pal))
    bg, bgvar = page_bg(img)
    print(f'  page bg={hexc(bg)} corner var={bgvar:.1f}')
    # non-background mask
    dist = np.linalg.norm(img.astype(np.int16) - bg.astype(np.int16), axis=2)
    mask = dist > 45
    print(f'  non-bg px: {100*mask.mean():.1f}%')
    # row / col profiles of edges
    ed = edge_map(img)
    rowsum = ed.sum(axis=1); colsum = ed.sum(axis=0)
    def bands(prof, thr, minlen=12):
        out, s = [], None
        for i, v in enumerate(prof):
            if v > thr and s is None: s = i
            elif v <= thr and s is not None:
                if i - s >= minlen: out.append((s, i))
                s = None
        if s is not None and len(prof) - s >= minlen: out.append((s, len(prof)))
        return out
    rb = bands(rowsum, max(6.0, rowsum.mean()*0.9))
    cb = bands(colsum, max(4.0, colsum.mean()*0.9))
    print('  content row-bands y:', [(a, b) for a, b in rb])
    print('  content col-bands x:', [(a, b) for a, b in cb])
    # board: largest square-ish non-bg component
    comp = largest_component(mask)
    if comp is not None:
        x, y, bw, bh, area = comp
        print(f'  largest comp bbox=({x},{y},{bw}x{bh}) area={area} aspect={bw/max(1,bh):.2f}')
    # candidate board: square band intersection
    board = None
    for (y0, y1) in rb:
        for (x0, x1) in cb:
            hh, ww = y1 - y0, x1 - x0
            if 240 < ww < w*0.95 and 0.8 < ww / max(1, hh) < 1.25 and ww > 0.5 * w:
                board = (x0, x1, y0, y1)
    if board is None and comp is not None and 0.8 < bw / max(1, bh) < 1.25 and bw > 300:
        board = (x, x + bw, y, y + bh)
    print('  BOARD bbox:', board)
    REG[tag] = dict(board=board, size=[w, h], bg=hexc(bg), pal=pal)
    if board:
        x0, x1, y0, y1 = board
        bi = img[y0:y1, x0:x1]
        pc, pr, nc, nr = cell_pitch(ed, x0, x1, y0, y1)
        print(f'  grid pitch: cols {pc} (n={nc}) rows {pr} (n={nr})')
        inner_w = x1 - x0
        if pc:
            print(f'  implied cells across: {(x1-x0)/pc:.2f}  cell px={pc:.1f}')
        # cell classification
        n = 8
        cw = (x1 - x0) / n; ch = (y1 - y0) / n
        cellcols, cellstats = [], []
        for i in range(n):
            for j in range(n):
                cx0, cy0 = int(x0 + j*cw), int(y0 + i*ch)
                cell = img[cy0+3:cy0+int(ch)-3, cx0+3:cx0+int(cw)-3]
                if cell.size == 0: continue
                mean = cell.reshape(-1,3).mean(axis=0)
                cell_L = cv2.cvtColor(cell[None], cv2.COLOR_BGR2LAB)[0,...,0]
                cellcols.append(mean)
                cellstats.append((cell_L.mean(), cell_L.std()))
        cellcols = np.array(cellcols)
        celllab = cv2.cvtColor(cellcols[None].astype(np.float32), cv2.COLOR_BGR2LAB)[0]
        L = celllab[:, 0]
        medL = np.median(L)
        occ = L > medL + 6
        emptyc = cellcols[~occ]
        occc = cellcols[occ]
        print(f'  cells: occupied={occ.sum()}/64  empty median L={np.median(L[~occ]) if (~occ).any() else -1:.1f} occ L={np.median(L[occ]) if occ.any() else -1:.1f}')
        if emptyc.any():
            print('  empty-cell color:', hexc(emptyc.mean(axis=0)), 'std', round(float(emptyc.std(axis=0).mean()),1))
        if len(occc) > 3:
            d = occc.astype(np.float32)
            crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.5)
            _, lab2, cen = cv2.kmeans(d, min(6, len(d)), None, crit, 3, cv2.KMEANS_PP_CENTERS)
            cnt = np.bincount(lab2.flatten())
            blkpal = [(hexc(cen[i]), int(cnt[i])) for i in np.argsort(-cnt)]
            print('  BLOCK palette:', blkpal)
        # per-cell rendering metrics on occupied cells: vertical/horizontal ramp + texture
        rampsV, rampsH, tex = [], [], []
        for i in range(n):
            for j in range(n):
                cx0, cy0 = int(x0 + j*cw), int(y0 + i*ch)
                cell = img[cy0+3:cy0+int(ch)-3, cx0+3:cx0+int(cw)-3]
                if cell.size == 0: continue
                g = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY).astype(np.float32)
                if abs(g.mean() - np.median(L[occ])) > 8:  # not a typical occupied cell
                    pass
                rampsV.append(g[:max(1,int(g.shape[0]*0.25))].mean() - g[-max(1,int(g.shape[0]*0.25)):].mean())
                rampsH.append(g[:, :max(1,int(g.shape[1]*0.25))].mean() - g[:, -max(1,int(g.shape[1]*0.25)):].mean())
                tex.append(g.std())
        print(f'  block ramps: top-bottom {np.mean(rampsV):+.1f} L*  left-right {np.mean(rampsH):+.1f} L*  in-cell std {np.mean(tex):.1f}')
    # OCR
    words, lang = ocr(img, tag)
    print(f'  OCR({lang}) words conf>55: {len(words)}')
    for t, x, y, ww, hh, conf in words:
        print(f'    "{t}" @({x},{y}) {ww}x{hh} conf{conf}')

json.dump(REG, open('/tmp/critic_crops/regions.json', 'w'), indent=1)
print('\nDONE recon')
