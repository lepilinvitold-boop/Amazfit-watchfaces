from pathlib import Path
import io,json,zipfile,hashlib,math
import numpy as np
from PIL import Image,ImageDraw
from reportlab.graphics.barcode.qr import QrCodeWidget
P=Path(__file__).resolve().parent;ROOT=P.parents[1];D=ROOT/'dist';B='Graphite-2-v1.2.3'
codec=P.parent/'Owl-Graphite-Color-1.0.9/build.py';ns={'__file__':str(codec)};exec(codec.read_text().split('with zipfile.ZipFile')[0],ns);encode=ns['encode']
base=D/'Graphite-2-0-v1.2.2-RU-Balance2.zpk'
assert hashlib.sha256(base.read_bytes()).hexdigest()=='1a4cd25241d88aff7856cf9634258ee82fa3eda1ccc6710b11ab217b0f95c7e9'
with zipfile.ZipFile(base) as z:
 with zipfile.ZipFile(io.BytesIO(z.read('device.zip'))) as q:files={n:q.read(n) for n in q.namelist()}
S=6
for name,tip,half,shoulder,innerhalf in [('hour',73,15,207,10.5),('minute',37,13,209,8.5)]:
 outer=[(36,tip),(36+half,shoulder),(43,222),(43,249),(36,255),(29,249),(29,222),(36-half,shoulder)]
 hole=[(36,tip+26),(36+innerhalf,shoulder-3),(41.5,215),(30.5,215),(36-innerhalf,shoulder-3)]
 mask=Image.new('L',(76*S,300*S));dr=ImageDraw.Draw(mask);pts=lambda pp:[(round(x*S),round(y*S)) for x,y in pp]
 dr.polygon(pts(outer),fill=255);dr.polygon(pts(hole),fill=0)
 yy,xx=np.mgrid[:300*S,:76*S];x=xx/S-36;y=yy/S;light=np.clip(196-2.2*x+16*np.cos(x/4)+3*np.sin(y/27),125,243)
 a=np.zeros((300*S,76*S,4),np.uint8)
 for channel,offset in enumerate([-3,0,3]):a[:,:,channel]=np.clip(light+offset,0,255)
 a[:,:,3]=np.array(mask);im=Image.fromarray(a);edge=ImageDraw.Draw(im)
 edge.line(pts(outer+[outer[0]]),fill=(226,231,235,255),width=round(1.15*S),joint='curve')
 edge.line(pts(hole+[hole[0]]),fill=(158,166,173,255),width=round(1.6*S),joint='curve');edge.polygon(pts(hole),fill=(0,0,0,0))
 im=im.resize((76,300),Image.Resampling.LANCZOS);files['assets/'+name+'123.png']=encode(im)
 a=np.array(im);a[:,:,:3]=(a[:,:,:3]*.38).astype('uint8');files['assets/aod_'+name+'123.png']=encode(Image.fromarray(a))
preview=D/(B+'-preview.png')
if preview.exists():files['assets/preview.png']=encode(Image.open(preview).convert('RGBA').resize((240,240),Image.Resampling.LANCZOS))
m=json.loads(files['app.json']);m['app']['appName']='Graphite 2 (1.2.3)';m['i18n']['en-US']['appName']=m['app']['appName'];m['app']['version']={'code':27,'name':'1.2.3'};m['packageInfo']['timeStamp']=1793707200
mb=json.dumps(m,ensure_ascii=False).encode();files['app.json']=mb;(P/'app.json').write_bytes(mb)
files['watchface/index.js']=(P/'watchface.js').read_bytes()
def archive(items):
 b=io.BytesIO()
 with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED) as z:
  for n,v in items.items():
   info=zipfile.ZipInfo(n,(2026,11,3,12,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,v)
 return b.getvalue()
target=ROOT/'verify-graphite-arm-123';target.mkdir(exist_ok=True)
for n,v in files.items():
 p=target/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(v)
zpk=D/(B+'-RU-Balance2.zpk');zpk.write_bytes(archive({'device.zip':archive(files),'app-side.zip':archive({'app.json':mb})}))
url='zpkd1://raw.githubusercontent.com/lepilinvitold-boop/Amazfit-watchfaces/graphite-arm-1.2.3/dist/'+B+'-RU-Balance2.zpk';(D/(B+'-install-url.txt')).write_text(url)
q=QrCodeWidget(url,barLevel='M');q.qr.make();matrix=q.qr.modules;n=len(matrix);qr=Image.new('RGB',((n+8)*8,)*2,'white');draw=ImageDraw.Draw(qr)
for y,row in enumerate(matrix):
 for x,v in enumerate(row):
  if v:draw.rectangle(((x+4)*8,(y+4)*8,(x+5)*8-1,(y+5)*8-1),fill='black')
qr.save(D/(B+'-zepp-qr.png'))
print('Built',zpk.name,hashlib.sha256(zpk.read_bytes()).hexdigest())
