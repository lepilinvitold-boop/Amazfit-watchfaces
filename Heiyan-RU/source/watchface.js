const moduleSlot = __$$hmAppManager$$__.currentApp.current;
moduleSlot.module = DeviceRuntimeCore.WatchFace({
  init_view() {
    if (this.built) return;
    this.built = true;
    const active = hmUI.show_level.ONLY_NORMAL;
    const idle = hmUI.show_level.ONLY_AOD ?? hmUI.show_level.ONAL_AOD;
    const widget = (kind, options, mode) =>
      hmUI.createWidget(hmUI.widget[kind], {...options, show_level: mode});
    const levels = [active, idle];
    const glyph = (mode, name, char) => (mode === idle ? 'aod_' : '') + name + '_' + char.charCodeAt(0) + '.png';
    const img = (src, x, y, mode) => widget('IMG', {src, x, y}, mode);
    const value = (type, name, x, y, w, mode, unit, signed = false) => {
      const options = {x, y, w, h: 28, align_h: hmUI.align.CENTER_H,
        type: hmUI.data_type[type], padding: false, h_space: 0,
        font_array: Array.from('0123456789', c => glyph(mode,name, c))};
      if (unit) options.unit_sc = options.unit_tc = options.unit_en = glyph(mode,name, unit);
      if (signed) options.negative_image = glyph(mode,name, '−');
      if (type === 'DISTANCE') {
        options.dot_image = glyph(mode,name, ',');
        options.unit_sc = options.unit_tc = options.unit_en = mode === idle ? 'aod_km.png' : 'km.png';
      }
      if (options.type !== undefined) widget('TEXT_IMG', options, mode);
    };
    const label = (text, x, y, w, size, mode) => widget('TEXT', {
      text, x, y, w, h: size+5, text_size: size, color: mode === idle ? 0x66686b : 0xebedf0,
      align_h: hmUI.align.CENTER_H, align_v: hmUI.align.CENTER_V
    }, mode);
    const rows = [];
    for (const mode of levels) {
      img(mode === active ? 'dial.png' : 'aod.png', 0, 0, mode);
      widget('IMG_LEVEL', {x:221,y:65,w:38,h:35, image_length:29,
        image_array:Array.from({length:29},(_,i)=>(mode === idle ? 'aod_' : '')+'weather_'+i+'.png'),
        type:hmUI.data_type.WEATHER_CURRENT}, mode);
      value('WEATHER_CURRENT','current',201,99,78,mode,'°',true);
      value('WEATHER_LOW','small',185,136,51,mode,'°',true);
      value('WEATHER_HIGH','small',244,136,51,mode,'°',true);
      label('/',234,135,12,15,mode);
      value('HEART','value',99,98,62,mode);
      value('BATTERY','value',317,98,66,mode,'%');
      value('CAL','value',99,321,62,mode);
      value('STRESS','value',317,321,66,mode);
      value('STEP','value',188,340,104,mode);
      value('DISTANCE','small',184,384,112,mode);
      const date = label('',66,211,114,25,mode);
      const day = label('',66,245,114,19,mode);
      const time = label('',289,211,132,23,mode);
      widget('IMG_STATUS',{x:315,y:247,src:'0068.png',type:hmUI.system_status.CLOCK},mode);
      label('—:—',332,245,55,16,mode);
      rows.push({mode,date,day,time});
      for (const [part,src,px,py] of [['hour','0064',37,250],['minute','0065',37,247]]) {
        widget('TIME_POINTER',{
          [part+'_path']:(mode === idle ? 'aod_'+Number(src) : src)+'.png',
          [part+'_centerX']:240,[part+'_centerY']:240,
          [part+'_posX']:px,[part+'_posY']:py
        }, mode);
      }
    }
    const smooth = typeof timer !== 'undefined' && typeof timer.createTimer === 'function';
    const seconds = smooth
      ? widget('IMG',{x:0,y:0,w:480,h:480,src:'0066.png',center_x:240,center_y:240,
        pos_x:204,pos_y:-8,angle:0,enable:false},active)
      : widget('TIME_POINTER',{second_path:'0066.png',second_centerX:240,second_centerY:240,
        second_posX:36,second_posY:248},active);
    const pad = number => ('0'+number).slice(-2);
    let lastSecond;
    let clock;
    try { clock = hmSensor.createSensor(hmSensor.id.TIME); } catch (error) {}
    const update = () => {
      const stamp = Date.now();
      if (smooth) seconds.setProperty(hmUI.prop.ANGLE,(stamp % 60000)*.006);
      const second = Math.floor(stamp/1000);
      if (second === lastSecond) return;
      lastSecond = second;
      const now = new Date(stamp);
      const week = ['ВСК','ПНД','ВТР','СРД','ЧТВ','ПТН','СБТ'];
      const hhmm = pad(clock?.hour ?? now.getHours())+':'+pad(clock?.minute ?? now.getMinutes());
      for (const row of rows) {
        row.date.setProperty(hmUI.prop.TEXT,pad(clock?.day ?? now.getDate())+'.'+pad(clock?.month ?? now.getMonth()+1));
        row.day.setProperty(hmUI.prop.TEXT,week[(clock?.week ?? now.getDay()) % 7]);
        row.time.setProperty(hmUI.prop.TEXT,hhmm+(row.mode === active ? ':'+pad(clock?.second ?? now.getSeconds()) : ''));
      }
    };
    this.stop = () => {
      if (this.tick !== undefined) timer.stopTimer(this.tick);
      this.tick = undefined;
    };
    const resume = () => {
      this.stop();
      update();
      if (smooth) this.tick = timer.createTimer(50,50,update,{});
    };
    if (clock) {
      this.clock = clock;
      this.event = clock.event ? clock.event.MINUTEEND : hmSensor.event.MINUTEEND;
      this.refresh = update;
      clock.addEventListener(this.event,update);
    }
    widget('WIDGET_DELEGATE',{resume_call:resume,pause_call:this.stop},active);
    resume();
    for (const [x,y,w,h,screen,metric] of [
      [173,54,134,122,'WeatherScreen'], [92,72,74,58,'heart_app_Screen'],
      [314,72,74,58,'Settings_batteryManagerScreen'], [92,316,74,71,null,'CAL'],
      [314,316,74,71,'StressHomeScreen'], [174,307,132,69,null,'STEP'],
      [182,377,116,44,null,'DISTANCE'], [53,204,138,69,'ScheduleCalScreen'],
      [295,211,35,31,'AlarmInfoScreen'], [330,211,43,31,'StopWatchScreen'],
      [373,211,42,31,'CountdownAppScreen'], [303,243,109,33,'AlarmInfoScreen']
    ]) {
      const bounds = {x,y,w,h,enable:true};
      const hit = metric
        ? widget('IMG_CLICK',{...bounds,src:'hit.png',type:hmUI.data_type[metric]},active)
        : widget('BUTTON',{...bounds,text:'',normal_src:'hit.png',press_src:'hit.png',
            click_func:()=>hmApp.startApp({url:screen,native:true})},active);
      hit.setEnable(true);
    }
  },
  build() { this.init_view(); },
  onDestroy() {
    if (this.stop) this.stop();
    if (this.clock) this.clock.removeEventListener(this.event,this.refresh);
  }
});
