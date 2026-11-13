#!/usr/bin/env python3
"""Halo layering CONFIRMED: distinct steps above board at y190->186->182->178:
(51,63,80) then (41,49,63) then (65,80,104) then (180,169,133) then (157,145,108) further up.
=> 3+ concentric layers (2 gold tones + interleaves). Below board: NO halo at all (lum 29) —
halo only wraps top/left/right, not below. Builder's 'halo outside 216px' is nonsense vs
69104 goldish px measured outside board (but note: much of that is the top fan, which may be
the rays/banner rather than halo).
Now finalize: PONTOS/RECORDE cap heights. Band y29..53 letters are 10 clusters x209..504 —
that's 'PONTOS' (6 letters) + 'RECORDE' (7 letters)? 10 letters? PONTOS=6, RECORDE=7 => 13 letters,
we have 10 clusters — some letters merged. Colors: white-ish (242,246,252) at band y29..53.
Second band y64..80 = digits (143,163,191).
The claim: PONTOS 0.24*cell=20.3px cap vs RECORDE 0.19*cell=16.1px cap.
Measured: BOTH at rows 29..53 => 25px raw incl. antialias; same height! But wait: claim says
PONTOS label bigger than RECORDE. Measure separately: PONTOS should be left group, RECORDE right.
Letter clusters x209..504 continuous: 10 clusters. 'PONTOS' letters: P O N T O S = 6 letters
' RECORDE' 7 letters: R E C O R D E. 6+7=13, clusters=10 because narrow letters merged (I-like).
Measure mean cluster height per letter over left vs right halves of the word zone.
"""
import sys
sys.path.insert(0, '/home/z/my-project/scripts')
from r6_forensics_lib import *

im = load('01_main_classic.png'); p = px(im)
clusters = [(209,226),(240,254),(265,286),(299,318),(330,352),(383,398),(410,412),(424,445),(458,476),(489,504)]
# find the gap that separates the two words: between (330,352) and (383,398) gap = 31px — biggest?
gaps = [clusters[i+1][0]-clusters[i][1] for i in range(len(clusters)-1)]
print('gaps:', gaps)
# letters heights (cap only, using bright threshold)
for (x0,x1) in clusters:
    ys = [y for y in range(25, 60) if any(p[x,y][0]>200 and p[x,y][1]>200 for x in range(x0,x1+1))]
    print(f'   letter x{x0}..{x1}: rows {ys[0]}..{ys[-1]} h={ys[-1]-ys[0]+1}')
