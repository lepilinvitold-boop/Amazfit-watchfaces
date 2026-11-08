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

def put(name, image):
    files[f'assets/{name}.png'] = encode(image)

def dim(image):
    faded = ImageEnhance.Brightness(image).enhance(.38)
    faded.putalpha(image.getchannel('A'))
    return faded

def font(size):
    return ImageFont.truetype('DejaVuSans-Bold.ttf', size)

# The approved metal artwork is cropped to the outer bezel and sampled at device size.
background = Image.open(root/'dial-art.png').convert('RGBA')
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
for x,y,label,size in [(135,141,'72',23),(350,141,'83%',23),(135,324,'540',23),(347,324,'28',23),
                       (240,112,'−10°',22),(240,146,'−18° / −12°',15),(122,228,'12.12',23),
                       (122,260,'ПТН',19),(361,228,'10:09:42',23),(361,260,'—:—',16),
                       (240,356,'1196',23),(240,389,'0,50 км',17)]:
    d.text((x,y),label,font=font(size),fill='#ebedf0',anchor='mm')
preview.alpha_composite(decode(files['assets/weather_4.png']),(221,65))
for index,py,px,angle in [(64,250,37,304.85),(65,247,37,58.2),(66,248,36,252)]:
    hand=Image.new('RGBA',(960,960))
    hand.alpha_composite(decode(files[f'assets/{index:04}.png']),(480-px,480-py))
    preview.alpha_composite(hand.rotate(-angle,resample=Image.Resampling.BICUBIC).crop((240,240,720,720)))
preview.save(out/'preview.png', optimize=True)
put('preview',preview.resize((240,240),Image.Resampling.LANCZOS))
manifest=json.loads((root/'platform.json').read_text())
manifest['app'].update(appId=10625861,appName='Heiyan RU',version={'code':2,'name':'1.1.0'},
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
