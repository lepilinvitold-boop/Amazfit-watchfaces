const fs=require('fs');let s=fs.readFileSync('projects/Graphite-Arm-1.1.0/validate.cjs','utf8');s=s.slice(0,s.indexOf('vm.runInNewContext'));
s+=`Object.assign(sensors,{BATTERY:{current:19},STEP:{current:10000,target:10000},STRESS:{current:86},HEART:{last:86},TIME:{hour:10,minute:8,second:36,day:1,month:11,week:7}});for(const s of Object.values(sensors)){s.events={};s.addEventListener=function(e,f){(this.events[e]??=[]).push(f)};s.removeEventListener=function(){}};
vm.runInNewContext(fs.readFileSync(root+'/watchface/index.js','utf8'),sandbox);face.onInit();fs.writeFileSync('/tmp/widgets.json',JSON.stringify(widgets));`;
require('vm').runInThisContext('(function(require,process){'+s+'})')(require,process);
