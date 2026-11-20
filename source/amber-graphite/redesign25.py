from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import math

ROOT = Path(__file__).resolve().parent
base = Image.open(ROOT / 'assets/background.png').convert('RGBA')
w = h = 480
from bezel25 import rebuild
base=rebuild(base)
# Replace the three old misaligned panels inside the newly circular lip.
Y,X=np.mgrid[:480,:480]
R=np.hypot(X-239.5,Y-239.5)
clear=Image.new('L',(w,h));cd=ImageDraw.Draw(clear)
cd.polygon([(46,180),(163,180),(187,205),(187,265),(162,291),(46,291)],fill=255)
cd.polygon([(434,180),(317,180),(293,205),(293,265),(318,291),(434,291)],fill=255)
cd.polygon([(125,121),(355,121),(355,143),(323,203),(157,203),(125,143)],fill=255)
area=np.array(clear)>0
area &= R<185.5
arr=np.asarray(base).copy()
tone=np.clip(10+5*np.abs(X-240)/240+3*np.abs(Y-240)/240,7,20).astype('uint8')
for c in range(3):arr[:,:,c]=np.where(area,tone+c,arr[:,:,c])
base=Image.fromarray(arr,'RGBA')
# The original lower digital aperture is beneath the three custom panels.
fade=Image.new('L',(w,h));ImageDraw.Draw(fade).rounded_rectangle((107,289,373,378),radius=17,fill=255)
fade=fade.filter(ImageFilter.GaussianBlur(6))
dark=Image.fromarray(np.dstack([tone,tone+1,tone+2,np.full((h,w),255,dtype='uint8')]),'RGBA')
base.paste(dark,(0,0),fade)

S=4
overlay=Image.new('RGBA',(w*S,h*S));draw=ImageDraw.Draw(overlay)
def rounded(rect,radius,fill,outline=None,width=1):
    draw.rounded_rectangle(tuple(round(v*S) for v in rect),radius=radius*S,fill=fill,
                           outline=outline,width=width*S)
def line(points,fill,width=1):
    draw.line([(round(x*S),round(y*S)) for x,y in points],fill=fill,width=width*S)
# Fully closed bevels drawn in one pass. All outer points are inside r=184;
# the rebuilt bezel begins at r=188, leaving a visible graphite gap.
def panel(points):
    def path(inset):
        x0,y0,x1,y1=87,240,393,240
        cx=sum(x for x,y in points)/len(points)
        cy=sum(y for x,y in points)/len(points)
        return [(round((x+(cx-x)*inset)*S),round((y+(cy-y)*inset)*S)) for x,y in points]
    outer=path(0)
    draw.polygon(outer,fill=(6,8,9,255))
    for inset,color,width in [(0,(22,24,25,255),2.7),(.022,(126,128,121,255),1.2),(.043,(50,54,52,255),1.0)]:
        p=path(inset)
        draw.line(p+[p[0]],fill=color,width=round(width*S),joint='curve')
step_points=[(137,122),(343,122),(349,135),(321,184),(308,196),(172,196),(159,184),(131,135)]
left_points=[(78,184),(154,184),(177,208),(177,258),(153,282),(78,282),(57,259),(57,207)]
panel(step_points)
panel(left_points)
panel([(480-x,y) for x,y in left_points])
def frame(rect,radius=12):
    rounded(rect,radius,(6,8,9,250),(29,31,32,255),2)
    x0,y0,x1,y1=rect
    rounded((x0+2,y0+2,x1-2,y1-2),max(1,radius-2),None,(103,105,100,235),1)
    rounded((x0+4,y0+4,x1-4,y1-4),max(1,radius-4),None,(45,47,46,240),1)
frame((175,297,305,366),12)
# Inner sides remain straight; the two outer sides are true concentric arcs
# 12 px inside the dial ring. The matching lower corners are softly cut.
def curved_side_frame(right=False):
    from math import sqrt
    def path(inset):
        radius=185-inset
        def edge(y):return 239.5-sqrt(radius**2-(y-239.5)**2)
        top=298+inset; bottom=365-inset; inner=165-inset
        pts=[(edge(top),top),(inner-7,top),(inner,top+7),
             (inner,bottom-7),(inner-7,bottom),(edge(bottom)+6,bottom)]
        pts += [(edge(y),y) for y in np.linspace(bottom-4,top,96)]
        if right:pts=[(480-x,y) for x,y in pts]
        return [(round(x*S),round(y*S)) for x,y in pts]
    draw.polygon(path(0),fill=(7,9,10,255))
    for inset,color,width in [(0,(25,28,29,255),2),(2,(99,103,98,255),1),
                              (4,(43,47,45,255),1)]:
        pts=path(inset);draw.line(pts+pts[:1],fill=color,width=width*S,joint='curve')
curved_side_frame()
curved_side_frame(True)
for x in (106,374):
    draw.ellipse(((x-21)*S, (153-21)*S, (x+21)*S,(153+21)*S),
                 fill=(10,12,13,255),outline=(115,116,108,255),width=2*S)
    draw.ellipse(((x-17)*S, (153-17)*S, (x+17)*S,(153+17)*S),
                 outline=(46,49,47,255),width=S)
for a,b,y in [(72,161,247),(171,309,172),(316,409,247)]:
    line([(a,y),(b,y)],(88,82,69,255),1)
    line([(a+2,y+1),(b-2,y+1)],(17,18,18,255),1)
# The lower bezels sit above the plate and cast a shallow, diffuse shadow.
shadow=Image.new('RGBA',(w*S,h*S))
sh=ImageDraw.Draw(shadow)
sh.rounded_rectangle((173*S,299*S,307*S,370*S),radius=14*S,fill=(0,0,0,170))
for right in (False,True):
    from math import sqrt
    pts=[]
    for yy in np.linspace(298,365,72):
        x=239.5-sqrt(185**2-(yy-239.5)**2)
        pts.append((x,yy))
    pts.extend([(165,365),(165,298)])
    if right:pts=[(480-x,y) for x,y in pts]
    sh.polygon([(round(x*S),round(y*S)) for x,y in pts],fill=(0,0,0,175))
shadow=shadow.resize((w,h),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(5))
base.alpha_composite(shadow)
base.alpha_composite(overlay.resize((w,h),Image.Resampling.LANCZOS))
# Eight five-minute indices repeat the saturated gold of the outer cardinal markers.
mark=Image.new('RGBA',(w*S,h*S)); md=ImageDraw.Draw(mark)
import math
for minute in (5,10,20,25,35,40,50,55):
    a=math.radians(minute*6-90)
    ux,uy=math.cos(a),math.sin(a); tx,ty=-uy,ux
    def corners(radius, half):
        return [(round((239.5+radius*ux+half*tx)*S),round((239.5+radius*uy+half*ty)*S)),
                (round((239.5+radius*ux-half*tx)*S),round((239.5+radius*uy-half*ty)*S))]
    outer=corners(226,3.0); mid=corners(211,1.65)
    md.polygon([outer[0],outer[1],mid[1],mid[0]],fill=(184,117,29,255))
    a2=corners(223,1.45); b2=corners(212,0.9)
    md.polygon([a2[0],a2[1],b2[1],b2[0]],fill=(242,180,62,255))
base.alpha_composite(mark.resize((w,h),Image.Resampling.LANCZOS))
base.save(ROOT/'assets/redesigned_dial.png')
dim=Image.new('RGBA',(w,h),'black')
from PIL import ImageEnhance
dim.alpha_composite(ImageEnhance.Brightness(base).enhance(.25))
dim.save(ROOT/'assets/redesigned_aod.png')

def save_icon(name,image):
    if name in ('steps_icon','handset_icon','training_icon','battery_new'):
        image=image.filter(ImageFilter.UnsharpMask(radius=.7,percent=145,threshold=2))
    image.save(ROOT/'assets'/f'{name}.png')

# Small, legible indicators made for the actual panel size.
# A walking figure is unambiguous at 30 pixels, unlike tiny toe marks.
step=Image.new('RGBA',(30*S,30*S));d=ImageDraw.Draw(step)
gold='#e9d4a1';edge='#654e30'
d.ellipse((12*S,2*S,19*S,9*S),fill=gold)
d.line((15*S,10*S,15*S,19*S),fill=gold,width=3*S)
d.line((15*S,12*S,7*S,17*S),fill=gold,width=3*S)
d.line((15*S,13*S,23*S,16*S),fill=gold,width=3*S)
d.line((15*S,18*S,8*S,27*S),fill=gold,width=3*S)
d.line((15*S,18*S,23*S,27*S),fill=gold,width=3*S)
d.line((7*S,27*S,11*S,27*S),fill=edge,width=S)
d.line((22*S,27*S,26*S,27*S),fill=edge,width=S)
save_icon('steps_icon',step.resize((30,30),Image.Resampling.LANCZOS))
heart=Image.new('RGBA',(26*S,26*S));d=ImageDraw.Draw(heart)
d.ellipse((2*S,3*S,14*S,15*S),fill='#e34e4a')
d.ellipse((12*S,3*S,24*S,15*S),fill='#e34e4a')
d.polygon([(2*S,10*S),(24*S,10*S),(13*S,24*S)],fill='#e34e4a')
save_icon('heart_icon',heart.resize((26,26),Image.Resampling.LANCZOS))
# Matching gold line icons, drawn at fourfold resolution for crisp edges.
def icon(name,paint):
    canvas=Image.new('RGBA',(34*S,34*S)); d=ImageDraw.Draw(canvas)
    paint(d)
    save_icon(name,canvas.resize((34,34),Image.Resampling.LANCZOS))
GOLD='#e9d4a1'; DARK='#4e4029'
def handset(d):
    # Diagonal receiver: two wide earpieces joined by a curved handle.
    d.polygon([(4*S,7*S),(9*S,3*S),(16*S,9*S),(12*S,14*S),
               (20*S,22*S),(25*S,18*S),(32*S,25*S),(28*S,31*S),
               (22*S,32*S),(12*S,25*S),(6*S,19*S),(2*S,12*S)],fill=GOLD)
    d.polygon([(7*S,8*S),(10*S,6*S),(13*S,9*S),(10*S,12*S)],fill=DARK)
    d.polygon([(25*S,23*S),(28*S,26*S),(26*S,29*S),(22*S,26*S)],fill=DARK)
    d.line((11*S,15*S,20*S,24*S),fill=DARK,width=S)
icon('handset_icon',handset)
save_icon('handset_icon',Image.open(ROOT/'assets/handset_icon.png').resize((30,30),Image.Resampling.LANCZOS))
def dumbbell(d):
    d.line((6*S,17*S,28*S,17*S),fill=DARK,width=6*S)
    d.line((6*S,16*S,28*S,16*S),fill=GOLD,width=3*S)
    for x in (4,26):
        d.rounded_rectangle((x*S,9*S,(x+5)*S,25*S),radius=S,fill=DARK,outline=GOLD,width=2*S)
        d.line(((x+1)*S,11*S,(x+1)*S,23*S),fill='#fff0be',width=S)
    for x in (1,31):d.rounded_rectangle((x*S,13*S,(x+2)*S,21*S),radius=S,fill=GOLD)
canvas=Image.new('RGBA',(34*S,34*S));d=ImageDraw.Draw(canvas);dumbbell(d)
canvas=canvas.rotate(32,Image.Resampling.BICUBIC,expand=False)
save_icon('training_icon',canvas.resize((30,30),Image.Resampling.LANCZOS))
def battery(d):
    d.rounded_rectangle((2*S,6*S,29*S,28*S),radius=3*S,fill=DARK,outline=GOLD,width=2*S)
    d.rounded_rectangle((29*S,12*S,33*S,22*S),radius=S,fill=GOLD)
    
    for x in (7,13,19):d.rounded_rectangle((x*S,11*S,(x+4)*S,23*S),radius=S,fill=GOLD)
icon('battery_new',battery)

sun=Image.new('RGBA',(48*S,33*S));sd=ImageDraw.Draw(sun)
import math
for degree in range(0,360,45):
    a=math.radians(degree)
    x0,y0=24+12*math.cos(a),16+12*math.sin(a)
    x1,y1=24+15*math.cos(a),16+15*math.sin(a)
    sd.line((round(x0*S),round(y0*S),round(x1*S),round(y1*S)),fill='#e7c46f',width=2*S)
sd.ellipse((15*S,7*S,33*S,25*S),fill='#9e6d23',outline='#f1d68a',width=2*S)
sd.ellipse((17*S,9*S,30*S,22*S),fill='#dbac4e')
sd.arc((18*S,9*S,30*S,21*S),195,300,fill='#fff0bb',width=2*S)
save_icon('weather_3',sun.resize((48,33),Image.Resampling.LANCZOS))
save_icon('aod_weather_3',ImageEnhance.Brightness(sun.resize((48,33),Image.Resampling.LANCZOS)).enhance(.35))
for name in ('steps_icon','heart_icon','handset_icon','training_icon','battery_new'):
    image=Image.open(ROOT/'assets'/f'{name}.png')
    save_icon('aod_'+name,ImageEnhance.Brightness(image).enhance(.40))

for name in ('battery_icon','aod_battery_icon'):
    icon=Image.open(ROOT/'assets'/f'{name}.png').convert('RGBA')
    icon.resize((38,36),Image.Resampling.LANCZOS).save(ROOT/'assets'/f'redesigned_{name}.png')
