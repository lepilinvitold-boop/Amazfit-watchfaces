"""Rebuild only the two panel footprints; preserve every pixel outside them."""
from pathlib import Path
import math,json,struct
import numpy as np
from PIL import Image,ImageDraw,ImageFont
TIME=(240,110,91,18,False)
DATE=(240,370,92,17,True)
def render_panel(spec,half_extra=0):
 cx,cy,radius,half,upper=spec;S=4;y,x=np.mgrid[:480*S,:480*S];dx=x/S-cx;dy=y/S-cy;sign=-1 if upper else 1
 theta=np.arctan2(dx,sign*dy);near=np.clip(theta,-math.radians(47),math.radians(47))
 ddx=dx-radius*np.sin(near);ddy=dy-sign*radius*np.cos(near);dist=np.hypot(ddx,ddy)
 edge=half+half_extra-dist;valid=edge>=0;light=(-ddx/np.maximum(dist,1)-ddy/np.maximum(dist,1))/1.414
 shade=np.where(edge<.8,32,np.where(edge<2,165+65*light,np.where(edge<3.3,65+35*light,5+2*np.cos(dx/60))))
 ar=np.zeros((480*S,480*S,4),np.uint8);ar[:,:,:3]=np.clip(shade[:,:,None],0,255);ar[:,:,3]=np.where(valid,255,0)
 return Image.fromarray(ar).resize((480,480),Image.Resampling.LANCZOS)
def patch_palette(raw,im,mask):
 # Keep accepted palette and all indices outside the authorised patch byte-for-byte.
 pw,h=struct.unpack_from('<HH',raw,12);aw=struct.unpack_from('<I',raw,22)[0]
 pal=np.frombuffer(raw[64:1088],np.uint8).reshape(256,4).astype(np.int32)
 ids=np.frombuffer(raw[1088:],np.uint8).reshape(h,pw).copy();rgb=np.array(im)[:,:,:3].astype(np.int32);points=rgb[mask]
 palette=pal[:,:3];available=pal[:,3]==255
 result=[]
 for chunk in np.array_split(points,max(1,len(points)//1000)):
  d=((chunk[:,None,:]-palette[None,:,:])**2).sum(2);d[:,~available]=2**30;result.append(d.argmin(1).astype('uint8'))
 ids[:,:aw][mask]=np.concatenate(result)
 return raw[:1088]+ids.tobytes()
def rebuild(P,files,asset,put):
 root=P.parents[1];original=root/'projects/Graphite-Arm-1.0.9/build.py'
 # Exact original carrier/circles, before either old silver window was painted.
 ctx={'__file__':str(original)};exec(original.read_text().split('# Curved silver bezels')[0],ctx)
 clean=ctx['bg'];mask=np.zeros((480,480),bool)
 for spec in [(240,110,87,16,False),(240,370,85,15,True),TIME,DATE]:mask|=np.array(render_panel(spec,2))[:,:,3]>0
 for spec in [TIME,DATE]:clean.alpha_composite(render_panel(spec))
 for pre,factor in [('',1),('aod_',.38)]:
  im=clean.copy()
  if factor!=1:
   a=np.array(im);a[:,:,:3]=(a[:,:,:3]*factor).astype('uint8');im=Image.fromarray(a)
  name='assets/'+pre+'background.png';files[name]=patch_palette(files[name],im,mask)
 Image.fromarray((mask*255).astype('uint8')).save(P/'panel_patch_mask.png')
 for key,spec in [('time',TIME),('date',DATE)]:render_panel(spec).save(P/('panel_'+key+'_mask.png'))
 font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
 def glyph(t,size,width):
  S=4;f=ImageFont.truetype(font,size*S);b=f.getbbox(t);im=Image.new('RGBA',(max(1,b[2]-b[0]),max(1,b[3]-b[1])));ImageDraw.Draw(im).text((-b[0],-b[1]),t,font=f,fill=(235,237,239,255));return im.resize((width,math.ceil(im.height/S)),Image.Resampling.LANCZOS)
 layout={'normal_time':[],'aod_time':[],'date':[]}
 for family,label in [('nt','00:00:00'),('at','00:00')]:
  widths=[21 if c.isdigit() else 8 for c in label];total=sum(widths)+len(label)-1;cursor=-total/2
  for i,(c,width) in enumerate(zip(label,widths)):
   delta=-(cursor+width/2)/91;theta=math.pi+delta;layout['normal_time' if family=='nt' else 'aod_time'].append([round(240+91*math.sin(theta))-24,round(110-91*math.cos(theta))-24])
   for ch in ('0123456789' if c!=':' else ':'):
    g=glyph(ch,31,21 if ch.isdigit() else 8);rr=g.rotate(-math.degrees(delta),Image.Resampling.BICUBIC,expand=True);tile=Image.new('RGBA',(48,48));tile.alpha_composite(rr,((48-rr.width)//2,(48-rr.height)//2));put(f'{family}_{i}_{ord(ch)}',tile)
   cursor+=width+1
 for i in range(9):
  theta=(i-4)*18/92;layout['date'].append([round(240+92*math.sin(theta))-24,round(370-92*math.cos(theta))-24])
  for ch in '0123456789. ПНВТСРЧБК':
   g=Image.new('RGBA',(26,34))
   if ch!=' ':
    letter=glyph(ch,26,6 if ch=='.' else 17);g.alpha_composite(letter,((26-letter.width)//2,24 if ch=='.' else (34-letter.height)//2))
   rr=g.rotate(-math.degrees(theta),Image.Resampling.BICUBIC,expand=True);tile=Image.new('RGBA',(48,48));tile.alpha_composite(rr,((48-rr.width)//2,(48-rr.height)//2));put(f'dt_{i}_{ord(ch)}',tile)
 (P/'layout.json').write_text(json.dumps(layout));return layout
