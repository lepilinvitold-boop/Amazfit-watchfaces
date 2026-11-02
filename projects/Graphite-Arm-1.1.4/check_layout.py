from pathlib import Path
import numpy as np,math
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
codec=P.parent/'Owl-Graphite-Color-1.0.9/build.py';ns={'__file__':str(codec)};exec(codec.read_text().split('with zipfile.ZipFile')[0],ns)
y,x=np.mgrid[:480,:480];centres=[(240,110),(110,240),(370,240),(240,370)]
assert {math.hypot(a-240,b-240) for a,b in centres}=={130}
assert all(math.hypot(a-240,b-240)+65<201 for a,b in centres)
circles=np.logical_or.reduce([(x-a)**2+(y-b)**2<=66**2 for a,b in centres]);clock=(x>=180)&(x<300)&(y>=180)&(y<210)
for name,ox,oy in [('sleep',40,40),('stress',240,40),('steps',40,240),('calories',240,240)]:
 for level in range(21):
  im=ns['decode']((ROOT/f'verify-graphite-arm-114/assets/{name}_scale_{level}.png').read_bytes());assert im.size==(200,200)
  ink=np.array(im)[:,:,3]>32
  assert not (ink&circles[oy:oy+200,ox:ox+200]).any(),(name,level,'circle')
  assert not (ink&clock[oy:oy+200,ox:ox+200]).any(),(name,level,'clock')
# All pre-rotated time/date glyphs stay outside the four circular rims.
import json
layout=json.loads((P/'layout.json').read_text())
for family,key in [('nt','normal_time'),('at','aod_time'),('dt','date')]:
 for i,(px,py) in enumerate(layout[key]):
  for path in (ROOT/'verify-graphite-arm-114/assets').glob(f'{family}_{i}_*.png'):
   im=ns['decode'](path.read_bytes());ink=np.array(im)[:,:,3]>64
   assert not (ink&circles[py:py+48,px:px+48]).any(),path.name
print('PASS: all scale frames and rotated time/date glyphs clear circular rims; symmetric 130px circle placement.')

# Render all one/two-digit signed temperatures using the native alignment/spacing.
for side in ['low','high']:
 for value in range(-99,100):
  glyphs=[ns['decode']((ROOT/f'verify-graphite-arm-114/assets/forecast_{c}.png').read_bytes()) if c!='-' else ns['decode']((ROOT/'verify-graphite-arm-114/assets/forecast_minus.png').read_bytes()) for c in str(value)]
  glyphs.append(ns['decode']((ROOT/'verify-graphite-arm-114/assets/forecast_degree.png').read_bytes()))
  width=sum(g.width for g in glyphs)-len(glyphs)+1;assert width<=38
  px=233-width if side=='low' else 247
  for g in glyphs:
   a=np.array(g)[:,:,3]>64;gy,gx=np.where(a);wx=px+gx;wy=381+gy
   assert ((wx-240)**2+(wy-370)**2<50**2).all(),(side,value,'rim')
   assert ((wx<235) if side=='low' else (wx>=247)).all(),(side,value,'separator')
   px+=g.width-1
print('PASS: all 398 low/high cases from -99 to +99 stay inside the black weather well and clear of the separator.')
# Enlarged scale labels: test longest labels in all quadrants against circular rims.
from PIL import Image
for center,bottom in [(315,False),(45,False),(225,True),(135,True)]:
 for text in ['0%','100%','9999%','255','−']:
  for i,c in enumerate(text):
   name='arc_'+c if c.isdigit() else 'arc_percent' if c=='%' else 'arc_dash'
   g=ns['decode']((ROOT/f'verify-graphite-arm-114/assets/{name}.png').read_bytes())
   angle=center+(i-(len(text)-1)/2)*5.2*(-1 if bottom else 1)
   r=159;cx=240+r*math.sin(math.radians(angle));cy=240-r*math.cos(math.radians(angle))
   g=g.rotate(-(angle-180 if bottom else angle),Image.Resampling.BICUBIC,expand=True)
   px,py=round(cx-g.width/2),round(cy-g.height/2);a=np.array(g)[:,:,3]>64;gy,gx=np.where(a)
   assert not circles[py+gy,px+gx].any(),(center,text,'label/circle')
print('PASS: enlarged gauge labels clear circle rims, including 9999% and 255 bpm.')

# Curved lower digits: exact runtime widths, baseline, tangential rotations.
assets=ROOT/'verify-graphite-arm-114/assets'
import re
raw=(P/'watchface.js').read_text();tap_rows=json.loads(re.search(r'const taps=(\[.*?\]);',raw).group(1))
tap_masks={}
for name in ['distance','calories']:
 cover=np.zeros((480,480),bool)
 for row in tap_rows:
  if row[0].startswith(name):
   _,tx,ty,tw,th,_=row;cover[ty:ty+th,tx:tx+tw]=True
 tap_masks[name]=cover
for angle,unit,strings in [(225,'km',['0,00','5,00','99,99','100,00','−']),(135,'kcal',['0','650','9999','10000','−'])]:
 for text in strings:
  tokens=[(c if c.isdigit() else 'dot' if c==',' else 'dash',14 if c.isdigit() else 4 if c==',' else 8,19 if c!='−' else 4) for c in text]
  if text!='−':tokens.append((unit,18 if unit=='km' else 26,19))
  total=sum(t[1] for t in tokens)+(6 if text!='−' else 0);offset=-total/2
  masks=[]
  for key,width,height in tokens:
   if key==unit:offset+=6
   g=ns['decode']((assets/('arc_'+key+'.png')).read_bytes());ang=angle-(offset+width/2)/159*180/math.pi
   # Match renderer/runtime pos rounding, rather than assuming glyph-centred math.
   cv=Image.new('RGBA',(960,960));cv.alpha_composite(g,(round(240-width/2)+240,round(399-height/2)+240));cv=cv.rotate(-(ang-180),Image.Resampling.BICUBIC,center=(480,480));a=np.array(cv.crop((240,240,720,720)))[:,:,3]>64
   assert not (a&circles).any(),(angle,text,key,'circle')
   # Check every scale frame, not merely its centreline.
   for level in range(21):
    nm,ox=('steps',40) if angle==225 else ('calories',240)
    layer=np.zeros((480,480),bool);layer[240:440,ox:ox+200]=np.array(ns['decode']((assets/f'{nm}_scale_{level}.png').read_bytes()))[:,:,3]>64
    assert not (a&layer).any(),(angle,text,key,'scale',level)
   assert not (a&clock).any(),(angle,text,key,'clock')
   assert not np.any(a&~tap_masks['distance' if angle==225 else 'calories']),(angle,text,key,'tap coverage')
   assert not np.any(a&(((x-240)**2+(y-240)**2)>=201**2)),(angle,text,'bezel')
   for old in masks:assert not (a&old).any(),(angle,text,'glyph overlap')
   masks.append(a);offset+=width
print('PASS: exact curved metric-label geometry, units, circles, every scale frame, clock, bezel and neighbouring glyphs.')

# Exact runtime sleep HH:MM/dash glyphs and three SLEEP tap areas.
sleep_cover=np.zeros((480,480),bool)
for name,tx,ty,tw,th,_ in tap_rows:
 if name.startswith('battery_scale'):sleep_cover[ty:ty+th,tx:tx+tw]=True
for text in ['00:01','07:35','12:59','24:00','−−:−−']:
 for i,c in enumerate(text):
  key=c if c.isdigit() else 'colon' if c==':' else 'dash';width=14 if c.isdigit() else 8;height=4 if c=='−' else 19
  g=ns['decode']((assets/('arc_'+key+'.png')).read_bytes());cv=Image.new('RGBA',(960,960));cv.alpha_composite(g,(round(240-width/2)+240,round(81-height/2)+240));cv=cv.rotate(-(315+(i-2)*5.2),Image.Resampling.BICUBIC,center=(480,480));mask=np.array(cv.crop((240,240,720,720)))[:,:,3]>64
  assert not (mask&circles).any(),(text,c,'sleep/circle');assert not np.any(mask&~sleep_cover),(text,c,'sleep/tap')
  for level in range(21):
   scale=np.zeros((480,480),bool);scale[40:240,40:240]=np.array(ns['decode']((assets/f'sleep_scale_{level}.png').read_bytes()))[:,:,3]>64
   assert not (mask&scale).any(),(text,c,'sleep/scale')
print('PASS: full sleep range and placeholders clear circles/scales and remain within active SLEEP tap coverage.')

# All 101 readiness states: combined original scale and curved digits fit the same tap sectors.
for value in range(101):
 im=ns['decode']((assets/f'readiness_{value}.png').read_bytes());mask=np.zeros((480,480),bool);mask[40:240,40:240]=np.array(im)[:,:,3]>64
 assert not (mask&circles).any(),(value,'readiness/circle')
 assert not np.any(mask&~sleep_cover),(value,'readiness/tap')
 assert not np.any(mask&clock),(value,'readiness/clock')
print('PASS: all101 readiness frames clear circles, clock and stay inside native readiness tap sectors.')
