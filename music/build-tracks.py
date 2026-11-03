#!/usr/bin/env python3
"""Five original 24 s music beds, one per promo style. Fully synthesised, no samples.
Every track: groove to 18.0 s, riser, hit on the close, held chord fading to 24 s."""
import sys, wave
import numpy as np

SR = 44100; DUR = 24.0; HIT = 18.0; N = int(SR * DUR)
rng = np.random.default_rng(11)
t_ = lambda sec: np.arange(int(SR * sec)) / SR

def filt(x, lo=None, hi=None):
    """FFT band filter: lo = low-pass cutoff, hi = high-pass cutoff (Hz)."""
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    g = np.ones_like(f)
    if lo: g *= 1 / np.sqrt(1 + (f / lo) ** 4)
    if hi: g *= 1 / np.sqrt(1 + (hi / np.maximum(f, 1e-3)) ** 4)
    return np.fft.irfft(X * g, n=len(x))

def env(n, a=0.005, d=0.2, s=0.0, r=0.05):
    e = np.full(n, float(s)); ai, di, ri = int(a * SR), int(d * SR), int(r * SR)
    ai = min(ai, n); e[:ai] = np.linspace(0, 1, ai)
    end = min(n, ai + di); e[ai:end] = np.linspace(1, s, end - ai)
    if ri and s > 0 and ri < n: e[-ri:] *= np.linspace(1, 0, ri)
    return e

def add(buf, x, start):
    i = int(start * SR)
    if i >= len(buf): return
    x = x[: len(buf) - i]; buf[i:i + len(x)] += x

NAMES = {'C': -9, 'C#': -8, 'Db': -8, 'D': -7, 'D#': -6, 'Eb': -6, 'E': -5, 'F': -4, 'F#': -3, 'G': -2, 'G#': -1, 'Ab': -1, 'A': 0, 'A#': 1, 'Bb': 1, 'B': 2}
def note(nm): return 440 * 2 ** ((NAMES[nm[:-1]] + (int(nm[-1]) - 4) * 12) / 12)

def wave_(kind, f, sec, duty=0.5):
    t = t_(sec); ph = (t * f) % 1.0
    if kind == 'sine': return np.sin(2 * np.pi * f * t)
    if kind == 'saw': return 2 * ph - 1
    if kind == 'square': return np.where(ph < duty, 1.0, -1.0)
    if kind == 'tri': return 2 * np.abs(2 * ph - 1) - 1
    if kind == 'marimba': return np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-30 * t) + 0.15 * np.sin(2 * np.pi * f * 10.1 * t) * np.exp(-60 * t)
    if kind == 'epiano': return np.sin(2 * np.pi * f * t + 0.6 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-3 * t))

def kick(decay=9, pitch=45, click=0.3):
    tk = t_(0.35); k = np.sin(2 * np.pi * (pitch * tk + 6 * (1 - np.exp(-18 * tk)))) * np.exp(-decay * tk)
    return k + click * np.sin(2 * np.pi * 2200 * tk) * np.exp(-200 * tk)
def clap(): return filt(rng.standard_normal(int(0.18 * SR)), lo=3500, hi=900) * np.exp(-22 * t_(0.18))
def snare(): return (filt(rng.standard_normal(int(0.2 * SR)), lo=6000, hi=400) * np.exp(-18 * t_(0.2)) + np.sin(2 * np.pi * 190 * t_(0.2)) * np.exp(-30 * t_(0.2)) * 0.6)
def hat(open_=False):
    l = 0.3 if open_ else 0.05
    return filt(rng.standard_normal(int(l * SR)), hi=7000) * np.exp(-(8 if open_ else 90) * t_(l))
def rim(): return filt(rng.standard_normal(int(0.04 * SR)), lo=4000, hi=1500) * np.exp(-120 * t_(0.04))
def shaker(): return filt(rng.standard_normal(int(0.08 * SR)), hi=5000) * np.exp(-50 * t_(0.08))

def finish(parts, duck_times=(), duck_depth=0.5, name='x'):
    duck = np.ones(N)
    for tb in duck_times:
        i = int(tb * SR); m = int(0.18 * SR)
        duck[i:i + m] = np.minimum(duck[i:i + m], (1 - duck_depth) + duck_depth * np.linspace(0, 1, m))
    mix = parts['drums'] + (parts['bass'] + parts['keys']) * duck + parts['fx']
    mix[-int(0.6 * SR):] *= np.linspace(1, 0, int(0.6 * SR))
    mix = np.tanh(mix * 1.4) / np.tanh(1.4); mix /= np.max(np.abs(mix)) * 1.12
    st = np.stack([mix, mix], axis=1); d = int(0.012 * SR)
    st[d:, 1] = 0.85 * st[d:, 1] + 0.15 * mix[:-d]
    with wave.open(f'{sys.argv[1]}/{name}.wav', 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype('<i2').tobytes())
    print('wrote', name)

def hit_and_tail(p, chord_notes, root, kind='saw', lo=1800):
    add(p['drums'], kick() * 1.2, HIT)
    add(p['fx'], filt(rng.standard_normal(int(2.5 * SR)), hi=4000) * np.exp(-1.8 * t_(2.5)) * 0.18, HIT)
    tail = DUR - HIT
    held = sum(wave_(kind, note(n) * d, tail) for n in chord_notes for d in (0.996, 1.004))
    add(p['keys'], filt(held, lo=lo) * np.exp(-(2.7 / tail) * t_(tail)) * 0.05, HIT)
    add(p['bass'], np.sin(2 * np.pi * note(root) * t_(tail)) * np.exp(-(3.6 / tail) * t_(tail)) * 0.35, HIT)

def riser(p, bar):
    rn = rng.standard_normal(int(bar * SR)); add(p['fx'], filt(rn, hi=1500) * np.linspace(0, 1, len(rn)) ** 2 * 0.18, HIT - bar)

def parts(): return {k: np.zeros(N) for k in ('drums', 'bass', 'keys', 'fx')}

# 1. plans: bright house, 122 bpm, C G Am F, saw stabs + arp lead
def plans():
    p = parts(); BPM = 122; B = 60 / BPM; bar = 4 * B; beats = int(HIT / B)
    for b in range(beats):
        t0 = b * B
        add(p['drums'], kick() * 0.95, t0)
        if b % 2 == 1 and b >= 4: add(p['drums'], clap() * 0.5, t0)
        add(p['drums'], hat() * 0.22, t0 + B / 2)
        if b >= 8: add(p['drums'], hat(True) * 0.08, t0 + B / 2)
    prog = [(['C4', 'E4', 'G4'], 'C2'), (['G3', 'B3', 'D4'], 'G1'), (['A3', 'C4', 'E4'], 'A1'), (['F3', 'A3', 'C4'], 'F1')]
    for i in range(int(HIT / bar)):
        chord, root = prog[i % 4]
        for b in range(4):
            stab = sum(wave_('saw', note(n) * d, 0.22) for n in chord for d in (0.997, 1.003))
            add(p['keys'], filt(stab, lo=2600) * env(len(stab), d=0.2) * 0.07, i * bar + b * B + B / 2)
        pad = sum(np.sin(2 * np.pi * note(n) * t_(bar)) for n in chord)
        add(p['keys'], pad * env(int(bar * SR), a=0.25, d=bar, s=1.0, r=0.2) * 0.035, i * bar)
        for e8 in range(8):
            f = note(root) * (2 if e8 % 2 else 1); bl = B / 2 * 0.9
            add(p['bass'], filt(wave_('saw', f, bl), lo=500 + 300 * (e8 % 2)) * env(int(bl * SR), a=0.004, d=bl, s=0.6, r=0.03) * 0.3, i * bar + e8 * B / 2)
        if i >= 2:  # arp lead, 16ths
            for s16 in range(16):
                n = chord[s16 % 3]; f = note(n) * 2
                tone = np.sin(2 * np.pi * f * t_(B / 4)) * env(int(B / 4 * SR), a=0.002, d=0.12) * 0.05
                add(p['keys'], tone, i * bar + s16 * B / 4)
    riser(p, bar); hit_and_tail(p, ['C3', 'C4', 'E4', 'G4'], 'C2')
    finish(p, [b * B for b in range(beats)], 0.5, 'plans')

# 2. pixel: chiptune, 150 bpm, Em C G D, pulse arps + triangle bass + noise snare
def pixel():
    p = parts(); BPM = 150; B = 60 / BPM; bar = 4 * B; beats = int(HIT / B)
    for b in range(beats):
        t0 = b * B
        add(p['drums'], kick(decay=14, pitch=60, click=0.5) * 0.8, t0)
        if b % 2 == 1: add(p['drums'], filt(rng.standard_normal(int(0.12 * SR)), hi=2000) * np.exp(-40 * t_(0.12)) * 0.45, t0)
        for q in (0.25, 0.5, 0.75): add(p['drums'], filt(rng.standard_normal(int(0.03 * SR)), hi=8000) * np.exp(-150 * t_(0.03)) * 0.18, t0 + q * B)
    prog = [(['E4', 'G4', 'B4'], 'E2'), (['C4', 'E4', 'G4'], 'C2'), (['G4', 'B4', 'D5'], 'G2'), (['D4', 'F#4', 'A4'], 'D2')]
    for i in range(int(HIT / bar)):
        chord, root = prog[i % 4]
        for s16 in range(16):
            n = chord[[0, 1, 2, 1][s16 % 4]]; f = note(n) * (2 if s16 % 8 >= 4 else 1)
            tone = wave_('square', f, B / 4 * 0.9, duty=0.25) * env(int(B / 4 * 0.9 * SR), a=0.001, d=0.1, s=0.3, r=0.02) * 0.06
            add(p['keys'], tone, i * bar + s16 * B / 4)
        for e8 in range(8):
            f = note(root) * (2 if e8 in (3, 7) else 1)
            add(p['bass'], wave_('tri', f, B / 2 * 0.95) * env(int(B / 2 * 0.95 * SR), a=0.002, d=0.3, s=0.5, r=0.02) * 0.32, i * bar + e8 * B / 2)
        if i % 2 == 1:  # pulse chord stab on the 2 and 4
            for b in (1, 3):
                st = sum(wave_('square', note(n), 0.18, duty=0.5) for n in chord)
                add(p['keys'], st * env(int(0.18 * SR), d=0.15) * 0.035, i * bar + b * B)
    riser(p, bar); hit_and_tail(p, ['E3', 'E4', 'G4', 'B4'], 'E2', kind='square', lo=3000)
    finish(p, [b * B for b in range(beats)], 0.35, 'pixel')

# 3. dark: warm minimal, 88 bpm, Dm Bb F C, e-piano + sub + rim and shaker
def dark():
    p = parts(); BPM = 88; B = 60 / BPM; bar = 4 * B; beats = int(HIT / B)
    for b in range(beats):
        t0 = b * B
        if b % 2 == 0: add(p['drums'], kick(decay=6, pitch=40, click=0.1) * 0.8, t0)
        if b % 2 == 1: add(p['drums'], rim() * 0.5, t0)
        for q in (0, 0.5): add(p['drums'], shaker() * (0.12 if q else 0.07), t0 + q * B)
    prog = [(['D3', 'F3', 'A3', 'C4'], 'D1'), (['Bb2', 'D3', 'F3', 'A3'], 'Bb0'), (['F3', 'A3', 'C4', 'E4'], 'F1'), (['C3', 'E3', 'G3', 'B3'], 'C1')]
    for i in range(int(HIT / bar)):
        chord, root = prog[i % 4]
        ep = sum(wave_('epiano', note(n) * d, bar * 0.98) for n in chord for d in (0.999, 1.001))
        trem = 1 + 0.12 * np.sin(2 * np.pi * 4.5 * t_(bar * 0.98))
        add(p['keys'], ep * trem * env(int(bar * 0.98 * SR), a=0.02, d=bar, s=0.35, r=0.3) * 0.04, i * bar)
        sub = np.sin(2 * np.pi * note(root) * 2 * t_(bar)) * env(int(bar * SR), a=0.02, d=bar, s=0.7, r=0.2)
        add(p['bass'], sub * 0.4, i * bar)
        pad = sum(np.sin(2 * np.pi * note(n) * 2 * t_(bar)) for n in chord[:3])
        add(p['keys'], filt(pad, lo=900) * env(int(bar * SR), a=0.6, d=bar, s=1.0, r=0.4) * 0.018, i * bar)
        if i >= 1:  # a slow melody note on beat 3
            m = ['A4', 'F4', 'E4', 'G4'][i % 4]
            add(p['keys'], wave_('epiano', note(m), B * 1.6) * env(int(B * 1.6 * SR), a=0.01, d=1.2, s=0.2) * 0.05, i * bar + 2 * B)
    riser(p, bar); hit_and_tail(p, ['D3', 'D4', 'F4', 'A4'], 'D1', kind='epiano', lo=2500)
    finish(p, [b * B for b in range(0, beats, 2)], 0.25, 'dark')

# 4. blobs: playful marimba, 108 bpm swung, G D Em C, claps and woodblock
def blobs():
    p = parts(); BPM = 108; B = 60 / BPM; bar = 4 * B; beats = int(HIT / B); sw = 0.08 * B
    for b in range(beats):
        t0 = b * B
        if b % 2 == 0: add(p['drums'], kick(decay=10, pitch=55, click=0.2) * 0.7, t0)
        if b % 2 == 1: add(p['drums'], clap() * 0.45, t0)
        add(p['drums'], rim() * 0.35, t0 + B / 2 + sw)
        if b % 4 == 3: add(p['drums'], rim() * 0.25, t0 + 3 * B / 4 + sw)
    prog = [(['G3', 'B3', 'D4'], 'G1'), (['D3', 'F#3', 'A3'], 'D1'), (['E3', 'G3', 'B3'], 'E1'), (['C3', 'E3', 'G3'], 'C1')]
    melody = ['B4', 'D5', 'G4', 'A4', 'B4', 'G4', 'D5', 'E5']
    for i in range(int(HIT / bar)):
        chord, root = prog[i % 4]
        for e8 in range(8):
            t0 = i * bar + e8 * B / 2 + (sw if e8 % 2 else 0)
            n = melody[(e8 + i * 3) % 8]
            add(p['keys'], wave_('marimba', note(n), 0.4) * env(int(0.4 * SR), a=0.002, d=0.35) * 0.09, t0)
            if e8 % 2 == 0:
                tri = sum(wave_('marimba', note(c), 0.3) for c in chord)
                add(p['keys'], tri * env(int(0.3 * SR), a=0.002, d=0.25) * 0.035, t0)
        for q in range(4):
            f = note(root) * (2 if q in (1, 3) else 1)
            add(p['bass'], filt(wave_('tri', f, B * 0.8), lo=600) * env(int(B * 0.8 * SR), a=0.004, d=0.4, s=0.4, r=0.05) * 0.3, i * bar + q * B)
    riser(p, bar); hit_and_tail(p, ['G3', 'G4', 'B4', 'D5'], 'G1', kind='marimba', lo=4000)
    finish(p, [b * B for b in range(0, beats, 2)], 0.3, 'blobs')

# 5. kinetic: driving, 126 bpm, Fm Db Ab Eb, offbeat saw bass, big kick, open hats, sidechained pad
def kinetic():
    p = parts(); BPM = 126; B = 60 / BPM; bar = 4 * B; beats = int(HIT / B)
    for b in range(beats):
        t0 = b * B
        add(p['drums'], kick(decay=8, pitch=48, click=0.4) * 1.0, t0)
        if b % 2 == 1 and b >= 4: add(p['drums'], clap() * 0.45, t0); add(p['drums'], snare() * 0.27, t0)
        add(p['drums'], hat(True) * 0.16, t0 + B / 2)
        add(p['drums'], hat() * 0.12, t0 + B / 4); add(p['drums'], hat() * 0.12, t0 + 3 * B / 4)
    prog = [(['F3', 'Ab3', 'C4'], 'F1'), (['Db3', 'F3', 'Ab3'], 'Db1'), (['Ab3', 'C4', 'Eb4'], 'Ab1'), (['Eb3', 'G3', 'Bb3'], 'Eb1')]
    for i in range(int(HIT / bar)):
        chord, root = prog[i % 4]
        pad = sum(wave_('saw', note(n) * d, bar) for n in chord for d in (0.995, 1.0, 1.005))
        add(p['keys'], filt(pad, lo=1400) * env(int(bar * SR), a=0.1, d=bar, s=1.0, r=0.1) * 0.03, i * bar)
        for e8 in range(8):
            if e8 % 2 == 0: continue  # off-beats only
            f = note(root) * 2; bl = B / 2 * 0.8
            add(p['bass'], filt(wave_('saw', f, bl), lo=700) * env(int(bl * SR), a=0.003, d=bl, s=0.5, r=0.03) * 0.34, i * bar + e8 * B / 2)
        if i >= 1:  # octave stabs on the "and" of 2 and 4
            for b in (1, 3):
                st = sum(wave_('saw', note(n) * 2, 0.15) for n in chord)
                add(p['keys'], filt(st, lo=3000) * env(int(0.15 * SR), d=0.12) * 0.045, i * bar + b * B + B / 2)
    riser(p, bar); hit_and_tail(p, ['F3', 'F4', 'Ab4', 'C5'], 'F1')
    finish(p, [b * B for b in range(beats)], 0.6, 'kinetic')

if __name__ == '__main__':
    for fn in (plans, pixel, dark, blobs, kinetic): fn()
