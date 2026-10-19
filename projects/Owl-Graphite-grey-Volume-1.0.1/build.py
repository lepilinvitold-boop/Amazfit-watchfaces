from pathlib import Path
import io,zipfile
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;ROOT=P.parents[1];D=ROOT/'dist'
codec=P.parent/'Owl-Graphite-Color-1.0.9/build.py';s=codec.read_text();ns={'__file__':str(codec)};exec(s[:s.index('with zipfile.ZipFile')],ns);decode=ns['decode']
with zipfile.ZipFile(D/'Owl-Graphite-grey-Volume-v1.0.0-RU-Balance2.zpk') as z:
 with zipfile.ZipFile(io.BytesIO(z.read('device.zip'))) as d:files={n:d.read(n) for n in d.namelist()}
def asset(n):return decode(files['assets/'+n+'.png'])

import struct,json,time
from PIL import ImageDraw
from reportlab.graphics.barcode.qr import QrCodeWidget
B='Owl-Graphite-grey-Volume-v1.0.1';encode=ns['encode']
base=dict(files)
CIRCLES=[(240,115,65,74),(116,240,65,74),(364,240,65,74),(124,124,27,36),(356,124,30,36),(124,356,27,36),(356,356,27,36)]
def background(blob,aod=False):
 source=decode(blob);paint=source.copy();mask=np.zeros((480,480),bool)
 # Move only the pulse divider and MIN-MAX label up 10 px, unchanged glyph pixels.
 block=source.crop((190,113,290,129));paint.paste(source.getpixel((240,150)),(190,103,290,129));paint.paste(block,(190,103));mask[103:129,190:290]=True
 yy,xx=np.mgrid[:480,:480]
 for cx,cy,inner,outer in CIRCLES:
  S=4;size=2*outer+4;y,x=np.mgrid[:size*S,:size*S];dx=(x+.5)/S-size/2;dy=(y+.5)/S-size/2;r=np.hypot(dx,dy);t=(r-inner)/(outer-inner)
  light=-(dx+dy)/np.maximum(r,1)/np.sqrt(2)
  value=np.interp(t,[0,.07,.13,.20,.35,.60,.73,.80,.87,.94,1],[6,10,55,180,125,82,62,105,28,10,3])
  value+=light*(18+45*np.sin(np.clip(t,0,1)*np.pi));value*=.36 if aod else 1
  a=np.zeros((*r.shape,4),np.uint8);a[:,:,:3]=np.clip(value[:,:,None],1,225).astype(np.uint8);a[:,:,3]=np.where((r>=inner)&(r<outer),255,0)
  patch=Image.fromarray(a).resize((size,size),Image.Resampling.LANCZOS);paint.alpha_composite(patch,(cx-size//2,cy-size//2))
  rad=np.hypot(xx-cx+.5,yy-cy+.5);mask|=(rad>=inner-1)&(rad<=outer+1)
 # Only changed circle pixels get new indices. Preserve palette and every other pixel.
 out=bytearray(blob);pw,h=struct.unpack_from('<HH',out,12);pal=np.frombuffer(out,np.uint8,offset=64,count=1024).reshape(256,4);indices=np.frombuffer(out,np.uint8,offset=1088).reshape(h,pw);old=indices.copy()
 rgba=np.array(paint);alpha=rgba[:,:,3:4].astype(float);premul=rgba.copy();premul[:,:,:3]=np.rint(rgba[:,:,:3]*alpha/255).astype(np.uint8)
 changed=mask&np.any(np.array(source)!=rgba,axis=2)
 values=premul[changed].astype(float);choices=np.where(pal[:,3]>=254)[0]
 # Quantize only modified pixels, using the existing fine steel ramp.
 for start in range(0,len(values),2000):
  v=values[start:start+2000];nearest=((pal[choices].astype(float)[None,:,:]-v[:,None,:])**2).sum(2).argmin(1)
  positions=np.flatnonzero(changed)[start:start+len(v)];indices[:,:480].flat[positions]=choices[nearest]
 assert np.array_equal(old[:,:480][~mask],indices[:,:480][~mask])
 assert blob[:1088]==bytes(out[:1088])
 return bytes(out)
for prefix in ['', 'aod_']:
 files['assets/'+prefix+'background.png']=background(base['assets/'+prefix+'background.png'],bool(prefix))
 for name in ['heart','graph','stress','calorie']:
  for level in range(21):
   key='assets/'+prefix+name+'_ring_'+str(level)+'.png';a=decode(base[key]);a=a.resize((130,130),Image.Resampling.LANCZOS);tile=Image.new('RGBA',(138,138));tile.alpha_composite(a,(4,4));files[key]=encode(tile)
# All font files, units, labels in the unchanged inner areas, icons and hands retained.
for key,value in base.items():
 if key.startswith('assets/') and not any(part in key for part in ['background.png','heart_ring_','graph_ring_','stress_ring_','calorie_ring_','preview.png']):assert files[key]==value,key
for i,(x,y,inner,outer) in enumerate(CIRCLES):
 assert np.hypot(x-240,y-240)+outer<201
 for xx,yy,ii,oo in CIRCLES[i+1:]:assert np.hypot(x-xx,y-yy)>outer+oo
im=asset('background')
# PREVIEW_BODY_START
def paste(n,x,y,scale=False):
 a=asset(n)
 im.alpha_composite(a,(x,y))
for n,x,y in [('graph_ring_15',295,171),('heart_ring_12',171,46),('stress_ring_14',47,171),('calorie_ring_10',47,171)]:paste(n,x,y,True)
for n,x,y in [('phone_icon',103,335),('workout_icon',103,103),('alarm_icon',336,336),('weather_3',186,300)]:paste(n,x,y)
def digits(t,font,x,y,width=None):
 imgs=[asset(font+'_'+c) if c.isdigit() else asset('range_sep' if c=='–' else 'dot') for c in t];total=sum(a.width for a in imgs);x=round(x+(width-total)/2) if width else x
 for a in imgs:im.alpha_composite(a,(x,y));x+=a.width
for t,f,x,y,w in [('271','detail',70,262,92),('7650','circle',314,211,100),('5.84','detail',318,262,92),('77','battery',331,117,50),('22','circle',216,303,70),('10','time',178,350,None),('08','time',246,350,None),('19','date',188,404,None),('48–133','range',191,119,98),('89','circle',202,82,76),('73','small',70,210,92)]:digits(t,f,x,y,w)
paste('colon',234,350);paste('week_0',230,404);paste('graph_degree',278,303)
def hand(n,px,py,angle):
 a=asset(n);canvas=Image.new('RGBA',(960,960));canvas.alpha_composite(a,(480-px,480-py));canvas=canvas.rotate(-angle,resample=Image.Resampling.BICUBIC,center=(480,480));im.alpha_composite(canvas.crop((240,240,720,720)))
hand('hour',21,156,304);hand('minute',19,192,48);hand('second',6,222,210);paste('cap',227,227)
im.save(D/(B+'-preview.png'))
# PREVIEW_BODY_END

# AOD preview uses the same exact frame assets and independently dimmed rims.
normal_files=files
# Render with the shared exact preview code, selecting native AOD assets and omitting seconds.
def render_aod():
 global im,asset
 original_asset=asset;asset=lambda n:decode(files['assets/aod_'+n+'.png']);im=asset('background')
 exec(P.joinpath('preview-body.py').read_text().replace("hand('second',6,222,210);",'').replace("B+'-preview.png'","B+'-AOD-preview.png'"),globals())
 asset=original_asset
P.joinpath('preview-body.py').write_text(P.joinpath('build.py').read_text().split('# PREVIEW_BODY_START\n')[1].split('# PREVIEW_BODY_END')[0])
render_aod()
m=json.loads(files['app.json']);m['app']['version']={'code':2,'name':'1.0.1'};m['packageInfo']['timeStamp']=int(time.time());mb=json.dumps(m,ensure_ascii=False).encode();files['app.json']=mb;(P/'app.json').write_bytes(mb)
files['app.js']=(P/'app.js').read_bytes();files['watchface/index.js']=(P/'watchface.js').read_bytes()
preview=Image.open(D/(B+'-preview.png'));files['assets/preview.png']=encode(preview.resize((240,240),Image.Resampling.LANCZOS))
def archive(items):
 b=io.BytesIO()
 with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED) as z:
  for n,v in items.items():z.writestr(n,v)
 return b.getvalue()
(D/(B+'-RU-Balance2.zpk')).write_bytes(archive({'device.zip':archive(files),'app-side.zip':archive({'app.json':mb})}))
url='zpkd1://raw.githubusercontent.com/lepilinvitold-boop/Amazfit-watchfaces/owl-graphite-grey-volume-1.0.1/dist/'+B+'-RU-Balance2.zpk';(D/(B+'-install-url.txt')).write_text(url)
q=QrCodeWidget(url,barLevel='M');q.qr.make();matrix=q.qr.modules;n=len(matrix);qr=Image.new('RGB',((n+8)*8,)*2,'white');draw=ImageDraw.Draw(qr)
for y,row in enumerate(matrix):
 for x,v in enumerate(row):
  if v:draw.rectangle(((x+4)*8,(y+4)*8,(x+5)*8-1,(y+5)*8-1),fill='black')
qr.save(D/(B+'-zepp-qr.png'))
T=ROOT/'verify-grey-volume-1.0.1';T.mkdir(exist_ok=True)
for n,v in files.items():p=T/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(v)
print('Built',B,'; fonts/icons/hands unchanged; widened bevels and reduced progress tracks; appId',m['app']['appId'])
