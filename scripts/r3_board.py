from PIL import Image
import numpy as np

base='/home/z/my-project/critic_shots/r3/'
im=Image.open(base+'01_main_classic.png').convert('RGB')
a=np.array(im).astype(int)

# Column profile in board middle rows (y400-500) to find grid lines / cell pitch
seg=a[400:800]
colmean=seg.mean(axis=(0,2))  # per-column mean over those rows
colstd=seg.std(axis=(0,2))
# print local minima pattern every ~10px
xs=np.arange(720)
# detect pitch via autocorrelation of column means
cm=colmean-colmean.mean()
ac=np.correlate(cm,cm,'full')[719:]
peak=np.argmax(ac[40:120])+40
print('col autocorr peak lag (cell pitch?):',peak)
rm=None
seg2=a[:,200:600]
rowmean=seg2.mean(axis=(1,2))
r2=rowmean-rowmean.mean()
ac2=np.correlate(r2,r2,'full')[1439:]
peak2=np.argmax(ac2[40:120])+40
print('row autocorr peak lag:',peak2)

# Column band edges: gradient of column means
grad=np.abs(np.diff(colmean))
edges=[x for x in range(1,719) if grad[x]>3 and grad[x]>=grad[max(0,x-3):x+4].max()]
print('strong col edges:',edges[:40])
