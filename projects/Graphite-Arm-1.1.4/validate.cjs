const fs=require('fs'),vm=require('vm'),assert=require('assert');
const root=process.argv[2],constants=new Proxy({},{get:(o,k)=>o[k]??(o[k]=k)});let face;const widgets=[],logs=[],launched=[],sensors={};
const activeTimers=new Map();let timerId=0;const sandbox={timer:{createTimer(delay,repeat,cb){assert.equal(repeat,50);activeTimers.set(++timerId,cb);return timerId},stopTimer(id){activeTimers.delete(id)}},__$$hmAppManager$$__:{currentApp:{current:{}}},DeviceRuntimeCore:{HmUtils:{Lang:function(){},getLanguage:()=>0,getPx:()=>x=>x,gettextFactory:()=>x=>x},App:c=>c,WatchFace:c=>(face=c)},hmUI:{widget:constants,data_type:constants,show_level:constants,align:constants,prop:constants,createWidget(type,props){const w={type,props:{...props},visible:true,setProperty(k,v){if(k==='VISIBLE')this.visible=v;else if(k==='MORE')Object.assign(this.props,v);else this.props[({SRC:'src',ANGLE:'angle',POS_X:'pos_x',POS_Y:'pos_y'})[k]||k]=v},setEnable(v){this.props.enable=v}};widgets.push(w);return w}},hmSensor:{id:constants,event:constants,createSensor(id){return sensors[id]??(sensors[id]={last:72,current:71,target:100,totalMinutes:455,updateInfo(){this.updateCount=(this.updateCount||0)+1},getTotalTime(){return this.totalMinutes},events:{},addEventListener(e,f){(this.events[e]??=[]).push(f)},removeEventListener(e,f){assert(this.events[e].includes(f));this.events[e]=this.events[e].filter(v=>v!==f);if(!this.events[e].length)delete this.events[e]}})}},hmApp:{startApp:p=>launched.push(p)},console:{log:(...args)=>logs.push(args)}};
vm.runInNewContext(fs.readFileSync(root+'/app.js','utf8'),sandbox);vm.runInNewContext(fs.readFileSync(root+'/watchface/index.js','utf8'),sandbox);assert(face);face.onInit();const count=widgets.length;face.build();assert.equal(count,widgets.length);assert.equal(logs.length,0,JSON.stringify(logs));
for(const {props} of widgets)for(const v of Object.values(props).flat())if(typeof v==='string'&&v.endsWith('.png'))assert(fs.existsSync(root+'/assets/'+v),v);
const cells=widgets.filter(w=>['BUTTON','IMG_CLICK'].includes(w.type));assert.equal(cells.length,21);const pixels=new Set();
for(const {props:p} of cells){assert(p.enable);assert.equal(p.show_level,'ONLY_NORMAL');const b=fs.readFileSync(root+'/assets/'+(p.src||p.normal_src));assert.equal(b.readUInt32LE(22),p.w);assert.equal(b.readUInt16LE(14),p.h);for(let y=p.y;y<p.y+p.h;y++)for(let x=p.x;x<p.x+p.w;x++){assert(!pixels.has(x+','+y),'overlap');pixels.add(x+','+y)}if(p.click_func)p.click_func()}
assert.deepEqual(cells.filter(w=>w.type==='IMG_CLICK').map(w=>w.props.type).sort(),['READINESS','READINESS','READINESS','CAL','CAL','CAL','DISTANCE','DISTANCE','DISTANCE','STEP'].sort());assert(launched.some(v=>v.url==='StopWatchScreen'));assert(launched.some(v=>v.url==='CountdownAppScreen'));assert(launched.some(v=>v.url==='AlarmInfoScreen'));
const axis=cells.find(w=>w.props.x===220&&w.props.y===220);const pointers=widgets.filter(w=>w.type==='TIME_POINTER'||w.props.src==='second.png');assert(pointers.every(w=>!w.visible));axis.props.click_func();assert(pointers.every(w=>w.visible));axis.props.click_func();assert(pointers.every(w=>!w.visible));axis.props.click_func();
const aod=widgets.filter(w=>w.props.show_level==='ONAL_AOD');assert(aod.length>15);assert(aod.every(w=>!['BUTTON','IMG_CLICK'].includes(w.type)));assert(aod.filter(w=>w.type==='TIME_POINTER').every(w=>!('second_path'in w.props)));
const hearts=widgets.filter(w=>w.type==='TEXT_IMG'&&w.props.type==='HEART');assert.equal(hearts.length,2);for(const v of [0,-1,undefined,NaN,Infinity,300,89]){sensors.HEART.last=v;sensors.HEART.events.LAST.forEach(f=>f());hearts.forEach(w=>assert.equal(w.visible,v===89))}
for(const w of widgets.filter(w=>w.type==='IMG_TIME'))assert(!Object.keys(w.props).some(k=>k.startsWith('second_')));
// Live gauges: empty/full/invalid values, no bright normal assets leak into AOD.
for(const [id,name] of [['CALORIE','calories'],['STRESS','stress']]){const sensor=sensors[id];for(const [v,target,expected] of [[0,100,0],[50,100,10],[100,100,20],[NaN,100,0]]){sensor.current=v;sensor.target=target;sensor.events.CHANGE.forEach(f=>f());const layers=widgets.filter(w=>w.type==='IMG'&&String(w.props.src).includes(name+'_scale_'));assert.equal(layers.length,2);assert(layers.some(w=>new RegExp('^(red_|green_|blue_|yellow_)?'+name+'_scale_'+expected+'\\.png$').test(w.props.src)));assert(layers.some(w=>new RegExp('^aod_(red_|green_|blue_|yellow_)?'+name+'_scale_'+expected+'\\.png$').test(w.props.src)));}}
assert.equal(widgets.filter(w=>w.type==='TIME_POINTER'&&w.props.hour_posX===36&&w.props.hour_posY===232).length,2);
assert(!widgets.some(w=>w.type==='TEXT_IMG'&&['DISTANCE','CAL'].includes(w.props.type)));
assert.equal(widgets.filter(w=>w.type==='IMG_CLICK'&&w.props.type==='STEP').length,1);
// Exact live time/date glyph updates; midnight, year boundary and AOD.
const nt=widgets.filter(w=>w.type==='IMG'&&/^nt_/.test(w.props.src)),at=widgets.filter(w=>w.type==='IMG'&&/^aod_at_/.test(w.props.src)),dt=widgets.filter(w=>w.type==='IMG'&&/^dt_/.test(w.props.src));
assert.equal(nt.length,8);assert.equal(at.length,5);assert.equal(dt.length,9);
const readChars=ws=>ws.map(w=>String.fromCharCode(Number(w.props.src.match(/_(\d+)\.png$/)[1]))).join('');
for(const sample of [{hour:23,minute:59,second:59,day:31,month:12,week:4,time:'23:59:59',date:'31.12 ЧТ '},{hour:0,minute:0,second:0,day:1,month:1,week:5,time:'00:00:00',date:'01.01 ПТ '},{hour:10,minute:8,second:36,day:1,month:11,week:7,time:'10:08:36',date:'01.11 ВСК'}]){Object.assign(sensors.TIME,sample);sensors.TIME.events.MINUTEEND.forEach(f=>f());assert.equal(readChars(nt),sample.time);assert.equal(readChars(at),sample.time.slice(0,5));assert.equal(readChars(dt),sample.date)}
assert(!widgets.some(w=>w.type==='IMG_DATE'||w.type==='IMG_WEEK'||w.type==='IMG_TIME'));
const forecast=widgets.filter(w=>w.type==='TEXT_IMG'&&['WEATHER_LOW','WEATHER_HIGH'].includes(w.props.type));assert.equal(forecast.length,4);forecast.forEach(w=>{assert.equal(w.props.y,381);assert.equal(w.props.h_space,-1);assert.equal(w.props.w,38);assert.equal(w.props.align_h,w.props.type==='WEATHER_LOW'?'RIGHT':'LEFT')});
assert(!widgets.some(w=>String(w.props.src).includes('arc_icon_')));
// Boundary transitions must be reversible, including invalid and missing values.
for(const [id,name,cases] of [['STRESS','stress',[[79,''],[80,'blue_'],[100,'blue_'],[0,''],[101,''],[NaN,'']]]]){
 for(const [v,tone] of cases){sensors[id].current=v;sensors[id].target=100;sensors[id].events.CHANGE.forEach(f=>f());const layers=widgets.filter(w=>w.type==='IMG'&&new RegExp('^(aod_)?(red_|green_|blue_|yellow_)?'+name+'_scale_').test(w.props.src));assert.equal(layers.length,2);assert(layers.some(w=>w.props.src.startsWith(tone+name+'_scale_')));assert(layers.some(w=>w.props.src.startsWith('aod_'+tone+name+'_scale_')));}
}
assert(!widgets.some(w=>w.type==='IMG_LEVEL'&&w.props.type==='DISTANCE'));assert(!widgets.some(w=>w.props.type==='TRAINING_LOAD'));
const stressCells=cells.filter(w=>w.props.normal_src&&w.props.normal_src.includes('stress_scale'));assert.equal(stressCells.length,3);for(const w of stressCells){launched.length=0;w.props.click_func();assert.equal(launched[0].url,'StressHomeScreen');assert.equal(launched[0].native,true)}
// Distance text is km, but achievement and fill follow EXACTLY 10000 steps.
const fire=id=>sensors[id].events.CHANGE.forEach(f=>f());
const distanceLayers=widgets.filter(w=>w.type==='IMG'&&/^(aod_)?(green_)?distance_scale_/.test(w.props.src));
const first=widgets.indexOf(distanceLayers[1])+1;
const distanceCells=widgets.slice(first,first+18).filter(w=>w.props.show_level==='ONLY_NORMAL');
const readDistance=()=>distanceCells.filter(w=>w.visible).map(w=>w.props.src.replace(/^(green_)?arc_/,'').replace('.png','')).join('|');
for(const [steps,meters,prefix,level] of [[9999,9000,'',20],[10000,3500,'green_',20],[10001,5200,'green_',20],[5000,20000,'',10],[0,0,'',0],[NaN,3500,'',0],[10000,NaN,'',0],[10000,3500,'green_',20]]){
 sensors.STEP.current=steps;sensors.STEP.target=20000;sensors.DISTANCE.current=meters;sensors.DISTANCE.target=1000;fire('STEP');fire('DISTANCE');
 for(const w of distanceLayers)assert.equal(w.props.src,(w.props.show_level==='ONAL_AOD'?'aod_':'')+prefix+'distance_scale_'+level+'.png');
 const chars=widgets.slice(first,first+18).filter(w=>w.visible);assert(chars.every(w=>w.props.src.startsWith((w.props.show_level==='ONAL_AOD'?'aod_':'')+'arc_')));
 assert(chars.every(w=>w.props.angle>0&&w.props.angle<90&&w.props.pos_y>=389));
}
// A STEP change alone, without a distance event, must recolour both normal/AOD views.
sensors.DISTANCE.current=3500;sensors.STEP.current=9999;fire('STEP');assert.equal(readDistance(),'3|dot|5|0|km');assert.equal(distanceLayers[0].props.src,'distance_scale_20.png');
sensors.STEP.current=10000;fire('STEP');assert.equal(distanceLayers[0].props.src,'green_distance_scale_20.png');assert.equal(readDistance(),'3|dot|5|0|km');
// Distance change alone must update km without altering step-goal completion.
sensors.DISTANCE.current=4999;fire('DISTANCE');assert.equal(readDistance(),'4|dot|9|9|km');assert.equal(distanceLayers[0].props.src,'green_distance_scale_20.png');
for(const [v,target,prefix,level] of [[599,600,'',20],[600,600,'yellow_',20],[601,600,'yellow_',20],[600,1200,'',10],[0,600,'',0],[NaN,600,'',0],[600,0,'',0],[600,undefined,'',0],[600,Infinity,'',0]]){
 Object.assign(sensors.CALORIE,{current:v,target});fire('CALORIE');
 const layers=widgets.filter(w=>w.type==='IMG'&&/^(aod_)?(yellow_)?calories_scale_/.test(w.props.src));assert.equal(layers.length,2);
 for(const w of layers)assert.equal(w.props.src,(w.props.show_level==='ONAL_AOD'?'aod_':'')+prefix+'calories_scale_'+level+'.png');
 const start=widgets.indexOf(layers[1])+1;const chars=widgets.slice(start,start+18).filter(w=>w.visible);assert(chars.every(w=>w.props.src.startsWith((w.props.show_level==='ONAL_AOD'?'aod_':'')+'arc_')));
}
console.log('PASS: 9999/10000/10001-step boundaries, independent STEP/DISTANCE updates, fixed actual-km text, native calorie goal and normal/AOD colours.');
// Native readiness: 101 exact values, normal/AOD bindings and tap destinations.
const ready=widgets.filter(w=>w.type==='IMG_LEVEL'&&w.props.type==='READINESS');assert.equal(ready.length,2);
for(const w of ready){assert.equal(w.props.image_length,101);assert.equal(w.props.image_array.length,101);for(let i=0;i<=100;i++)assert.equal(w.props.image_array[i],(w.props.show_level==='ONAL_AOD'?'aod_':'')+'readiness_'+i+'.png');}
assert(!widgets.some(w=>w.type==='IMG_CLICK'&&w.props.type==='SLEEP'));
console.log('PASS: native READINESS 0..100 normal/AOD resources and all three native readiness tap zones.');
// Central battery ICON and VALUE (including percent) switch together, with exact20% boundary.
const batteryIcons=widgets.filter(w=>w.type==='IMG_LEVEL'&&w.props.type==='BATTERY');assert.equal(batteryIcons.length,4);
const batteryValues=widgets.filter(w=>w.type==='TEXT_IMG'&&w.props.type==='BATTERY');assert.equal(batteryValues.length,4);
for(const value of [100,20,19,1,0,20,21,NaN,undefined,Infinity,-1,19]){
 sensors.BATTERY.current=value;fire('BATTERY');const low=typeof value==='number'&&Number.isFinite(value)&&value>=0&&value<20;
 for(const w of batteryIcons){const red=w.props.image_array[0].includes('red_battery');assert.equal(w.visible,red?low:!low)}
 for(const w of batteryValues){const red=w.props.font_array[0].includes('red_battery');assert.equal(w.visible,red?low:!low);assert.equal(w.props.unit_en.includes('red_battery'),red)}
}
console.log('PASS: central battery icon/digits/percent switch red below20%, reversible at20%, same normal/AOD geometry.');
const delegate=widgets.find(w=>w.type==='WIDGET_DELEGATE');assert.equal(activeTimers.size,1);const second=widgets.find(w=>w.type==='IMG'&&w.props.src==='second.png');assert(second);assert.equal(second.props.pos_x+6,240);assert.equal(second.props.pos_y+222,240);activeTimers.values().next().value();assert(second.props.angle>=0&&second.props.angle<360);delegate.props.pause_call();assert.equal(activeTimers.size,0);delegate.props.resume_call();assert.equal(activeTimers.size,1);face.onDestroy();assert.equal(activeTimers.size,0);assert.equal(Object.keys(sensors.HEART.events).length,0);console.log('PASS: 21 nonoverlapping native taps, all assets, normal/AOD, HH:MM, heart missing/recovery and cleanup, idempotent build.');
// Verify requested destinations at circle centres, gauge endpoints and all three clock regions.
const tapAt=(x,y)=>{const found=cells.filter(w=>{const p=w.props;return x>=p.x&&x<p.x+p.w&&y>=p.y&&y<p.y+p.h});assert.equal(found.length,1,`tap coverage ${x},${y}`);return found[0]};
for(const [x,y,url] of [[240,100,'Settings_batteryManagerScreen'],[370,240,'heart_app_Screen'],[240,370,'WeatherScreen'],[240,290,'ScheduleCalScreen'],[180,180,'AlarmInfoScreen'],[240,195,'StopWatchScreen'],[300,180,'CountdownAppScreen']]){const w=tapAt(x,y);assert.equal(w.type,'BUTTON');launched.length=0;w.props.click_func();assert.equal(launched[0].url,url)}
for(const [x,y,type] of [[110,240,'STEP'],[66,177,'READINESS'],[162,72,'READINESS'],[66,303,'DISTANCE'],[162,407,'DISTANCE'],[414,303,'CAL'],[318,407,'CAL']]){const w=tapAt(x,y);assert.equal(w.type,'IMG_CLICK');assert.equal(w.props.type,type)}
console.log('PASS: exact requested tap destinations for circles, gauge endpoints, calendar and three time sections.');

assert(Object.values(sensors).every(s=>Object.keys(s.events).length===0),'all listeners cleaned');
if(process.env.DUMP_WIDGETS)fs.writeFileSync(process.env.DUMP_WIDGETS,JSON.stringify(widgets));
console.log('PASS: colour boundaries, native CAL binding, stress taps and complete listener cleanup.');


