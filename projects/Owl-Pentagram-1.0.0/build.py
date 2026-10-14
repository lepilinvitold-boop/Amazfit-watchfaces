from pathlib import Path
import io,json,math,struct,zipfile,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
P=Path(__file__).resolve().parent; ROOT=P.parents[1]; D=ROOT/'dist'; B='Owl-Pentagram-v1.0.0'; S=4
src=D/'Owl-Graphite-Color-v1.0.9-RU-Balance2.zpk'
source_hash=hashlib.sha256(src.read_bytes()).hexdigest()
with zipfile.ZipFile(src) as z:
 with zipfile.ZipFile(io.BytesIO(z.read('device.zip'))) as d: old={n:d.read(n) for n in d.namelist()}
def decode(b):
 w,h=struct.unpack_from('<HH',b,12);aw=struct.unpack_from('<I',b,22)[0];p=np.frombuffer(b[64:1088],np.uint8).reshape(256,4);a=p[np.frombuffer(b[1088:],np.uint8).reshape(h,w)][:,:aw].copy();alpha=a[:,:,3:4].astype(float);a[:,:,:3]=np.clip(np.divide(a[:,:,:3].astype(float)*255,alpha,out=np.zeros_like(a[:,:,:3],dtype=float),where=alpha>0),0,255).astype('uint8');return Image.fromarray(a)
def encode(im):
 im=im.convert('RGBA');w,h=im.size;pw=(w+15)//16*16;t=Image.new('RGBA',(pw,h));t.alpha_composite(im);q=t.quantize(colors=256,method=Image.Quantize.FASTOCTREE);p=np.zeros((256,4),np.uint8);e=np.frombuffer(q.palette.palette,np.uint8).reshape(-1,4);p[:len(e)]=e;p[:,:3]=np.rint(p[:,:3].astype(float)*p[:,3:4]/255).astype('uint8');head=bytearray(64);head[:18]=bytes.fromhex('2e0101000000012000000000000000000820');struct.pack_into('<HH',head,12,pw,h);head[18:22]=b'SOMH';struct.pack_into('<I',head,22,w);return bytes(head)+p.tobytes()+np.array(q).tobytes()
F='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def glyph(t,size,color=170):
 f=ImageFont.truetype(F,size*S);b=f.getbbox(t);im=Image.new('RGBA',((b[2]-b[0])+2*S,size*S+4*S));ImageDraw.Draw(im).text((S,-b[1]+S),t,font=f,fill=(color,color,color,255));return im.resize((round(im.width/S),round(im.height/S)),Image.Resampling.LANCZOS)
def poly(rad,angle):a=math.radians(angle);return np.array([240+rad*math.sin(a),240-rad*math.cos(a)])
yy,xx=np.mgrid[:480*S,:480*S];dx=xx/S-240;dy=yy/S-240;r=np.hypot(dx,dy);light=(-dx-dy)/np.maximum(r,1)/math.sqrt(2)
v=np.zeros_like(r)
v=np.where((r>=212)&(r<=239),29+12*light,v)
v=np.where((r>=235)&(r<=239),65+30*light-12*(r-235),v)
v=np.where((r>=211)&(r<215),80+35*light-16*(r-211),v)
v=np.where((r>=202)&(r<211),8,v)
v=np.where((r>=200)&(r<202),85+25*light,v)
v=np.where((r>=194)&(r<200),153+30*light+2*np.sin(dy*18+dx*.2),v)
v=np.where((r>=192)&(r<194),80+35*light,v)
arr=np.zeros((480*S,480*S,4),np.uint8);arr[:,:,:3]=np.clip(v[:,:,None],0,255);arr[:,:,3]=255;bg=Image.fromarray(arr);dr=ImageDraw.Draw(bg)
def ln(a,b,col,w):dr.line([tuple(a*S),tuple(b*S)],fill=(col,col,col,255),width=round(w*S))
def label(t,x,y,size=12,col=145):
 im=glyph(t,size,col).resize((glyph(t,size,col).width*S,glyph(t,size,col).height*S));bg.alpha_composite(im,(round(x*S-im.width/2),round(y*S)))
for i in range(60):ln(poly(203,i*6),poly(210 if i%5==0 else 207,i*6),175 if i%5==0 else 130,2 if i%5==0 else .8)
for i in range(0,60,5):
 im=glyph('60' if i==0 else f'{i:02}',14,195);im=im.resize((im.width*S,im.height*S)).rotate(-(i*6-180 if 90<i*6<270 else i*6),Image.Resampling.BICUBIC,expand=True);p=poly(225,i*6)*S;bg.alpha_composite(im,(round(p[0]-im.width/2),round(p[1]-im.height/2)))
for lo,hi in [(6,24),(36,54),(66,84)]:
 dr.arc((15*S,15*S,465*S,465*S),lo-90,hi-90,fill=(138,138,138,255),width=6*S)
 for a in range(lo,hi+1,6):ln(poly(220,a),poly(230,a),155,2)
# Centre-line radius adjusted for exact miter tips at outer radius 186.
width=11; tip_radius=186; radius=tip_radius-width/(2*math.sin(math.radians(18)))
verts=[poly(radius,i*72) for i in range(5)]; order=[0,2,4,1,3]; points=[verts[i] for i in order]
mask=Image.new('L',bg.size);md=ImageDraw.Draw(mask)
def intersection(a,u,b,v):
 return a+u*np.linalg.solve(np.column_stack((u,-v)),b-a)[0]
tip_radii=[]
for i,a in enumerate(points):
 b=points[(i+1)%5];u=(b-a)/np.linalg.norm(b-a);n=np.array([-u[1],u[0]])*width/2
 md.polygon([tuple(p*S) for p in [a+n,b+n,b-n,a-n]],fill=255)
 prev=points[(i-1)%5];v=(a-prev)/np.linalg.norm(a-prev);m=np.array([-v[1],v[0]])*width/2
 for sign in [-1,1]:
  joint=intersection(a+sign*m,v,a+sign*n,u)
  md.polygon([tuple(p*S) for p in [a,a+sign*m,joint,a+sign*n]],fill=255)
  if np.linalg.norm(joint-np.array([240,240]))>radius:tip_radii.append(float(np.linalg.norm(joint-np.array([240,240]))))
assert len(tip_radii)==5 and all(abs(t-tip_radius)<1e-6 for t in tip_radii)
metal=Image.fromarray(np.dstack([np.clip(150+22*light+4*np.sin(dy*2.5+dx*.5),0,255).astype('uint8')]*3+[np.full(r.shape,255,np.uint8)]))
edge=mask.filter(ImageFilter.MinFilter(9));border=Image.new('RGBA',bg.size,(83,83,83,255));bg.paste(border,(0,0),mask);bg.paste(metal,(0,0),edge)
# Five crossings: segment i passes over segment i+2; each segment alternates.
crossings=[]
for i in range(5):
 a=points[i];b=points[(i+1)%5];j=(i+2)%5;c=points[j];d=points[(j+1)%5];p=intersection(a,b-a,c,d-c);crossings.append(p.tolist())
 u=(b-a)/np.linalg.norm(b-a);n=np.array([-u[1],u[0]])
 ln(p-u*10,p+u*10,40,width+2)
 ln(p-u*10,p+u*10,105,width)
 ln(p-u*10,p+u*10,163,width-2)
# Labels and theme icons share one subdued monochrome palette.
label('СТРЕСС',145,126);label('ПУЛЬС',330,126);label('ШАГИ',103,274);label('КМ',378,274)
dr.rounded_rectangle((230*S,124*S,249*S,137*S),radius=2*S,outline=(160,160,160),width=2*S)
dr.line((252*S,127*S,252*S,134*S),fill=(160,160,160),width=2*S)
dr.line((234*S,128*S,245*S,128*S),fill=(160,160,160),width=2*S)
dr.line((234*S,133*S,245*S,133*S),fill=(160,160,160),width=2*S)
dr.polygon([(x*S,y*S) for x,y in [(315,105),(319,100),(325,100),(330,105),(335,100),(342,100),(346,105),(330,119)]],outline=(165,165,165),width=2*S)
dr.line([(x*S,y*S) for x,y in [(132,109),(138,109),(141,101),(145,118),(149,106),(152,109),(158,109)]],fill=(155,155,155),width=2*S)
dr.ellipse((370*S,248*S,386*S,264*S),outline=(155,155,155),width=2*S)
dr.polygon([(371*S,260*S),(385*S,260*S),(378*S,271*S)],fill=(155,155,155))
for x,y in [(97,251),(107,247)]:
 dr.ellipse(((x-3)*S,y*S,(x+3)*S,(y+12)*S),fill=(150,150,150))
bg=bg.resize((480,480),Image.Resampling.LANCZOS);bg.save(D/(B+'-background.png'))
files={'app.js':old['app.js'],'watchface/index.js':(P/'watchface.js').read_bytes()}
manifest=json.loads(old['app.json']);manifest['app'].update(appId=10623100,appName='Owl Pentagram',version={'code':1,'name':'1.0.0'});manifest['i18n']['en-US']['appName']='Owl Pentagram';manifest['packageInfo']['timeStamp']=1792011600;mb=json.dumps(manifest,ensure_ascii=False).encode();files['app.json']=mb;(P/'app.json').write_bytes(mb);(P/'app.js').write_bytes(old['app.js'])
assets={'background.png':bg}
for name,size in [('value',26),('battery',16),('time',26),('date',23)]:
 for i in range(10):
  im=glyph(str(i),size)
  if name=='value':im=im.resize((17,im.height),Image.Resampling.LANCZOS)
  if name=='battery':im=im.resize((11,im.height),Image.Resampling.LANCZOS)
  assets[f'{name}_{i}.png']=im
dot=Image.new('RGBA',(9,30));dot.alpha_composite(glyph(',',18),(0,20));assets['dot.png']=dot;assets['minus.png']=glyph('-',26);assets['degree.png']=glyph('°',23);assets['percent.png']=glyph('%',12).resize((8,20),Image.Resampling.LANCZOS)
for i,t in enumerate(['ПН','ВТ','СР','ЧТ','ПТ','СБ','ВС']):assets[f'week_{i}.png']=glyph(t,23)
for n in ['hour.png','minute.png','second.png','cap.png']+[f'weather_{i}.png' for i in range(29)]: 
 im=decode(old['assets/'+n]);a=np.array(im);gray=np.mean(a[:,:,:3],axis=2);a[:,:,:3]=np.minimum(gray[:,:,None],170).astype('uint8') if n.startswith('weather') else a[:,:,:3];assets[n]=Image.fromarray(a)
import re
taps=json.loads(re.search(r'const taps = (.*)',(P/'watchface.js').read_text()).group(1))
for n,x,y,w,h,url in taps:assets['hit_'+n+'.png']=Image.new('RGBA',(w,h),(0,0,0,1))
for n,im in list(assets.items()):
 files['assets/'+n]=encode(im)
 if not n.startswith('hit_'):
  a=np.array(im.convert('RGBA'));a[:,:,:3]=(a[:,:,:3]*.3).astype('uint8');files['assets/aod_'+n]=encode(Image.fromarray(a))
# Test the actual opaque pixels of widest data strings against star geometry.
star=np.array(mask.resize((480,480),Image.Resampling.LANCZOS))>32
cases=[('100',108,143,70,'value'),('255',302,143,60,'value'),('100%',216,156,48,'battery'),('99999',62,293,90,'value'),('99,99',338,293,84,'value'),('23',126,194,0,'time'),('59',310,194,0,'time'),('31',181,292,0,'date')]
for t,x,y,w,name in cases:
 ims=[assets['dot.png' if c==',' else 'percent.png' if c=='%' else name+'_'+c+'.png'] for c in t]
 total=sum(im.width for im in ims);pos=x+round((w-total)/2) if w else x
 assert not w or total<=w,(t,total,w)
 for im in ims:
  ink=np.array(im)[:,:,3]>64
  assert not np.any(star[y:y+im.height,pos:pos+im.width]&ink),('Data overlaps star',t,pos,y)
  pos+=im.width
for i in range(7):
 im=assets[f'week_{i}.png'];ink=np.array(im)[:,:,3]>64
 assert not np.any(star[292:292+im.height,265:265+im.width]&ink),('Week overlaps',i)
preview=bg.copy()
def put(t,x,y,name='value'):
 pos=x
 for c in t:
  n='dot.png' if c in '.,' else 'minus.png' if c=='-' else 'degree.png' if c=='°' else 'percent.png' if c=='%' else name+'_'+c+'.png'
  im=assets[n];preview.alpha_composite(im,(pos,y));pos+=im.width
put('38',128,143);put('72',313,143);put('84%',225,156,'battery');put('8668',68,293);put('6,62',352,293);put('23',126,194,'time');put('42',310,194,'time');put('14',181,292,'date');preview.alpha_composite(assets['week_2.png'],(265,292));preview.alpha_composite(assets['weather_2.png'],(188,373));put('10°',226,373)
# Rotate around the native hand pivot for an honest static preview.
for n,pivot,angle in [('hour.png',(21,156),330),('minute.png',(19,192),204),('second.png',(6,222),42)]:
 canvas=Image.new('RGBA',(480,480));canvas.alpha_composite(assets[n],(240-pivot[0],240-pivot[1]));canvas=canvas.rotate(-angle,Image.Resampling.BICUBIC,center=(240,240));preview.alpha_composite(canvas)
preview.alpha_composite(assets['cap.png'],(227,227))
preview.save(D/(B+'-preview.png'));files['assets/preview.png']=encode(preview.resize((240,240)))
def archive(items):
 b=io.BytesIO()
 with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED) as z:
  for n,v in items.items():z.writestr(n,v)
 return b.getvalue()
zpk=D/(B+'-RU-Balance2.zpk');zpk.write_bytes(archive({'device.zip':archive(files),'app-side.zip':archive({'app.json':mb})}))
check=P/'check';check.mkdir(exist_ok=True)
for n,b in files.items():p=check/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
geometry={'center':[240,240],'outer_tip_radius':tip_radius,'ring_inner_radius':192,'tip_gap':6,'strip_width':width,'angles':[i*72 for i in range(5)],'crossings':crossings,'source_sha256':source_hash}
(P/'geometry.json').write_text(json.dumps(geometry,indent=2))
assert hashlib.sha256(src.read_bytes()).hexdigest()==source_hash
print('Built',zpk,'appId',manifest['app']['appId'])
