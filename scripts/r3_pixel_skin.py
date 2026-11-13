from PIL import Image
import numpy as np

base='/home/z/my-project/critic_shots/r3/'
a=np.array(Image.open(base+'05_skin3.png').convert('RGB')).astype(int)
# Claim: empty cells gray #4A4E58=(74,78,88), hue-neutral; non-AA hard edges; 2-tone hard ramp.
# Measure empty cell colors in skin3: from earlier cell map at y centers we saw parity (64,67,76)/(77,81,91)?? That was my old wrong geometry.
colx=[(26,102),(110,187),(195,271),(280,356),(364,440),(449,525),(533,610),(618,694)]
rowy=[(193,267),(281,352),(365,436),(449,522),(533,605),(618,690),(703,774),(787,833)]
print('skin3 cell center colors (12px patch):')
gr=[]
for j,(x0,x1) in enumerate(colx):
    row=[]
    for i,(y0,y1) in enumerate(rowy):
        cx=(x0+x1)//2; cy=(y0+y1)//2
        m=a[cy-12:cy+12,cx-12:cx+12].reshape(-1,3).mean(0)
        s=a[cy-12:cy+12,cx-12:cx+12].reshape(-1,3).std(0).mean()
        row.append((m,s))
        if m.mean()<95: gr.append(m)
    print(f'row{i}: '+' '.join(f'({m[0]:.0f},{m[1]:.0f},{m[2]:.0f})' for m,s in row))
g=np.array(gr)
print(f'\nempty-ish mean=({g[:,0].mean():.1f},{g[:,1].mean():.1f},{g[:,2].mean():.1f}) claim #4A4E58=(74,78,88)')
# Edge hardness: scan a horizontal line crossing an empty cell edge in skin3
# Take row y=230 (row0), x from 100 to 200
row=a[230,100:200]
print('\nskin3 row y230 x100-200 RGB:')
print([tuple(int(v) for v in row[x]) for x in range(0,100,4)])
# gradient analysis
grad=np.abs(np.diff(row.astype(float))).sum(1)
print('edge gradients (sum over 3ch):', [f'{x+100}:{grad[x]:.0f}' for x in range(0,99) if grad[x]>8])
# count AA (intermediate) pixels along the edge: between (24,32,46) bg and empty gray
