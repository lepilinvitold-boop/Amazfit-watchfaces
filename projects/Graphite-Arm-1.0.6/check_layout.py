from pathlib import Path
import numpy as np,math
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
codec=P.parent/'Owl-Graphite-Color-1.0.9/build.py';ns={'__file__':str(codec)};exec(codec.read_text().split('with zipfile.ZipFile')[0],ns)
y,x=np.mgrid[:480,:480];centres=[(240,110),(110,240),(370,240),(240,370)]
assert {math.hypot(a-240,b-240) for a,b in centres}=={130}
assert all(math.hypot(a-240,b-240)+65<201 for a,b in centres)
circles=np.logical_or.reduce([(x-a)**2+(y-b)**2<=66**2 for a,b in centres]);clock=(x>=180)&(x<300)&(y>=180)&(y<210)
for name,ox,oy in [('battery',40,40),('heart',240,40),('steps',40,240),('calories',240,240)]:
 for level in range(21):
  im=ns['decode']((ROOT/f'verify-graphite-arm-106/assets/{name}_scale_{level}.png').read_bytes());assert im.size==(200,200)
  ink=np.array(im)[:,:,3]>32
  assert not (ink&circles[oy:oy+200,ox:ox+200]).any(),(name,level,'circle')
  assert not (ink&clock[oy:oy+200,ox:ox+200]).any(),(name,level,'clock')
# All pre-rotated time/date glyphs stay outside the four circular rims.
import json
layout=json.loads((P/'layout.json').read_text())
for family,key in [('nt','normal_time'),('at','aod_time'),('dt','date')]:
 for i,(px,py) in enumerate(layout[key]):
  for path in (ROOT/'verify-graphite-arm-106/assets').glob(f'{family}_{i}_*.png'):
   im=ns['decode'](path.read_bytes());ink=np.array(im)[:,:,3]>64
   assert not (ink&circles[py:py+48,px:px+48]).any(),path.name
print('PASS: all scale frames and rotated time/date glyphs clear circular rims; symmetric 130px circle placement.')

# Render all one/two-digit signed temperatures using the native alignment/spacing.
for side in ['low','high']:
 for value in range(-99,100):
  glyphs=[ns['decode']((ROOT/f'verify-graphite-arm-106/assets/forecast_{c}.png').read_bytes()) if c!='-' else ns['decode']((ROOT/'verify-graphite-arm-106/assets/forecast_minus.png').read_bytes()) for c in str(value)]
  glyphs.append(ns['decode']((ROOT/'verify-graphite-arm-106/assets/forecast_degree.png').read_bytes()))
  width=sum(g.width for g in glyphs)-len(glyphs)+1;assert width<=38
  px=233-width if side=='low' else 247
  for g in glyphs:
   a=np.array(g)[:,:,3]>64;gy,gx=np.where(a);wx=px+gx;wy=381+gy
   assert ((wx-240)**2+(wy-370)**2<50**2).all(),(side,value,'rim')
   assert ((wx<235) if side=='low' else (wx>=247)).all(),(side,value,'separator')
   px+=g.width-1
print('PASS: all 398 low/high cases from -99 to +99 stay inside the black weather well and clear of the separator.')
