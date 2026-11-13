from PIL import Image
import numpy as np, sys

base='/home/z/my-project/critic_shots/r3/'
PALETTE=[
 ((13,19,31),'.'),((20,21,33),'_'),((31,36,52),'-'),
 ((24,32,46),' '),  # board bg
 ((31,40,56),':'),((41,52,73),':'),((50,64,90),'w'),((63,73,93),'W'),  # wells
 ((255,183,77),'G'),((229,115,115),'R'),((186,104,200),'P'),  # gold/red/purple blocks
 ((77,182,172),'T'),((129,199,132),'g'),((79,195,247),'B'),  # teal/green/blue
 ((255,213,79),'*'),  # star gold / trophy
]
def chr_for(px):
    best=None;bd=1e9
    for c,ch in PALETTE:
        d=sum((int(px[i])-c[i])**2 for i in range(3))
        if d<bd: bd=d;best=ch
    return best

def render(name,x0,y0,x1,y1,sx,sy):
    im=Image.open(base+name).convert('RGB')
    a=np.array(im).astype(int)
    print(f'### {name} region x{x0}-{x1} y{y0}-{y1} scale {sx}x{sy} ###')
    for y in range(y0,y1,sy):
        line=''
        for x in range(x0,x1,sx):
            block=a[y:y+sy,x:x+sx].reshape(-1,3).mean(0)
            line+=chr_for(block)
        print(line)
    print()

if __name__=='__main__':
    args=sys.argv[1:]
    name=args[0]; regs=[int(v) for v in args[1:9]] if len(args)>=9 else None
    if regs: render(name,*regs)
    else: render(name,0,0,720,1440,8,16)
