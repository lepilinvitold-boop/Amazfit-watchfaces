const fs=require('fs'),vm=require('vm'),assert=require('assert');
const root=process.argv[2];assert(root);
const constants=new Proxy({},{get:(o,k)=>o[k]??(o[k]=k)});
let face;const widgets=[],sensors={},launched=[],logs=[];
const current={current:{}};
const core={HmUtils:{Lang:function(){},getLanguage:()=>0,getPx:()=>x=>x,gettextFactory:()=>x=>x},App:c=>c,HmDomApi:function(){},WidgetFactory:function(){},WatchFace:c=>(face=c)};
const sandbox={__$$hmAppManager$$__:{currentApp:current},DeviceRuntimeCore:core,hmUI:{widget:constants,data_type:constants,show_level:constants,align:constants,prop:constants,createWidget(type,props){const w={type,props:{...props},visible:true,setProperty(k,v){if(k==='MORE')Object.assign(this.props,v);else if(k==='VISIBLE')this.visible=v;else this.props[k]=v;},setEnable(v){this.props.enable=v;}};widgets.push(w);return w;}},hmSensor:{id:constants,event:constants,createSensor(id){return sensors[id]??(sensors[id]={current:60,last:72,target:400,today:[0,65,72,NaN],events:{},addEventListener(e,f){(this.events[e]??=[]).push(f)},removeEventListener(e,f){this.events[e]=this.events[e].filter(v=>v!==f)},emit(e){(this.events[e]||[]).forEach(f=>f())}})}},hmApp:{startApp:p=>launched.push(p)},console:{log:(...v)=>logs.push(v)}};
vm.runInNewContext(fs.readFileSync(root+'/app.js','utf8'),sandbox);
vm.runInNewContext(fs.readFileSync(root+'/watchface/index.js','utf8'),sandbox);assert(face);face.onInit();const count=widgets.length;face.build();assert.equal(count,widgets.length);
for(const {props} of widgets)for(const v of Object.values(props).flat())if(typeof v==='string'&&v.endsWith('.png'))assert(fs.existsSync(root+'/assets/'+v),v);
const cells=widgets.filter(w=>['BUTTON','IMG_CLICK'].includes(w.type));assert.equal(cells.length,13);
const grid=new Set();for(const {props:p} of cells){assert(p.enable);const b=fs.readFileSync(root+'/assets/'+(p.src||p.normal_src));assert.equal(b.readUInt32LE(22),p.w);assert.equal(b.readUInt16LE(14),p.h);for(let y=p.y;y<p.y+p.h;y++)for(let x=p.x;x<p.x+p.w;x++){const k=x+','+y;assert(!grid.has(k),'overlap');grid.add(k)}if(p.click_func)p.click_func();}
for(const [type,x,y] of [['CAL',60,253],['STEP',308,182],['DISTANCE',308,253]])assert(cells.some(w=>w.type==='IMG_CLICK'&&w.props.type===type&&w.props.x===x&&w.props.y===y),'wrong metric route '+type);
assert.equal(launched.length,10);assert(!launched.some(v=>v.url==='activityAppScreen'));
const aod=widgets.filter(w=>w.props.show_level==='ONAL_AOD');assert(aod.length);assert(!aod.some(w=>['BUTTON','IMG_CLICK'].includes(w.type)));assert(!aod.filter(w=>w.type==='TIME_POINTER').some(w=>'second_path'in w.props));
const data=t=>widgets.filter(w=>w.type==='TEXT_IMG'&&w.props.type===t);
const check=(t,valid)=>{assert.equal(data(t).length,2);data(t).forEach(w=>assert.equal(w.visible,valid));};
check('HEART',true);check('STRESS',true);
for(const value of [0,-1,NaN,Infinity,undefined,256]){sensors.HEART.last=value;sensors.HEART.emit('LAST');check('HEART',false);widgets.filter(w=>w.type==='IMG_LEVEL'&&w.props.type==='HEART').forEach(w=>assert(!w.visible));}
sensors.HEART.last=89;sensors.HEART.emit('LAST');check('HEART',true);
for(const value of [0,-1,NaN,Infinity,undefined,101]){sensors.STRESS.current=value;sensors.STRESS.emit('CHANGE');check('STRESS',false)}
sensors.STRESS.current=24;sensors.STRESS.emit('CHANGE');check('STRESS',true);
// Daily counters are native and valid zero must stay visible.
sensors.CALORIE.current=0;sensors.CALORIE.emit('CHANGE');check('CAL',true);check('STEP',true);check('DISTANCE',true);
sensors.HEART.last=0;widgets.find(w=>w.type==='WIDGET_DELEGATE').props.resume_call();check('HEART',false);
face.onDestroy();for(const s of Object.values(sensors))for(const list of Object.values(s.events))assert.equal(list.length,0);
assert.equal(logs.length,0,JSON.stringify(logs));console.log('PASS: native metric targets, 13 nonoverlapping full-size hit assets; invalid/recovery/resume normal+AOD; legitimate zero counters; cleanup and resources.');
