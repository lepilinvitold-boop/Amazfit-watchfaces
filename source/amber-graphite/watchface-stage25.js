try { (() => {
const slot = __$$hmAppManager$$__.currentApp.current;
slot.module = DeviceRuntimeCore.WatchFace({
  init_view() {
    if (this.built) return;
    this.built = true;
    const normal = hmUI.show_level.ONLY_NORMAL;
    const aod = hmUI.show_level.ONAL_AOD || hmUI.show_level.ONLY_AOD;
    const safe = (kind, options, mode) => {
      try { return hmUI.createWidget(hmUI.widget[kind], {...options, show_level: mode}); }
      catch (error) { console.log('Amber widget', kind, error); return {setProperty(){}, setEnable(){}}; }
    };
    const image = (src, x, y, mode) => safe('IMG', {src, x, y}, mode);
    image('dial.png', 0, 0, normal);
    image('aod.png', 0, 0, aod);
    const rows = [];
    const text = (x, y, w, h, size, mode, color) => safe('TEXT', {
      x, y, w, h, text: '', text_size: size, color,
      align_h: hmUI.align.CENTER_H, align_v: hmUI.align.CENTER_V
    }, mode);
    const weatherNumber = (type, size, x, y, w, mode, unit) => {
      const prefix = mode === aod ? 'aod_' : '';
      const options = {x, y, w, h: size === 'large' ? 32 : 23,
        type: hmUI.data_type[type], align_h: hmUI.align.CENTER_H, h_space: 0,
        font_array: Array.from({length:10}, (_, i) => prefix+size+'_'+i+'.png'),
        negative_image: prefix+size+'_minus.png', dot_image: prefix+size+'_dot.png'};
      if (unit) options.unit_sc = options.unit_tc = options.unit_en = prefix+size+'_degree.png';
      safe('TEXT_IMG', options, mode);
    };
    for (const mode of [normal, aod]) {
      const prefix = mode === aod ? 'aod_' : '';
      const color = mode === aod ? 0x756f59 : 0xf0dfad;
      const label = (x,y,w,h,size) => text(x,y,w,h,size,mode,color);
      safe('IMG_LEVEL', {x:164,y:65,w:48,h:33,image_length:29,
        image_array:Array.from({length:29},(_,i)=>prefix+'weather_'+i+'.png'),
        type:hmUI.data_type.WEATHER_CURRENT},mode);
      weatherNumber('WEATHER_CURRENT','large',220,63,100,mode,true);
      weatherNumber('WEATHER_LOW','small',214,92,54,mode,true);
      weatherNumber('WEATHER_HIGH','small',277,92,54,mode,true);
      const slash=label(265,92,12,23,17); slash.setProperty(hmUI.prop.TEXT,'/');
      image(prefix+'steps_icon.png',161,137,mode);
      const step=label(190,139,136,34,30);
      const distance=label(171,174,138,24,22);
      image(prefix+'heart_icon.png',78,207,mode);
      const heart=label(105,207,65,35,30);
      const heartRange=label(69,252,94,26,22);
      const date=label(306,211,118,35,30);
      const month=label(309,253,112,27,22);
      const clock=label(179,302,122,56,38);
      const calories=label(77,300,86,35,27);
      const stress=label(317,300,86,35,27);
      label(82,336,80,23,18).setProperty(hmUI.prop.TEXT,'ккал');
      label(320,336,69,23,16).setProperty(hmUI.prop.TEXT,'стресс');
      image(prefix+'training_icon.png',92,139,mode);
      image(prefix+'handset_icon.png',360,139,mode);
      image(prefix+'battery_new.png',167,386,mode);
      const battery=label(210,382,110,39,30);
      rows.push({mode,step,distance,heart,heartRange,calories,stress,date,month,clock,battery});
      for (const [part,px,py] of [['hour',37,250],['minute',34,227]])
        safe('TIME_POINTER',{[part+'_path']:prefix+part+'.png',
          [part+'_centerX']:240,[part+'_centerY']:240,
          [part+'_posX']:px,[part+'_posY']:py},mode);
      if (mode === normal) safe('TIME_POINTER',{second_path:'second.png',second_centerX:240,
        second_centerY:240,second_posX:36,second_posY:248},normal);
      image(prefix+'hub_alarm.png',218,218,mode);
      safe('IMG_STATUS',{x:218,y:218,src:prefix+'hub_alarm_on.png',
        type:hmUI.system_status.CLOCK},mode);
    }
    const sensor = name => { try { return hmSensor.createSensor(hmSensor.id[name]); }
      catch (error) { console.log('Amber sensor',name,error); return null; } };
    const sensors = {};
    for (const name of ['STEP','DISTANCE','HEART','CALORIE','BATTERY','STRESS']) sensors[name]=sensor(name);
    const get = (name, property='current') => {
      try { const s=sensors[name], v=s && (s[property] === undefined ? s.current : s[property]);
        return Number.isFinite(v) && v>=0 ? v : undefined; }
      catch (_) { return undefined; }
    };
    const pad = n => ('0'+n).slice(-2);
    const week=['вск','пнд','втр','срд','чтв','птн','сбт'];
    const months=['Январь','Февраль','Март','Апрель','Май','Июнь',
      'Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь'];
    const refresh = () => {
      try {
        const now=new Date(), time=pad(now.getHours())+':'+pad(now.getMinutes());
        const steps=get('STEP');
        const dailyDistance=get('DISTANCE');
        const meters=dailyDistance===undefined?get('DISTANCE','distance'):dailyDistance;
        const bpm=get('HEART','last'), cal=get('CALORIE'), charge=get('BATTERY'), stress=get('STRESS');
        let heartMin=Infinity, heartMax=0;
        try { const samples=sensors.HEART && sensors.HEART.today;
          if (Array.isArray(samples)) for (const sample of samples)
            if (Number.isFinite(sample) && sample>0) {heartMin=Math.min(heartMin,sample);heartMax=Math.max(heartMax,sample);}
        } catch (_) {}
        for (const row of rows) {
          const dim=row.mode===aod;
          row.clock.setProperty(hmUI.prop.TEXT,time);
          row.date.setProperty(hmUI.prop.MORE,{text:now.getDate()+' '+week[now.getDay()],
            color:now.getDay()===0||now.getDay()===6?(dim?0x743330:0xe5544c):(dim?0x756f59:0xf0dfad)});
          row.month.setProperty(hmUI.prop.TEXT,months[now.getMonth()]);
          row.step.setProperty(hmUI.prop.MORE,{text:steps===undefined?'—':String(Math.round(steps)),
            color:steps>=10000?(dim?0x36552c:0x83b86d):(dim?0x756f59:0xf0dfad)});
          row.distance.setProperty(hmUI.prop.TEXT,meters===undefined?'— км':(meters/1000).toFixed(1).replace('.',',')+' км');
          row.heart.setProperty(hmUI.prop.MORE,{text:bpm>0?String(Math.round(bpm)):'—',
            color:bpm>100?(dim?0x743330:0xe5544c):(dim?0x756f59:0xf0dfad)});
          row.heartRange.setProperty(hmUI.prop.TEXT,heartMax?Math.round(heartMin)+'–'+Math.round(heartMax):'—–—');
          row.calories.setProperty(hmUI.prop.TEXT,cal===undefined?'—':String(Math.round(cal)));
          row.stress.setProperty(hmUI.prop.TEXT,stress===undefined?'—':String(Math.round(stress)));
          row.battery.setProperty(hmUI.prop.MORE,{text:charge===undefined?'—%':Math.round(charge)+'%',
            color:charge<20?(dim?0x743330:0xe5544c):(dim?0x756f59:0xf0dfad)});
        }
      } catch (error) { console.log('Amber refresh',error); }
    };
    refresh();
    this.stop=()=>{if(this.timerId!==undefined){timer.stopTimer(this.timerId);this.timerId=undefined;}};
    this.resume=()=>{this.stop();refresh();this.timerId=timer.createTimer(1000,1000,refresh,{});};
    try { safe('WIDGET_DELEGATE',{resume_call:this.resume,pause_call:this.stop},normal);this.resume(); }
    catch (error) { console.log('Amber timer',error); }
    for (const [x,y,w,h,screen,metric] of [
      [155,62,180,67,'WeatherScreen',null],
      [163,138,154,34,null,'STEP'],[168,173,144,24,null,'DISTANCE'],
      [58,205,110,39,null,'HEART'],[58,251,109,28,null,'HEART'],
      [305,207,120,35,'ScheduleCalScreen',null],
      [85,132,42,42,'SportListScreen',null],[309,252,112,28,'ScheduleCalScreen',null],
      [353,132,42,42,'PhoneHomeScreen',null],
      [218,218,44,44,null,'ALARM_CLOCK'],[165,383,151,39,'Settings_batteryManagerScreen',null],
      [61,299,88,71,null,'CAL'],[331,299,88,71,'StressHomeScreen',null],
      [176,307,64,55,'StopWatchScreen',null],
      [240,307,64,55,'CountdownAppScreen',null]
    ]) {
      const box={x,y,w,h,enable:true};
      const hit=metric?safe('IMG_CLICK',{...box,src:'hit.png',type:hmUI.data_type[metric]},normal)
        :safe('BUTTON',{...box,text:'',normal_src:'hit.png',press_src:'hit.png',
            click_func:()=>hmApp.startApp({url:screen,native:true})},normal);
    }
  },
  onInit(){this.init_view();},build(){this.init_view();},
  onDestroy(){if(this.stop)this.stop();}
});
})() } catch(error) { console.log('Amber Stage 5',error); }
