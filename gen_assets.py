"""
gen_assets.py
Generates placeholder WAV audio assets for the Bean & Brew kiosk prototype.

Sounds generated:
  click.wav        - short blip for menu item taps
  confirm.wav       - two-tone chime for order confirmation
  whoosh.wav        - soft filtered sweep for screen transitions
  tick.wav          - short mechanical tick for receipt "printing" animation
  ambient.wav       - looping layered ambient pad for background atmosphere
  step_up.wav       - rising blip for quantity stepper "+"
  step_down.wav     - falling blip for quantity stepper "-"

Run once: python3 gen_assets.py
Replace these with real recorded/branded audio for a production version.
"""
import wave
import struct
import math
import os
import random

OUT_DIR = os.path.join(os.path.dirname(__file__), "assets")
os.makedirs(OUT_DIR, exist_ok=True)
SR = 44100


def write_wav(filename, samples, sample_rate=SR):
    path = os.path.join(OUT_DIR, filename)
    with wave.open(path, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        frames = b"".join(
            struct.pack("<h", int(max(-1.0, min(1.0, s)) * 32767)) for s in samples
        )
        f.writeframes(frames)
    print(f"wrote {path}  ({len(samples)/sample_rate:.2f}s)")


def envelope(i, n, fade_in, fade_out):
    if i < fade_in:
        return i / fade_in
    if i > n - fade_out:
        return (n - i) / fade_out
    return 1.0


def tone(freq, duration, volume=0.5, fade=0.01, sample_rate=SR, wave_fn=math.sin):
    n = int(duration * sample_rate)
    fade_n = max(1, int(fade * sample_rate))
    out = []
    for i in range(n):
        t = i / sample_rate
        s = wave_fn(2 * math.pi * freq * t) * volume
        s *= envelope(i, n, fade_n, fade_n)
        out.append(s)
    return out


def sweep(f_start, f_end, duration, volume=0.4, sample_rate=SR):
    """frequency sweep with light noise texture - used for transition whoosh"""
    n = int(duration * sample_rate)
    fade_n = max(1, int(0.02 * sample_rate))
    out = []
    for i in range(n):
        t = i / sample_rate
        frac = i / n
        freq = f_start + (f_end - f_start) * frac
        s = math.sin(2 * math.pi * freq * t) * volume
        s += (random.uniform(-1, 1) * 0.05) * (1 - frac)
        s *= envelope(i, n, fade_n, fade_n)
        out.append(s)
    return out


def click_sound():
    return tone(1200, 0.07, volume=0.4)


def step_up_sound():
    return tone(700, 0.06, volume=0.35) + tone(1000, 0.06, volume=0.35)


def step_down_sound():
    return tone(700, 0.06, volume=0.35) + tone(450, 0.06, volume=0.35)


def confirm_sound():
    a = tone(880, 0.15, volume=0.4)
    b = tone(1320, 0.28, volume=0.4)
    return a + b


def whoosh_sound():
    return sweep(300, 900, 0.35, volume=0.3)


def tick_sound():
    n = int(0.02 * SR)
    out = [random.uniform(-1, 1) * 0.3 * (1 - i / n) for i in range(n)]
    return out


def ambient_loop():
    n = int(4.0 * SR)
    out = []
    for i in range(n):
        t = i / SR
        s = 0.05 * math.sin(2 * math.pi * 110 * t)
        s += 0.03 * math.sin(2 * math.pi * 165 * t)
        s += 0.02 * math.sin(2 * math.pi * 220 * t + 0.5)
        s += 0.015 * math.sin(2 * math.pi * 55 * t + 1.2)
        out.append(s)
    return out


if __name__ == "__main__":
    write_wav("click.wav", click_sound())
    write_wav("confirm.wav", confirm_sound())
    write_wav("whoosh.wav", whoosh_sound())
    write_wav("tick.wav", tick_sound())
    write_wav("ambient.wav", ambient_loop())
    write_wav("step_up.wav", step_up_sound())
    write_wav("step_down.wav", step_down_sound())
