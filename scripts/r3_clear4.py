from PIL import Image
import numpy as np

base='/home/z/my-project/critic_shots/r3/'
a=np.array(Image.open(base+'07_clear.png').convert('RGB')).astype(int)
def chr_for(px):
    P=[((13,19,31),'.'),((20,21,33),'_'),((31,36,52),'-'),((24,32,46),' '),((45,53,68),':'),
       ((50,64,90),'w'),((63,73,93),'W'),((255,183,77),'G'),((229,115,115),'R'),((186,104,200),'P'),
       ((77,182,172),'T'),((129,199,132),'g'),((79,195,247),'B'),((255,213,79),'*'),
       ((255,216,93),'*'),((243,247,252),'+'),((255,189,92),'*')]
    return min(P,key=lambda c:sum((int(px[i])-c[0][i])**2 for i in range(3)))[1]
# Top HUD + tray mid y0-190 and y1140-1440
print('=== TOP y0-190 ===')
for y in range(0,190,10):
    print(f'y{y:4d} '+''.join(chr_for(a[y:y+10,x:x+8].reshape(-1,3).mean(0)) for x in range(0,720,8)))
print('=== BOTTOM y1140-1440 ===')
for y in range(1140,1440,12):
    print(f'y{y:4d} '+''.join(chr_for(a[y:y+12,x:x+8].reshape(-1,3).mean(0)) for x in range(0,720,8)))
