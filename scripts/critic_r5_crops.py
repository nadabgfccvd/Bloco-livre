#!/usr/bin/env python3
"""R5 art-director forensic crops + measurements for Bloco Livre.

Writes crops to /tmp/critic_crops_r5/ and prints a forensic report so the
critic can verify the builder's 7 numbered claims from pixel data.
"""
import os
from PIL import Image
import numpy as np

SHOTS = '/home/z/my-project/critic_shots/r5'
CROPS = '/tmp/critic_crops_r5'
os.makedirs(CROPS, exist_ok=True)

def load(name):
    return Image.open(os.path.join(SHOTS, name)).convert('RGB')

def save_crop(im, box, fname):
    c = im.crop(box)
    c.save(os.path.join(CROPS, fname))
    return c

def a(crop):
    return np.asarray(crop, dtype=np.int16)

# ---------------------------------------------------------------
# 1. Locate the board: find strongest vertical edges in each shot.
# ---------------------------------------------------------------
def find_board(im, tag):
    g = np.asarray(im.convert('L'), dtype=np.int16)
    # column-wise absolute difference to detect board side rails
    colstd = g.std(axis=0)
    top = g[:300].mean(axis=1)  # HUD luminance row profile
    print(f'--- {tag}: col-std top10 (x, std):',
          sorted(enumerate(colstd), key=lambda t: -t[1])[:10])
    return colstd

# quick overall stats per shot
def stats(tag, im):
    arr = np.asarray(im.convert('RGB'), dtype=np.int16)
    print(f'{tag}: mean RGB = {arr[...,0].mean():.1f} {arr[...,1].mean():.1f} {arr[...,2].mean():.1f}  '
          f'lum p1={np.percentile(arr.mean(axis=2),1):.0f} p50={np.percentile(arr.mean(axis=2),50):.0f} p99={np.percentile(arr.mean(axis=2),99):.0f}')

for name in ['01_main_classic.png','02_skin0.png','03_skin1.png','04_skin2.png','05_skin3.png','06_full.png','07_clear.png']:
    stats(name, load(name))
