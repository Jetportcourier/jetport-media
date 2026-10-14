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
                       "texto": "Baterías de litio sueltas o líquidos inflamables pueden quedar retenidos en aduana."},
    {"tipo": "texto",  "dur": 5,   "etiqueta": "¿SABÍAS QUE?", "titulo": "Un casillero es tu dirección en USA",
                       "texto": "Compras en cualquier tienda online y la envías a nuestro almacén en Miami."},
    {"tipo": "cta",    "dur": 4}
  ]
}
Cada escena puede llevar "fondo": "avion" | "ruta" | "tienda" | "cajas" (escenario ilustrado animado:
aviones y nubes, mapa Miami→Lima, toldo de tienda con carteles de oferta, cajas en cinta, bolsas de compras).
Si se omite, se rotan automáticamente.
La escena "cta" admite "modo": "seguir" (por defecto: Síguenos @jetportcourier) o "escribenos"
(Escríbenos "INFO"; opcionales "linea1", "palabra", "sub").
Clips reales: escena {"tipo": "clip", "dur": 3, "archivo": "material/clip.mp4", "inicio": 2.0,
  "texto": "POV: llegó tu pedido de Amazon", "resaltado": "📦", "posicion": "arriba|centro|abajo"}
  usa el video real como fondo (recortado a vertical, con acercamiento lento) y texto estilo TikTok.
  Opcionales: "recorte": [x, y, ancho, alto] para quitar franjas negras o subtítulos quemados del original;
  "con_audio": true para usar la voz del clip (la música baja de volumen); "subtitulos": [[desde, hasta, "frase"]].
  Avatar de la marca (presentadora virtual): clips en material/avatar_*.mp4 (ver material/LEEME.md).
Transiciones: cualquier escena puede llevar "transicion": "zoom" (por defecto: golpe de zoom + destello),
  "barrido" (deslizamiento rápido) o "ninguna".
Marca: generador/logo_horizontal.png (logo oficial) va en el pie de todos los cuadros, SIEMPRE sobre tarjeta blanca.\n  generador/logo_vertical.png es la versión vertical, también sobre blanco.
La escena "cta" muestra las redes oficiales (TikTok @jetport_courier, Instagram @jetportcourier,
  Facebook Jetport Courier, jpcourier.com).
Música: "musica_semilla" de 0 a 119 elige estilo, acordes, tono y velocidad (ver musica.py); usa una distinta en cada video.
Reglas: NUNCA poner números de teléfono/WhatsApp en los videos ni en los textos de las publicaciones.
Otras reglas de contenido: nunca poner el domicilio fiscal; la ubicación pública es "Los Olivos, Lima".
"""
import json, math, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont, ImageFilter

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

# ---------- escenarios ilustrados (franja superior 40-300 px e inferior 1460-1770 px, sin tapar el texto) ----------
CARTON = (205, 150, 92); CARTON_OSC = (160, 110, 62); CINTA = (232, 206, 150)

def _nubes(L, t, a):
    d = ImageDraw.Draw(L)
    for i, (x0, y, s, v) in enumerate([(0, 120, 1.0, 40), (500, 230, 0.7, 25), (900, 90, 0.8, 32)]):
        x = (x0 + t * v) % (W + 400) - 200
        for dx, dy, r in [(0, 0, 48), (45, -22, 58), (100, 0, 46), (55, 12, 40)]:
            d.ellipse([x + dx * s - r * s, y + dy * s - r * s, x + dx * s + r * s, y + dy * s + r * s], fill=rgba(WHITE, 0.13 * a))

def _avion_ruta(L, t, a):
    _nubes(L, t, a)
    d = ImageDraw.Draw(L)
    x = (t * 260) % (W + 600) - 300; y = 180 + 30 * math.sin(t * 1.5)
    for k in range(1, 14):                                  # estela punteada
        xx = x - 70 - k * 38
        if xx > -20: d.ellipse([xx - 6, y - 6, xx + 6, y + 6], fill=rgba(WHITE, 0.35 * a * (1 - k / 14)))
    plane(L, x, y, 85, 0.9 * a)

def _ruta_mapa(L, t, a):
    d = ImageDraw.Draw(L)
    x1, x2, yb = 150, W - 150, 250
    pts = [(x1 + (x2 - x1) * u, yb - 170 * math.sin(math.pi * u)) for u in [i / 60 for i in range(61)]]
    for i in range(0, 60, 2): d.line([pts[i], pts[i + 1]], fill=rgba(WHITE, 0.45 * a), width=6)
    for (px, py), nombre in [((x1, yb), "MIAMI"), ((x2, yb), "LIMA")]:
        d.ellipse([px - 16, py - 16, px + 16, py + 16], fill=rgba(ORANGE, a))
        text(L, (px, py + 42), nombre, font("Black", 34), WHITE, 0.8 * a)
    u = (t * 0.35) % 1; i = int(u * 60)
    px, py = pts[i]; qx, qy = pts[min(i + 1, 60)]
    ang = math.atan2(qy - py, qx - px)
    pl = Image.new("RGBA", (260, 260), (0, 0, 0, 0)); plane(pl, 130, 130, 60, a)
    pl = pl.rotate(-math.degrees(ang), resample=Image.BICUBIC)
    L.alpha_composite(pl, (int(px - 130), int(py - 130)))

def _dibujar_caja(d, x, y, w, h, a, etiqueta=True):
    d.rectangle([x, y, x + w, y + h], fill=rgba(CARTON, a), outline=rgba(CARTON_OSC, a), width=4)
    d.rectangle([x + w / 2 - w * 0.09, y, x + w / 2 + w * 0.09, y + h], fill=rgba(CINTA, a))
    if etiqueta and w > 110:
        d.rectangle([x + w * 0.62, y + h * 0.55, x + w * 0.92, y + h * 0.85], fill=rgba(WHITE, a))
        for k in range(3):
            yy = y + h * (0.61 + k * 0.08)
            d.line([x + w * 0.66, yy, x + w * 0.88, yy], fill=rgba(NAVY, a), width=3)

def _cajas_cinta(L, t, a):
    d = ImageDraw.Draw(L)
    yb = 1740
    d.rounded_rectangle([-20, yb, W + 20, yb + 28], 14, fill=rgba((40, 44, 60), 0.85 * a))
    for k in range(-1, 20):                                 # rodillos que avanzan
        xx = (k * 70 + t * 120) % (W + 70) - 35
        d.ellipse([xx - 9, yb + 5, xx + 9, yb + 23], fill=rgba((120, 125, 140), a))
    for i, (w, h) in enumerate([(170, 140), (130, 110), (200, 160), (150, 120), (120, 100)]):
        x = (i * 290 + t * 120) % (W + 600) - 300
        _dibujar_caja(d, x, yb - h, w, h, 0.95 * a)

def _bolsas(L, t, a):
    d = ImageDraw.Draw(L)
    colores = [ORANGE, (255, 255, 255), (80, 200, 255), (255, 214, 64), (236, 72, 153)]
    for i, c in enumerate(colores):
        w, h = 140 + (i % 2) * 30, 170 + (i % 3) * 20
        x = 70 + i * 200; y = 1760 - h - 10 * abs(math.sin(t * 2.2 + i))
        d.arc([x + w * 0.25, y - 60, x + w * 0.75, y + 50], 180, 360, fill=rgba(c, a), width=9)
        d.rounded_rectangle([x, y, x + w, y + h], 14, fill=rgba(c, 0.92 * a))
        d.rounded_rectangle([x, y, x + w, y + h], 14, outline=rgba((0, 0, 0), 0.12 * a), width=3)

def _tienda(L, t, a):
    d = ImageDraw.Draw(L)
    n, wseg = 9, W / 9
    for i in range(n):                                      # toldo a rayas con ondas
        c = ORANGE if i % 2 == 0 else WHITE
        x = i * wseg
        d.rectangle([x, 30, x + wseg, 150], fill=rgba(c, 0.85 * a))
        d.pieslice([x, 110, x + wseg, 190], 0, 180, fill=rgba(c, 0.85 * a))
    for i, emo in enumerate(["SALE", "-50%", "OFERTA", "NEW"]):
        x = 140 + i * 260; y = 240 + 8 * math.sin(t * 3 + i)
        d.rounded_rectangle([x - 90, y - 32, x + 90, y + 32], 16, fill=rgba((236, 72, 153) if i % 2 else (255, 214, 64), 0.9 * a))
        text(L, (x, y), emo, font("Black", 36), NAVY2 if i % 2 == 0 else WHITE, a)

ESCENARIOS = {
    "avion": (_avion_ruta, _cajas_cinta),
    "ruta": (_ruta_mapa, _cajas_cinta),
    "tienda": (_tienda, _bolsas),
    "cajas": (_avion_ruta, _bolsas),
}
ORDEN_ESCENARIOS = ["avion", "tienda", "ruta", "cajas"]

def escenario(L, nombre, t, a):
    arriba, abajo = ESCENARIOS[nombre]
    arriba(L, t, a); abajo(L, t, a)

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

# ---------- redes sociales y logo ----------
REDES = [("tiktok", "@jetport_courier"), ("instagram", "@jetportcourier"),
         ("facebook", "Jetport Courier"), ("web", "jpcourier.com")]
_RUTA_LOGO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo_horizontal.png")
LOGO = Image.open(_RUTA_LOGO).convert("RGBA") if os.path.exists(_RUTA_LOGO) else None
_LOGO_PIE = None

def icono(L, red, cx, cy, r, a):
    d = ImageDraw.Draw(L)
    if red == "instagram":
        for i in range(r * 2, 0, -2):                     # degradado tipo Instagram
            k = i / (r * 2); c = (int(250 * k + 130 * (1 - k)), int(60 * k + 50 * (1 - k)), int(120 * k + 200 * (1 - k)))
            d.rounded_rectangle([cx - i / 2, cy - i / 2, cx + i / 2, cy + i / 2], int(i * 0.28), fill=rgba(c, a))
        d.rounded_rectangle([cx - r * .55, cy - r * .55, cx + r * .55, cy + r * .55], int(r * .32), outline=rgba(WHITE, a), width=max(3, r // 9))
        d.ellipse([cx - r * .26, cy - r * .26, cx + r * .26, cy + r * .26], outline=rgba(WHITE, a), width=max(3, r // 9))
        d.ellipse([cx + r * .3, cy - r * .42, cx + r * .42, cy - r * .3], fill=rgba(WHITE, a))
    elif red == "facebook":
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rgba((24, 119, 242), a))
        text(L, (cx + r * .06, cy + r * .12), "f", font("Black", int(r * 1.5)), WHITE, a)
    elif red == "tiktok":
        d.rounded_rectangle([cx - r, cy - r, cx + r, cy + r], int(r * .35), fill=rgba((10, 10, 14), a))
        for dx, dy, c in [(-3, -2, (37, 244, 238)), (3, 2, (254, 44, 85)), (0, 0, (255, 255, 255))]:
            x, y = cx + dx * r / 30, cy + dy * r / 30
            d.ellipse([x - r * .5, y + r * .05, x - r * .05, y + r * .5], outline=rgba(c, a), width=max(3, r // 8))
            d.line([x - r * .07, y + r * .28, x - r * .07, y - r * .55], fill=rgba(c, a), width=max(3, r // 8))
            d.arc([x - r * .07, y - r * .75, x + r * .45, y - r * .25], 180, 270, fill=rgba(c, a), width=max(3, r // 8))
    else:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rgba(ORANGE, a))
        d.ellipse([cx - r * .6, cy - r * .6, cx + r * .6, cy + r * .6], outline=rgba(WHITE, a), width=max(3, r // 10))
        d.ellipse([cx - r * .25, cy - r * .6, cx + r * .25, cy + r * .6], outline=rgba(WHITE, a), width=max(3, r // 10))
        d.line([cx - r * .6, cy, cx + r * .6, cy], fill=rgba(WHITE, a), width=max(3, r // 10))

def bloque_redes(L, top, lt, inicio, a):
    """Lista de redes con ícono y usuario, apareciendo una por una."""
    f = font("Bold", 50)
    ancho = max(f.getlength(u) for _, u in REDES) + 110
    x0 = W / 2 - ancho / 2
    pill(L, [x0 - 40, top - 20, x0 + ancho + 40, top + len(REDES) * 105 + 5], WHITE, 0.10 * a, 36)
    for i, (red, usuario) in enumerate(REDES):
        p, dy = appear(lt, inicio + i * 0.15)
        y = top + 45 + i * 105
        icono(L, red, int(x0 + 36), int(y + dy * 0.3), 34, a * p)
        text(L, (x0 + 100, y + dy * 0.3), usuario, f, WHITE, a * p, "lm")

def marca_pie(L):
    """Logo oficial SIEMPRE sobre tarjeta blanca (pedido del dueño: que resalten sus colores)."""
    global _LOGO_PIE
    if LOGO is not None:
        if _LOGO_PIE is None:
            h = 104; w = int(LOGO.width * h / LOGO.height)
            _LOGO_PIE = LOGO.resize((w, h), Image.LANCZOS)
        w, h = _LOGO_PIE.size
        x, y = int(W / 2 - w / 2), H - 112 - h // 2
        ImageDraw.Draw(L).rounded_rectangle([x - 26, y - 14, x + w + 26, y + h + 14], 30, fill=(255, 255, 255, 255))
        L.alpha_composite(_LOGO_PIE, (x, y))
    else:
        text(L, (W/2, H - 120), "JETPORT COURIER", font("Black", 44), WHITE)
        ImageDraw.Draw(L).rectangle([W/2 - 60, H - 85, W/2 + 60, H - 79], fill=rgba(ORANGE, 1))

def esc_cta(L, e, lt, a):
    if e.get("modo") == "escribenos":
        return esc_cta_escribenos(L, e, lt, a)
    p, dy = appear(lt, 0.0)
    text(L, (W/2, 430 + dy), e.get("linea1", "Síguenos"), font("Black", 130), WHITE, a * p)
    text(L, (W/2, 570 + dy), e.get("linea2", "para más tips"), font("Black", 100), ORANGE, a * p)
    p, dy = appear(lt, 0.3)
    text(L, (W/2, 700 + dy), e.get("sub", "de compras internacionales"), font("Bold", 56), SOFT, a * p)
    bloque_redes(L, 820, lt, 0.5, a)
    p, dy = appear(lt, 1.3)
    text(L, (W/2, 1330 + dy), "USA y China → Perú · Los Olivos, Lima", font("Medium", 44), SOFT, a * p)

def esc_cta_escribenos(L, e, lt, a):
    """Cierre que invita a escribir (sin números de contacto): 'Escríbenos INFO'."""
    p, dy = appear(lt, 0.0)
    block(L, 520 + dy, e.get("linea1", "¿Quieres traer tus compras?"), "Black", 88, WHITE, a * p, max_lines=2)
    p, dy = appear(lt, 0.4)
    text(L, (W/2, 790 + dy), "Escríbenos", font("Black", 120), ORANGE, a * p)
    p, dy = appear(lt, 0.8)
    pulse = 1 + 0.04 * math.sin(lt * 6); bw, bh = 300 * pulse, 90 * pulse
    pill(L, [W/2 - bw, 1010 - bh + dy, W/2 + bw, 1010 + bh + dy], WHITE, a * p, 90)
    text(L, (W/2, 1010 + dy), e.get("palabra", "INFO"), font("Black", 110), NAVY, a * p)
    p, dy = appear(lt, 1.2)
    block(L, 1170 + dy, e.get("sub", "por mensaje o en los comentarios y te ayudamos"), "Bold", 50, SOFT, a * p, max_lines=2)
    p, dy = appear(lt, 1.5)
    for i, (red, _) in enumerate(REDES):
        icono(L, red, int(W / 2 + (i - 1.5) * 120), 1345 + dy, 40, a * p)
    text(L, (W/2, 1430 + dy), "Jetport Courier en todas las redes", font("Bold", 42), WHITE, a * p)

# ---------- clips reales (material/ del repositorio) ----------
class Clip:
    """Lee un video real recortado a 1080x1920 (rellena la pantalla) a 30 fps.
    En vista previa saca un solo cuadro; al renderizar lee los cuadros en orden con ffmpeg."""
    def __init__(self, ruta, inicio, dur, recorte=None):
        self.ruta, self.inicio, self.dur = ruta, float(inicio), float(dur)
        self.proc, self.ultimo = None, None
        pre = f"crop={recorte[2]}:{recorte[3]}:{recorte[0]}:{recorte[1]}," if recorte else ""
        self.vf = pre + f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}"

    def cuadro_suelto(self, lt):
        out = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", str(self.inicio + lt), "-i", self.ruta,
                              "-frames:v", "1", "-vf", self.vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                             capture_output=True).stdout
        return Image.frombytes("RGB", (W, H), out[: W * H * 3]) if len(out) >= W * H * 3 else Image.new("RGB", (W, H))

    def siguiente(self):
        if self.proc is None:
            self.proc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-ss", str(self.inicio), "-i", self.ruta,
                                          "-t", str(self.dur + 0.5), "-vf", self.vf, "-an", "-f", "rawvideo",
                                          "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE,
                                         stderr=subprocess.DEVNULL)
        buf = self.proc.stdout.read(W * H * 3)
        if len(buf) == W * H * 3:
            self.ultimo = Image.frombytes("RGB", (W, H), buf)
        return self.ultimo or Image.new("RGB", (W, H))

_clips = {}
MODO_PREVIA = False

def fondo_clip(i, e, lt):
    if i not in _clips:
        _clips[i] = Clip(e["archivo"], e.get("inicio", 0), e["dur"], e.get("recorte"))
    img = _clips[i].cuadro_suelto(lt) if MODO_PREVIA else _clips[i].siguiente()
    z = 1.0 + 0.06 * min(lt / max(float(e["dur"]), 0.1), 1.0)       # acercamiento lento (efecto Ken Burns)
    cw, ch = int(W / z), int(H / z)
    img = img.crop(((W - cw) // 2, (H - ch) // 2, (W + cw) // 2, (H + ch) // 2)).resize((W, H), Image.BILINEAR)
    sombra = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(sombra)
    for y in range(0, 760, 8):                                        # degradado oscuro arriba para leer el texto
        d.rectangle([0, y, W, y + 8], fill=(0, 0, 0, int(150 * (1 - y / 760))))
    for y in range(H - 520, H, 8):                                    # y abajo para la marca
        d.rectangle([0, y, W, y + 8], fill=(0, 0, 0, int(140 * (y - (H - 520)) / 520)))
    img = img.convert("RGBA"); img.alpha_composite(sombra); return img

def texto_borde(L, xy, s, f, color, a, borde=8):
    ImageDraw.Draw(L).text(xy, s, font=f, fill=rgba(color, a), anchor="mm",
                           stroke_width=borde, stroke_fill=rgba((0, 0, 0), a))

def esc_clip(L, e, lt, a):
    """Escena sobre video real con texto estilo TikTok (blanco con borde negro).
    "subtitulos": [[desde, hasta, "texto"], ...] muestra subtítulos abajo (para videos con voz)."""
    for desde, hasta, frase in e.get("subtitulos", []):
        if desde <= lt < hasta:
            f, lines, sz = fit(frase, "Black", 64, W - 160, 3)
            y = 1500 - (len(lines) - 1) * sz * 0.6
            for ln in lines:
                texto_borde(L, (W / 2, y), ln, f, (255, 214, 64), a, borde=8); y += sz * 1.15
    pos = {"arriba": 330, "centro": 860, "abajo": 1380}[e.get("posicion", "arriba")]
    p = ease((lt - 0.15) / 0.3)
    escala = 1 + 0.25 * (1 - p)                                       # el texto entra "de golpe"
    f, lines, s = fit(e.get("texto", ""), "Black", int(84 * escala), W - 140, 4)
    y = pos
    for ln in lines:
        texto_borde(L, (W / 2, y), ln, f, WHITE, a * p, borde=9); y += s * 1.15
    if e.get("resaltado"):
        p2 = ease((lt - 0.6) / 0.3)
        f2, l2, s2 = fit(e["resaltado"], "Black", 96, W - 200, 2)
        y += 30
        for ln in l2:
            tw = f2.getlength(ln)
            pill(L, [W/2 - tw/2 - 34, y - s2 * 0.62, W/2 + tw/2 + 34, y + s2 * 0.62], ORANGE, a * p2, 24)
            text(L, (W / 2, y), ln, f2, WHITE, a * p2); y += s2 * 1.3

TIPOS = {"titulo": esc_titulo, "punto": esc_punto, "texto": esc_texto, "cta": esc_cta, "clip": esc_clip}

def transicion(img, lt, tipo):
    """Efecto al entrar en una escena: 'zoom' (golpe de zoom + destello), 'barrido' o 'ninguna'."""
    if tipo == "ninguna" or lt > 0.3: return img
    k = ease(lt / 0.25)
    if tipo == "barrido":
        dx = int((1 - k) * W * 0.35)
        img2 = img.filter(ImageFilter.GaussianBlur(14 * (1 - k))) if k < 1 else img
        base = Image.new("RGBA", (W, H), (0, 0, 0, 255)); base.alpha_composite(img2, (dx, 0)); img = base
    else:
        z = 1 + 0.14 * (1 - k); cw, ch = int(W / z), int(H / z)
        img = img.crop(((W - cw) // 2, (H - ch) // 2, (W + cw) // 2, (H + ch) // 2)).resize((W, H), Image.BILINEAR)
    fl = max(0.0, 0.55 * (1 - lt / 0.18))
    if fl > 0:
        img = Image.blend(img, Image.new("RGBA", (W, H), (255, 255, 255, 255)), fl)
    return img

def build(guion):
    escenas, t = [], 0.0
    for e in guion["escenas"]:
        escenas.append((t, t + float(e["dur"]), e)); t += float(e["dur"])
    return escenas, t

def frame(escenas, total, t):
    idx, t_esc = 0, t
    for i, (s, e_, _) in enumerate(escenas):
        if s <= t: idx, t_esc = i, t - s
    s0, e0, esc = escenas[idx]
    es_clip = esc["tipo"] == "clip"
    img = fondo_clip(idx, esc, t_esc) if es_clip else fondo(t, idx, t_esc)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if not es_clip:
        d = ImageDraw.Draw(L); off = (t * 120) % 400
        for k in range(-2, 7):
            x0 = k * 400 + off - 600
            d.polygon([(x0, 0), (x0 + 60, 0), (x0 + 760, H), (x0 + 700, H)], fill=(255, 255, 255, 10))
    a = 1.0 if (t <= e0 - 0.3 or e0 >= total) else (e0 - t) / 0.3
    if es_clip and esc.get("transicion", "zoom") != "ninguna":
        a = 1.0                                   # en clips el corte lo marca la transición, sin fundido
    if not es_clip:
        a_in = ease(t_esc / 0.35) if idx > 0 else 1.0
        escenario(L, esc.get("fondo") or ORDEN_ESCENARIOS[idx % len(ORDEN_ESCENARIOS)], t, a * a_in)
    TIPOS[esc["tipo"]](L, esc, t_esc, a)
    progress(L, t, total)
    marca_pie(L)
    img.alpha_composite(L)
    if idx > 0:
        img = transicion(img, t_esc, esc.get("transicion", "zoom"))
    return img.convert("RGB")

def main():
    guion = json.load(open(sys.argv[1], encoding="utf-8")); out = sys.argv[2]
    escenas, total = build(guion)
    if len(sys.argv) > 3:
        global MODO_PREVIA; MODO_PREVIA = True
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
    for c in _clips.values():
        if c.proc: c.proc.kill()
    voces = [(s0, e) for s0, _, e in escenas if e["tipo"] == "clip" and e.get("con_audio")]
    entradas = ["-i", muda, "-i", wav]
    if not voces:
        filtro, mapa = None, "1:a"
    else:
        partes = ["[1:a]volume=0.22[mus]"]; etiquetas = ["[mus]"]
        for k, (s0, e) in enumerate(voces):
            entradas += ["-ss", str(e.get("inicio", 0)), "-t", str(e["dur"]), "-i", e["archivo"]]
            ms = int(s0 * 1000)
            partes.append(f"[{k + 2}:a]aresample=44100,volume=1.6,adelay={ms}|{ms}[v{k}]"); etiquetas.append(f"[v{k}]")
        partes.append("".join(etiquetas) + f"amix=inputs={len(etiquetas)}:duration=first:normalize=0,alimiter=limit=0.95[a]")
        filtro, mapa = ";".join(partes), "[a]"
    cmd = ["ffmpeg", "-y", "-loglevel", "error"] + entradas
    if filtro: cmd += ["-filter_complex", filtro]
    cmd += ["-map", "0:v", "-map", mapa, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
            "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    main()
