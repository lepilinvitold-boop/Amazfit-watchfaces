// Validate the actual application bootstrap and widget lifecycle, not just syntax.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const root=__dirname;const assets=root+'/assets/';
function run(optionalFails=false){
 let bootstrap=false,face,widgets=[],logs=[],stepHandler,removed=false;
 const constants=new Proxy({},{get:(o,k)=>k in o?o[k]:(o[k]=k)});
 const current={current:{}};
 const step={current:8300,target:10000,addEventListener:(event,fn)=>stepHandler=fn,removeEventListener:()=>removed=true};
 const hmUI={widget:constants,data_type:constants,show_level:constants,align:constants,prop:constants,
  createWidget(type,props){assert(bootstrap,'Application app.js must run before widgets');assert(current.__globals__.px);const record={type,props:{...props},updates:[]};widgets.push(record);return {setProperty(k,v){record.updates.push([k,v]);record.props[k]=v}}}};
 const core={HmUtils:{Lang:function(){},getLanguage:()=>0,getPx:()=>x=>x,gettextFactory:()=>x=>x},App:config=>{bootstrap=true;return config},HmDomApi:function(){assert(bootstrap)},WidgetFactory:function(){},WatchFace:config=>(face=config)};
 const sensor={id:constants,event:constants,createSensor(id){if(optionalFails)throw Error('Optional sensors unavailable');return id==='STEP'?step:{year:2026}}};
 const sandbox={__$$hmAppManager$$__:{currentApp:current},DeviceRuntimeCore:core,hmUI,hmSensor:sensor,console:{log:(...x)=>logs.push(x)}};
 vm.runInNewContext(fs.readFileSync(root+'/app.js','utf8'),sandbox);assert(bootstrap);assert(current.app);
 vm.runInNewContext(fs.readFileSync(root+'/watchface.js','utf8'),sandbox);assert(face,'Watchface was not registered');face.onInit();assert(widgets.length>25,'Watchface did not render');let n=widgets.length;face.build();assert.equal(widgets.length,n,'Repeated build duplicated the screen');
 assert.equal(widgets[0].props.src,'background.png');assert.equal(widgets[1].props.src,'aod_background.png');
 for(const {type,props} of widgets){
  for(const [key,value] of Object.entries(props)){
   const values=Array.isArray(value)?value:[value];for(const v of values)if(typeof v==='string'&&v.endsWith('.png'))assert(fs.existsSync(assets+v),'Missing resource: '+v);
  }
  if(type==='TIME_POINTER'&&props.show_level==='ONAL_AOD')assert(!('second_path' in props),'Second hand remains in AOD');
  if(type==='IMG_TIME'&&props.show_level==='ONAL_AOD')assert(!('second_array' in props),'Digital seconds remain in AOD');
 }
 if(!optionalFails){
  assert(widgets.some(w=>w.updates.some(([key,val])=>key==='TEXT'&&val==='83u')),'Step goal percent incorrect');
  assert(widgets.some(w=>w.updates.some(([key,val])=>key==='TEXT'&&val==='26')),'Year incorrect');
  step.current=0;stepHandler();assert(widgets.some(w=>w.updates.some(([key,val])=>key==='TEXT'&&val==='0u')));
  step.target=0;stepHandler();assert(widgets.some(w=>w.updates.some(([key,val])=>key==='TEXT'&&val==='--')));
 }
 face.onDestroy();if(!optionalFails)assert(removed,'Listener leak');
 assert(!logs.some(x=>String(x[0]).includes('Amazfit Green RU error')),'Fatal runtime failure');
 return n;
}
console.log('Bootstrap, lifecycle, native paths, sensor refresh, missing-sensor fallback and AOD passed:',run(),run(true),'widgets');
