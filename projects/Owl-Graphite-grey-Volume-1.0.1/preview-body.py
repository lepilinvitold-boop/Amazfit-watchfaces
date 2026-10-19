def paste(n,x,y,scale=False):
 a=asset(n)
 im.alpha_composite(a,(x,y))
for n,x,y in [('graph_ring_15',295,171),('heart_ring_12',171,46),('stress_ring_14',47,171),('calorie_ring_10',47,171)]:paste(n,x,y,True)
for n,x,y in [('phone_icon',103,335),('workout_icon',103,103),('alarm_icon',336,336),('weather_3',186,300)]:paste(n,x,y)
def digits(t,font,x,y,width=None):
 imgs=[asset(font+'_'+c) if c.isdigit() else asset('range_sep' if c=='–' else 'dot') for c in t];total=sum(a.width for a in imgs);x=round(x+(width-total)/2) if width else x
 for a in imgs:im.alpha_composite(a,(x,y));x+=a.width
for t,f,x,y,w in [('271','detail',70,262,92),('7650','circle',314,211,100),('5.84','detail',318,262,92),('77','battery',331,117,50),('22','circle',216,303,70),('10','time',178,350,None),('08','time',246,350,None),('19','date',188,404,None),('48–133','range',191,119,98),('89','circle',202,82,76),('73','small',70,210,92)]:digits(t,f,x,y,w)
paste('colon',234,350);paste('week_0',230,404);paste('graph_degree',278,303)
def hand(n,px,py,angle):
 a=asset(n);canvas=Image.new('RGBA',(960,960));canvas.alpha_composite(a,(480-px,480-py));canvas=canvas.rotate(-angle,resample=Image.Resampling.BICUBIC,center=(480,480));im.alpha_composite(canvas.crop((240,240,720,720)))
hand('hour',21,156,304);hand('minute',19,192,48);hand('second',6,222,210);paste('cap',227,227)
im.save(D/(B+'-preview.png'))
