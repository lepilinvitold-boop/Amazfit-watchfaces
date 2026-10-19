try {
    ((() => {
        const __$$app$$__ = __$$hmAppManager$$__.currentApp;
        function getApp() {
            return __$$app$$__.app;
        }
        function getCurrentPage() {
            return __$$app$$__.current && __$$app$$__.current.module;
        }
        const __$$module$$__ = __$$app$$__.current;
        const h = new DeviceRuntimeCore.WidgetFactory(new DeviceRuntimeCore.HmDomApi(__$$app$$__, __$$module$$__));
        const {px} = __$$app$$__.__globals__;
const font = name => Array.from({length:10},(_,i)=>name+'_'+i+'.png')
const rings = Array.from({length:21},(_,i)=>'graph_ring_'+i+'.png')
const heartRings = Array.from({length:21},(_,i)=>'heart_ring_'+i+'.png')
const weeks = Array.from({length:7},(_,i)=>'week_'+i+'.png')
const taps = [["battery", 324, 92, 64, 64, "Settings_batteryManagerScreen"], ["heart", 182, 57, 116, 114, "heart_app_Screen"], ["stress", 60, 182, 112, 64, "StressHomeScreen"], ["calories", 60, 253, 112, 49, "activityAppScreen"], ["steps", 308, 182, 112, 64, "activityAppScreen"], ["distance", 308, 253, 112, 49, "activityAppScreen"], ["weather", 177, 283, 126, 49, "WeatherScreen"], ["hours", 178, 350, 56, 49, "StopWatchScreen"], ["minutes", 246, 350, 56, 49, "CountdownAppScreen"], ["alarm", 324, 324, 64, 64, "AlarmInfoScreen"], ["date", 185, 404, 110, 38, "ScheduleCalScreen"], ["phone", 92, 324, 64, 64, "PhoneHomeScreen"], ["workout", 92, 92, 64, 64, "SportListScreen"]]
__$$module$$__.module = DeviceRuntimeCore.WatchFace({
 init_view(){
  if(this._built)return;this._built=true;
  const normal=hmUI.show_level.ONLY_NORMAL
  // Separate native visual widgets for AOD; no duplicated sensors or tap targets.
  const aod=hmUI.show_level.ONAL_AOD
  const dimValue=value=>typeof value==='string'&&value.endsWith('.png')?'aod_'+value:Array.isArray(value)?value.map(dimValue):value
  const dimProps=props=>{const out={};Object.keys(props).forEach(key=>out[key]=dimValue(props[key]));return out}
  const visual=[hmUI.widget.IMG,hmUI.widget.TEXT_IMG,hmUI.widget.IMG_LEVEL,hmUI.widget.IMG_TIME,hmUI.widget.IMG_DATE,hmUI.widget.IMG_WEEK,hmUI.widget.TIME_POINTER]
  const createWidget=(type,props)=>{
   const widget=hmUI.createWidget(type,props)
   if(props.show_level!==normal||visual.indexOf(type)<0)return widget
   const dim=dimProps(props);dim.show_level=aod
   // Seconds remain in normal mode; AOD updates hour and minute natively.
   if(type===hmUI.widget.IMG_TIME){
    Object.keys(dim).filter(key=>key.startsWith('second_')||key.startsWith('minute_unit_')).forEach(key=>delete dim[key])
    dim.hour_startX=178;dim.minute_startX=246;dim.minute_follow=0
   }
   if(type===hmUI.widget.TIME_POINTER)Object.keys(dim).filter(key=>key.startsWith('second_')).forEach(key=>delete dim[key])
   const mirror=hmUI.createWidget(type,dim)
   return {setProperty(key,value){widget.setProperty(key,value);mirror.setProperty(key,key===hmUI.prop.MORE?dimProps(value):dimValue(value))}}
  }
  createWidget(hmUI.widget.IMG,{x:0,y:0,w:480,h:480,src:'background.png',show_level:normal,enable:false})
  const number=(type,x,y,w,unit)=>{
   const p={x,y,w,h:33,font_array:font('small'),h_space:0,align_h:hmUI.align.CENTER_H,type:hmUI.data_type[type],show_level:normal,enable:false,dot_image:'dot.png',negative_image:'minus.png'}
   if(unit){p.unit_en=unit;p.unit_sc=unit;p.unit_tc=unit}
   return createWidget(hmUI.widget.TEXT_IMG,p)
  }
  const num=(type,x,y,w,name='circle',unit)=>{const p={x,y,w,h:38,font_array:font(name),h_space:0,align_h:hmUI.align.CENTER_H,type:hmUI.data_type[type],show_level:normal,enable:false,dot_image:'dot.png',negative_image:'minus.png'};if(unit)p.unit_en=p.unit_sc=p.unit_tc=unit;return createWidget(hmUI.widget.TEXT_IMG,p)}
  const missingNumber=(type,x,y,w,name='circle')=>{
   const value=num(type,x,y,w,name)
   const dash=createWidget(hmUI.widget.IMG,{x:x+Math.round((w-24)/2),y:y+12,w:24,h:6,src:'missing_dash.png',show_level:normal,enable:false})
   dash.setProperty(hmUI.prop.VISIBLE,false)
   return valid=>{value.setProperty(hmUI.prop.VISIBLE,valid);dash.setProperty(hmUI.prop.VISIBLE,!valid)}
  }
  const heartValid=missingNumber('HEART',202,82,76)
  const stressValid=missingNumber('STRESS',70,210,92,'small');num('CAL',70,262,92,'detail')
  num('STEP',314,211,100);num('DISTANCE',318,262,92,'detail')
  num('BATTERY',331,117,50,'battery')
  num('WEATHER_CURRENT',216,303,84,'circle','graph_degree.png')
  createWidget(hmUI.widget.IMG_LEVEL,{x:186,y:300,image_array:Array.from({length:29},(_,i)=>'weather_'+i+'.png'),image_length:29,type:hmUI.data_type.WEATHER_CURRENT,show_level:normal,enable:false})
  createWidget(hmUI.widget.IMG_LEVEL,{x:295,y:171,image_array:rings,image_length:21,type:hmUI.data_type.STEP,show_level:normal,enable:false})
  const heartRing=createWidget(hmUI.widget.IMG_LEVEL,{x:171,y:46,image_array:heartRings,image_length:21,type:hmUI.data_type.HEART,show_level:normal,enable:false})
  const emptyHeartRing=createWidget(hmUI.widget.IMG,{x:171,y:46,src:'heart_ring_0.png',show_level:normal,enable:false})
  emptyHeartRing.setProperty(hmUI.prop.VISIBLE,false)
  createWidget(hmUI.widget.IMG,{x:103,y:335,src:'phone_icon.png',show_level:normal,enable:false})
  createWidget(hmUI.widget.IMG,{x:103,y:103,src:'workout_icon.png',show_level:normal,enable:false})
  createWidget(hmUI.widget.IMG,{x:336,y:336,src:'alarm_icon.png',show_level:normal,enable:false})
  const stressRing=createWidget(hmUI.widget.IMG,{x:47,y:171,src:'stress_ring_0.png',show_level:normal,enable:false})
  const calorieRing=createWidget(hmUI.widget.IMG,{x:47,y:171,src:'calorie_ring_0.png',show_level:normal,enable:false})
  this._listeners=[]
  const attach=(id,widget,name,ratio,onValidity)=>{try{const sensor=hmSensor.createSensor(id);const update=()=>{try{const value=ratio(sensor);if(onValidity)onValidity(Number.isFinite(value));const level=Number.isFinite(value)?Math.max(0,Math.min(20,Math.round(value*20))):0;widget.setProperty(hmUI.prop.MORE,{src:name+'_ring_'+level+'.png'})}catch(e){if(onValidity)onValidity(false);widget.setProperty(hmUI.prop.MORE,{src:name+'_ring_0.png'})}};const event=hmSensor.event.CHANGE;sensor.addEventListener(event,update);this._listeners.push({sensor,event,update});update()}catch(e){if(onValidity)onValidity(false);console.log('Graphite optional scale unavailable',name)}}
  attach(hmSensor.id.STRESS,stressRing,'stress',s=>typeof s.current==='number'&&s.current>0&&s.current<=100?s.current/100:NaN,stressValid)
  attach(hmSensor.id.CALORIE,calorieRing,'calorie',s=>typeof s.current==='number'&&s.current>=0&&typeof s.target==='number'&&s.target>0?s.current/s.target:NaN)
  // Active screen: native HH:MM:SS, no AM/PM images.
  createWidget(hmUI.widget.IMG,{x:234,y:350,src:'colon.png',show_level:normal,enable:false})
  createWidget(hmUI.widget.IMG_TIME,{
   hour_zero:1,hour_startX:178,hour_startY:350,hour_array:font('time'),hour_space:0,hour_align:hmUI.align.LEFT,
   minute_zero:1,minute_startX:246,minute_startY:350,minute_array:font('time'),minute_space:0,minute_align:hmUI.align.LEFT,minute_follow:0,
   show_level:normal,enable:false
  })
  createWidget(hmUI.widget.IMG_DATE,{day_startX:188,day_startY:404,day_zero:1,day_space:0,day_align:hmUI.align.LEFT,day_en_array:font('date'),day_sc_array:font('date'),day_tc_array:font('date'),show_level:normal,enable:false})
  createWidget(hmUI.widget.IMG_WEEK,{x:230,y:404,week_en:weeks,week_sc:weeks,week_tc:weeks,show_level:normal,enable:false})
  createWidget(hmUI.widget.TIME_POINTER,{
   hour_centerX:240,hour_centerY:240,hour_posX:21,hour_posY:156,hour_path:'hour.png',
   minute_centerX:240,minute_centerY:240,minute_posX:19,minute_posY:192,minute_path:'minute.png',
   second_centerX:240,second_centerY:240,second_posX:6,second_posY:222,second_path:'second.png',show_level:normal,enable:false
  })
  createWidget(hmUI.widget.IMG,{x:227,y:227,src:'cap.png',show_level:normal,enable:false})
  // Daily heart-rate range: missing/invalid samples never become a zero minimum.
  const rangeWidgets=Array.from({length:7},(_,i)=>createWidget(hmUI.widget.IMG,{x:191+i*14,y:119,w:14,h:29,src:'range_dash.png',enable:false,show_level:normal}))
  const drawRange=text=>{
   const x=240-text.length*7
   rangeWidgets.forEach((widget,i)=>{
    widget.setProperty(hmUI.prop.VISIBLE,i<text.length)
    if(i<text.length){const c=text.charAt(i);widget.setProperty(hmUI.prop.MORE,{x:x+i*14,src:c==='–'?'range_sep.png':c==='-'?'range_dash.png':'range_'+c+'.png'})}
   })
  }
  drawRange('--–--')
  const refreshHeart=()=>{
   let valid=false
   try{const value=this._heart&&this._heart.last;valid=typeof value==='number'&&Number.isFinite(value)&&value>0&&value<=255}catch(e){}
   heartValid(valid);heartRing.setProperty(hmUI.prop.VISIBLE,valid);emptyHeartRing.setProperty(hmUI.prop.VISIBLE,!valid)
  }
  const refreshRange=()=>{
   refreshHeart()
   try {
    const data=this._heart&&this._heart.today
    let min=Infinity,max=-Infinity
    if(Array.isArray(data))data.forEach(v=>{if(typeof v==='number'&&Number.isFinite(v)&&v>0&&v<=255){min=Math.min(min,v);max=Math.max(max,v)}})
    drawRange(min===Infinity?'--–--':Math.round(min)+'–'+Math.round(max))
   } catch(e){drawRange('--–--');console.log('Owl range unavailable',e)}
  }
  try {
   this._heart=hmSensor.createSensor(hmSensor.id.HEART)
   this._heartCallback=refreshRange
   this._heartEvent=this._heart.event?this._heart.event.LAST:hmSensor.event.LAST
   this._heart.addEventListener(this._heartEvent,this._heartCallback)
  }catch(e){console.log('Owl heart history unavailable',e)}
  refreshRange()
  createWidget(hmUI.widget.WIDGET_DELEGATE,{resume_call:()=>{refreshRange();this._listeners.forEach(x=>x.update())},pause_call:()=>{}})

  // Explicit buttons with matching resource dimensions; all created after
  // visual widgets and enabled independently of the visual/AOD factory.
  taps.forEach(([name,x,y,w,h,url])=>{
   const metric={calories:'CAL',steps:'STEP',distance:'DISTANCE'}[name]
   if(metric){
    const hit=hmUI.createWidget(hmUI.widget.IMG_CLICK,{x,y,w,h,src:'hit_'+name+'.png',type:hmUI.data_type[metric],show_level:normal,enable:true});hit.setEnable(true);return
   }
   const button=hmUI.createWidget(hmUI.widget.BUTTON,{x,y,w,h,text:'',normal_src:'hit_'+name+'.png',press_src:'hit_'+name+'.png',show_level:normal,enable:true,click_func:()=>hmApp.startApp({url,native:true})});
   button.setEnable(true);
  });

 },onInit(){this.init_view()},build(){this.init_view()},onDestroy(){
  try{(this._listeners||[]).forEach(x=>x.sensor.removeEventListener(x.event,x.update));if(this._heart&&this._heartCallback)this._heart.removeEventListener(this._heartEvent,this._heartCallback)}catch(e){console.log('Owl heart listener cleanup',e)}
 }
})

;
    })());
} catch(e){console.log("Mini Program Error",e);}