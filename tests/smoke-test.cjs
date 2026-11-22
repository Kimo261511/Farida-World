const fs=require('fs'),assert=require('assert');
const root=__dirname+'/..';
const html=fs.readFileSync(root+'/app/src/main/assets/index.html','utf8');
const activity=fs.readFileSync(root+'/app/src/main/java/com/farida/adventures/MainActivity.java','utf8');
const manifest=fs.readFileSync(root+'/app/src/main/AndroidManifest.xml','utf8');
const checks=[
 ['Arabic right-to-left game shell',()=>assert.match(html,/<html lang="ar" dir="rtl">/)],
 ['All six activities exist',()=>['fishing','colors','memory','puzzle','learn','drawing'].forEach(x=>assert(html.includes('id="'+x+'"')))],
 ['Fishing interaction and score',()=>{assert(html.includes('function catchFish'));assert(html.includes('fishScore>=fishTarget'))}],
 ['Twenty progressive fishing levels',()=>{assert(html.includes('function renderLevels'));assert(html.includes('n<=20'));assert(html.includes('fishTarget=5+Math.floor'))}],
 ['Color matching game',()=>assert(html.includes('function nextColor'))],
 ['Six-pair memory game',()=>{assert(html.includes('const emojis='));assert(html.includes('memoryMatches===6'))}],
 ['Twenty learning puzzles',()=>assert((html.match(/\['/g)||[]).length>=20)],
 ['Arabic letters and numbers',()=>{assert(html.includes('const chars='));assert(html.includes('const nums='))}],
 ['Touch drawing canvas',()=>assert(html.includes('pointermove'))],
 ['Synthesized offline sound and melody',()=>{assert(html.includes('AudioContext'));assert(html.includes('function startMusic'))}],
 ['Offline Android WebView',()=>{assert(activity.includes('file:///android_asset/index.html'));assert(manifest.includes('usesCleartextTraffic="false"'))}],
 ['No remote scripts or internet permission',()=>{assert(!/<script[^>]+src=/.test(html));assert(!manifest.includes('android.permission.INTERNET'))}]
];
let failed=0;for(const [name,fn] of checks){try{fn();console.log('PASS '+name)}catch(e){failed++;console.error('FAIL '+name+': '+e.message)}}
console.log(checks.length-failed+'/'+checks.length+' checks passed');if(failed)process.exit(1);
