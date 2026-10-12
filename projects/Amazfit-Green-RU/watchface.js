try { (()=> {
 const app=__$$hmAppManager$$__.currentApp,module=app.current;
 module.module=DeviceRuntimeCore.WatchFace({
 init_view(){if(this.built)return;this.built=true;
 const normal=hmUI.show_level.ONLY_NORMAL,aod=hmUI.show_level.ONAL_AOD;
 const font=n=>Array.from({length:10},(_,i)=>n+'_'+i+'.png');
 const dim=v=>typeof v==='string'&&v.endsWith('.png')?'aod_'+v:Array.isArray(v)?v.map(dim):v;
 const create=(type,p)=>{hmUI.createWidget(type,Object.assign({show_level:normal,enable:false},p));const dp={};Object.keys(p).forEach(k=>dp[k]=dim(p[k]));dp.show_level=aod;dp.enable=false;if(type===hmUI.widget.TIME_POINTER||type===hmUI.widget.IMG_TIME)Object.keys(dp).filter(k=>k.startsWith('second_')).forEach(k=>delete dp[k]);hmUI.createWidget(type,dp)};
 create(hmUI.widget.IMG,{x:0,y:0,src:'background.png'});
 const num=(type,x,y,w,prefix)=>create(hmUI.widget.TEXT_IMG,{x,y,w,h:30,font_array:font(prefix),h_space:0,align_h:hmUI.align.CENTER_H,type:hmUI.data_type[type],negative_image:prefix+'_minus.png',dot_image:prefix+'_dot.png'});
 num('HEART',299,259,43,'small');num('BATTERY',351,259,45,'small');num('WEATHER_CURRENT',131,250,60,'weather');num('STEP',85,331,70,'date');
 create(hmUI.widget.IMG,{x:233,y:327,src:'digital_colon.png'});
 create(hmUI.widget.IMG_TIME,{hour_zero:1,hour_startX:153,hour_startY:327,hour_array:font('digital'),hour_space:0,hour_align:hmUI.align.LEFT,minute_zero:1,minute_startX:249,minute_startY:327,minute_array:font('digital'),minute_space:0,minute_align:hmUI.align.LEFT,minute_follow:0,second_zero:1,second_startX:337,second_startY:337,second_array:font('small'),second_space:0,second_align:hmUI.align.LEFT,second_follow:0});
 create(hmUI.widget.IMG_WEEK,{x:161,y:308,week_en:Array.from({length:7},(_,i)=>'week_'+i+'.png'),week_sc:Array.from({length:7},(_,i)=>'week_'+i+'.png'),week_tc:Array.from({length:7},(_,i)=>'week_'+i+'.png')});
 create(hmUI.widget.IMG,{x:303,y:308,src:'date_dot.png'});
 create(hmUI.widget.IMG_DATE,{day_startX:284,day_startY:308,day_zero:1,day_space:0,day_align:hmUI.align.LEFT,day_en_array:font('date'),day_sc_array:font('date'),day_tc_array:font('date'),month_startX:309,month_startY:308,month_zero:1,month_space:0,month_align:hmUI.align.LEFT,month_en_array:font('date'),month_sc_array:font('date'),month_tc_array:font('date'),month_is_character:false,month_follow:0});
 create(hmUI.widget.TIME_POINTER,{hour_centerX:240,hour_centerY:240,hour_posX:20,hour_posY:101,hour_path:'hour.png',minute_centerX:240,minute_centerY:240,minute_posX:20,minute_posY:161,minute_path:'minute.png',second_centerX:240,second_centerY:240,second_posX:20,second_posY:180,second_path:'second.png'});
 create(hmUI.widget.IMG,{x:233,y:233,src:'cap.png'});
 [['steps',85,331,70,40,'STEP'],['music',70,80,55,35,'MUSIC'],['timer',325,355,80,40,'STOP_WATCH']].forEach(([n,x,y,w,h,t])=>{if(hmUI.data_type[t]!==undefined)hmUI.createWidget(hmUI.widget.IMG_CLICK,{x,y,w,h,src:'tap_'+n+'.png',type:hmUI.data_type[t],show_level:normal})});
 },onInit(){this.init_view()},build(){this.init_view()},onDestroy(){}});
 })(); }catch(e){console.log('Amazfit Green RU error',e)}
