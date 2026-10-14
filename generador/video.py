"""Generador de videos verticales de Jetport Courier (1080x1920, TikTok/Reels).

Uso:
    python3 generador/video.py guion.json salida.mp4          # video completo con música
    python3 generador/video.py guion.json preview.png 4.5     # un fotograma en el segundo 4.5

El guion es un JSON:
{
  "musica_semilla": 7,                      # opcional: cambia la variación de la música
  "escenas": [
    {"tipo": "titulo", "dur": 3.5, "arriba": "3 ERRORES", "lineas": ["al comprar en USA", "desde Perú"], "sub": "¿Cuál cometiste tú?"},
    {"tipo": "punto",  "dur": 5,   "numero": "1", "etiqueta": "ERROR", "titulo": "No revisar los productos restringidos",
                       "texto": "Baterías sueltas, perfumes o inflamables pueden quedar retenidos en aduana."},
    {"tipo": "texto",  "dur": 5,   "etiqueta": "¿SABÍAS QUE?", "titulo": "Un casillero es tu dirección en USA",
                       "texto": "Compras en cualquier tienda online y la envías a nuestro almacén en Miami."},
    {"tipo": "cta",    "dur": 4}
  ]
}
Reglas de contenido: nunca poner el domicilio fiscal; la ubicación pública es "Los Olivos, Lima".
"""
import json, math, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
FONT_DIR = "/usr/share/fonts/opentype/inter/"
NAVY = (11, 37, 84); NAVY2 = (5, 18, 45)
ORANGE = (255, 122, 26); WHITE = (255, 255, 255); SOFT = (190, 205, 230)
MARGIN = 110

_fonts = {}
def font(w, s):
    k = (w, s)
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(FONT_DIR + f"Inter-{w}.otf", s)
    return _fonts[k]

import numpy as np

# Paletas de fondo (color A arriba-izquierda → color B abajo-derecha). Una por escena, en rotación.
PALETAS = [
    ((10, 31, 77), (30, 95, 216)),    # azul marino → azul eléctrico
    ((36, 18, 79), (122, 31, 162)),   # índigo → morado
    ((3, 47, 79), (11, 127, 168)),    # azul petróleo → turquesa
    ((18, 11, 61), (74, 43, 176)),    # medianoche → violeta
]
_SW, _SH = W // 4, H // 4                      # el degradado se calcula pequeño y se escala (rápido)
_yy, _xx = np.mgrid[0:_SH, 0:_SW].astype(np.float32)

def _gradiente(c1, c2, ang):
    dx, dy = math.cos(ang), math.sin(ang)
    proy = (_xx / _SW - 0.5) * dx + (_yy / _SH - 0.5) * dy * (H / W)
    k = np.clip(proy / 1.4 + 0.5, 0, 1)[..., None]
    arr = np.array(c1, np.float32) * (1 - k) + np.array(c2, np.float32) * k
    return Image.fromarray(arr.astype(np.uint8)).resize((W, H), Image.BILINEAR)

def _brillo(radio, color):
    r = np.hypot(*np.mgrid[-radio:radio, -radio:radio].astype(np.float32)) / radio
    a = (np.clip(1 - r, 0, 1) ** 2.2 * 255).astype(np.uint8)
    im = Image.new("RGBA", (2 * radio, 2 * radio), color + (0,)); im.putalpha(Image.fromarray(a))
    return im

_GLOW_NARANJA = _brillo(520, (255, 122, 26))
_GLOW_NARANJA.putalpha(_GLOW_NARANJA.getchannel("A").point(lambda v: int(v * 0.45)))
_GLOW_CIAN = _brillo(460, (80, 200, 255))
_GLOW_CIAN.putalpha(_GLOW_CIAN.getchannel("A").point(lambda v: int(v * 0.30)))

def fondo(t, idx, t_escena):
    """Fondo animado: degradado que gira despacio, transición suave entre escenas y destellos de luz."""
    c1, c2 = PALETAS[idx % len(PALETAS)]
    if idx > 0 and t_escena < 0.5:            # mezcla con la paleta anterior al entrar en la escena
        p1, p2 = PALETAS[(idx - 1) % len(PALETAS)]; k = ease(t_escena / 0.5)
        c1 = tuple(int(p1[i] * (1 - k) + c1[i] * k) for i in range(3))
        c2 = tuple(int(p2[i] * (1 - k) + c2[i] * k) for i in range(3))
    img = _gradiente(c1, c2, 1.1 + 0.25 * math.sin(t * 0.6)).convert("RGBA")
    img.alpha_composite(_GLOW_NARANJA, (int(W * 0.75 + 160 * math.sin(t * 0.7)) - 520, int(H * 0.18 + 120 * math.cos(t * 0.5)) - 520))
    img.alpha_composite(_GLOW_CIAN, (int(W * 0.15 + 140 * math.cos(t * 0.6)) - 460, int(H * 0.82 + 100 * math.sin(t * 0.8)) - 460))
    return img

def ease(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
def rgba(c, a): return c + (int(255 * max(0, min(1, a))),)
def appear(t, start, dur=0.45):
    e = ease((t - start) / dur); return e, int((1 - e) * 60)

def wrap(texto, f, maxw):
    words, lines, cur = texto.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if f.getlength(test) <= maxw or not cur: cur = test
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def fit(texto, weight, size, maxw, max_lines, min_size=40):
    """Reduce el tamaño hasta que el texto quepa en max_lines líneas."""
    while True:
        f = font(weight, size); lines = wrap(texto, f, maxw)
        if len(lines) <= max_lines or size <= min_size: return f, lines, size
        size -= 4

def text(L, xy, s, f, fill, a=1.0, anchor="mm"):
    ImageDraw.Draw(L).text(xy, s, font=f, fill=rgba(fill, a), anchor=anchor)

def block(L, y, texto, weight, size, color, a, maxw=W - 2 * MARGIN, max_lines=3, gap=1.18):
    f, lines, s = fit(texto, weight, size, maxw, max_lines)
    for i, ln in enumerate(lines):
        text(L, (W / 2, y + i * s * gap), ln, f, color, a)
    return y + len(lines) * s * gap

def plane(L, cx, cy, s, a):
    d = ImageDraw.Draw(L); c = rgba(WHITE, a)
    d.polygon([(cx - s, cy), (cx + s, cy - .12*s), (cx + 1.15*s, cy), (cx + s, cy + .12*s)], fill=c)
    d.polygon([(cx + .1*s, cy - .05*s), (cx - .25*s, cy - .75*s), (cx - .05*s, cy - .75*s), (cx + .45*s, cy)], fill=c)
    d.polygon([(cx + .1*s, cy + .05*s), (cx - .25*s, cy + .75*s), (cx - .05*s, cy + .75*s), (cx + .45*s, cy)], fill=c)
    d.polygon([(cx - .85*s, cy), (cx - 1.05*s, cy - .35*s), (cx - .92*s, cy - .35*s), (cx - .6*s, cy)], fill=c)

def pill(L, box, color, a=1.0, r=40):
    ImageDraw.Draw(L).rounded_rectangle(box, r, fill=rgba(color, a))

def progress(L, t, total):
    ImageDraw.Draw(L).rectangle([0, 0, W * t / total, 10], fill=rgba(ORANGE, 0.9))

# ---------- escenas ----------
def esc_titulo(L, e, lt, a):
    p, dy = appear(lt, 0.1)
    y = 520
    if e.get("arriba"):
        y = block(L, y + dy, e["arriba"], "Black", 140, ORANGE, a * p, max_lines=2) + 20
    p, dy = appear(lt, 0.4)
    for ln in e.get("lineas", []):
        y = block(L, y + dy, ln, "Black", 90, WHITE, a * p, max_lines=2)
    x = -200 + ease((lt - 0.7) / 2.2) * (W + 400)
    plane(L, x, max(y + 180, 1100) - 40 * math.sin(lt * 2), 110, a)
    if e.get("sub"):
        p, dy = appear(lt, 1.3)
        block(L, 1420 + dy, e["sub"], "Bold", 60, SOFT, a * p, max_lines=2)

def esc_punto(L, e, lt, a):
    p, dy = appear(lt, 0.0)
    ImageDraw.Draw(L).ellipse([W/2 - 95, 300 + dy, W/2 + 95, 490 + dy], fill=rgba(ORANGE, a * p))
    text(L, (W/2, 395 + dy), str(e.get("numero", "")), font("Black", 120), WHITE, a * p)
    p, dy = appear(lt, 0.3)
    if e.get("etiqueta"): text(L, (W/2, 620 + dy), e["etiqueta"], font("Black", 56), ORANGE, a * p)
    y = block(L, 730 + dy, e["titulo"], "Black", 80, WHITE, a * p, max_lines=3)
    _caja(L, max(y + 40, 1010), e.get("texto", ""), lt, a)

def esc_texto(L, e, lt, a):
    p, dy = appear(lt, 0.0)
    if e.get("etiqueta"): text(L, (W/2, 460 + dy), e["etiqueta"], font("Black", 60), ORANGE, a * p)
    p, dy = appear(lt, 0.3)
    y = block(L, 600 + dy, e["titulo"], "Black", 88, WHITE, a * p, max_lines=4)
    _caja(L, max(y + 40, 1010), e.get("texto", ""), lt, a)

def _caja(L, top, texto, lt, a):
    if not texto: return
    p, dy = appear(lt, 0.8)
    f, lines, s = fit(texto, "Medium", 54, W - 2 * MARGIN - 80, 5)
    hgt = 110 + len(lines) * s * 1.25
    pill(L, [MARGIN, top + dy, W - MARGIN, top + hgt + dy], WHITE, a * p * 0.09, 40)
    text(L, (MARGIN + 50, top + 50 + dy), "TIP", font("Black", 44), ORANGE, a * p, "lm")
    for i, ln in enumerate(lines):
        text(L, (W/2, top + 115 + i * s * 1.25 + dy), ln, f, WHITE, a * p)

def esc_cta(L, e, lt, a):
    p, dy = appear(lt, 0.0)
    text(L, (W/2, 560 + dy), e.get("linea1", "Síguenos"), font("Black", 130), WHITE, a * p)
    text(L, (W/2, 700 + dy), e.get("linea2", "para más tips"), font("Black", 100), ORANGE, a * p)
    p, dy = appear(lt, 0.4)
    text(L, (W/2, 870 + dy), e.get("sub", "de compras internacionales"), font("Bold", 56), SOFT, a * p)
    p, dy = appear(lt, 0.8)
    pulse = 1 + 0.03 * math.sin(lt * 6); bw, bh = 400 * pulse, 80 * pulse
    pill(L, [W/2 - bw, 1080 - bh + dy, W/2 + bw, 1080 + bh + dy], ORANGE, a * p, 80)
    text(L, (W/2, 1080 + dy), "@jetportcourier", font("Black", 76), WHITE, a * p)
    p, dy = appear(lt, 1.2)
    text(L, (W/2, 1290 + dy), "USA y China → Perú", font("Medium", 50), SOFT, a * p)
    text(L, (W/2, 1360 + dy), "Los Olivos, Lima", font("Medium", 50), SOFT, a * p)

TIPOS = {"titulo": esc_titulo, "punto": esc_punto, "texto": esc_texto, "cta": esc_cta}

def build(guion):
    escenas, t = [], 0.0
    for e in guion["escenas"]:
        escenas.append((t, t + float(e["dur"]), e)); t += float(e["dur"])
    return escenas, t

def frame(escenas, total, t):
    idx, t_esc = 0, t
    for i, (s, e_, _) in enumerate(escenas):
        if s <= t: idx, t_esc = i, t - s
    img = fondo(t, idx, t_esc); L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(L); off = (t * 120) % 400
    for k in range(-2, 7):
        x0 = k * 400 + off - 600
        d.polygon([(x0, 0), (x0 + 60, 0), (x0 + 760, H), (x0 + 700, H)], fill=(255, 255, 255, 10))
    for s, e_, e in escenas:
        if s <= t <= e_:
            a = 1.0 if (t <= e_ - 0.3 or e_ >= total) else (e_ - t) / 0.3
            TIPOS[e["tipo"]](L, e, t - s, a)
    progress(L, t, total)
    text(L, (W/2, H - 120), "JETPORT COURIER", font("Black", 44), WHITE)
    ImageDraw.Draw(L).rectangle([W/2 - 60, H - 85, W/2 + 60, H - 79], fill=rgba(ORANGE, 1))
    img.alpha_composite(L); return img.convert("RGB")

def main():
    guion = json.load(open(sys.argv[1], encoding="utf-8")); out = sys.argv[2]
    escenas, total = build(guion)
    if len(sys.argv) > 3:
        frame(escenas, total, float(sys.argv[3])).save(out); return
    tmp = tempfile.mkdtemp()
    wav, muda = os.path.join(tmp, "m.wav"), os.path.join(tmp, "v.mp4")
    aqui = os.path.dirname(os.path.abspath(__file__))
    subprocess.run([sys.executable, os.path.join(aqui, "musica.py"), wav, str(total),
                    str(guion.get("musica_semilla", 7))], check=True)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
                          "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "20", muda], stdin=subprocess.PIPE)
    for i in range(int(total * FPS)):
        p.stdin.write(frame(escenas, total, i / FPS).tobytes())
    p.stdin.close(); p.wait()
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", muda, "-i", wav, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out], check=True)

if __name__ == "__main__":
    main()
