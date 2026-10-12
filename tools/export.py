import re,base64,json,os,shutil
SRC='/mnt/user-data/outputs/portfolio-demo.html'
OUT='/tmp/claude-0/-home-claude/e832e4d2-a3e9-58f5-bd03-8574968a6034/scratchpad/export/rollimario.eu'
shutil.rmtree(OUT,ignore_errors=True);os.makedirs(OUT+'/clouds');os.makedirs(OUT+'/assets')
s=open(SRC,encoding='utf-8').read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(a[:80],s.count(a));s=s.replace(a,b)
# 1) point clouds -> binary files
m=re.search(r"const CL=mk\('([^']*)',(\d+)\),CB=mk\('([^']*)',(\d+)\),CC=mk\('([^']*)',(\d+)\),CD=mk\('([^']*)',(\d+)\),CE=mk\('([^']*)',(\d+)\),CS=\[CL,CB,CC,CD,CE\];",s);assert m
names=['forest','scan','frame','car','stairs'];n=int(m.group(2))
for k,nm in enumerate(names):
    open(f'{OUT}/clouds/{nm}.bin','wb').write(base64.b64decode(m.group(2*k+1)))
loader=("const NP=%d,CN=%s,CS=CN.map(()=>null);\n"
"const mkb=(b,n)=>{const sc=1/4000,q=new Int16Array(b,0,n*3),X=new Float32Array(n),Y=new Float32Array(n),Z=new Float32Array(n),W=new Float32Array(n),w=new Uint8Array(b,n*6,n);for(let i=0;i<n;i++){X[i]=q[i]*sc;Y[i]=q[n+i]*sc;Z[i]=q[2*n+i]*sc;W[i]=w[i]/255;}return{n,X,Y,Z,W};};\n"
"const getCloud=u=>fetch(u).then(r=>{if(!r.ok)throw 0;return r.arrayBuffer();}).then(b=>mkb(b,b.byteLength/7|0));\n"
"/* first cloud right away, the others one after another in the background */\n"
"(async()=>{for(let k=0;k<CN.length;k++){try{CS[k]=await getCloud(CN[k]);if(k===0&&typeof R!=='undefined'&&R)draw();}catch(e){}}})();")%(n,json.dumps(['clouds/%s.bin'%x for x in names]))
s=s[:m.start()]+loader+s[m.end():]
rep("const RX=new Float32Array(CL.n*3);","const RX=new Float32Array(NP*3);")
rep("{n}=CL,{X,Y,Z,W:Wt}=CS[MS],{X:X2,Y:Y2,Z:Z2,W:W2}=CS[(MS+1)%5]","n=NP,{X,Y,Z,W:Wt}=CS[MS],{X:X2,Y:Y2,Z:Z2,W:W2}=CS[(MS+1)%5]||CS[MS]")
# don't draw before the first cloud has arrived; hold the rotation until the next cloud is loaded
rep("function cloud(){\n","function cloud(){\n if(!CS[MS]){if(U32){U32.fill(0);c.putImageData(IM,0,0);}return;}\n")
rep("if(!R){MT+=dt;const r=mmAt(MT);MS=r[0];MM=r[1];}",
    "if(!R&&CS[0]){const r=mmAt(MT+dt);if(r[1]===0||CS[(r[0]+1)%5])MT+=dt;const q=mmAt(MT);MS=q[0];MM=q[1];if(!CS[MS]){MS=0;MM=0;}}")
# 2) project cloud as binary
rep("fetch(u).then(r=>{if(!r.ok)throw 0;return r.json();}).then(j=>{PCC[u]=mk(j.b,j.n);if(R)draw();})","getCloud(u).then(cl=>{PCC[u]=cl;if(R)draw();})")
rep("PRJ[0].cloud='p/st-mauritius/church-cloud.json';","PRJ[0].cloud='p/st-mauritius/church.bin';")
os.makedirs(OUT+'/p/st-mauritius',exist_ok=True)
j=json.load(open('/mnt/user-data/outputs/p/st-mauritius/church-cloud.json'))
open(OUT+'/p/st-mauritius/church.bin','wb').write(base64.b64decode(j['b']))
for f in os.listdir('/mnt/user-data/outputs/p/st-mauritius'):
    if f.endswith('.jpg'):shutil.copy('/mnt/user-data/outputs/p/st-mauritius/'+f,OUT+'/p/st-mauritius/'+f)
# 3) embedded images -> files
cnt=[0]
def img(mo):
    cnt[0]+=1;ext={'jpeg':'jpg','png':'png','webp':'webp'}[mo.group(1)]
    fn=f'assets/img-{cnt[0]:02d}.{ext}';open(f'{OUT}/{fn}','wb').write(base64.b64decode(mo.group(2)));return '"u":"%s"'%fn
s=re.sub(r'"s":"data:image/(jpeg|png|webp);base64,([A-Za-z0-9+/=]+)"',img,s)
print('images extracted',cnt[0])
# 4) font -> file
fm=re.search(r'url\(data:font/woff2;base64,([A-Za-z0-9+/=]+)\)',s);assert fm
open(OUT+'/assets/akkurat-regular.woff2','wb').write(base64.b64decode(fm.group(1)))
s=s[:fm.start()]+'url(assets/akkurat-regular.woff2)'+s[fm.end():]
# 5) not indexed yet (soft launch)
rep('<meta charset="utf-8">','<meta charset="utf-8">\n<meta name="robots" content="noindex, nofollow">')
open(OUT+'/index.html','w',encoding='utf-8').write(s)
open(OUT+'/robots.txt','w').write('User-agent: *\nDisallow: /\n')
print('index.html',round(len(s.encode())/1e6,2),'MB')
