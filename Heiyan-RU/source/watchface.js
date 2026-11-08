try { (() => {
const moduleSlot = __$$hmAppManager$$__.currentApp.current;
moduleSlot.module = DeviceRuntimeCore.WatchFace({
  init_view() {
    if (this.built) return;
    this.built = true;
    const active = hmUI.show_level.ONLY_NORMAL;
    const idle = hmUI.show_level.ONAL_AOD || hmUI.show_level.ONLY_AOD;
    const widget = (kind, options, mode) => {
      try {
        return hmUI.createWidget(hmUI.widget[kind], Object.assign({}, options, {show_level: mode}));
      } catch (error) {
        console.log('Heiyan widget '+kind,error);
        return {setProperty(){},setEnable(){}};
      }
    };
    widget('IMG',{src:'dial.png',x:0,y:0,w:480,h:480},active);
    widget('IMG',{src:'aod.png',x:0,y:0,w:480,h:480},idle);
    const levels = [active, idle];
    const glyph = (mode, name, char) => (mode === idle ? 'aod_' : '') + name + '_' + char.charCodeAt(0) + '.png';
    const img = (src, x, y, mode) => widget('IMG', {src, x, y}, mode);
    const value = (type, name, x, y, w, mode, unit, signed = false) => {
      const options = {x, y, w, h: name === 'digital' ? 38 : 32, align_h: hmUI.align.CENTER_H,
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
    const label = (text, x, y, w, size, mode, color = mode === idle ? 0x66686b : 0xebedf0) => widget('TEXT', {
      text, x, y, w, h: size+5, text_size: size, color,
      align_h: hmUI.align.CENTER_H, align_v: hmUI.align.CENTER_V
    }, mode);
    const rows = [];
    const stressLabels = [];
    for (const mode of levels) {
      widget('IMG_LEVEL', {x:221,y:60,w:38,h:35, image_length:29,
        image_array:Array.from({length:29},(_,i)=>(mode === idle ? 'aod_' : '')+'weather_'+i+'.png'),
        type:hmUI.data_type.WEATHER_CURRENT}, mode);
      value('WEATHER_CURRENT','digital',196,90,88,mode,'°',true);
      value('WEATHER_LOW','small',184,137,53,mode,'°',true);
      value('WEATHER_HIGH','small',243,137,53,mode,'°',true);
      label('/',234,135,12,18,mode);
      value('HEART','value',104,127,62,mode);
      value('BATTERY','value',317,127,66,mode);
      value('CAL','value',104,310,62,mode);
      stressLabels.push(label('—',314,310,66,20,mode));
      value('STEP','digital',185,337,110,mode);
      value('DISTANCE','small',184,380,112,mode);
      const cells = (x,count) => Array.from({length:count},(_,i)=>
        img(glyph(mode,'digital',' '),x+22*i,225,mode));
      const date = cells(57,6);
      const time = cells(306,5);
      const prefix = mode === idle ? 'aod_' : '';
      img(prefix+'alarm.png',226,195,mode);
      widget('IMG_STATUS',{x:226,y:195,src:prefix+'alarm_on.png',type:hmUI.system_status.CLOCK},mode);
      rows.push({mode,date,time});
      for (const [part,src,px,py] of [['hour','0064',37,250],['minute','0065',37,247]]) {
        widget('TIME_POINTER',{
          [part+'_path']:(mode === idle ? 'aod_'+Number(src) : src)+'.png',
          [part+'_centerX']:240,[part+'_centerY']:240,
          [part+'_posX']:px,[part+'_posY']:py
        }, mode);
      }
    }
    const refreshStress = () => {
      const value = this.stress && this.stress.current;
      const text = Number.isFinite(value) && value > 0 && value <= 100 ? String(Math.round(value)) : '—';
      for (const target of stressLabels) target.setProperty(hmUI.prop.TEXT,text);
    };
    try {
      this.stress = hmSensor.createSensor(hmSensor.id.STRESS);
      this.stressRefresh = refreshStress;
      this.stress.addEventListener(hmSensor.event.CHANGE,refreshStress);
    } catch (error) {}
    refreshStress();
    const smooth = typeof timer !== 'undefined' && typeof timer.createTimer === 'function';
    const seconds = smooth
      ? widget('IMG',{x:0,y:0,w:480,h:480,src:'0066.png',center_x:240,center_y:240,
        pos_x:204,pos_y:-8,angle:0,enable:false},active)
      : widget('TIME_POINTER',{second_path:'0066.png',second_centerX:240,second_centerY:240,
        second_posX:36,second_posY:248},active);
    const pad = number => ('0'+number).slice(-2);
    let lastSecond;
    let lastDisplay;
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
      const hhmm = pad(clock ? clock.hour : now.getHours())+':'+pad(clock ? clock.minute : now.getMinutes());
      const weekday = (clock ? clock.week : now.getDay()) % 7;
      const text = (' '+(clock ? clock.day : now.getDate())+' '+week[weekday]).slice(-6);
      if (lastDisplay === text+hhmm) return;
      lastDisplay = text+hhmm;
      for (const row of rows) {
        const set = (cells, chars, name) => cells.forEach((cell,i)=>
          cell.setProperty(hmUI.prop.SRC,glyph(row.mode,name,chars[i])));
        set(row.date,text,weekday === 0 || weekday === 6 ? 'weekend' : 'digital');
        set(row.time,hhmm,'digital');
      }
    };
    this.stop = () => {
      if (this.tick !== undefined) timer.stopTimer(this.tick);
      this.tick = undefined;
    };
    const resume = () => {
      this.stop();
      refreshStress();
      update();
      if (smooth) this.tick = timer.createTimer(50,50,update,{});
    };
    if (clock && typeof clock.addEventListener === "function") {
      this.clock = clock;
      this.event = clock.event ? clock.event.MINUTEEND : hmSensor.event.MINUTEEND;
      this.refresh = update;
      try { clock.addEventListener(this.event,update); } catch (error) { console.log("Heiyan clock",error); }
    }
    widget('WIDGET_DELEGATE',{resume_call:resume,pause_call:this.stop},active);
    resume();
    for (const [x,y,w,h,screen,metric] of [
      [173,54,134,122,'WeatherScreen'], [94,96,78,65,'heart_app_Screen'],
      [311,96,78,65,'Settings_batteryManagerScreen'], [94,305,78,70,null,'CAL'],
      [310,305,78,70,'StressHomeScreen'], [174,307,132,69,null,'STEP'],
      [182,377,116,44,null,'DISTANCE'], [53,204,138,69,'ScheduleCalScreen'],
      [303,221,58,47,'StopWatchScreen'], [361,221,59,47,'CountdownAppScreen'],
      [222,192,36,34,'AlarmInfoScreen']
    ]) {
      const bounds = {x,y,w,h,enable:true};
      const hit = metric
        ? widget('IMG_CLICK',{...bounds,src:'hit.png',type:hmUI.data_type[metric]},active)
        : widget('BUTTON',{...bounds,text:'',normal_src:'hit.png',press_src:'hit.png',
            click_func:()=>hmApp.startApp({url:screen,native:true})},active);
      hit.setEnable(true);
    }
  },
  onInit() { this.init_view(); },
  build() { this.init_view(); },
  onDestroy() {
    if (this.stop) this.stop();
    if (this.stress && this.stressRefresh) this.stress.removeEventListener(hmSensor.event.CHANGE,this.stressRefresh);
    if (this.clock) this.clock.removeEventListener(this.event,this.refresh);
  }
});

})(); } catch (error) { console.log("Heiyan module",error); }
