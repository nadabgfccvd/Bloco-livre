from PIL import Image
import numpy as np

base='/home/z/my-project/critic_shots/r3/'
a=np.array(Image.open(base+'02_skin0.png').convert('RGB')).astype(int)
print('=== left edge x=0-26 (full page) vertical extent of gold/red run ===')
# For every row 0-1440, check if x27-101 contains gold (255,183,77) or red (229,115,115)
gold=(a[:,27:101,0]>230)&(a[:,27:101,1]>150)&(a[:,27:101,2]<120)
red=(a[:,27:101,0]>200)&(a[:,27:101,1]<170)&(a[:,27:101,2]<170)&(a[:,27:101,1]>80)
g_rows=np.nonzero(gold.any(1))[0]
r_rows=np.nonzero(red.any(1))[0]
def runs_of(rows):
    if len(rows)==0: return []
    out=[];s=rows[0];p=rows[0]
    for r in rows[1:]:
        if r-p>4: out.append((s,p)); s=r
        p=r
    out.append((s,p)); return out
print('gold rows runs:',runs_of(g_rows))
print('red rows runs:',runs_of(r_rows))
# same on right side x=696-720 — but right side shows page bg (31,36,52). Check gold there
gold2=(a[:,697:720,0]>230)&(a[:,697:720,1]>150)&(a[:,697:720,2]<120)
g2=np.nonzero(gold2.any(1))[0]
print('right-side gold rows runs:',runs_of(g2))
