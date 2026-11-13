from PIL import Image
import numpy as np

base='/home/z/my-project/critic_shots/r3/'
a=np.array(Image.open(base+'02_skin0.png').convert('RGB')).astype(int)

# PONTOS/RECORDE/numeral zones. From HUD map: left labels x24-119 (y108-168?), title x134-617, right x648-674.
# Dump vertical scanline at x=30 (label letters) to get cap/x heights
def vprofile(x, y0, y1, label, thr=90):
    col=a[y0:y1,x]
    bright=(col.sum(1)>thr*3)
    runs=[]
    s=None
    for i,v in enumerate(bright):
        if v and s is None: s=i
        if not v and s is not None:
            if i-s>=2: runs.append((y0+s,y0+i-1))
            s=None
    if s is not None: runs.append((y0+s,y0+len(bright)-1))
    print(f'{label} x={x}: runs {runs}')

# left labels around x=30,60,90 (PONTOS / RECORDE?)
for x in [28,30,45,52,68,85,100,110]:
    vprofile(x,105,175,f'label')

# right zone x648-674 (probably home button icon?) check colors
print()
print('right zone y=124-152 sample colors:')
for y in range(124,156,4):
    print(f'  y={y}: x648={tuple(a[y,648])} x660={tuple(a[y,660])} x670={tuple(a[y,670])} x674={tuple(a[y,674])}')
