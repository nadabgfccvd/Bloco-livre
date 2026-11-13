from PIL import Image
import numpy as np

base='/home/z/my-project/critic_shots/r3/'
a=np.array(Image.open(base+'02_skin0.png').convert('RGB')).astype(int)
# The board panel spans x24-696 (w=672) but last column run stops at 694. Cell runs 7 with width ~76.
# Maybe 8th column exists but empty cells in col 8 have different color? At y=482 col8 (x620-689) WAS bright (50,64,90).
# Board inner starts x36? Panel x24-696. Try wider zone and lower threshold.
iswell=~(np.abs(a-np.array([24,32,46])).sum(2)<30)
zone=iswell[190:835,24:720]
colprof=zone.mean(0)
runs=[];s=None
for i,v in enumerate(colprof>0.15):
    if v and s is None: s=i
    if not v and s is not None:
        if i-s>=30: runs.append((24+s,24+i))
        s=None
print('cell col runs (thr .15, w>=30):',runs)
# Check the far right region x 694-710
print('x695-710 y482:',[tuple(a[482,x]) for x in range(693,712)])
