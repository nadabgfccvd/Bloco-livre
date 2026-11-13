from PIL import Image
import numpy as np

base='/home/z/my-project/critic_shots/r3/'
a=np.array(Image.open(base+'02_skin0.png').convert('RGB')).astype(int)
# Right piece = 1x5 vertical? bbox 168 wide x 167 tall. ASCII at row=510..690 showed only ~60 cols wide (x510-570) used. Check full width.
def chr_for(px):
    P=[((24,32,46),'.'),((129,199,132),'g'),((179,221,181),'L'),((70,109,72),'d'),((143,163,191),'x')]
    return min(P,key=lambda c:sum((int(px[i])-c[0][i])**2 for i in range(3)))[1]
# Check x range 510-690 fully:
green=(np.abs(a-np.array([129,199,132])).sum(2)<80)|(np.abs(a-np.array([179,221,181])).sum(2)<80)|(np.abs(a-np.array([70,109,72])).sum(2)<80)
sub=green[900:1110,:]
xs=np.nonzero(sub.any(0))[0]
print('green piece columns:',xs.min(),xs.max())
# Count vertical green runs at various x
for x in [520,540,560,600,640,670]:
    col=sub[:,x]
    runs=[];s=None
    for i,v in enumerate(col):
        if v and s is None: s=i
        if not v and s is not None:
            if i-s>5: runs.append((900+s,900+i))
            s=None
    if s is not None: runs.append((900+s,900+len(col)))
    print(f'x={x}: green runs {runs}')
