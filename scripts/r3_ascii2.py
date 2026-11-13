from PIL import Image
import numpy as np

base='/home/z/my-project/critic_shots/r3/'
def chr_for(px):
    P=[((13,19,31),'.'),((20,21,33),'_'),((31,36,52),'-'),((24,32,46),' '),
       ((31,40,56),':'),((41,52,73),':'),((50,64,90),'w'),((63,73,93),'W'),
       ((255,183,77),'G'),((229,115,115),'R'),((186,104,200),'P'),
       ((77,182,172),'T'),((129,199,132),'g'),((79,195,247),'B'),
       ((255,213,79),'*'),((254,212,79),'*')]
    return min(P,key=lambda c:sum((int(px[i])-c[0][i])**2 for i in range(3)))[1]
def render(name,x0,y0,x1,y1,sx,sy,title=''):
    a=np.array(Image.open(base+name).convert('RGB')).astype(int)
    print(f'### {title or name} x{x0}-{x1} y{y0}-{y1} ###')
    for y in range(y0,y1,sy):
        print(''.join(chr_for(a[y:y+sy,x:x+sx].reshape(-1,3).mean(0)) for x in range(x0,x1,sx)))
    print()

# Empty cell macro: 2x2 cells at board top-left (row0-1, col0-1) region x24-190 y193-360
render('02_skin0.png',24,190,190,360,3,3,'EMPTY CELL MACRO skin0 (col0-1,row0-1)')
