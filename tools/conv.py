import numpy as np, base64, json, sys
f='/mnt/user-data/uploads/forest_day_13mio_clean_3.ply'
dt=np.dtype([('x','<f4'),('y','<f4'),('z','<f4'),('r','u1'),('g','u1'),('b','u1'),('i','<f4')])
off=open(f,'rb').read(1000).index(b'end_header\n')+11
a=np.memmap(f,dtype=dt,mode='r',offset=off)
RMAX=float(sys.argv[1]) if len(sys.argv)>1 else 14; ZMAX=17; TARGET=int(sys.argv[2]) if len(sys.argv)>2 else 300000
P=[];L=[]
for s in range(0,len(a),1000000):
    c=np.array(a[s:s+1000000])
    m=(np.hypot(c['x'],c['y'])<RMAX)&(c['z']<ZMAX)&(c['z']>-3)
    c=c[m]
    P.append(np.stack([c['x'],c['y'],c['z']],1)); L.append((0.299*c['r']+0.587*c['g']+0.114*c['b'])/255)
P=np.concatenate(P);L=np.concatenate(L).astype(np.float32)
print('cropped',len(P))
def thin(v):
    k=np.floor(P/v).astype(np.int64); k-=k.min(0)
    key=(k[:,0]*100003+k[:,1])*100003+k[:,2]
    _,idx=np.unique(key,return_index=True); return idx
lo,hi=0.01,1.0
for _ in range(14):
    mid=(lo*hi)**.5; n=len(thin(mid))
    if n>TARGET: lo=mid
    else: hi=mid
idx=thin(hi); print('voxel',hi,'n',len(idx))
P=P[idx];L=L[idx]
np.savez('cloud_thin.npz',P=P,L=L,v=hi)
