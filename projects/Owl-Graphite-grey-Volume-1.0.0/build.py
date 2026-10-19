from pathlib import Path
import io,json,zipfile,time
import numpy as np
from PIL import Image,ImageDraw
from reportlab.graphics.barcode.qr import QrCodeWidget
P=Path(__file__).resolve().parent;ROOT=P.parents[1];D=ROOT/'dist';B='Owl-Graphite-grey-Volume-v1.0.0'
ns={};s=(P.parent/'Owl-Graphite-Color-1.0.9/build.py').read_text();exec(s[:s.index('with zipfile.ZipFile')].replace('P=Path(__file__).resolve().parent','P=Path('+repr(str(P))+')'),ns)
encode,decode=ns['encode'],ns['decode']
def archive(items):
 b=io.BytesIO()
 with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED) as z:
  for n,v in items.items():z.writestr(n,v)
 return b.getvalue()
with zipfile.ZipFile(D/'Owl-Graphite-grey-v1.0.1-RU-Balance2.zpk') as z:
 with zipfile.ZipFile(io.BytesIO(z.read('device.zip'))) as d:base={n:d.read(n) for n in d.namelist()}
files=dict(base);m=json.loads(files['app.json']);m['app'].update(appId=10622121,appName='Owl Graphite grey Volume',version={'code':1,'name':'1.0.0'});m['i18n']['en-US']['appName']='Owl Graphite grey Volume';m['packageInfo']['timeStamp']=int(time.time());mb=json.dumps(m,ensure_ascii=False).encode();files['app.json']=mb;(P/'app.json').write_bytes(mb)
for n,src in [('app.js','app.js'),('watchface/index.js','watchface.js')]:files[n]=(P/src).read_bytes()
# Seven radial steel rims, rasterized directly into the native background.
# Reuse the original palette and header. All indices outside the seven circle regions are exact.
import struct
CIRCLES=[(240,115,69,5),(116,240,69,5),(364,240,69,5),
         (124,124,32,4),(356,124,32,4),(124,356,32,4),(356,356,32,4)]
def rims(blob,aod=False):
 out=bytearray(blob);pw,h=struct.unpack_from('<HH',out,12);w=struct.unpack_from('<I',out,22)[0]
 pal=np.frombuffer(out,np.uint8,offset=64,count=1024).reshape(256,4)
 indices=np.frombuffer(out,np.uint8,offset=1088).reshape(h,pw)
 original=indices.copy();yy,xx=np.mgrid[:h,:w];mask=np.zeros((h,w),bool)
 # Move the complete pulse circle 5 px inward so its full-width rim clears the bezel.
 disk=np.hypot(xx-240+.5,yy-115+.5)<69
 indices[:,:w][disk]=original[np.maximum(yy[disk]-5,0),xx[disk]];mask|=disk
 # Add smooth steel greys only in unused palette slots; existing pixels retain their colours.
 unused=[i for i in range(256) if i not in set(original.ravel())]
 for i,v in zip(unused,np.linspace(0,220,min(128,len(unused))).round().astype(int)):pal[i]=[v,v,v,255]
 choices=np.where((pal[:,3]>=254)&(pal[:,:3].max(1)-pal[:,:3].min(1)<=8))[0]
 assert len(choices)>=8
 for cx,cy,r,width in CIRCLES:
  dx=xx-cx+.5;dy=yy-cy+.5;rad=np.hypot(dx,dy)
  inner=r-(4 if r==32 else 2);outer=r+width;sel=(rad>=inner)&(rad<outer)
  t=(rad-inner)/(outer-inner);light=np.clip(-(dx+dy)/(np.maximum(rad,1)*1.414),-1,1)
  # Dark inner wall, broad convex steel shoulder, bright lip, dark outer wall.
  knots=[0,.10,.19,.32,.48,.65,.76,.83,.90,1]
  shades=[12,22,135,115,85,55,140,185,45,8]
  value=np.interp(t,knots,shades)+light*(14+35*np.sin(np.clip(t,0,1)*np.pi))
  value=np.clip(value,5,210)*(0.36 if aod else 1)
  desired=np.repeat(value[sel,None],3,axis=1)
  nearest=((pal[choices,:3].astype(float)[None,:,:]-desired[:,None,:])**2).sum(2).argmin(1)
  indices[:,:w][sel]=choices[nearest];mask|=sel
 assert np.array_equal(original[:,:w][~mask],indices[:,:w][~mask])
 assert blob[:64]==bytes(out[:64]);assert all(blob[64+i*4:68+i*4]==bytes(out[64+i*4:68+i*4]) for i in map(int,set(original.ravel())))
 return bytes(out)
for prefix in ['', 'aod_']:
 key='assets/'+prefix+'background.png';files[key]=rims(base[key],bool(prefix))
for n,v in base.items():
 if n.startswith('assets/') and not n.endswith('/background.png') and not n.endswith('/aod_background.png'):assert files[n]==v,n
(D/(B+'-RU-Balance2.zpk')).write_bytes(archive({'device.zip':archive(files),'app-side.zip':archive({'app.json':mb})}))
url='zpkd1://raw.githubusercontent.com/lepilinvitold-boop/Amazfit-watchfaces/owl-graphite-grey-volume-1.0.0/dist/'+B+'-RU-Balance2.zpk';(D/(B+'-install-url.txt')).write_text(url)
q=QrCodeWidget(url,barLevel='M');q.qr.make();matrix=q.qr.modules;n=len(matrix);qr=Image.new('RGB',((n+8)*8,)*2,'white');draw=ImageDraw.Draw(qr)
for y,row in enumerate(matrix):
 for x,v in enumerate(row):
  if v:draw.rectangle(((x+4)*8,(y+4)*8,(x+5)*8-1,(y+5)*8-1),fill='black')
qr.save(D/(B+'-zepp-qr.png'))
T=ROOT/'verify-grey-volume';T.mkdir(exist_ok=True)
for n,v in files.items():p=T/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(v)
print('Built',B,'; seven raised rims; other dial assets and background pixels outside circle regions unchanged; appId:',m['app']['appId'])

# Previews assembled from the exact installed resources.
def preview(aod=False,missing=False):
 prefix='aod_' if aod else ''
 def asset(n):return decode(files['assets/'+prefix+n+'.png'])
 im=asset('background')
 def paste(n,x,y):im.alpha_composite(asset(n),(x,y))
 def digits(t,font,x,y,width=None):
  imgs=[asset(font+'_'+c) if c.isdigit() else asset('range_sep' if c=='–' else 'dot') for c in t]
  total=sum(a.width for a in imgs);x=round(x+(width-total)/2) if width else x
  for a in imgs:im.alpha_composite(a,(x,y));x+=a.width
 for n,x,y in [('graph_ring_15',295,171),('heart_ring_0' if missing else 'heart_ring_12',171,46),('stress_ring_0' if missing else 'stress_ring_14',47,171),('calorie_ring_10',47,171),('phone_icon',103,335),('workout_icon',103,103),('alarm_icon',336,336),('weather_3',186,300)]:paste(n,x,y)
 for t,f,x,y,w in [('271','detail',70,262,92),('7650','circle',314,211,100),('5.84','detail',318,262,92),('77','battery',331,117,50),('22','circle',216,303,70),('10','time',178,350,None),('08','time',246,350,None),('19','date',188,404,None),('48–133','range',191,130,98)]:digits(t,f,x,y,w)
 if missing:paste('missing_dash',228,94);paste('missing_dash',104,222)
 else:digits('89','circle',202,82,76);digits('73','small',70,210,92)
 paste('colon',234,350);paste('week_0',230,404);paste('graph_degree',278,303)
 def hand(n,px,py,angle):
  a=asset(n);canvas=Image.new('RGBA',(960,960));canvas.alpha_composite(a,(480-px,480-py));canvas=canvas.rotate(-angle,resample=Image.Resampling.BICUBIC,center=(480,480));im.alpha_composite(canvas.crop((240,240,720,720)))
 hand('hour',21,156,304);hand('minute',19,192,48)
 if not aod:hand('second',6,222,210)
 paste('cap',227,227);return im
preview().save(D/(B+'-preview.png'));preview(True).save(D/(B+'-AOD-preview.png'));preview(missing=True).save(D/(B+'-missing-preview.png'))

# Verify that the rings remain separate and inside the inner bezel.
for i,(x,y,r,w) in enumerate(CIRCLES):
 assert np.hypot(x-240,y-240)+r+w<201
 for xx,yy,rr,ww in CIRCLES[i+1:]:assert np.hypot(x-xx,y-yy)>r+w+rr+ww
# Updated installation thumbnail; normal/AOD dial resources outside rims unchanged.
files['assets/preview.png']=encode(preview().resize((240,240),Image.Resampling.LANCZOS))
(D/(B+'-RU-Balance2.zpk')).write_bytes(archive({'device.zip':archive(files),'app-side.zip':archive({'app.json':mb})}))
(T/'assets/preview.png').write_bytes(files['assets/preview.png'])
