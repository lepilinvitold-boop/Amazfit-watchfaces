from pathlib import Path
import io,json,zipfile,hashlib,math,struct
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from reportlab.graphics.barcode.qr import QrCodeWidget
P=Path(__file__).resolve().parent;ROOT=P.parents[1];D=ROOT/'dist';B='Graphite-2-v1.2.7'
codec=P.parent/'Owl-Graphite-Color-1.0.9/build.py';ns={'__file__':str(codec)};exec(codec.read_text().split('with zipfile.ZipFile')[0],ns);encode=ns['encode']
base=D/'Graphite-2-v1.2.6-RU-Balance2.zpk'
assert hashlib.sha256(base.read_bytes()).hexdigest()=='47f5bfdf22136387c3fd3c27e055352c70329ab2d45ebfba5a5b23c292cfd328'
with zipfile.ZipFile(base) as z:
 with zipfile.ZipFile(io.BytesIO(z.read('device.zip'))) as q:files={n:q.read(n) for n in q.namelist()}
# Short narrow neck, angular shoulders38px ahead of pivot, then tapered blade.
S=6
for name,tip,half,inner in [('hour',73,17,7),('minute',37,15,6)]:
 outer=[(36,tip),(36+half,194),(41,214),(41,232),(40,244),(36,247),(32,244),(31,232),(31,214),(36-half,194)]
 hole=[(36,tip+35),(36+inner,186),(39.5,200),(32.5,200),(36-inner,186)]
 pts=lambda pp:[(round(x*S),round(y*S)) for x,y in pp]
 mask=Image.new('L',(76*S,300*S));draw=ImageDraw.Draw(mask);draw.polygon(pts(outer),fill=255);draw.polygon(pts(hole),fill=0)
 yy,xx=np.mgrid[:300*S,:76*S];light=np.clip(196-2.2*(xx/S-36)+16*np.cos((xx/S-36)/4)+3*np.sin(yy/S/27),125,243)
 a=np.zeros((300*S,76*S,4),np.uint8)
 for ch,offset in enumerate([-3,0,3]):a[:,:,ch]=np.clip(light+offset,0,255)
 a[:,:,3]=np.array(mask);im=Image.fromarray(a);edge=ImageDraw.Draw(im)
 edge.line(pts(outer+[outer[0]]),fill=(226,231,235,255),width=round(1.15*S),joint='curve')
 edge.line(pts(hole+[hole[0]]),fill=(158,166,173,255),width=round(1.6*S),joint='curve');edge.polygon(pts(hole),fill=(0,0,0,0))
 im=im.resize((76,300),Image.Resampling.LANCZOS)
 for pre,factor in [('',1),('aod_',.38)]:
  rgba=np.array(im);rgba[:,:,:3]=(rgba[:,:,:3]*factor).astype('uint8');raw=bytearray(encode(Image.fromarray(rgba)));alpha=rgba[:,:,3];outer_alpha=alpha.copy()
  for y0,row in enumerate(alpha):
   xs=np.where(row>128)[0]
   if len(xs):outer_alpha[y0,xs.min():xs.max()+1]=255
  dilated=np.array(Image.fromarray(outer_alpha).filter(ImageFilter.MaxFilter(3)));rim=np.maximum(0,dilated.astype('int16')-outer_alpha.astype('int16')).astype('uint8')
  stride=struct.unpack_from('<H',raw,12)[0];ids=np.frombuffer(raw[1088:],np.uint8).reshape(300,stride).copy();used=set(ids.flat);free=[i for i in range(256) if i not in used];assert len(free)>=15
  levels=np.rint(rim/17).astype('uint8');visible=ids[:,:76]
  for level in range(1,16):
   idx=free[level-1];raw[64+idx*4:68+idx*4]=bytes([0,0,0,level*17]);visible[(alpha==0)&(levels==level)]=idx
  files['assets/'+pre+name+'127.png']=bytes(raw[:1088])+ids.tobytes()
preview=D/(B+'-preview.png')
if preview.exists():files['assets/preview.png']=encode(Image.open(preview).convert('RGBA').resize((240,240),Image.Resampling.LANCZOS))
m=json.loads(files['app.json']);m['app']['appName']='Graphite 2 (1.2.7)';m['i18n']['en-US']['appName']=m['app']['appName'];m['app']['version']={'code':31,'name':'1.2.7'};m['packageInfo']['timeStamp']=1793707200
mb=json.dumps(m,ensure_ascii=False).encode();files['app.json']=mb;(P/'app.json').write_bytes(mb)
files['watchface/index.js']=(P/'watchface.js').read_bytes()
def archive(items):
 b=io.BytesIO()
 with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED) as z:
  for n,v in items.items():
   info=zipfile.ZipInfo(n,(2026,11,3,12,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,v)
 return b.getvalue()
target=ROOT/'verify-graphite-arm-127';target.mkdir(exist_ok=True)
for n,v in files.items():
 p=target/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(v)
zpk=D/(B+'-RU-Balance2.zpk');zpk.write_bytes(archive({'device.zip':archive(files),'app-side.zip':archive({'app.json':mb})}))
url='zpkd1://raw.githubusercontent.com/lepilinvitold-boop/Amazfit-watchfaces/graphite-arm-1.2.7/dist/'+B+'-RU-Balance2.zpk';(D/(B+'-install-url.txt')).write_text(url)
q=QrCodeWidget(url,barLevel='M');q.qr.make();matrix=q.qr.modules;n=len(matrix);qr=Image.new('RGB',((n+8)*8,)*2,'white');draw=ImageDraw.Draw(qr)
for y,row in enumerate(matrix):
 for x,v in enumerate(row):
  if v:draw.rectangle(((x+4)*8,(y+4)*8,(x+5)*8-1,(y+5)*8-1),fill='black')
qr.save(D/(B+'-zepp-qr.png'))
print('Built',zpk.name,hashlib.sha256(zpk.read_bytes()).hexdigest())
