from PIL import Image
import numpy as np

base='/home/z/my-project/critic_shots/r3/'
a=np.array(Image.open(base+'07_clear.png').convert('RGB')).astype(int)
# Celebration: look for gold clusters anywhere OUTSIDE the board cell area (board region x24-696 y190-835 but exclude cells? stars may overlay board)
# First: full-image gold mask
gold=(a[:,:,0]>200)&(a[:,:,1]>150)&(a[:,:,2]<180)
ys,xs=np.nonzero(gold)
print('total gold px:',len(ys))
# Where are they? histogram by y-band
for y0 in range(0,1440,80):
    m=(ys>=y0)&(ys<y0+80)
    if m.sum()>50: print(f'  y{y0}-{y0+80}: {m.sum()} gold px, x range {xs[m].min()}-{xs[m].max()}')
# confetti: many small bright color clusters across screen. Sample colors present in top region y0-190
print()
print('color census y0-190 (excluding bg):')
sub=a[0:190].reshape(-1,3)
u,counts=np.unique(sub,axis=0,return_counts=True)
for c,n in zip(u,counts):
    if n>200 and c.sum()>150: print(f'  color=({c[0]},{c[1]},{c[2]}) n={n}')
