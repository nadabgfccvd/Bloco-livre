from PIL import Image
import numpy as np

base='/home/z/my-project/critic_shots/r3/'
a=np.array(Image.open(base+'02_skin0.png').convert('RGB')).astype(int)
# Right tray piece: x515-682, y921-1087, 168x167. Contains a 5x1 vertical? or 2 stacked pieces?
# from vscan x=550: green blocks y921-1085 continuous with gaps at y971-975,1024-1029 (horizontal seams)
# From hscan y925: green x520-568 only (top row) — so top part is 1 cell wide horizontally?? 
# Let's ASCII-render that region at fine scale.
def chr_for(px):
    P=[((24,32,46),'.'),((129,199,132),'g'),((179,221,181),'L'),((70,109,72),'d'),((143,163,191),'x'),((248,206,133),'s')]
    return min(P,key=lambda c:sum((int(px[i])-c[0][i])**2 for i in range(3)))[1]
for y in range(915,1095,7):
    print(''.join(chr_for(a[y,x]) for x in range(510,690,3)))
