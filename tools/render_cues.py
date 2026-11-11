#!/usr/bin/env python3
"""
저승공무원으로 취업했습니다!!! — 음향 큐 렌더러

모든 음악은 이 스크립트에서 직접 작곡한 원곡이며,
악기 소리는 FluidR3 GM 사운드폰트(MIT 라이선스, 실제 악기 녹음 샘플)로 렌더링하고,
효과음(바람·천둥·도장·타이핑·박수·동전 등)은 numpy로 합성합니다.
→ 결과물은 저작권 걱정 없이 공연에 사용할 수 있습니다.

필요: python3, numpy, scipy, mido, fluidsynth, ffmpeg, FluidR3_GM.sf2
실행: python3 tools/render_cues.py   (패키지 폴더에서)
"""
import os, json, subprocess, tempfile, shutil
import numpy as np
import mido
from scipy.io import wavfile
from scipy import signal

SR = 48000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "audio")
SF2 = next((p for p in ["/usr/share/sounds/sf2/FluidR3_GM.sf2",
                        os.path.join(ROOT, "tools", "FluidR3_GM.sf2")] if os.path.exists(p)), None)
RNG = np.random.default_rng(4444)

# ───────────────────────── MIDI 작곡 도구 ─────────────────────────
class Score:
    def __init__(self, bpm):
        self.bpm, self.ev, self.setup = bpm, [], {}
    def prog(self, ch, p, vol=100, pan=64, rev=50):
        self.setup[ch] = (p, vol, pan, rev); return self
    def n(self, ch, beat, dur, pitch, vel=90):
        for p in (pitch if isinstance(pitch, (list, tuple)) else [pitch]):
            self.ev.append((beat, 1, ('on', ch, p, vel)))
            self.ev.append((beat + dur, 0, ('off', ch, p, 0)))
        return self
    def seq(self, ch, notes, vel=90, offset=0, transpose=0):
        for b, d, p in notes:
            if p is None: continue
            p = [x + transpose for x in p] if isinstance(p, (list, tuple)) else p + transpose
            self.n(ch, offset + b, d, p, vel)
        return self
    def cc(self, ch, beat, c, v):
        self.ev.append((beat, 0, ('cc', ch, c, int(max(0, min(127, v))))))
    def ramp(self, ch, b0, b1, v0, v1, c=11, steps=24):
        for i in range(steps + 1):
            self.cc(ch, b0 + (b1 - b0) * i / steps, c, v0 + (v1 - v0) * i / steps)
    def bend(self, ch, beat, v):
        self.ev.append((beat, 0, ('bend', ch, int(max(-8192, min(8191, v))), 0)))
    def sec(self, beat): return beat * 60.0 / self.bpm
    def length(self): return max(b for b, _, _ in self.ev)

    def render(self, tail=3.0):
        tpb = 480
        mid = mido.MidiFile(ticks_per_beat=tpb); tr = mido.MidiTrack(); mid.tracks.append(tr)
        tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(self.bpm), time=0))
        for ch, (p, vol, pan, rev) in self.setup.items():
            if ch != 9: tr.append(mido.Message('program_change', channel=ch, program=p, time=0))
            for c, v in ((7, vol), (10, pan), (91, rev), (11, 127)):
                tr.append(mido.Message('control_change', channel=ch, control=c, value=v, time=0))
        end = self.length() + tail * self.bpm / 60.0
        evs = sorted(self.ev + [(end, 0, ('cc', 0, 110, 0))], key=lambda e: (e[0], e[1]))
        last = 0
        for beat, _, e in evs:
            t = int(round(beat * tpb)); dt = max(0, t - last); last = max(last, t)
            k = e[0]
            if k == 'on':   m = mido.Message('note_on', channel=e[1], note=e[2], velocity=e[3], time=dt)
            elif k == 'off': m = mido.Message('note_off', channel=e[1], note=e[2], velocity=0, time=dt)
            elif k == 'cc':  m = mido.Message('control_change', channel=e[1], control=e[2], value=e[3], time=dt)
            else:            m = mido.Message('pitchwheel', channel=e[1], pitch=e[2], time=dt)
            tr.append(m)
        with tempfile.TemporaryDirectory() as d:
            mp, wp = os.path.join(d, 'a.mid'), os.path.join(d, 'a.wav')
            mid.save(mp)
            subprocess.run(['fluidsynth', '-ni', '-q', '-g', '0.55', '-r', str(SR), '-F', wp, SF2, mp],
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            sr, x = wavfile.read(wp)
        x = x.astype(np.float32) / 32768.0
        return x if x.ndim == 2 else np.stack([x, x], 1)

# ───────────────────────── DSP / 효과음 합성 ─────────────────────────
def T(d): return np.arange(int(d * SR)) / SR
def st(m, pan=0.0):
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    return np.stack([m * l * 1.414, m * r * 1.414], 1).astype(np.float32)
def filt(x, f, kind='low', order=4):
    sos = signal.butter(order, f, btype=kind, fs=SR, output='sos')
    return signal.sosfilt(sos, x, axis=0)
def noise(d): return RNG.standard_normal(int(d * SR)).astype(np.float32)
def mix(total, parts):
    out = np.zeros((int(total * SR), 2), np.float32)
    for at, a in parts:
        i = int(at * SR); j = min(len(out), i + len(a))
        if j > i: out[i:j] += a[:j - i]
    return out
def reverb(x, rt=1.6, wet=0.22):
    t = T(rt * 1.2)
    ir = np.stack([noise(len(t) / SR) * np.exp(-6.9 * t / rt) for _ in range(2)], 1)
    ir = filt(ir, 5000); ir /= np.sqrt((ir ** 2).sum(0))
    pad = np.vstack([x, np.zeros((len(ir), 2), np.float32)])
    w = np.stack([signal.fftconvolve(pad[:, c], ir[:, c])[:len(pad)] for c in range(2)], 1)
    return (pad * (1 - wet * 0.5) + w * wet).astype(np.float32)

def boing(d=0.9):
    t = T(d)
    f = 210 + 420 * (1 - np.exp(-9 * t)) + 70 * np.exp(-3.5 * t) * np.sin(2 * np.pi * 13 * t)
    ph = 2 * np.pi * np.cumsum(f) / SR
    m = (np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph)) * np.exp(-3.2 * t)
    m[:240] *= np.linspace(0, 1, 240)
    return reverb(st(m * 0.6), 0.8, 0.15)

def busy_tone(n=3):
    t = T(0.5); b = (np.sin(2 * np.pi * 480 * t) + np.sin(2 * np.pi * 620 * t)) * 0.3
    b *= np.minimum(1, np.minimum(t, 0.5 - t) / 0.008)
    m = np.concatenate([np.concatenate([b, np.zeros(len(b))]) for _ in range(n)])
    m = filt(np.tanh(m * 1.6), [300, 3400], 'band', 2)
    return st(m.astype(np.float32) * 0.8)

def wind(d=12):
    x = noise(d); out = np.zeros_like(x); blk = 2048; zi = None
    lfo = lambda tt: 0.5 + 0.5 * np.sin(2 * np.pi * 0.11 * tt + 1.3) * np.sin(2 * np.pi * 0.047 * tt)
    for i in range(0, len(x), blk):
        tt = i / SR; c = 260 + 520 * lfo(tt)
        sos = signal.butter(2, [c * 0.7, c * 1.4], 'band', fs=SR, output='sos')
        if zi is None: zi = signal.sosfilt_zi(sos) * 0
        out[i:i + blk], zi = signal.sosfilt(sos, x[i:i + blk], zi=zi)
    t = T(d); env = (0.35 + 0.65 * lfo(t)) * np.minimum(1, t / 2.5) * np.minimum(1, (d - t) / 3)
    m = out * env * 0.9
    return np.stack([m, np.roll(m, 900)], 1).astype(np.float32)

def gong(d=6, f0=68):
    t = T(d); m = np.zeros_like(t)
    for k, (r, dec, a) in enumerate([(1, 5, 1), (1.48, 4, .6), (2.13, 3.4, .5), (2.98, 2.6, .35),
                                     (3.52, 2.2, .3), (4.37, 1.8, .22), (5.9, 1.2, .15)]):
        m += a * np.sin(2 * np.pi * f0 * r * t + k) * np.exp(-t / dec) * (1 + 0.15 * np.sin(2 * np.pi * (0.7 + k * .3) * t))
    m *= np.minimum(1, t / 0.015)
    strike = filt(noise(0.08), 1200) * np.exp(-T(0.08) * 40) * 0.6
    m[:len(strike)] += strike
    return reverb(st(m / 3.2), 2.4, 0.3)

def sub_boom(d=1.6, f=48):
    t = T(d); ph = 2 * np.pi * np.cumsum(f * (1 + 0.8 * np.exp(-t * 18))) / SR
    return st(np.sin(ph) * np.exp(-t * 2.4) * 0.9)

def thunder(d=6.5):
    t = T(d)
    crack = filt(noise(0.5), 1800, 'high') * np.exp(-T(0.5) * 9) * 0.8
    bumps = np.zeros(len(t))
    for _ in range(14):
        c, w, a = RNG.uniform(0.1, 3.5), RNG.uniform(0.2, 0.9), RNG.uniform(0.4, 1)
        bumps += a * np.exp(-((t - c) / w) ** 2)
    bumps = bumps / bumps.max() * np.minimum(1, (d - t) / 2.5)
    rum = np.stack([filt(noise(d), 160) for _ in range(2)], 1) * bumps[:, None] * 2.4
    mid = np.stack([filt(noise(d), [150, 900], 'band', 2) for _ in range(2)], 1) * (bumps ** 2)[:, None] * 0.8
    out = rum + mid; out[:len(crack)] += st(crack)
    return reverb(out.astype(np.float32), 2.0, 0.2)

def stamp():
    t = T(0.35)
    thump = np.sin(2 * np.pi * np.cumsum(55 + 110 * np.exp(-t * 30)) / SR) * np.exp(-t * 16)
    knock = filt(noise(0.35), [250, 700], 'band', 2) * np.exp(-t * 45) * 2.2
    click = filt(noise(0.35), 2500, 'high') * np.exp(-t * 160) * 0.5
    return reverb(st((thump + knock + click) * 0.85), 0.6, 0.12)

def keystroke(v=1.0):
    t = T(0.06)
    a = filt(noise(0.06), [1800, 5500], 'band', 2) * np.exp(-t * 260)
    b = filt(noise(0.06), [180, 450], 'band', 2) * np.exp(-t * 90) * 1.6
    return st((a + b) * 0.55 * v, RNG.uniform(-.2, .2))

def typing(d=1.5):
    parts, at = [], 0.0
    while at < d:
        parts.append((at, keystroke(RNG.uniform(.7, 1)))); at += RNG.uniform(0.07, 0.15)
    return mix(d + 0.1, parts)

def enter_key():
    t = T(0.2)
    m = filt(noise(0.2), [900, 4000], 'band', 2) * np.exp(-t * 120) + \
        np.sin(2 * np.pi * np.cumsum(140 + 80 * np.exp(-t * 40)) / SR) * np.exp(-t * 30) * 0.7
    return st(m * 0.8)

def clap(f):
    t = T(0.05)
    return filt(noise(0.05), [f * 0.6, f * 1.6], 'band', 2) * (np.exp(-t * 90) + 0.4 * np.exp(-t * 400))

def applause(d=3.5, people=45):
    out = np.zeros((int(d * SR), 2), np.float32); t = T(d)
    for _ in range(people):
        f, pan, rate = RNG.uniform(800, 2600), RNG.uniform(-.9, .9), RNG.uniform(3.2, 5.5)
        at = RNG.uniform(0, 0.25)
        while at < d - 0.06:
            c = st(clap(f) * RNG.uniform(.5, 1), pan); i = int(at * SR)
            out[i:i + len(c)] += c; at += 1 / rate * RNG.uniform(.85, 1.15)
    env = np.minimum(1, t / 0.25) * np.minimum(1, (d - t) / 1.2)
    return reverb(out * env[:, None] * 0.12, 1.2, 0.25)

def popper():
    t = T(0.6)
    pop = noise(0.6) * np.exp(-t * 70) * 1.2
    crackle = np.zeros(len(t))
    for _ in range(40):
        i = int(RNG.uniform(0.02, 0.45) * SR); crackle[i:i + 120] += RNG.uniform(.2, .6) * noise(120 / SR)
    rustle = filt(noise(0.6), 3000, 'high') * np.exp(-t * 5) * 0.25
    return reverb(st(filt(pop + crackle + rustle, 9000) * 0.7), 0.9, 0.15)

def coin(f):
    t = T(0.6); m = np.zeros(len(t))
    for r, a, dec in [(1, 1, 9), (2.32, .6, 12), (4.25, .45, 16), (6.63, .3, 22)]:
        m += a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * dec)
    return m * np.minimum(1, t / 0.001) * 0.18

def coins(n=7):
    parts = []
    for i in range(n):
        parts.append((i * 0.09 + RNG.uniform(0, .04), st(coin(RNG.uniform(2300, 3600)), RNG.uniform(-.5, .5))))
    return reverb(mix(n * 0.1 + 0.7, parts), 0.7, 0.18)

def heartbeat(d=9):
    parts, at, gap = [], 0.4, 1.1
    def thump(v):
        t = T(0.25)
        return st(np.sin(2 * np.pi * np.cumsum(38 + 40 * np.exp(-t * 25)) / SR) * np.exp(-t * 18) * v)
    while at < d - 0.4:
        parts += [(at, thump(0.9)), (at + 0.17, thump(0.6))]
        at += gap; gap = max(0.42, gap * 0.9)
    return mix(d, parts)

def water(d):
    out = np.zeros((int(d * SR), 2), np.float32)
    for _ in range(int(d * 22)):
        dd = RNG.uniform(0.02, 0.07); t = T(dd); f0 = RNG.uniform(350, 1300)
        b = np.sin(2 * np.pi * np.cumsum(f0 * (1 + 2.5 * t / dd)) / SR) * np.exp(-t * 60) * RNG.uniform(.2, .6)
        c = st(b, RNG.uniform(-.8, .8)); i = int(RNG.uniform(0, d - .1) * SR); out[i:i + len(c)] += c
    stream = np.stack([filt(noise(d), [300, 1800], 'band', 2) for _ in range(2)], 1) * 0.12
    return reverb((out * 0.25 + stream).astype(np.float32), 1.0, 0.25)

# ───────────────────────── 화성·선율 재료 ─────────────────────────
C, Am, F, G = [60, 64, 67], [57, 60, 64], [53, 57, 60], [55, 59, 62]
MAIN_MEL = [  # 오프닝·커튼콜·하우스 공통 주제 (C장조, 8마디 + 마무리)
    (0, .5, 72), (.5, .5, 76), (1, 1, 79), (2, .5, 76), (2.5, .5, 79), (3, 1, 84),
    (4, 1, 81), (5, .5, 79), (5.5, .5, 76), (6, 2, 72),
    (8, .5, 77), (8.5, .5, 81), (9, 1, 84), (10, .5, 81), (10.5, .5, 77), (11, 1, 74),
    (12, 1.5, 79), (13.5, .5, 77), (14, .5, 76), (14.5, .5, 74), (15, 1, 71),
    (16, .5, 72), (16.5, .5, 76), (17, 1, 79), (18, .5, 76), (18.5, .5, 79), (19, 1, 84),
    (20, 1, 81), (21, .5, 84), (21.5, .5, 81), (22, 2, 79),
    (24, .5, 77), (24.5, .5, 76), (25, .5, 74), (25.5, .5, 72), (26, 1, 74), (27, 1, 76),
    (28, 2, 74), (30, .5, 79), (30.5, .5, 77), (31, .5, 76), (31.5, .5, 74)]
MAIN_CH = [C, Am, F, G, C, Am, F, G]

def band(s, bars, chords, off=0, drums=True, full=False, guitar=True):
    for i, ch in enumerate(chords[:bars]):
        b0 = off + i * 4; root = ch[0] - 24 if ch[0] >= 57 else ch[0] - 12
        s.n(3, b0, 1.8, root, 95); s.n(3, b0 + 2, 1.8, root + 7, 85)
        if guitar:
            for k in (0.5, 1.5, 2.5, 3.5): s.n(2, b0 + k, 0.35, ch, 70)
        if drums:
            s.n(9, b0, .3, 36, 90); s.n(9, b0 + 2, .3, 36, 80)
            s.n(9, b0 + 1, .3, 38 if full else 37, 80 if full else 70); s.n(9, b0 + 3, .3, 38 if full else 37, 80 if full else 70)
            for k in range(8): s.n(9, b0 + k * .5, .2, 42 if full else 82, 60 if k % 2 == 0 else 42)
            if full: s.n(9, b0 + 1, .3, 54, 60); s.n(9, b0 + 3, .3, 54, 60)

def loop_wrap(x, loop_sec):
    L = int(loop_sec * SR); y = x[:L].copy(); tail = x[L:L + L]
    y[:len(tail)] += tail; return y

# ───────────────────────── 큐 음원 ─────────────────────────
def opening():
    s = Score(132).prog(0, 9, 100, 64, 40).prog(1, 73, 70, 54, 40).prog(2, 24, 95, 80, 30).prog(3, 32, 105).prog(9, 0, 95)
    s.seq(0, MAIN_MEL, 100); s.seq(1, MAIN_MEL, 70)
    band(s, 8, MAIN_CH)
    s.n(0, 32, 2, 84, 110); s.n(1, 32, 2, 72, 90); s.n(2, 32, 2, C, 90); s.n(3, 32, 2, 36, 110)
    s.n(9, 32, 2, 49, 100); s.n(9, 32, .3, 36, 110)
    return s.render(3)

def house():
    s = Score(96).prog(0, 8, 90, 64, 70).prog(4, 0, 70, 64, 70).prog(3, 32, 85)
    s.seq(0, MAIN_MEL, 80)
    for i, ch in enumerate(MAIN_CH):
        for k, p in enumerate([ch[0] - 12, ch[1] - 12, ch[2] - 12, ch[1]]): s.n(4, i * 4 + k, 1.5, p, 55)
        s.n(3, i * 4, 3.5, ch[0] - 24, 70)
    return loop_wrap(s.render(4), s.sec(32))

def curtain():
    s = Score(144).prog(0, 9, 100, 60, 40).prog(1, 56, 95, 70, 50).prog(2, 24, 90, 84, 30) \
                  .prog(3, 32, 110).prog(4, 61, 85, 44, 50).prog(5, 47, 100, 64, 50).prog(9, 0, 110)
    s.seq(0, MAIN_MEL, 100); s.seq(0, MAIN_MEL, 105, offset=32)
    s.seq(1, MAIN_MEL, 95, offset=32, transpose=-12)
    band(s, 8, MAIN_CH, 0, True, True); band(s, 8, MAIN_CH, 32, True, True)
    for i, ch in enumerate(MAIN_CH * 2):
        s.n(4, i * 4 + 3.5, .4, [p - 12 for p in ch], 90)
    s.n(9, 0, 2, 49, 100); s.n(9, 32, 2, 49, 110)
    for k in range(16): s.n(5, 62 + k * 0.125, .12, 43, 60 + k * 4)   # 팀파니 롤
    s.n(0, 64, 3, 84, 120); s.n(1, 64, 3, [72, 76, 79], 115); s.n(4, 64, 3, [48, 55, 60, 64], 115)
    s.n(2, 64, 3, C, 100); s.n(3, 64, 3, 36, 120); s.n(5, 64, 1, 36, 127)
    s.n(9, 64, 3, 49, 127); s.n(9, 64, 3, 57, 120); s.n(9, 64, .3, 36, 127)
    return s.render(3.5)

def jingle():
    s = Score(120).prog(0, 6, 100, 50, 60).prog(1, 45, 110, 78, 60).prog(2, 47, 110).prog(3, 8, 80, 64, 70)
    s.seq(0, [(0, .5, 69), (.5, .5, 72), (1, .5, 71), (1.5, .5, 70), (2, .5, 69), (2.5, .5, 68), (3, 1, 64),
              (4, .5, 65), (4.5, .5, 64), (5, .5, 63), (5.5, .5, 62), (6, 1.5, 57)], 100)
    s.seq(1, [(i * .5, .4, p) for i, p in enumerate([45, 52, 44, 52, 43, 52, 42, 52, 41, 48, 40, 47])] + [(6, 1, 33)], 105)
    s.n(2, 6, 1, 45, 115)
    s.seq(3, [(6.5, .2, 81), (6.625, .2, 84), (6.75, .2, 88), (6.875, .8, 93)], 85)
    return s.render(2.5)

def auditor():
    s = Score(60).prog(0, 61, 110, 64, 60).prog(1, 47, 110).prog(2, 43, 110).prog(3, 48, 100, 64, 60)
    for k in range(32): s.n(1, k * 0.0625, .06, 38, 50 + k * 2)
    s.n(0, 0.3, 3.8, [38, 45, 50, 53], 100); s.ramp(0, 0.3, 2.0, 30, 127)
    s.n(3, 2.0, 3, [50, 57, 62, 65], 95); s.n(2, 2.0, 3.5, 26, 115); s.n(1, 2.0, 1, 38, 127)
    x = s.render(3)
    return mix(len(x) / SR + 3, [(0, x), (2.0, gong(5.5) * 0.9)])

def fanfare_score(s, off=0, applause_after=True):
    s.prog(0, 56, 110, 54, 50).prog(1, 56, 100, 74, 50).prog(2, 57, 105, 64, 50).prog(3, 47, 110).prog(9, 0, 100)
    s.seq(0, [(0, 1/3, 67), (1/3, 1/3, 67), (2/3, 1/3, 67), (1, 1.5, 72), (2.5, .5, 67), (3, .5, 72), (3.5, .5, 76), (4, 2.5, 79)], 115, off)
    s.seq(1, [(0, 1/3, 64), (1/3, 1/3, 64), (2/3, 1/3, 64), (1, 1.5, 67), (2.5, .5, 64), (3, .5, 67), (3.5, .5, 72), (4, 2.5, 76)], 105, off)
    s.seq(2, [(1, 1.5, 48), (2.5, 1.5, 55), (4, 2.5, [48, 60])], 105, off)
    s.n(3, off + 1, .5, 48, 120); s.n(3, off + 4, .5, 48, 127)
    for k in range(12): s.n(3, off + 4.5 + k * .125, .12, 43, 70 + k * 3)
    s.n(9, off + 4, 2, 49, 115); s.n(9, off + 4, .3, 36, 120)

def fanfare(extra_applause=True):
    s = Score(120); fanfare_score(s)
    x = s.render(2.5)
    parts = [(0, x)]
    if extra_applause: parts.append((2.0, applause(3.5)))
    return mix(max(len(x) / SR, 5.6), parts)

def comic_fanfare():
    s = Score(132); fanfare_score(s)
    x = s.render(2.5)
    return mix(5.6, [(0.0, popper()), (0.15, x), (1.9, applause(3.5) * 1.1), (2.0, popper() * 0.8)])

def pass_notice():
    s = Score(60).prog(0, 11, 110, 64, 60).prog(1, 8, 70, 64, 60)
    s.n(0, 0, .5, 84, 110); s.n(1, 0, .5, 96, 60); s.n(0, .45, 1, 79, 105); s.n(1, .45, 1, 91, 55)
    ars = s.render(1.0)
    return mix(9.5, [(0, ars), (1.9, fanfare())])

def scare():
    s = Score(60).prog(0, 44, 110, 64, 70).prog(1, 55, 110).prog(2, 43, 110)
    s.n(1, 0, 1, [36, 48], 120); s.n(0, 0, 1.6, [83, 84, 85], 95); s.ramp(0, 0, 1.6, 127, 30)
    s.n(2, 0, 1.6, 28, 110)
    x = s.render(2)
    return mix(len(x) / SR, [(0, x), (0, sub_boom(1.6) * 0.8)])

def horror():
    s = Score(60).prog(0, 55, 127).prog(1, 44, 120, 64, 70).prog(2, 61, 110).prog(3, 47, 127).prog(9, 0, 110)
    s.n(0, 0, 1, [48, 49, 55, 56, 60, 61], 127); s.n(3, 0, 1, 40, 127)
    s.n(1, 0, 2.8, [84, 85, 86, 87, 88], 110); s.ramp(1, 0.2, 2.8, 127, 20)
    s.n(2, 0, 2.2, [36, 37, 43], 115); s.ramp(2, 0.1, 2.2, 127, 25)
    s.n(9, 0, 2, 49, 120); s.n(9, 0, 2, 57, 110)
    x = s.render(2.5)
    hit = st(filt(noise(1.2), 4000) * np.exp(-T(1.2) * 6) * 0.6)
    return mix(len(x) / SR + 1, [(0, x), (0, sub_boom(2.0, 40)), (0, hit), (0.02, gong(4.5, 52) * 0.8)])

def drone():
    s = Score(60).prog(0, 43, 110, 54, 60).prog(1, 42, 100, 74, 60).prog(2, 89, 90, 64, 70).prog(3, 44, 100, 64, 70)
    s.n(0, 0, 10, [33, 34], 110); s.n(1, 0, 10, 45, 100); s.n(2, 0, 10, [57, 58], 90)
    s.n(3, 5, 5, [81, 82], 90)
    for ch in (0, 1, 2): s.ramp(ch, 0, 9.5, 15, 127)
    s.ramp(3, 5, 9.5, 10, 120)
    x = s.render(0.5)[:int(10 * SR)]
    return mix(10, [(0, x), (0, heartbeat(10) * 0.9)])

def ring():
    s = Score(120).prog(0, 12, 115, 64, 30).prog(1, 9, 70, 64, 30)
    motif = [(0, .25, 76), (.25, .25, 79), (.5, .25, 84), (.75, .25, 79), (1, .25, 81), (1.25, .25, 84),
             (1.5, .5, 88), (2, .25, 84), (2.25, .25, 81), (2.5, .25, 79), (2.75, .25, 81), (3, .75, 84)]
    for r in range(2):
        s.seq(0, motif, 110, r * 5); s.seq(1, motif, 60, r * 5, 12)
    x = s.render(1.0)
    y = loop_wrap(x, s.sec(10))
    return filt(y, 180, 'high', 2).astype(np.float32)   # 휴대폰 스피커 질감

def midnight():
    s = Score(60).prog(0, 14, 115, 64, 90)
    for i in range(3): s.n(0, i * 1.5, 1.4, 48, 115)
    x = s.render(4)
    return mix(13, [(0, wind(13) * 0.85), (0.6, x)])

def trombone():
    s = Score(100).prog(0, 57, 115, 60, 50).prog(1, 58, 90, 70, 50)
    for i, p in enumerate([58, 57, 56]): s.n(0, i * .9, .8, p, 105); s.n(1, i * .9, .8, p - 12, 90)
    s.n(0, 2.7, 2.6, 55, 110); s.n(1, 2.7, 2.6, 43, 95)
    for k in range(60):
        b = 3.0 + k * 0.035
        w = 2800 * np.sin(2 * np.pi * 6 * (b - 3.0) * 60 / 100); s.bend(0, b, w); s.bend(1, b, w)
    s.bend(0, 5.3, 0); s.bend(1, 5.3, 0)
    return s.render(1.5)

def thunder_sting():
    s = Score(60).prog(0, 55, 127).prog(1, 44, 115, 64, 70).prog(2, 43, 110)
    s.n(0, 0, 1, [45, 46, 52], 127); s.n(1, 0, 2.2, [69, 70, 75, 76], 105); s.ramp(1, 0.2, 2.2, 127, 30)
    s.n(2, 0, 2.2, 28, 115)
    x = s.render(2)
    return mix(7.5, [(0, x), (0, sub_boom(1.5) * 0.7), (0.35, thunder(6.8))])

def piano_theme():
    s = Score(72).prog(0, 0, 105, 64, 70).prog(1, 49, 70, 64, 80).prog(2, 0, 90, 64, 70)
    roots = [(45, 3), (41, 4), (48, 4), (43, 4), (45, 3), (41, 4), (50, 3), (40, 4)]
    mel = [(0, 1.5, 76), (1.5, .5, 74), (2, 1, 72), (3, 1, 71), (4, 2, 72), (6, 1, 69), (7, 1, 72),
           (8, 1.5, 79), (9.5, .5, 77), (10, 1, 76), (11, 1, 74), (12, 3, 74), (15, 1, 71),
           (16, 1.5, 76), (17.5, .5, 77), (18, 1, 79), (19, 1, 81), (20, 2, 81), (22, 1, 79), (23, 1, 77),
           (24, 1.5, 77), (25.5, .5, 76), (26, 2, 74), (28, 3, 71), (31, 1, 68)]
    s.seq(0, mel, 88)
    for i, (r, third) in enumerate(roots):
        pat = [r, r + 7, r + 12, r + 12 + third, r + 12, r + 7, r + 12, r + 7]
        for k, p in enumerate(pat): s.n(2, i * 4 + k * .5, .9, p, 62)
        s.n(1, i * 4, 4, [r + 12, r + 12 + third, r + 19], 60)
    s.cc(1, 0, 11, 75)
    return loop_wrap(s.render(4), s.sec(32))

def strings_theme():
    s = Score(66).prog(0, 42, 115, 54, 80).prog(1, 49, 95, 74, 85).prog(2, 46, 85, 64, 70).prog(3, 43, 90, 64, 80)
    chords = [[53, 57, 60, 65], [52, 55, 60, 64], [50, 57, 62, 65], [46, 53, 58, 62],
              [45, 53, 57, 60], [43, 55, 58, 62], [46, 53, 58, 62], [48, 55, 60, 64]]
    mel = [(0, 2, 60), (2, 1, 65), (3, 1, 64), (4, 2, 64), (6, 2, 60), (8, 1.5, 62), (9.5, .5, 64), (10, 1, 65), (11, 1, 67),
           (12, 3, 65), (15, 1, 62), (16, 2, 69), (18, 1, 67), (19, 1, 65), (20, 2, 67), (22, 1, 65), (23, 1, 62),
           (24, 1.5, 62), (25.5, .5, 65), (26, 2, 67), (28, 4, 64)]
    s.seq(0, mel, 95)
    for i, ch in enumerate(chords):
        s.n(1, i * 4, 4, ch, 70); s.n(3, i * 4, 4, ch[0] - 12, 75)
        for k in range(4): s.n(2, i * 4 + k, 1.5, ch[k % 4] + 12, 55)
    x = loop_wrap(s.render(4), s.sec(32))
    w = water(len(x) / SR) * 0.35
    return (x + w[:len(x)]).astype(np.float32)

def hope():
    s = Score(84).prog(0, 48, 110, 64, 80).prog(1, 61, 100, 54, 70).prog(2, 0, 90, 74, 60) \
                 .prog(3, 43, 105).prog(4, 47, 110).prog(5, 9, 80, 64, 60).prog(6, 56, 100, 60, 70).prog(9, 0, 110)
    chords = [[48, 55, 64], [47, 55, 62], [45, 57, 64], [41, 57, 65], [43, 60, 64], [41, 57, 69], [43, 59, 67], [36, 60, 64, 67]]
    mel = [(0, 2, 72), (2, 1, 74), (3, 1, 76), (4, 3, 74), (7, 1, 71), (8, 2, 72), (10, 1, 76), (11, 1, 79),
           (12, 3, 77), (15, 1, 76), (16, 2, 79), (18, 1, 81), (19, 1, 84), (20, 3, 81), (23, 1, 77),
           (24, 2, 79), (26, 1, 83), (27, 1, 86), (28, 8, 84)]
    s.seq(0, mel, 100); s.seq(6, [m for m in mel if m[0] >= 16], 100, transpose=-12); s.seq(5, [m for m in mel if m[0] >= 24], 90)
    for i, ch in enumerate(chords):
        d = 8 if i == 7 else 4
        s.n(0, i * 4, d, [p + 12 for p in ch[1:]], 80); s.n(3, i * 4, d, ch[0] - 12, 95)
        if i >= 4: s.n(1, i * 4, d, ch, 90)
        for k in range(8 if i < 7 else 0): s.n(2, i * 4 + k * .5, .8, ch[k % len(ch)] + 12 * (k // len(ch) + 1), 60 + i * 5)
    for ch in (0, 1, 6): s.ramp(ch, 0, 26, 55, 127)
    for k in range(32): s.n(4, 24 + k * .125, .12, 43, 50 + k * 2)
    s.n(4, 28, 1, 36, 127); s.n(9, 28, 4, 49, 120); s.n(9, 28, 4, 57, 110); s.n(2, 28, 6, [48, 60, 64, 67, 72], 100)
    return s.render(4)

def reaper():
    s = Score(126).prog(0, 71, 105, 54, 50).prog(1, 32, 115, 64, 30).prog(9, 0, 90)
    sw = lambda b: b + (0.08 if (b * 2) % 2 == 1 else 0)
    bass = [40, 43, 45, 46, 47, 45, 43, 42, 40, 43, 45, 47, 52, 50, 47, 43]
    s.seq(1, [(i, .9, p) for i, p in enumerate(bass)], 110)
    mel = [(0, 1, 64), (1.5, .5, 67), (2, .5, 69), (2.5, 1.5, 70), (4, .5, 71), (4.5, .5, 70), (5, .5, 69), (5.5, .5, 67), (6, 2, 64),
           (8, 1, 64), (9.5, .5, 67), (10, .5, 69), (10.5, 1.5, 70), (12, .5, 76), (12.5, .5, 75), (13, 1, 71), (14, 1.5, 64)]
    s.seq(0, [(sw(b), d, p) for b, d, p in mel], 100)
    for b in range(16):
        s.n(9, b, .3, 51, 70); s.n(9, b + 0.67, .2, 51, 45)
        if b % 2 == 1: s.n(9, b, .2, 39, 65)
    s.n(1, 16, 1.5, 40, 115); s.n(9, 16, 2, 49, 90)
    x = s.render(2)
    return mix(len(x) / SR + 0.5, [(0, x), (s.sec(15.5), coins(8) * 1.2)])

def ding():
    s = Score(60).prog(0, 11, 115, 64, 70).prog(1, 8, 80, 64, 70)
    s.n(0, 0, 1.6, 88, 110); s.n(1, 0, 1.6, 100, 70)
    return s.render(2)

def dundun():
    s = Score(76).prog(0, 48, 115, 64, 70).prog(1, 61, 110, 64, 70).prog(2, 47, 120).prog(3, 43, 110)
    for b, d, ch in [(0, .4, [50, 53, 57]), (.6, .4, [52, 55, 59]), (1.2, 2.2, [49, 52, 56])]:
        s.n(0, b, d, [p + 12 for p in ch], 120); s.n(1, b, d, ch, 120); s.n(2, b, .4, ch[0] - 12, 127); s.n(3, b, d, ch[0] - 24, 115)
    for k in range(16): s.n(2, 1.6 + k * 0.1, .1, 37, 70 + k * 3)
    return s.render(2.5)

def chime():
    s = Score(60).prog(0, 11, 115, 64, 70).prog(1, 8, 70, 64, 70)
    for i, p in enumerate([79, 76, 72, 67]): s.n(0, i * .6, 1.3, p, 110); s.n(1, i * .6, 1.3, p + 12, 55)
    return s.render(2.5)

def edit():
    s = Score(140).prog(0, 8, 100, 64, 60).prog(1, 56, 100, 60, 50).prog(2, 61, 95, 68, 50).prog(9, 0, 100)
    s.seq(0, [(i * 0.125, .3, p) for i, p in enumerate([84, 88, 91, 96, 100, 103])], 95)
    s.seq(1, [(1, 1/3, 72), (4/3, 1/3, 72), (5/3, 1/3, 72), (2, 2, 79)], 110)
    s.n(2, 2, 2, [48, 55, 60, 64], 105); s.n(9, 2, 2, 49, 110)
    sparkle = s.render(2.5)
    return mix(7.2, [(0, typing(1.5)), (1.65, enter_key()), (2.15, stamp()), (2.35, sparkle)])

def ringback(cycles=2):
    """한국 통화 연결음(발신음): 440+480Hz, 1초 울림 / 2초 쉼. 휴대폰 스피커 질감."""
    t = T(1.0); tone = (np.sin(2 * np.pi * 440 * t) + np.sin(2 * np.pi * 480 * t)) * 0.3
    tone *= np.minimum(1, np.minimum(t, 1.0 - t) / 0.01)
    m = np.concatenate([np.concatenate([tone, np.zeros(int(2.0 * SR))]) for _ in range(cycles)])
    m = filt(np.tanh(m * 1.4), [300, 3400], 'band', 2)
    return st(m.astype(np.float32) * 0.8)

def ars():
    """녹음 메시지 시작 신호 (ARS 띵동)"""
    s = Score(60).prog(0, 11, 110, 64, 60).prog(1, 8, 70, 64, 60)
    s.n(0, 0, .5, 84, 110); s.n(1, 0, .5, 96, 60); s.n(0, .45, 1, 79, 105); s.n(1, .45, 1, 91, 55)
    return s.render(1.0)

# ───────────────────────── 큐 목록 (2026.11.08 대본 형광펜 표시 기준) ─────────────────────────
# type: audio | stop      fadeOthers: GO 시 재생 중인 다른 큐를 몇 초에 걸쳐 페이드아웃
# 이전 34큐 버전은 git 기록(c0e548c)에 있습니다.
CUES = [
    dict(id="0",  scene="프리쇼", title="하우스 음악", timing="관객 입장 중 (공연 전)", file="00_house", gen=house, loop=True, vol=0.55),
    dict(id="1",  scene="1장", title="음악1 · 밝은 음악", timing="지문 '밝은 조명. 음악1'", file="01_opening", gen=opening, fadeOthers=2.5,
         note="음악 종류: 경쾌한 오피스 코미디(우쿨렐레·글로켄슈필·휘슬, 132BPM). \"여러분!!!\" 직전에 볼륨을 낮춤"),
    dict(id="2",  scene="1장", title="휴대전화 벨소리 (수신)", timing="지문 '휴대전화 벨소리.' (\"…'저승관리청' 이었어요!\" 뒤)", file="03_ring", gen=ring, loop=True, vol=0.8),
    dict(id="2B", scene="1장", title="벨소리 정지", timing="주인공 \"여보세요?\" 직전 (받는 순간)", type="stop", fade=0.1,
         note="이어지는 인사담당자 (전화) 대사는 무대 뒤 마이크 + 전화 음색 EQ"),
    dict(id="3",  scene="1장", title="통화 종료음", timing="지문 '(전화 종료)' (\"열심히 준비 하겠습니다!\" 뒤)", file="04_hangup", gen=busy_tone),
    dict(id="4",  scene="2장", title="통화 발신음", timing="지문 '팀장이 휴대전화를 꺼내 감사팀장에게 전화를 한다.'", file="05_ringback", gen=ringback, loop=True, vol=0.8),
    dict(id="4B", scene="2장", title="발신음 정지", timing="팀장 \"감사팀장님 오랜만이에요.\" 직전 (연결되는 순간)", type="stop", fade=0.1),
    dict(id="5",  scene="3장", title="녹음 메시지 신호음", timing="지문 '녹음된 메세지가 재생된다' (3장 시작, 암전 중)", file="06_ars", gen=ars,
         note="이어서 인사담당자 메시지: 배우 녹음 파일로 교체하거나 무대 뒤 마이크 + 전화 음색 EQ"),
    dict(id="6",  scene="3장", title="명부 재확인 스팅", timing="\"…저였어요!!!(명부를 다시 확인한다.)\"", file="07_recheck", gen=dundun),
    dict(id="7",  scene="3→4장", title="4장 전환 음악", timing="\"(머리를 감싼다.)\" → 4장 시작", file="08_jingle", gen=jingle),
    dict(id="8",  scene="4장", title="휴대전화 벨소리 (크게)", timing="지문 '그때 휴대전화 벨소리.' (\"지금 칭찬하실 때가 아니잖아요!\" 뒤)", file="03_ring", loop=True, vol=1.0),
    dict(id="8B", scene="4장", title="벨소리 정지", timing="\"(전화 받음.) 여보세요?\"", type="stop", fade=0.1,
         note="인사담당자 (전화) 대사는 무대 뒤 마이크 + 전화 음색 EQ"),
    dict(id="9",  scene="8장", title="방송음 (사내 방송 차임)", timing="인사담당자 \"(방송) 긴급 공지입니다…\" 직전", file="09_chime", gen=chime,
         note="차임 끝나고 방송 대사: 무대 뒤 마이크 + 확성기 음색 EQ"),
    dict(id="10", scene="9장", title="밝은 음악 · 커튼콜", timing="지문 '밝은 음악. 모두 관객을 향해 인사한다.'", file="10_curtain", gen=curtain, fadeOthers=1,
         note="\"하나, 둘! 감사합니다!!!\" · 암전 뒤 인사가 끝날 때까지 이어짐 (마지막 화음은 시작 약 27초 뒤)"),
    dict(id="11", scene="공연 후", title="하우스 음악", timing="커튼콜 인사 후 하우스 조명", file="00_house", loop=True, vol=0.55, fadeOthers=4, fadeIn=3),
]

LEVEL = {  # 목표 RMS(dBFS) — 큐 사이 음량 균형
    "00_house": -22, "03_ring": -19, "04_hangup": -21, "05_ringback": -21, "06_ars": -19, "09_chime": -19,
}

def master(x, name):
    x = x.astype(np.float64)
    if not name.endswith(("house", "piano", "strings", "ring", "ringback")):        # 루프가 아니면 꼬리 정리
        env = np.max(np.abs(x), 1); idx = np.where(env > 10 ** (-62 / 20))[0]
        if len(idx): x = x[:idx[-1] + int(0.05 * SR)]
        n = int(0.04 * SR); x[-n:] *= np.linspace(1, 0, n)[:, None]
    x[:int(0.003 * SR)] *= np.linspace(0, 1, int(0.003 * SR))[:, None]
    rms = np.sqrt(np.mean(x ** 2)) + 1e-9
    g = min(10 ** (LEVEL.get(name, -18) / 20) / rms, 10 ** (-1 / 20) / (np.max(np.abs(x)) + 1e-9))
    return (x * g).astype(np.float32)

def main():
    assert SF2 and shutil.which('fluidsynth') and shutil.which('ffmpeg'), "fluidsynth / ffmpeg / FluidR3_GM.sf2 필요"
    os.makedirs(OUT, exist_ok=True)
    meta = {}
    for c in CUES:
        if c.get("type") == "stop" or "gen" not in c: continue
        x = master(c["gen"](), c["file"])
        wav = os.path.join(OUT, c["file"] + ".wav")
        wavfile.write(wav, SR, (np.clip(x, -1, 1) * 32767).astype(np.int16))
        if not c.get("loop"):   # 단발 큐는 MP3(320k), 루프 큐는 끊김 없는 WAV 유지
            subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', wav, '-b:a', '320k', wav[:-4] + '.mp3'], check=True)
            os.remove(wav)
        meta[c["file"]] = round(len(x) / SR, 2)
        print(f'{c["id"]:>4}  {c["file"]:<18} {len(x)/SR:5.1f}s')
    cues = []
    for c in CUES:
        d = {k: v for k, v in c.items() if k != "gen"}
        if c.get("type") != "stop":
            d["type"] = "audio"
            d["src"] = f'audio/{c["file"]}.' + ("wav" if os.path.exists(os.path.join(OUT, c["file"] + ".wav")) else "mp3")
            d["dur"] = meta.get(c["file"])
            d.pop("file")
        cues.append(d)
    with open(os.path.join(ROOT, "cues.js"), "w", encoding="utf-8") as f:
        f.write("// 큐 목록 — 음원을 바꾸려면 src 경로만 바꾸면 됩니다.\n")
        f.write("// type: audio | stop · loop: 반복 · vol: 0~1 · fadeIn/fadeOthers/fade: 초\n")
        f.write("window.CUES = " + json.dumps(cues, ensure_ascii=False, indent=1) + ";\n")

if __name__ == "__main__":
    main()
