#!/usr/bin/env python3
"""Verify original game music and artwork are bundled in the Android APK."""
from pathlib import Path
import sys, zipfile, wave
apk=Path("app/build/outputs/apk/debug/app-debug.apk")
if not apk.is_file(): raise SystemExit("APK missing")
assets=[
 "audio/forest_theme.wav","audio/desert_theme.wav","audio/star_islands_theme.wav",
 "art/forest_background.jpg","art/desert_background.jpg","art/star_islands_background.jpg",
 "art/farida_character_strip.png"
]
base=Path("app/src/main/assets")
for name in assets:
 p=base/name
 if not p.is_file() or p.stat().st_size<1000: raise SystemExit(f"Missing or empty generated asset: {name}")
for name in assets[:3]:
 with wave.open(str(base/name),"rb") as wav:
  if wav.getnchannels()!=2 or wav.getframerate()!=44100 or wav.getnframes()<44100*224:
   raise SystemExit(f"Invalid soundtrack: {name}")
with zipfile.ZipFile(apk) as z:
 names=set(z.namelist())
 for name in assets:
  key="assets/"+name
  if key not in names: raise SystemExit(f"APK missing {key}")
  if z.getinfo(key).file_size<1000: raise SystemExit(f"APK asset empty: {key}")
size=apk.stat().st_size
if size<100*1024*1024: raise SystemExit(f"APK only {size:,} bytes; expected at least 104,857,600")
print(f"APK verified: {size:,} bytes; 3 music tracks, 3 backgrounds, and Farida animation strip are bundled.")
