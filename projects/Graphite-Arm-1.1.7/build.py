from pathlib import Path
import io,json,zipfile,math,hashlib,struct
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from reportlab.graphics.barcode.qr import QrCodeWidget
P=Path(__file__).resolve().parent;ROOT=P.parents[1];D=ROOT/'dist';B='Graphite-2-v1.1.7'
codec=P.parent/'Owl-Graphite-Color-1.0.9/build.py';ns={'__file__':str(codec)};exec(codec.read_text().split('with zipfile.ZipFile')[0],ns);encode=ns['encode'];decode=ns['decode']
base=D/'Graphite-Arm-v1.0.9-RU-Balance2.zpk'
assert hashlib.sha256(base.read_bytes()).hexdigest()=='76b71a4aa2fe45c2ef30198df503626ebbecf82c2ac1365290d2cb95e01f507e'
with zipfile.ZipFile(base) as z:
 with zipfile.ZipFile(io.BytesIO(z.read('device.zip'))) as q:files={n:q.read(n) for n in q.namelist()}
def asset(n):return decode(files['assets/'+n+'.png'])
def put(n,im):
 files['assets/'+n+'.png']=encode(im)
 a=np.array(im.convert('RGBA'));a[:,:,:3]=(a[:,:,:3]*.38).astype('uint8');files['assets/aod_'+n+'.png']=encode(Image.fromarray(a))
def tint(im,color,scale=False):
 a=np.array(im.convert('RGBA'));rgb=a[:,:,:3].astype(float);light=rgb.max(axis=2);mask=(light>90) if scale else (a[:,:,3]>0)
 out=light[:,:,None]*np.array(color)[None,None,:]/235
 a[:,:,:3][mask]=np.clip(out,0,255).astype('uint8')[mask];return Image.fromarray(a)
colors={'red':(181,104,108),'green':(123,162,133),'blue':(110,145,183),'yellow':(177,158,112),'amber':(181,138,100),'purple':(155,134,181)}
for level in range(21):
 put('fatburn_scale_'+str(level),asset('battery_scale_'+str(level)))
 put('purple_fatburn_scale_'+str(level),tint(asset('battery_scale_'+str(level)),colors['purple'],True))
 put('stress_scale_'+str(level),asset('heart_scale_'+str(level)))
 # Preserve original encoded normal/AOD frames without a second palette conversion.
 for prefix in ['', 'aod_']:files['assets/'+prefix+'sleep_scale_'+str(level)+'.png']=files['assets/'+prefix+'battery_scale_'+str(level)+'.png']
 put('amber_sleep_scale_'+str(level),tint(asset('battery_scale_'+str(level)),colors['amber'],True))
 put('distance_scale_'+str(level),asset('steps_scale_'+str(level)))
 for tone,name in [('red','battery'),('green','distance'),('blue','stress'),('yellow','calories')]:put(tone+'_'+name+'_scale_'+str(level),tint(asset(name+'_scale_'+str(level)),colors[tone],True))
for tone,color in colors.items():
 for c in list('0123456789')+['percent','dash']:put(tone+'_arc_'+c,tint(asset('arc_'+c),color))
def curved(im,t,center=135,bottom=True):
 for i,c in enumerate(t):
  g=asset('arc_'+c if c.isdigit() else 'arc_dash');ang=center+(i-(len(t)-1)/2)*5.2*(-1 if bottom else 1)
  x=240+159*math.sin(math.radians(ang));y=240-159*math.cos(math.radians(ang));g=g.rotate(-(ang-180 if bottom else ang),Image.Resampling.BICUBIC,expand=True)
  im.alpha_composite(g,(round(x-g.width/2),round(y-g.height/2)))
# Units use the same DejaVu Sans Bold 25px family as all arc digits.
def unit_glyph(text,width):
 S=4;f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',25*S);box=f.getbbox(text);im=Image.new('RGBA',(box[2]-box[0],box[3]-box[1]));ImageDraw.Draw(im).text((-box[0],-box[1]),text,font=f,fill=(235,235,235,255));im=im.resize((width,19),Image.Resampling.LANCZOS);return im
for name,text,width in [('km','км',18),('mi','ми',18),('kcal','кК',26),('min','мин',36)]:put('arc_'+name,unit_glyph(text,width))
dot=Image.new('RGBA',(4,19));ImageDraw.Draw(dot).ellipse((1,15,3,17),fill=(235,235,235,255));put('arc_dot',dot)
for tone,color in colors.items():
 for name in ['km','kcal','dot','min']:put(tone+'_arc_'+name,tint(asset('arc_'+name),color))
colon=Image.new('RGBA',(8,19));cd=ImageDraw.Draw(colon);cd.ellipse((2,4,5,7),fill=(235,235,235,255));cd.ellipse((2,13,5,16),fill=(235,235,235,255));put('arc_colon',colon)
put('amber_arc_colon',tint(asset('arc_colon'),colors['amber']))
# Neutral native missing-data marker at the same nominal arc font size.
missing=Image.new('RGBA',(24,19));missing.alpha_composite(asset('arc_dash'),(0,7));missing.alpha_composite(asset('arc_dash'),(16,7));put('load_invalid',missing)
# Original heart icon/digits: colour only, same dimensions and alpha masks.
put('red_heart_icon',tint(asset('heart_icon'),colors['red']))
for i in range(10):put('red_value_'+str(i),tint(asset('value_'+str(i)),colors['red']))
# Central battery: same native icons/digit shapes, muted red palette only below20%.
for i in range(11):put('red_battery_icon_'+str(i),tint(asset('battery_icon_'+str(i)),colors['red']))
for i in range(10):put('red_battery_'+str(i),tint(asset('battery_'+str(i)),colors['red']))
put('red_battery_percent',tint(asset('battery_percent'),colors['red']))
for name,w,h in [('stress_scale0',104,64),('stress_scale1',98,36),('stress_scale2',64,30)]:files['assets/hit_'+name+'.png']=encode(Image.new('RGBA',(w,h)))
preview=D/(B+'-preview.png')
if preview.exists():files['assets/preview.png']=encode(Image.open(preview).convert('RGBA').resize((240,240),Image.Resampling.LANCZOS))
m=json.loads(files['app.json']);m['app']['appName']='Graphite 2';m['i18n']['en-US']['appName']='Graphite 2';m['app']['version']={'code':21,'name':'1.1.7'};m['packageInfo']['timeStamp']=1793552400
mb=json.dumps(m,ensure_ascii=False).encode();(P/'app.json').write_bytes(mb);files['app.json']=mb
files['app.js']=(P/'app.js').read_bytes()
config=json.loads((P/'goal-config.json').read_text());goal=config['distance_scale_step_goal']
assert isinstance(goal,int) and not isinstance(goal,bool) and goal>0
source=(P/'watchface.js').read_text()
source=source.replace('const USER_STEP_GOAL=10000;', 'const USER_STEP_GOAL='+json.dumps(goal)+';')
files['watchface/index.js']=source.encode()
def archive(items):
 b=io.BytesIO()
 with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED) as z:
  for n,v in items.items():
   info=zipfile.ZipInfo(n,(2026,11,1,17,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,v)
 return b.getvalue()
target=ROOT/'verify-graphite-arm-117';target.mkdir(exist_ok=True)
for n,v in files.items():
 p=target/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(v)
zpk=D/(B+'-RU-Balance2.zpk');zpk.write_bytes(archive({'device.zip':archive(files),'app-side.zip':archive({'app.json':mb})}))
url='zpkd1://raw.githubusercontent.com/lepilinvitold-boop/Amazfit-watchfaces/graphite-arm-1.1.7/dist/'+B+'-RU-Balance2.zpk';(D/(B+'-install-url.txt')).write_text(url)
q=QrCodeWidget(url,barLevel='M');q.qr.make();matrix=q.qr.modules;n=len(matrix);qr=Image.new('RGB',((n+8)*8,)*2,'white');draw=ImageDraw.Draw(qr)
for y,row in enumerate(matrix):
 for x,v in enumerate(row):
  if v:draw.rectangle(((x+4)*8,(y+4)*8,(x+5)*8-1,(y+5)*8-1),fill='black')
qr.save(D/(B+'-zepp-qr.png'))
print('Built',zpk.name,hashlib.sha256(zpk.read_bytes()).hexdigest())
