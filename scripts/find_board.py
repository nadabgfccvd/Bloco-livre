#!/usr/bin/env python3
"""Locate board bbox precisely: model board as large square region distinct from page bg."""
import cv2, numpy as np, os

SRC = '/home/z/my-project/critic_shots/r1'
FILES = ['01_main_classic.png', '02_skin0.png', '03_skin1.png',
         '04_skin2.png', '05_skin3.png', '06_full.png', '07_clear.png']
TAGS = ['main', 'skin0', 'skin1', 'skin2', 'skin3', 'full', 'clear']

for fn, tag in zip(FILES, TAGS):
    img = cv2.imread(os.path.join(SRC, fn))
    h, w = img.shape[:2]
    bg = img[0, 0].astype(np.int16)
    dist = np.linalg.norm(img.astype(np.int16) - bg, axis=2)
    mask = (dist > 38).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3,3), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(mask, 8)
    comps = sorted(range(1, n), key=lambda i: -st[i, cv2.CC_STAT_AREA])[:8]
    print(f'{tag}: candidates')
    for i in comps:
        x, y, bw, bh, area = st[i]
        print(f'   bbox=({x},{y}) {bw}x{bh} area={area} aspect={bw/max(1,bh):.2f} fill={area/max(1,bw*bh):.2f}')
    # board: aspect near 1, big
    best = None
    for i in comps:
        x, y, bw, bh, area = st[i]
        if bw > 300 and 0.9 < bw / max(1, bh) < 1.1 and area > 60000:
            best = (x, y, bw, bh)
    print('   -> board:', best)
