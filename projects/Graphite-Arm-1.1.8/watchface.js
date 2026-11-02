try { (()=>{
const app=__$$hmAppManager$$__.currentApp,mod=app.current;
const font=n=>Array.from({length:10},(_,i)=>n+'_'+i+'.png');
const taps=[["battery", 190, 60, 100, 100, "Settings_batteryManagerScreen"], ["weather", 190, 320, 100, 105, "WeatherScreen"], ["heart", 320, 190, 100, 100, "heart_app_Screen"], ["steps", 60, 190, 100, 100, "activityAppScreen"], ["date", 170, 260, 140, 54, "ScheduleCalScreen"], ["date_left", 153, 290, 17, 34, "ScheduleCalScreen"], ["date_upper_left", 160, 287, 10, 3, "ScheduleCalScreen"], ["date_right", 310, 290, 17, 34, "ScheduleCalScreen"], ["date_upper_right", 310, 287, 10, 3, "ScheduleCalScreen"], ["date_bottom_left", 170, 314, 20, 12, "ScheduleCalScreen"], ["date_bottom_right", 290, 314, 20, 12, "ScheduleCalScreen"], ["alarm", 152, 150, 38, 40, "AlarmInfoScreen"], ["alarm_upper_mid", 190, 160, 23, 30, "AlarmInfoScreen"], ["alarm_lower", 160, 190, 53, 30, "AlarmInfoScreen"], ["stopwatch", 213, 175, 54, 45, "StopWatchScreen"], ["countdown", 290, 150, 38, 40, "CountdownAppScreen"], ["countdown_upper_mid", 267, 160, 23, 30, "CountdownAppScreen"], ["countdown_lower", 267, 190, 53, 30, "CountdownAppScreen"], ["battery_scale0", 56, 122, 94, 64, "activityAppScreen"], ["battery_scale1", 80, 86, 98, 36, "activityAppScreen"], ["battery_scale2", 120, 56, 64, 30, "activityAppScreen"], ["distance0", 56, 294, 94, 50, "activityAppScreen"], ["distance1", 80, 344, 98, 40, "activityAppScreen"], ["distance2", 120, 384, 64, 44, "activityAppScreen"], ["calories0", 330, 294, 94, 50, "activityAppScreen"], ["calories1", 302, 344, 98, 40, "activityAppScreen"], ["calories2", 296, 384, 64, 44, "activityAppScreen"]];
taps.push(['stress_scale0',330,122,94,64,'StressHomeScreen'],['stress_scale1',302,86,98,36,'StressHomeScreen'],['stress_scale2',296,56,64,30,'StressHomeScreen']);
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
  const gauge=(name,id,read,ratio,angle,bottom=false,showLabel=true)=>{
   const w=img(name+'_scale_0',['battery','steps'].includes(name)?40:240,['battery','stress'].includes(name)?40:240);
   const chars=Array.from({length:6},()=>create(hmUI.widget.IMG,{x:0,y:0,w:480,h:480,center_x:240,center_y:240,pos_x:236,pos_y:70,src:'arc_dash.png'}));
   const refresh=()=>{let v=NaN,r=0;try{v=read(sensor);r=ratio(sensor,v)}catch(e){}const valid=Number.isFinite(v)&&v>=0;const tone=valid?(name==='battery'&&v<20?'red_':name==='steps'&&r>=1?'green_':name==='stress'&&v>=80?'blue_':''):'';const text=name==='stress'?(valid?String(Math.round(v)):'−'):(valid&&Number.isFinite(r)?String(Math.min(9999,Math.max(0,Math.round(r*100))))+'%':'−');const level=Number.isFinite(r)?Math.max(0,Math.min(20,Math.round(r*20))):0;w.setProperty(hmUI.prop.SRC,tone+name+'_scale_'+level+'.png');chars.forEach((ch,i)=>{ch.setProperty(hmUI.prop.VISIBLE,showLabel&&i<text.length);if(showLabel&&i<text.length){const c=text[i],ang=angle+(i-(text.length-1)/2)*5.2*(bottom?-1:1);ch.setProperty(hmUI.prop.SRC,(c==='%'?'arc_percent.png':c==='−'?'arc_dash.png':'arc_'+c+'.png'));ch.setProperty(hmUI.prop.MORE,{pos_x:Math.round(240-(c==='%'?16:c==='−'?8:14)/2),pos_y:Math.round(240+(bottom?159:-159)-(c==='%'?18:c==='−'?4:19)/2),angle:bottom?ang-180:ang})}})};
   let sensor;try{sensor=hmSensor.createSensor(id);const event=hmSensor.event.CHANGE;sensor.addEventListener(event,refresh);this._listeners.push({sensor,event,refresh})}catch(e){}this._gauges.push(refresh);refresh();
  };
  gauge('stress',hmSensor.id.STRESS,s=>s.current>0&&s.current<=100?s.current:NaN,(s,v)=>v/100,45);
  // Distance-sector fill/achievement follows the user's 10000-step goal; text stays actual km.
  const USER_STEP_GOAL=10000;
  const metricGauge=(name,id,angle,unit,color)=>{
   const top=name==='fatburn';
   const scale=img(name+'_scale_0',top||name==='distance'?40:240,top?40:240);
   const cells=Array.from({length:9},()=>create(hmUI.widget.IMG,{x:0,y:0,w:480,h:480,center_x:240,center_y:240,pos_x:233,pos_y:390,src:'arc_dash.png'}));
   const update=()=>{
    let value=NaN,target=NaN;
    try{value=sensor.current;target=sensor.target}catch(e){}
    const valid=typeof value==='number'&&Number.isFinite(value)&&value>=0;
    let ratio=NaN;
    if(name==='distance'){
     let steps;try{steps=stepSensor.current}catch(e){}
     if(valid&&typeof steps==='number'&&Number.isFinite(steps)&&steps>=0)ratio=steps/USER_STEP_GOAL;
    }else if(valid&&typeof target==='number'&&Number.isFinite(target)&&target>0)ratio=value/target;
    const tone=Number.isFinite(ratio)&&ratio>=1?color+'_':'';
    const level=Number.isFinite(ratio)?Math.max(0,Math.min(20,(top?Math.floor(ratio*20):Math.round(ratio*20)))):0;
    scale.setProperty(hmUI.prop.SRC,tone+name+'_scale_'+level+'.png');
    const label=valid?(name==='distance'?(Math.floor(value/10)/100).toFixed(2).replace('.',','):String(Math.floor(value))):'−';
    const tokens=label.split('').map(c=>({key:c==='−'?'dash':c===','?'dot':c,w:c==='−'?8:c===','?4:14,h:c==='−'?4:19}));
    if(valid)tokens.push({key:unit,w:unit==='km'?18:unit==='min'?36:26,h:19,gap:6});
    // Same 25px arc digits as above; proportional arc-length spacing fits units.
    const total=tokens.reduce((sum,t)=>sum+t.w+(t.gap||0),0);
    let offset=-total/2;
    cells.forEach((cell,i)=>{
     cell.setProperty(hmUI.prop.VISIBLE,i<tokens.length);
     if(i>=tokens.length)return;
     const t=tokens[i];offset+=t.gap||0;const a=angle+(top?1:-1)*(offset+t.w/2)/159*180/Math.PI;
     cell.setProperty(hmUI.prop.SRC,'arc_'+t.key+'.png');
     cell.setProperty(hmUI.prop.MORE,{pos_x:Math.round(240-t.w/2),pos_y:Math.round((top?81:399)-t.h/2),angle:top?a:a-180});
     offset+=t.w;
    });
   };
   let sensor,stepSensor;
   const listen=id=>{const s=hmSensor.createSensor(id),event=hmSensor.event.CHANGE;s.addEventListener(event,update);this._listeners.push({sensor:s,event,refresh:update});return s};
   try{sensor=listen(id)}catch(e){}
   if(name==='distance')try{stepSensor=listen(hmSensor.id.STEP)}catch(e){}
   this._gauges.push(update);update();
  };
  metricGauge('fatburn',hmSensor.id.FAT_BURRING,315,'min','purple');
  metricGauge('distance',hmSensor.id.DISTANCE,225,'km','green');
  metricGauge('calories',hmSensor.id.CALORIE,135,'kcal','yellow');
  const num=(type,x,y,w,name='value',unit,alignment=hmUI.align.CENTER_H,spacing=0)=>{
   const p={x,y,w,h:36,type:hmUI.data_type[type],font_array:font(name),h_space:spacing,align_h:alignment,dot_image:name==='metric'?'metric_dot.png':'dot.png',negative_image:name==='forecast'?'forecast_minus.png':'minus.png'};
   if(unit)p.unit_en=p.unit_sc=p.unit_tc=unit+'.png';return create(hmUI.widget.TEXT_IMG,p);
  };
  const batteryIconProps={x:220,y:76,image_length:11,type:hmUI.data_type.BATTERY};
  const batteryIcon=create(hmUI.widget.IMG_LEVEL,{...batteryIconProps,image_array:Array.from({length:11},(_,i)=>'battery_icon_'+i+'.png')});
  const batteryLowIcon=create(hmUI.widget.IMG_LEVEL,{...batteryIconProps,image_array:Array.from({length:11},(_,i)=>'red_battery_icon_'+i+'.png')});
  const batteryValue=num('BATTERY',204,107,72,'battery','battery_percent');
  const batteryLowValue=num('BATTERY',204,107,72,'red_battery','red_battery_percent');
  let batterySensor;
  const refreshBattery=()=>{
   let value;try{value=batterySensor.current}catch(e){}
   const low=typeof value==='number'&&Number.isFinite(value)&&value>=0&&value<20;
   batteryIcon.setProperty(hmUI.prop.VISIBLE,!low);batteryValue.setProperty(hmUI.prop.VISIBLE,!low);
   batteryLowIcon.setProperty(hmUI.prop.VISIBLE,low);batteryLowValue.setProperty(hmUI.prop.VISIBLE,low);
  };
  try{batterySensor=hmSensor.createSensor(hmSensor.id.BATTERY);const event=hmSensor.event.CHANGE;batterySensor.addEventListener(event,refreshBattery);this._listeners.push({sensor:batterySensor,event,refresh:refreshBattery})}catch(e){}
  this._gauges.push(refreshBattery);refreshBattery();
  img('walk_icon',100,204);const stepValue=num('STEP',60,237,100,'step'),stepDoneValue=num('STEP',60,237,100,'green_step');
  let stepColorSensor;
  const refreshStepColor=()=>{let value;try{value=stepColorSensor.current}catch(e){}const done=typeof value==='number'&&Number.isFinite(value)&&value>=USER_STEP_GOAL;stepValue.setProperty(hmUI.prop.VISIBLE,!done);stepDoneValue.setProperty(hmUI.prop.VISIBLE,done)};
  try{stepColorSensor=hmSensor.createSensor(hmSensor.id.STEP);const event=hmSensor.event.CHANGE;stepColorSensor.addEventListener(event,refreshStepColor);this._listeners.push({sensor:stepColorSensor,event,refresh:refreshStepColor})}catch(e){}
  this._gauges.push(refreshStepColor);refreshStepColor();
  const heartIcon=img('heart_icon',358,204);const heart=num('HEART',335,237,70);const highHeart=num('HEART',335,237,70,'red_value');const missing=img('minus',363,243);
  const HEART_HIGH_THRESHOLD=151;
  create(hmUI.widget.IMG_LEVEL,{x:227,y:319,image_array:Array.from({length:29},(_,i)=>'weather_'+i+'.png'),image_length:29,type:hmUI.data_type.WEATHER_CURRENT});
  num('WEATHER_CURRENT',194,348,92,'value','degree');
  num('WEATHER_LOW',195,381,38,'forecast','forecast_degree',hmUI.align.RIGHT,-1);img('range_dash',235,386);
  num('WEATHER_HIGH',247,381,38,'forecast','forecast_degree',hmUI.align.LEFT,-1);
  const layout={"normal_time": [[157, 155], [175, 167], [190, 173], [205, 176], [227, 176], [242, 173], [257, 167], [275, 155]], "aod_time": [[180, 169], [201, 176], [216, 177], [231, 176], [252, 169]], "date": [[151, 281], [165, 269], [181, 261], [198, 256], [216, 254], [234, 256], [251, 261], [267, 269], [281, 281]]};
  const createClock=(family,positions,pattern,show)=>positions.map(([x,y],i)=>hmUI.createWidget(hmUI.widget.IMG,{x,y,src:(show===aod?'aod_':'')+family+'_'+i+'_'+pattern.charCodeAt(i)+'.png',show_level:show,enable:false}));
  const normalClock=createClock('nt',layout.normal_time,'00:00:00',normal),aodClock=createClock('at',layout.aod_time,'00:00',aod);
  const dateCells=layout.date.map(([x,y],i)=>img('dt_'+i+'_'+('01.11 ВСК'.charCodeAt(i)),x,y));
  const pad=n=>('0'+n).slice(-2);let clock;try{clock=hmSensor.createSensor(hmSensor.id.TIME)}catch(e){}
  let previousTime='',previousDate='';
  const refreshClock=()=>{
   const now=new Date();const pick=(key,fallback,min,max)=>{let v;try{v=clock[key]}catch(e){}return typeof v==='number'&&Number.isFinite(v)&&v>=min&&v<=max?v:fallback};
   const h=pick('hour',now.getHours(),0,23),m=pick('minute',now.getMinutes(),0,59),s=pick('second',now.getSeconds(),0,59);
   const label=pad(h)+':'+pad(m)+':'+pad(s);
   if(label!==previousTime){normalClock.forEach((w,i)=>w.setProperty(hmUI.prop.SRC,'nt_'+i+'_'+label.charCodeAt(i)+'.png'));aodClock.forEach((w,i)=>w.setProperty(hmUI.prop.SRC,'aod_at_'+i+'_'+label.charCodeAt(i)+'.png'));previousTime=label}
   const day=pick('day',now.getDate(),1,31),month=pick('month',now.getMonth()+1,1,12),week=pick('week',now.getDay()||7,1,7);
   const wd=['ПН','ВТ','СР','ЧТ','ПТ','СБ','ВСК'][week-1];const date=pad(day)+'.'+pad(month)+' '+wd+(wd.length===2?' ':'');
   if(date!==previousDate){dateCells.forEach((w,i)=>w.setProperty(hmUI.prop.SRC,'dt_'+i+'_'+date.charCodeAt(i)+'.png'));previousDate=date}
  };
  refreshClock();this._gauges.push(refreshClock);
  if(clock){const event=clock.event?clock.event.MINUTEEND:hmSensor.event.MINUTEEND;clock.addEventListener(event,refreshClock);this._listeners.push({sensor:clock,event,refresh:refreshClock})}
  const pointer={hour_centerX:240,hour_centerY:240,hour_posX:36,hour_posY:232,hour_path:'hour.png',minute_centerX:240,minute_centerY:240,minute_posX:36,minute_posY:232,minute_path:'minute.png',second_centerX:240,second_centerY:240,second_posX:6,second_posY:222,second_path:'second.png'};
  // Native H/M hands plus a fractional-angle second image in the active view.
  this._smoothSupported=typeof timer!=='undefined'&&typeof timer.createTimer==='function';
  if(this._smoothSupported)Object.keys(pointer).filter(k=>k.startsWith('second_')).forEach(k=>delete pointer[k]);
  const hands=create(hmUI.widget.TIME_POINTER,pointer);
  let handsVisible=true,secondHand;
  this._startSecond=()=>{};this._stopSecond=()=>{};
  if(this._smoothSupported){
   const second=hmUI.createWidget(hmUI.widget.IMG,{x:0,y:0,w:480,h:480,center_x:240,center_y:240,pos_x:234,pos_y:18,src:'second.png',angle:0,show_level:normal,enable:false});
   secondHand=second;
   const update=()=>{second.setProperty(hmUI.prop.ANGLE,(Date.now()%60000)*.006);refreshClock()};
   this._stopSecond=()=>{if(this._secondTimer!==undefined){timer.stopTimer(this._secondTimer);this._secondTimer=undefined}};
   this._startSecond=()=>{this._stopSecond();update();this._secondTimer=timer.createTimer(50,50,update,{})};
   this._startSecond();
  }
  img('cap',227,227);
  hmUI.createWidget(hmUI.widget.BUTTON,{x:220,y:220,w:40,h:40,text:'',normal_src:'hit_axis.png',press_src:'hit_axis.png',show_level:normal,enable:true,click_func:()=>{handsVisible=!handsVisible;hands.setProperty(hmUI.prop.VISIBLE,handsVisible);if(secondHand)secondHand.setProperty(hmUI.prop.VISIBLE,handsVisible)}}).setEnable(true);

  const refresh=()=>{let value;try{value=this._heart.last}catch(e){}const valid=typeof value==='number'&&Number.isFinite(value)&&value>0&&value<=255;const high=valid&&value>=HEART_HIGH_THRESHOLD;heart.setProperty(hmUI.prop.VISIBLE,valid&&!high);highHeart.setProperty(hmUI.prop.VISIBLE,high);heartIcon.setProperty(hmUI.prop.SRC,(high?'red_':'')+'heart_icon.png');missing.setProperty(hmUI.prop.VISIBLE,!valid)};
  try{this._heart=hmSensor.createSensor(hmSensor.id.HEART);this._event=hmSensor.event.LAST;this._callback=refresh;this._heart.addEventListener(this._event,refresh)}catch(e){}refresh();
  hmUI.createWidget(hmUI.widget.WIDGET_DELEGATE,{resume_call:()=>{refresh();this._gauges.forEach(f=>f());this._startSecond()},pause_call:()=>{this._stopSecond()}});
  taps.forEach(([name,x,y,w,h,url])=>{
   const metric=name==='steps'?'STEP':name.startsWith('battery_scale')?'FAT_BURNING':name.startsWith('distance')?'DISTANCE':name.startsWith('calories')?'CAL':null;
   const hit=metric?hmUI.createWidget(hmUI.widget.IMG_CLICK,{x,y,w,h,src:'hit_'+name+'.png',type:hmUI.data_type[metric],show_level:normal,enable:true}):hmUI.createWidget(hmUI.widget.BUTTON,{x,y,w,h,text:'',normal_src:'hit_'+name+'.png',press_src:'hit_'+name+'.png',show_level:normal,enable:true,click_func:()=>hmApp.startApp({url,native:true})});hit.setEnable(true);
  });
 },onInit(){this.init_view()},build(){this.init_view()},onDestroy(){if(this._stopSecond)this._stopSecond();if(this._heart)this._heart.removeEventListener(this._event,this._callback);(this._listeners||[]).forEach(x=>x.sensor.removeEventListener(x.event,x.refresh))}
});
})();}catch(e){console.log('Graphite Arm error',e);}
