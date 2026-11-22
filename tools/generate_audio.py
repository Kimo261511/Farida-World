#!/usr/bin/env python3
"""Generate three original, layered instrumental soundtracks for Farida World."""
from pathlib import Path
import math
import wave
import numpy as np

ROOT = Path(__file__).resolve().parents[1] / "app" / "src" / "main" / "assets" / "music"
ROOT.mkdir(parents=True, exist_ok=True)
RATE = 44100
DURATION = 225
BPM = 96
CHUNK_SECONDS = 2
TRACKS = {
    "forest.wav": {"scale": [0, 2, 4, 7, 9], "roots": [48, 53, 55, 50], "tone": 0},
    "ocean.wav": {"scale": [0, 3, 5, 7, 10], "roots": [45, 50, 53, 48], "tone": 1},
    "adventure.wav": {"scale": [0, 2, 5, 7, 9], "roots": [50, 55, 57, 52], "tone": 2},
}

def hz(midi):
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))

def make_track(path, cfg):
    scale = cfg["scale"]
    roots = cfg["roots"]
    tone = cfg["tone"]
    melody = np.array([0, 2, 4, 2, 1, 3, 4, 3, 0, 2, 4, 5, 4, 3, 1, 2])
    melody = np.array([scale[int(x) % len(scale)] for x in melody])
    with wave.open(str(path), "wb") as out:
        out.setnchannels(2)
        out.setsampwidth(2)
        out.setframerate(RATE)
        total = RATE * DURATION
        chunk = RATE * CHUNK_SECONDS
        for start in range(0, total, chunk):
            n = min(chunk, total - start)
            t = (np.arange(n, dtype=np.float64) + start) / RATE
            beat = t * BPM / 60.0
            beat_i = np.floor(beat).astype(np.int32)
            beat_pos = beat - beat_i
            bar_i = np.floor(beat / 4).astype(np.int32)
            root = np.array(roots, dtype=np.float64)[bar_i % len(roots)]
            # Warm sustained chord pad, gently pulsing and stereo-spread.
            chord = np.zeros(n, dtype=np.float64)
            for interval in (0, 4 if tone != 1 else 3, 7):
                f = hz(root + interval + 12)
                chord += np.sin(2 * np.pi * f * t + interval) * 0.045
                chord += np.sin(2 * np.pi * f * 2.003 * t) * 0.012
            pad_env = 0.78 + 0.22 * np.sin(2 * np.pi * beat / 4.0)
            chord *= pad_env
            # Plucked melodic motif with a soft bell-like upper partial.
            note_idx = (beat_i % len(melody)).astype(np.int32)
            note = root + 24 + melody[note_idx]
            f = 440.0 * np.power(2.0, (note - 69.0) / 12.0)
            env = np.exp(-beat_pos * (3.8 if tone == 0 else 3.1))
            lead = (np.sin(2*np.pi*f*t) + 0.32*np.sin(2*np.pi*f*2.01*t)) * env * 0.105
            # Rounded bass pulse on each beat.
            bass_f = 440.0 * np.power(2.0, (root - 12.0 - 69.0) / 12.0)
            bass = np.sin(2*np.pi*bass_f*t) * np.exp(-beat_pos*2.2) * 0.10
            # Soft kick and alternating hand-drum accents.
            kick_phase = np.mod(beat, 1.0)
            kick_env = np.exp(-kick_phase * 18.0)
            kick = np.sin(2*np.pi*(48.0 + 42.0*np.exp(-kick_phase*28.0))*t) * kick_env * 0.075
            snare_phase = np.mod(beat - 1.0, 2.0)
            snare_env = np.exp(-snare_phase * 22.0) * ((beat_i % 4) == 2)
            noise = np.sin(2*np.pi*(1730 + 310*np.sin(t*17))*t)
            snare = noise * snare_env * 0.025
            shimmer = np.sin(2*np.pi*(7200 + 300*np.sin(t*0.7))*t) * np.exp(-np.mod(beat, 0.5)*32) * 0.009
            mix = chord + lead + bass + kick + snare + shimmer
            # Gentle fade-in/out and soft saturation prevent harsh clipping.
            fade = np.minimum(1.0, t / 2.0) * np.minimum(1.0, (DURATION - t) / 3.0)
            mix = np.tanh(mix * 1.65) * fade
            pan = 0.12 * np.sin(2*np.pi*t/13.0 + tone)
            left = np.clip(mix * (0.92 - pan), -0.98, 0.98)
            right = np.clip(mix * (0.92 + pan), -0.98, 0.98)
            stereo = np.column_stack((left, right))
            out.writeframesraw((stereo * 32767).astype("<i2").tobytes())
    print(f"Generated {path.name}: {path.stat().st_size:,} bytes")

if __name__ == "__main__":
    for filename, config in TRACKS.items():
        make_track(ROOT / filename, config)
    total = sum(p.stat().st_size for p in ROOT.glob("*.wav"))
    print(f"Total soundtrack payload: {total:,} bytes")
