"""Pistas musicales originales sin derechos de autor, generadas por síntesis.

Uso: python3 musica.py salida.wav segundos [semilla]

La semilla elige el ESTILO, los ACORDES, el TONO y la VELOCIDAD, así cada video suena distinto:
  estilo = semilla % 4  ->  0 electrónico (126-130 bpm), 1 reguetón/dembow (92-98 bpm),
                            2 house con piano (120-124 bpm), 3 lo-fi relajado (82-88 bpm)
  acordes = (semilla // 4) % 6     tono = transposición de -2 a +2 semitonos según la semilla
Con semillas de 0 a 119 no se repite ninguna combinación.
"""
import sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 44100
dur = float(sys.argv[2])
SEED = int(sys.argv[3]) if len(sys.argv) > 3 else 7
N = int(SR * dur)
mix = np.zeros((N, 2))
rng = np.random.default_rng(SEED)

ESTILO = SEED % 4
BPM = {0: 126, 1: 92, 2: 120, 3: 82}[ESTILO] + (SEED % 3) * 2
STEP = 60 / BPM / 4                       # una semicorchea
TRANSP = (SEED // 24) % 5 - 2

PROGS = [  # (acordes en notas MIDI, raíces del bajo)
    ([[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]], [45, 41, 48, 43]),  # Am F C G
    ([[50, 53, 57], [58, 62, 65], [53, 57, 60], [48, 52, 55]], [38, 46, 41, 36]),  # Dm Bb F C
    ([[52, 55, 59], [48, 52, 55], [55, 59, 62], [50, 54, 57]], [40, 36, 43, 38]),  # Em C G D
    ([[48, 52, 55], [55, 59, 62], [57, 60, 64], [53, 57, 60]], [36, 43, 45, 41]),  # C G Am F
    ([[53, 57, 60], [55, 59, 62], [52, 55, 59], [57, 60, 64]], [41, 43, 40, 45]),  # F G Em Am
    ([[50, 53, 57], [55, 59, 62], [48, 52, 55], [57, 60, 64]], [38, 43, 36, 45]),  # Dm G C Am
]
chords, roots = PROGS[(SEED // 4) % len(PROGS)]
chords = [[m + TRANSP for m in c] for c in chords]; roots = [r + TRANSP for r in roots]

def add(sig, t0, gain=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N or i < 0: return
    sig = sig[: N - i]
    mix[i:i + len(sig), 0] += sig * gain * (1 - max(pan, 0))
    mix[i:i + len(sig), 1] += sig * gain * (1 + min(pan, 0))

def env(n, a=0.005, r=0.2):
    t = np.arange(n) / SR
    return np.minimum(t / a, 1) * np.exp(-t / r)

def hp(x, f): b, a = butter(2, f / (SR / 2), "high"); return lfilter(b, a, x)
def lp(x, f): b, a = butter(2, f / (SR / 2), "low"); return lfilter(b, a, x)
def note(m): return 440 * 2 ** ((m - 69) / 12)

def kick(punch=110, decay=7):
    n = int(0.4 * SR); t = np.arange(n) / SR
    f = 48 + punch * np.exp(-t * 35)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * decay)

def snare(tono=1500, r=0.07):
    n = int(0.25 * SR); t = np.arange(n) / SR
    cuerpo = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30)
    return (hp(rng.standard_normal(n), tono) * 0.8 + cuerpo * 0.4) * env(n, 0.002, r)

def hat(abierto=False):
    n = int((0.2 if abierto else 0.05) * SR)
    return hp(rng.standard_normal(n), 7000) * env(n, 0.001, 0.09 if abierto else 0.015)

def saw(freq, n):
    t = np.arange(n) / SR
    return sum(2 * ((t * freq * 2 ** (d / 12)) % 1) - 1 for d in (-0.12, 0, 0.12)) / 3

def keys(freq, n, r=0.6):            # piano eléctrico suave
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(4 * np.pi * freq * t) + 0.1 * np.sin(6 * np.pi * freq * t)
    return s * env(n, 0.004, r)

def sub(freq, n, r=0.3):
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * freq * t) * env(n, 0.004, r)

bars = int(dur / (16 * STEP)) + 1
for bar in range(bars):
    t0 = bar * 16 * STEP
    ch, root = chords[bar % 4], roots[bar % 4]
    full = bar >= 1                                   # primer compás suave para crear expectativa
    at = lambda s: t0 + s * STEP

    if ESTILO == 0:                                   # electrónico con arpegio
        for s in range(0, 16, 4):
            if full: add(kick(), at(s), 0.9)
            add(hat(), at(s + 2), 0.18, 0.3)
        if full:
            for s in (4, 12): add(snare(1200, 0.06), at(s), 0.35)
            for s in range(1, 16, 2): add(hat(), at(s), 0.06, -0.3)
        for s in range(0, 16, 2):
            n = int(2 * STEP * SR); add(lp(saw(note(root), n), 400) * env(n, 0.003, 0.12), at(s), 0.45 if full else 0.25)
        arp = ch + [ch[0] + 12]
        for s in range(16):
            n = int(STEP * SR); add(lp(saw(note(arp[s % 4] + 12), n), 3500) * env(n, 0.002, 0.07), at(s), 0.16, 0.4 if s % 2 else -0.4)
        n = int(16 * STEP * SR)
        add(sum(lp(saw(note(m), n), 1500) for m in ch) / 3 * np.minimum(np.arange(n) / (0.3 * SR), 1), t0, 0.08)

    elif ESTILO == 1:                                 # reguetón / dembow
        for s in (0, 4, 8, 12):
            if full: add(kick(90, 9), at(s), 0.95)
        for s in (3, 6, 11, 14):
            if full: add(snare(1800, 0.05), at(s), 0.42, 0.1)
        for s in range(0, 16, 2): add(hat(), at(s), 0.12, -0.2)
        for s in (0, 8):
            n = int(8 * STEP * SR); add(sub(note(root - 12), n, 0.5), at(s), 0.6 if full else 0.3)
        for s in (0, 3, 6, 10, 12):                   # acordes cortos sincopados
            n = int(1.5 * STEP * SR)
            add(sum(lp(saw(note(m + 12), n), 2500) for m in ch) / 3 * env(n, 0.002, 0.08), at(s), 0.22, 0.2)
        if bar % 2 == 1:                              # pequeña melodía
            for k, s in enumerate((0, 2, 4, 7)):
                n = int(2 * STEP * SR); add(keys(note(ch[k % 3] + 24), n, 0.25), at(s), 0.14, -0.3)

    elif ESTILO == 2:                                 # house con piano
        for s in (0, 4, 8, 12):
            if full: add(kick(120, 6), at(s), 0.9)
        for s in (4, 12):
            if full: add(snare(1000, 0.08), at(s), 0.3)
        for s in (2, 6, 10, 14): add(hat(True), at(s), 0.14, 0.25)
        for s in (2, 6, 10, 14):                      # bajo en contratiempo
            n = int(2 * STEP * SR); add(lp(saw(note(root), n), 500) * env(n, 0.003, 0.15), at(s), 0.42 if full else 0.2)
        for s in (0, 3, 6, 10):                       # acordes de piano
            n = int(3 * STEP * SR)
            add(sum(keys(note(m + 12), n, 0.35) for m in ch) / 3, at(s), 0.3, -0.15)

    else:                                             # lo-fi relajado
        swing = STEP * 0.18
        for s in (0, 7, 10):
            if full: add(lp(kick(70, 8), 900), at(s), 0.75)
        for s in (4, 12):
            if full: add(lp(snare(900, 0.09), 4000), at(s), 0.3)
        for s in range(0, 16, 2): add(lp(hat(), 9000), at(s) + (swing if (s // 2) % 2 else 0), 0.09)
        n = int(16 * STEP * SR)
        add(lp(sum(keys(note(m), n, 1.6) for m in ch + [ch[1] + 12]) / 4, 2200), t0, 0.45)
        n = int(8 * STEP * SR)
        for s in (0, 8): add(sub(note(root - 12), n, 0.6), at(s), 0.45)
        for k, s in enumerate((2, 5, 9, 13)):
            n = int(3 * STEP * SR); add(lp(keys(note(ch[(k + bar) % 3] + 24), n, 0.4), 3000), at(s), 0.1, 0.3)

if ESTILO == 3:                                       # crepitar de vinilo
    ruido = rng.standard_normal(N) * (rng.random(N) > 0.9993) * 0.6 + lp(rng.standard_normal(N), 3000) * 0.012
    mix[:, 0] += ruido; mix[:, 1] += ruido
else:                                                 # subida de ruido al inicio
    n = int(16 * STEP * SR)
    add(hp(rng.standard_normal(n), 2000) * np.linspace(0, 1, n) ** 2, 0, 0.1)

fade = int(1.2 * SR)
mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
mix /= np.max(np.abs(mix)) + 1e-9
mix = np.tanh(mix * 1.4) / np.tanh(1.4) * 0.85
wavfile.write(sys.argv[1], SR, (mix * 32767).astype(np.int16))
