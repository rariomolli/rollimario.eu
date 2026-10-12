import numpy as np
rng=np.random.default_rng(3)
P=[];Wt=[]
def add(pts,w):
    P.append(np.asarray(pts,np.float64));Wt.append(np.full(len(pts),w,np.float32))
def rect(o,u,v,dens,w,noise=.015,fn=None):
    o,u,v=map(np.asarray,(o,u,v));A=np.linalg.norm(u)*np.linalg.norm(v);n=max(1,int(A*dens))
    a=rng.random((n,1));b=rng.random((n,1));p=o+a*u+b*v
    if fn is not None:p=fn(p)
    add(p+rng.normal(0,noise,p.shape),w)
def box(c,s,dens,w,faces='xXyYzZ'):
    c=np.asarray(c,float);s=np.asarray(s,float);h=s/2
    if 'x' in faces:rect(c+[-h[0],-h[1],-h[2]],[0,s[1],0],[0,0,s[2]],dens,w)
    if 'X' in faces:rect(c+[h[0],-h[1],-h[2]],[0,s[1],0],[0,0,s[2]],dens,w)
    if 'y' in faces:rect(c+[-h[0],-h[1],-h[2]],[s[0],0,0],[0,0,s[2]],dens,w)
    if 'Y' in faces:rect(c+[-h[0],h[1],-h[2]],[s[0],0,0],[0,0,s[2]],dens,w)
    if 'z' in faces:rect(c+[-h[0],-h[1],-h[2]],[s[0],0,0],[0,s[1],0],dens,w)
    if 'Z' in faces:rect(c+[-h[0],-h[1],h[2]],[s[0],0,0],[0,s[1],0],dens,w)
def line(a,b,dens,w,noise=.012):
    a,b=np.asarray(a,float),np.asarray(b,float);L=np.linalg.norm(b-a);n=max(2,int(L*dens))
    t=rng.random((n,1));p=a+t*(b-a);add(p+rng.normal(0,noise,p.shape),w)
# ---- dimensions (m), origin = hall centre at floor level; x right, y up, z towards viewer
CO=16.0;CW=1.75          # column outer face, column size (reference 1.75 m)
WO,WI=15.8,14.65         # tower wall outer / inner face
TX=13.95                 # textile plane
H_BEAM0,H_BEAM1=4.6,5.6
H_T0,H_T1=6.0,16.3       # textile
H_C=17.9;H_R=19.8;H_RT=20.2  # ceiling underside, coffer top, roof top
GRID=[-11.0,-6.6,-2.2,2.2,6.6,11.0]
# walls kept: -x and +z ; removed (cut): +x and -z
KEEP=[('x',-1),('z',1)]
def wallpts(axis,sgn,pos,y0,y1,dens,w,fn=None,span=None):
    a=span if span else pos
    if axis=='x':rect([sgn*pos,y0,-a],[0,y1-y0,0],[0,0,2*a],dens,w,fn=fn)
    else:rect([-a,y0,sgn*pos],[2*a,0,0],[0,y1-y0,0],dens,w,fn=fn)
# floor (light, model floor)
rect([-CO,0,-CO],[2*CO,0,0],[0,0,2*CO],26,.32,noise=.01)
# columns: solid, full height to ceiling
for sx in(-1,1):
    for sz in(-1,1):
        c=[sx*(CO-CW/2),H_C/2,sz*(CO-CW/2)];box(c,[CW,H_C,CW],55,.62,faces='xXzZ')
for axis,s in KEEP:
    # tower wall (inner and outer face) above the open ground floor
    wallpts(axis,s,WI,H_BEAM0,H_C,14,.7,span=WI);wallpts(axis,s,WO,H_BEAM0,H_RT,7,.55,span=WO)
    # ring beam
    wallpts(axis,s,WI-.05,H_BEAM0,H_BEAM1,90,.95,span=WI)
    # textile with vertical folds and slight sag
    def fold(p,axis=axis,s=s):
        u=p[:,2] if axis=='x' else p[:,0];yy=p[:,1]
        d=.09*np.sin(u*2*np.pi/.32)+.05*np.sin(u*2*np.pi/1.7+yy*.4)+.12*np.sin((yy-H_T0)/(H_T1-H_T0)*np.pi)
        if axis=='x':p[:,0]=s*(TX-d)
        else:p[:,2]=s*(TX-d)
        return p
    wallpts(axis,s,TX,H_T0,H_T1,85,.44,fn=fold,span=TX)
    # cable grid of the textile and its nodes
    hs=[H_T0,H_T0+2.57,H_T0+5.15,H_T0+7.72,H_T1]
    for g in GRID:
        a=[s*TX-s*.15,H_T0,g] if axis=='x' else [g,H_T0,s*TX-s*.15]
        b=list(a);b[1]=H_T1;line(a,b,70,.85)
    for h in hs:
        a=[s*TX-s*.15,h,-TX] if axis=='x' else [-TX,h,s*TX-s*.15]
        b=[s*TX-s*.15,h,TX] if axis=='x' else [TX,h,s*TX-s*.15];line(a,b,60,.85)
        for g in GRID:
            c=np.array([s*TX-s*.15,h,g] if axis=='x' else [g,h,s*TX-s*.15]);add(c+rng.normal(0,.06,(60,3)),1.0)
    # light slot below the ceiling
    a=[s*(WI-.3),H_C-.35,-WI] if axis=='x' else [-WI,H_C-.35,s*(WI-.3)];b=[s*(WI-.3),H_C-.35,WI] if axis=='x' else [WI,H_C-.35,s*(WI-.3)]
    line(a,b,120,.22,noise=.05)
# coffered ceiling: ribs (bottom + sides), coffer backs with round skylights
edges=[-WI]+GRID+[WI]
for g in edges:
    for axis in('x','z'):
        for side in(-.25,.25):
            if axis=='x':rect([g+side,H_C,-WI],[0,H_R-H_C,0],[0,0,2*WI],13,.9)
            else:rect([-WI,H_C,g+side],[2*WI,0,0],[0,H_R-H_C,0],13,.9)
        if axis=='x':rect([g-.25,H_C,-WI],[.5,0,0],[0,0,2*WI],90,1.0)
        else:rect([-WI,H_C,g-.25],[2*WI,0,0],[0,0,.5],90,1.0)
for i in range(7):
    for j in range(7):
        x0,x1=edges[i]+.25,edges[i+1]-.25;z0,z1=edges[j]+.25,edges[j+1]-.25
        cx,cz=(x0+x1)/2,(z0+z1)/2;sky=2<=i<=4 and 3<=j<=5
        n=int((x1-x0)*(z1-z0)*7);p=np.c_[x0+rng.random(n)*(x1-x0),np.full(n,H_R),z0+rng.random(n)*(z1-z0)]
        r=1.0
        if sky:
            k=np.hypot(p[:,0]-cx,p[:,2]-cz)>r;add(p[~k]+rng.normal(0,.02,p[~k].shape),.18);p=p[k]
            # dome above the skylight
            m=900;t=rng.random(m)*2*np.pi;ph=np.arccos(rng.random(m));
            add(np.c_[cx+r*np.sin(ph)*np.cos(t),H_RT+r*.55*np.cos(ph),cz+r*np.sin(ph)*np.sin(t)],.35)
            t=rng.random(500)*2*np.pi;add(np.c_[cx+r*np.cos(t),np.full(500,H_R),cz+r*np.sin(t)],.9)
        add(p+rng.normal(0,.015,p.shape),.55)
# truss ring (22 m) at 12.6 m, 0.6 m deep, with diagonals and four spotlights
TS,TY,TD=11.0,12.6,.6
def truss(a,b):
    a,b=np.asarray(a,float),np.asarray(b,float);d=b-a;L=np.linalg.norm(d);u=d/L
    side=np.cross(u,[0,1,0]);side/=np.linalg.norm(side)
    offs=[np.array([0,TD/2,0])+side*TD/2,np.array([0,TD/2,0])-side*TD/2,np.array([0,-TD/2,0])+side*TD/2,np.array([0,-TD/2,0])-side*TD/2]
    for o in offs:line(a+o,b+o,110,.8,noise=.01)
    k=int(L/TD)
    for i in range(k):
        p0=a+u*i*TD;p1=a+u*(i+1)*TD
        for o0,o1 in((0,2),(1,3),(0,1),(2,3)):line(p0+offs[o0],p1+offs[o1 if i%2 else o0^1 if o0 in(0,2) else o1],40,.7,noise=.01)
for a,b in(([-TS,TY,-TS],[TS,TY,-TS]),([TS,TY,-TS],[TS,TY,TS]),([TS,TY,TS],[-TS,TY,TS]),([-TS,TY,TS],[-TS,TY,-TS])):truss(a,b)
for x in(-6.5,-3.8,3.8,6.5):
    box([x,TY-1.0,TS-.3],[.45,.6,.45],260,1.0);line([x,TY-.3,TS],[x,TY-.7,TS-.2],80,1.0)
for c in(-TS,TS):
    for g in(-TS,0,TS):
        line([c,TY+TD/2,g],[c,H_C,g],60,.6);line([g,TY+TD/2,c],[g,H_C,c],60,.6)
# benches (pews) from the floor plan: seat, backrest, two end boards
def pew(x,z,L,along):
    if along=='x':
        box([x,.43,z],[L,.05,.42],170,.78,faces='yY');box([x,.65,z+.2],[L,.45,.04],170,.78,faces='zZ')
        for e in(-1,1):box([x+e*L/2,.4,z],[.05,.8,.45],400,.85,faces='xX')
    else:
        box([x,.43,z],[.42,.05,L],170,.78,faces='yY');box([x+.2,.65,z],[.04,.45,L],170,.78,faces='xX')
        for e in(-1,1):box([x,.4,z+e*L/2],[.45,.8,.05],400,.85,faces='zZ')
PX=15.7;cx,cy=476.25,526.25
for xc in(398,553.5):
    for yr in(313,333,352,372,393,413,435):pew((xc-cx)/PX,(yr-cy)/PX,6.5,'x')
for xs in((259,278,296,315,334),(609,628,646,665,684)):
    for x in xs:
        for zc in((475+578)/2,(610+716)/2):pew((x-cx)/PX,(zc-cy)/PX,6.6,'z')
# stage platform and grand piano
x0,x1,z0,z1=(391-cx)/PX,(562-cx)/PX,(492-cy)/PX,(755-cy)/PX
box([(x0+x1)/2,.22,(z0+z1)/2],[x1-x0,.45,z1-z0],40,.92,faces='xXyYzZ')
px,pz=(478-cx)/PX,(585-cy)/PX
box([px,.45+.75,pz],[1.5,.3,2.7],220,1.0);rect([px-.75,1.35,pz-1.35],[1.5,0,0],[0,.9,.9],220,1.0)
for e in((-.6,-1.1),(.6,-1.1),(0,1.1)):line([px+e[0],.45,pz+e[1]],[px+e[0],1.05,pz+e[1]],200,1.0)

# ---- cloister ring (Kreuzgang) around the high hall, from plan and section
RX0,RX1,RZ0,RZ1=-24.1,24.1,-19.5,19.7   # inside faces of the outer walls (north: annex wall)
OT=.64;RH=5.6                            # outer wall thickness, ring height
def floor_ring():
    n=int(((RX1-RX0)*(RZ1-RZ0)-(2*CO)**2)*16);p=np.c_[RX0+rng.random(n*2)*(RX1-RX0),np.zeros(n*2),RZ0+rng.random(n*2)*(RZ1-RZ0)]
    k=(np.abs(p[:,0])>CO)|(np.abs(p[:,2])>CO);p=p[k][:n];add(p+rng.normal(0,.01,p.shape),.3)
floor_ring()
# kept outer walls: west (-x) and south (+z); cut: east and north
rect([RX0-OT,0,RZ0],[0,RH,0],[0,0,RZ1-RZ0+OT],10,.6)          # west outer face
rect([RX0,0,RZ0],[0,RH,0],[0,0,RZ1-RZ0],12,.7)                # west inner face
rect([RX0-OT,RH,RZ0],[OT,0,0],[0,0,RZ1-RZ0+OT],60,.95)        # west wall top (cut edge)
rect([RX0-OT,0,RZ1+OT],[RX1-RX0+OT,0,0],[0,RH,0],10,.6)       # south outer face
rect([RX0,0,RZ1],[RX1-RX0,0,0],[0,RH,0],12,.7)                # south inner face
rect([RX0-OT,RH,RZ1],[RX1-RX0+OT,0,0],[0,0,OT],60,.95)        # south wall top
# textile on the inner faces of the kept outer walls (0-4 m), with folds
def foldx(p):p[:,0]=RX0+.25+.07*np.sin(p[:,2]*2*np.pi/.32)+.04*np.sin(p[:,2]*1.3);return p
def foldz(p):p[:,2]=RZ1-.25-.07*np.sin(p[:,0]*2*np.pi/.32)-.04*np.sin(p[:,0]*1.3);return p
rect([RX0+.25,.2,RZ0+.5],[0,3.8,0],[0,0,RZ1-RZ0-1],55,.45,fn=foldx)
rect([RX0+.5,.2,RZ1-.25],[RX1-RX0-1,0,0],[0,3.8,0],55,.45,fn=foldz)
# ring roof edge on the kept sides (roof itself left open to look in from above)
line([RX0,RH-.5,RZ0],[RX0,RH-.5,RZ1],80,.9);line([RX0,RH-.5,RZ1],[RX1,RH-.5,RZ1],80,.9)

# stair (13 steps) and counter in the west aisle
sx0,sx1=(135-476.25)/15.7,(203-476.25)/15.7;sz0,sz1=(330-526.25)/15.7,(552-526.25)/15.7
for k in range(13):
    z0=sz1-(k+1)*(sz1-sz0)/13;z1=sz1-k*(sz1-sz0)/13;h=(k+1)*.19
    rect([sx0,h,z0],[sx1-sx0,0,0],[0,0,z1-z0],90,.75);rect([sx0,h-.19,z1],[sx1-sx0,0,0],[0,.19,0],90,.85)
rect([sx0,0,sz0],[0,13*.19,0],[0,0,sz1-sz0],25,.7)
cz0,cz1=(578-526.25)/15.7,(696-526.25)/15.7
box([(sx0+sx1)/2,.55,(cz0+cz1)/2],[sx1-sx0,1.1,cz1-cz0],80,.9)
P=np.concatenate(P);W=np.concatenate(Wt)
print('points',len(P),'extent',P.min(0).round(1),P.max(0).round(1))
np.savez('church_model.npz',P=P.astype(np.float32),W=W)
