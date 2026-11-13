from PIL import Image
import numpy as np

base='/home/z/my-project/critic_shots/r3/'
im=Image.open(base+'01_main_classic.png').convert('RGB')
a=np.array(im).astype(int)

# Fine per-row profile around suspected regions
def rowprof(y0,y1,label):
    print(f'--- {label} y{y0}-{y1} ---')
    for y in range(y0,y1,8):
        r=a[y]
        m=r.mean(0); s=r.std(0)
        print(f'y{y:4d} mean=({m[0]:5.1f},{m[1]:5.1f},{m[2]:5.1f}) std=({s[0]:4.1f},{s[1]:4.1f},{s[2]:4.1f})')

rowprof(850,900,'board->? transition')
rowprof(1080,1300,'claimed streak strip zone')
