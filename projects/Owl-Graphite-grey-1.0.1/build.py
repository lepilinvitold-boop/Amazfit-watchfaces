from pathlib import Path
import io,json,zipfile,time
import numpy as np
from PIL import Image,ImageDraw
from reportlab.graphics.barcode.qr import QrCodeWidget
P=Path(__file__).resolve().parent;ROOT=P.parents[1];D=ROOT/'dist';B='Owl-Graphite-grey-v1.0.1'
ns={};s=(P.parent/'Owl-Graphite-Color-1.0.9/build.py').read_text();exec(s[:s.index('with zipfile.ZipFile')].replace('P=Path(__file__).resolve().parent','P=Path('+repr(str(P))+')'),ns)
encode,decode=ns['encode'],ns['decode']
def archive(items):
 b=io.BytesIO()
 with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED) as z:
  for n,v in items.items():z.writestr(n,v)
 return b.getvalue()
with zipfile.ZipFile(D/(B+'-RU-Balance2.zpk')) as z:
 with zipfile.ZipFile(io.BytesIO(z.read('device.zip'))) as d:base={n:d.read(n) for n in d.namelist()}
files=dict(base);m=json.loads(files['app.json']);m['app']['version']={'code':2,'name':'1.0.1'};m['packageInfo']['timeStamp']=int(time.time());mb=json.dumps(m,ensure_ascii=False).encode();files['app.json']=mb;(P/'app.json').write_bytes(mb)
for n,src in [('app.js','app.js'),('watchface/index.js','watchface.js')]:files[n]=(P/src).read_bytes()
# New dash only; every existing asset, including bezel, icons and labels, is exact.
for prefix,color in [('',(217,217,217,255)),('aod_',(90,90,90,255))]:
 im=Image.new('RGBA',(24,6));ImageDraw.Draw(im).rounded_rectangle((0,1,23,4),radius=1,fill=color);files['assets/'+prefix+'missing_dash.png']=encode(im)
for n,v in base.items():
 if n.startswith('assets/'):assert files[n]==v,n
(D/(B+'-RU-Balance2.zpk')).write_bytes(archive({'device.zip':archive(files),'app-side.zip':archive({'app.json':mb})}))
url='zpkd1://raw.githubusercontent.com/lepilinvitold-boop/Amazfit-watchfaces/owl-graphite-grey-1.0.1/dist/'+B+'-RU-Balance2.zpk';(D/(B+'-install-url.txt')).write_text(url)
q=QrCodeWidget(url,barLevel='M');q.qr.make();matrix=q.qr.modules;n=len(matrix);qr=Image.new('RGB',((n+8)*8,)*2,'white');draw=ImageDraw.Draw(qr)
for y,row in enumerate(matrix):
 for x,v in enumerate(row):
  if v:draw.rectangle(((x+4)*8,(y+4)*8,(x+5)*8-1,(y+5)*8-1),fill='black')
qr.save(D/(B+'-zepp-qr.png'))
T=ROOT/'verify-grey-1.0.1';T.mkdir(exist_ok=True)
for n,v in files.items():p=T/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(v)
print('Built',B,'; ALL existing assets byte-identical; appId unchanged:',m['app']['appId'])
