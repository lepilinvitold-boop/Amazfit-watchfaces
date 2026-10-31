from pathlib import Path
import io,json,zipfile,math,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from reportlab.graphics.barcode.qr import QrCodeWidget
P=Path(__file__).resolve().parent;ROOT=P.parents[1];D=ROOT/'dist';B='Blue-Scale-Grey-v1.0.0';S=4
codec=P.parent/'Owl-Graphite-Color-1.0.9/build.py';ns={'__file__':str(codec)};exec(codec.read_text().split('with zipfile.ZipFile')[0],ns);encode=ns['encode'];decode=ns['decode']
with zipfile.ZipFile(D/'Owl-Graphite-grey-Volume-v1.0.1-RU-Balance2.zpk') as z:
 with zipfile.ZipFile(io.BytesIO(z.read('device.zip'))) as q:old={n:q.read(n) for n in q.namelist()}
assets={}
def put(n,im):assets[n]=im.convert('RGBA')
def oldasset(n):return decode(old['assets/'+n+'.png'])
font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def glyph(t,size,color=(235,237,239,255),width=None):
 f=ImageFont.truetype(font,size*S);b=f.getbbox(t);im=Image.new('RGBA',(max(1,b[2]-b[0]),b[3]-b[1]));ImageDraw.Draw(im).text((-b[0],-b[1]),t,font=f,fill=color)
 return im.resize((width or math.ceil(im.width/S),math.ceil(im.height/S)),Image.Resampling.LANCZOS)
for name,size,width in [('value',30,22),('time',38,27),('date',24,18),('small',17,11),('step',27,18)]:
 for i in range(10):put(name+'_'+str(i),glyph(str(i),size,width=width))
put('dot',glyph('.',24,width=7));put('minus',glyph('−',24,width=14));put('degree',glyph('°',21,width=13));put('colon',glyph(':',38,width=10));put('date_dot',glyph('.',24,width=7))
# Align punctuation to the numeric baseline, not the top of its ink box.
for n,height in [('dot',18),('date_dot',18),('colon',29)]:
 g=assets[n];cv=Image.new('RGBA',(g.width,height));cv.alpha_composite(g,(0,height-g.height));put(n,cv)
put('km',glyph(' КМ',12));put('kcal',glyph(' ККАЛ',12))
for i,t in enumerate(['ПН','ВТ','СР','ЧТ','ПТ','СБ','ВС']):
 g=glyph(t,20);im=Image.new('RGBA',(60,24));im.alpha_composite(g,((60-g.width)//2,0));put('week_'+str(i),im)
for i in range(29):put('weather_'+str(i),oldasset('weather_'+str(i)).resize((32,32),Image.Resampling.LANCZOS))
for n in ['hour','minute','second','cap']:put(n,oldasset(n))
# Copy the accepted Grey bezel pixels without generating a replacement.
bg=oldasset('background');a=np.array(bg);yy,xx=np.mgrid[:480,:480];rad=np.hypot(xx-239.5,yy-239.5);a[rad<201]=[0,0,0,255];bg=Image.fromarray(a)
layer=Image.new('RGBA',(480*S,480*S));dr=ImageDraw.Draw(layer)
def text(t,x,y,size,color=(190,193,197,255)):
 g=glyph(t,size,color);layer.alpha_composite(g.resize((g.width*S,g.height*S),Image.Resampling.LANCZOS),(round((x-g.width/2)*S),round(y*S)))
def line(points,fill,width):dr.line([(int(x*S),int(y*S)) for x,y in points],fill=fill,width=round(width*S))
# Four independent, convex steel rims; lighting is consistent at every circle.
for cx,cy in [(179,172),(301,172),(179,290),(301,290)]:
 y,x=np.mgrid[:120*S,:120*S];dx=x/S-60;dy=y/S-60;r=np.hypot(dx,dy);direction=(-dx-dy)/np.maximum(r,1)/1.414
 v=np.where(r>55,22,np.where(r>53,75+50*direction,np.where(r>50,170+55*direction,np.where(r>48,55+35*direction,4))))
 ar=np.zeros((120*S,120*S,4),np.uint8);ar[:,:,:3]=np.clip(v[:,:,None],0,255);ar[:,:,3]=np.where(r<=58,255,0);layer.alpha_composite(Image.fromarray(ar),(int((cx-60)*S),int((cy-60)*S)))
# Discrete inner chapter marks echo the segmented Blue Scale perimeter.
for ang in list(range(10,51,6))+list(range(130,171,6))+list(range(190,231,6))+list(range(310,351,6)):
 t=math.radians(ang);line([(240+174*math.sin(t),240-174*math.cos(t)),(240+182*math.sin(t),240-182*math.cos(t))],(132,137,143),2.5)
text('12',240,46,30);text('9',68,221,35);text('3',412,221,35);text('6',240,411,29)
text('ПОГОДА',179,177,11);text('ПУЛЬС',301,177,11);text('ШАГИ',179,284,11)
# Battery silhouette, percent sign, heart, walking icon and understated dividers.
dr.rounded_rectangle((222*S,84*S,254*S,97*S),radius=2*S,outline=(206,210,214),width=S);dr.rectangle((255*S,88*S,257*S,93*S),fill=(206,210,214));dr.rectangle((225*S,87*S,245*S,94*S),fill=(151,155,160))
text('%',260,102,14)
heart=glyph('♥',30);layer.alpha_composite(heart.resize((heart.width*S,heart.height*S)),(round((301-heart.width/2)*S),139*S))
dr.ellipse((175*S,249*S,182*S,256*S),fill=(222,225,229));line([(178,259),(174,269),(183,277)],(222,225,229),3);line([(177,264),(187,266)],(222,225,229),3);line([(175,269),(168,280)],(222,225,229),3)
text('КМ',166,393,11);text('ККАЛ',336,393,11)
bg.alpha_composite(layer.resize((480,480),Image.Resampling.LANCZOS));put('background',bg)
TAPS=[['battery',219,83,43,38,'Settings_batteryManagerScreen'],['weather',128,122,102,102,'WeatherScreen'],['heart',250,122,102,102,'heart_app_Screen'],['steps',128,239,102,102,'activityAppScreen'],['date',250,239,102,102,'ScheduleCalScreen'],['hours',181,347,54,39,'StopWatchScreen'],['minutes',245,347,54,39,'CountdownAppScreen'],['distance',111,388,104,23,'activityAppScreen'],['calories',265,388,104,23,'activityAppScreen']]
for name,x,y,w,h,url in TAPS:put('hit_'+name,Image.new('RGBA',(w,h)))
files={}
for n,im in list(assets.items()):
 files['assets/'+n+'.png']=encode(im)
 if not n.startswith('hit_'):
  a=np.array(im);a[:,:,:3]=(a[:,:,:3]*.38).astype('uint8');files['assets/aod_'+n+'.png']=encode(Image.fromarray(a))
def render(aod=False):
 im=assets['background'].copy()
 def paste(n,x,y):im.alpha_composite(assets[n],(x,y))
 def digits(t,f,x,y):
  for c in t:
   n=f+'_'+c if c.isdigit() else 'dot';paste(n,x,y);x+=assets[n].width
 digits('71','small',226,102);paste('weather_3',163,139);digits('22','value',153,195);paste('degree',197,195);digits('72','value',279,195);digits('6972','step',143,302);paste('week_5',271,260);digits('31','date',262,300);paste('date_dot',298,300);digits('10','date',305,300)
 digits('10','time',181,347);paste('colon',235,347);digits('08','time',245,347);digits('3.94','small',111,389);digits('228','small',279,389)
 for n,px,py,angle in [('hour',21,156,304),('minute',19,192,48)]+([] if aod else [('second',6,222,216)]):
  cv=Image.new('RGBA',(960,960));cv.alpha_composite(assets[n],(480-px,480-py));cv=cv.rotate(-angle,resample=Image.Resampling.BICUBIC,center=(480,480));im.alpha_composite(cv.crop((240,240,720,720)))
 paste('cap',227,227)
 if aod:
  a=np.array(im);a[:,:,:3]=(a[:,:,:3]*.38).astype('uint8');im=Image.fromarray(a)
 return im
preview=render();preview.save(D/(B+'-preview.png'));render(True).save(D/(B+'-AOD-preview.png'));files['assets/preview.png']=encode(preview.resize((240,240),Image.Resampling.LANCZOS))
m=json.loads(old['app.json']);m['app']['appId']=10622131;m['app']['appName']='Blue Scale Grey';m['app']['version']={'code':1,'name':'1.0.0'};m['i18n']['en-US']['appName']='Blue Scale Grey';m['packageInfo']['timeStamp']=1793491200;mb=json.dumps(m,ensure_ascii=False).encode();(P/'app.json').write_bytes(mb);files['app.json']=mb
files['app.js']=(P/'app.js').read_bytes();files['watchface/index.js']=(P/'watchface.js').read_bytes()
def archive(items):
 b=io.BytesIO()
 with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED) as z:
  for n,v in items.items():z.writestr(n,v)
 return b.getvalue()
(D/(B+'-RU-Balance2.zpk')).write_bytes(archive({'device.zip':archive(files),'app-side.zip':archive({'app.json':mb})}))
target=ROOT/'verify-blue-scale-grey';target.mkdir(exist_ok=True)
for n,v in files.items():p=target/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(v)
url='zpkd1://raw.githubusercontent.com/lepilinvitold-boop/Amazfit-watchfaces/blue-scale-grey-1.0.0/dist/'+B+'-RU-Balance2.zpk';(D/(B+'-install-url.txt')).write_text(url)
q=QrCodeWidget(url,barLevel='M');q.qr.make();matrix=q.qr.modules;n=len(matrix);qr=Image.new('RGB',((n+8)*8,)*2,'white');draw=ImageDraw.Draw(qr)
for y,row in enumerate(matrix):
 for x,v in enumerate(row):
  if v:draw.rectangle(((x+4)*8,(y+4)*8,(x+5)*8-1,(y+5)*8-1),fill='black')
qr.save(D/(B+'-zepp-qr.png'))
print('Built',B,'appId',m['app']['appId'],'assets',len(files))
