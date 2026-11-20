from pathlib import Path
from PIL import Image
import zipfile,io,json
root=Path(__file__).resolve().parent
src=root/'dist/Amber-Graphite-1.0.23-Balance2.zpk'
dst=root/'dist/Amber-Graphite-1.0.25-Balance2.zpk'
with zipfile.ZipFile(src) as z:
 with zipfile.ZipFile(io.BytesIO(z.read('device.zip'))) as d: files={n:d.read(n) for n in d.namelist()}
manifest=json.loads(files['app.json']);manifest['app']['version']={'name':'1.0.25','code':15};manifest['app']['description']='Amber Graphite: объёмный безель и исправленные тапы';manifest['packageInfo']['timeStamp']+=1
files['watchface/index.js']=(root/'watchface-stage25.js').read_bytes()
files['assets/dial.png']=(root/'assets/redesigned_dial.png').read_bytes()
files['assets/aod.png']=(root/'assets/redesigned_aod.png').read_bytes()
for n in ['handset_icon','aod_handset_icon','training_icon','aod_training_icon','battery_new','aod_battery_new','steps_icon','aod_steps_icon','weather_3','aod_weather_3']:
 files['assets/'+n+'.png']=(root/'assets'/f'{n}.png').read_bytes()
files['app.json']=json.dumps(manifest,ensure_ascii=False).encode()
side=io.BytesIO()
with zipfile.ZipFile(side,'w',zipfile.ZIP_DEFLATED) as z:z.writestr('app.json',files['app.json'])
def write():
 dev=io.BytesIO()
 with zipfile.ZipFile(dev,'w',zipfile.ZIP_DEFLATED) as z:
  for n,v in files.items():z.writestr(n,v)
 with zipfile.ZipFile(dst,'w',zipfile.ZIP_DEFLATED) as z:z.writestr('device.zip',dev.getvalue());z.writestr('app-side.zip',side.getvalue())
preview=root/'qa/stage25-sun.png'
if preview.exists():
    out=io.BytesIO();Image.open(preview).resize((240,240),Image.Resampling.LANCZOS).save(out,format='PNG');files['assets/preview.png']=out.getvalue()
write()
