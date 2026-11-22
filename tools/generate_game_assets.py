#!/usr/bin/env python3
"""Generate original, playable game assets: three composed stereo soundtracks and illustrated backgrounds."""
from pathlib import Path
import math, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path("app/src/main/assets")
AUDIO = ROOT / "audio"
ART = ROOT / "art"
AUDIO.mkdir(parents=True, exist_ok=True)
ART.mkdir(parents=True, exist_ok=True)
SR, SECONDS, CHUNK = 44100, 225, 5
TRACKS = [
    ("forest_theme.wav", 112, [261.63, 329.63, 392.00, 523.25], "forest"),
    ("desert_theme.wav", 96, [220.00, 277.18, 329.63, 440.00], "desert"),
    ("star_islands_theme.wav", 124, [293.66, 369.99, 440.00, 587.33], "stars"),
]

def make_track(filename, bpm, chord, mood):
    path = AUDIO / filename
    total = SR * SECONDS
    beat = 60.0 / bpm
    rng = np.random.default_rng({"forest": 17, "desert": 29, "stars": 43}[mood])
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(2); wav.setsampwidth(2); wav.setframerate(SR)
        for start in range(0, total, SR * CHUNK):
            n = min(SR * CHUNK, total - start)
            t = (np.arange(start, start+n, dtype=np.float64) / SR)
            beat_pos = t / beat
            beat_i = np.floor(beat_pos).astype(np.int64)
            phase = np.mod(beat_pos, 1.0)
            bar = (beat_i // 4) % 4
            roots = np.asarray(chord)[bar]
            # Warm sustained chord bed with slow filter-like movement.
            pad = (np.sin(2*np.pi*(roots*0.5)*t) +
                   .42*np.sin(2*np.pi*(roots*.75)*t + .4) +
                   .24*np.sin(2*np.pi*roots*t + .9))
            pad *= .17 * (0.82 + .18*np.sin(2*np.pi*t/13.0))
            # A hand-composed, repeating but evolving pentatonic melody.
            scale = np.asarray([1, 1.125, 1.25, 1.5, 1.6667, 2, 2.25, 2.5])
            seq = np.asarray([0,2,4,3,1,4,6,4, 2,5,7,5,3,4,2,1,
                              0,2,5,4,2,6,4,3, 1,3,4,7,5,3,2,0])
            idx = (beat_i // 2 + (bar*3)) % len(seq)
            note = roots * scale[seq[idx]]
            local = np.mod(t, beat*2)
            env = np.clip(local/.09,0,1) * np.clip((beat*1.8-local)/.16,0,1)
            melody = np.sin(2*np.pi*note*t + .13*np.sin(2*np.pi*4*t)) * env * .19
            bell = np.sin(2*np.pi*note*2*t) * env**2 * .055
            # Soft kick and shaker, with mood-specific percussion texture.
            kick_env = np.exp(-phase*17) * ((beat_i % 4)==0)
            kick = np.sin(2*np.pi*(58-18*phase)*t) * kick_env * .20
            snare_env = np.exp(-phase*23) * ((beat_i % 4)==2)
            noise = rng.standard_normal(n)
            snare = noise * snare_env * .035
            shaker_env = np.maximum(0, 1-np.abs(phase-.5)*18) * ((beat_i % 2)==1)
            shaker = noise * shaker_env * .012
            # Gentle stereo width and slow moving pan.
            mix = pad + melody + bell + kick + snare + shaker
            pan = .5 + .22*np.sin(2*np.pi*t/19.0)
            left = np.clip(mix*(1.0-pan*.25), -.92, .92)
            right = np.clip(mix*(.75+pan*.25), -.92, .92)
            stereo = np.column_stack((left,right))
            pcm = (stereo*32767).astype('<i2')
            wav.writeframesraw(pcm.tobytes())
    print(f"created {path} ({path.stat().st_size:,} bytes)")

def gradient_bg(name, top, bottom, accent, seed):
    w,h=2048,1152
    y=np.linspace(0,1,h)[:,None,None]
    top=np.array(top,dtype=float)[None,None,:]
    bottom=np.array(bottom,dtype=float)[None,None,:]
    arr=np.broadcast_to(top*(1-y)+bottom*y,(h,w,3)).copy().astype(np.uint8)
    im=Image.fromarray(arr,"RGB").convert("RGBA")
    d=ImageDraw.Draw(im,"RGBA")
    rng=np.random.default_rng(seed)
    # Distant hills and layered ridges.
    for layer in range(5):
        base=760+layer*70
        pts=[(0,h)]
        for x in range(0,w+1,32):
            yy=base + math.sin(x/(90+layer*28)+layer)*42 + math.sin(x/(31+layer*13))*17 + rng.integers(-12,13)
            pts.append((x,int(yy)))
        pts.extend([(w,h)])
        col=tuple(max(0,min(255,int(v*(.68+layer*.055)))) for v in accent)+(255,)
        d.polygon(pts,fill=col)
    # Clouds / stars / distant light.
    if name=="star_islands":
        for _ in range(240):
            x=int(rng.integers(0,w)); yy=int(rng.integers(20,760)); r=int(rng.integers(2,7))
            d.ellipse((x-r,yy-r,x+r,yy+r),fill=(255,245,220,int(rng.integers(90,230))))
        for x,y0,r in [(300,250,120),(1650,190,90),(1100,400,60)]:
            d.ellipse((x-r,y0-r,x+r,y0+r),fill=(230,210,255,35))
    else:
        for _ in range(24):
            x=int(rng.integers(-100,w)); yy=int(rng.integers(80,420)); scale=int(rng.integers(35,100))
            d.ellipse((x,yy,x+scale*2,yy+scale*.38),fill=(255,255,255,48))
    # Foreground silhouettes, trees or dunes.
    if name=="forest":
        for x in range(-30,w+100,150):
            height=int(rng.integers(170,340)); base=1000
            d.rectangle((x+45,base-height//2,x+70,base),fill=(48,76,66,255))
            d.ellipse((x,base-height-80,x+170,base-height+110),fill=(31,110,79,245))
            d.ellipse((x+32,base-height-125,x+145,base-height+45),fill=(64,153,103,225))
            for _ in range(5):
                sx=x+int(rng.integers(15,145)); sy=base-height+int(rng.integers(-60,110))
                d.ellipse((sx,sy,sx+12,sy+12),fill=(255,223,117,180))
    elif name=="desert":
        for x in range(-100,w+200,260):
            d.ellipse((x,780,x+520,1210),fill=(219,157,91,255))
            d.arc((x,760,x+520,1150),180,350,fill=(255,218,157,170),width=8)
        for x,y0 in [(280,730),(1490,700)]:
            d.rectangle((x+55,y0,x+75,1000),fill=(69,111,71,255))
            for a in range(7):
                d.line((x+65,y0+35,x+65+int(math.cos(a)*90),y0-50+int(math.sin(a)*70)),fill=(72,145,86,255),width=16)
    else:
        for x,y0,r in [(260,760,180),(1040,810,230),(1740,750,200)]:
            d.ellipse((x-r,y0-r//2,x+r,y0+r//2),fill=(90,93,173,255))
            d.ellipse((x-r//2,y0-r//2-30,x+r//2,y0+r//2-30),fill=(124,117,205,230))
    im=im.filter(ImageFilter.GaussianBlur(.35)).convert("RGB")
    im.save(ART/(name+"_background.jpg"),quality=94,optimize=True)
    print("created",ART/(name+"_background.jpg"))

def character_sheet():
    # Four clean, transparent 512px character animation cells in a 2048x512 strip.
    sheet=Image.new("RGBA",(2048,512),(0,0,0,0))
    for frame in range(4):
        im=Image.new("RGBA",(512,512),(0,0,0,0)); d=ImageDraw.Draw(im)
        bob=[0,-5,0,4][frame]; leg=[-12,2,13,0][frame]
        # Soft contact shadow.
        d.ellipse((125,430,390,470),fill=(24,35,56,65))
        # Hair back and ponytail.
        d.ellipse((175,68+bob,354,265+bob),fill=(91,48,37,255))
        d.ellipse((315,130+bob,392,245+bob),fill=(105,55,42,255))
        d.ellipse((340,100+bob,390,160+bob),fill=(122,67,48,255))
        # Legs and boots.
        d.line((225,350+bob,215+leg,420),fill=(226,163,125,255),width=28)
        d.line((305,350+bob,315-leg,420),fill=(226,163,125,255),width=28)
        d.rounded_rectangle((177+leg,407,247+leg,450),radius=18,fill=(93,57,85,255),outline=(255,218,166,255),width=5)
        d.rounded_rectangle((278-leg,407,348-leg,450),radius=18,fill=(93,57,85,255),outline=(255,218,166,255),width=5)
        # Dress, scarf, arms.
        d.polygon([(188,220+bob),(326,220+bob),(375,385+bob),(145,385+bob)],fill=(238,105,157,255))
        d.polygon([(188,220+bob),(326,220+bob),(348,270+bob),(170,270+bob)],fill=(255,183,207,255))
        d.line((190,260+bob,130,340+bob),fill=(232,171,133,255),width=25)
        d.line((326,260+bob,385,330+bob),fill=(232,171,133,255),width=25)
        d.ellipse((116,324+bob,149,357+bob),fill=(244,190,151,255))
        d.ellipse((370,314+bob,403,347+bob),fill=(244,190,151,255))
        # Face and bangs.
        d.ellipse((184,83+bob,342,254+bob),fill=(244,194,157,255),outline=(189,123,98,255),width=4)
        d.pieslice((174,48+bob,350,230+bob),180,360,fill=(91,48,37,255))
        d.ellipse((175,100+bob,218,230+bob),fill=(91,48,37,255))
        d.ellipse((309,100+bob,352,230+bob),fill=(91,48,37,255))
        # eyes, brows, cheeks, smile.
        for ex in (230,292):
            d.ellipse((ex-9,155+bob,ex+9,180+bob),fill=(255,255,255,255))
            d.ellipse((ex-4,161+bob,ex+5,178+bob),fill=(49,56,76,255))
            d.arc((ex-13,140+bob,ex+13,163+bob),190,345,fill=(87,52,42,255),width=5)
        d.ellipse((202,185+bob,225,199+bob),fill=(239,129,137,100))
        d.ellipse((299,185+bob,322,199+bob),fill=(239,129,137,100))
        d.arc((246,182+bob,278,211+bob),5,170,fill=(155,73,78,255),width=5)
        # Star hair clip and necklace.
        d.ellipse((318,95+bob,350,127+bob),fill=(255,218,100,255),outline=(255,247,204,255),width=4)
        d.ellipse((250,233+bob,263,246+bob),fill=(255,231,135,255))
        sheet.alpha_composite(im,(frame*512,0))
    sheet.save(ART/"farida_character_strip.png",optimize=True)
    print("created",ART/"farida_character_strip.png")

if __name__=="__main__":
    for track in TRACKS: make_track(*track)
    gradient_bg("forest",(97,190,218),(202,235,183),(55,135,103),7)
    gradient_bg("desert",(238,163,103),(255,222,157),(178,117,73),11)
    gradient_bg("star_islands",(32,44,105),(125,115,193),(83,83,154),19)
    character_sheet()
    total=sum(p.stat().st_size for p in AUDIO.glob("*.wav"))
    print(f"ORIGINAL_AUDIO_BYTES={total}")
    if total < 115_000_000: raise SystemExit("Audio asset set unexpectedly small")
