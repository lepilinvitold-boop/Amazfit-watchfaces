try { (()=>{
const app=__$$hmAppManager$$__.currentApp,mod=app.current;
const font=n=>Array.from({length:10},(_,i)=>n+'_'+i+'.png');
const taps=[['battery',190,62,100,100,'Settings_batteryManagerScreen'],['weather',190,288,100,113,'WeatherScreen'],['heart',310,190,100,100,'heart_app_Screen'],['steps',70,190,100,100,'activityAppScreen'],['date',174,405,132,24,'ScheduleCalScreen'],['hours',181,180,54,32,'StopWatchScreen'],['minutes',245,180,54,32,'CountdownAppScreen']];
mod.module=DeviceRuntimeCore.WatchFace({
 init_view(){
  if(this._built)return;this._built=true;
  const normal=hmUI.show_level.ONLY_NORMAL,aod=hmUI.show_level.ONAL_AOD;
  const dim=v=>typeof v==='string'&&v.endsWith('.png')?'aod_'+v:Array.isArray(v)?v.map(dim):v;
  const create=(type,p)=>{
   const w=hmUI.createWidget(type,{...p,enable:false,show_level:normal});
   const ap={...p,enable:false,show_level:aod};Object.keys(p).forEach(k=>ap[k]=dim(p[k]));
   if(type===hmUI.widget.TIME_POINTER)Object.keys(ap).filter(k=>k.startsWith('second_')).forEach(k=>delete ap[k]);
   const aw=hmUI.createWidget(type,ap);
   return {setProperty(k,v){w.setProperty(k,v);aw.setProperty(k,k===hmUI.prop.SRC?dim(v):k===hmUI.prop.MORE?Object.fromEntries(Object.entries(v).map(([a,b])=>[a,dim(b)])):v)}};
  };
  const img=(src,x,y)=>create(hmUI.widget.IMG,{src:src+'.png',x,y});
  img('background',0,0);
  this._listeners=[];this._gauges=[];
  const gauge=(name,id,read,ratio,angle,bottom=false)=>{
   const w=img(name+'_scale_0',['battery','steps'].includes(name)?52:285,['battery','heart'].includes(name)?52:285);
   const chars=Array.from({length:6},()=>create(hmUI.widget.IMG,{x:0,y:0,w:480,h:480,center_x:240,center_y:240,pos_x:236,pos_y:70,src:'arc_dash.png'}));
   const icon=create(hmUI.widget.IMG,{x:0,y:0,w:480,h:480,center_x:240,center_y:240,pos_x:235,pos_y:bottom?399:70,src:'arc_icon_'+name+'.png',angle:angle+(bottom?13:-13)-(bottom?180:0)});
   const refresh=()=>{let v=NaN,r=0;try{v=read(sensor);r=ratio(sensor,v)}catch(e){}const valid=Number.isFinite(v)&&v>=0;const text=valid?String(Math.round(v))+(name==='battery'?'%':''):'−';const level=Number.isFinite(r)?Math.max(0,Math.min(20,Math.round(r*20))):0;w.setProperty(hmUI.prop.SRC,name+'_scale_'+level+'.png');chars.forEach((ch,i)=>{ch.setProperty(hmUI.prop.VISIBLE,i<text.length);if(i<text.length){const c=text[i],ang=angle+(i-(text.length-1)/2)*3.2*(bottom?-1:1);ch.setProperty(hmUI.prop.MORE,{src:c==='%'?'arc_percent.png':c==='−'?'arc_dash.png':'arc_'+c+'.png',pos_x:236,pos_y:bottom?399:70,angle:bottom?ang-180:ang})}})};
   let sensor;try{sensor=hmSensor.createSensor(id);const event=name==='heart'?hmSensor.event.LAST:hmSensor.event.CHANGE;sensor.addEventListener(event,refresh);this._listeners.push({sensor,event,refresh})}catch(e){}this._gauges.push(refresh);refresh();
  };
  gauge('battery',hmSensor.id.BATTERY,s=>s.current,(s,v)=>v/100,319);
  gauge('heart',hmSensor.id.HEART,s=>s.last>0&&s.last<=255?s.last:NaN,(s,v)=>(v-30)/154,45);
  gauge('steps',hmSensor.id.STEP,s=>s.current,(s,v)=>s.target>0?v/s.target:NaN,224,true);
  gauge('calories',hmSensor.id.CALORIE,s=>s.current,(s,v)=>s.target>0?v/s.target:NaN,132,true);
  const num=(type,x,y,w,name='value',unit)=>{
   const p={x,y,w,h:36,type:hmUI.data_type[type],font_array:font(name),h_space:0,align_h:hmUI.align.CENTER_H,dot_image:name==='metric'?'metric_dot.png':'dot.png',negative_image:name==='forecast'?'forecast_minus.png':'minus.png'};
   if(unit)p.unit_en=p.unit_sc=p.unit_tc=unit+'.png';return create(hmUI.widget.TEXT_IMG,p);
  };
  create(hmUI.widget.IMG_LEVEL,{x:220,y:78,image_array:Array.from({length:11},(_,i)=>'battery_icon_'+i+'.png'),image_length:11,type:hmUI.data_type.BATTERY});
  num('BATTERY',204,115,72,'battery','battery_percent');
  img('walk_icon',108,204);num('STEP',70,243,100,'step');
  img('heart_icon',346,204);const heart=num('HEART',325,243,70);const missing=img('minus',353,249);
  create(hmUI.widget.IMG_LEVEL,{x:224,y:291,image_array:Array.from({length:29},(_,i)=>'weather_'+i+'.png'),image_length:29,type:hmUI.data_type.WEATHER_CURRENT});
  num('WEATHER_CURRENT',194,322,92,'value','degree');
  img('low',195,375);num('WEATHER_LOW',205,363,33,'small','degree');
  img('high',241,375);num('WEATHER_HIGH',251,363,33,'small','degree');
  const weeks=Array.from({length:7},(_,i)=>'week_'+i+'.png');
  create(hmUI.widget.IMG_WEEK,{x:248,y:406,week_en:weeks,week_sc:weeks,week_tc:weeks});
  create(hmUI.widget.IMG_DATE,{day_startX:180,day_startY:407,day_zero:1,day_space:0,day_align:hmUI.align.LEFT,day_en_array:font('date'),day_sc_array:font('date'),day_tc_array:font('date'),month_startX:214,month_startY:407,month_zero:1,month_space:0,month_align:hmUI.align.LEFT,month_en_array:font('date'),month_sc_array:font('date'),month_tc_array:font('date'),month_follow:0});img('date_dot',208,407);
  img('colon',235,180);
  create(hmUI.widget.IMG_TIME,{hour_zero:1,hour_startX:181,hour_startY:180,hour_array:font('time'),hour_space:0,hour_align:hmUI.align.LEFT,minute_zero:1,minute_startX:245,minute_startY:180,minute_array:font('time'),minute_space:0,minute_align:hmUI.align.LEFT,minute_follow:0});
  const pointer={hour_centerX:240,hour_centerY:240,hour_posX:36,hour_posY:232,hour_path:'hour.png',minute_centerX:240,minute_centerY:240,minute_posX:36,minute_posY:232,minute_path:'minute.png',second_centerX:240,second_centerY:240,second_posX:6,second_posY:222,second_path:'second.png'};
  // Native H/M hands plus a fractional-angle second image in the active view.
  this._smoothSupported=typeof timer!=='undefined'&&typeof timer.createTimer==='function';
  if(this._smoothSupported)Object.keys(pointer).filter(k=>k.startsWith('second_')).forEach(k=>delete pointer[k]);
  create(hmUI.widget.TIME_POINTER,pointer);
  this._startSecond=()=>{};this._stopSecond=()=>{};
  if(this._smoothSupported){
   const second=hmUI.createWidget(hmUI.widget.IMG,{x:0,y:0,w:480,h:480,center_x:240,center_y:240,pos_x:234,pos_y:18,src:'second.png',angle:0,show_level:normal,enable:false});
   const update=()=>second.setProperty(hmUI.prop.ANGLE,(Date.now()%60000)*.006);
   this._stopSecond=()=>{if(this._secondTimer!==undefined){timer.stopTimer(this._secondTimer);this._secondTimer=undefined}};
   this._startSecond=()=>{this._stopSecond();update();this._secondTimer=timer.createTimer(50,50,update,{})};
   this._startSecond();
  }
  img('cap',227,227);

  const refresh=()=>{let value;try{value=this._heart.last}catch(e){}const valid=typeof value==='number'&&Number.isFinite(value)&&value>0&&value<=255;heart.setProperty(hmUI.prop.VISIBLE,valid);missing.setProperty(hmUI.prop.VISIBLE,!valid)};
  try{this._heart=hmSensor.createSensor(hmSensor.id.HEART);this._event=hmSensor.event.LAST;this._callback=refresh;this._heart.addEventListener(this._event,refresh)}catch(e){}refresh();
  hmUI.createWidget(hmUI.widget.WIDGET_DELEGATE,{resume_call:()=>{refresh();this._gauges.forEach(f=>f());this._startSecond()},pause_call:()=>{this._stopSecond()}});
  taps.forEach(([name,x,y,w,h,url])=>{
   const metric={steps:'STEP'}[name];
   const hit=metric?hmUI.createWidget(hmUI.widget.IMG_CLICK,{x,y,w,h,src:'hit_'+name+'.png',type:hmUI.data_type[metric],show_level:normal,enable:true}):hmUI.createWidget(hmUI.widget.BUTTON,{x,y,w,h,text:'',normal_src:'hit_'+name+'.png',press_src:'hit_'+name+'.png',show_level:normal,enable:true,click_func:()=>hmApp.startApp({url,native:true})});hit.setEnable(true);
  });
 },onInit(){this.init_view()},build(){this.init_view()},onDestroy(){if(this._stopSecond)this._stopSecond();if(this._heart)this._heart.removeEventListener(this._event,this._callback);(this._listeners||[]).forEach(x=>x.sensor.removeEventListener(x.event,x.refresh))}
});
})();}catch(e){console.log('Graphite Arm error',e);}
