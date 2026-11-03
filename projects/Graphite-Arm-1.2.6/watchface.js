try { (()=>{
const app=__$$hmAppManager$$__.currentApp,mod=app.current;
const font=n=>Array.from({length:10},(_,i)=>n+'_'+i+'.png');
const taps=[["battery", 190, 60, 100, 94, "Settings_batteryManagerScreen"], ["battery_seg1", 213, 154, 54, 6, "Settings_batteryManagerScreen"], ["weather", 200, 320, 81, 2, "WeatherScreen"], ["weather_seg1", 190, 322, 100, 103, "WeatherScreen"], ["heart", 320, 190, 100, 95, "heart_app_Screen"], ["heart_seg1", 333, 285, 87, 5, "heart_app_Screen"], ["steps", 60, 190, 100, 95, "activityAppScreen"], ["steps_seg1", 60, 285, 87, 5, "activityAppScreen"], ["date", 170, 257, 140, 57, "ScheduleCalScreen"], ["alarm_upper_mid", 190, 175, 23, 15, "AlarmInfoScreen"], ["alarm_lower", 160, 190, 53, 30, "AlarmInfoScreen"], ["stopwatch", 213, 175, 54, 45, "StopWatchScreen"], ["countdown_upper_mid", 267, 175, 23, 15, "CountdownAppScreen"], ["countdown_lower", 267, 190, 53, 30, "CountdownAppScreen"], ["battery_scale0", 56, 122, 94, 18, "activityAppScreen"], ["battery_scale0_seg1", 56, 140, 92, 46, "activityAppScreen"], ["battery_scale1", 80, 86, 98, 36, "activityAppScreen"], ["battery_scale2", 120, 56, 64, 30, "activityAppScreen"], ["distance0", 56, 294, 91, 33, "activityAppScreen"], ["distance0_seg1", 56, 327, 91, 9, "activityAppScreen"], ["distance0_seg1_seg1", 56, 336, 94, 8, "activityAppScreen"], ["distance1", 80, 344, 98, 40, "activityAppScreen"], ["distance2", 120, 384, 64, 44, "activityAppScreen"], ["calories220", 333, 294, 91, 33, "activityAppScreen"], ["calories220_seg1", 333, 327, 91, 9, "activityAppScreen"], ["calories220_seg1_seg1", 330, 336, 94, 8, "activityAppScreen"], ["calories221", 302, 344, 98, 40, "activityAppScreen"], ["calories222", 296, 384, 64, 44, "activityAppScreen"], ["stress_scale0", 330, 122, 94, 18, "StressHomeScreen"], ["stress_scale0_seg1", 332, 140, 92, 46, "StressHomeScreen"], ["stress_scale1", 302, 86, 98, 36, "StressHomeScreen"], ["stress_scale2", 296, 56, 64, 30, "StressHomeScreen"], ["alarm_extension", 148, 140, 42, 50, "AlarmInfoScreen"], ["countdown_extension", 290, 140, 42, 50, "CountdownAppScreen"], ["date_left_extension", 147, 285, 23, 29, "ScheduleCalScreen"], ["date_right_extension", 310, 285, 23, 29, "ScheduleCalScreen"], ["date_mid_left_extension", 190, 314, 10, 8, "ScheduleCalScreen"], ["date_mid_right_extension", 281, 314, 9, 8, "ScheduleCalScreen"], ["date_bottom_left_extension", 147, 314, 43, 22, "ScheduleCalScreen"], ["date_bottom_right_extension", 290, 314, 43, 22, "ScheduleCalScreen"], ["alarm_mid_extension", 190, 154, 23, 21, "AlarmInfoScreen"], ["countdown_mid_extension", 267, 154, 23, 21, "CountdownAppScreen"], ["stopwatch_extension", 213, 171, 54, 4, "StopWatchScreen"], ["stopwatch_axis_extension", 213, 220, 54, 3, "StopWatchScreen"], ["date_shift_left", 169, 284, 1, 1, "ScheduleCalScreen"], ["date_shift_right", 310, 284, 2, 1, "ScheduleCalScreen"]];

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
  img('background22',0,0);img('panel_frames22',0,0);
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
  const UNIT_LAYOUTS={"min": {"1": [{"src": "unit22_min_1_0", "x": 110, "y": 113}, {"src": "unit22_min_1_1", "x": 119, "y": 105}, {"src": "unit22_min_1_2", "x": 128, "y": 97}], "2": [{"src": "unit22_min_2_0", "x": 115, "y": 108}, {"src": "unit22_min_2_1", "x": 124, "y": 100}, {"src": "unit22_min_2_2", "x": 134, "y": 93}], "3": [{"src": "unit22_min_3_0", "x": 120, "y": 103}, {"src": "unit22_min_3_1", "x": 130, "y": 96}, {"src": "unit22_min_3_2", "x": 140, "y": 89}], "4": [{"src": "unit22_min_4_0", "x": 126, "y": 99}, {"src": "unit22_min_4_1", "x": 135, "y": 92}, {"src": "unit22_min_4_2", "x": 146, "y": 86}], "5": [{"src": "unit22_min_5_0", "x": 131, "y": 95}, {"src": "unit22_min_5_1", "x": 141, "y": 88}, {"src": "unit22_min_5_2", "x": 152, "y": 82}], "6": [{"src": "unit22_min_6_0", "x": 137, "y": 91}, {"src": "unit22_min_6_1", "x": 147, "y": 85}, {"src": "unit22_min_6_2", "x": 158, "y": 79}], "7": [{"src": "unit22_min_7_0", "x": 143, "y": 87}, {"src": "unit22_min_7_1", "x": 154, "y": 81}, {"src": "unit22_min_7_2", "x": 165, "y": 77}], "8": [{"src": "unit22_min_8_0", "x": 149, "y": 84}, {"src": "unit22_min_8_1", "x": 160, "y": 78}, {"src": "unit22_min_8_2", "x": 171, "y": 74}], "9": [{"src": "unit22_min_9_0", "x": 155, "y": 81}, {"src": "unit22_min_9_1", "x": 166, "y": 76}, {"src": "unit22_min_9_2", "x": 178, "y": 72}]}, "km": {"1": [{"src": "unit22_km_1_0", "x": 116, "y": 341}, {"src": "unit22_km_1_1", "x": 125, "y": 348}], "2": [{"src": "unit22_km_2_0", "x": 121, "y": 345}, {"src": "unit22_km_2_1", "x": 131, "y": 353}], "3": [{"src": "unit22_km_3_0", "x": 127, "y": 350}, {"src": "unit22_km_3_1", "x": 136, "y": 357}], "4": [{"src": "unit22_km_4_0", "x": 132, "y": 354}, {"src": "unit22_km_4_1", "x": 142, "y": 360}], "5": [{"src": "unit22_km_5_0", "x": 138, "y": 358}, {"src": "unit22_km_5_1", "x": 148, "y": 364}], "6": [{"src": "unit22_km_6_0", "x": 144, "y": 361}, {"src": "unit22_km_6_1", "x": 155, "y": 367}], "7": [{"src": "unit22_km_7_0", "x": 150, "y": 365}, {"src": "unit22_km_7_1", "x": 161, "y": 370}], "8": [{"src": "unit22_km_8_0", "x": 156, "y": 368}, {"src": "unit22_km_8_1", "x": 167, "y": 373}], "9": [{"src": "unit22_km_9_0", "x": 163, "y": 371}, {"src": "unit22_km_9_1", "x": 174, "y": 375}]}};
  const metricGauge=(name,id,angle,unit,color)=>{
   const top=name==='fatburn22';
   const scale=img(name+'_scale_0',top||name==='distance'?40:240,top?40:240);
   const cells=Array.from({length:9},()=>create(hmUI.widget.IMG,{x:0,y:0,w:480,h:480,center_x:240,center_y:240,pos_x:233,pos_y:390,src:'arc_dash.png'}));
   const unitGroups={};
   if(unit==='min'||unit==='km')for(const [count,items] of Object.entries(UNIT_LAYOUTS[unit]))unitGroups[count]=items.map(it=>img(it.src,it.x,it.y));
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
    const digitCount=valid?Math.min(9,label.replace(',','').length):0;Object.entries(unitGroups).forEach(([count,group])=>group.forEach(w=>w.setProperty(hmUI.prop.VISIBLE,valid&&Number(count)===digitCount)));
    const tokens=label.split('').map(c=>({key:c==='−'?'dash':c===','?'dot':c,w:c==='−'?8:c===','?4:14,h:c==='−'?4:19}));
    if(valid)tokens.push({key:unit,w:unit==='km'?24:unit==='min'?36:26,h:19,gap:6});
    // Same 25px arc digits as above; proportional arc-length spacing fits units.
    const total=tokens.reduce((sum,t)=>sum+t.w+(t.gap||0),0);
    let offset=-total/2;
    cells.forEach((cell,i)=>{
     const unitIndex=valid&&(unit==='min'||unit==='km')?tokens.length-1:-1;
     cell.setProperty(hmUI.prop.VISIBLE,i<tokens.length&&i!==unitIndex);
     if(i>=tokens.length||i===unitIndex)return;
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
  metricGauge('fatburn22',hmSensor.id.FAT_BURRING,315,'min','purple');
  metricGauge('distance',hmSensor.id.DISTANCE,225,'km','green');
  metricGauge('calories22',hmSensor.id.CALORIE,135,'kcal','yellow');
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
  const layout={"normal_time": [[154, 152], [173, 167], [188, 173], [204, 177], [228, 177], [244, 173], [259, 167], [278, 152]], "aod_time": [[177, 169], [200, 176], [216, 178], [232, 176], [255, 169]], "date": [[146, 288], [160, 273], [177, 263], [196, 256], [216, 254], [236, 256], [255, 263], [272, 273], [286, 288]]};
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
  const pointer={hour_centerX:240,hour_centerY:240,hour_posX:36,hour_posY:232,hour_path:'hour126.png',minute_centerX:240,minute_centerY:240,minute_posX:36,minute_posY:232,minute_path:'minute126.png',second_centerX:240,second_centerY:240,second_posX:6,second_posY:222,second_path:'second.png'};
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
  hmUI.createWidget(hmUI.widget.BUTTON,{x:224,y:224,w:32,h:32,text:'',normal_src:'hit_axis.png',press_src:'hit_axis.png',show_level:normal,enable:true,click_func:()=>{handsVisible=!handsVisible;hands.setProperty(hmUI.prop.VISIBLE,handsVisible);if(secondHand)secondHand.setProperty(hmUI.prop.VISIBLE,handsVisible)}}).setEnable(true);

  const refresh=()=>{let value;try{value=this._heart.last}catch(e){}const valid=typeof value==='number'&&Number.isFinite(value)&&value>0&&value<=255;const high=valid&&value>=HEART_HIGH_THRESHOLD;heart.setProperty(hmUI.prop.VISIBLE,valid&&!high);highHeart.setProperty(hmUI.prop.VISIBLE,high);heartIcon.setProperty(hmUI.prop.SRC,(high?'red_':'')+'heart_icon.png');missing.setProperty(hmUI.prop.VISIBLE,!valid)};
  try{this._heart=hmSensor.createSensor(hmSensor.id.HEART);this._event=hmSensor.event.LAST;this._callback=refresh;this._heart.addEventListener(this._event,refresh)}catch(e){}refresh();
  hmUI.createWidget(hmUI.widget.WIDGET_DELEGATE,{resume_call:()=>{refresh();this._gauges.forEach(f=>f());this._startSecond()},pause_call:()=>{this._stopSecond()}});
  taps.forEach(([name,x,y,w,h,url])=>{
   const metric=name==='steps'?'STEP':name.startsWith('battery_scale')?'FAT_BURNING':name.startsWith('distance')?'DISTANCE':name.startsWith('calories22')?'CAL':null;
   const hit=metric?hmUI.createWidget(hmUI.widget.IMG_CLICK,{x,y,w,h,src:'hit_'+name+'.png',type:hmUI.data_type[metric],show_level:normal,enable:true}):hmUI.createWidget(hmUI.widget.BUTTON,{x,y,w,h,text:'',normal_src:'hit_'+name+'.png',press_src:'hit_'+name+'.png',show_level:normal,enable:true,click_func:()=>hmApp.startApp({url,native:true})});hit.setEnable(true);
  });
 },onInit(){this.init_view()},build(){this.init_view()},onDestroy(){if(this._stopSecond)this._stopSecond();if(this._heart)this._heart.removeEventListener(this._event,this._callback);(this._listeners||[]).forEach(x=>x.sensor.removeEventListener(x.event,x.refresh))}
});
})();}catch(e){console.log('Graphite Arm error',e);}
