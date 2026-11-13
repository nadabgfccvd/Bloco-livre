from PIL import Image
import numpy as np

base='/home/z/my-project/critic_shots/r3/'
for name in ['02_skin0.png','03_skin1.png','04_skin2.png','05_skin3.png','01_main_classic.png','06_full.png','07_clear.png']:
    a=np.array(Image.open(base+name).convert('RGB')).astype(int)
    # Board background vs page bg: board bg is a distinct box. Find rows where the middle columns (200-520) are uniform but different from page
    # Scan for the board: look at column range 100-700 for a large rect with texture std>3 vs flat rows above/below
    # find row band y100-900: compute row std limited to x100-700
    sub=a[100:950,100:700]
    rs=sub.std(axis=(1,2))
    # board rows should have texture (grid lines). find longest run of rs>2
    run=0;best=0;start=0
    for i,v in enumerate(rs):
        if v>2: run+=1
        if run>best: best=run; start=i-run+1
        if v<=2: run=0
    print(f'{name}: board texture run y{100+start}..{100+start+best} len={best}')
    # column edges detection inside that band
    band=a[100+start:100+start+best, 60:720]
    cm=band.mean(axis=(0,2))
    grad=np.abs(np.diff(cm))
    edges=[60+x for x in range(1,660) if grad[x]>2.5 and grad[x]>=grad[max(0,x-4):x+5].max()]
    print('   col edges:',edges)
