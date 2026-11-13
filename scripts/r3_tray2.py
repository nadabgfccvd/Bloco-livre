from PIL import Image
import numpy as np

base='/home/z/my-project/critic_shots/r3/'
for name in ['02_skin0.png','06_full.png']:
    a=np.array(Image.open(base+name).convert('RGB')).astype(int)
    print(f'=== {name} tray ASCII (y880-1120) ===')
    def chr_for(px):
        P=[((13,19,31),'.'),((20,21,33),'_'),((31,36,52),'-'),((24,32,46),' '),
           ((31,40,56),':'),((41,52,73),':'),((50,64,90),'w'),((63,73,93),'W'),
           ((255,183,77),'G'),((229,115,115),'R'),((186,104,200),'P'),
           ((77,182,172),'T'),((129,199,132),'g'),((79,195,247),'B'),((255,213,79),'*')]
        return min(P,key=lambda c:sum((int(px[i])-c[0][i])**2 for i in range(3)))[1]
    for y in range(880,1120,10):
        print(''.join(chr_for(a[y:y+10,x:x+8].reshape(-1,3).mean(0)) for x in range(0,720,8)))
    print()
