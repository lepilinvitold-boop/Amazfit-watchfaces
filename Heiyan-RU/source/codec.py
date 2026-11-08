from pathlib import Path
import io,json,math,struct,zipfile
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from reportlab.graphics.barcode.qr import QrCodeWidget
P=Path(__file__).resolve().parent; ROOT=P.parents[1];D=ROOT/'dist'; B='Owl-Graphite-Color-v1.0.9'; S=4
def decode(b):
 w,h=struct.unpack_from('<HH',b,12);aw=struct.unpack_from('<I',b,22)[0];pal=np.frombuffer(b[64:1088],np.uint8).reshape(256,4);a=pal[np.frombuffer(b[1088:],np.uint8).reshape(h,w)][:,:aw].copy();al=a[:,:,3:4].astype(float);a[:,:,:3]=np.clip(np.divide(a[:,:,:3].astype(float)*255,al,out=np.zeros_like(a[:,:,:3],dtype=float),where=al>0),0,255).astype('uint8');return Image.fromarray(a)
def encode(im):
 im=im.convert('RGBA');w,h=im.size;pw=(w+15)//16*16;tmp=Image.new('RGBA',(pw,h));tmp.alpha_composite(im);q=tmp.quantize(colors=256,method=Image.Quantize.FASTOCTREE);pal=np.zeros((256,4),np.uint8);e=np.frombuffer(q.palette.palette,np.uint8).reshape(-1,4);pal[:len(e)]=e;pal[:,:3]=np.rint(pal[:,:3].astype(float)*pal[:,3:4]/255).astype('uint8');head=bytearray(64);head[:18]=bytes.fromhex('2e0101000000012000000000000000000820');struct.pack_into('<HH',head,12,pw,h);head[18:22]=b'SOMH';struct.pack_into('<I',head,22,w);return bytes(head)+pal.tobytes()+np.array(q).tobytes()
