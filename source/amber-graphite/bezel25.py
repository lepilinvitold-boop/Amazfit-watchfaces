import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

CX = CY = 240.0
SIZE = 480
S = 4

def rebuild(base):
    src = np.asarray(base.convert('RGBA'), dtype=np.float32)
    yy, xx = np.mgrid[:SIZE, :SIZE]
    r = np.hypot(xx - CX, yy - CY)
    a = np.arctan2(yy - CY, xx - CX)

    # A single radial profile defines every circular surface. The gently
    # directional reflection gives the metal depth without moving its edge.
    neutral = np.median(src[:, :, :3], axis=(0, 1))
    radii = np.arange(183, 241)
    samples = []
    for radius in radii:
        selection = (abs(r - radius) < .55)
        values = src[:, :, :3][selection]
        gray = values.max(axis=1) - values.min(axis=1) < 18
        values = values[gray]
        samples.append(float(np.median(values)) if len(values) else 18.)
    from scipy.ndimage import gaussian_filter1d
    profile = gaussian_filter1d(np.array(samples), 2.0)
    tone = np.interp(r, radii, profile)
    # Highlights share the same center and radius at every angle.
    tone += 12 * np.exp(-((r - 188.5) / 1.25) ** 2)
    tone += 7 * np.exp(-((r - 205.5) / 2.3) ** 2)
    tone += 12 * np.exp(-((r - 228.5) / 3.6) ** 2)
    tone -= 12 * np.exp(-((r - 195.5) / 3.6) ** 2)
    tone -= 8 * np.exp(-((r - 215) / 5.4) ** 2)
    tone += 4.5 * np.cos(a + 2.2)
    tone = np.clip(tone, 5, 72)
    # Feathered outer boundary avoids a pasted-on edge.
    blend = np.clip((r - 183.5) / 2, 0, 1) * np.clip((239.5 - r) / 2, 0, 1)
    rgb = np.stack([tone, tone + 1, tone + 1], axis=2)
    src[:, :, :3] = src[:, :, :3] * (1-blend[:, :, None]) + rgb * blend[:, :, None]
    out = Image.fromarray(src.astype('uint8'), 'RGBA')

    layer = Image.new('RGBA', (SIZE*S, SIZE*S))
    d = ImageDraw.Draw(layer)
    def point(rad, angle):
        return (round((CX + rad*math.cos(angle))*S), round((CY + rad*math.sin(angle))*S))
    def ring(rad, color, width):
        bbox = tuple(round(v*S) for v in (CX-rad,CY-rad,CX+rad,CY+rad))
        d.ellipse(bbox, outline=color, width=round(width*S))
    # Concentric machined edges, with no independent elliptical artwork.
    ring(188.0, (117, 119, 115, 240), .75)
    ring(190.3, (10, 12, 13, 255), 1.4)
    ring(207.5, (68, 72, 71, 225), .6)
    ring(210, (10, 12, 13, 245), 1.1)
    ring(233.0, (82, 84, 81, 190), .8)
    ring(236.7, (19, 21, 22, 240), 1.2)
    ring(239.0, (75, 77, 75, 155), .65)

    for minute in range(60):
        angle = math.radians(6*minute-90)
        if minute % 5:
            d.line([point(193,angle),point(201,angle)],fill=(100,103,101,230),width=round(.85*S))
        elif minute % 15:
            # 5, 10, 20, 25, 35, 40, 50, 55: continuous metal strips
            # with a narrower amber surface, all at identical radii.
            d.line([point(210,angle),point(235,angle)],fill=(11,12,13,255),width=round(11*S))
            d.line([point(211,angle),point(233,angle)],fill=(75,78,79,255),width=round(8.5*S))
            d.line([point(212,angle),point(232,angle)],fill=(171,174,171,255),width=round(4.3*S))
            d.line([point(215,angle),point(230,angle)],fill=(223,154,42,255),width=round(2.4*S))
            d.line([point(216,angle),point(226,angle)],fill=(255,192,72,255),width=round(1.0*S))
        else:
            # 12, 3, 6 and 9 keep their broad golden orientation marks.
            d.line([point(215,angle),point(235,angle)],fill=(87,56,16,255),width=round(12*S))
            d.line([point(216,angle),point(232,angle)],fill=(236,171,47,255),width=round(8*S))
    out.alpha_composite(layer.resize((SIZE,SIZE),Image.Resampling.LANCZOS))
    # The numeral 12 is part of the original design. Preserve only its gold
    # pixels, so old circular artwork cannot reappear behind the new ring.
    original=np.asarray(base.convert('RGBA'))
    region=(xx>206)&(xx<274)&(yy>18)&(yy<64)
    gold=(original[:,:,0]>75)&(original[:,:,0]>original[:,:,2]*1.30)&(original[:,:,1]>original[:,:,2]*1.17)
    mask=Image.fromarray(np.uint8(region&gold)*255,'L')
    out.paste(base,(0,0),mask)
    return out
