#!/usr/bin/env python3
"""Genera base house limpia o tech.
  python3 render_base_electronica.py --style tech --bpm 118 --bars 16 --out ./base
"""
from __future__ import annotations
import argparse, os, sys
import numpy as np
from scipy.io import wavfile
from scipy import signal

SR = 44100

def midi_hz(m):
    return 440.0 * (2.0 ** ((m - 69) / 12.0))

def filt(x, kind, *cuts, order=2):
    wn = [min(max(c / (SR * 0.5), 1e-4), 0.99) for c in cuts]
    if kind == "band":
        b, a = signal.butter(order, wn, btype="band")
    else:
        b, a = signal.butter(order, wn[0], btype=kind)
    return signal.lfilter(b, a, np.asarray(x, np.float32)).astype(np.float32)

def add_at(dest, src, t, g=1.0):
    i0 = int(t * SR)
    if i0 >= len(dest) or i0 < 0:
        return
    src = np.asarray(src, np.float32)
    i1 = min(len(dest), i0 + len(src))
    dest[i0:i1] += src[: i1 - i0] * np.float32(g)

def kick(tech=False):
    n = int(0.36 * SR)
    t = np.arange(n, dtype=np.float32) / SR
    freq = (42.0 if tech else 48.0) + (95.0 if tech else 70.0) * np.exp(-t / 0.02)
    body = np.sin(np.cumsum(freq) * (2 * np.pi / SR)) * np.exp(-t / (0.15 if tech else 0.11))
    punch = np.sin(2 * np.pi * 210 * t) * np.exp(-t / 0.025) * (0.45 if tech else 0.22)
    cn = int(0.0035 * SR)
    click = np.zeros(n, np.float32)
    click[:cn] = np.hanning(cn).astype(np.float32)
    click = filt(click, "high", 2200) * (0.4 if tech else 0.28)
    k = np.tanh(body + punch + click)
    return (k / (np.max(np.abs(k)) + 1e-9)).astype(np.float32)

def hat(bright=False):
    rng = np.random.default_rng(3)
    n = int(0.05 * SR)
    t = np.arange(n, dtype=np.float32) / SR
    s = rng.normal(0, 1, n).astype(np.float32) + np.sin(2 * np.pi * 9000 * t)
    s = filt(s, "band", 7000 if bright else 5500, 16000)
    s *= np.exp(-t / (0.02 if bright else 0.016))
    return (s / (np.max(np.abs(s)) + 1e-9) * (0.2 if bright else 0.14)).astype(np.float32)

def clap():
    rng = np.random.default_rng(5)
    n = int(0.16 * SR)
    t = np.arange(n, dtype=np.float32) / SR
    s = np.zeros(n, np.float32)
    for off, amp in ((0.0, 1.0), (0.011, 0.55), (0.02, 0.28)):
        i = int(off * SR)
        bn = int(0.024 * SR)
        burst = rng.normal(0, 1, bn).astype(np.float32) * np.hanning(bn).astype(np.float32)
        if i + bn <= n:
            s[i : i + bn] += burst * amp
    s = filt(s, "band", 900, 4000) * np.exp(-t / 0.05)
    return (s / (np.max(np.abs(s)) + 1e-9) * 0.3).astype(np.float32)

def sub(freq, dur):
    n = int(dur * SR)
    t = np.arange(n, dtype=np.float32) / SR
    env = np.minimum(t / 0.007, 1.0) * np.exp(-t / (dur * 0.6))
    return filt(np.sin(2 * np.pi * freq * t) * env * 0.7, "low", 100)

def midbass(freq, dur):
    n = int(dur * SR)
    t = np.arange(n, dtype=np.float32) / SR
    env = np.minimum(t / 0.01, 1.0) * np.exp(-t / (dur * 0.36))
    s = filt(np.sign(np.sin(2 * np.pi * freq * t)), "low", 360)
    s = filt(s, "high", 70)
    return np.tanh(s * env * 0.5).astype(np.float32)

def write_st(path, mono):
    peak = float(np.max(np.abs(mono)) + 1e-12)
    y = np.tanh(mono * np.float32(0.88 / peak)).astype(np.float32)
    d = int(0.006 * SR)
    r = np.empty_like(y)
    r[:d] = y[:d]
    r[d:] = y[:-d] * 0.98
    wavfile.write(path, SR, (np.clip(np.stack([y, r], 1), -1, 1) * 32767).astype(np.int16))
    print("wrote", path, "dur", len(y) / SR)

def render(style, bpm, seconds):
    beat = 60.0 / bpm
    n = int(seconds * SR)
    mix = np.zeros(n, np.float32)
    k, h, hb, c = kick(style == "tech"), hat(False), hat(True), clap()
    d1, d2 = midi_hz(26), midi_hz(38)
    t = 0.0
    bi = 0
    while t < seconds - 0.02:
        add_at(mix, k, t, 1.0)
        add_at(mix, h, t, 0.3)
        add_at(mix, hb, t + 0.5 * beat, 0.95)
        add_at(mix, h, t + 0.25 * beat, 0.2)
        add_at(mix, h, t + 0.75 * beat, 0.28)
        if bi % 2 == 1:
            add_at(mix, c, t, 0.9)
        if bi % 2 == 0:
            add_at(mix, sub(d1, beat * 1.65), t, 1.0)
        if style == "tech":
            add_at(mix, midbass(d2, beat * 0.4), t + 0.5 * beat, 1.0)
        t += beat
        bi += 1
    return filt(filt(mix, "high", 26), "low", 14000)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--style", choices=["limpia", "tech"], default="tech")
    p.add_argument("--bpm", type=float, default=118.0)
    p.add_argument("--seconds", type=float, default=0.0)
    p.add_argument("--bars", type=int, default=16)
    p.add_argument("--out", default="./base_skill")
    args = p.parse_args()
    beat = 60.0 / args.bpm
    seconds = args.seconds if args.seconds > 0 else args.bars * 4 * beat
    print("style", args.style, "bpm", args.bpm, "seconds", seconds)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    write_st(args.out + ".wav", render(args.style, args.bpm, seconds))

if __name__ == "__main__":
    sys.exit(main() or 0)
