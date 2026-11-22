#!/usr/bin/env python3
"""Fail the Android build if real soundtrack assets are missing from the APK."""
from pathlib import Path
import sys
import zipfile
import wave

apk = Path("app/build/outputs/apk/debug/app-debug.apk")
if not apk.is_file():
    raise SystemExit("APK missing")
assets = [
    Path("app/src/main/assets/music/forest.wav"),
    Path("app/src/main/assets/music/ocean.wav"),
    Path("app/src/main/assets/music/adventure.wav"),
]
for asset in assets:
    if not asset.is_file():
        raise SystemExit(f"Missing generated soundtrack: {asset}")
    with wave.open(str(asset), "rb") as wav:
        if wav.getnchannels() != 2 or wav.getframerate() != 44100 or wav.getnframes() < 44100 * 224:
            raise SystemExit(f"Invalid soundtrack format/duration: {asset}")
size = apk.stat().st_size
if size < 100 * 1024 * 1024:
    raise SystemExit(f"APK is only {size:,} bytes; required minimum is 104,857,600")
with zipfile.ZipFile(apk) as z:
    names = set(z.namelist())
    required = {
        "assets/music/forest.wav",
        "assets/music/ocean.wav",
        "assets/music/adventure.wav",
    }
    missing = required - names
    if missing:
        raise SystemExit(f"APK missing soundtrack assets: {sorted(missing)}")
    for name in required:
        info = z.getinfo(name)
        if info.file_size < 39_000_000:
            raise SystemExit(f"Soundtrack in APK is unexpectedly small: {name}")
print(f"APK verified: {size:,} bytes; all 3 original WAV tracks are bundled.")
