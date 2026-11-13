from PIL import Image
import numpy as np

base='/home/z/my-project/critic_shots/r3/'
for name in ['01_main_classic.png','02_skin0.png','03_skin1.png','04_skin2.png','05_skin3.png','06_full.png','07_clear.png']:
    a=np.array(Image.open(base+name).convert('RGB')).astype(int)
    sub=a[100:950,100:700]
    rs=sub.std(axis=(1,2))
    run=0;best=0;start=0
    for i,v in enumerate(rs):
        if v>2: run+=1
        if run>best: best=run; start=i-run+1
        if v<=2: run=0
    print(f'{name}: texture run y{100+start}..{100+start+best}')
    y1=100+start; y2=100+start+best
    band=a[y1:y2, 60:720]
    cm=band.mean(axis=(0,2))
    grad=np.abs(np.diff(cm))
    edges=[60+x for x in range(1,len(grad)) if grad[x]>2.5 and grad[x]>=grad[max(0,x-4):min(len(grad),x+5)].max()]
    print('   col edges:',edges)
    # row edges similar
    rm=band.mean(axis=(1,2))
    g2=np.abs(np.diff(rm))
    redges=[y1+x for x in range(1,len(g2)) if g2[x]>2.5 and g2[x]>=g2[max(0,x-4):min(len(g2),x+5)].max()]
    print('   row edges:',redges)
