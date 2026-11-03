from pathlib import Path
import io,json,zipfile,hashlib,math,struct
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from reportlab.graphics.barcode.qr import QrCodeWidget
P=Path(__file__).resolve().parent;ROOT=P.parents[1];D=ROOT/'dist';B='Graphite-2-v1.2.6'
codec=P.parent/'Owl-Graphite-Color-1.0.9/build.py';ns={'__file__':str(codec)};exec(codec.read_text().split('with zipfile.ZipFile')[0],ns);encode=ns['encode']
base=D/'Graphite-2-v1.2.5-RU-Balance2.zpk'
assert hashlib.sha256(base.read_bytes()).hexdigest()=='3e398f1e729c739d17d6879fa0073f00680b85cc45e04545e252bd3881e76e3f'
with zipfile.ZipFile(base) as z:
 with zipfile.ZipFile(io.BytesIO(z.read('device.zip'))) as q:files={n:q.read(n) for n in q.namelist()}
# One-pixel black OUTER contour; fill holes only in the temporary silhouette mask.
for name in ['hour','minute']:
 for pre in ['', 'aod_']:
  original=ns['decode'](files['assets/'+pre+name+'125.png']);a=np.array(original);alpha=a[:,:,3];outer=alpha.copy()
  for y0,row in enumerate(alpha):
   xs=np.where(row>128)[0]
   if len(xs):outer[y0,xs.min():xs.max()+1]=255
  dilated=np.array(Image.fromarray(outer).filter(ImageFilter.MaxFilter(3)))
  rim=np.maximum(0,dilated.astype('int16')-outer.astype('int16')).astype('uint8')
  black=Image.new('RGBA',original.size,(0,0,0,0));black.putalpha(Image.fromarray(rim));black.alpha_composite(original)
  # Keep every original used palette entry/index, including antialiasing.
  # Reserve unused palette slots for exact black at sixteen alpha levels.
  raw=bytearray(files['assets/'+pre+name+'125.png']);stride=struct.unpack_from('<H',raw,12)[0]
  ids=np.frombuffer(raw[1088:],np.uint8).reshape(300,stride).copy();used=set(ids.flat);free=[i for i in range(256) if i not in used];assert len(free)>=15
  visible=ids[:,:76];levels=np.rint(rim/17).astype('uint8')
  for level in range(1,16):
   idx=free[level-1];raw[64+idx*4:68+idx*4]=bytes([0,0,0,level*17]);visible[(alpha==0)&(levels==level)]=idx
  files['assets/'+pre+name+'126.png']=bytes(raw[:1088])+ids.tobytes()
preview=D/(B+'-preview.png')
if preview.exists():files['assets/preview.png']=encode(Image.open(preview).convert('RGBA').resize((240,240),Image.Resampling.LANCZOS))
m=json.loads(files['app.json']);m['app']['appName']='Graphite 2 (1.2.6)';m['i18n']['en-US']['appName']=m['app']['appName'];m['app']['version']={'code':30,'name':'1.2.6'};m['packageInfo']['timeStamp']=1793707200
mb=json.dumps(m,ensure_ascii=False).encode();files['app.json']=mb;(P/'app.json').write_bytes(mb)
files['watchface/index.js']=(P/'watchface.js').read_bytes()
def archive(items):
 b=io.BytesIO()
 with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED) as z:
  for n,v in items.items():
   info=zipfile.ZipInfo(n,(2026,11,3,12,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,v)
 return b.getvalue()
target=ROOT/'verify-graphite-arm-126';target.mkdir(exist_ok=True)
for n,v in files.items():
 p=target/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(v)
zpk=D/(B+'-RU-Balance2.zpk');zpk.write_bytes(archive({'device.zip':archive(files),'app-side.zip':archive({'app.json':mb})}))
url='zpkd1://raw.githubusercontent.com/lepilinvitold-boop/Amazfit-watchfaces/graphite-arm-1.2.6/dist/'+B+'-RU-Balance2.zpk';(D/(B+'-install-url.txt')).write_text(url)
q=QrCodeWidget(url,barLevel='M');q.qr.make();matrix=q.qr.modules;n=len(matrix);qr=Image.new('RGB',((n+8)*8,)*2,'white');draw=ImageDraw.Draw(qr)
for y,row in enumerate(matrix):
 for x,v in enumerate(row):
  if v:draw.rectangle(((x+4)*8,(y+4)*8,(x+5)*8-1,(y+5)*8-1),fill='black')
qr.save(D/(B+'-zepp-qr.png'))
print('Built',zpk.name,hashlib.sha256(zpk.read_bytes()).hexdigest())
