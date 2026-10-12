from pathlib import Path
import json, math, struct, zipfile, io
from PIL import Image,ImageDraw,ImageFont
import numpy as np
P=Path(__file__).resolve().parent; A=P/'assets';A.mkdir(exist_ok=True);D=P.parents[1]/'dist';D.mkdir(exist_ok=True)
S=3; green='#18bf49'
def font(n):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',n*S)
def save(im,n):im.resize((im.width//S,im.height//S),Image.Resampling.LANCZOS).save(A/(n+'.png'))
im=Image.new('RGBA',(480*S,480*S),'black');d=ImageDraw.Draw(im)
def ellipse(box,fill,outline=None,width=1):d.ellipse(tuple(int(v*S) for v in box),fill=fill,outline=outline,width=width*S)
def line(points,c,w=1):d.line([(int(x*S),int(y*S)) for x,y in points],fill=c,width=w*S)
def txt(t,x,y,n,c='white'):d.text((x*S,y*S),t,font=font(n),fill=c,anchor='mm')
def polar(r,a):a=math.radians(a);return 240+r*math.sin(a),240-r*math.cos(a)
ellipse((1,1,479,479),'#171717','#777777',2);ellipse((24,24,456,456),'#363636','#606060');ellipse((44,44,436,436),'#111111','#777777');ellipse((63,63,417,417),'#292929','#555555')
for i in range(60):
 a=i*6;line([polar(181,a),polar(190 if i%5 else 194,a)],'#aaaaaa' if i%5==0 else '#777777',2 if i%5==0 else 1)
for i in range(12):
 x,y=polar(204,i*30);txt('60' if i==0 else f'{i*5:02}',x,y,17)
for i in range(1,13):
 if i in [4,5,6,7,8]:continue
 x,y=polar(143,(i%12)*30);txt(str(i),x+2,y+2,37,'#101010');txt(str(i),x,y,37)
for i in range(1,16):line([polar(215,i*6),polar(224,i*6)],green,4)
# Lower asymmetric recessed information panel.
pts=[(82,311),(201,301),(289,227),(335,216),(385,218),(409,261),(395,320),(342,380),(276,411),(195,411),(139,383)]
d.polygon([(x*S,y*S) for x,y in pts],fill='black');line(pts+[pts[0]],'#545454',2)
txt('Amazfit',240,137,17);txt('ПОГОДА',153,231,8,'#bbbbbb');txt('ПУЛЬС',315,245,9);txt('ЗАРЯД',365,245,9);line([(289,287),(384,287)],'#cccccc');txt('МУЗЫКА',96,98,10,green);txt('ШАГИ',93,367,10,green);txt('СЕКУНДОМЕР',365,373,9,green)
save(im,'background')
for prefix,size in [('digital',43),('small',17),('date',12),('weather',19)]:
 for c in '0123456789:-.%':
  f=font(size); box=f.getbbox(c);w=max(1,math.ceil(f.getlength(c)/S));img=Image.new('RGBA',(w*S,(size+7)*S));ImageDraw.Draw(img).text((0,0),c,font=f,fill='white');save(img,prefix+'_'+{'(': 'x',':':'colon','-':'minus','.':'dot','%':'percent'}.get(c,c))
for i,t in enumerate(['ПОНЕДЕЛЬНИК','ВТОРНИК','СРЕДА','ЧЕТВЕРГ','ПЯТНИЦА','СУББОТА','ВОСКРЕСЕНЬЕ']):
 img=Image.new('RGBA',(110*S,20*S));ImageDraw.Draw(img).text((55*S,0),t,font=font(10),fill='white',anchor='mt');save(img,'week_'+str(i))
for name,length,width,col in [('hour',101,18,'#dddddd'),('minute',161,13,'#eeeeee'),('second',180,3,green)]:
 img=Image.new('RGBA',(40*S,(length+35)*S));dr=ImageDraw.Draw(img);x=20*S; pivot=length*S
 dr.polygon([(x,0),(x+width*S/2,12*S),(x+width*S/2,pivot),(x,pivot+25*S),(x-width*S/2,pivot),(x-width*S/2,12*S)],fill=col)
 if name!='second':dr.line([(x,25*S),(x,pivot-17*S)],fill='#222222',width=3*S)
 save(img,name)
img=Image.new('RGBA',(14*S,14*S));ImageDraw.Draw(img).ellipse((0,0,14*S-1,14*S-1),fill='#999999',outline='#111111',width=3*S);save(img,'cap')
# Transparent tap targets.
for name,w,h in [('steps',70,40),('music',55,35),('timer',80,40)]:Image.new('RGBA',(w,h)).save(A/('tap_'+name+'.png'))
for f in list(A.glob('*.png')):
 if f.stem.startswith('tap_'):continue
 a=np.array(Image.open(f).convert('RGBA'));a[:,:,:3]=(a[:,:,:3].astype(float)*.28).astype('uint8');Image.fromarray(a).save(A/('aod_'+f.name))
manifest={'configVersion':'v2','app':{'appId':10623001,'appName':'Amazfit Green RU','appType':'watchface','version':{'code':1,'name':'1.0.0'},'icon':'preview.png','cover':['preview.png'],'vender':'Vitold personal','description':'Русский аналогово-цифровой циферблат'},'runtime':{'apiVersion':{'minVersion':'1.0','target':'1.0.1','compatible':'1.0.0'}},'permissions':[],'i18n':{'en-US':{'appName':'Amazfit Green RU'}},'defaultLanguage':'en-US','designWidth':480,'module':{'watchface':{'path':'watchface/index','main':1,'editable':0,'lockscreen':1}},'platforms':[{'name':'Balance 2','deviceSource':v} for v in [9568512,9568513,9568515]],'watchfacePreview':{'icon':'preview.png','size':[]}}
(P/'app.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
# Preview uses the very same source assets and widget positions.
canvas=Image.open(A/'background.png').convert('RGBA')
def text(t,prefix,x,y):
 for c in t:
  n={'-':'minus',':':'colon','.':'dot','%':'percent'}.get(c,c);a=Image.open(A/(prefix+'_'+n+'.png'));canvas.alpha_composite(a,(x,y));x+=a.width
text('12','digital',153,327);text(':','digital',233,327);text('42','digital',249,327);text('5508','date',86,331);text('40','small',337,337);text('83','small',303,259);text('97','small',356,259);text('27.01','date',284,308);text('18','weather',141,250);canvas.alpha_composite(Image.open(A/'week_2.png'),(161,308))
for name,pivot,angle in [('hour',101,22),('minute',161,252),('second',180,240)]:
 layer=Image.new('RGBA',(480,480));layer.alpha_composite(Image.open(A/(name+'.png')),(220,240-pivot));canvas.alpha_composite(layer.rotate(-angle,center=(240,240),resample=Image.Resampling.BICUBIC))
canvas.alpha_composite(Image.open(A/'cap.png'),(233,233));canvas.save(D/'Amazfit-Green-RU-v1.0.0-preview.png');canvas.resize((240,240)).save(A/'preview.png')
# Zepp native paletted assets: padded width, SOMH header, BGRA palette.
def encode(im):
 im=im.convert('RGBA');width,height=im.size;pw=(width+7)//8*8;tmp=Image.new('RGBA',(pw,height));tmp.alpha_composite(im);a=np.array(tmp);q=tmp.convert('RGB').quantize(colors=255);idx=np.array(q);idx[a[:,:,3]==0]=255;pal=np.zeros((256,4),np.uint8);pal[:255,:3]=np.array((q.getpalette()+[0]*765)[:765],np.uint8).reshape(255,3)[:,::-1];pal[:255,3]=255
 b=bytearray(64);b[:12]=bytes.fromhex('2e0101000000012000000000');struct.pack_into('<HH',b,12,pw,height);b[16:22]=bytes.fromhex('0820534f4d48');struct.pack_into('<I',b,22,width);b[26]=1
 return bytes(b)+pal.tobytes()+idx.tobytes()
device=io.BytesIO();mb=json.dumps(manifest,ensure_ascii=False).encode()
with zipfile.ZipFile(device,'w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('app.json',mb);z.writestr('watchface/index.js',(P/'watchface.js').read_bytes())
 for f in A.glob('*.png'):z.writestr('assets/'+f.name,encode(Image.open(f)))
side=io.BytesIO()
with zipfile.ZipFile(side,'w',zipfile.ZIP_DEFLATED) as z:z.writestr('app.json',mb)
with zipfile.ZipFile(D/'Amazfit-Green-RU-v1.0.0-Balance2.zpk','w',zipfile.ZIP_DEFLATED) as z:z.writestr('device.zip',device.getvalue());z.writestr('app-side.zip',side.getvalue())
print('Generated assets, preview and ZPK')
