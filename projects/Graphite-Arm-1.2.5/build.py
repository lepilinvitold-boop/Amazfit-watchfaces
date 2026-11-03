from pathlib import Path
import io,json,zipfile,hashlib,math
import numpy as np
from PIL import Image,ImageDraw
from reportlab.graphics.barcode.qr import QrCodeWidget
P=Path(__file__).resolve().parent;ROOT=P.parents[1];D=ROOT/'dist';B='Graphite-2-v1.2.5'
codec=P.parent/'Owl-Graphite-Color-1.0.9/build.py';ns={'__file__':str(codec)};exec(codec.read_text().split('with zipfile.ZipFile')[0],ns);encode=ns['encode']
base=D/'Graphite-2-v1.2.4-RU-Balance2.zpk'
assert hashlib.sha256(base.read_bytes()).hexdigest()=='533b8d6c19cb5c8f81787152461a32b43e4f4d597a2360bea9d4830f0d8673f8'
with zipfile.ZipFile(base) as z:
 with zipfile.ZipFile(io.BytesIO(z.read('device.zip'))) as q:files={n:q.read(n) for n in q.namelist()}
S=6
for name,tip,half,shoulder,innerhalf in [('hour',73,15,207,10.5),('minute',37,13,209,8.5)]:
 outer=[(36,tip),(36+half,shoulder),(43,222),(43,249),(36,255),(29,249),(29,222),(36-half,shoulder)]
 hole=[(36,tip+26),(36+innerhalf,shoulder-3),(41.5,215),(30.5,215),(36-innerhalf,shoulder-3)]
 cy=(tip+26+215)/2
 hole=[(36+(x-36)*.40,cy+(y-cy)*.78) for x,y in hole]
 mask=Image.new('L',(76*S,300*S));dr=ImageDraw.Draw(mask);pts=lambda pp:[(round(x*S),round(y*S)) for x,y in pp]
 dr.polygon(pts(outer),fill=255);dr.polygon(pts(hole),fill=0)
 yy,xx=np.mgrid[:300*S,:76*S];x=xx/S-36;y=yy/S;light=np.clip(196-2.2*x+16*np.cos(x/4)+3*np.sin(y/27),125,243)
 a=np.zeros((300*S,76*S,4),np.uint8)
 for channel,offset in enumerate([-3,0,3]):a[:,:,channel]=np.clip(light+offset,0,255)
 a[:,:,3]=np.array(mask);im=Image.fromarray(a);edge=ImageDraw.Draw(im)
 edge.line(pts(outer+[outer[0]]),fill=(226,231,235,255),width=round(1.15*S),joint='curve')
 edge.line(pts(hole+[hole[0]]),fill=(158,166,173,255),width=round(1.6*S),joint='curve');edge.polygon(pts(hole),fill=(0,0,0,0))
 im=im.resize((76,300),Image.Resampling.LANCZOS);files['assets/'+name+'125.png']=encode(im)
 a=np.array(im);a[:,:,:3]=(a[:,:,:3]*.38).astype('uint8');files['assets/aod_'+name+'125.png']=encode(Image.fromarray(a))
# Preserve every original outer-edge pixel/index; modify only the inner blade area.
import struct
for name,tip in [('hour',73),('minute',37)]:
 for pre in ['', 'aod_']:
  raw=bytearray(files['assets/'+pre+name+'123.png']);old=np.array(ns['decode'](raw));target=np.array(ns['decode'](files['assets/'+pre+name+'125.png'])).astype('int32')
  stride=struct.unpack_from('<H',raw,12)[0];pal=np.frombuffer(raw[64:1088],np.uint8).reshape(256,4).astype('int32')
  target[:,:,:3]=np.rint(target[:,:,:3]*target[:,:,3:4]/255)
  for y0 in range(tip+24,218):
   xs=np.where(old[y0,:,3]>128)[0]
   if len(xs)<6:continue
   lo=int(xs.min())+2;hi=int(xs.max())-1
   colours=target[y0,lo:hi];ids=((colours[:,None,:]-pal[None,:,:])**2).sum(2).argmin(1).astype('uint8')
   raw[1088+y0*stride+lo:1088+y0*stride+hi]=ids.tobytes()
  files['assets/'+pre+name+'125.png']=bytes(raw)
preview=D/(B+'-preview.png')
if preview.exists():files['assets/preview.png']=encode(Image.open(preview).convert('RGBA').resize((240,240),Image.Resampling.LANCZOS))
m=json.loads(files['app.json']);m['app']['appName']='Graphite 2 (1.2.5)';m['i18n']['en-US']['appName']=m['app']['appName'];m['app']['version']={'code':29,'name':'1.2.5'};m['packageInfo']['timeStamp']=1793707200
mb=json.dumps(m,ensure_ascii=False).encode();files['app.json']=mb;(P/'app.json').write_bytes(mb)
files['watchface/index.js']=(P/'watchface.js').read_bytes()
def archive(items):
 b=io.BytesIO()
 with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED) as z:
  for n,v in items.items():
   info=zipfile.ZipInfo(n,(2026,11,3,12,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,v)
 return b.getvalue()
target=ROOT/'verify-graphite-arm-125';target.mkdir(exist_ok=True)
for n,v in files.items():
 p=target/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(v)
zpk=D/(B+'-RU-Balance2.zpk');zpk.write_bytes(archive({'device.zip':archive(files),'app-side.zip':archive({'app.json':mb})}))
url='zpkd1://raw.githubusercontent.com/lepilinvitold-boop/Amazfit-watchfaces/graphite-arm-1.2.5/dist/'+B+'-RU-Balance2.zpk';(D/(B+'-install-url.txt')).write_text(url)
q=QrCodeWidget(url,barLevel='M');q.qr.make();matrix=q.qr.modules;n=len(matrix);qr=Image.new('RGB',((n+8)*8,)*2,'white');draw=ImageDraw.Draw(qr)
for y,row in enumerate(matrix):
 for x,v in enumerate(row):
  if v:draw.rectangle(((x+4)*8,(y+4)*8,(x+5)*8-1,(y+5)*8-1),fill='black')
qr.save(D/(B+'-zepp-qr.png'))
print('Built',zpk.name,hashlib.sha256(zpk.read_bytes()).hexdigest())
