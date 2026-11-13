from PIL import Image
import numpy as np

base='/home/z/my-project/critic_shots/r3/'
f='01_main_classic.png'
im=Image.open(base+f).convert('RGB')
a=np.array(im)
print('size',im.size)
# Row-band profile: mean color + std per 20px band
for y0 in range(0,1440,40):
    band=a[y0:y0+40]
    m=band.reshape(-1,3).mean(0)
    s=band.reshape(-1,3).std(0)
    print(f'y{y0:4d}-{y0+40:4d} mean=({m[0]:5.1f},{m[1]:5.1f},{m[2]:5.1f}) std=({s[0]:4.1f},{s[1]:4.1f},{s[2]:4.1f})')
