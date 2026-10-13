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
const taps = [["battery",324,92,64,64,"BATTERY"],["heart",232,41,16,8,"HEART"],["heart",207,49,66,8,"HEART"],["heart",196,57,88,8,"HEART"],["heart",188,65,104,8,"HEART"],["heart",182,73,116,8,"HEART"],["heart",178,81,124,8,"HEART"],["heart",175,89,130,8,"HEART"],["heart",173,97,134,8,"HEART"],["heart",172,105,136,8,"HEART"],["heart",172,113,136,8,"HEART"],["heart",173,121,134,2,"HEART"],["heart",174,123,132,6,"HEART"],["heart",177,129,126,8,"HEART"],["heart",181,137,118,8,"HEART"],["heart",186,145,108,8,"HEART"],["heart",193,153,94,8,"HEART"],["heart",204,161,72,8,"HEART"],["heart",222,169,36,8,"HEART"],["heart",232,177,16,2,"HEART"],["stress",108,171,16,8,"STRESS"],["stress",83,179,66,8,"STRESS"],["stress",72,187,88,8,"STRESS"],["stress",64,195,104,8,"STRESS"],["stress",58,203,116,8,"STRESS"],["stress",54,211,124,8,"STRESS"],["stress",51,219,130,8,"STRESS"],["stress",49,227,134,8,"STRESS"],["stress",48,235,136,8,"STRESS"],["stress",48,243,136,8,"STRESS"],["stress",49,251,134,2,"STRESS"],["calories",50,253,132,6,"CAL"],["calories",53,259,126,8,"CAL"],["calories",57,267,118,8,"CAL"],["calories",62,275,108,8,"CAL"],["calories",69,283,94,8,"CAL"],["calories",80,291,72,8,"CAL"],["calories",98,299,36,8,"CAL"],["calories",108,307,16,2,"CAL"],["steps",356,171,16,8,"STEP"],["steps",331,179,66,8,"STEP"],["steps",320,187,88,8,"STEP"],["steps",312,195,104,8,"STEP"],["steps",306,203,116,8,"STEP"],["steps",302,211,124,8,"STEP"],["steps",299,219,130,8,"STEP"],["steps",297,227,134,8,"STEP"],["steps",296,235,136,8,"STEP"],["steps",296,243,136,8,"STEP"],["steps",297,251,134,2,"STEP"],["distance",298,253,132,6,"DISTANCE"],["distance",301,259,126,8,"DISTANCE"],["distance",305,267,118,8,"DISTANCE"],["distance",310,275,108,8,"DISTANCE"],["distance",317,283,94,8,"DISTANCE"],["distance",328,291,72,8,"DISTANCE"],["distance",346,299,36,8,"DISTANCE"],["distance",356,307,16,2,"DISTANCE"],["weather",177,283,126,49,"WEATHER_CURRENT"],["hours",178,350,56,49,"STOP_WATCH"],["minutes",246,350,56,49,"COUNT_DOWN"],["alarm",324,324,64,64,"ALARM_CLOCK"]]
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
  num('HEART',202,77,76)
  num('STRESS',70,210,92,'small');num('CAL',70,262,92,'detail')
  num('STEP',314,211,100);num('DISTANCE',318,262,92,'detail')
  num('BATTERY',331,117,50,'battery')
  num('WEATHER_CURRENT',216,303,84,'circle','graph_degree.png')
  createWidget(hmUI.widget.IMG_LEVEL,{x:186,y:300,image_array:Array.from({length:29},(_,i)=>'weather_'+i+'.png'),image_length:29,type:hmUI.data_type.WEATHER_CURRENT,show_level:normal,enable:false})
  createWidget(hmUI.widget.IMG_LEVEL,{x:295,y:171,image_array:rings,image_length:21,type:hmUI.data_type.STEP,show_level:normal,enable:false})
  createWidget(hmUI.widget.IMG_LEVEL,{x:171,y:41,image_array:heartRings,image_length:21,type:hmUI.data_type.HEART,show_level:normal,enable:false})
  createWidget(hmUI.widget.IMG,{x:103,y:335,src:'phone_icon.png',show_level:normal,enable:false})
  createWidget(hmUI.widget.IMG,{x:103,y:103,src:'workout_icon.png',show_level:normal,enable:false})
  createWidget(hmUI.widget.IMG,{x:336,y:336,src:'alarm_icon.png',show_level:normal,enable:false})
  const stressRing=createWidget(hmUI.widget.IMG,{x:47,y:171,src:'stress_ring_0.png',show_level:normal,enable:false})
  const calorieRing=createWidget(hmUI.widget.IMG,{x:47,y:171,src:'calorie_ring_0.png',show_level:normal,enable:false})
  this._listeners=[]
  const attach=(id,widget,name,ratio)=>{try{const sensor=hmSensor.createSensor(id);const update=()=>{try{const value=ratio(sensor);const level=Number.isFinite(value)?Math.max(0,Math.min(20,Math.round(value*20))):0;widget.setProperty(hmUI.prop.MORE,{src:name+'_ring_'+level+'.png'})}catch(e){widget.setProperty(hmUI.prop.MORE,{src:name+'_ring_0.png'})}};const event=hmSensor.event.CHANGE;sensor.addEventListener(event,update);this._listeners.push({sensor,event,update});update()}catch(e){console.log('Graphite optional scale unavailable',name)}}
  attach(hmSensor.id.STRESS,stressRing,'stress',s=>typeof s.current==='number'&&s.current>0&&s.current<=100?s.current/100:NaN)
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
  const rangeWidgets=Array.from({length:7},(_,i)=>createWidget(hmUI.widget.IMG,{x:191+i*14,y:125,w:14,h:29,src:'range_dash.png',enable:false,show_level:normal}))
  const drawRange=text=>{
   const x=240-text.length*7
   rangeWidgets.forEach((widget,i)=>{
    widget.setProperty(hmUI.prop.VISIBLE,i<text.length)
    if(i<text.length){const c=text.charAt(i);widget.setProperty(hmUI.prop.MORE,{x:x+i*14,src:c==='–'?'range_sep.png':c==='-'?'range_dash.png':'range_'+c+'.png'})}
   })
  }
  drawRange('--–--')
  const refreshRange=()=>{
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

  // Exact annular hit cells; no cell extends into the inner data panels.
  const bezelTargets=[['player',315,'SYSTEM_APP_MUSIC'],['pressure',225,'SYSTEM_APP_ALTIMETER'],['settings',135,'SYSTEM_APP_SETTING']];
  bezelTargets.forEach(([name,angle,constant])=>{
   for(let y=0;y<480;y+=4){let first=-1,last=-1;
    for(let x=0;x<480;x++){
     let inside=true;
     for(const [ox,oy] of [[0,0],[1,0],[0,4],[1,4]]){
      const dx=x+ox-240,dy=y+oy-240,r=Math.hypot(dx,dy),a=(Math.atan2(dx,-dy)*180/Math.PI+360)%360,d=Math.abs(((a-angle+540)%360)-180);
      if(r<214||r>237||d>11)inside=false;
     }
     if(inside){if(first<0)first=x;last=x;}
    }
    if(first>=0)createWidget(hmUI.widget.BUTTON,{x:first,y,w:last-first+1,h:4,text:'',normal_src:'tap_bezel.png',press_src:'tap_bezel.png',show_level:normal,click_func:()=>{
     try{const router=__$$RQR$$__('@zos/router');router.launchApp({appId:router[constant],native:true});}catch(e){console.log('Bezel shortcut unavailable',name,e);}
    }});
   }
  });
  // All tap targets on top, so moving hands cannot cover hit regions.
  taps.forEach(([name,x,y,w,h,type])=>createWidget(hmUI.widget.IMG_CLICK,{x,y,w,h,src:'tap_'+name+'.png',type:hmUI.data_type[type],show_level:normal}))
  createWidget(hmUI.widget.BUTTON,{x:185,y:404,w:110,h:38,text:'',normal_src:'tap_date.png',press_src:'tap_date.png',show_level:normal,click_func:()=>hmApp.startApp({appid:1,url:'ScheduleCalScreen',native:true})})
  createWidget(hmUI.widget.BUTTON,{x:92,y:324,w:64,h:64,text:'',normal_src:'tap_phone.png',press_src:'tap_phone.png',show_level:normal,click_func:()=>hmApp.startApp({appid:1,url:'PhoneHomeScreen',native:true})})
  createWidget(hmUI.widget.BUTTON,{x:92,y:92,w:64,h:64,text:'',normal_src:'tap_workout.png',press_src:'tap_workout.png',show_level:normal,click_func:()=>hmApp.startApp({appid:1,url:'SportListScreen',native:true})})
 },onInit(){this.init_view()},build(){this.init_view()},onDestroy(){
  try{(this._listeners||[]).forEach(x=>x.sensor.removeEventListener(x.event,x.update));if(this._heart&&this._heartCallback)this._heart.removeEventListener(this._heartEvent,this._heartCallback)}catch(e){console.log('Owl heart listener cleanup',e)}
 }
})

;
    })());
} catch(e){console.log("Mini Program Error",e);}