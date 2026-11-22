const fs=require('fs'),assert=require('assert'),vm=require('vm');
const root=__dirname+'/..';
const html=fs.readFileSync(root+'/app/src/main/assets/index.html','utf8');
const activity=fs.readFileSync(root+'/app/src/main/java/com/farida/adventures/MainActivity.java','utf8');
const manifest=fs.readFileSync(root+'/app/src/main/AndroidManifest.xml','utf8');
const gradle=fs.readFileSync(root+'/app/build.gradle','utf8');
const checks=[
 ['Arabic right-to-left game shell',()=>assert.match(html,/<html lang="ar" dir="rtl">/)],
 ['Canvas-based 2D game engine',()=>{assert(html.includes("getContext('2d')"));assert(html.includes('function loop(now)'));assert(html.includes('function update(dt)'))}],
 ['Game JavaScript parses without syntax errors',()=>{const js=html.slice(html.indexOf('<script>')+8,html.indexOf('</script>'));assert(js.length>0);new vm.Script(js)}],
 ['Three worlds and fifteen stages',()=>{['الغابة المضيئة','مملكة الرمال','جزر النجوم'].forEach(x=>assert(html.includes(x)));assert(html.includes('n<=unlocked'))}],
 ['Touch controls for movement, jump and attack',()=>['left','right','jump','hit'].forEach(x=>assert(html.includes('id="'+x+'"')))],
 ['Keyboard controls',()=>assert(html.includes('ArrowLeft')&&html.includes('keydown'))],
 ['Collectible gems and local persistence',()=>{assert(html.includes('function crystal'));assert(html.includes('earned++'));assert(html.includes("['gems',gems]"))}],
 ['Enemies, hazards and combat',()=>{assert(html.includes('function attack()'));assert(html.includes('function hurt()'));assert(html.includes('traps.forEach'))}],
 ['Level completion and star progression',()=>{assert(html.includes('function win()'));assert(html.includes("['unlocked',unlocked]"));assert(html.includes("['stars',stars]"))}],
 ['Unlockable outfits and settings',()=>{assert(html.includes('function shop()'));assert(html.includes('function buy(i)'));assert(html.includes('function settings()'))}],
 ['Offline synthesized music and effects',()=>{assert(html.includes('AudioContext'));assert(html.includes('function audioOn()'));assert(html.includes('function fx(k)'))}],
 ['Android offline WebView',()=>{assert(activity.includes('file:///android_asset/index.html'));assert(manifest.includes('usesCleartextTraffic="false"'))}],
 ['No remote scripts or Internet permission',()=>{assert(!/<script[^>]+src=/.test(html));assert(!manifest.includes('android.permission.INTERNET'))}],
 ['Version 3.0.0',()=>{assert(gradle.includes("versionName '3.0.0'"));assert(gradle.includes('versionCode 7'))}],
 ['APK build enforces 100 MB maximum',()=>assert(fs.readFileSync(root+'/.github/workflows/build-apk.yml','utf8').includes('104857600'))]
];
let failed=0;for(const [name,fn] of checks){try{fn();console.log('PASS '+name)}catch(e){failed++;console.error('FAIL '+name+': '+e.message)}}
console.log(checks.length-failed+'/'+checks.length+' checks passed');if(failed)process.exit(1);