const fs=require('fs'),vm=require('vm'),assert=require('assert');
const root=process.argv[2];assert(root);
const constants=new Proxy({},{get:(o,k)=>o[k]??(o[k]=k)});
let face,widgets=[],launched=[],logs=[];
const router={SYSTEM_APP_MUSIC:8,SYSTEM_APP_ALTIMETER:32,SYSTEM_APP_SETTING:13,launchApp:p=>launched.push(p)};
const context={__$$R$$__:name=>{assert.equal(name,'@zos/router');return router}};
const current={__globals__:{__$$G$$__:context},current:{__globals__:{__$$G$$__:context}}};
const core={LifeCycle:{},HmUtils:{Lang:function(){},getLanguage:()=>0,getPx:()=>x=>x,gettextFactory:()=>x=>x},App:c=>c,HmDomApi:function(){},WidgetFactory:function(){},WatchFace:c=>(face=c)};
const sandbox={__$$hmAppManager$$__:{currentApp:current},DeviceRuntimeCore:core,hmUI:{widget:constants,data_type:constants,show_level:constants,align:constants,prop:constants,createWidget(type,props){widgets.push({type,props});return {setProperty(){},setEnable(){}}}},hmSensor:{id:constants,event:constants,createSensor:()=>({current:60,addEventListener(){},removeEventListener(){}})},hmApp:{startApp(){}},console:{log:(...v)=>logs.push(v)}};
vm.runInNewContext(fs.readFileSync(root+'/app.js','utf8'),sandbox);assert(current.app);assert(current.__globals__.__$$G$$__);
vm.runInNewContext(fs.readFileSync(root+'/watchface/index.js','utf8'),sandbox);assert(face);face.onInit();const count=widgets.length;face.build();assert.equal(count,widgets.length);
for(const {props} of widgets)for(const v of Object.values(props).flat())if(typeof v==='string'&&v.endsWith('.png'))assert(fs.existsSync(root+'/assets/'+v),v);
const cells=widgets.filter(w=>w.props.normal_src==='tap_bezel.png');assert(cells.length>20);
const grid=new Set();for(const {props:p} of cells){
 for(let y=p.y;y<p.y+p.h;y++)for(let x=p.x;x<p.x+p.w;x++){
  const r=Math.hypot(x+.5-240,y+.5-240);assert(r>=213&&r<=238);const key=x+','+y;assert(!grid.has(key),'Overlapping bezel targets');grid.add(key);
 }
 p.click_func();
}
assert.deepEqual([...new Set(launched.map(v=>v.appId))].sort((a,b)=>a-b),[8,13,32]);assert(launched.every(v=>v.native));
const aod=widgets.filter(w=>w.props.show_level==='ONAL_AOD');assert(aod.length);assert(!aod.some(w=>w.type==='BUTTON'||w.type==='IMG_CLICK'));
assert(!aod.filter(w=>w.type==='TIME_POINTER').some(w=>'second_path' in w.props));face.onDestroy();assert(!logs.some(v=>String(v[0]).includes('Error')));
console.log('Package bootstrap, resources, AOD, independent tap cells, three system routes and idempotent build passed;',cells.length,'bezel cells');
