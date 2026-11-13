#!/usr/bin/env python3
"""R6 forensic step 2: precise board bounds via rail-run detection."""
import os
import numpy as np
from PIL import Image

SHOTS = '/home/z/my-project/critic_shots/r6'

def gray(n):
    return np.asarray(Image.open(os.path.join(SHOTS, n)).convert('L'), dtype=np.int32)

def find_vertical_rail(g, x_hint, half=3):
    """Refine a vertical rail x by maximizing |d/dx| summed over middle rows."""
    best_x, best_s = x_hint, -1
    for x in range(x_hint - half, x_hint + half + 1):
        s = np.abs(np.diff(g[300:1300, :], axis=1))[:, x-1].sum() if x > 0 else 0
        if s > best_s:
            best_s, best_x = s, x
    return best_x

def rail_vertical_extent(g, x, tag):
    """Given a rail column x, find the run of rows where col x-1..x+2 differ from bg."""
    col = g[:, x]
    # background is dark; rail is lighter -> find contiguous run where col > bg + margin
    bg = np.median(col[:250])
    run = col > bg + 12
    # longest run
    best = (0, 0)
    cur = None
    for i, v in enumerate(run):
        if v and cur is None:
            cur = i
        elif not v and cur is not None:
            if i - cur > best[1] - best[0]:
                best = (cur, i)
            cur = None
    if cur is not None and len(run) - cur > best[1] - best[0]:
        best = (cur, len(run))
    print(f'{tag}: rail x={x} bg={bg} vertical run y {best[0]}..{best[1]} len={best[1]-best[0]}')
    return best

for n in ['02_skin0.png', '01_main_classic.png', '06_full.png', '07_clear.png']:
    g = gray(n)
    lx = find_vertical_rail(g, 185)
    rx = find_vertical_rail(g, 608)
    rail_vertical_extent(g, lx, f'{n} LEFT')
    rail_vertical_extent(g, rx, f'{n} RIGHT')
    # horizontal rails: rows where diff along y is strong across board width
    rowmag = np.abs(np.diff(g[:, lx+8:rx-8], axis=0)).sum(axis=1)
    idx = sorted(np.argsort(rowmag)[::-1][:10].tolist())
    print(f'{n}: top horizontal edges (y, strength):', [(r, int(rowmag[r])) for r in idx])
    print()
