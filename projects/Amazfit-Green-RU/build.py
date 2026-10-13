"""Reproducible 480px native Zepp dial, rebuilt from the supplied reference."""
from pathlib import Path
import io,json,math,struct,zipfile,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from scipy.ndimage import distance_transform_edt
from reportlab.graphics.barcode.qr import QrCodeWidget
P=Path(__file__).resolve().parent;A=P/'assets';D=P.parents[1]/'dist';V='1.0.3';B='Amazfit-Green-RU-v'+V
if A.exists():shutil.rmtree(A)
A.mkdir();D.mkdir(exist_ok=True)
SOURCE={};S=4;GREEN=(16,188,61,255);WHITE=(235,236,237,255)
F='/usr/share/fonts/opentype/urw-base35/NimbusSansNarrow-BoldOblique.otf'
REG='/usr/share/fonts/opentype/urw-base35/NimbusSansNarrow-Regular.otf'
BOLD='/usr/share/fonts/opentype/urw-base35/NimbusSans-Bold.otf'
def image(w,h):return Image.new('RGBA',(w*S,h*S))
def font(n,kind=F):return ImageFont.truetype(kind,round(n*S))
def store(name,im):
 im=im.resize((im.width//S,im.height//S),Image.Resampling.LANCZOS);im.save(A/(name+'.png'));SOURCE[name+'.png']=im;return im
class Draw:
 def __init__(self,im):self.im=im;self.d=ImageDraw.Draw(im)
 def line(self,p,c,w=1):self.d.line([(round(x*S),round(y*S)) for x,y in p],fill=c,width=max(1,round(w*S)),joint='curve')
 def poly(self,p,c):self.d.polygon([(round(x*S),round(y*S)) for x,y in p],fill=c)
 def ellipse(self,b,c=None,o=None,w=1):self.d.ellipse(tuple(round(x*S) for x in b),fill=c,outline=o,width=round(w*S))
 def arc(self,b,start,end,c,w=1):self.d.arc(tuple(round(x*S) for x in b),start,end,fill=c,width=round(w*S))
 def text(self,t,x,y,size,c=WHITE,angle=0,kind=F,shadow=False):
  f=font(size,kind);box=f.getbbox(t);layer=Image.new('RGBA',(box[2]-box[0]+8*S,box[3]-box[1]+8*S));dr=ImageDraw.Draw(layer)
  if shadow:dr.text((4*S-box[0]+S,4*S-box[1]+S),t,font=f,fill=(0,0,0,240),stroke_width=S,stroke_fill=(0,0,0,240))
  dr.text((4*S-box[0],4*S-box[1]),t,font=f,fill=c,stroke_width=round(.45*S) if shadow else 0,stroke_fill=c)
  if angle:layer=layer.rotate(-angle,resample=Image.Resampling.BICUBIC,expand=True)
  self.im.alpha_composite(layer,(round(x*S-layer.width/2),round(y*S-layer.height/2)))
def arc_text(d,t,r,angle,size,c,kind,tracking=.4):
 f=font(size,kind);adv=[f.getlength(ch)/S+tracking for ch in t];total=sum(adv)-tracking
 direction=-1 if 90<angle%360<270 else 1;offset=-total/2
 for ch,w in zip(t,adv):
  theta=angle+direction*math.degrees((offset+(w-tracking)/2)/r);px,py=polar(r,theta)
  rotation=theta if direction==1 else theta-180
  d.text(ch,px,py,size,c,angle=rotation,kind=kind)
  offset+=w

def polar(r,a,cx=240,cy=240):a=math.radians(a);return cx+r*math.sin(a),cy-r*math.cos(a)
def hour_number(d,t,cx,cy):
 # Squared condensed oblique glyphs, with a broad stem and narrow counters like the reference.
 widths={'1':15,'0':24,'2':24,'9':24};cap=45;w=sum(widths[c] for c in t)+3*(len(t)-1)+8
 mask=Image.new('L',(w*S,(cap+4)*S));dr=ImageDraw.Draw(mask);xx=0
 for c in t:
  def poly(p):dr.polygon([((x+xx)*S,y*S) for x,y in p],fill=255)
  def rect(b,fill=255,radius=0):dr.rounded_rectangle(tuple(int(v*S) for v in (b[0]+xx,b[1],b[2]+xx,b[3])),radius=int(radius*S),fill=fill)
  if c=='1':poly([(6,0),(15,0),(15,45),(6,45),(6,9),(0,9),(0,4)])
  elif c=='0':rect((0,0,24,45),radius=5);rect((8,8,16,37),0,radius=1.5)
  elif c=='2':poly([(5,0),(19,0),(24,5),(24,19),(21,24),(8,36),(24,36),(24,45),(0,45),(0,34),(15,18),(16,15),(16,8),(8,8),(8,14),(0,14),(0,5)])
  elif c=='9':poly([(5,0),(19,0),(24,5),(24,39),(19,45),(1,45),(1,37),(14,37),(16,35),(16,27),(5,27),(0,22),(0,5)]);rect((8,8,16,19),0,radius=1)
  xx+=widths[c]+3
 mask=mask.transform(mask.size,Image.Transform.AFFINE,(1,.16,-7.2*S,0,1,0),resample=Image.Resampling.BICUBIC)
 a=np.array(mask);opaque=a>128;hi=opaque&(~np.roll(opaque,2,0)|~np.roll(opaque,2,1));lo=opaque&(~np.roll(opaque,-2,0)|~np.roll(opaque,-2,1))
 rgba=np.zeros((*a.shape,4),np.uint8);rgba[:,:,:3]=231;rgba[:,:,:3][hi]=255;rgba[:,:,:3][lo]=154;rgba[:,:,3]=a
 body=Image.fromarray(rgba);shadow=Image.new('RGBA',body.size,(0,0,0,0));shadow.putalpha(mask.filter(ImageFilter.GaussianBlur(.6*S)))
 px=round(cx*S-body.width/2);py=round(cy*S-cap*S/2)
 d.im.alpha_composite(shadow,(px+S,py+2*S));d.im.alpha_composite(body,(px,py))

# One-piece circular metal chapter ring with outer chamfer and inner vertical wall.
bg=image(480,480)
y,x=np.mgrid[:480*S,:480*S];xx=x/S-240;yy=y/S-240;r=np.hypot(xx,yy)
light=np.divide(-xx-yy,np.maximum(r,1)*math.sqrt(2));angular=.5+.5*light
shade=np.clip(39+4*light,0,255)
# Metal face, outer lip, steep inner wall, then recessed dial surface.
shade=np.where((r>=210)&(r<233),52+22*angular,shade)
shade=np.where((r>=233)&(r<237),68+83*angular+15*np.sin((r-233)/4*math.pi),shade)
shade=np.where((r>=237)&(r<239),20+46*angular,shade)
shade=np.where(r>=239,8,shade)
shade=np.where((r>=202)&(r<210),12+34*(r-202)/8+27*(1-angular),shade)
shade=np.where((r>=200)&(r<202),10+14*(1-angular),shade)
shade+=np.where((r>=210)&(r<233),.6*np.sin(r*3),0)
a=np.zeros((480*S,480*S,4),np.uint8);a[:,:,3]=255
for c in range(3):a[:,:,c]=np.clip(shade,0,255).astype('uint8')
bg=Image.fromarray(a);d=Draw(bg)
for radius,c,w in [(237.5,'#505357',.45),(232.7,'#242729',.5),(210.3,'#a0a1a2',.5),(201.7,'#0b0b0c',.75),(199.7,'#68696a',.45),(188,'#454545',.6)]:d.ellipse((240-radius,240-radius,240+radius,240+radius),None,c,w)
# Minute numerals: wider upright type, tangent orientation exactly as on the reference.
for i in range(12):
 angle=i*30;tx,ty=polar(221.5,angle);d.text('60' if i==0 else f'{5*i:02}',tx,ty,24,angle=angle,kind='/usr/share/fonts/opentype/urw-base35/NimbusSans-Regular.otf')
# Original three green comb-shaped arcs are preserved in the free right-hand sectors.
for start,end in [(6,25),(36,55),(66,85)]:
 for i in np.linspace(start,end,100):d.line([polar(231,i),polar(225,i)],GREEN,1.1)
 for i in [start,start+6,start+12,end]:d.line([polar(231,i),polar(219,i)],GREEN,2.4)
# No screw heads or decorative dots. Nine exact requested midpoint labels.
outer_labels=[('ПУЛЬС',345),('ШАГИ',315),('ДИСТАНЦИЯ',285),('СТРЕСС',255),('БУДИЛЬНИК',225),('СЕКУНДОМЕР',195),('ТАЙМЕР',165),('ТРЕНИРОВКА',135),('КАЛОРИИ',105)]
for label,angle in outer_labels:
 sx,sy=polar(221.5,angle);rotation=angle-180 if 90<angle<270 else angle if angle<=180 else angle-360
 arc_text(d,label,221.5,angle,13.5,GREEN,'/usr/share/fonts/opentype/urw-base35/NimbusSansNarrow-Bold.otf')
# 240 subdivisions with longer fifth and quarter marks.
for i in range(240):
 ang=i*1.5;outer=201;inner=194 if i%4 else 190
 if i%20==0:inner=188
 d.line([polar(inner,ang),polar(outer,ang)],'#727272' if i%4 else '#969696',.7 if i%4 else 1.1)
# Sector contours remain; the removed words ANALOG/SCREEN never enter any raster resource.
for a in [0,30,60,90,270,300,330]:d.line([polar(169,a),polar(186,a)],'#5c5d5e',.7)
for t,angle in [('ПЛЕЕР',285),('БАТАРЕЯ',315),('ТЕЛЕФОН',345)]:
 tx,ty=polar(178,angle);arc_text(d,t,178,angle,9.5,(172,174,176,255),BOLD,.25)
# Raised white hour blocks, with no marks hidden under the lower panel.
for ang in [0,30,60,270,300,330]:
 p=[polar(171,ang-2.1),polar(185,ang-2.1),polar(185,ang+2.1),polar(171,ang+2.1)];d.poly(p,'#bababa');d.line([p[0],p[1],p[2]],'#f1f1f1',1.4)
# Flat, upright baseline with original oblique tall hour glyphs; not rotated around dial.
for number,xx,yy,size in [('12',240,98,61),('1',310,120,63),('2',371,175,63),('9',86,240,63),('10',113,176,63),('11',167,120,63)]:hour_number(d,number,xx,yy)
# Original subtle crosshairs and four green squares retained; MEN text removed.
for p in [[(178,166),(203,166)],[(204,157),(204,180)],[(282,166),(302,166)]]:d.line(p,'#626262',.7)
for sx,sy in [(225,156),(237,156),(225,168),(237,168)]:d.poly([(sx,sy),(sx+8,sy),(sx+8,sy+8),(sx,sy+8)],GREEN)
# Amazfit sits directly under 12, as requested, without moving the numeral.
d.text('Amazfit',240,134,17,kind=BOLD)
# Recessed lower digital panel: traced coordinates, continuous rounded shoulder.
def cubic(p0,p1,p2,p3):
 return [tuple((1-t)**3*p0[j]+3*(1-t)**2*t*p1[j]+3*(1-t)*t*t*p2[j]+t**3*p3[j] for j in [0,1]) for t in np.linspace(0,1,40)]
# Smooth reference silhouette: a horizontal upper-left ledge, diagonal shoulder, round right wall.
panel=[(68,294),(179,294)]+cubic((179,294),(198,294),(209,288),(222,273))+[(276,218)]+cubic((276,218),(285,208),(293,205),(311,205))+[(402,205)]+cubic((402,205),(421,205),(429,225),(429,246))+cubic((429,246),(426,281),(403,325),(373,354))+cubic((373,354),(348,379),(323,397),(289,400))+[(157,400)]+cubic((157,400),(116,383),(85,341),(68,294))
mask=image(480,480);Draw(mask).poly(panel,'white');inside=np.array(mask)[:,:,3]>0
signed=distance_transform_edt(inside)/S
# Border normal supplies directional edge lighting. The dark wall is seven pixels deep.
gy,gx=np.gradient(signed);norm=np.maximum(np.hypot(gx,gy),1e-5);normal_light=np.clip((-gx-gy)/(norm*math.sqrt(2)),-1,1)
wall=12+19*np.clip(1-(signed-2)/5,0,1)+14*np.maximum(0,normal_light)
rim=38+36*np.maximum(0,normal_light)
value=np.where(signed<1.3,rim,np.where(signed<7,wall,0))
arr=np.array(bg)
for c in range(3):arr[:,:,c][inside]=np.clip(value[inside],0,255).astype('uint8')
bg=Image.fromarray(arr);d=Draw(bg)
d.line([(280,285),(407,285)],'#c4c4c4',1.1)
# Eye-like indicator and outlined battery match the two original status symbols.
d.arc((315,232,335,244),180,360,WHITE,1.4);d.arc((315,232,335,244),0,180,WHITE,1.4);d.ellipse((322,232,328,244),WHITE)
d.line([(376,231),(394,231),(394,244),(376,244),(376,231)],WHITE,1.6);d.line([(395,235),(396,235),(396,240)],WHITE,1)
# Lower lock symbol and straight base line.
d.line([(156,405),(326,405)],'#666666',1.4)
store('background',bg)
# Colored condition images, in the official Zepp weather-index order 0..28.
weather_names=['cloudy','showers','snow_showers','sunny','overcast','light_rain','light_snow','moderate_rain','moderate_snow','heavy_snow','heavy_rain','sandstorm','rain_snow','fog','haze','thunderstorms','snowstorm','floating_dust','very_heavy_rain','rain_hail','thunder_hail','heavy_rainstorm','dust','heavy_sandstorm','rainstorm','unknown','cloudy_night','showers_night','clear_night']
for index,condition in enumerate(weather_names):
 im=image(36,25);dr=Draw(im)
 def sun(cx=10,cy=8):
  dr.ellipse((cx-4,cy-4,cx+4,cy+4),'#f2bc45','#ffe2a0',.6)
  for ang in range(0,360,45):
   p1=polar(5.5,ang,cx,cy);p2=polar(7.5,ang,cx,cy);dr.line([p1,p2],'#e9b03b',1)
 def moon(cx=10,cy=8):
  dr.ellipse((cx-6,cy-6,cx+6,cy+6),'#e3ddb5');dr.ellipse((cx-2,cy-8,cx+8,cy+2),(0,0,0,0))
 def cloud(dark=False):
  col='#8e9da8' if dark else '#bbc9d4'
  for box in [(9,6,22,18),(16,9,29,20),(4,10,16,20)]:dr.ellipse(box,col)
  dr.poly([(9,14),(25,14),(25,20),(9,20)],col)
  dr.arc((9,6,22,18),185,280,'#dde6ed',.75);dr.arc((4,10,16,20),90,250,'#e6edf2',.6)
 if index==3:sun(18,12)
 elif index==28:moon(18,12)
 elif index==25:dr.text('?',18,12,25,'#bcc5ca',kind=BOLD)
 else:
  if index in [0,1,2]:sun()
  if index in [26,27]:moon()
  cloud(index in [4,10,15,18,20,21,24])
  if index in [1,5,7,10,12,15,18,19,20,21,24,27]:
   count=1 if index==5 else 2 if index in [1,7,12,15,19,20,27] else 3
   for i in range(count):sx=10+i*7;dr.line([(sx,21),(sx-1.4,24)],'#58aee3',1.3)
  if index in [2,6,8,9,12,16]:
   for sx in ([13] if index==6 else [10,23]):
    for angle in [0,60,120]:dr.line([polar(2.2,angle,sx,22),polar(2.2,angle+180,sx,22)],'#d4effb',.7)
  if index in [15,20]:dr.poly([(23,16),(19,22),(22,22),(20,25),(27,19),(23,19)],'#f2ba46')
  if index in [19,20]:dr.ellipse((26,21,29,24),'#d5edf6')
  if index in [11,13,14,17,22,23]:
   color='#c9a275' if index in [11,17,22,23] else '#a2bac6'
   for yy in [17,21,24]:dr.line([(5,yy),(30,yy)],color,1.1)
 store('condition_'+str(index),im)

# Glyph resources, fixed cell widths preserve numeric alignment.
def glyph(prefix,t,height,width,size,kind=F):
 # Measure INK, including oblique overhang. Preserve a margin on every side.
 f=font(size,kind);box=f.getbbox(t);ref=f.getbbox('0');lw=max(1,box[2]-box[0]);lh=max(1,box[3]-box[1])
 layer=Image.new('RGBA',(lw,lh));ImageDraw.Draw(layer).text((-box[0],-box[1]),t,font=f,fill=WHITE)
 factor=min(1,(height*S-4*S)/max(1,ref[3]-ref[1],box[3]-box[1]));tw=min(lw,(width-2)*S);th=max(1,round(lh*factor));layer=layer.resize((round(tw),th),Image.Resampling.LANCZOS)
 im=image(width,height);yy=2*S+round((box[1]-ref[1])*factor);yy=max(2*S,min(height*S-th-2*S,yy));im.alpha_composite(layer,(round((im.width-tw)/2),yy));return store(prefix,im)
for n in range(10):
 glyph('status_'+str(n),str(n),30,15,34)
 glyph('date_'+str(n),str(n),19,10,24)
 glyph('weather_'+str(n),str(n),24,13,30)
for prefix,h,w,size in [('status',30,14,30),('date',19,8,24),('weather',24,10,30)]:
 for t,name in [('%','percent'),('-','minus'),('.','dot'),('/','slash')]:glyph(prefix+'_'+name,t,h,w,size)
im=image(10,24);dr=Draw(im);dr.ellipse((1,1,7,7),None,WHITE,1.3);store('degree',im)
# Seven-segment time glyphs: custom thin beveled bars, matching original digital display.
segments={0:'abcdef',1:'bc',2:'abdeg',3:'abcdg',4:'bcfg',5:'acdfg',6:'acdefg',7:'abc',8:'abcdefg',9:'abcdfg'}
shapes={'a':[(6,2),(23,2),(26,5),(22,8),(7,8),(4,5)],'g':[(6,24),(23,24),(26,27),(22,30),(7,30),(4,27)],'d':[(6,47),(23,47),(26,50),(22,53),(7,53),(4,50)],'f':[(3,7),(6,10),(6,22),(3,25),(0,22),(0,10)],'b':[(24,7),(27,10),(27,22),(24,25),(21,22),(21,10)],'e':[(3,29),(6,32),(6,44),(3,47),(0,44),(0,32)],'c':[(24,29),(27,32),(27,44),(24,47),(21,44),(21,32)]}
def seven(n,width,height):
 im=image(width,height);dr=Draw(im);scale=height/55
 for s in segments[n]:dr.poly([((x+4.5*(1-y/55))*scale,y*scale) for x,y in shapes[s]],WHITE)
 return im
for n in range(10):store('digital_'+str(n),seven(n,32,55));store('second_'+str(n),seven(n,15,25))
colon=image(13,55);dc=Draw(colon);dc.ellipse((5,23,10,28),WHITE);dc.ellipse((3,40,8,45),WHITE);store('colon',colon)
for i,t in enumerate(['ПОНЕДЕЛЬНИК','ВТОРНИК','СРЕДА','ЧЕТВЕРГ','ПЯТНИЦА','СУББОТА','ВОСКРЕСЕНЬЕ']):
 glyph('week_'+str(i),t,19,109,17 if len(t)>9 else 20)
for n,t in [('am','ДП'),('pm','ПП')]:
 glyph(n,t,25,38,31)
# Long original-style blades with beveled shoulders and tapered, separate counterweights.
for name,length,width,tail in [('hour',114,18,31),('minute',185,18,26)]:
 im=image(44,length+tail+8);dr=Draw(im);cx=22;py=length
 if name=='hour':
  contour=[(cx-4,2),(cx+4,0),(cx+5.7,12),(cx+11,py-18),(cx+4,py-7),(cx+4,py+7),(cx+10,py+18),(cx+8,py+26),(cx,py+31),(cx-9,py+27),(cx-10,py+19),(cx-4,py+7),(cx-4,py-7),(cx-11,py-18),(cx-5.7,12)]
 else:
  contour=[(cx-3,0),(cx+3,0),(cx+5,14),(cx+10.5,py-16),(cx+4,py-5),(cx+4,py+14),(cx,py+26),(cx-5,py+15),(cx-4,py-5),(cx-10.5,py-16),(cx-5,14)]
 dr.poly([(x+1,y+1.5) for x,y in contour],(0,0,0,120));dr.poly(contour,'#cdd0d3')
 dr.line([(cx-4,2),(cx-5.7,12),(cx-11,py-18)],'#f3f4f4',.9)
 dr.line([(cx+5.7,14),(cx+10.5,py-18)],'#999da0',.75)
 dr.poly([(cx-1.65,28),(cx+1.65,28),(cx+1.65,py-15),(cx-1.65,py-15)],'#101213')
 dr.ellipse((cx-4,py-4,cx+4,py+4),'#303336')
 store(name,im)
# Thin solid green seconds, ending exactly at the minute ring.
im=image(12,239);dr=Draw(im);dr.poly([(5,0),(7,0),(7,201),(5,201)],GREEN);dr.poly([(5,201),(7,201),(7,231),(5,231)],'#454545');store('second',im)
im=image(12,12);dr=Draw(im);dr.ellipse((0,0,12,12),'#333333','#171717',1.6);dr.ellipse((4,4,8,8),'#a0a0a0');store('cap',im)
for state in ['open','closed']:
 im=image(28,30);dr=Draw(im);color='#e4ecec' if state=='open' else '#e8bd65'
 dr.arc((7,3,19,17),180,360,color,2)
 if state=='open':dr.line([(7,9),(7,15)],color,2)
 else:dr.line([(7,9),(7,18)],color,2);dr.line([(19,9),(19,18)],color,2)
 dr.poly([(8,15),(24,15),(24,28),(8,28)],color);dr.ellipse((14,19,18,23),'#111111');store('lock_'+state,im)
SOURCE['shield.png']=Image.new('RGBA',(480,480));SOURCE['shield.png'].save(A/'shield.png')
for n,w,h in [('',1,1)]:
 im=Image.new('RGBA',(w,h));im.save(A/'tap.png');SOURCE['tap.png']=im
for n,im in list(SOURCE.items()):
 if n.startswith('tap'):continue
 a=np.array(im);a[:,:,:3]=(a[:,:,:3].astype(float)*.28).astype('uint8');dim=Image.fromarray(a);dim.save(A/('aod_'+n));SOURCE['aod_'+n]=dim
# Byte layout is the official Zepp L8_ARGB8888 TGA/SOMH format, RGBA and 16px padding.
def encode(im):
 im=im.convert('RGBA');w,h=im.size;pw=(w+15)//16*16;tmp=Image.new('RGBA',(pw,h));tmp.alpha_composite(im)
 q=tmp.quantize(colors=256,method=Image.Quantize.FASTOCTREE);idx=np.array(q);raw=q.palette.palette;pal=np.zeros((256,4),np.uint8);entries=np.frombuffer(raw,np.uint8).reshape(-1,4);pal[:len(entries)]=entries
 pal[:,:3]=np.rint(pal[:,:3].astype(float)*(pal[:,3:4]/255)).astype('uint8')
 head=bytearray(64);head[:18]=bytes.fromhex('2e0101000000012000000000000000000820');struct.pack_into('<HH',head,12,pw,h);head[18:22]=b'SOMH';struct.pack_into('<I',head,22,w)
 return bytes(head)+pal.tobytes()+idx.tobytes()
def decode(b):
 w,h=struct.unpack_from('<HH',b,12);aw=struct.unpack_from('<I',b,22)[0];p=np.frombuffer(b[64:1088],np.uint8).reshape(256,4);idx=np.frombuffer(b[1088:],np.uint8).reshape(h,w);a=p[idx][:,:aw].copy();alpha=a[:,:,3:4].astype(float);a[:,:,:3]=np.clip(np.divide(a[:,:,:3].astype(float)*255,alpha,out=np.zeros_like(a[:,:,:3],dtype=float),where=alpha>0),0,255).astype('uint8');return Image.fromarray(a)
manifest={'configVersion':'v2','app':{'appId':10623001,'appName':'Amazfit Green RU','appType':'watchface','version':{'code':4,'name':V},'icon':'preview.png','cover':['preview.png'],'vender':'Vitold personal','description':'Русский циферблат по исходному образцу'},'runtime':{'apiVersion':{'minVersion':'1.0','target':'1.0.1','compatible':'1.0.0'}},'permissions':[],'i18n':{'en-US':{'appName':'Amazfit Green RU'}},'defaultLanguage':'en-US','designWidth':480,'module':{'watchface':{'path':'watchface/index','main':1,'editable':0,'lockscreen':1}},'platforms':[{'name':'Balance 2','deviceSource':v} for v in [9568512,9568513,9568515]],'watchfacePreview':{'icon':'preview.png','size':[]},'packageInfo':{'mode':'production','zpm':'3.4.2'}}
(P/'app.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));mb=json.dumps(manifest,ensure_ascii=False).encode()
resources={n:encode(im) for n,im in SOURCE.items()}
# Preview comes from decoded NATIVE resources, not a separate illustrative mockup.
canvas=decode(resources['background.png'])
def paste(n,x,y):canvas.alpha_composite(decode(resources[n+'.png']),(x,y))
def text(t,prefix,x,y):
 for c in t:
  n={'%':'percent','-':'minus','.':'dot','/':'slash'}.get(c,c);a=decode(resources[prefix+'_'+n+'.png']);canvas.alpha_composite(a,(x,y));x+=a.width
text('83','status',302,250);paste('status_percent',341,250);text('97','status',362,250);paste('status_percent',401,250);text('18','weather',137,242);paste('degree',163,242);paste('condition_0',137,213);paste('pm',122,336)
paste('week_2',143,305);text('14/10/26','date',253,305)
text('12','digital',171,336);paste('colon',235,336);text('42','digital',251,336);text('40','second',319,336)
for name,pivot,angle in [('hour',114,22),('minute',185,252),('second',201,240)]:
 layer=Image.new('RGBA',(480,480));asset=decode(resources[name+'.png']);layer.alpha_composite(asset,(240-(6 if name=='second' else 22),240-pivot));canvas.alpha_composite(layer.rotate(-angle,resample=Image.Resampling.BICUBIC,center=(240,240)))
paste('cap',234,234);paste('lock_open',226,409);canvas.convert('RGB').save(D/(B+'-preview.png'));canvas.resize((240,240),Image.Resampling.LANCZOS).save(A/'preview.png');resources['preview.png']=encode(Image.open(A/'preview.png'))
device=io.BytesIO()
with zipfile.ZipFile(device,'w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('app.json',mb);z.writestr('app.js',(P/'app.js').read_bytes());z.writestr('watchface/index.js',(P/'watchface.js').read_bytes())
 for n,b in resources.items():z.writestr('assets/'+n,b)
side=io.BytesIO()
with zipfile.ZipFile(side,'w',zipfile.ZIP_DEFLATED) as z:z.writestr('app.json',mb)
with zipfile.ZipFile(D/(B+'-Balance2.zpk'),'w',zipfile.ZIP_DEFLATED) as z:z.writestr('device.zip',device.getvalue());z.writestr('app-side.zip',side.getvalue())
url='zpkd1://raw.githubusercontent.com/lepilinvitold-boop/Amazfit-watchfaces/main/dist/'+B+'-Balance2.zpk';q=QrCodeWidget(url,barLevel='M');q.qr.make();m=q.qr.modules;n=len(m);qr=Image.new('RGB',((n+8)*10,)*2,'white');dr=ImageDraw.Draw(qr)
for y,row in enumerate(m):
 for x,v in enumerate(row):
  if v:dr.rectangle(((x+4)*10,(y+4)*10,(x+5)*10-1,(y+5)*10-1),fill='black')
qr.save(D/(B+'-zepp-qr.png'));(D/(B+'-install-url.txt')).write_text(url+'\n')
print('Built',B,'with app bootstrap and',len(resources),'native assets')
