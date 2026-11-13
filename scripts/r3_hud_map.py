from PIL import Image
import numpy as np

base='/home/z/my-project/critic_shots/r3/'
a=np.array(Image.open(base+'02_skin0.png').convert('RGB')).astype(int)
print('=== HUD y0-170: object map by scanning rows for non-bg runs ===')
bg=np.array([13,19,31])
for y in range(0,170,4):
    row=a[y]
    d=np.abs(row-bg).sum(1)
    nz=np.nonzero(d>40)[0]
    if len(nz):
        # group
        groups=[];s=nz[0];p=nz[0]
        for x in nz[1:]:
            if x-p>6: groups.append((s,p)); s=x
            p=x
        groups.append((s,p))
        print(f'y{y:3d}: {groups}')
