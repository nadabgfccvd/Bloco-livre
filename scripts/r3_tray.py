from PIL import Image
import numpy as np

base='/home/z/my-project/critic_shots/r3/'
for name in ['02_skin0.png','06_full.png']:
    a=np.array(Image.open(base+name).convert('RGB')).astype(int)
    print(f'=== {name} tray zone y880-1120: column profile of non-bg ===')
    zone=a[880:1120]
    # bg = (13,19,31)/(20,21,33)? tray bg appears (24,32,46)-ish. Detect non-dark pixels
    bright=(zone.sum(2)>200)
    colh=bright.sum(0)
    runs=[];s=None
    for i,v in enumerate(colh):
        if v>3 and s is None: s=i
        if v<=3 and s is not None:
            if i-s>10: runs.append((s,i))
            s=None
    print('piece x-runs:',runs)
    for x0,x1 in runs:
        sub=bright[:,x0:x1]
        ys=np.nonzero(sub.any(1))[0]
        print(f'  piece x{x0}-{x1} (w={x1-x0}) rows y{880+ys.min()}-{880+ys.max()} h={ys.max()-ys.min()+1}')
    # colors
    for x0,x1 in runs:
        sub=zone[:,x0:x1]
        m=sub.reshape(-1,3).mean(0)
        print(f'  piece x{x0}-{x1} mean color=({m[0]:.0f},{m[1]:.0f},{m[2]:.0f})')
