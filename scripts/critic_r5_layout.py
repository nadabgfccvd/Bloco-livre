#!/usr/bin/env python3
"""R5 forensics part 2: locate layout bands precisely on every shot.

Strategy: the board is a 10-col grid; find its exact pixel bounds by scanning
for the grid pitch in the mid image, then report HUD / board / tray / footer
bands. Save probe crops.
"""
import os
from PIL import Image
import numpy as np

SHOTS = '/home/z/my-project/critic_shots/r5'
CROPS = '/tmp/critic_crops_r5'
os.makedirs(CROPS, exist_ok=True)

def bands(name, tag):
    im = Image.open(os.path.join(SHOTS, name)).convert('RGB')
    g = np.asarray(im.convert('L'), dtype=np.float32)
    # vertical edges restricted to rows 300..1150 (board zone)
    zone = g[300:1150, :]
    ex = np.abs(np.diff(zone, axis=1)).mean(axis=0)
    # find local maxima spaced ~84px
    peaks = []
    for i in range(2, len(ex)-2):
        if ex[i] == max(ex[i-2:i+3]) and ex[i] > 8:
            peaks.append(i)
    # cluster peaks that are within 4px
    clustered = []
    for p in peaks:
        if clustered and p - clustered[-1][-1] <= 4:
            clustered[-1].append(p)
        else:
            clustered.append([p])
    centers = [int(np.mean(c)) for c in clustered]
    # keep those forming ~84px ladder
    print(f'--- {tag}: vertical-edge centers in board zone:', centers)
    # horizontal edges restricted to cols 150..570
    zone2 = g[:, 150:570]
    ey = np.abs(np.diff(zone2, axis=0)).mean(axis=1)
    hpeaks = []
    for i in range(2, len(ey)-2):
        if ey[i] == max(ey[i-2:i+3]) and ey[i] > 8:
            hpeaks.append(i)
    hc = []
    for p in hpeaks:
        if hc and p - hc[-1][-1] <= 4:
            hc[-1].append(p)
        else:
            hc.append([p])
    hcenters = [int(np.mean(c)) for c in hc]
    print(f'--- {tag}: horizontal-edge centers:', hcenters)
    return im, centers, hcenters

for n, t in [('01_main_classic.png','main'), ('02_skin0.png','skin0'),
             ('03_skin1.png','skin1'), ('04_skin2.png','skin2'),
             ('05_skin3.png','skin3'), ('06_full.png','full'),
             ('07_clear.png','clear')]:
    bands(n, t)
