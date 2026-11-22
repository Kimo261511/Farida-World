const fs=require('fs'),assert=require('assert'),vm=require('vm');
const root=__dirname+'/..';
const html=fs.readFileSync(root+'/app/src/main/assets/index.html','utf8');
const activity=fs.readFileSync(root+'/app/src/main/java/com/farida/adventures/MainActivity.java','utf8');
const manifest=fs.readFileSync(root+'/app/src/main/AndroidManifest.xml','utf8');
const gradle=fs.readFileSync(root+'/app/build.gradle','utf8');
const workflow=fs.readFileSync(root+'/.github/workflows/build-apk.yml','utf8');
const generator=fs.readFileSync(root+'/tools/generate_game_assets.py','utf8');
const checks=[
 ['Arabic right-to-left game shell',()=>assert.match(html,/<html lang="ar" dir="rtl">/)],
 ['Canvas game loop and physics',()=>{assert(html.includes("getContext('2d')"));assert(html.includes('function loop(now)'));assert(html.includes('function update(dt)'))}],
 ['Game JavaScript syntax',()=>{const js=html.slice(html.indexOf('<script>')+8,html.indexOf('</script>'));try{new vm.Script(js)}catch(e){throw new Error(e.stack)}}],
 ['Original playable world music is loaded by world',()=>{assert(html.includes("forest_theme.wav"));assert(html.includes("desert_theme.wav"));assert(html.includes("star_islands_theme.wav"));assert(html.includes("player.play().catch(()=>{})"))}],
 ['Original illustrated backgrounds and animated character',()=>{['art/forest_background.jpg','art/desert_background.jpg','art/star_islands_background.jpg','art/farida_character_strip.png'].forEach(x=>assert(html.includes(x)));assert(html.includes('faridaStrip'))}],
 ['Arabic story intros for the three worlds',()=>{assert(html.includes('حكاية العالم'));assert(html.includes('وصلت فريدة إلى الغابة المضيئة'));assert(html.includes('عبرت فريدة الصحراء الذهبية'));assert(html.includes('وصلت فريدة إلى جزر النجوم'));assert(html.includes('continueStory'))}],
 ['Educational memory, color and Arabic letter games',()=>{assert(html.includes('function learnMenu()'));assert(html.includes('function flipMemory(i)'));assert(html.includes('function pickColor(i)'));assert(html.includes('function pickLetter(i)'));assert(html.includes('ألعاب فريدة التعليمية'))}],
 ['Fishing mini-game with touch rewards',()=>{assert(html.includes('function fishing()'));assert(html.includes('function fishTap(e)'));assert(html.includes('اصطد 10 سمكات'));assert(html.includes('fishCaught*2'))}],
 ['Three worlds and fifteen stages',()=>{['الغابة المضيئة','مملكة الرمال','جزر النجوم'].forEach(x=>assert(html.includes(x)));assert(html.includes('n<=unlocked'))}],
 ['Touch movement, jump and attack',()=>['left','right','jump','hit'].forEach(x=>assert(html.includes('id="'+x+'"')))],
 ['Keyboard controls',()=>assert(html.includes('ArrowLeft')&&html.includes('keydown'))],
 ['Collectibles and local persistence',()=>{assert(html.includes('function crystal'));assert(html.includes('earned++'));assert(html.includes("['gems',gems]"))}],
 ['Enemies, hazards and combat',()=>{assert(html.includes('function attack()'));assert(html.includes('function hurt()'));assert(html.includes('traps.forEach'))}],
 ['Level completion and progression',()=>{assert(html.includes('function win()'));assert(html.includes("['unlocked',unlocked]"));assert(html.includes("['stars',stars]"))}],
 ['Outfit shop and settings',()=>{assert(html.includes('function shop()'));assert(html.includes('function buy(i)'));assert(html.includes('function settings()'))}],
 ['Real audio assets generated as PCM WAV',()=>{assert(generator.includes('wave.open'));assert(generator.includes('SR, SECONDS, CHUNK = 44100, 225, 5'));assert(generator.includes('wav.writeframesraw'))}],
 ['Asset generation is part of APK build',()=>{assert(workflow.includes('python tools/generate_game_assets.py'));assert(workflow.includes('115000000'))}],
 ['Android offline WebView',()=>{assert(activity.includes('file:///android_asset/index.html'));assert(manifest.includes('usesCleartextTraffic="false"'));assert(!manifest.includes('android.permission.INTERNET'))}],
 ['WAV files remain uncompressed in APK',()=>assert(gradle.includes("noCompress += ['wav']"))],
 ['Version 4.1.0',()=>{assert(gradle.includes("versionName '4.1.0'"));assert(gradle.includes('versionCode 9'))}],
 ['APK enforces 100 MiB minimum',()=>{assert(workflow.includes('104857600'));assert(workflow.includes('-ge 104857600'))}]
];
let failed=0;for(const [name,fn] of checks){try{fn();console.log('PASS '+name)}catch(e){failed++;console.error('FAIL '+name+': '+e.message)}}
console.log(checks.length-failed+'/'+checks.length+' checks passed');if(failed)process.exit(1);