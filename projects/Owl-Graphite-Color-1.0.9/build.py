from pathlib import Path
import io,json,math,struct,zipfile
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from reportlab.graphics.barcode.qr import QrCodeWidget
P=Path(__file__).resolve().parent; ROOT=P.parents[1];D=ROOT/'dist'; B='Owl-Graphite-Color-v1.0.9'; S=4
def decode(b):
 w,h=struct.unpack_from('<HH',b,12);aw=struct.unpack_from('<I',b,22)[0];pal=np.frombuffer(b[64:1088],np.uint8).reshape(256,4);a=pal[np.frombuffer(b[1088:],np.uint8).reshape(h,w)][:,:aw].copy();al=a[:,:,3:4].astype(float);a[:,:,:3]=np.clip(np.divide(a[:,:,:3].astype(float)*255,al,out=np.zeros_like(a[:,:,:3],dtype=float),where=al>0),0,255).astype('uint8');return Image.fromarray(a)
def encode(im):
 im=im.convert('RGBA');w,h=im.size;pw=(w+15)//16*16;tmp=Image.new('RGBA',(pw,h));tmp.alpha_composite(im);q=tmp.quantize(colors=256,method=Image.Quantize.FASTOCTREE);pal=np.zeros((256,4),np.uint8);e=np.frombuffer(q.palette.palette,np.uint8).reshape(-1,4);pal[:len(e)]=e;pal[:,:3]=np.rint(pal[:,:3].astype(float)*pal[:,3:4]/255).astype('uint8');head=bytearray(64);head[:18]=bytes.fromhex('2e0101000000012000000000000000000820');struct.pack_into('<HH',head,12,pw,h);head[18:22]=b'SOMH';struct.pack_into('<I',head,22,w);return bytes(head)+pal.tobytes()+np.array(q).tobytes()
with zipfile.ZipFile(D/'Owl-Graphite-Color-v1.0.8-fixed-RU-Balance2.zpk') as z:
 with zipfile.ZipFile(io.BytesIO(z.read('device.zip'))) as d: files={n:d.read(n) for n in d.namelist()}
manifest=json.loads(files['app.json']);manifest['app']['appId']=10622109;manifest['app']['appName']='Owl Graphite Color Bezel';manifest['app']['version']={'code':4,'name':'1.0.9'};manifest['i18n']['en-US']['appName']=manifest['app']['appName'];manifest['packageInfo']['timeStamp']=1791897600
# Retain the proven API 1 bootstrap from the working 1.0.8 package.
mb=json.dumps(manifest,ensure_ascii=False).encode();files['app.json']=mb;(P/'app.json').write_bytes(mb)
# The inner content remains byte-for-byte unchanged inside radius 201.
y,x=np.mgrid[:480*S,:480*S];dx=x/S-239.5;dy=y/S-239.5;r=np.hypot(dx,dy);light=-1.18
# Broad directional metal lighting, outer chamfer, inner sloped lip and
# a recessed vertical wall: depth occupies real radial width, not one outline.
v=57+18*light+1.2*np.sin(r*15)
v=np.where(r>=234,112+50*light-15*(r-234),v)
v=np.where(r>=238,30+12*light,v)
v=np.where((r>=211)&(r<216),94+40*light-8*(r-211),v)
v=np.where((r>=207)&(r<211),20+8*light+5*(r-207),v)
v=np.where((r>=201)&(r<207),9+3*light,v)
v=np.where((r>=200.5)&(r<202),66+24*light,v)
v=np.where(r>=211,v*.58,v)
# Raised outer edge of the inner chapter ring, over a uniform vertical wall.
v=np.where((r>=207.8)&(r<210.7),18+14*(r-207.8),v)
v=np.where((r>=210.7)&(r<211.6),160,v)
v=np.where((r>=211.6)&(r<212.4),65,v)
v=np.where((r>=212.4)&(r<214.7),4,v)
a=np.zeros((480*S,480*S,4),np.uint8);a[:,:,:3]=np.clip(v[:,:,None],0,255);a[:,:,3]=np.where((r>=201)&(r<=239),255,0)
ring=Image.fromarray(a);draw=ImageDraw.Draw(ring);BLUE=(67,112,154,255);WHITE=(233,235,237,255)
def polar(rad,ang):t=math.radians(ang);return ((240+rad*math.sin(t))*S,(240-rad*math.cos(t))*S)
def line(rad1,rad2,ang,color,width):draw.line([polar(rad1,ang),polar(rad2,ang)],fill=color,width=round(width*S))
fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def text(t,rad,ang,size,color,width=None):
 f=ImageFont.truetype(fontpath,round(size*S));b=f.getbbox(t);im=Image.new('RGBA',(b[2]-b[0],b[3]-b[1]));ImageDraw.Draw(im).text((-b[0],-b[1]),t,font=f,fill=color)
 if width:im=im.resize((round(width*S),im.height),Image.Resampling.LANCZOS)
 im=im.rotate(-(ang-180 if 90<ang%360<270 else ang),Image.Resampling.BICUBIC,expand=True);px,py=polar(rad,ang);ring.alpha_composite(im,(round(px-im.width/2),round(py-im.height/2)))
# 60 intervals, strong marks at precisely 0,5,10,...55 seconds.
for sec in range(60):line(203,210 if sec%5==0 else 207.3,sec*6,(250,250,250,255) if sec%5==0 else (202,207,211,255),2.4 if sec%5==0 else .7)
for sec in range(0,60,5):text('60' if sec==0 else f'{sec:02}',225,sec*6,15,WHITE)
for sec in [17.5,27.5,32.5,42.5,47.5,57.5]:line(221,229,sec*6,WHITE,1.4)
# Three raised segments, with one notch per SECOND; spacing is exactly 6 degrees.
for lo,hi in [(6,24),(36,54),(66,84)]:
 draw.arc((14*S,14*S,466*S,466*S),lo-90,hi-90,fill=BLUE,width=7*S)
 for ang in range(lo,hi+1,6):line(220,230,ang,BLUE,2.7)
# All captions use the same 20-degree ink span and equal 5-degree gaps
# to the equal-width neighbouring number cells. Glyphs follow the arc.
def caption(t,center):
 size=11;f=ImageFont.truetype(fontpath,round(size*S));widths=[f.getbbox(ch)[2]-f.getbbox(ch)[0] for ch in t];widths=[v/S for v in widths]
 total=225*math.radians(21);gap=(total-sum(widths))/(len(t)-1);offset=-total/2;direction=-1 if 90<center<270 else 1
 for ch,w in zip(t,widths):
  text(ch,225,center+direction*math.degrees((offset+w/2)/225),size,BLUE);offset+=w+gap
# Outer bezel has no captions and no touch zones.
ring=ring.resize((480,480),Image.Resampling.LANCZOS)
yy,xx=np.mgrid[:480,:480];mask=np.hypot(xx-239.5,yy-239.5)>=201
def replace(im):
 im=im.convert('RGBA');ar=np.array(im);ar[mask]=0;im=Image.fromarray(ar);im.alpha_composite(ring);return im
bg=replace(decode(files['assets/background.png']));files['assets/background.png']=encode(bg)
ad=np.array(bg);ad[:,:,:3]=(ad[:,:,:3]*.28).astype('uint8');files['assets/aod_background.png']=encode(Image.fromarray(ad))
preview=replace(Image.open(D/'Owl-Graphite-Color-v1.0.8-fixed-preview.png'));preview.save(D/(B+'-preview.png'));files['assets/preview.png']=encode(preview.resize((240,240),Image.Resampling.LANCZOS))
files['watchface/index.js']=(P/'watchface.js').read_bytes();files['assets/tap_bezel.png']=encode(Image.new('RGBA',(1,1)))
files['app.js']=(P/'app.js').read_bytes()
# Full-size, almost invisible button images, rather than mismatched clipped
# image-click resources or very narrow rows.
import re
hit_targets=json.loads(re.search(r'const taps = (.*)',(P/'watchface.js').read_text()).group(1))
for name,x,y,w,h,url in hit_targets:files['assets/hit_'+name+'.png']=encode(Image.new('RGBA',(w,h),(0,0,0,1)))

def archive(items):
 b=io.BytesIO()
 with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED) as z:
  for n,data in items.items():z.writestr(n,data)
 return b.getvalue()
(D/(B+'-RU-Balance2.zpk')).write_bytes(archive({'device.zip':archive(files),'app-side.zip':archive({'app.json':mb})}))
(D/(B+'-uniform-bezel-RU-Balance2.zpk')).write_bytes((D/(B+'-RU-Balance2.zpk')).read_bytes())
url='zpkd1://raw.githubusercontent.com/lepilinvitold-boop/Amazfit-watchfaces/owl-graphite-color-1.0.9/dist/'+B+'-uniform-bezel-RU-Balance2.zpk';q=QrCodeWidget(url,barLevel='M');q.qr.make();m=q.qr.modules;n=len(m);qr=Image.new('RGB',((n+8)*8,)*2,'white');qd=ImageDraw.Draw(qr)
for y,row in enumerate(m):
 for x,v in enumerate(row):
  if v:qd.rectangle(((x+4)*8,(y+4)*8,(x+5)*8-1,(y+5)*8-1),fill='black')
qr.save(D/(B+'-zepp-qr.png'));qr.save(D/(B+'-uniform-bezel-zepp-qr.png'))
print('Built',B,'appId',manifest['app']['appId'])
