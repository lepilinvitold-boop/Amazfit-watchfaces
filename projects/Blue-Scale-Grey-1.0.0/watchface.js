try { (()=>{
const app=__$$hmAppManager$$__.currentApp,mod=app.current;
const font=n=>Array.from({length:10},(_,i)=>n+'_'+i+'.png');
const taps=[['battery',219,83,43,38,'Settings_batteryManagerScreen'],['weather',128,122,102,102,'WeatherScreen'],['heart',250,122,102,102,'heart_app_Screen'],['steps',128,239,102,102,'activityAppScreen'],['date',250,239,102,102,'ScheduleCalScreen'],['hours',181,347,54,39,'StopWatchScreen'],['minutes',245,347,54,39,'CountdownAppScreen'],['distance',111,388,104,23,'activityAppScreen'],['calories',265,388,104,23,'activityAppScreen']];
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
   return {setProperty(k,v){w.setProperty(k,v);aw.setProperty(k,v)}};
  };
  const img=(src,x,y)=>create(hmUI.widget.IMG,{src:src+'.png',x,y});
  img('background',0,0);
  const num=(type,x,y,w,name='value',unit)=>{
   const p={x,y,w,h:36,type:hmUI.data_type[type],font_array:font(name),h_space:0,align_h:hmUI.align.CENTER_H,dot_image:'dot.png',negative_image:'minus.png'};
   if(unit)p.unit_en=p.unit_sc=p.unit_tc=unit+'.png';return create(hmUI.widget.TEXT_IMG,p);
  };
  num('BATTERY',220,102,38,'small');num('WEATHER_CURRENT',146,195,79,'value','degree');
  const heart=num('HEART',266,195,70);const missing=img('minus',294,205);
  create(hmUI.widget.IMG_LEVEL,{x:163,y:139,image_array:Array.from({length:29},(_,i)=>'weather_'+i+'.png'),image_length:29,type:hmUI.data_type.WEATHER_CURRENT});
  num('STEP',130,302,98,'step');num('DISTANCE',100,389,65,'small');num('CAL',273,389,55,'small');
  const weeks=Array.from({length:7},(_,i)=>'week_'+i+'.png');
  create(hmUI.widget.IMG_WEEK,{x:271,y:260,week_en:weeks,week_sc:weeks,week_tc:weeks});
  create(hmUI.widget.IMG_DATE,{day_startX:262,day_startY:300,day_zero:1,day_space:0,day_align:hmUI.align.LEFT,day_en_array:font('date'),day_sc_array:font('date'),day_tc_array:font('date'),month_startX:305,month_startY:300,month_zero:1,month_space:0,month_align:hmUI.align.LEFT,month_en_array:font('date'),month_sc_array:font('date'),month_tc_array:font('date'),month_follow:0});img('date_dot',298,300);
  img('colon',235,347);
  create(hmUI.widget.IMG_TIME,{hour_zero:1,hour_startX:181,hour_startY:347,hour_array:font('time'),hour_space:0,hour_align:hmUI.align.LEFT,minute_zero:1,minute_startX:245,minute_startY:347,minute_array:font('time'),minute_space:0,minute_align:hmUI.align.LEFT,minute_follow:0});
  create(hmUI.widget.TIME_POINTER,{hour_centerX:240,hour_centerY:240,hour_posX:21,hour_posY:156,hour_path:'hour.png',minute_centerX:240,minute_centerY:240,minute_posX:19,minute_posY:192,minute_path:'minute.png',second_centerX:240,second_centerY:240,second_posX:6,second_posY:222,second_path:'second.png'});img('cap',227,227);
  const refresh=()=>{let value;try{value=this._heart.last}catch(e){}const valid=typeof value==='number'&&Number.isFinite(value)&&value>0&&value<=255;heart.setProperty(hmUI.prop.VISIBLE,valid);missing.setProperty(hmUI.prop.VISIBLE,!valid)};
  try{this._heart=hmSensor.createSensor(hmSensor.id.HEART);this._event=hmSensor.event.LAST;this._callback=refresh;this._heart.addEventListener(this._event,refresh)}catch(e){}refresh();
  hmUI.createWidget(hmUI.widget.WIDGET_DELEGATE,{resume_call:refresh,pause_call:()=>{}});
  taps.forEach(([name,x,y,w,h,url])=>{
   const metric={steps:'STEP',distance:'DISTANCE',calories:'CAL'}[name];
   const hit=metric?hmUI.createWidget(hmUI.widget.IMG_CLICK,{x,y,w,h,src:'hit_'+name+'.png',type:hmUI.data_type[metric],show_level:normal,enable:true}):hmUI.createWidget(hmUI.widget.BUTTON,{x,y,w,h,text:'',normal_src:'hit_'+name+'.png',press_src:'hit_'+name+'.png',show_level:normal,enable:true,click_func:()=>hmApp.startApp({url,native:true})});hit.setEnable(true);
  });
 },onInit(){this.init_view()},build(){this.init_view()},onDestroy(){if(this._heart)this._heart.removeEventListener(this._event,this._callback)}
});
})();}catch(e){console.log('Blue Scale Grey error',e);}
