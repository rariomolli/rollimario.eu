import re,numpy as np,base64,sys
sys.setrecursionlimit(10000)
rng=np.random.default_rng(11)
n=250000
def wt(L,G=1.6):
    lo,hi=np.percentile(L,[2,98]);t=np.clip((L-lo)/(hi-lo),0,1);return (0.3+0.7*(1-t)**G).astype(np.float32)
def sub(P,w,k):
    i=np.sort(rng.choice(len(P),k,replace=False));return P[i],w[i]
def fill(P,w,k,jit):   # pad to k with jittered duplicates
    if len(P)>=k:return sub(P,w,k)
    ex=rng.choice(len(P),k-len(P),replace=True)
    return np.concatenate([P,P[ex]+rng.normal(0,jit,(len(ex),3)).astype(np.float32)]),np.concatenate([w,w[ex]])
# A forest
d=np.load('cloud_thin.npz');P=d['P'];L=d['L']
A=np.stack([P[:,0]*.32,(P[:,2]-6.3)*.32,P[:,1]*.32],1).astype(np.float32);A,wA=sub(A,wt(L),n)
# B scan
d=np.load('cloud2_thin.npz');P=d['P'];L=d['L']
B=np.stack([P[:,0]*.15,(P[:,2]-1.5)*.15,P[:,1]*.15],1).astype(np.float32);B,wB=sub(B,wt(L),n)
# C frame: sparse (about 40% visible), slightly frayed, rest invisible duplicates
d=np.load('cloud3_thin.npz');P=d['P'];nz=d['nz']
C0=(np.stack([P[:,0],P[:,2],P[:,1]],1)*.0011).astype(np.float32);w0=(0.55+0.45*(1-nz)).astype(np.float32)
C0,w0=sub(C0,w0,100000)
C0=C0+rng.normal(0,.016,C0.shape).astype(np.float32)
fr=rng.random(len(C0))<.05
dirs=rng.normal(size=(fr.sum(),3));dirs/=np.linalg.norm(dirs,axis=1,keepdims=True)
C0[fr]+=(dirs*rng.exponential(.07,(fr.sum(),1))).astype(np.float32)
ex=rng.choice(len(C0),n-len(C0),replace=True)
C=np.concatenate([C0,C0[ex]+rng.normal(0,.01,(len(ex),3)).astype(np.float32)]);wC=np.concatenate([w0,np.zeros(len(ex),np.float32)])
# D car (smaller)
dt=np.dtype([('x','<f4'),('y','<f4'),('z','<f4'),('r','u1'),('g','u1'),('b','u1'),('i','<f4'),('o','<f4')])
off=open('car4.ply','rb').read(1000).index(b'end_header\n')+11
a=np.array(np.memmap('car4.ply',dtype=dt,mode='r',offset=off))
Lc=((0.299*a['r']+0.587*a['g']+0.114*a['b'])/255).astype(np.float32)
D=(np.stack([a['x']+72.,a['z']-0.15,a['y']-8.4],1)*1.9).astype(np.float32);D,wD=fill(D,wt(Lc),n,.009)
# E staircase
dt=np.dtype([('x','<f8'),('y','<f8'),('z','<f8'),('r','u1'),('g','u1'),('b','u1')])
off=open('stair.ply','rb').read(2000).index(b'end_header\n')+11
a=np.array(np.memmap('stair.ply',dtype=dt,mode='r',offset=off))
Ls=((0.299*a['r']+0.587*a['g']+0.114*a['b'])/255).astype(np.float32)
mx,my=(a['x'].min()+a['x'].max())/2,(a['y'].min()+a['y'].max())/2
E=(np.stack([a['x']-mx,a['z']-1.0,a['y']-my],1)*1.8).astype(np.float32);E,wE=sub(E,wt(Ls),n)
dch=np.load('church_model.npz');Pc=dch['P'].astype(np.float32);Wc=dch['W'].astype(np.float32)
G=np.stack([Pc[:,0]*.155,(Pc[:,1]-7.0)*.155,Pc[:,2]*.155],1).astype(np.float32);G,wG=sub(G,Wc,n)
print('ranges');[print(k,X.min(0).round(2),X.max(0).round(2)) for k,X in zip('ABCDE',[A,B,C,D,E])]
S=[A,B,C,D,E,G];W=[wA,wB,wC,wD,wE,wG];K=len(S)
outs=[[] for _ in S];axes=[1,0,2]
def rec(ids,d):
    if len(ids[0])<=6:
        for k in range(K):outs[k].append(ids[k])
        return
    ax=axes[d%3];nid=[ids[k][np.argsort(S[k][ids[k],ax],kind='stable')] for k in range(K)]
    m=len(nid[0])//2
    rec([x[:m] for x in nid],d+1);rec([x[m:] for x in nid],d+1)
rec([np.arange(n)]*K,0)
O=[np.concatenate(o) for o in outs]
S=[S[k][O[k]] for k in range(K)];W=[W[k][O[k]] for k in range(K)]
SC=4000.
q=lambda v:np.clip(np.round(v*SC),-32767,32767).astype('<i2')
enc=lambda P,w:base64.b64encode(q(P[:,0]).tobytes()+q(P[:,1]).tobytes()+q(P[:,2]).tobytes()+np.round(w*255).astype('u1').tobytes()).decode()
B64=[enc(S[k],W[k]) for k in range(K)]
import json;json.dump({'n':n,'b':B64[5]},open('/mnt/user-data/outputs/p/st-mauritius/church-cloud.json','w'))
B64=B64[:5];K=5
p='/mnt/user-data/outputs/portfolio-demo.html'
s=open(p,encoding='utf-8').read()
m=re.search(r"const CL=mk\('([^']*)',(\d+)\),CB=mk\('([^']*)',(\d+)\),CC=mk\('([^']*)',(\d+)\),CD=mk\('([^']*)',(\d+)\),CE=mk\('([^']*)',(\d+)\),CS=\[CL,CB,CC,CD,CE\];",s);assert m
nm=['CL','CB','CC','CD','CE']
s=s[:m.start()]+','.join(f"{nm[k]}=mk('{B64[k]}',{n})" for k in range(K)).join(['const ',f",CS=[{','.join(nm)}];"])+s[m.end():]
open(p,'w',encoding='utf-8').write(s);print(len(s)/1e6,'MB')
