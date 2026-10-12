"""Reproducible 480px native Zepp dial, rebuilt from the supplied reference."""
from pathlib import Path
import io,json,math,struct,zipfile,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from reportlab.graphics.barcode.qr import QrCodeWidget
P=Path(__file__).resolve().parent;A=P/'assets';D=P.parents[1]/'dist';V='1.0.1';B='Amazfit-Green-RU-v'+V
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
  dr.text((4*S-box[0],4*S-box[1]),t,font=f,fill=c)
  if angle:layer=layer.rotate(-angle,resample=Image.Resampling.BICUBIC,expand=True)
  self.im.alpha_composite(layer,(round(x*S-layer.width/2),round(y*S-layer.height/2)))
def polar(r,a,cx=240,cy=240):a=math.radians(a);return cx+r*math.sin(a),cy-r*math.cos(a)
# The photograph's physical black/silver case bezel is deliberately outside this screen.
bg=image(480,480);d=Draw(bg)
y,x=np.mgrid[:480*S,:480*S];r=np.hypot(x/S-240,y/S-240);light=-(x/S+y/S-480)/(max(1,480)*1.41)
a=np.zeros((480*S,480*S,4),np.uint8);a[:,:,3]=255
metal=np.clip(58+12*light,0,255).astype('uint8');face=np.clip(39+5*light,0,255).astype('uint8')
for c in range(3):a[:,:,c]=np.where(r<208,face,np.where(r<237,metal,13))
bg=Image.fromarray(a);d=Draw(bg)
for radius,c,w in [(237,'#181818',1),(235,'#686868',.7),(210,'#171717',2),(205,'#707070',.7),(196,'#141414',1),(188,'#454545',1)]:d.ellipse((240-radius,240-radius,240+radius,240+radius),None,c,w)
# Ring labels follow exactly the tangential orientation of the reference (including bottom).
for i in range(12):
 angle=i*30;tx,ty=polar(222,angle);d.text('60' if i==0 else f'{5*i:02}',tx,ty,26,angle=angle,kind=REG)
# Three thick green comb-shaped arcs at 12-3, with four inward teeth each.
for start,end in [(6,25),(36,55),(66,85)]:
 for i in np.linspace(start,end,100):d.line([polar(230,i),polar(224,i)],GREEN,1.1)
 for i in [start,start+6,start+12,end]:d.line([polar(230,i),polar(217,i)],GREEN,2.5)
# Chrome screw heads between the labels on the remaining ring.
for angle in [105,135,165,195,225,255,285,315,345]:
 sx,sy=polar(222,angle);d.ellipse((sx-7,sy-7,sx+7,sy+7),'#303030','#535353',.7)
 d.ellipse((sx-5.3,sy-5.3,sx+5.3,sy+5.3),'#737373','#454545',.5)
 d.arc((sx-4.2,sy-4.2,sx+4.2,sy+4.2),200,310,'#acacac',1.2)
 d.line([(sx-2.8,sy-2.2),(sx+2.8,sy+2.2)],'#3f3f3f',1.8)
# Small light dots adjacent to outer green legends, as in the photo.
for angle in [128,145,215,232,305,323]:
 sx,sy=polar(222,angle);d.ellipse((sx-3.3,sy-3.3,sx+3.3,sy+3.3),'#adadad','#737373',.5)
for label,angle in [('МУЗЫКА',314),('ШАГИ',224),('СЕКУНДОМЕР',136)]:
 sx,sy=polar(222,angle);d.text(label,sx,sy,16 if label!='СЕКУНДОМЕР' else 12,GREEN,angle=angle if angle<180 else angle-360)
# 240 subdivisions with longer fifth and quarter marks.
for i in range(240):
 ang=i*1.5;outer=201;inner=194 if i%4 else 190
 if i%20==0:inner=188
 d.line([polar(inner,ang),polar(outer,ang)],'#727272' if i%4 else '#969696',.7 if i%4 else 1.1)
# Thin sector separators and tiny sector legends inside the chapter ring.
for a in [0,30,60,90,270,300,330]:d.line([polar(169,a),polar(186,a)],'#666666',.8)
for t,a in [('ЦИФЕРБЛАТ',-15),('Amazfit',15),('АНАЛОГ',45),('ЭКРАН',75),('ЭКРАН',-75),('ХРОНОГРАФ',-45)]:
 if t=='Amazfit':continue
 tx,ty=polar(178,a);d.text(t,tx,ty,8.5,(154,155,155,255),angle=a,kind=BOLD)
# Raised white hour blocks, with no marks hidden under the lower panel.
for ang in [0,30,60,270,300,330]:
 p=[polar(171,ang-2.1),polar(185,ang-2.1),polar(185,ang+2.1),polar(171,ang+2.1)];d.poly(p,'#bababa');d.line([p[0],p[1],p[2]],'#f1f1f1',1.4)
# Flat, upright baseline with original oblique tall hour glyphs; not rotated around dial.
for number,xx,yy,size in [('12',240,100,60),('1',310,120,61),('2',370,178,61),('9',86,242,61),('10',117,179,61),('11',169,121,61)]:d.text(number,xx,yy,size,shadow=True)
# Lightning status icon above 12.
d.poly([(239,34),(232,47),(237,47),(233,58),(247,43),(242,43),(247,34)],WHITE)
# Original subtle crosshairs and four green squares retained; MEN text removed.
for p in [[(178,166),(203,166)],[(204,157),(204,180)],[(282,166),(302,166)]]:d.line(p,'#626262',.7)
for sx,sy in [(225,156),(237,156),(225,168),(237,168)]:d.poly([(sx,sy),(sx+8,sy),(sx+8,sy+8),(sx,sy+8)],GREEN)
# Amazfit sits directly under 12, as requested, without moving the numeral.
d.text('Amazfit',240,134,17,kind=BOLD)
# Recessed lower digital panel: traced coordinates, continuous rounded shoulder.
def cubic(p0,p1,p2,p3):
 return [tuple((1-t)**3*p0[j]+3*(1-t)**2*t*p1[j]+3*(1-t)*t*t*p2[j]+t**3*p3[j] for j in [0,1]) for t in np.linspace(0,1,40)]
panel_unused=[(70,308),(101,327),(188,313),(213,304),(226,290),(237,275),(251,259),(268,239),(287,218),(301,211),(328,210),(338,204),(341,204),(341,212),(364,212),(368,204),(372,204),(372,212),(411,212),(422,229),(427,247),(424,273),(414,301),(398,328),(379,352),(356,373),(326,390),(289,399),(204,400),(158,391),(121,369),(93,339)]
panel=[(62,299)]+cubic((62,299),(111,337),(178,325),(212,286))+[(275,225)]+cubic((275,225),(289,210),(291,207),(316,207))+[(338,207),(338,199),(342,199),(342,208),(369,208),(369,199),(373,199),(373,208),(411,208)]+cubic((411,208),(438,233),(432,263),(416,296))+cubic((416,296),(389,349),(334,397),(286,400))+[(158,400)]+cubic((158,400),(112,384),(78,340),(62,299))
d.poly(panel,'#444444');panel2=[(x+(240-x)*.014,y+(280-y)*.014) for x,y in panel];d.poly(panel2,'#0a0a0a');panel3=[(x+(240-x)*.025,y+(280-y)*.025) for x,y in panel];d.poly(panel3,'black')
d.line([(280,285),(407,285)],'#c4c4c4',1.1)
# Eye-like indicator and outlined battery match the two original status symbols.
d.arc((315,232,335,244),180,360,WHITE,1.4);d.arc((315,232,335,244),0,180,WHITE,1.4);d.ellipse((322,232,328,244),WHITE)
d.line([(376,231),(394,231),(394,244),(376,244),(376,231)],WHITE,1.6);d.line([(395,235),(396,235),(396,240)],WHITE,1)
# Cloud weather icon on the left.
d.line([(146,230),(143,230),(141,226),(142,222),(146,220),(149,217),(154,217),(158,220),(162,220),(166,223),(166,228),(163,231),(149,231),(146,230)],WHITE,1.5)
# Lower lock symbol and straight base line.
d.line([(156,405),(326,405)],'#666666',1.4)
d.arc((231,412,242,426),180,340,WHITE,2);d.poly([(237,424),(254,424),(254,437),(237,437)],WHITE);d.ellipse((243,428,248,433),'#111111')
store('background',bg)
# Glyph resources, fixed cell widths preserve numeric alignment.
def glyph(prefix,t,height,width,size,kind=F):
 im=image(width,height);dr=ImageDraw.Draw(im);f=font(size,kind);box=f.getbbox(t);dr.text((width*S/2,(height-2)*S),t,font=f,fill=WHITE,anchor='ms');return store(prefix,im)
for n in range(10):
 glyph('status_'+str(n),str(n),26,13,34)
 glyph('date_'+str(n),str(n),19,10,24)
 glyph('weather_'+str(n),str(n),24,13,30)
for prefix,h,w,size in [('status',26,14,30),('date',19,8,24),('weather',24,10,30)]:
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
 im=image(109,19);d=Draw(im);d.text(t,54.5,9,17 if len(t)>9 else 20);store('week_'+str(i),im)
for n,t in [('am','ДП'),('pm','ПП')]:
 im=image(38,25);dr=Draw(im);dr.text(t,19,12,31);store(n,im)
# Reference blade shapes; long rectangular black slots, original counterweights.
for name,length,width,tail in [('hour',111,17,31),('minute',179,15,24)]:
 im=image(40,length+tail+7);dr=Draw(im);cx=20;py=length
 dr.poly([(cx-5,2),(cx+5,0),(cx+width/2,10),(cx+width/2,py-18),(cx+7,py-8),(cx+12,py+tail-5),(cx+1,py+tail),(cx-9,py+tail-5),(cx-7,py-8),(cx-width/2,py-18),(cx-width/2,10)],'#d6d7d8')
 dr.line([(cx-5,3),(cx-width/2,11),(cx-width/2,py-18)],'#f4f4f4',1)
 dr.poly([(cx-2,30),(cx+2,30),(cx+2,py-18),(cx-2,py-18)],'#141414');dr.ellipse((cx-4,py-4,cx+4,py+4),'#242424')
 store(name,im)
# Thin solid green seconds, ending exactly at the minute ring.
im=image(12,239);dr=Draw(im);dr.poly([(5,0),(7,0),(7,201),(5,201)],GREEN);dr.poly([(5,201),(7,201),(7,231),(5,231)],'#454545');store('second',im)
im=image(12,12);dr=Draw(im);dr.ellipse((0,0,12,12),'#333333','#171717',1.6);dr.ellipse((4,4,8,8),'#a0a0a0');store('cap',im)
for n,w,h in [('music',70,55),('steps',70,55),('timer',80,55)]:
 im=Image.new('RGBA',(w,h));im.save(A/('tap_'+n+'.png'));SOURCE['tap_'+n+'.png']=im
for n,im in list(SOURCE.items()):
 if n.startswith('tap_'):continue
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
manifest={'configVersion':'v2','app':{'appId':10623001,'appName':'Amazfit Green RU','appType':'watchface','version':{'code':2,'name':V},'icon':'preview.png','cover':['preview.png'],'vender':'Vitold personal','description':'Русский циферблат по исходному образцу'},'runtime':{'apiVersion':{'minVersion':'1.0','target':'1.0.1','compatible':'1.0.0'}},'permissions':[],'i18n':{'en-US':{'appName':'Amazfit Green RU'}},'defaultLanguage':'en-US','designWidth':480,'module':{'watchface':{'path':'watchface/index','main':1,'editable':0,'lockscreen':1}},'platforms':[{'name':'Balance 2','deviceSource':v} for v in [9568512,9568513,9568515]],'watchfacePreview':{'icon':'preview.png','size':[]},'packageInfo':{'mode':'production','zpm':'3.4.2'}}
(P/'app.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));mb=json.dumps(manifest,ensure_ascii=False).encode()
resources={n:encode(im) for n,im in SOURCE.items()}
# Preview comes from decoded NATIVE resources, not a separate illustrative mockup.
canvas=decode(resources['background.png'])
def paste(n,x,y):canvas.alpha_composite(decode(resources[n+'.png']),(x,y))
def text(t,prefix,x,y):
 for c in t:
  n={'%':'percent','-':'minus','.':'dot','/':'slash'}.get(c,c);a=decode(resources[prefix+'_'+n+'.png']);canvas.alpha_composite(a,(x,y));x+=a.width
text('83%','status',311,252);text('97%','status',366,252);text('18','weather',137,242);paste('degree',163,242);paste('pm',122,336)
paste('week_2',143,305);text('14/10/26','date',253,305)
text('12','digital',171,336);paste('colon',235,336);text('42','digital',251,336);text('40','second',319,336)
for name,pivot,angle in [('hour',111,22),('minute',179,252),('second',201,240)]:
 layer=Image.new('RGBA',(480,480));asset=decode(resources[name+'.png']);layer.alpha_composite(asset,(240-(6 if name=='second' else 20),240-pivot));canvas.alpha_composite(layer.rotate(-angle,resample=Image.Resampling.BICUBIC,center=(240,240)))
paste('cap',234,234);canvas.convert('RGB').save(D/(B+'-preview.png'));canvas.resize((240,240),Image.Resampling.LANCZOS).save(A/'preview.png');resources['preview.png']=encode(Image.open(A/'preview.png'))
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
