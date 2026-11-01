from pathlib import Path
import io,json,zipfile,math,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from reportlab.graphics.barcode.qr import QrCodeWidget
P=Path(__file__).resolve().parent;ROOT=P.parents[1];D=ROOT/'dist';B='Graphite-Arm-v1.0.9';S=4
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
for name,size,width in [('value',30,18),('time',38,27),('date',22,14),('small',17,11),('step',30,18),('metric',13,7),('battery',30,18),('forecast',25,10)]:
 for i in range(10):put(name+'_'+str(i),glyph(str(i),size,width=width))
put('dot',glyph('.',24,width=7));put('minus',glyph('−',24,width=14));put('degree',glyph('°',21,width=13));put('colon',glyph(':',38,width=10));put('date_dot',glyph('.',22,width=6))
# Align punctuation to the numeric baseline, not the top of its ink box.
for n,height in [('dot',18),('date_dot',17),('colon',29)]:
 g=assets[n];cv=Image.new('RGBA',(g.width,height));cv.alpha_composite(g,(0,height-g.height));put(n,cv)
md=Image.new('RGBA',(4,10));md.alpha_composite(glyph('.',13,width=4),(0,8));put('metric_dot',md)
put('km',glyph(' КМ',12));put('kcal',glyph(' ККАЛ',12))
for i,t in enumerate(['ПН','ВТ','СР','ЧТ','ПТ','СБ','ВСК']):
 g=glyph(t,20);im=Image.new('RGBA',(54,24));im.alpha_composite(g,((54-g.width)//2,0));put('week_'+str(i),im)
for i in range(29):put('weather_'+str(i),oldasset('weather_'+str(i)).resize((26,26),Image.Resampling.LANCZOS))
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
curve((305,110),(315,145),(335,165),(370,175))
outline.append((370*S,305*S))
curve((370,305),(335,315),(315,335),(305,370))
outline.append((175*S,370*S))
curve((175,370),(165,335),(145,315),(110,305))
outline.append((110*S,175*S))
curve((110,175),(145,165),(165,145),(175,110))
ImageDraw.Draw(mask).polygon(outline,fill=255)
from scipy.ndimage import distance_transform_edt,gaussian_filter
from PIL import ImageChops
y,x=np.mgrid[:480*S,:480*S];inside=np.array(mask)>0
distance=distance_transform_edt(inside)/S
gy,gx=np.gradient(distance);norm=np.maximum(np.hypot(gx,gy),1e-6)
light=(gx+gy)/(norm*1.414)
face=43+14*(480-x/S-y/S)/480+1.2*np.sin(x*1.6+y*.35)+.6*np.sin(x*.6-y*1.7)
# Convex edge slopes down to a dark sidewall and catches light on upper-left edges.
v=face+8*np.exp(-distance/14)
v=np.where(distance<7,55+28*light+(7-distance)*1.8,v)
v=np.where(distance<3.3,80+44*light,v)
v=np.where(distance<1.1,24+10*light,v)
# Contact shadows below the four elevated rings give the carrier a lower plane.
nearest=np.minimum.reduce([np.maximum(np.hypot(x/S-cx,y/S-cy)-65,0) for cx,cy in [(240,110),(110,240),(370,240),(240,370)]])
v-=13*np.exp(-nearest/4)
# A dark offset sidewall and soft cast shadow sit behind the illuminated face.
shadow=Image.new('RGBA',mask.size,(0,0,0,255));shadow.putalpha(Image.fromarray((gaussian_filter(np.array(mask).astype(float),2.2*S)*.8).astype('uint8')))
shadow=ImageChops.offset(shadow,2*S,3*S);bg.alpha_composite(shadow.resize((480,480),Image.Resampling.LANCZOS))
side=Image.new('RGBA',mask.size,(12,14,17,255));side.putalpha(ImageChops.offset(mask,0,2*S));bg.alpha_composite(side.resize((480,480),Image.Resampling.LANCZOS))
carrier=np.zeros((480*S,480*S,4),np.uint8);carrier[:,:,:3]=np.clip(v[:,:,None],0,255);carrier[:,:,3]=np.array(mask)
bg.alpha_composite(Image.fromarray(carrier).resize((480,480),Image.Resampling.LANCZOS))
# Broad brushed-steel annuli with polished bevels and a recessed black well.
for cx,cy in [(240,110),(110,240),(370,240),(240,370)]:
 y,x=np.mgrid[:132*S,:132*S];dx=x/S-66;dy=y/S-66;r=np.hypot(dx,dy);ang=np.arctan2(dy,dx)
 # Alternating reflections across a broad curved metal face, rather than a grey stroke.
 shine=(.5+.5*np.cos(2*(ang+.67)))**5
 fine=2*np.sin(r*39+ang*.4)+1.4*np.sin(r*73)
 face=58+169*shine+18*np.cos((r-56)/7*math.pi)+fine
 v=np.where(r>64,12,np.where(r>63,125,np.where(r>61,185-45*(r-61)+55*shine,np.where(r>53,face,np.where(r>51,160-55*(53-r)+40*shine,np.where(r>50,25,0))))))
 ar=np.zeros((132*S,132*S,4),np.uint8);ar[:,:,:3]=np.clip(v[:,:,None],0,255);ar[:,:,3]=np.where(r<=65,255,0)
 bg.alpha_composite(Image.fromarray(ar).resize((132,132),Image.Resampling.LANCZOS),(cx-66,cy-66))
# Curved silver bezels around time and date, below the moving hands.
def silver_window(cx,cy,radius,half,upper):
 scale=4;y,x=np.mgrid[:480*scale,:480*scale];dx=x/scale-cx;dy=y/scale-cy;sign=-1 if upper else 1
 theta=np.arctan2(dx,sign*dy);near=np.clip(theta,-math.radians(47),math.radians(47))
 ddx=dx-radius*np.sin(near);ddy=dy-sign*radius*np.cos(near);dist=np.hypot(ddx,ddy)
 edge=half-dist;valid=edge>=0
 nx=ddx/np.maximum(dist,1);ny=ddy/np.maximum(dist,1);light=(-nx-ny)/1.414
 shade=np.where(edge<.8,32,np.where(edge<2,165+65*light,np.where(edge<3.3,65+35*light,5+2*np.cos(dx/60))))
 ar=np.zeros((480*scale,480*scale,4),np.uint8);ar[:,:,:3]=np.clip(shade[:,:,None],0,255);ar[:,:,3]=np.where(valid,255,0)
 bg.alpha_composite(Image.fromarray(ar).resize((480,480),Image.Resampling.LANCZOS))
silver_window(240,110,87,16,False)
silver_window(240,370,85,15,True)

# Polished inner bezel lip: bright crown with dark outer separation.
by,bx=np.mgrid[:480*S,:480*S];br=np.hypot(bx/S-239.5,by/S-239.5)
shine=.5+.5*np.cos(np.arctan2(by/S-239.5,bx/S-239.5)+2.3)
ba=np.zeros((480*S,480*S,4),np.uint8)
for lo,hi,base,amp in [(199.5,200.2,20,8),(200.2,201.4,145,65),(201.4,202.2,65,24),(202.2,202.8,17,7)]:
 mask=(br>=lo)&(br<hi);tone=np.clip(base+amp*shine,0,255).astype(np.uint8)
 for ch in range(3):ba[:,:,ch][mask]=tone[mask]
 ba[:,:,3][mask]=255
bg.alpha_composite(Image.fromarray(ba).resize((480,480),Image.Resampling.LANCZOS))
put('background',bg)
# Clear metric pictograms for the two lateral circles.
heart=Image.new('RGBA',(40*S,36*S));hd=ImageDraw.Draw(heart)
hd.ellipse((0,0,22*S,22*S),fill='white');hd.ellipse((18*S,0,40*S,22*S),fill='white');hd.polygon([(0,12*S),(40*S,12*S),(20*S,36*S)],fill='white');hd.line([(2*S,17*S),(12*S,17*S),(17*S,10*S),(22*S,24*S),(27*S,17*S),(38*S,17*S)],fill=(10,10,10),width=2*S);put('heart_icon',heart.resize((24,22),Image.Resampling.LANCZOS))
# Compact walking pictogram, rounded joints, distinct arms and legs.
walk=Image.new('RGBA',(28*S,32*S));wd=ImageDraw.Draw(walk);ink=(235,238,240,255)
wd.ellipse((14*S,1*S,21*S,8*S),fill=ink)
def limb(points,width):
 pts=[(int(x*S),int(y*S)) for x,y in points];wd.line(pts,fill=ink,width=round(width*S),joint='curve')
 for x,y in points:wd.ellipse(((x-width/2)*S,(y-width/2)*S,(x+width/2)*S,(y+width/2)*S),fill=ink)
limb([(16,11),(13,19)],4)
limb([(15,12),(10,14),(7,19)],2.8)
limb([(16,12),(20,17),(24,17)],2.8)
limb([(13,19),(9,25),(5,29)],3.5)
limb([(14,19),(18,23),(20,30)],3.5)
put('walk_icon',walk.resize((21,24),Image.Resampling.LANCZOS))
# Native gauge resources: battery/calories continuous arcs and round markers;
# pulse/steps segmented, matching the original distinction and angular sectors.
GAUGES=[('battery',290,335,False),('heart',25,70,True),('steps',205,250,True),('calories',110,155,False)]
for name,sector_start,sector_end,segmented in GAUGES:
 for level in range(21):
  start,end=sector_start,sector_end
  im=Image.new('RGBA',(480*S,480*S));dr=ImageDraw.Draw(im)
  def point(r,ang):t=math.radians(ang);return ((240+r*math.sin(t))*S,(240-r*math.cos(t))*S)
  if segmented:
   for i in range(11):
    angle=start+1+(end-start-2)*i/10;active=(10-i)<round(level/20*11)
    # Radial blocks: bevel edges plus a brushed silver centre.
    for r0,r1,col,w in [(178,192,(15,17,20,255),7),(179,191,(221,225,229,255) if active else (65,69,74,255),5.5),(180,190,(158,164,171,255) if active else (39,42,47,255),4.2)]:dr.line([point(r0,angle),point(r1,angle)],fill=col,width=round(w*S))
  else:
   start+=1.25;end-=1.25
   box=tuple(v*S for v in (51,51,429,429));dr.arc(box,start-90,end-90,fill=(54,58,64,255),width=8*S)
   finish=end-(end-start)*level/20 if name in ['battery','calories'] else start+(end-start)*level/20
   if level:dr.arc(box,(finish if name in ['battery','calories'] else start)-90,(end if name in ['battery','calories'] else finish)-90,fill=(193,199,206,255),width=8*S)
   px,py=point(185,finish);dr.ellipse((px-4*S,py-4*S,px+4*S,py+4*S),fill=(242,244,246,255))
  box={'battery':(40,40,240,240),'heart':(240,40,440,240),'steps':(40,240,240,440),'calories':(240,240,440,440)}[name]
  put(name+'_scale_'+str(level),im.resize((480,480),Image.Resampling.LANCZOS).crop(box))
# Curved perimeter data uses the original native IMG rotation mechanism.
for i in range(10):put('arc_'+str(i),glyph(str(i),25,width=14))
put('arc_percent',glyph('%',24,width=16));put('battery_percent',glyph('%',25,width=18));put('arc_dash',glyph('−',11,width=8))
# Four clean 12x12 pictograms, placed upright at the start of each scale.
for name in ['battery','heart','steps','calories']:
 cv=Image.new('RGBA',(12*S,12*S));dr=ImageDraw.Draw(cv);white=(225,229,233,255)
 if name=='battery':
  dr.rounded_rectangle((S,3*S,10*S,9*S),radius=S,outline=white,width=S);dr.rectangle((10*S,5*S,11*S,7*S),fill=white);dr.rectangle((3*S,5*S,7*S,7*S),fill=white)
 elif name=='heart':cv.alpha_composite(assets['heart_icon'].resize((10*S,9*S),Image.Resampling.LANCZOS),(S,2*S))
 elif name=='steps':cv.alpha_composite(assets['walk_icon'].resize((9*S,11*S),Image.Resampling.LANCZOS),(2*S,0))
 else:
  dr.polygon([(6*S,0),(9*S,4*S),(10*S,7*S),(9*S,10*S),(6*S,12*S),(3*S,10*S),(2*S,7*S),(4*S,3*S),(4*S,7*S),(6*S,5*S)],fill=white)
  dr.polygon([(6*S,7*S),(8*S,10*S),(6*S,11*S),(4*S,10*S)],fill=(60,65,70,255))
 put('arc_icon_'+name,cv.resize((12,12),Image.Resampling.LANCZOS))
for level in range(11):
 im=Image.new('RGBA',(40*S,18*S));di=ImageDraw.Draw(im);di.rounded_rectangle((S,S,36*S,17*S),radius=3*S,outline=(221,225,230,255),width=2*S);di.rectangle((37*S,6*S,39*S,12*S),fill=(221,225,230,255))
 if level:di.rectangle((4*S,4*S,round((4+29*level/10)*S),14*S),fill=(195,201,208,255))
 put('battery_icon_'+str(level),im.resize((40,18),Image.Resampling.LANCZOS))
put('low',glyph('↓',16,width=8));put('high',glyph('↑',16,width=8));put('forecast_degree',glyph('°',19,width=6));put('forecast_minus',glyph('−',18,width=8))
for c in '0123456789. ПНВТСРЧБК':
 g=Image.new('RGBA',(12,14)) if c==' ' else glyph(c,18,width=4 if c=='.' else 12);cv=Image.new('RGBA',(20,24));cv.alpha_composite(g,((20-g.width)//2,17 if c=='.' else (24-g.height)//2));put('date_arc_'+str(ord(c)),cv)
# Fixed-position pre-rotated glyph tiles. Runtime updates SRC only.
layout={'normal_time':[],'aod_time':[],'date':[]}
for family,label in [('nt','00:00:00'),('at','00:00')]:
 widths=[19 if c.isdigit() else 7 for c in label];total=sum(widths)+len(label)-1;cursor=-total/2
 for i,(c,width) in enumerate(zip(label,widths)):
  delta=-(cursor+width/2)/87;theta=math.pi+delta
  layout['normal_time' if family=='nt' else 'aod_time'].append([round(240+87*math.sin(theta))-24,round(110-87*math.cos(theta))-24])
  for ch in ('0123456789' if c!=':' else ':'):
   g=glyph(ch,28,width=19 if ch.isdigit() else 7);rr=g.rotate(-math.degrees(delta),Image.Resampling.BICUBIC,expand=True);tile=Image.new('RGBA',(48,48));tile.alpha_composite(rr,((48-rr.width)//2,(48-rr.height)//2));put(f'{family}_{i}_{ord(ch)}',tile)
  cursor+=width+1
for i in range(9):
 theta=(i-4)*16/85;layout['date'].append([round(240+85*math.sin(theta))-24,round(370-85*math.cos(theta))-24])
 for ch in '0123456789. ПНВТСРЧБК':
  g=Image.new('RGBA',(24,30))
  if ch!=' ':
   letter=glyph(ch,23,width=5 if ch=='.' else 15);g.alpha_composite(letter,((24-letter.width)//2,21 if ch=='.' else (30-letter.height)//2))
  rr=g.rotate(-math.degrees(theta),Image.Resampling.BICUBIC,expand=True);tile=Image.new('RGBA',(48,48));tile.alpha_composite(rr,((48-rr.width)//2,(48-rr.height)//2));put(f'dt_{i}_{ord(ch)}',tile)
(P/'layout.json').write_text(json.dumps(layout))
put('range_dash',glyph('–',22,width=10))
# Vertically align a possible minus sign within the larger forecast digits.
g=glyph('−',22,width=7);cv=Image.new('RGBA',(7,19));cv.alpha_composite(g,(0,(19-g.height)//2));put('forecast_minus',cv)

TAPS=[['battery', 190, 60, 100, 100, 'Settings_batteryManagerScreen'], ['weather', 190, 320, 100, 105, 'WeatherScreen'], ['heart', 320, 190, 100, 100, 'heart_app_Screen'], ['steps', 60, 190, 100, 100, 'activityAppScreen'], ['date', 170, 272, 140, 36, 'ScheduleCalScreen'], ['alarm', 160, 160, 53, 54, 'AlarmInfoScreen'], ['stopwatch', 213, 175, 54, 40, 'StopWatchScreen'], ['countdown', 267, 160, 53, 54, 'CountdownAppScreen'], ['battery_scale0', 56, 122, 104, 64, 'activityAppScreen'], ['battery_scale1', 80, 86, 98, 36, 'activityAppScreen'], ['battery_scale2', 120, 56, 64, 30, 'activityAppScreen'], ['distance0', 56, 294, 104, 50, 'activityAppScreen'], ['distance1', 80, 344, 98, 40, 'activityAppScreen'], ['distance2', 120, 384, 64, 44, 'activityAppScreen'], ['calories0', 320, 294, 104, 50, 'activityAppScreen'], ['calories1', 302, 344, 98, 40, 'activityAppScreen'], ['calories2', 296, 384, 64, 44, 'activityAppScreen']]
put('hit_axis',Image.new('RGBA',(40,40)))
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
   g=assets['arc_'+c if c.isdigit() else 'arc_percent'];ang=center+(i-(len(t)-1)/2)*5.2*(-1 if bottom else 1)
   rad=159;xx=240+rad*math.sin(math.radians(ang));yy=240-rad*math.cos(math.radians(ang));g=g.rotate(-(ang-180 if bottom else ang),Image.Resampling.BICUBIC,expand=True);im.alpha_composite(g,(round(xx-g.width/2),round(yy-g.height/2)))
 curved('71%',315);curved('72',45);curved('70%',225,True);curved('45%',135,True)
 paste('battery_icon_7',220,76);digits('71','battery',213,107);paste('battery_percent',249,107)
 paste('walk_icon',100,204);digits('10000','step',65,237)
 paste('heart_icon',358,204);digits('72','value',352,237)
 paste('weather_3',227,319);digits('4','value',225,348);paste('degree',243,348)
 def range_value(value,right=False):
  glyphs=[assets['forecast_minus'] if c=='-' else assets['forecast_'+c] for c in str(value)]+[assets['forecast_degree']]
  width=sum(g.width for g in glyphs)-(len(glyphs)-1);x=247 if right else 233-width
  for g in glyphs:im.alpha_composite(g,(x,381));x+=g.width-1
 range_value(4);paste('range_dash',235,386);range_value(10,True)
 # Smaller HH:MM:SS follows the lower battery circle.
 chars=[glyph(c,28,width=19 if c.isdigit() else 7) for c in ('10:08' if aod else '10:08:36')]
 # The colons are aligned by their ink centre along the curve.
 total=sum(g.width for g in chars)+(len(chars)-1);cursor=-total/2
 for g in chars:
  offset=cursor+g.width/2;delta=-offset/87;theta=math.pi+delta
  x=240+87*math.sin(theta);y=110-87*math.cos(theta)
  rr=g.rotate(-math.degrees(delta),Image.Resampling.BICUBIC,expand=True);im.alpha_composite(rr,(round(x-rr.width/2),round(y-rr.height/2)));cursor+=g.width+1
 # Slightly larger date follows the upper weather circle.
 label='01.11 ВСК';spacing=16
 for i,c in enumerate(label):
  theta=(i-(len(label)-1)/2)*spacing/85
  g=Image.new('RGBA',(24,30))
  if c!=' ':
   letter=glyph(c,23,width=5 if c=='.' else 15);g.alpha_composite(letter,((24-letter.width)//2,21 if c=='.' else (30-letter.height)//2))
  rr=g.rotate(-math.degrees(theta),Image.Resampling.BICUBIC,expand=True)
  x=240+85*math.sin(theta);y=370-85*math.cos(theta)
  im.alpha_composite(rr,(round(x-rr.width/2),round(y-rr.height/2)))
 for n,px,py,angle in [('hour',36,232,304),('minute',36,232,48)]+([] if aod else [('second',6,222,216)]):
  cv=Image.new('RGBA',(960,960));cv.alpha_composite(assets[n],(480-px,480-py));cv=cv.rotate(-angle,resample=Image.Resampling.BICUBIC,center=(480,480));im.alpha_composite(cv.crop((240,240,720,720)))
 # The Grey axle covers the join; both tails behind it remain Blue Scale.
 paste('cap',227,227)
 if aod:
  a=np.array(im);a[:,:,:3]=(a[:,:,:3]*.38).astype('uint8');im=Image.fromarray(a)
 return im
preview=render();preview.save(D/(B+'-preview.png'));render(True).save(D/(B+'-AOD-preview.png'));files['assets/preview.png']=encode(preview.resize((240,240),Image.Resampling.LANCZOS))
m=json.loads(old['app.json']);m['app']['appId']=10623141;m['app']['appName']='Графит-арм';m['app']['version']={'code':10,'name':'1.0.9'};m['i18n']['en-US']['appName']='Графит-арм';m['packageInfo']['timeStamp']=1793491200;mb=json.dumps(m,ensure_ascii=False).encode();(P/'app.json').write_bytes(mb);files['app.json']=mb
files['app.js']=(P/'app.js').read_bytes();files['watchface/index.js']=(P/'watchface.js').read_bytes()
def archive(items):
 b=io.BytesIO()
 with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED) as z:
  for n,v in items.items():z.writestr(n,v)
 return b.getvalue()
(D/(B+'-RU-Balance2.zpk')).write_bytes(archive({'device.zip':archive(files),'app-side.zip':archive({'app.json':mb})}))
target=ROOT/'verify-graphite-arm-109';target.mkdir(exist_ok=True)
for n,v in files.items():p=target/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(v)
url='zpkd1://raw.githubusercontent.com/lepilinvitold-boop/Amazfit-watchfaces/graphite-arm-1.0.9/dist/'+B+'-RU-Balance2.zpk';(D/(B+'-install-url.txt')).write_text(url)
q=QrCodeWidget(url,barLevel='M');q.qr.make();matrix=q.qr.modules;n=len(matrix);qr=Image.new('RGB',((n+8)*8,)*2,'white');draw=ImageDraw.Draw(qr)
for y,row in enumerate(matrix):
 for x,v in enumerate(row):
  if v:draw.rectangle(((x+4)*8,(y+4)*8,(x+5)*8-1,(y+5)*8-1),fill='black')
qr.save(D/(B+'-zepp-qr.png'))
print('Built',B,'appId',m['app']['appId'],'assets',len(files))
