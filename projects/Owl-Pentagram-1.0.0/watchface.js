try {
 const app=__$$hmAppManager$$__.currentApp, module=app.current;
 const font=n=>Array.from({length:10},(_,i)=>n+'_'+i+'.png');
 const taps = [["stress",108,90,70,88,"StressHomeScreen"],["heart",302,90,60,88,"heart_app_Screen"],["battery",213,102,54,66,"Settings_batteryManagerScreen"],["steps",62,246,90,76,"activityAppScreen"],["distance",343,246,76,76,"activityAppScreen"],["hours",117,187,66,54,"AlarmInfoScreen"],["minutes",303,187,66,54,"CountdownAppScreen"],["date",175,285,48,44,"ScheduleCalScreen"],["weekday",260,285,56,44,"ScheduleCalScreen"],["weather",188,369,112,43,"WeatherScreen"]]
 module.module=DeviceRuntimeCore.WatchFace({
 init_view(){
  if(this.built)return;this.built=true;
  const normal=hmUI.show_level.ONLY_NORMAL,aod=hmUI.show_level.ONAL_AOD;
  const dim=v=>typeof v==='string'&&v.endsWith('.png')?'aod_'+v:Array.isArray(v)?v.map(dim):v;
  const visual=(type,p)=>{
   hmUI.createWidget(type,p);const q={};Object.keys(p).forEach(k=>q[k]=dim(p[k]));q.show_level=aod;
   if(type===hmUI.widget.TIME_POINTER)Object.keys(q).filter(k=>k.startsWith('second_')).forEach(k=>delete q[k]);
   hmUI.createWidget(type,q);
  };
  visual(hmUI.widget.IMG,{x:0,y:0,w:480,h:480,src:'background.png',show_level:normal,enable:false});
  const number=(type,x,y,w,name='value',unit)=>{
   const p={x,y,w,h:32,font_array:font(name),h_space:0,align_h:hmUI.align.CENTER_H,type:hmUI.data_type[type],dot_image:'dot.png',negative_image:'minus.png',show_level:normal,enable:false};
   if(unit)p.unit_en=p.unit_sc=p.unit_tc=unit;
   visual(hmUI.widget.TEXT_IMG,p);
  };
  number('STRESS',108,143,70);number('HEART',302,143,60);
  number('BATTERY',216,156,48,'battery','percent.png');
  number('STEP',62,293,90);number('DISTANCE',338,293,84);
  number('WEATHER_CURRENT',224,373,76,'value','degree.png');
  visual(hmUI.widget.IMG_LEVEL,{x:188,y:373,image_array:Array.from({length:29},(_,i)=>'weather_'+i+'.png'),image_length:29,type:hmUI.data_type.WEATHER_CURRENT,show_level:normal,enable:false});
  visual(hmUI.widget.IMG_TIME,{hour_zero:1,hour_startX:126,hour_startY:194,hour_array:font('time'),hour_space:0,hour_align:hmUI.align.LEFT,minute_zero:1,minute_startX:310,minute_startY:194,minute_array:font('time'),minute_space:0,minute_align:hmUI.align.LEFT,minute_follow:0,show_level:normal,enable:false});
  visual(hmUI.widget.IMG_DATE,{day_startX:181,day_startY:292,day_zero:1,day_space:0,day_align:hmUI.align.LEFT,day_en_array:font('date'),day_sc_array:font('date'),day_tc_array:font('date'),show_level:normal,enable:false});
  const weeks=Array.from({length:7},(_,i)=>'week_'+i+'.png');
  visual(hmUI.widget.IMG_WEEK,{x:265,y:292,week_en:weeks,week_sc:weeks,week_tc:weeks,show_level:normal,enable:false});
  visual(hmUI.widget.TIME_POINTER,{hour_centerX:240,hour_centerY:240,hour_posX:21,hour_posY:156,hour_path:'hour.png',minute_centerX:240,minute_centerY:240,minute_posX:19,minute_posY:192,minute_path:'minute.png',second_centerX:240,second_centerY:240,second_posX:6,second_posY:222,second_path:'second.png',show_level:normal,enable:false});
  visual(hmUI.widget.IMG,{x:227,y:227,src:'cap.png',show_level:normal,enable:false});
  taps.forEach(([name,x,y,w,h,url])=>{const button=hmUI.createWidget(hmUI.widget.BUTTON,{x,y,w,h,text:'',normal_src:'hit_'+name+'.png',press_src:'hit_'+name+'.png',show_level:normal,enable:true,click_func:()=>hmApp.startApp({url,native:true})});button.setEnable(true);});
 },onInit(){this.init_view()},build(){this.init_view()},onDestroy(){}
 });
} catch(e){console.log('Mini Program Error',e);}
