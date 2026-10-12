try {
 (()=>{
  const __$$app$$__=__$$hmAppManager$$__.currentApp;
  function getApp(){return __$$app$$__.app}
  function getCurrentPage(){return __$$app$$__.current&&__$$app$$__.current.module}
  const __$$module$$__=__$$app$$__.current;
  const h=new DeviceRuntimeCore.WidgetFactory(new DeviceRuntimeCore.HmDomApi(__$$app$$__,__$$module$$__));
  const {px}=__$$app$$__.__globals__;
  __$$module$$__.module=DeviceRuntimeCore.WatchFace({
   init_view(){
    if(this._built)return;this._built=true;this._listeners=[];
    const normal=hmUI.show_level.ONLY_NORMAL,aod=hmUI.show_level.ONAL_AOD;
    const fonts=n=>Array.from({length:10},(_,i)=>n+'_'+i+'.png');
    const dim=v=>typeof v==='string'&&v.endsWith('.png')?'aod_'+v:Array.isArray(v)?v.map(dim):v;
    const create=(type,props)=>{
     const full=Object.assign({show_level:normal,enable:false},props);const widget=hmUI.createWidget(type,full);
     const dp={};Object.keys(full).forEach(k=>dp[k]=dim(full[k]));dp.show_level=aod;
     if(type===hmUI.widget.TIME_POINTER||type===hmUI.widget.IMG_TIME)Object.keys(dp).filter(k=>k.startsWith('second_')).forEach(k=>delete dp[k]);
     const mirror=hmUI.createWidget(type,dp);
     return {setProperty(k,v){widget.setProperty(k,v);mirror.setProperty(k,k===hmUI.prop.MORE?Object.assign({},v):v)}};
    };
    // Bootstrap and background are required; optional indicators below never block the dial.
    create(hmUI.widget.IMG,{x:0,y:0,w:480,h:480,src:'background.png'});
    const number=(type,x,y,w,font,height,unit)=>{
     const p={x,y,w,h:height,font_array:fonts(font),h_space:0,align_h:hmUI.align.CENTER_H,negative_image:font+'_minus.png',dot_image:font+'_dot.png'};
     if(type)p.type=hmUI.data_type[type];else p.text='';
     if(unit)p.unit_en=p.unit_sc=p.unit_tc=unit;
     return create(hmUI.widget.TEXT_IMG,p);
    };
    // Left percentage is daily step-goal completion, not heart rate in percent.
    const progress=number(null,302,252,57,'status',26,'status_percent.png');
    number('BATTERY',357,252,58,'status',26,'status_percent.png');
    number('WEATHER_CURRENT',132,242,45,'weather',24,'degree.png');
    create(hmUI.widget.IMG,{x:235,y:336,src:'colon.png'});
    create(hmUI.widget.IMG_TIME,{
     hour_zero:1,hour_startX:171,hour_startY:336,hour_array:fonts('digital'),hour_space:0,hour_align:hmUI.align.LEFT,
     minute_zero:1,minute_startX:251,minute_startY:336,minute_array:fonts('digital'),minute_space:0,minute_align:hmUI.align.LEFT,minute_follow:0,
     second_zero:1,second_startX:319,second_startY:336,second_array:fonts('second'),second_space:0,second_align:hmUI.align.LEFT,second_follow:0,
     am_x:122,am_y:336,am_en_path:'am.png',am_sc_path:'am.png',am_tc_path:'am.png',pm_x:122,pm_y:336,pm_en_path:'pm.png',pm_sc_path:'pm.png',pm_tc_path:'pm.png'
    });
    const weeks=Array.from({length:7},(_,i)=>'week_'+i+'.png');
    create(hmUI.widget.IMG_WEEK,{x:143,y:305,w:109,h:19,week_en:weeks,week_sc:weeks,week_tc:weeks});
    create(hmUI.widget.IMG,{x:273,y:305,src:'date_slash.png'});
    create(hmUI.widget.IMG,{x:301,y:305,src:'date_slash.png'});
    create(hmUI.widget.IMG_DATE,{
     day_startX:253,day_startY:305,day_zero:1,day_space:0,day_align:hmUI.align.LEFT,day_en_array:fonts('date'),day_sc_array:fonts('date'),day_tc_array:fonts('date'),day_is_character:false,day_follow:0,
     month_startX:281,month_startY:305,month_zero:1,month_space:0,month_align:hmUI.align.LEFT,month_en_array:fonts('date'),month_sc_array:fonts('date'),month_tc_array:fonts('date'),month_is_character:false,month_follow:0
    });
    const year=number(null,309,305,20,'date',19);
    create(hmUI.widget.TIME_POINTER,{
     hour_centerX:240,hour_centerY:240,hour_posX:20,hour_posY:111,hour_path:'hour.png',
     minute_centerX:240,minute_centerY:240,minute_posX:20,minute_posY:179,minute_path:'minute.png',
     second_centerX:240,second_centerY:240,second_posX:6,second_posY:201,second_path:'second.png'
    });
    create(hmUI.widget.IMG,{x:234,y:234,src:'cap.png'});
    const refresh=()=>{
     try{if(this._step){const s=this._step,v=Number.isFinite(s.current)&&Number.isFinite(s.target)&&s.target>0?Math.max(0,Math.min(999,Math.round(s.current/s.target*100))) : null;progress.setProperty(hmUI.prop.TEXT,v===null?'--':String(v)+'u')}}catch(e){console.log('Step percentage unavailable',e)}
     try{if(this._time&&Number.isFinite(this._time.year))year.setProperty(hmUI.prop.TEXT,('0'+(this._time.year%100)).slice(-2))}catch(e){console.log('Year unavailable',e)}
    };
    try{this._step=hmSensor.createSensor(hmSensor.id.STEP);const fn=refresh,event=hmSensor.event.CHANGE;this._step.addEventListener(event,fn);this._listeners.push({sensor:this._step,event,fn})}catch(e){console.log('Steps unavailable',e)}
    try{this._time=hmSensor.createSensor(hmSensor.id.TIME)}catch(e){console.log('Date unavailable',e)}
    refresh();
    hmUI.createWidget(hmUI.widget.WIDGET_DELEGATE,{resume_call:refresh,pause_call:()=>{}});
    [['steps',65,350,70,55,'STEP'],['music',65,55,70,55,'MUSIC'],['timer',330,350,80,55,'STOP_WATCH']].forEach(([n,x,y,w,h,type])=>{
     if(hmUI.data_type[type]!==undefined)try{hmUI.createWidget(hmUI.widget.IMG_CLICK,{x,y,w,h,src:'tap_'+n+'.png',type:hmUI.data_type[type],show_level:normal})}catch(e){console.log('Shortcut unavailable',type,e)}
    });
   },onInit(){this.init_view()},build(){this.init_view()},onDestroy(){(this._listeners||[]).forEach(x=>{try{x.sensor.removeEventListener(x.event,x.fn)}catch(e){console.log('Listener cleanup',e)}})}
  });
 })();
}catch(e){console.log('Amazfit Green RU error',e);e&&e.stack&&console.log(e.stack)}
