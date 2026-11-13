from PIL import Image
import numpy as np

base='/home/z/my-project/critic_shots/r3/'
a=np.array(Image.open(base+'02_skin0.png').convert('RGB')).astype(int)

# vertical scanline x=650 (inside empty cell col 8) from 180 to 860
x=650
col=a[:,x]
print(f'--- vertical scanline x={x}, y=180..870, runs (change>6) ---')
prev=None;start=180
for y in range(180,880):
    t=tuple(col[y])
    if prev is None: prev=t; continue
    if max(abs(t[i]-prev[i]) for i in range(3))>6:
        print(f'  y{start:3d}-{y:3d} len={y-start:3d} rgb={tuple(int(v) for v in col[start])}')
        start=y; prev=t
print(f'  y{start:3d}-880 rgb={tuple(int(v) for v in col[start])}')

# Horizontal scanlines at several rows to map empty vs occupied cells across board
print()
for y in [230,315,400,485,570,655,740,825]:
    row=a[y]
    # sample color at cell centers: cell i center = 24+85*i+36
    cells=[]
    for i in range(8):
        cx=24+85*i+36
        m=row[cx-10:cx+10]
        cells.append(tuple(int(v) for v in m.mean(0)))
    print(f'y={y:3d} cell centers: {cells}')
