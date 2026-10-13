// Validate the actual application bootstrap and widget lifecycle, not just syntax.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const root=__dirname;const assets=root+'/assets/';
function run(optionalFails=false){
 let bootstrap=false,face,widgets=[],logs=[],stepHandler,removed=false,batteryHandler,batteryRemoved=false;
 const constants=new Proxy({},{get:(o,k)=>k in o?o[k]:(o[k]=k)});
 const current={current:{}};
 const step={current:8300,target:10000,addEventListener:(event,fn)=>stepHandler=fn,removeEventListener:()=>removed=true};
 const battery={current:48,addEventListener:(event,fn)=>batteryHandler=fn,removeEventListener:()=>batteryRemoved=true};
 const hmUI={widget:constants,data_type:constants,show_level:constants,align:constants,prop:constants,
  createWidget(type,props){assert(bootstrap,'Application app.js must run before widgets');assert(current.__globals__.px);const record={type,props:{...props},updates:[]};widgets.push(record);return {setProperty(k,v){record.updates.push([k,v]);record.props[k]=v},setEnable(v){record.props.enable=v}}}};
 const core={HmUtils:{Lang:function(){},getLanguage:()=>0,getPx:()=>x=>x,gettextFactory:()=>x=>x},App:config=>{bootstrap=true;return config},HmDomApi:function(){assert(bootstrap)},WidgetFactory:function(){},WatchFace:config=>(face=config)};
 const sensor={id:constants,event:constants,createSensor(id){if(optionalFails)throw Error('Optional sensors unavailable');return id==='STEP'?step:id==='BATTERY'?battery:{year:2026}}};
 const sandbox={__$$hmAppManager$$__:{currentApp:current},DeviceRuntimeCore:core,hmUI,hmSensor:sensor,console:{log:(...x)=>logs.push(x)}};
 vm.runInNewContext(fs.readFileSync(root+'/app.js','utf8'),sandbox);assert(bootstrap);assert(current.app);
 vm.runInNewContext(fs.readFileSync(root+'/watchface.js','utf8'),sandbox);assert(face,'Watchface was not registered');face.onInit();assert(widgets.length>25,'Watchface did not render');let n=widgets.length;face.build();assert.equal(widgets.length,n,'Repeated build duplicated the screen');
 const conditions=widgets.filter(w=>w.type==='IMG_LEVEL');assert.equal(conditions.length,2);conditions.forEach(w=>{assert.equal(w.props.image_length,29);assert.equal(w.props.type,'WEATHER_CURRENT');assert(w.props.image_array.every((n,i)=>n===(w.props.show_level==='ONAL_AOD'?'aod_':'')+'condition_'+i+'.png'))});
 assert.equal(widgets.filter(w=>w.type==='IMG'&&w.props.src==='status_percent.png').length,2,'Exactly one percent sign per indicator');
 assert(widgets.filter(w=>w.type==='TEXT_IMG').every(w=>!w.props.unit_en||w.props.unit_en==='degree.png'||w.props.unit_en==='aod_degree.png'),'Duplicate percent unit');
 assert(widgets.filter(w=>w.type==='TEXT_IMG').every(w=>!w.updates.some(([k,v])=>typeof v==='string'&&v.includes('u'))),'Duplicate percent marker');
 const hits=widgets.filter(w=>w.type==='IMG_CLICK'||w.type==='BUTTON');assert(hits.length>=60);
 const types=new Set(hits.filter(w=>w.type==='IMG_CLICK').map(w=>w.props.type));['HEART','STEP','DISTANCE','STRESS','ALARM_CLOCK','STOP_WATCH','COUNT_DOWN','CAL','BATTERY'].forEach(t=>assert(types.has(t),'Missing shortcut '+t));
 hits.forEach(w=>assert(w.props.x>=0&&w.props.y>=0&&w.props.x+w.props.w<=480&&w.props.y+w.props.h<=480,'Out-of-bounds shortcut'));
 assert.equal(widgets[0].props.src,'background.png');assert.equal(widgets[1].props.src,'aod_background.png');
 for(const {type,props} of widgets){
  for(const [key,value] of Object.entries(props)){
   const values=Array.isArray(value)?value:[value];for(const v of values)if(typeof v==='string'&&v.endsWith('.png'))assert(fs.existsSync(assets+v),'Missing resource: '+v);
  }
  if(type==='TIME_POINTER'&&props.show_level==='ONAL_AOD')assert(!('second_path' in props),'Second hand remains in AOD');
  if(type==='IMG_TIME'&&props.show_level==='ONAL_AOD')assert(!('second_array' in props),'Digital seconds remain in AOD');
 }
 if(!optionalFails){
  assert(widgets.some(w=>w.updates.some(([key,val])=>key==='TEXT'&&val==='83')),'Step goal percent incorrect');
  assert(widgets.some(w=>w.updates.some(([key,val])=>key==='TEXT'&&val==='26')),'Year incorrect');
  assert(widgets.some(w=>w.updates.some(([key,val])=>key==='TEXT'&&val==='48')),'Battery numeric rendering incorrect');
  battery.current=100;batteryHandler();assert(widgets.some(w=>w.updates.some(([key,val])=>key==='TEXT'&&val==='100')));
  step.current=0;stepHandler();assert(widgets.some(w=>w.updates.some(([key,val])=>key==='TEXT'&&val==='0')));
  step.target=0;stepHandler();assert(widgets.some(w=>w.updates.some(([key,val])=>key==='TEXT'&&val==='--')));
 }
 const lock=widgets.find(w=>w.type==='BUTTON'&&w.props.x===216&&w.props.y===403);assert(lock,'Lock button missing');lock.props.click_func();assert(face._locked);assert(widgets.find(w=>w.props.src==='shield.png').props.enable===true);assert(hits.filter(w=>w!==lock).every(w=>w.props.enable===false),'Locked shortcuts remain enabled');assert(widgets.some(w=>w.updates.some(([k,v])=>k==='MORE'&&v.src==='lock_closed.png')));lock.props.click_func();assert(!face._locked);assert(widgets.find(w=>w.props.src==='shield.png').props.enable===false);assert(hits.filter(w=>w!==lock).every(w=>w.props.enable===true),'Unlock did not restore shortcuts');
 face.onDestroy();if(!optionalFails)assert(removed&&batteryRemoved,'Listener leak');
 assert(!logs.some(x=>String(x[0]).includes('Amazfit Green RU error')),'Fatal runtime failure');
 return n;
}
console.log('Bootstrap, lifecycle, native paths, sensor refresh, missing-sensor fallback and AOD passed:',run(),run(true),'widgets');
