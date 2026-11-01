from pathlib import Path
import io,json,zipfile,math,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from reportlab.graphics.barcode.qr import QrCodeWidget
P=Path(__file__).resolve().parent;ROOT=P.parents[1];D=ROOT/'dist';B='Graphite-Arm-v1.0.0';S=4
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
for name,size,width in [('value',28,18),('time',38,27),('date',22,14),('small',17,11),('step',28,18),('metric',13,7),('battery',28,18),('forecast',14,8)]:
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
# Restore original Blue Scale H/M resources byte-for-byte after decoding.
# Grey Volume 1.0.1 fronts, Blue Scale rear sections. Unified pivot (36,232).
for name,px,py in [('hour',21,156),('minute',19,192)]:
 front=oldasset(name).crop((0,0,oldasset(name).width,py+1))
 rear=decode((P/('original-'+name+'.bin')).read_bytes())
 tail=rear.crop((0,233,76,300));ar=np.array(tail);ar[:,:,:3]=np.rint(ar[:,:,:3]*.42).astype('uint8');tail=Image.fromarray(ar)
 # Narrow only the counterweight, keeping its centre aligned with the pivot.
 tail=tail.resize((50,67),Image.Resampling.LANCZOS)
 combined=Image.new('RGBA',(76,300));combined.alpha_composite(front,(36-px,232-py));combined.alpha_composite(tail,(13,233));put(name,combined)
put('second',oldasset('second'));put('cap',oldasset('cap'))
# Rebuild only the interior; retain the accepted external Grey bezel.
bg=oldasset('background');a=np.array(bg);yy,xx=np.mgrid[:480,:480];rad=np.hypot(xx-239.5,yy-239.5);a[rad<201]=[0,0,0,255];bg=Image.fromarray(a)
# Analytic steel rims, exact cardinal alignment and consistent lighting.
for cx,cy in [(240,112),(120,240),(360,240),(240,344)]:
 y,x=np.mgrid[:124*S,:124*S];dx=x/S-62;dy=y/S-62;r=np.hypot(dx,dy);light=(-dx-dy)/np.maximum(r,1)/1.414
 v=np.where(r>60,18,np.where(r>58,80+45*light,np.where(r>53,170+55*light,np.where(r>51,55+30*light,0))))
 ar=np.zeros((124*S,124*S,4),np.uint8);ar[:,:,:3]=np.clip(v[:,:,None],0,255);ar[:,:,3]=np.where(r<=62,255,0)
 bg.alpha_composite(Image.fromarray(ar).resize((124,124),Image.Resampling.LANCZOS),(cx-62,cy-62))
put('background',bg)
# Clear metric pictograms for the two lateral circles.
heart=Image.new('RGBA',(40*S,36*S));hd=ImageDraw.Draw(heart)
hd.ellipse((0,0,22*S,22*S),fill='white');hd.ellipse((18*S,0,40*S,22*S),fill='white');hd.polygon([(0,12*S),(40*S,12*S),(20*S,36*S)],fill='white');hd.line([(2*S,17*S),(12*S,17*S),(17*S,10*S),(22*S,24*S),(27*S,17*S),(38*S,17*S)],fill=(10,10,10),width=2*S);put('heart_icon',heart.resize((40,36),Image.Resampling.LANCZOS))
walk=Image.new('RGBA',(34*S,39*S));wd=ImageDraw.Draw(walk);wd.ellipse((15*S,0,23*S,8*S),fill='white')
for pts,w in [([(18,11),(14,23),(22,29)],4), ([(17,13),(9,20),(5,18)],3), ([(18,14),(23,20),(30,20)],3), ([(14,23),(8,37)],4), ([(21,28),(28,36)],4)]:wd.line([(x*S,y*S) for x,y in pts],fill='white',width=w*S)
put('walk_icon',walk.resize((34,39),Image.Resampling.LANCZOS))
# Symmetric spear tips. Both outer and inner vertices lie on pivot X=36.
for name,length,width in [('hour',144,19),('minute',181,14)]:
 im=Image.new('RGBA',(76*S,300*S));d=ImageDraw.Draw(im);tip=232-length
 def poly(points,col):d.polygon([(round(x*S),round(y*S)) for x,y in points],fill=col)
 poly([(36,tip),(36+width/2,tip+24),(42,228),(30,228),(36-width/2,tip+24)],(226,230,233,255))
 poly([(36,tip+10),(36+width/2-3,tip+26),(38,216),(34,216),(36-width/2+3,tip+26)],(8,10,12,255))
 d.line([(36*S,(tip+8)*S),(36*S,215*S)],fill=(142,148,155),width=S)
 # Dark narrow counterweight retained from the previous build.
 tail=assets[name].crop((0,233,76,300)).resize((76*S,67*S),Image.Resampling.LANCZOS);im.alpha_composite(tail,(0,233*S));put(name,im.resize((76,300),Image.Resampling.LANCZOS))
# Native gauge resources: battery/calories continuous arcs and round markers;
# pulse/steps segmented, matching the original distinction and angular sectors.
GAUGES=[('battery',294,348,False),('heart',19,71,True),('steps',199,249,True),('calories',105,155,False)]
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
   finish=end-(end-start)*level/20 if name=='battery' else start+(end-start)*level/20
   if level:dr.arc(box,(finish if name=='battery' else start)-90,(end if name=='battery' else finish)-90,fill=(193,199,206,255),width=8*S)
   px,py=point(181,finish);dr.ellipse((px-4*S,py-4*S,px+4*S,py+4*S),fill=(242,244,246,255))
  box={'battery':(52,52,240,204),'heart':(285,52,432,204),'steps':(52,285,204,432),'calories':(285,285,432,432)}[name]
  put(name+'_scale_'+str(level),im.resize((480,480),Image.Resampling.LANCZOS).crop(box))
# Curved perimeter data uses the original native IMG rotation mechanism.
for i in range(10):put('arc_'+str(i),glyph(str(i),13,width=8))
put('arc_percent',glyph('%',12,width=10));put('battery_percent',glyph('%',22,width=18));put('arc_dash',glyph('−',11,width=8))
# Four native indicators placed beside the appropriate curved values.
original_bg=decode((P/'original-background.bin').read_bytes())
for name,box in [('battery',(112,68,144,100)),('heart',(305,58,342,87)),('steps',(137,389,170,425)),('calories',(305,389,342,427))]:
 ar=np.array(original_bg.crop(box));mx=ar[:,:,:3].max(axis=2).astype(float);mn=ar[:,:,:3].min(axis=2).astype(float);alpha=np.clip((mx-mn-12)*2,0,255).astype('uint8');ar[:,:,:3]=220;ar[:,:,3]=alpha;put('arc_icon_'+name,Image.fromarray(ar).resize((11,12),Image.Resampling.LANCZOS))
for level in range(11):
 im=Image.new('RGBA',(40*S,18*S));di=ImageDraw.Draw(im);di.rounded_rectangle((S,S,36*S,17*S),radius=3*S,outline=(221,225,230,255),width=2*S);di.rectangle((37*S,6*S,39*S,12*S),fill=(221,225,230,255))
 if level:di.rectangle((4*S,4*S,round((4+29*level/10)*S),14*S),fill=(195,201,208,255))
 put('battery_icon_'+str(level),im.resize((40,18),Image.Resampling.LANCZOS))
put('low',glyph('↓',14,width=8));put('high',glyph('↑',14,width=8));put('forecast_degree',glyph('°',12,width=8));put('forecast_minus',glyph('−',14,width=8))
TAPS=[['battery',190,62,100,100,'Settings_batteryManagerScreen'],['weather',190,298,100,107,'WeatherScreen'],['heart',310,190,100,100,'heart_app_Screen'],['steps',70,190,100,100,'activityAppScreen'],['date',174,413,132,24,'ScheduleCalScreen'],['hours',181,180,54,32,'StopWatchScreen'],['minutes',245,180,54,32,'CountdownAppScreen']]
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
   n=f+'_'+c if c.isdigit() else ('metric_dot' if f=='metric' else 'dot');paste(n,x,y);x+=assets[n].width
 for name,level in [('battery',14),('heart',5),('steps',14),('calories',9)]:paste(name+'_scale_'+str(level),52 if name in ['battery','steps'] else 285,52 if name in ['battery','heart'] else 285)
 def curved(t,center,bottom=False):
  for i,c in enumerate(t):
   g=assets['arc_'+c if c.isdigit() else 'arc_percent'];ang=center+(i-(len(t)-1)/2)*3.2*(-1 if bottom else 1)
   rad=165;xx=240+rad*math.sin(math.radians(ang));yy=240-rad*math.cos(math.radians(ang));g=g.rotate(-(ang-180 if bottom else ang),Image.Resampling.BICUBIC,expand=True);im.alpha_composite(g,(round(xx-g.width/2),round(yy-g.height/2)))
 curved('71%',319);curved('72',45);curved('6972',224,True);curved('228',132,True)
 for name,angle,bottom in [('battery',306,False),('heart',32,False),('steps',237,True),('calories',145,True)]:
  g=assets['arc_icon_'+name];g=g.rotate(-(angle-180 if bottom else angle),Image.Resampling.BICUBIC,expand=True);xx=240+165*math.sin(math.radians(angle));yy=240-165*math.cos(math.radians(angle));im.alpha_composite(g,(round(xx-g.width/2),round(yy-g.height/2)))
 paste('battery_icon_7',220,78);digits('71','battery',213,112);paste('battery_percent',249,114)
 paste('walk_icon',103,205);digits('6972','step',84,252)
 paste('heart_icon',340,205);digits('72','value',342,252)
 paste('weather_3',224,297);digits('4','value',225,337);paste('degree',243,337)
 paste('low',195,369);paste('high',242,369);digits('2','forecast',215,369);paste('forecast_degree',223,369);digits('7','forecast',262,369);paste('forecast_degree',270,369)
 digits('01','date',180,415);paste('date_dot',208,415);digits('11','date',214,415);paste('week_6',248,414)
 digits('10','time',181,180);paste('colon',235,180);digits('08','time',245,180)
 for n,px,py,angle in [('hour',36,232,304),('minute',36,232,48)]+([] if aod else [('second',6,222,216)]):
  cv=Image.new('RGBA',(960,960));cv.alpha_composite(assets[n],(480-px,480-py));cv=cv.rotate(-angle,resample=Image.Resampling.BICUBIC,center=(480,480));im.alpha_composite(cv.crop((240,240,720,720)))
 # The Grey axle covers the join; both tails behind it remain Blue Scale.
 paste('cap',227,227)
 if aod:
  a=np.array(im);a[:,:,:3]=(a[:,:,:3]*.38).astype('uint8');im=Image.fromarray(a)
 return im
preview=render();preview.save(D/(B+'-preview.png'));render(True).save(D/(B+'-AOD-preview.png'));files['assets/preview.png']=encode(preview.resize((240,240),Image.Resampling.LANCZOS))
m=json.loads(old['app.json']);m['app']['appId']=10623141;m['app']['appName']='Графит-арм';m['app']['version']={'code':1,'name':'1.0.0'};m['i18n']['en-US']['appName']='Графит-арм';m['packageInfo']['timeStamp']=1793491200;mb=json.dumps(m,ensure_ascii=False).encode();(P/'app.json').write_bytes(mb);files['app.json']=mb
files['app.js']=(P/'app.js').read_bytes();files['watchface/index.js']=(P/'watchface.js').read_bytes()
def archive(items):
 b=io.BytesIO()
 with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED) as z:
  for n,v in items.items():z.writestr(n,v)
 return b.getvalue()
(D/(B+'-RU-Balance2.zpk')).write_bytes(archive({'device.zip':archive(files),'app-side.zip':archive({'app.json':mb})}))
target=ROOT/'verify-graphite-arm';target.mkdir(exist_ok=True)
for n,v in files.items():p=target/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(v)
url='zpkd1://raw.githubusercontent.com/lepilinvitold-boop/Amazfit-watchfaces/graphite-arm-1.0.0/dist/'+B+'-RU-Balance2.zpk';(D/(B+'-install-url.txt')).write_text(url)
q=QrCodeWidget(url,barLevel='M');q.qr.make();matrix=q.qr.modules;n=len(matrix);qr=Image.new('RGB',((n+8)*8,)*2,'white');draw=ImageDraw.Draw(qr)
for y,row in enumerate(matrix):
 for x,v in enumerate(row):
  if v:draw.rectangle(((x+4)*8,(y+4)*8,(x+5)*8-1,(y+5)*8-1),fill='black')
qr.save(D/(B+'-zepp-qr.png'))
print('Built',B,'appId',m['app']['appId'],'assets',len(files))
