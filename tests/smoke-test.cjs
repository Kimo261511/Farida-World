const fs=require('fs'),assert=require('assert'),vm=require('vm');
const root=__dirname+'/..';
const html=fs.readFileSync(root+'/app/src/main/assets/index.html','utf8');
const activity=fs.readFileSync(root+'/app/src/main/java/com/farida/adventures/MainActivity.java','utf8');
const manifest=fs.readFileSync(root+'/app/src/main/AndroidManifest.xml','utf8');
const gradle=fs.readFileSync(root+'/app/build.gradle','utf8');
const checks=[
 ['Arabic right-to-left interface',()=>assert.match(html,/<html lang="ar" dir="rtl">/)],
 ['Canvas renderer and animation loop',()=>{assert(html.includes('<canvas id="scene"'));assert(html.includes('function draw('));assert(html.includes('function loop('))}],
 ['Five selectable game worlds',()=>{['الغابة السحرية','مملكة البحار','وادي الرمال','جزر السحاب','حديقة الحيوانات'].forEach(x=>assert(html.includes(x)));assert.strictEqual((html.match(/data-world=/g)||[]).length,5)}],
 ['Start and home navigation controls',()=>{['id="play"','id="home"','id="sound"'].forEach(x=>assert(html.includes(x)))}],
 ['Touch movement and jump controls',()=>{['id="left"','id="right"','id="jump"'].forEach(x=>assert(html.includes(x)))}],
 ['Local progress persistence',()=>{assert(html.includes('localStorage.fwGems'));assert(html.includes('localStorage.fwStars'))}],
 ['Audio generation and mute control',()=>{assert(html.includes('function sound('));assert(html.includes('muted'))}],
 ['Game JavaScript syntax',()=>{const a=html.indexOf('<script>'),b=html.indexOf('</script>');assert(a>=0&&b>a);new vm.Script(html.slice(a+8,b),{filename:'farida-game.js'})}],
 ['Android opens the bundled offline game',()=>{assert(activity.includes('file:///android_asset/index.html'));assert(manifest.includes('usesCleartextTraffic="false"'))}],
 ['APK configuration',()=>{assert(gradle.includes('versionName'));assert(gradle.includes("noCompress += ['wav']"))}]
];
let failed=0;
for(const [name,fn] of checks){try{fn();console.log('PASS '+name)}catch(e){failed++;console.error('FAIL '+name+': '+e.message)}}
console.log(checks.length-failed+'/'+checks.length+' checks passed');
if(failed)process.exit(1);
