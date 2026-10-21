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
Fondos variados (por defecto): además del degradado, cada escena usa un fondo distinto que llama la atención:
  "rayos", "confeti", "ciudad" (atardecer con edificios y palmeras), "patron" (cajas y aviones), "burbujas",
  "puntos" o "degradado". Se rotan solos (inicio distinto según musica_semilla, nunca dos escenas seguidas iguales).
  Fíjalo por escena con "estilo_fondo": "confeti", o por video con "fondos": ["rayos", "ciudad", ...].
La escena "cta" admite "modo": "seguir" (por defecto: Síguenos @jetportcourier) o "escribenos"
(Escríbenos "INFO"; opcionales "linea1", "palabra", "sub").
Clips reales: escena {"tipo": "clip", "dur": 3, "archivo": "material/clip.mp4", "inicio": 2.0,
  "texto": "POV: llegó tu pedido de Amazon", "resaltado": "📦", "posicion": "arriba|centro|abajo"}
  usa el video real como fondo (recortado a vertical, con acercamiento lento) y texto estilo TikTok.
  Opcionales: "recorte": [x, y, ancho, alto] para quitar franjas negras o subtítulos quemados del original;
  "con_audio": true para usar la voz del clip (la música baja de volumen); "subtitulos": [[desde, hasta, "frase"]].
  También acepta FOTOS (.png/.jpg) como "archivo": se muestran con acercamiento lento.
  "globo": "texto" dibuja un globo de diálogo blanco (para que la presentadora 'hable'); "globo_y" ajusta la altura.
  (Las fotos y videos del avatar en referencias/ son SOLO referencia del dueño: NO usarlos en los videos.)
Cierre: al final de cada video se agrega solo un cierre animado de 2,6 s (círculo blanco que se abre, logo
  con rebote, lema y fundido). Hay 3 variantes que se rotan solas: "circulo", "barrido" y "persiana". Opcional "lema" en una escena {"tipo": "cierre", "dur": 2.6}; "cierre": false lo quita.
Transiciones: cualquier escena puede llevar "transicion": "zoom" (golpe de zoom + destello), "barrido"
  (deslizamiento lateral), "deslizar" (entra desde abajo), "giro", "sacudida" (temblor + colores separados),
  "glitch" (falla digital), "destello" (flash blanco fuerte) o "ninguna". Si no se indica: en escenas "clip" se
  rotan todas (zoom, glitch, giro, deslizar, sacudida, destello, barrido); en las demás se alternan zoom y barrido.
  Cada transición suena con un "whoosh" ("whoosh": false en el guion lo quita). Los clips llevan además un
  "pulso" (golpe de zoom suave en cada tiempo de la música); "pulso": false en la escena lo quita.
Marca: generador/logo_horizontal.png (logo oficial) va en el pie de todos los cuadros, SIEMPRE sobre tarjeta blanca.\n  generador/logo_vertical.png es la versión vertical, también sobre blanco.
La escena "cta" muestra las redes oficiales (TikTok @jetport_courier, Instagram @jetportcourier,
  Facebook Jetport Courier, jpcourier.com).
Música: "musica_semilla" de 0 a 119 elige estilo, acordes, tono y velocidad (ver musica.py); usa una distinta en cada video.
Los emojis NO se ven dentro del video (se quitan solos): úsalos solo en el texto de la publicación.
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

# ---------- fondos variados (pedido del dueño 16/10/2026: no solo degradados de color; variar siempre) ----------
# Tipos: "degradado" (el original), "rayos" (rayos de sol pop que giran), "confeti" (confeti y estrellas que caen),
# "ciudad" (atardecer con edificios y palmeras de Miami), "patron" (patrón de cajas y aviones que se desliza),
# "burbujas" (luces de colores desenfocadas), "puntos" (trama pop de puntos con ondas).
# Cada escena puede llevar "estilo_fondo"; si no, se rotan solos empezando en un punto distinto según la
# musica_semilla, sin repetir el mismo tipo en dos escenas seguidas. El guion puede fijar "fondos": [lista].
TIPOS_FONDO = ["rayos", "confeti", "ciudad", "patron", "burbujas", "puntos", "degradado"]
_cache_fondo = {}

def _oscurecer(img, k=0.30):
    """Velo oscuro suave en la zona del texto para que siempre se lea bien."""
    if "velo" not in _cache_fondo:
        yy = np.linspace(0, 1, H, dtype=np.float32)
        a = (k * 255 * np.exp(-((yy - 0.5) / 0.32) ** 2)).astype(np.uint8)
        capa = Image.new("RGBA", (W, H), (5, 12, 35, 0)); capa.putalpha(Image.fromarray(np.repeat(a[:, None], W, 1)))
        _cache_fondo["velo"] = capa
    img.alpha_composite(_cache_fondo["velo"]); return img

def _f_degradado(t, idx, c1, c2):
    img = _gradiente(c1, c2, 1.1 + 0.25 * math.sin(t * 0.6)).convert("RGBA")
    img.alpha_composite(_GLOW_NARANJA, (int(W * 0.75 + 160 * math.sin(t * 0.7)) - 520, int(H * 0.18 + 120 * math.cos(t * 0.5)) - 520))
    img.alpha_composite(_GLOW_CIAN, (int(W * 0.15 + 140 * math.cos(t * 0.6)) - 460, int(H * 0.82 + 100 * math.sin(t * 0.8)) - 460))
    return img

def _f_rayos(t, idx, c1, c2):
    sw, sh = W // 3, H // 3
    im = Image.new("RGB", (sw, sh), c1); d = ImageDraw.Draw(im)
    cx, cy, R, n = sw / 2, sh * 0.42, sh * 1.2, 18
    giro = t * 0.25
    for i in range(n):
        a0 = giro + i * 2 * math.pi / n; a1 = a0 + math.pi / n
        d.polygon([(cx, cy), (cx + R * math.cos(a0), cy + R * math.sin(a0)), (cx + R * math.cos(a1), cy + R * math.sin(a1))], fill=c2)
    img = im.resize((W, H), Image.BILINEAR).convert("RGBA")
    img.alpha_composite(_GLOW_NARANJA, (W // 2 - 520, int(H * 0.42) - 520))
    return _oscurecer(img, 0.28)

def _f_confeti(t, idx, c1, c2):
    img = _gradiente(c1, c2, 0.9).convert("RGBA")
    d = ImageDraw.Draw(img)
    cols = [(255, 214, 64), (255, 122, 26), (80, 200, 255), (236, 72, 153), (120, 230, 140)]
    r = np.random.default_rng(idx * 7 + 3)
    for k in range(60):
        x0, v, fase, tam = r.random() * W, 90 + r.random() * 160, r.random() * 10, 10 + r.random() * 16
        y = (r.random() * (H + 200) + t * v) % (H + 200) - 100
        x = x0 + 40 * math.sin(t * 1.5 + fase)
        ang = t * 3 + fase; w2 = tam * abs(math.cos(ang)) + 3
        c = cols[k % len(cols)]
        if 520 < y < 1000 and 120 < x < W - 120: continue      # deja libre la zona de títulos
        if k % 5 == 0:                                          # estrellitas
            pts = [(x + (tam if j % 2 == 0 else tam * 0.45) * math.cos(ang + j * math.pi / 5),
                    y + (tam if j % 2 == 0 else tam * 0.45) * math.sin(ang + j * math.pi / 5)) for j in range(10)]
            d.polygon(pts, fill=c + (230,))
        else:
            d.rectangle([x - w2, y - tam * 0.45, x + w2, y + tam * 0.45], fill=c + (215,))
    return _oscurecer(img, 0.22)

def _f_ciudad(t, idx, c1, c2):
    key = ("ciudad", c1, c2)
    if key not in _cache_fondo:
        cielo = _gradiente((120, 40, 160), (255, 120, 80), 1.57).convert("RGBA")      # atardecer
        cielo = Image.blend(cielo, _gradiente(c1, c2, 1.57).convert("RGBA"), 0.2)
        sil = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(sil)
        r = np.random.default_rng(5); x = -20
        while x < W:                                            # edificios
            w2 = int(70 + r.random() * 90); h2 = int(180 + r.random() * 380)
            d.rectangle([x, 1500 - h2, x + w2, H], fill=(28, 20, 70, 235))
            for yy in range(1500 - h2 + 30, 1480, 46):          # ventanas encendidas
                for xx in range(x + 14, x + w2 - 14, 30):
                    if r.random() < 0.45: d.rectangle([xx, yy, xx + 12, yy + 18], fill=(255, 214, 120, 150))
            x += w2 + 8
        for px in (90, 960):                                    # palmeras
            d.line([px, 1500, px + 30, 1180], fill=(20, 14, 50, 255), width=22)
            for k in range(7):
                a0 = math.pi * (1.05 + k * 0.15)
                d.line([px + 30, 1180, px + 30 + 190 * math.cos(a0), 1180 + 110 * math.sin(a0) + 60], fill=(20, 14, 50, 255), width=16)
        d.rectangle([0, 1500, W, H], fill=(20, 14, 50, 255))
        _cache_fondo[key] = (cielo, sil)
    cielo, sil = _cache_fondo[key]
    img = cielo.copy(); d = ImageDraw.Draw(img)
    sy = 1290 + 20 * math.sin(t * 0.4)
    for rr, al in ((260, 50), (200, 90), (150, 255)):           # sol con halo
        d.ellipse([W / 2 - rr, sy - rr, W / 2 + rr, sy + rr], fill=(255, 210, 90, al))
    img.alpha_composite(sil)
    return _oscurecer(img, 0.30)

def _f_patron(t, idx, c1, c2):
    key = ("patron", c1, c2)
    if key not in _cache_fondo:
        T = 270
        tile = Image.new("RGBA", (T, T), (0, 0, 0, 0)); d = ImageDraw.Draw(tile)
        _dibujar_caja(d, 30, 40, 90, 70, 0.30, etiqueta=False)
        plane(tile, 195, 190, 45, 0.20)
        d.ellipse([190, 40, 214, 64], fill=(255, 214, 64, 70)); d.ellipse([40, 190, 58, 208], fill=(255, 255, 255, 60))
        grande = Image.new("RGBA", (W + T, H + T), (0, 0, 0, 0))
        for yy in range(0, H + T, T):
            for xx in range(0, W + T, T): grande.alpha_composite(tile, (xx, yy))
        _cache_fondo[key] = (_gradiente(c1, c2, 1.0).convert("RGBA"), grande, T)
    base, grande, T = _cache_fondo[key]
    img = base.copy(); o = int(t * 45) % T
    img.alpha_composite(grande.crop((T - o, o, T - o + W, o + H)))
    return _oscurecer(img, 0.25)

def _f_burbujas(t, idx, c1, c2):
    sw, sh = W // 4, H // 4
    im = _gradiente(c1, c2, 1.3).resize((sw, sh)).convert("RGBA")
    capa = Image.new("RGBA", (sw, sh), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    cols = [(255, 122, 26), (80, 200, 255), (236, 72, 153), (255, 214, 64), (255, 255, 255)]
    r = np.random.default_rng(idx * 11 + 1)
    for k in range(16):
        rad = 20 + r.random() * 55
        x = (r.random() * sw + 18 * math.sin(t * 0.5 + k)) % sw
        y = (r.random() * sh - t * (6 + r.random() * 10)) % (sh + 100) - 50
        d.ellipse([x - rad, y - rad, x + rad, y + rad], fill=cols[k % 5] + (70,))
    capa = capa.filter(ImageFilter.GaussianBlur(5))
    im.alpha_composite(capa)
    return _oscurecer(im.resize((W, H), Image.BILINEAR), 0.25)

def _f_puntos(t, idx, c1, c2):
    key = ("puntos", c1, c2)
    if key not in _cache_fondo:
        sw, sh = W // 2, H // 2
        yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
        _cache_fondo[key] = (_gradiente(c1, c2, 0.6).convert("RGBA"), xx, yy)
    base, xx, yy = _cache_fondo[key]
    paso = 27.0
    gx = (xx % paso) - paso / 2; gy = (yy % paso) - paso / 2
    onda = 0.5 + 0.5 * np.sin((xx * 0.012 + yy * 0.02) - t * 2.2)
    rad = 2.5 + 7.5 * onda
    a = np.clip((rad - np.hypot(gx, gy)) * 1.5, 0, 1) * 60
    capa = Image.new("RGBA", (W // 2, H // 2), (255, 255, 255, 0)); capa.putalpha(Image.fromarray(a.astype(np.uint8)))
    img = base.copy(); img.alpha_composite(capa.resize((W, H), Image.BILINEAR))
    img.alpha_composite(_GLOW_NARANJA, (int(W * 0.8 + 120 * math.sin(t * 0.6)) - 520, int(H * 0.2) - 520))
    return _oscurecer(img, 0.22)

FONDOS = {"degradado": _f_degradado, "rayos": _f_rayos, "confeti": _f_confeti, "ciudad": _f_ciudad,
          "patron": _f_patron, "burbujas": _f_burbujas, "puntos": _f_puntos}
# paletas vivas extra para los fondos nuevos (sin naranja dominante para que los títulos naranjas resalten)
PALETAS_VIVAS = [
    ((88, 24, 140), (200, 40, 120)),   # morado → fucsia
    ((0, 92, 151), (20, 170, 170)),    # azul → turquesa
    ((30, 60, 190), (110, 50, 200)),   # azul rey → violeta
    ((150, 20, 90), (60, 20, 120)),    # frambuesa → uva
    ((10, 110, 120), (30, 70, 180)),   # verde mar → azul
]
TIPO_FONDO_ESCENA = {}       # idx de escena -> tipo, lo llena build()

def _fondo_tipo(t, idx):
    tipo = TIPO_FONDO_ESCENA.get(idx, "degradado")
    if tipo == "degradado":
        c1, c2 = PALETAS[idx % len(PALETAS)]
    else:
        c1, c2 = PALETAS_VIVAS[(idx + SEMILLA) % len(PALETAS_VIVAS)]
    return FONDOS[tipo](t, idx, c1, c2)

def fondo(t, idx, t_escena):
    """Fondo animado de la escena; al entrar se funde con el fondo de la escena anterior."""
    img = _fondo_tipo(t, idx)
    if idx > 0 and t_escena < 0.45:
        prev = _fondo_tipo(t, idx - 1)
        img = Image.blend(prev, img, ease(t_escena / 0.45))
    return img

SEMILLA = 0

def ease(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
def rgba(c, a): return c + (int(255 * max(0, min(1, a))),)
def appear(t, start, dur=0.45):
    e = ease((t - start) / dur); return e, int((1 - e) * 60)

def limpiar(texto):
    """Quita emojis y símbolos que la fuente no tiene (en el video saldrían como cuadritos)."""
    t = "".join(c for c in str(texto) if ord(c) < 0x2190 or c in "→←")
    return " ".join(t.split())

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
    texto = limpiar(texto)
    while True:
        f = font(weight, size); lines = wrap(texto, f, maxw)
        if len(lines) <= max_lines or size <= min_size: return f, lines, size
        size -= 4

def text(L, xy, s, f, fill, a=1.0, anchor="mm"):
    s = limpiar(s) if s not in ("→",) else s
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

# Estilo de los recuadros (TIP y redes): "blanco" (tarjeta blanca sólida), "oscuro" (azul oscuro sólido con
# borde naranja) o "cristal" (oscuro translúcido con borde blanco). Se elige en el guion con "estilo_caja".
ESTILO_CAJA = "blanco"       # aprobado por el dueño

def tarjeta(L, box, a, r=40):
    """Dibuja el fondo del recuadro según el estilo y devuelve el color del texto que va encima."""
    d = ImageDraw.Draw(L)
    if ESTILO_CAJA == "blanco":
        d.rounded_rectangle([box[0] + 6, box[1] + 10, box[2] + 6, box[3] + 10], r, fill=(0, 0, 0, int(70 * a)))
        d.rounded_rectangle(box, r, fill=rgba(WHITE, 0.97 * a))
        d.rounded_rectangle([box[0], box[1], box[0] + 14, box[3]], 7, fill=rgba(ORANGE, a))
        return NAVY
    if ESTILO_CAJA == "oscuro":
        d.rounded_rectangle(box, r, fill=rgba((8, 22, 56), 0.92 * a), outline=rgba(ORANGE, a), width=5)
        return WHITE
    d.rounded_rectangle(box, r, fill=(0, 0, 0, int(120 * a)), outline=rgba(WHITE, 0.55 * a), width=3)
    return WHITE

def _caja(L, top, texto, lt, a):
    if not texto: return
    p, dy = appear(lt, 0.8)
    f, lines, s = fit(texto, "Medium", 54, W - 2 * MARGIN - 80, 5)
    hgt = 110 + len(lines) * s * 1.25
    color = tarjeta(L, [MARGIN, top + dy, W - MARGIN, top + hgt + dy], a * p)
    text(L, (MARGIN + 50, top + 50 + dy), "TIP", font("Black", 44), ORANGE, a * p, "lm")
    for i, ln in enumerate(lines):
        text(L, (W/2, top + 115 + i * s * 1.25 + dy), ln, f, color, a * p)

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
    color = tarjeta(L, [x0 - 40, top - 20, x0 + ancho + 40, top + len(REDES) * 105 + 5], a, 36)
    for i, (red, usuario) in enumerate(REDES):
        p, dy = appear(lt, inicio + i * 0.15)
        y = top + 45 + i * 105
        icono(L, red, int(x0 + 36), int(y + dy * 0.3), 34, a * p)
        text(L, (x0 + 100, y + dy * 0.3), usuario, f, color, a * p, "lm")

# Estilo del logo en el pie: "tarjeta" (sobre tarjeta blanca), "transparente" (sin fondo)
# o "contorno" (sin fondo, con un borde blanco suave para que no se pierda en fondos azules).
LOGO_ESTILO = "tarjeta"
LOGO_OPACIDAD = 0.85         # opacidad de la tarjeta blanca del logo (aprobado por el dueño: 85%)
_LOGOS = {}

def marca_pie(L):
    aqui = os.path.dirname(os.path.abspath(__file__))
    archivo = {"tarjeta": "logo_horizontal_transparente.png", "transparente": "logo_horizontal_transparente.png",
               "contorno": "logo_horizontal_contorno.png"}.get(LOGO_ESTILO, "logo_horizontal.png")
    ruta = os.path.join(aqui, archivo)
    if not os.path.exists(ruta):
        text(L, (W/2, H - 120), "JETPORT COURIER", font("Black", 44), WHITE); return
    if archivo not in _LOGOS:
        im = Image.open(ruta).convert("RGBA")
        h = 84 if LOGO_ESTILO == "tarjeta" else 128
        _LOGOS[archivo] = im.resize((int(im.width * h / im.height), h), Image.LANCZOS)
    lg = _LOGOS[archivo]; w, h = lg.size
    # la tarjeta va DEBAJO de la línea de la cinta transportadora (y = 1768), sin chocar con ella
    x, y = int(W / 2 - w / 2), (H - 70 - h // 2) if LOGO_ESTILO == "tarjeta" else (H - 112 - h // 2)
    if LOGO_ESTILO == "tarjeta":
        ImageDraw.Draw(L).rounded_rectangle([x - 24, y - 12, x + w + 24, y + h + 12], 26,
                                            fill=(255, 255, 255, int(255 * LOGO_OPACIDAD)))
    L.alpha_composite(lg, (x, y))

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
        self.loop = ["-loop", "1"] if ruta.lower().endswith((".png", ".jpg", ".jpeg", ".webp")) else []

    def cuadro_suelto(self, lt):
        out = subprocess.run(["ffmpeg", "-loglevel", "error"] + self.loop + ["-ss", str(self.inicio + lt), "-i", self.ruta,
                              "-frames:v", "1", "-vf", self.vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                             capture_output=True).stdout
        return Image.frombytes("RGB", (W, H), out[: W * H * 3]) if len(out) >= W * H * 3 else Image.new("RGB", (W, H))

    def siguiente(self):
        if self.proc is None:
            self.proc = subprocess.Popen(["ffmpeg", "-loglevel", "error"] + self.loop + ["-ss", str(self.inicio), "-i", self.ruta,
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

def _globo(L, frase, lt, a, y_top):
    """Globo de diálogo blanco (la presentadora 'habla'), aparece con un pequeño rebote."""
    p = ease((lt - 0.25) / 0.35)
    if p <= 0: return
    f, lines, sz = fit(frase, "Bold", 58, W - 300, 4)
    hgt = 70 + len(lines) * sz * 1.22
    x0, x1 = 110, W - 110
    y0 = y_top + (1 - p) * 40
    d = ImageDraw.Draw(L)
    d.rounded_rectangle([x0, y0, x1, y0 + hgt], 44, fill=(255, 255, 255, int(245 * a * p)))
    d.polygon([(W / 2 - 40, y0 + 2), (W / 2 + 30, y0 + 2), (W / 2 - 10, y0 - 50)], fill=(255, 255, 255, int(245 * a * p)))
    for i, ln in enumerate(lines):
        text(L, (W / 2, y0 + 35 + sz * 0.62 + i * sz * 1.22), ln, f, NAVY, a * p)

def esc_clip(L, e, lt, a):
    """Escena sobre video real con texto estilo TikTok (blanco con borde negro).
    "subtitulos": [[desde, hasta, "texto"], ...] muestra subtítulos abajo (para videos con voz)."""
    for desde, hasta, frase in e.get("subtitulos", []):
        if desde <= lt < hasta:
            f, lines, sz = fit(frase, "Black", 64, W - 160, 3)
            y = 1500 - (len(lines) - 1) * sz * 0.6
            for ln in lines:
                texto_borde(L, (W / 2, y), ln, f, (255, 214, 64), a, borde=8); y += sz * 1.15
    if e.get("globo"):
        _globo(L, e["globo"], lt, a, e.get("globo_y", 1230))
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

_LOGO_V = None
def esc_cierre(L, e, lt, a):
    """Final animado: círculo blanco que se abre, logo con rebote y lema; evita que el video acabe en seco."""
    global _LOGO_V
    dur = float(e["dur"])
    d = ImageDraw.Draw(L)
    k = ease(lt / 0.55)
    variante = e.get("variante", "circulo")
    if variante == "barrido":                           # franja blanca diagonal que barre la pantalla
        x = k * W * 1.55
        d.polygon([(-W * 2, 0), (x, 0), (x - W * 0.45, H), (-W * 2, H)], fill=(255, 255, 255, 255))
        if k >= 1: d.rectangle([0, 0, W, H], fill=(255, 255, 255, 255))
        borde = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        if k < 1:
            ImageDraw.Draw(borde).polygon([(x, 0), (x + 40, 0), (x - W * 0.45 + 40, H), (x - W * 0.45, H)], fill=rgba(ORANGE, 0.9))
        L.alpha_composite(borde)
    elif variante == "persiana":                        # franjas que se cierran una tras otra
        n = 8
        for i in range(n):
            ki = ease((lt - i * 0.04) / 0.4)
            hh = H / n
            d.rectangle([0, i * hh, W * ki, (i + 1) * hh + 1] if i % 2 == 0 else [W * (1 - ki), i * hh, W, (i + 1) * hh + 1],
                        fill=(255, 255, 255, 255))
    else:                                               # círculo que se abre desde el centro
        r = k * math.hypot(W, H) * 0.6
        d.ellipse([W / 2 - r, H / 2 - r, W / 2 + r, H / 2 + r], fill=(255, 255, 255, 255))
        r = r if variante == "circulo" else r
    anillos = Image.new("RGBA", (W, H), (0, 0, 0, 0)); da = ImageDraw.Draw(anillos)
    for k in range(3 if variante == "circulo" else 0):  # anillos naranja/azul que acompañan la apertura
        rr = r * (1 + 0.06 * (k + 1)); al = max(0.0, 1 - lt / 0.7) * (0.6 - 0.15 * k)
        if al > 0:
            da.ellipse([W / 2 - rr, H / 2 - rr, W / 2 + rr, H / 2 + rr], outline=rgba(ORANGE if k % 2 == 0 else (30, 99, 200), al), width=10)
    L.alpha_composite(anillos)
    if _LOGO_V is None:
        ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo_vertical.png")
        _LOGO_V = Image.open(ruta).convert("RGBA") if os.path.exists(ruta) else None
    p = max(0.0, (lt - 0.35) / 0.5)
    if _LOGO_V is not None and p > 0:
        rebote = 1 + 0.12 * math.sin(min(p, 1) * math.pi) * (1 - min(p, 1)) * 2 if p < 1 else 1.0
        esc = min(p, 1) ** 0.6 * rebote
        h = int(620 * esc)
        if h > 10:
            lg = _LOGO_V.resize((int(_LOGO_V.width * h / _LOGO_V.height), h), Image.LANCZOS)
            L.alpha_composite(lg, (int(W / 2 - lg.width / 2), int(820 - h / 2)))
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))     # texto en capa aparte para mezclarlo bien sobre el blanco
    p2, dy = appear(lt, 0.9)
    if p2 > 0.01:
        text(capa, (W / 2, 1260 + dy), e.get("lema", "Tus compras de USA y China, en Perú"), font("Bold", 50), NAVY, p2)
    p3, dy3 = appear(lt, 1.2)
    if p3 > 0.01:
        text(capa, (W / 2, 1345 + dy3), "@jetport_courier  ·  @jetportcourier", font("Medium", 40), (90, 110, 140), p3)
    L.alpha_composite(capa)
    fin = max(0.0, (lt - (dur - 0.45)) / 0.45)          # fundido a blanco al final
    if fin > 0:
        L.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255 * min(fin, 1)))))

TIPOS = {"cierre": esc_cierre, "titulo": esc_titulo, "punto": esc_punto, "texto": esc_texto, "cta": esc_cta, "clip": esc_clip}

TRANS_DUR = 0.32
# Orden en que se rotan las transiciones en escenas "clip" cuando el guion no indica una (más dinámico)
TRANS_CLIPS = ["zoom", "glitch", "giro", "deslizar", "sacudida", "destello", "barrido"]

def _zoom(img, z, cx=0.5, cy=0.5):
    cw, ch = int(W / z), int(H / z)
    x0 = int(max(0, min(W - cw, cx * W - cw / 2))); y0 = int(max(0, min(H - ch, cy * H - ch / 2)))
    return img.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.BILINEAR)

def _rgb_split(img, d):
    r, g, b, a = img.split()
    r = r.transform(img.size, Image.AFFINE, (1, 0, -d, 0, 1, 0)); b = b.transform(img.size, Image.AFFINE, (1, 0, d, 0, 1, 0))
    return Image.merge("RGBA", (r, g, b, a))

def transicion(img, lt, tipo):
    """Efecto al entrar en una escena. Tipos: 'zoom' (golpe de zoom + destello), 'barrido' (deslizamiento lateral
    con desenfoque), 'deslizar' (entra desde abajo), 'giro' (gira y se endereza), 'sacudida' (temblor de cámara con
    colores separados), 'glitch' (franjas desplazadas tipo falla digital), 'destello' (flash blanco fuerte y zoom
    hacia afuera) o 'ninguna'. Cada transición lleva un 'whoosh' en el audio."""
    if tipo == "ninguna" or lt > TRANS_DUR + 0.05: return img
    k = ease(lt / TRANS_DUR); q = 1 - k
    if tipo == "barrido":
        dx = int(q * W * 0.45)
        img2 = img.filter(ImageFilter.BoxBlur(int(22 * q))) if q > 0.02 else img
        base = Image.new("RGBA", (W, H), (0, 0, 0, 255)); base.alpha_composite(img2, (dx, 0)); img = base
    elif tipo == "deslizar":
        dy = int(q * H * 0.4)
        img2 = img.filter(ImageFilter.BoxBlur(int(22 * q))) if q > 0.02 else img
        base = Image.new("RGBA", (W, H), (0, 0, 0, 255)); base.alpha_composite(img2, (0, dy)); img = base
    elif tipo == "giro":
        ang = 18 * q * (1 if int(lt * 1000) >= 0 else -1)
        img = _zoom(img, 1 + 0.35 * q).rotate(ang, Image.BILINEAR, fillcolor=(0, 0, 0, 255))
        if q > 0.05: img = img.filter(ImageFilter.GaussianBlur(8 * q))
    elif tipo == "sacudida":
        amp = 46 * q; f = lt * 60
        img = _zoom(img, 1.08, 0.5 + amp * math.sin(f * 1.7) / W, 0.5 + amp * math.cos(f * 2.3) / H)
        if q > 0.05: img = _rgb_split(img, int(28 * q))
    elif tipo == "glitch":
        if q > 0.04:
            img = _rgb_split(img, int(36 * q)); out = img.copy()
            import random; rnd = random.Random(int(lt * 1000))
            for _ in range(9):
                y = rnd.randrange(0, H - 60); hgt = rnd.randrange(30, 160); dx = int(rnd.uniform(-160, 160) * q)
                out.paste(img.crop((0, y, W, y + hgt)), (dx, y))
            img = out
        img = _zoom(img, 1 + 0.06 * q)
    elif tipo == "destello":
        img = _zoom(img, 1 + 0.22 * q)
    else:                                                               # zoom
        img = _zoom(img, 1 + 0.18 * q)
    pico = {"destello": 0.95, "zoom": 0.55, "sacudida": 0.35, "glitch": 0.0}.get(tipo, 0.25)
    fl = max(0.0, pico * (1 - lt / 0.2))
    if fl > 0:
        img = Image.blend(img, Image.new("RGBA", (W, H), (255, 255, 255, 255)), fl)
    return img

def bpm(semilla):
    """Mismo tempo que musica.py, para que los 'pulsos' de los clips caigan en el ritmo."""
    return {0: 128, 1: 96, 2: 122, 3: 104}[semilla % 4] + (semilla % 3) * 2

def pulso(img, t):
    """Golpe de zoom suave en cada tiempo de la música (da energía a los clips reales)."""
    beat = 60 / bpm(SEMILLA); fase = (t % beat) / beat
    fuerza = 0.045 if int(t / beat) % 2 == 0 else 0.025
    z = 1 + fuerza * max(0.0, 1 - fase / 0.35) ** 2
    return _zoom(img, z) if z > 1.001 else img

def tipo_transicion(idx, esc):
    if esc.get("transicion"): return esc["transicion"]
    if esc["tipo"] == "clip": return TRANS_CLIPS[(idx + SEMILLA) % len(TRANS_CLIPS)]
    return "zoom" if idx % 2 else "barrido"

def whoosh(wav, tiempos):
    """Mezcla un 'whoosh' (y un golpe grave en destello/sacudida/zoom) en cada transición de la música."""
    import numpy as np
    from scipy.io import wavfile
    from scipy.signal import butter, lfilter
    sr, m = wavfile.read(wav); m = m.astype(np.float32); esc = 32767.0 if m.dtype != np.float32 else 1.0
    if np.abs(m).max() > 2: esc = 32767.0
    else: esc = 1.0
    rng = np.random.default_rng(5)
    for t, tipo in tiempos:
        n = int(0.42 * sr); x = rng.standard_normal(n)
        env = np.concatenate([np.linspace(0, 1, int(n * 0.6)) ** 2, np.linspace(1, 0, n - int(n * 0.6)) ** 1.5])
        b, a = butter(2, [900 / (sr / 2), 5200 / (sr / 2)], "band"); w = lfilter(b, a, x) * env * 0.33
        if tipo in ("destello", "sacudida", "zoom"):
            tt = np.arange(int(0.25 * sr)) / sr
            golpe = np.sin(2 * np.pi * (90 - 50 * tt / 0.25) * tt) * np.exp(-tt * 14) * 0.55
            w2 = np.zeros(n); i0 = int(n * 0.6); w2[i0:i0 + len(golpe)] = golpe[: n - i0]; w = w + w2
        i = int((t - 0.42 * 0.6) * sr)
        if i < 0: w = w[-i:]; i = 0
        j = min(len(m), i + len(w)); w = w[: j - i] * esc
        if m.ndim == 2: m[i:j] += w[:, None]
        else: m[i:j] += w
    m = np.clip(m, -esc, esc)
    wavfile.write(wav, sr, m.astype(np.int16) if esc > 2 else m.astype(np.float32))

def build(guion):
    escenas, t = [], 0.0
    lista = list(guion["escenas"])
    if guion.get("cierre", True) and not any(e["tipo"] == "cierre" for e in lista):
        variantes = ["circulo", "barrido", "persiana"]           # se rotan según la música para no repetir
        lista.append({"tipo": "cierre", "dur": 2.6, "transicion": "ninguna",
                      "variante": variantes[int(guion.get("musica_semilla", 0)) % 3]})
    global SEMILLA; SEMILLA = int(guion.get("musica_semilla", 0))
    rot = guion.get("fondos") or TIPOS_FONDO
    ini = SEMILLA % len(rot); previo = None
    for i, e in enumerate(lista):
        tipo = e.get("estilo_fondo") or rot[(ini + i) % len(rot)]
        if tipo == previo and not e.get("estilo_fondo"): tipo = rot[(ini + i + 1) % len(rot)]
        TIPO_FONDO_ESCENA[i] = tipo; previo = tipo
        escenas.append((t, t + float(e["dur"]), e)); t += float(e["dur"])
    return escenas, t

def frame(escenas, total, t):
    idx, t_esc = 0, t
    for i, (s, e_, _) in enumerate(escenas):
        if s <= t: idx, t_esc = i, t - s
    s0, e0, esc = escenas[idx]
    es_clip = esc["tipo"] == "clip"
    img = fondo_clip(idx, esc, t_esc) if es_clip else fondo(t, idx, t_esc)
    if es_clip and esc.get("pulso", True) and t_esc > TRANS_DUR:
        img = pulso(img, t)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if not es_clip:
        d = ImageDraw.Draw(L); off = (t * 120) % 400
        for k in range(-2, 7):
            x0 = k * 400 + off - 600
            d.polygon([(x0, 0), (x0 + 60, 0), (x0 + 760, H), (x0 + 700, H)], fill=(255, 255, 255, 10))
    a = 1.0 if (t <= e0 - 0.3 or e0 >= total) else (e0 - t) / 0.3
    if es_clip and tipo_transicion(idx, esc) != "ninguna":
        a = 1.0                                   # en clips el corte lo marca la transición, sin fundido
    es_cierre = esc["tipo"] == "cierre"
    if not es_clip and not es_cierre:
        a_in = ease(t_esc / 0.35) if idx > 0 else 1.0
        escenario(L, esc.get("fondo") or ORDEN_ESCENARIOS[idx % len(ORDEN_ESCENARIOS)], t, a * a_in)
    if es_cierre:
        TIPOS["cierre"](L, esc, t_esc, 1.0)
    else:
        TIPOS[esc["tipo"]](L, esc, t_esc, a)
        progress(L, t, total)
        marca_pie(L)
    img.alpha_composite(L)
    if idx > 0:   # si el guion no la define: clips rotan TRANS_CLIPS; las demás alternan zoom y barrido
        img = transicion(img, t_esc, tipo_transicion(idx, esc))
    return img.convert("RGB")

def main():
    guion = json.load(open(sys.argv[1], encoding="utf-8")); out = sys.argv[2]
    global ESTILO_CAJA, LOGO_ESTILO
    ESTILO_CAJA = guion.get("estilo_caja", ESTILO_CAJA); LOGO_ESTILO = guion.get("logo", LOGO_ESTILO)
    global LOGO_OPACIDAD; LOGO_OPACIDAD = float(guion.get("logo_opacidad", LOGO_OPACIDAD))
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
    if guion.get("whoosh", True):
        whoosh(wav, [(s0, tipo_transicion(i, e)) for i, (s0, _, e) in enumerate(escenas)
                     if i > 0 and tipo_transicion(i, e) != "ninguna" and e["tipo"] != "cierre"])
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
