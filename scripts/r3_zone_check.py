from PIL import Image
import numpy as np, glob, os

base='/home/z/my-project/critic_shots/r3/'
files=sorted(glob.glob(base+'*.png'))
print('=== y1120-1285 zone (claimed streak strip) per screenshot ===')
for f in files:
    a=np.array(Image.open(f).convert('RGB')).astype(int)
    z=a[1120:1286]
    m=z.reshape(-1,3).mean(0); s=z.reshape(-1,3).std(0)
    # count distinct colors
    cols={}
    for px in z.reshape(-1,3)[::37]:
        t=tuple(px)
        cols[t]=cols.get(t,0)+1
    print(f'{os.path.basename(f):22s} mean=({m[0]:5.1f},{m[1]:5.1f},{m[2]:5.1f}) std=({s[0]:5.1f},{s[1]:5.1f},{s[2]:5.1f}) distinct~{len(cols)}')
print()
print('=== full-row occupancy: which rows have std>5 (content) in each shot ===')
for f in files:
    a=np.array(Image.open(f).convert('RGB')).astype(int)
    rows=a.std(axis=(1,2))
    # find contiguous content bands
    content=rows>5
    bands=[]; y=0
    while y<1440:
        if content[y]:
            y2=y
            while y2<1440 and content[y2]: y2+=1
            if y2-y>8: bands.append((y,y2))
            y=y2
        else: y+=1
    print(f'{os.path.basename(f):22s} bands: {bands}')
