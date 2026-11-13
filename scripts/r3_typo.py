from PIL import Image
import numpy as np

base='/home/z/my-project/critic_shots/r3/'
a=np.array(Image.open(base+'02_skin0.png').convert('RGB')).astype(int)

def wordbox(y0,y1,label):
    # get letter-height profile in band
    band=a[y0:y1]
    txt=(band.sum(2)>150)  # bright text
    cols=np.nonzero(txt.any(0))[0]
    rows=np.nonzero(txt.any(1))[0]
    print(f'{label}: y{y0+rows.min()}-{y0+rows.max()} height={rows.max()-rows.min()+1}')
    return cols,rows

# PONTOS label and numerals: the score bar y108-168. find its sub-bands
# scanline-ish: identify dark-bright structure. Sample y120 row colors at x=530-620 (numeral zone)
print('=== score bar macro: horizontal runs at y=125, y=140, y=150 (x100-700) ===')
for y in [110,120,125,130,140,150,160]:
    row=a[y,100:700]
    runs=[];prev=None;start=0
    for i in range(600):
        t=tuple(row[i])
        if prev is None: prev=t;continue
        if max(abs(t[j]-prev[j]) for j in range(3))>25:
            runs.append((100+start,100+i,tuple(int(v) for v in row[100+start])))
            start=i;prev=t
    runs.append((100+start,700,tuple(int(v) for v in row[100+start])))
    print(f'y={y}: {runs[:14]}')
