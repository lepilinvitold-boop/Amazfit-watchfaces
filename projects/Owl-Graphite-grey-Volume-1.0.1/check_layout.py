from pathlib import Path
import io,zipfile,re,json
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;ROOT=P.parents[1];D=ROOT/'dist'
s=(P.parent/'Owl-Graphite-Color-1.0.9/build.py').read_text();ns={'__file__':str(P.parent/'Owl-Graphite-Color-1.0.9/build.py')};exec(s[:s.index('with zipfile.ZipFile')],ns);decode=ns['decode']
def unpack(path):
 with zipfile.ZipFile(path) as z:
  with zipfile.ZipFile(io.BytesIO(z.read('device.zip'))) as d:return {n:d.read(n) for n in d.namelist()}
new=unpack(D/'Owl-Graphite-grey-Volume-v1.0.1-RU-Balance2.zpk')
import hashlib
fonts=json.loads((P/'font-sha256.json').read_text())
assert fonts and all(hashlib.sha256(new[n]).hexdigest()==digest for n,digest in fonts.items())
assert json.loads(new['app.json'])['app']['appId']==10622121

def mask_asset(n):return np.array(decode(new['assets/'+n+'.png']))[:,:,3]>100

def text_mask(text,font,x,y,width=None,step=None):
 arrays=[mask_asset(font+'_'+c if c.isdigit() else 'range_sep' if c=='–' else 'dot') for c in text]
 total=sum(a.shape[1] for a in arrays) if step is None else (len(arrays)-1)*step+arrays[-1].shape[1]
 x=round(x+(width-total)/2) if width is not None else x
 canvas=np.zeros((480,480),bool)
 for a in arrays:
  h,w=a.shape;canvas[y:y+h,x:x+w]|=a;x+=w if step is None else step
 return canvas

def track(name,x,y):
 all_frames=np.logical_or.reduce([mask_asset(name+'_ring_'+str(i)) for i in range(21)])
 out=np.zeros((480,480),bool);h,w=all_frames.shape;out[y:y+h,x:x+w]=all_frames;return out
tracks={'heart':track('heart',171,46),'left':track('stress',47,171)|track('calorie',47,171),'right':track('graph',295,171)}
for name,t,f,x,y,w in [('heart','255','circle',202,82,76),('left','100','small',70,210,92),('left','9999','detail',70,262,92),('right','99999','circle',314,211,100),('right','99.99','detail',318,262,92)]:
 collision=(text_mask(t,f,x,y,w)&tracks[name]).sum();assert collision==0,(name,t,int(collision))
for text in ['255–255','100–199','48–133']:
 x=240-len(text)*7;m=text_mask(text,'range',x,119,step=14);assert not np.any(m&tracks['heart']),text
# 100% battery: unchanged glyphs stay inside its recessed face radius 30.
b=text_mask('100','battery',331,117,50);yy,xx=np.mgrid[:480,:480];assert not np.any(b&(np.hypot(xx-356+.5,yy-124+.5)>=30))
# Static labels do not intersect active progress tracks.
bg=np.array(decode(new['assets/background.png']));bright=(bg[:,:,:3].max(2)>170)&(bg[:,:,3]>100)
for name,(x1,y1,x2,y2) in {'heart':(195,60,285,145),'left':(65,190,168,270),'right':(313,190,416,270)}.items():
 region=np.zeros((480,480),bool);region[y1:y2,x1:x2]=True
 # Restrict to inner face (exclude the metal rim), where static labels live.
 cx,cy={'heart':(240,115),'left':(116,240),'right':(364,240)}[name];region&=np.hypot(xx-cx+.5,yy-cy+.5)<65
 assert not np.any(bright&region&tracks[name]),name
print('PASS:',len(fonts),'font resources byte-identical; 100% battery, five-digit steps, 9999 calories, 99.99 distance and seven-character pulse range clear of scales.')
