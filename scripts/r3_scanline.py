from PIL import Image
import numpy as np

base='/home/z/my-project/critic_shots/r3/'
a=np.array(Image.open(base+'02_skin0.png').convert('RGB')).astype(int)

# horizontal scanline through board middle (y=600)
y=600
row=a[y]
print(f'--- scanline y={y}, x=0..719 (print every px where change > 6) ---')
prev=None; runs=[]
start=0
for x in range(720):
    t=tuple(row[x])
    if prev is None: prev=t; start=0; continue
    if max(abs(t[i]-prev[i]) for i in range(3))>6:
        runs.append((start,x,tuple(int(v) for v in row[start])))
        start=x; prev=t
runs.append((start,720,tuple(int(v) for v in row[start])))
for s,e,c in runs: print(f'  x{s:3d}-{e:3d} len={e-s:3d} rgb={c}')
