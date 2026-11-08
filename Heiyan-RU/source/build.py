from pathlib import Path
import io
import json
import sys
import time
import zipfile

from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from codec import decode, encode

root = Path(__file__).resolve().parent
out = root.parent
with zipfile.ZipFile(sys.argv[1]) as original:
    files = {f'assets/{i:04}.png': original.read(f'assets/{i:04}.png')
             for i in [*range(3, 32), 64, 65, 66, 68]}
    background = decode(original.read('assets/0001.png'))

def put(name, image):
    files[f'assets/{name}.png'] = encode(image)

def dim(image):
    faded = ImageEnhance.Brightness(image).enhance(.38)
    faded.putalpha(image.getchannel('A'))
    return faded

def font(size):
    return ImageFont.truetype('DejaVuSans-Bold.ttf', size)

S = 3
canvas = background.resize((480*S, 480*S), Image.Resampling.BICUBIC)
draw = ImageDraw.Draw(canvas)
def ellipse(x, y, r, fill):
    draw.ellipse(tuple(int(v*S) for v in (x-r,y-r,x+r,y+r)), fill=fill)

def panel(points, center):
    cx,cy = center
    for scale,color in [(1,'#08090b'),(.97,'#6b7077'),(.90,'#34383e'),
                        (.83,'#1d2025'),(.79,'#101115')]:
        draw.polygon([(round((cx+(x-cx)*scale)*S),round((cy+(y-cy)*scale)*S))
                      for x,y in points], fill=color)

for y in (116,364):
    for r,dy,c in [(75,0,'#08090b'),(73,-1,'#62676e'),(70,0,'#333840'),
                   (66,1,'#191c21'),(62,0,'#101115')]:
        ellipse(240,y+dy,r,c)
    draw.line((194*S,(y+14)*S,286*S,(y+14)*S), fill='#32757c', width=S)
left = [(45,201),(128,179),(205,216),(205,264),(136,299),(47,280)]
for pts,cx in [(left,124), ([(480-x,y) for x,y in left],356)]:
    panel(pts,(cx,240))
for cx in (130,350):
    for cy in (111,334):
        panel([(cx-37,cy-15),(cx+37,cy-15),(cx+33,cy+16),(cx-33,cy+16)],(cx,cy))
for r,color in [(50,'#202328'),(36,'#111216'),(20,'#33383f'),(16,'#181a1e')]:
    ellipse(240,240,r,color)
# Remove the old lower icons before drawing the new positions.
for cx,mark,cy in [(139,'♥',83),(341,'▣',83),(139,'♨',366),(341,'≋',366)]:
    if cy==366:
        ellipse(cx,cy,18,'#282b31')
    if mark == '▣':
        draw.rounded_rectangle((331*S,78*S,349*S,88*S),radius=2*S,outline='#e8e9eb',width=2*S)
        draw.rectangle((350*S,81*S,352*S,85*S),fill='#e8e9eb')
        draw.rectangle((334*S,81*S,346*S,85*S),fill='#e8e9eb')
    elif mark == '♨':
        draw.polygon([(x*S,y*S) for x,y in [(138,354),(144,362),(147,368),(144,374),(136,374),(132,369),(133,364),(137,366)]],fill='#e8e9eb')
        ellipse(140,370,2,'#282b31')
    else:
        draw.text((cx*S,cy*S),mark,font=font(19*S),anchor='mm',fill='#e8e9eb')
for x,y in [(234,320),(246,316)]:
    draw.ellipse(((x-3)*S,(y-5)*S,(x+3)*S,(y+4)*S),fill='#e8e9eb')
    ellipse(x,y+7,2,'#e8e9eb')
background = canvas.resize((480,480),Image.Resampling.LANCZOS)
put('dial',background)
put('aod',dim(background))
put('hit',Image.new('RGBA',(1,1)))
km = Image.new('RGBA',(26,18))
ImageDraw.Draw(km).text((13,9),' км',font=font(13),anchor='mm',fill='#ebedf0')
put('km',km)
put('aod_km',dim(km))
for name, size, symbols in [('value',23,'0123456789%'),('small',15,'0123456789°−,.'),
                            ('current',23,'0123456789°−')]:
    for char in symbols:
        f=font(size*3)
        width=round(f.getlength(char)/3)
        glyph=Image.new('RGBA',(width*3,(size+3)*3))
        ImageDraw.Draw(glyph).text((width*1.5,(size+3)*1.5),char,font=f,
                                   fill='#ebedf0',anchor='mm')
        glyph = glyph.resize((width,size+3),Image.Resampling.LANCZOS)
        put(f'{name}_{ord(char)}',glyph)
        put(f'aod_{name}_{ord(char)}',dim(glyph))
for i in range(3,32):
    icon=decode(files[f'assets/{i:04}.png'])
    icon.thumbnail((38,35),Image.Resampling.LANCZOS)
    tile=Image.new('RGBA',(38,35))
    tile.alpha_composite(icon,((38-icon.width)//2,(35-icon.height)//2))
    put(f'weather_{i-3}',tile)
    put(f'aod_weather_{i-3}',dim(tile))
    del files[f'assets/{i:04}.png']

for i in (64,65):
    put(f'aod_{i}',dim(decode(files[f'assets/{i:04}.png'])))

preview = background.copy()
d = ImageDraw.Draw(preview)
for x,y,label,size in [(130,111,'72',23),(350,111,'83%',23),(130,334,'540',23),(350,334,'28',23),
                       (240,112,'−10°',22),(240,146,'−18° / −12°',15),(123,229,'12.12',25),
                       (123,257,'ПТН',19),(354,229,'10:09:42',23),(354,257,'—:—',16),
                       (240,354,'1196',23),(240,396,'0,50 км',17)]:
    d.text((x,y),label,font=font(size),fill='#ebedf0',anchor='mm')
preview.alpha_composite(decode(files['assets/weather_4.png']),(221,65))
for index,py,px,angle in [(64,250,37,304.85),(65,247,37,58.2),(66,248,36,252)]:
    hand=Image.new('RGBA',(960,960))
    hand.alpha_composite(decode(files[f'assets/{index:04}.png']),(480-px,480-py))
    preview.alpha_composite(hand.rotate(-angle,resample=Image.Resampling.BICUBIC).crop((240,240,720,720)))
preview.save(out/'preview.png')
put('preview',preview.resize((240,240),Image.Resampling.LANCZOS))
manifest=json.loads((root/'platform.json').read_text())
manifest['app'].update(appId=10625861,appName='Heiyan RU',version={'code':1,'name':'1.0.0'},
                       description='Русский циферблат Heiyan для Balance 2')
manifest['i18n']={'en-US':{'appName':'Heiyan RU'},'ru-RU':{'appName':'Heiyan RU'}}
manifest['packageInfo']['timeStamp']=int(time.time())
meta=json.dumps(manifest,ensure_ascii=False).encode()
files.update({'app.json':meta,'app.js':(root/'app.js').read_bytes(),
              'watchface/index.js':(root/'watchface.js').read_bytes()})

def archive(items):
    stream=io.BytesIO()
    with zipfile.ZipFile(stream,'w',zipfile.ZIP_DEFLATED) as package:
        for name,value in items.items():
            package.writestr(name,value)
    return stream.getvalue()

(out/'Heiyan-RU-Balance2.zpk').write_bytes(archive({'device.zip':archive(files),
                                                   'app-side.zip':archive({'app.json':meta})}))
