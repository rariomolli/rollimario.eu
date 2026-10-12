import numpy as np, sys
f='/mnt/user-data/uploads/Scan_0_segmented_subsampled.ply'
dt=np.dtype([('x','<f4'),('y','<f4'),('z','<f4'),('r','u1'),('g','u1'),('b','u1'),('i','<f4')])
off=open(f,'rb').read(1000).index(b'end_header\n')+11
a=np.memmap(f,dtype=dt,mode='r',offset=off)
CX,CY,R=float(sys.argv[1]),float(sys.argv[2]),float(sys.argv[3]);TARGET=int(sys.argv[4])
P=[];L=[]
for s in range(0,len(a),1000000):
    c=np.array(a[s:s+1000000])
    m=(np.hypot(c['x']-CX,c['y']-CY)<R)&(c['z']<16)&(c['z']>-3)
    c=c[m]
    P.append(np.stack([c['x']-CX,c['y']-CY,c['z']],1)); L.append((0.299*c['r']+0.587*c['g']+0.114*c['b'])/255)
P=np.concatenate(P);L=np.concatenate(L).astype(np.float32)
print('cropped',len(P))
def thin(v):
    k=np.floor(P/v).astype(np.int64); k-=k.min(0)
    key=(k[:,0]*100003+k[:,1])*100003+k[:,2]
    _,idx=np.unique(key,return_index=True); return idx
lo,hi=0.005,2.0
for _ in range(16):
    mid=(lo*hi)**.5; n=len(thin(mid))
    if n>TARGET: lo=mid
    else: hi=mid
idx=thin(hi); print('voxel',hi,'n',len(idx))
np.savez('cloud2_thin.npz',P=P[idx],L=L[idx],v=hi)
