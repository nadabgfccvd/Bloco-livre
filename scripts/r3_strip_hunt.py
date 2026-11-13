from PIL import Image
import numpy as np, glob, os

base='/home/z/my-project/critic_shots/r3/'
for name in ['01_main_classic.png','03_skin1.png','05_skin3.png','06_full.png','07_clear.png']:
    a=np.array(Image.open(base+name).convert('RGB')).astype(int)
    print(f'=== {name} y1240-1400 fine profile ===')
    for y in range(1240,1400,6):
        r=a[y]; m=r.mean(0); s=r.std(0)
        print(f'  y{y:4d} mean=({m[0]:5.1f},{m[1]:5.1f},{m[2]:5.1f}) std=({s[0]:4.1f},{s[1]:4.1f},{s[2]:4.1f})')
