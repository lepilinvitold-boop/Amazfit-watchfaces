from pathlib import Path
import io,json,struct,zipfile,runpy
import numpy as np
from PIL import Image,ImageDraw
from reportlab.graphics.barcode.qr import QrCodeWidget
P=Path(__file__).resolve().parent;ROOT=P.parents[1];D=ROOT/'dist';B='Owl-Graphite-grey-v1.0.0'
# Import codec definitions only; do not execute the Color builder.
s=(P.parent/'Owl-Graphite-Color-1.0.9/build.py').read_text();ns={};exec(s[:s.index('with zipfile.ZipFile')].replace('P=Path(__file__).resolve().parent','P=Path('+repr(str(P))+')'),ns)
decode,encode=ns['decode'],ns['encode']
def unpack(path):
 with zipfile.ZipFile(path) as z:
  with zipfile.ZipFile(io.BytesIO(z.read('device.zip'))) as d:return {n:d.read(n) for n in d.namelist()}
def archive(items):
 b=io.BytesIO()
 with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED) as z:
  for n,v in items.items():z.writestr(n,v)
 return b.getvalue()
base=unpack(D/'Owl-Graphite-Color-v1.0.9-RU-Balance2.zpk');ref={'assets/'+n:(P/'resources'/n).read_bytes() for n in ['second.png','aod_second.png']};files=dict(base)
def steel(b):
 # Edit only premultiplied palette RGB. Pixel indices, dimensions and alpha stay exact.
 out=bytearray(b);p=np.frombuffer(out,np.uint8,offset=64,count=1024).reshape(256,4);rgb=p[:,:3].astype(float);a=p[:,3].astype(float);mx=rgb.max(1);mn=rgb.min(1);colored=(mx-mn)>a*.025
 value=np.minimum(mx*1.7,a*225/255).round().astype('uint8');p[colored,:3]=value[colored,None];return bytes(out)
for n,b in base.items():
 if n.startswith('assets/') and n.endswith('.png'):files[n]=steel(b)
# The original Graphite hand is copied, with the 21 px portion beyond radius 201 red.
b=bytearray(ref['assets/second.png']);w,h=struct.unpack_from('<HH',b,12);p=np.frombuffer(b,np.uint8,offset=64,count=1024).reshape(256,4);idx=np.frombuffer(b,np.uint8,offset=1088).reshape(h,w);used=set(idx.ravel());free=[i for i in range(256) if i not in used];top=idx[:21].copy()
for old in np.unique(top):
 if p[old,3]==0:continue
 new=free.pop();alpha=int(p[old,3]);p[new]=[round(220*alpha/255),round(35*alpha/255),round(40*alpha/255),alpha];idx[:21][top==old]=new
files['assets/second.png']=bytes(b);files['assets/aod_second.png']=ref['assets/aod_second.png']
manifest=json.loads(files['app.json']);manifest['app'].update(appId=10622120,appName='Owl Graphite grey',version={'code':1,'name':'1.0.0'});manifest['i18n']['en-US']['appName']='Owl Graphite grey';manifest['packageInfo']['timeStamp']=1792058400
mb=json.dumps(manifest,ensure_ascii=False).encode();files['app.json']=mb;(P/'app.json').write_bytes(mb)
files['app.js']=(P/'app.js').read_bytes();files['watchface/index.js']=(P/'watchface.js').read_bytes()
# Assemble a preview from the actual native resources, including the new hand.
def preview(aod=False):
 prefix='aod_' if aod else ''
 def asset(n):return decode(files['assets/'+prefix+n+'.png'])
 im=asset('background')
 def paste(n,x,y):im.alpha_composite(asset(n),(x,y))
 def digits(t,font,x,y,width=None):
  ims=[asset(font+'_'+c) if c.isdigit() else asset('range_sep' if c=='–' else 'dot') for c in t];total=sum(a.width for a in ims);x=round(x+(width-total)/2) if width else x
  for a in ims:im.alpha_composite(a,(x,y));x+=a.width
 for n,x,y in [('graph_ring_15',295,171),('heart_ring_12',171,41),('stress_ring_14',47,171),('calorie_ring_10',47,171),('phone_icon',103,335),('workout_icon',103,103),('alarm_icon',336,336),('weather_3',186,300)]:paste(n,x,y)
 for t,f,x,y,w in [('89','circle',202,77,76),('73','small',70,210,92),('271','detail',70,262,92),('7650','circle',314,211,100),('5.84','detail',318,262,92),('77','battery',331,117,50),('22','circle',216,303,70),('14','time',178,350,None),('36','time',246,350,None),('15','date',188,404,None),('48–133','range',191,125,98)]:digits(t,f,x,y,w)
 paste('colon',234,350);paste('week_3',230,404);paste('graph_degree',278,303)
 def hand(n,px,py,angle):
  a=asset(n);canvas=Image.new('RGBA',(960,960));canvas.alpha_composite(a,(480-px,480-py));canvas=canvas.rotate(-angle,resample=Image.Resampling.BICUBIC,center=(480,480));im.alpha_composite(canvas.crop((240,240,720,720)))
 hand('hour',21,156,78);hand('minute',19,192,216)
 if not aod:hand('second',6,222,24)
 paste('cap',227,227);return im
pr=preview();pr.save(D/(B+'-preview.png'));preview(True).save(D/(B+'-AOD-preview.png'));files['assets/preview.png']=encode(pr.resize((240,240),Image.Resampling.LANCZOS))
(D/(B+'-RU-Balance2.zpk')).write_bytes(archive({'device.zip':archive(files),'app-side.zip':archive({'app.json':mb})}))
url='zpkd1://raw.githubusercontent.com/lepilinvitold-boop/Amazfit-watchfaces/owl-graphite-grey-1.0.0/dist/'+B+'-RU-Balance2.zpk';(D/(B+'-install-url.txt')).write_text(url)
q=QrCodeWidget(url,barLevel='M');q.qr.make();m=q.qr.modules;n=len(m);qr=Image.new('RGB',((n+8)*8,)*2,'white');draw=ImageDraw.Draw(qr)
for y,row in enumerate(m):
 for x,v in enumerate(row):
  if v:draw.rectangle(((x+4)*8,(y+4)*8,(x+5)*8-1,(y+5)*8-1),fill='black')
qr.save(D/(B+'-zepp-qr.png'))
T=ROOT/'verify-grey';T.mkdir(exist_ok=True)
for n,b in files.items():p=T/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
# Exact alpha and pixel-index preservation for every dynamic progress frame.
for n,b in base.items():
 if '_ring_' in n:
  assert b[1088:]==files[n][1088:];assert np.array_equal(np.frombuffer(b[64:1088],np.uint8).reshape(256,4)[:,3],np.frombuffer(files[n][64:1088],np.uint8).reshape(256,4)[:,3])
print('Built',B,'appId',manifest['app']['appId'],'; progress frame indices and alpha unchanged')
