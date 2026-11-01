from pathlib import Path
import numpy as np,math
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
codec=P.parent/'Owl-Graphite-Color-1.0.9/build.py';ns={'__file__':str(codec)};exec(codec.read_text().split('with zipfile.ZipFile')[0],ns)
y,x=np.mgrid[:480,:480];centres=[(240,110),(110,240),(370,240),(240,370)]
assert {math.hypot(a-240,b-240) for a,b in centres}=={130}
assert all(math.hypot(a-240,b-240)+65<201 for a,b in centres)
circles=np.logical_or.reduce([(x-a)**2+(y-b)**2<=66**2 for a,b in centres]);clock=(x>=180)&(x<300)&(y>=180)&(y<210)
for name,ox,oy in [('battery',40,40),('stress',240,40),('steps',40,240),('calories',240,240)]:
 for level in range(21):
  im=ns['decode']((ROOT/f'verify-graphite-arm-112/assets/{name}_scale_{level}.png').read_bytes());assert im.size==(200,200)
  ink=np.array(im)[:,:,3]>32
  assert not (ink&circles[oy:oy+200,ox:ox+200]).any(),(name,level,'circle')
  assert not (ink&clock[oy:oy+200,ox:ox+200]).any(),(name,level,'clock')
# All pre-rotated time/date glyphs stay outside the four circular rims.
import json
layout=json.loads((P/'layout.json').read_text())
for family,key in [('nt','normal_time'),('at','aod_time'),('dt','date')]:
 for i,(px,py) in enumerate(layout[key]):
  for path in (ROOT/'verify-graphite-arm-112/assets').glob(f'{family}_{i}_*.png'):
   im=ns['decode'](path.read_bytes());ink=np.array(im)[:,:,3]>64
   assert not (ink&circles[py:py+48,px:px+48]).any(),path.name
print('PASS: all scale frames and rotated time/date glyphs clear circular rims; symmetric 130px circle placement.')

# Render all one/two-digit signed temperatures using the native alignment/spacing.
for side in ['low','high']:
 for value in range(-99,100):
  glyphs=[ns['decode']((ROOT/f'verify-graphite-arm-112/assets/forecast_{c}.png').read_bytes()) if c!='-' else ns['decode']((ROOT/'verify-graphite-arm-112/assets/forecast_minus.png').read_bytes()) for c in str(value)]
  glyphs.append(ns['decode']((ROOT/'verify-graphite-arm-112/assets/forecast_degree.png').read_bytes()))
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
   g=ns['decode']((ROOT/f'verify-graphite-arm-112/assets/{name}.png').read_bytes())
   angle=center+(i-(len(text)-1)/2)*5.2*(-1 if bottom else 1)
   r=159;cx=240+r*math.sin(math.radians(angle));cy=240-r*math.cos(math.radians(angle))
   g=g.rotate(-(angle-180 if bottom else angle),Image.Resampling.BICUBIC,expand=True)
   px,py=round(cx-g.width/2),round(cy-g.height/2);a=np.array(g)[:,:,3]>64;gy,gx=np.where(a)
   assert not circles[py+gy,px+gx].any(),(center,text,'label/circle')
print('PASS: enlarged gauge labels clear circle rims, including 9999% and 255 bpm.')

# Both lower native readouts use unchanged arc digits and matching 25px units.
for side,x0,unit,texts in [('distance',80,'km',['0.00','9.99','99.99']),('calories',300,'kcal',['0','999','9999'])]:
 for text in texts:
  assets=ROOT/'verify-graphite-arm-112/assets'
  glyphs=[ns['decode']((assets/('arc_'+c+'.png' if c.isdigit() else 'arc_dot.png')).read_bytes()) for c in text]+[ns['decode']((assets/('arc_'+unit+'.png')).read_bytes())]
  width=sum(g.width for g in glyphs);assert width<=100,(side,text,width);px=x0+(100-width)//2
  for im in glyphs:
   yy,xx=np.where(np.array(im)[:,:,3]>64);assert not circles[310+yy,px+xx].any(),(side,text);
   for j,(dx,dy) in enumerate(layout['date']):
    for path in assets.glob(f'dt_{j}_*.png'):
     da=np.array(ns['decode'](path.read_bytes()))[:,:,3]>64;inside=(px+xx>=dx)&(px+xx<dx+48)&(310+yy>=dy)&(310+yy<dy+48)
     assert not da[310+yy[inside]-dy,px+xx[inside]-dx].any(),(side,text,'date')
   
   scale_name='steps' if side=='distance' else 'calories';ox=40 if side=='distance' else 240;oy=240
   scale=np.array(ns['decode']((assets/(scale_name+'_scale_20.png')).read_bytes()))[:,:,3]>64
   assert not scale[310+yy-oy,px+xx-ox].any(),(side,text,'scale');px+=im.width
print('PASS: distance up to 99.99 and calories up to 9999, including units, clear the circular rims without changing digit sizes.')
