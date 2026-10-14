const fs=require('fs'),vm=require('vm'),assert=require('assert');
const root=process.argv[2];assert(root);
const constants=new Proxy({},{get:(o,k)=>o[k]??(o[k]=k)});
let face,widgets=[],launched=[],logs=[];
const router={SYSTEM_APP_MUSIC:8,SYSTEM_APP_ALTIMETER:32,SYSTEM_APP_SETTING:13,launchApp:p=>launched.push(p)};
const context={__$$R$$__:name=>{assert.equal(name,'@zos/router');return router}};
const current={current:{}};
const core={HmUtils:{Lang:function(){},getLanguage:()=>0,getPx:()=>x=>x,gettextFactory:()=>x=>x},App:c=>c,HmDomApi:function(){},WidgetFactory:function(){},WatchFace:c=>(face=c)};
const sandbox={__$$hmAppManager$$__:{currentApp:current},DeviceRuntimeCore:core,hmUI:{widget:constants,data_type:constants,show_level:constants,align:constants,prop:constants,createWidget(type,props){widgets.push({type,props});return {setProperty(){},setEnable(v){props.enable=v;}}}},hmSensor:{id:constants,event:constants,createSensor:()=>({current:60,addEventListener(){},removeEventListener(){}})},hmApp:{startApp:p=>launched.push(p)},console:{log:(...v)=>logs.push(v)}};
vm.runInNewContext(fs.readFileSync(root+'/app.js','utf8'),sandbox);assert(current.app);assert(current.__globals__.px);
vm.runInNewContext(fs.readFileSync(root+'/watchface/index.js','utf8'),sandbox);assert(face);face.onInit();const count=widgets.length;face.build();assert.equal(count,widgets.length);
for(const {props} of widgets)for(const v of Object.values(props).flat())if(typeof v==='string'&&v.endsWith('.png'))assert(fs.existsSync(root+'/assets/'+v),v);
const cells=widgets.filter(w=>w.type==='BUTTON');assert.equal(cells.length,10);
const grid=new Set();for(const {props:p} of cells){
 assert(p.enable===true,'Touch button disabled');assert(p.w>=44&&p.h>=38,'Narrow hit target');
 assert(Math.hypot(p.x+p.w/2-240,p.y+p.h/2-240)<210,'Bezel hit target remains');
 const b=fs.readFileSync(root+'/assets/'+p.normal_src);assert.equal(b.readUInt32LE(22),p.w);assert.equal(b.readUInt16LE(14),p.h);
 for(let y=p.y;y<p.y+p.h;y++)for(let x=p.x;x<p.x+p.w;x++){const k=x+','+y;assert(!grid.has(k),'Overlapping button regions');grid.add(k);}
 p.click_func();
}
assert.equal(launched.length,10);assert(launched.every(v=>v.native&&v.url));
['heart_app_Screen','StressHomeScreen','activityAppScreen','WeatherScreen','CountdownAppScreen','AlarmInfoScreen','ScheduleCalScreen','Settings_batteryManagerScreen'].forEach(url=>assert(launched.some(v=>v.url===url),url));
assert(!widgets.some(w=>w.type==='IMG_CLICK'),'Legacy clipped image taps remain');
const aod=widgets.filter(w=>w.props.show_level==='ONAL_AOD');assert(aod.length);assert(!aod.some(w=>w.type==='BUTTON'||w.type==='IMG_CLICK'));
assert(!aod.filter(w=>w.type==='TIME_POINTER').some(w=>'second_path' in w.props));face.onDestroy();assert(!logs.some(v=>String(v[0]).includes('Error')));
console.log('Package bootstrap, resources, AOD, independent tap cells, all inner native routes and idempotent build passed;',cells.length,'full-size touch buttons');

assert(widgets.some(w=>w.type==='TEXT_IMG'&&w.props.type==='STRESS'));assert(!widgets.some(w=>w.type==='TEXT_IMG'&&w.props.type==='CAL'));cells.find(w=>w.props.x===117).props.click_func();assert.equal(launched.at(-1).url,'AlarmInfoScreen');cells.find(w=>w.props.x===303).props.click_func();assert.equal(launched.at(-1).url,'CountdownAppScreen');
