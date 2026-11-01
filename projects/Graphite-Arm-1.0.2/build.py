from pathlib import Path
import io,json,zipfile,math,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from reportlab.graphics.barcode.qr import QrCodeWidget
P=Path(__file__).resolve().parent;ROOT=P.parents[1];D=ROOT/'dist';B='Graphite-Arm-v1.0.2';S=4
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
for name,size,width in [('value',30,18),('time',38,27),('date',22,14),('small',17,11),('step',30,18),('metric',13,7),('battery',30,18),('forecast',14,8)]:
 for i in range(10):put(name+'_'+str(i),glyph(str(i),size,width=width))
put('dot',glyph('.',24,width=7));put('minus',glyph('−',24,width=14));put('degree',glyph('°',21,width=13));put('colon',glyph(':',38,width=10));put('date_dot',glyph('.',22,width=6))
# Align punctuation to the numeric baseline, not the top of its ink box.
for n,height in [('dot',18),('date_dot',17),('colon',29)]:
 g=assets[n];cv=Image.new('RGBA',(g.width,height));cv.alpha_composite(g,(0,height-g.height));put(n,cv)
md=Image.new('RGBA',(4,10));md.alpha_composite(glyph('.',13,width=4),(0,8));put('metric_dot',md)
put('km',glyph(' КМ',12));put('kcal',glyph(' ККАЛ',12))
for i,t in enumerate(['ПН','ВТ','СР','ЧТ','ПТ','СБ','ВСК']):
 g=glyph(t,20);im=Image.new('RGBA',(54,24));im.alpha_composite(g,((54-g.width)//2,0));put('week_'+str(i),im)
for i in range(29):put('weather_'+str(i),oldasset('weather_'+str(i)).resize((32,32),Image.Resampling.LANCZOS))
# Preserve accepted 1.0.10 hands exactly except the small leading tip.
with zipfile.ZipFile(D/'Blue-Scale-Grey-v1.0.10-RU-Balance2.zpk') as z:
 with zipfile.ZipFile(io.BytesIO(z.read('device.zip'))) as q:
  for name,tip,join,half in [('hour',73,95,9),('minute',37,59,7)]:
   original=decode(q.read('assets/'+name+'.png'));put('accepted_'+name,original)
   # Replace only rows above join. Everything from join onward is unchanged.
   top=Image.new('RGBA',(76*S,join*S));dr=ImageDraw.Draw(top)
   dr.polygon([(36*S,tip*S),((36-half)*S,join*S),((36+half)*S,join*S)],fill=(31,33,36,255))
   dr.polygon([(36*S,(tip+3)*S),((36-half+1.3)*S,join*S),((36+half-1.3)*S,join*S)],fill=(235,238,240,255))
   changed=original.copy();changed.paste(top.resize((76,join),Image.Resampling.LANCZOS),(0,0));put(name,changed)
put('second',oldasset('second'));put('cap',oldasset('cap'))
# Rebuild only the interior; retain the accepted external Grey bezel.
bg=oldasset('background');a=np.array(bg);yy,xx=np.mgrid[:480,:480];rad=np.hypot(xx-239.5,yy-239.5);a[rad<201]=[0,0,0,255];bg=Image.fromarray(a)
# Recessed common metal carrier. Its concave shoulders sit below the four rims.
mask=Image.new('L',(480*S,480*S));outline=[]
def curve(a,b,c,d):
 for t in np.linspace(0,1,101):
  u=1-t;outline.append(((u**3*a[0]+3*u*u*t*b[0]+3*u*t*t*c[0]+t**3*d[0])*S,(u**3*a[1]+3*u*u*t*b[1]+3*u*t*t*c[1]+t**3*d[1])*S))
curve((305,124),(305,162),(318,175),(356,175))
outline.append((356*S,305*S))
curve((356,305),(318,305),(305,318),(305,356))
outline.append((175*S,356*S))
curve((175,356),(175,318),(162,305),(124,305))
outline.append((124*S,175*S))
curve((124,175),(162,175),(175,162),(175,124))
ImageDraw.Draw(mask).polygon(outline,fill=255)
y,x=np.mgrid[:480*S,:480*S];texture=30+5*np.cos((x+y)/140)+1.3*np.sin(x*1.7+y*.4)+1*np.sin(x*.7-y*2.1)
carrier=np.zeros((480*S,480*S,4),np.uint8);carrier[:,:,:3]=np.clip(texture[:,:,None],0,255);carrier[:,:,3]=np.array(mask)
# Subtle bevel on the carrier edge; rings above occlude the joins.
body=Image.fromarray(carrier);edge=ImageDraw.Draw(body);edge.line(outline+[outline[0]],fill=(75,78,81,255),width=2*S,joint='curve')
bg.alpha_composite(body.resize((480,480),Image.Resampling.LANCZOS))
# Broad brushed-steel annuli with polished bevels and a recessed black well.
for cx,cy in [(240,124),(124,240),(356,240),(240,356)]:
 y,x=np.mgrid[:132*S,:132*S];dx=x/S-66;dy=y/S-66;r=np.hypot(dx,dy);ang=np.arctan2(dy,dx)
 # Alternating reflections across a broad curved metal face, rather than a grey stroke.
 shine=(.5+.5*np.cos(2*(ang+.67)))**5
 fine=2*np.sin(r*39+ang*.4)+1.4*np.sin(r*73)
 face=58+169*shine+18*np.cos((r-56)/7*math.pi)+fine
 v=np.where(r>64,12,np.where(r>63,125,np.where(r>61,185-45*(r-61)+55*shine,np.where(r>53,face,np.where(r>51,160-55*(53-r)+40*shine,np.where(r>50,25,0))))))
 ar=np.zeros((132*S,132*S,4),np.uint8);ar[:,:,:3]=np.clip(v[:,:,None],0,255);ar[:,:,3]=np.where(r<=65,255,0)
 bg.alpha_composite(Image.fromarray(ar).resize((132,132),Image.Resampling.LANCZOS),(cx-66,cy-66))
put('background',bg)
# Clear metric pictograms for the two lateral circles.
heart=Image.new('RGBA',(40*S,36*S));hd=ImageDraw.Draw(heart)
hd.ellipse((0,0,22*S,22*S),fill='white');hd.ellipse((18*S,0,40*S,22*S),fill='white');hd.polygon([(0,12*S),(40*S,12*S),(20*S,36*S)],fill='white');hd.line([(2*S,17*S),(12*S,17*S),(17*S,10*S),(22*S,24*S),(27*S,17*S),(38*S,17*S)],fill=(10,10,10),width=2*S);put('heart_icon',heart.resize((29,26),Image.Resampling.LANCZOS))
walk=Image.new('RGBA',(34*S,39*S));wd=ImageDraw.Draw(walk);wd.ellipse((15*S,0,23*S,8*S),fill='white')
for pts,w in [([(18,11),(14,23),(22,29)],4), ([(17,13),(9,20),(5,18)],3), ([(18,14),(23,20),(30,20)],3), ([(14,23),(8,37)],4), ([(21,28),(28,36)],4)]:wd.line([(x*S,y*S) for x,y in pts],fill='white',width=w*S)
put('walk_icon',walk.resize((25,29),Image.Resampling.LANCZOS))
# Native gauge resources: battery/calories continuous arcs and round markers;
# pulse/steps segmented, matching the original distinction and angular sectors.
GAUGES=[('battery',290,340,False),('heart',20,70,True),('steps',200,250,True),('calories',110,160,False)]
for name,start,end,segmented in GAUGES:
 for level in range(21):
  im=Image.new('RGBA',(480*S,480*S));dr=ImageDraw.Draw(im)
  def point(r,ang):t=math.radians(ang);return ((240+r*math.sin(t))*S,(240-r*math.cos(t))*S)
  if segmented:
   for i in range(11):
    angle=start+(end-start)*i/10;active=i<round(level/20*11)
    # Radial blocks: bevel edges plus a brushed silver centre.
    for r0,r1,col,w in [(178,192,(15,17,20,255),7),(179,191,(221,225,229,255) if active else (65,69,74,255),5.5),(180,190,(158,164,171,255) if active else (39,42,47,255),4.2)]:dr.line([point(r0,angle),point(r1,angle)],fill=col,width=round(w*S))
  else:
   box=tuple(v*S for v in (55,55,425,425));dr.arc(box,start-90,end-90,fill=(54,58,64,255),width=8*S)
   finish=end-(end-start)*level/20 if name in ['battery','calories'] else start+(end-start)*level/20
   if level:dr.arc(box,(finish if name in ['battery','calories'] else start)-90,(end if name in ['battery','calories'] else finish)-90,fill=(193,199,206,255),width=8*S)
   px,py=point(181,finish);dr.ellipse((px-4*S,py-4*S,px+4*S,py+4*S),fill=(242,244,246,255))
  box={'battery':(40,40,240,240),'heart':(240,40,440,240),'steps':(40,240,240,440),'calories':(240,240,440,440)}[name]
  put(name+'_scale_'+str(level),im.resize((480,480),Image.Resampling.LANCZOS).crop(box))
# Curved perimeter data uses the original native IMG rotation mechanism.
for i in range(10):put('arc_'+str(i),glyph(str(i),13,width=8))
put('arc_percent',glyph('%',12,width=10));put('battery_percent',glyph('%',25,width=18));put('arc_dash',glyph('−',11,width=8))
# Four native indicators placed beside the appropriate curved values.
original_bg=decode((P/'original-background.bin').read_bytes())
for name,box in [('battery',(112,68,144,100)),('heart',(305,58,342,87)),('steps',(137,389,170,425)),('calories',(305,389,342,427))]:
 ar=np.array(original_bg.crop(box));mx=ar[:,:,:3].max(axis=2).astype(float);mn=ar[:,:,:3].min(axis=2).astype(float);alpha=np.clip((mx-mn-12)*2,0,255).astype('uint8');ar[:,:,:3]=220;ar[:,:,3]=alpha;put('arc_icon_'+name,Image.fromarray(ar).resize((11,12),Image.Resampling.LANCZOS))
for level in range(11):
 im=Image.new('RGBA',(40*S,18*S));di=ImageDraw.Draw(im);di.rounded_rectangle((S,S,36*S,17*S),radius=3*S,outline=(221,225,230,255),width=2*S);di.rectangle((37*S,6*S,39*S,12*S),fill=(221,225,230,255))
 if level:di.rectangle((4*S,4*S,round((4+29*level/10)*S),14*S),fill=(195,201,208,255))
 put('battery_icon_'+str(level),im.resize((40,18),Image.Resampling.LANCZOS))
put('low',glyph('↓',14,width=8));put('high',glyph('↑',14,width=8));put('forecast_degree',glyph('°',12,width=8));put('forecast_minus',glyph('−',14,width=8))
for c in '0123456789. ПНВТСРЧБК':
 g=Image.new('RGBA',(12,14)) if c==' ' else glyph(c,18,width=4 if c=='.' else 12);cv=Image.new('RGBA',(20,24));cv.alpha_composite(g,((20-g.width)//2,17 if c=='.' else (24-g.height)//2));put('date_arc_'+str(ord(c)),cv)
TAPS=[['battery',190,74,100,100,'Settings_batteryManagerScreen'],['weather',190,306,100,105,'WeatherScreen'],['heart',306,190,100,100,'heart_app_Screen'],['steps',74,190,100,100,'activityAppScreen'],['date',174,422,132,18,'ScheduleCalScreen'],['hours',181,193,54,30,'StopWatchScreen'],['minutes',245,193,54,30,'CountdownAppScreen']]
for name,x,y,w,h,url in TAPS:put('hit_'+name,Image.new('RGBA',(w,h)))
files={}
for n,im in list(assets.items()):
 files['assets/'+n+'.png']=encode(im)
 if not n.startswith('hit_'):
  a=np.array(im);a[:,:,:3]=(a[:,:,:3]*.38).astype('uint8');files['assets/aod_'+n+'.png']=encode(Image.fromarray(a))
# Patch only the indexed tip rows in the original device resources.
# Preserve the original palette and every pixel below the edited tip.
with zipfile.ZipFile(D/'Blue-Scale-Grey-v1.0.10-RU-Balance2.zpk') as z:
 with zipfile.ZipFile(io.BytesIO(z.read('device.zip'))) as q:
  for name,join in [('hour',95),('minute',59)]:
   raw=bytearray(q.read('assets/'+name+'.png'));pal=np.frombuffer(raw[64:1088],np.uint8).reshape(256,4).astype('int32')
   target=np.array(assets[name])[:join].astype('int32');target[:,:,:3]=np.rint(target[:,:,:3]*target[:,:,3:4]/255)
   indices=((target[:,:,None,:]-pal[None,None,:,:])**2).sum(axis=3).argmin(axis=2).astype('uint8')
   import struct
   padded=struct.unpack_from('<H',raw,12)[0]
   for y in range(join):raw[1088+y*padded:1088+y*padded+76]=indices[y].tobytes()
   files['assets/'+name+'.png']=bytes(raw)
def render(aod=False):
 im=assets['background'].copy()
 def paste(n,x,y):im.alpha_composite(assets[n],(x,y))
 def digits(t,f,x,y):
  for c in t:
   n=f+'_'+c if c.isdigit() else ('metric_dot' if f=='metric' else 'dot');paste(n,x,y);x+=assets[n].width
 for name,level in [('battery',14),('heart',5),('steps',14),('calories',9)]:paste(name+'_scale_'+str(level),40 if name in ['battery','steps'] else 240,40 if name in ['battery','heart'] else 240)
 def curved(t,center,bottom=False):
  for i,c in enumerate(t):
   g=assets['arc_'+c if c.isdigit() else 'arc_percent'];ang=center+(i-(len(t)-1)/2)*3.2*(-1 if bottom else 1)
   rad=165;xx=240+rad*math.sin(math.radians(ang));yy=240-rad*math.cos(math.radians(ang));g=g.rotate(-(ang-180 if bottom else ang),Image.Resampling.BICUBIC,expand=True);im.alpha_composite(g,(round(xx-g.width/2),round(yy-g.height/2)))
 curved('71%',315);curved('72',45);curved('10000',225,True);curved('228',135,True)
 for name,angle,bottom in [('battery',302,False),('heart',32,False),('steps',238,True),('calories',148,True)]:
  g=assets['arc_icon_'+name];g=g.rotate(-(angle-180 if bottom else angle),Image.Resampling.BICUBIC,expand=True);xx=240+165*math.sin(math.radians(angle));yy=240-165*math.cos(math.radians(angle));im.alpha_composite(g,(round(xx-g.width/2),round(yy-g.height/2)))
 paste('battery_icon_7',220,90);digits('71','battery',213,127);paste('battery_percent',249,127)
 paste('walk_icon',112,204);digits('10000','step',79,243)
 paste('heart_icon',342,204);digits('72','value',338,243)
 paste('weather_3',224,309);digits('4','value',225,340);paste('degree',243,340)
 paste('low',195,381);paste('high',242,381);digits('2','forecast',215,381);paste('forecast_degree',223,381);digits('7','forecast',262,381);paste('forecast_degree',270,381)
 for i,c in enumerate('01.11 ВСК'):
  a=(4-i)*3.8;t=math.radians(180+a);g=assets['date_arc_'+str(ord(c))].rotate(-a,Image.Resampling.BICUBIC,expand=True);x=240+191*math.sin(t);y=240-191*math.cos(t);im.alpha_composite(g,(round(x-g.width/2),round(y-g.height/2)))
 digits('10','time',181,193);paste('colon',235,193);digits('08','time',245,193)
 for n,px,py,angle in [('hour',36,232,304),('minute',36,232,48)]+([] if aod else [('second',6,222,216)]):
  cv=Image.new('RGBA',(960,960));cv.alpha_composite(assets[n],(480-px,480-py));cv=cv.rotate(-angle,resample=Image.Resampling.BICUBIC,center=(480,480));im.alpha_composite(cv.crop((240,240,720,720)))
 # The Grey axle covers the join; both tails behind it remain Blue Scale.
 paste('cap',227,227)
 if aod:
  a=np.array(im);a[:,:,:3]=(a[:,:,:3]*.38).astype('uint8');im=Image.fromarray(a)
 return im
preview=render();preview.save(D/(B+'-preview.png'));render(True).save(D/(B+'-AOD-preview.png'));files['assets/preview.png']=encode(preview.resize((240,240),Image.Resampling.LANCZOS))
m=json.loads(old['app.json']);m['app']['appId']=10623141;m['app']['appName']='Графит-арм';m['app']['version']={'code':3,'name':'1.0.2'};m['i18n']['en-US']['appName']='Графит-арм';m['packageInfo']['timeStamp']=1793491200;mb=json.dumps(m,ensure_ascii=False).encode();(P/'app.json').write_bytes(mb);files['app.json']=mb
files['app.js']=(P/'app.js').read_bytes();files['watchface/index.js']=(P/'watchface.js').read_bytes()
def archive(items):
 b=io.BytesIO()
 with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED) as z:
  for n,v in items.items():z.writestr(n,v)
 return b.getvalue()
(D/(B+'-RU-Balance2.zpk')).write_bytes(archive({'device.zip':archive(files),'app-side.zip':archive({'app.json':mb})}))
target=ROOT/'verify-graphite-arm-102';target.mkdir(exist_ok=True)
for n,v in files.items():p=target/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(v)
url='zpkd1://raw.githubusercontent.com/lepilinvitold-boop/Amazfit-watchfaces/graphite-arm-1.0.2/dist/'+B+'-RU-Balance2.zpk';(D/(B+'-install-url.txt')).write_text(url)
q=QrCodeWidget(url,barLevel='M');q.qr.make();matrix=q.qr.modules;n=len(matrix);qr=Image.new('RGB',((n+8)*8,)*2,'white');draw=ImageDraw.Draw(qr)
for y,row in enumerate(matrix):
 for x,v in enumerate(row):
  if v:draw.rectangle(((x+4)*8,(y+4)*8,(x+5)*8-1,(y+5)*8-1),fill='black')
qr.save(D/(B+'-zepp-qr.png'))
print('Built',B,'appId',m['app']['appId'],'assets',len(files))
