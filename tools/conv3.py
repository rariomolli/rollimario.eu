import numpy as np
f='screen3.ply'
dt=np.dtype([('x','<f4'),('y','<f4'),('z','<f4'),('nx','<f4'),('ny','<f4'),('nz','<f4')])
off=open(f,'rb').read(1000).index(b'end_header\n')+11
a=np.array(np.memmap(f,dtype=dt,mode='r',offset=off))
P=np.stack([a['x'].astype(np.float64),a['y'].astype(np.float64),a['z'].astype(np.float64)],1)
P-=np.array([22700.,-4170.,2150.])
nz=np.abs(a['nz'])
def thin(v):
    k=np.floor(P/v).astype(np.int64);k-=k.min(0)
    key=(k[:,0]*100003+k[:,1])*100003+k[:,2]
    _,idx=np.unique(key,return_index=True);return idx
lo,hi=1.,200.
for _ in range(18):
    mid=(lo*hi)**.5;n=len(thin(mid))
    if n>300000:lo=mid
    else:hi=mid
idx=thin(hi);print('voxel',hi,len(idx))
np.savez('cloud3_thin.npz',P=P[idx],nz=nz[idx])
