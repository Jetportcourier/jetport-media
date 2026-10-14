"""Pista original energética sin derechos de autor, generada por síntesis.
Uso: python3 musica.py salida.wav segundos [semilla]  (la semilla cambia acordes y tempo)"""
import sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 44100
BPM = 124 + (int(sys.argv[3]) % 3) * 2 if len(sys.argv) > 3 else 128
BEAT = 60 / BPM
dur = float(sys.argv[2])
N = int(SR * dur)
mix = np.zeros((N, 2))
SEED = int(sys.argv[3]) if len(sys.argv) > 3 else 7
rng = np.random.default_rng(SEED)

def add(sig, t0, gain=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N: return
    sig = sig[: N - i]
    mix[i:i + len(sig), 0] += sig * gain * (1 - max(pan, 0))
    mix[i:i + len(sig), 1] += sig * gain * (1 + min(pan, 0))

def env(n, a=0.005, r=0.2):
    t = np.arange(n) / SR
    return np.minimum(t / a, 1) * np.exp(-t / r)

def hp(x, f):
    b, a = butter(2, f / (SR / 2), "high"); return lfilter(b, a, x)

def lp(x, f):
    b, a = butter(2, f / (SR / 2), "low"); return lfilter(b, a, x)

def kick():
    n = int(0.4 * SR); t = np.arange(n) / SR
    f = 50 + 110 * np.exp(-t * 35)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)

def clap():
    n = int(0.25 * SR)
    return hp(rng.standard_normal(n), 1200) * env(n, 0.002, 0.06)

def hat(open_=False):
    n = int((0.18 if open_ else 0.05) * SR)
    return hp(rng.standard_normal(n), 7000) * env(n, 0.001, 0.08 if open_ else 0.015)

def saw(freq, n):
    t = np.arange(n) / SR
    out = np.zeros(n)
    for det in (-0.12, 0, 0.12):  # supersaw ligero
        f = freq * 2 ** (det / 12)
        out += 2 * ((t * f) % 1) - 1
    return out / 3

def note(m): return 440 * 2 ** ((m - 69) / 12)

# progresión Am - F - C - G (2 compases cada acorde no; 1 compás = 4 tiempos)
PROGS = [([[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]], [45, 41, 48, 43]),
         ([[50, 53, 57], [58, 62, 65], [53, 57, 60], [48, 52, 55]], [38, 46, 41, 36]),
         ([[52, 55, 59], [48, 52, 55], [55, 59, 62], [50, 54, 57]], [40, 36, 43, 38])]
chords, bass_roots = PROGS[SEED % len(PROGS)]

bars = int(dur / (4 * BEAT)) + 1
intro_bars = 1  # primer compás más suave: crea expectativa
for bar in range(bars):
    t_bar = bar * 4 * BEAT
    ch = chords[bar % 4]; root = bass_roots[bar % 4]
    full = bar >= intro_bars
    for b in range(4):
        tb = t_bar + b * BEAT
        if full: add(kick(), tb, 0.9)
        if full and b in (1, 3): add(clap(), tb, 0.35)
        add(hat(), tb + BEAT / 2, 0.18, 0.3)
        if full: add(hat(), tb + BEAT / 4, 0.07, -0.3); add(hat(), tb + 3 * BEAT / 4, 0.07, -0.3)
        # bajo en corcheas (sidechain sencillo: entra en el contratiempo)
        for k in range(2):
            n = int(BEAT / 2 * SR)
            s = lp(saw(note(root), n), 400) * env(n, 0.003, 0.12)
            add(s, tb + k * BEAT / 2, 0.45 if full else 0.25)
    # arpegio en semicorcheas
    arp = ch + [ch[0] + 12]
    for s16 in range(16):
        n = int(BEAT / 4 * SR)
        m = arp[s16 % 4] + 12
        sig = lp(saw(note(m), n), 3500) * env(n, 0.002, 0.07)
        add(sig, t_bar + s16 * BEAT / 4, 0.16, 0.4 if s16 % 2 else -0.4)
    # pad de acorde
    n = int(4 * BEAT * SR)
    pad = sum(lp(saw(note(m), n), 1500) for m in ch) / 3
    pe = np.minimum(np.arange(n) / (0.3 * SR), 1) * np.minimum((n - np.arange(n)) / (0.2 * SR), 1)
    add(pad * pe, t_bar, 0.10)

# subida de ruido (riser) antes de entrar el ritmo completo
n = int(4 * BEAT * SR)
riser = hp(rng.standard_normal(n), 2000) * np.linspace(0, 1, n) ** 2
add(riser, 0, 0.12)

# fundido final
fade = int(1.2 * SR)
mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
mix /= np.max(np.abs(mix)) + 1e-9
mix = np.tanh(mix * 1.4) / np.tanh(1.4) * 0.85
wavfile.write(sys.argv[1], SR, (mix * 32767).astype(np.int16))
