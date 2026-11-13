from PIL import Image
import numpy as np

base='/home/z/my-project/critic_shots/r3/'
a=np.array(Image.open(base+'02_skin0.png').convert('RGB')).astype(int)
# Grid: cells start x=26 (col0). pitch=84? col runs: 26-102,110-187,195-271,280-356,364-440,449-525,533-610,618-694
colx=[(26,102),(110,187),(195,271),(280,356),(364,440),(449,525),(533,610),(618,694)]
# rows: from vertical gutter runs at x180: cell rows 193-267(?), let's derive: gutter runs (100,180)?? that's odd.
# vertical gutter runs at x180 y: 100-180 is long (top region), 193-211 partial... rows likely: 193-266, 280-352, 364-436, 449-522, 533-605, 618-690, 703-773, 787-833?
rowy=[(193,267),(281,352),(365,436),(449,522),(533,605),(618,690),(703,774),(787,833)]
# Actually simpler: sample centers
print('col x-center means and parity:')
vals=[]
for j,(x0,x1) in enumerate(colx):
    for i,(y0,y1) in enumerate(rowy):
        cx=(x0+x1)//2; cy=(y0+y1)//2
        patch=a[cy-12:cy+12,cx-12:cx+12].reshape(-1,3).mean(0)
        vals.append(((i,j),patch))
# print grid of means
for i in range(8):
    row=[]
    for j in range(8):
        v=[p for (ii,jj),p in vals if ii==i and jj==j][0]
        row.append(f'({v[0]:5.1f},{v[1]:5.1f},{v[2]:5.1f})')
    print(f'row{i}: '+' '.join(row))
