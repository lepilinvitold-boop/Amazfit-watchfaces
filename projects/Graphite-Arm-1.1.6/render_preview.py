from pathlib import Path
import json,math
from PIL import Image
P=Path(__file__).resolve().parent;R=P.parents[1];ns={'__file__':str(P.parent/'Owl-Graphite-Color-1.0.9/build.py')};exec(Path(ns['__file__']).read_text().split('with zipfile.ZipFile')[0],ns)
a=R/'verify-graphite-arm-116/assets'
def img(n):return ns['decode']((a/n).read_bytes())
w=json.loads(Path('/tmp/widgets.json').read_text())
for aod in [False,True]:
 out=Image.new('RGBA',(480,480));prefix='aod_' if aod else ''
 def paste(g,x,y):out.alpha_composite(g,(round(x),round(y)))
 for row in w:
  p=row['props'];t=row['type']
  if p.get('show_level')!=('ONAL_AOD' if aod else 'ONLY_NORMAL') or not row.get('visible',True):continue
  if t=='IMG':
   g=img(p['src'])
   if 'pos_x' in p:
    cv=Image.new('RGBA',(960,960));cv.alpha_composite(g,(p['pos_x']+240,p['pos_y']+240));angle=216 if p['src']=='second.png' else p.get('angle',0);cv=cv.rotate(-angle,Image.Resampling.BICUBIC,center=(480,480));paste(cv.crop((240,240,720,720)),0,0)
   else:paste(g,p['x'],p['y'])
  elif t=='IMG_LEVEL':
   v={'BATTERY':2,'WEATHER_CURRENT':3,'DISTANCE':12,'SLEEP':16,'READINESS':74}[p['type']];paste(img(p['image_array'][v]),p['x'],p['y'])
  elif t=='TEXT_IMG':
   v={'BATTERY':'19','STEP':'10000','HEART':'86','WEATHER_CURRENT':'7','WEATHER_LOW':'4','WEATHER_HIGH':'10','DISTANCE':'3.60','CAL':'471','TRAINING_LOAD':'105'}[p['type']]
   names=[p['font_array'][int(c)] if c.isdigit() else p['dot_image'] for c in v]+([p['unit_en']] if p.get('unit_en') else []);gs=[img(n) for n in names];spacing=p.get('h_space',0);width=sum(g.width for g in gs)+spacing*(len(gs)-1);x=p['x']+(p['w']-width)//2
   if p['align_h']=='LEFT':x=p['x']
   if p['align_h']=='RIGHT':x=p['x']+p['w']-width
   for g in gs:paste(g,x,p['y']);x+=g.width+spacing
  elif t=='TIME_POINTER':
   for n,angle in [('hour',304),('minute',48)]:
    g=img(p[n+'_path']);px=p[n+'_posX'];py=p[n+'_posY'];cv=Image.new('RGBA',(960,960));cv.alpha_composite(g,(480-px,480-py));cv=cv.rotate(-angle,Image.Resampling.BICUBIC,center=(480,480));paste(cv.crop((240,240,720,720)),0,0)
 out.save(R/'dist'/('Graphite-2-v1.1.6-'+('AOD-preview' if aod else 'preview')+'.png'))
