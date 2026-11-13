from PIL import Image
import numpy as np

base='/home/z/my-project/critic_shots/r3/'
a=np.array(Image.open(base+'02_skin0.png').convert('RGB')).astype(int)
# Verify 8x8: count distinct cell boxes. Horizontal cell x-starts from scanline y600: 112,197,282,366,451,536,620 → 7 cells + we need 8.
# Vertical cell y-starts: 193(?),280,364,449,533,618,703,787 → 8 rows.
# Check row 0 y 193-270: is it a cell row or gutter?
print('row0 y200 sample colors at cell centers x150,233,318,402,486,571,655:')
for x in [150,233,318,402,486,571,655]:
    print(f'  x={x}: y200={tuple(a[200,x])} y210={tuple(a[210,x])} y240={tuple(a[240,x])}')
# And count total cells: sample the full board at 40px steps, count "cell" (bright well) rectangles
iswell=~(np.abs(a-np.array([24,32,46])).sum(2)<30)
zone=iswell[190:835,100:700]
colprof=zone.mean(0)
# find cell columns (contiguous bright)
runs=[];s=None
for i,v in enumerate(colprof>0.3):
    if v and s is None: s=i
    if not v and s is not None:
        if i-s>=20: runs.append((100+s,100+i))
        s=None
print('cell column runs (width>=20):',runs)
