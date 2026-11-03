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
  "camara": movimiento de cámara (Ken Burns) en fotos/clips: "lento" (defecto), "acercar", "alejar", "paneo_der",
  "paneo_izq", "subir", "bajar", "diagonal", o lista [zoom0, zoom1, cx0, cy0, cx1, cy1].
  "estilo": "polaroid" muestra la foto como tarjeta inclinada con borde blanco sobre fondo desenfocado
  (disimula fotos de baja calidad); opcionales "pie" (texto en el borde) y "angulo".
Cortos animados: {"tipo": "anim", "escena": "hola|vuelo|aduana|llegada|fila|lupa|sonrisa|rayosx|sello|duo|aplastado|copito", "dur": 2.6, "texto": ..., "resaltado": ...}
  con "Paqui", la cajita animada (generador/personajes.py). "aduana" y "rayosx" admiten "cambio" + "texto_despues"; "sello" admite "sello" (texto del sello).
  Diálogo hablado en "anim": "voces": [[segundo, "material/voces/x.mp3"], ...] mezcla cada voz (la música baja sola) y
  "lineas": [[desde, hasta, "paqui|amigo", "frase"], ...] pone la frase arriba y mueve la boca de quien habla.
  "copito" (Paqui y Copito, muñeco robot navideño en su caja de regalo; modo sorpresa con "sale" | charla | baile).
  "subt_cortos": true en una escena anim con "lineas" muestra subtítulos de 1 a 3 palabras (palabra clave entre *asteriscos* sale en amarillo).
  "aplastado" (Paqui llega aplastado; modo llega | pizza | charla | boing con "pop" | feliz).
  "duo" (Paqui y su amigo) admite "modo": grito (el amigo entra gritando, para ganchos) | charla | verde (canal verde, Paqui se ríe) | rojo (canal rojo, el amigo llora) | abrazo.
  Usa "estilo_fondo" para el fondo. Ejemplo: guiones/muestra_animado-paqui.json.
  "show" es un escenario libre para sketches hablados: actores (paqui, amigo, maleta o un emoji), utilería
  (emoji, texto, cartel, burbuja, comentario, balanza, medidas, cajas_caen, fuegos, bodega, ruta, escritorio...),
  "sacudir" y "sfx" (efectos sintetizados, sin derechos). Todo se arma desde el JSON: ver generador/show.py y
  guiones/2026-11-03_paqui-*.json. Portadas "PAQUI #N": generador/portada.py con portadas/*.json.
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

# Movimientos de cámara para fotos y clips ("camara" en la escena). (zoom inicial, zoom final, centro x/y inicial, final)
CAMARAS = {
    "lento":      (1.00, 1.06, .5, .5, .5, .5),     # el de siempre: acercamiento muy suave
    "acercar":    (1.00, 1.28, .5, .5, .5, .45),
    "alejar":     (1.30, 1.00, .5, .42, .5, .5),
    "paneo_der":  (1.28, 1.28, .2, .5, .8, .5),     # recorre la foto de izquierda a derecha
    "paneo_izq":  (1.28, 1.28, .8, .5, .2, .5),
    "subir":      (1.25, 1.25, .5, .9, .5, .1),     # recorre de abajo hacia arriba (pilas de cajas)
    "bajar":      (1.25, 1.25, .5, .1, .5, .9),
    "diagonal":   (1.05, 1.32, .3, .75, .65, .35),
}

def _suave(x):
    x = max(0.0, min(1.0, x)); return 0.5 - 0.5 * math.cos(math.pi * x)

def camara(img, e, lt):
    """Zoom y paneo durante la escena. "camara": nombre de CAMARAS o lista propia [z0, z1, cx0, cy0, cx1, cy1]."""
    c = e.get("camara", "lento")
    z0, z1, x0, y0, x1, y1 = CAMARAS[c] if isinstance(c, str) else c
    k = _suave(lt / max(float(e["dur"]), 0.1))
    z = z0 + (z1 - z0) * k
    cw, ch = W / z, H / z
    cx = min(max((x0 + (x1 - x0) * k) * W, cw / 2), W - cw / 2)
    cy = min(max((y0 + (y1 - y0) * k) * H, ch / 2), H - ch / 2)
    return img.transform((W, H), Image.EXTENT, (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2), Image.BICUBIC)

def polaroid(img, e, lt):
    """La foto como tarjeta tipo Polaroid inclinada sobre un fondo desenfocado de la misma foto.
    Disimula fotos de baja calidad. Opcionales: "pie" (texto escrito en el borde blanco), "angulo" (grados)."""
    fondo_b = img.resize((W // 8, H // 8), Image.BILINEAR).filter(ImageFilter.GaussianBlur(4)).resize((W, H), Image.BILINEAR)
    fondo_b = Image.blend(fondo_b, Image.new("RGB", (W, H), NAVY2), 0.45).convert("RGBA")
    fw, fh, borde, pie = 780, 940, 30, 120
    foto = img.resize((fw, int(fw * H / W)), Image.BICUBIC)
    foto = foto.crop((0, (foto.height - fh) // 2, fw, (foto.height - fh) // 2 + fh))
    card = Image.new("RGBA", (fw + 2 * borde, fh + borde + pie), (255, 255, 255, 255))
    card.paste(foto, (borde, borde))
    if e.get("pie"):
        f, lines, sz = fit(limpiar(e["pie"]), "Black", 54, fw, 1)
        ImageDraw.Draw(card).text((card.width / 2, fh + borde + pie / 2), lines[0] if lines else "", font=f, fill=NAVY, anchor="mm")
    p = ease(lt / 0.45)
    ang = e.get("angulo", -5) + 14 * (1 - p)
    esc = 0.75 + 0.25 * p
    card = card.resize((int(card.width * esc), int(card.height * esc)), Image.BICUBIC)
    sombra = Image.new("RGBA", (card.width + 80, card.height + 80), (0, 0, 0, 0))
    ImageDraw.Draw(sombra).rectangle([40, 40, 40 + card.width, 40 + card.height], fill=(0, 0, 0, 150))
    sombra = sombra.filter(ImageFilter.GaussianBlur(18)).rotate(ang, Image.BICUBIC, expand=True)
    card = card.rotate(ang, Image.BICUBIC, expand=True)
    cy = 1060 + 8 * math.sin(lt * 2.2)
    fondo_b.alpha_composite(sombra, (int(W / 2 - sombra.width / 2 + 14), int(cy - sombra.height / 2 + 22)))
    fondo_b.alpha_composite(card, (int(W / 2 - card.width / 2), int(cy - card.height / 2)))
    return fondo_b.convert("RGB")

def fondo_clip(i, e, lt):
    if i not in _clips:
        _clips[i] = Clip(e["archivo"], e.get("inicio", 0), e["dur"], e.get("recorte"))
    img = _clips[i].cuadro_suelto(lt) if MODO_PREVIA else _clips[i].siguiente()
    img = camara(img, e, lt)                                          # zoom / paneo (efecto Ken Burns)
    if e.get("estilo") == "polaroid":
        img = polaroid(img, e, lt)
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

# ---------- cortos animados: escena {"tipo": "anim", "escena": "hola|vuelo|aduana|llegada", "texto": ...} ----------
# Protagonista: "Paqui", la cajita de Jetport (personajes.py). Texto igual que en las escenas "clip"
# ("texto", "resaltado", "posicion"); "texto_despues" + "cambio" (segundos) cambian el texto a mitad de escena.
import random as _random
import personajes as pj

_SUELO = 1340

def _nube(L, x, y, s, alfa):
    capa = Image.new("RGBA", (int(260 * s), int(130 * s)), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    for dx, dy, r in [(60, 80, 45), (110, 55, 58), (170, 75, 46), (125, 92, 40)]:
        d.ellipse([(dx - r) * s, (dy - r) * s, (dx + r) * s, (dy + r) * s], fill=(255, 255, 255, int(255 * alfa)))
    L.alpha_composite(capa, (int(x), int(y)))

def _impacto(L, cx, cy, k):
    """Rayitas de golpe al aterrizar (k de 0 a 1)."""
    if not 0 < k < 1: return
    d = ImageDraw.Draw(L)
    for i in range(7):
        ang = math.pi + math.pi * i / 6
        r0, r1 = 230 + 120 * k, 300 + 170 * k
        d.line([(cx + r0 * math.cos(ang), cy + 0.5 * r0 * math.sin(ang)), (cx + r1 * math.cos(ang), cy + 0.5 * r1 * math.sin(ang))],
               fill=(255, 255, 255, int(255 * (1 - k))), width=12)

def _a_hola(L, e, lt):
    s, cx, T = 400, W / 2, 0.5
    if lt < T:
        y = _SUELO - (1 - (lt / T) ** 2) * 1600; sx, sy, expr, br = 0.9, 1.12, "sorpresa", (150, 150)
    else:
        q = lt - T; sq = math.exp(-q * 6) * math.cos(q * 26)
        y = _SUELO; sx, sy = 1 + 0.2 * sq, 1 - 0.2 * sq; expr = "feliz"
        br = (25, 140 + 28 * math.sin(lt * 14)) if lt > 0.9 else (60, 60)
    pj.sombra(L, cx, _SUELO - 8, s * 1.4 * (0.4 + 0.6 * min(1, lt / T)))
    _impacto(L, cx, _SUELO - 60, (lt - T) / 0.4)
    pj.pegar(L, pj.caja(s, lt, expr, br, mirar=(0.3, 0.3)), cx, y, sx, sy)

_AVION = {}
def _a_vuelo(L, e, lt):
    rnd = _random.Random(4)
    for i in range(7):                                                # nubes de fondo
        x = (rnd.randrange(0, W + 600) - lt * (300 + 120 * (i % 3))) % (W + 600) - 400
        _nube(L, x, rnd.randrange(450, 1700), 0.9 + 0.5 * (i % 3), 0.55)
    d = ImageDraw.Draw(L)
    for i in range(10):                                               # líneas de velocidad
        x = (rnd.randrange(0, W + 800) - lt * 1800) % (W + 800) - 400
        y = rnd.randrange(600, 1600)
        d.line([(x, y), (x + 220, y)], fill=(255, 255, 255, 170), width=6)
    if "av" not in _AVION: _AVION["av"] = pj.avion(940)
    av = _AVION["av"]; sc = 940 / 300
    k = ease(lt / 0.7)
    cx = -520 + (W / 2 + 520) * k; cy = 1210 + 24 * math.sin(lt * 3.2)
    ang = 3 * math.sin(lt * 2.6) + 10 * (1 - k)
    im = av.rotate(ang, Image.BICUBIC, expand=True)
    a_r = math.radians(ang)
    dx, dy = (165 - 155) * sc, (60 - 80) * sc                       # la caja va sentada sobre el fuselaje
    bx = cx + dx * math.cos(a_r) + dy * math.sin(a_r); by = cy - dx * math.sin(a_r) + dy * math.cos(a_r)
    caja = pj.caja(250, lt, "abierta", (160 + 15 * math.sin(lt * 16), 160 + 15 * math.sin(lt * 16 + 2)), mirar=(0.6, 0))
    pj.pegar(L, caja, bx, by + 40, ang=ang)
    L.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))
    for i in range(2):                                                # nubes que pasan por delante
        x = (W + 300 + i * 900) - (lt * 1500) % (W + 1800)
        _nube(L, x, 1500 + i * 120, 1.6, 0.9)

def _lupa(L, lx, ly, r):
    zona = L.crop((int(lx - r / 1.5), int(ly - r / 1.5), int(lx + r / 1.5), int(ly + r / 1.5))).resize((2 * r, 2 * r), Image.BICUBIC)
    mask = Image.new("L", (2 * r, 2 * r), 0); ImageDraw.Draw(mask).ellipse([0, 0, 2 * r, 2 * r], fill=255)
    vidrio = Image.new("RGBA", (2 * r, 2 * r), (200, 235, 255, 70)); vidrio.alpha_composite(zona)
    L.paste(vidrio, (int(lx - r), int(ly - r)), mask)
    d = ImageDraw.Draw(L)
    hx, hy = lx + r * 0.72, ly + r * 0.72
    d.line([(hx, hy), (hx + 150, hy + 150)], fill=NAVY + (255,), width=40)
    d.ellipse([lx - r, ly - r, lx + r, ly + r], outline=NAVY + (255,), width=22)
    d.arc([lx - r * 0.7, ly - r * 0.7, lx + r * 0.7, ly + r * 0.7], 200, 250, fill=(255, 255, 255, 230), width=12)

def _a_aduana(L, e, lt):
    s, c = 400, float(e.get("cambio", 1.7))
    pj.sombra(L, W / 2, _SUELO - 8, s * 1.4)
    if lt < c:
        lx = W / 2 + 230 * math.cos(lt * 3.1); ly = 1080 + 150 * math.sin(lt * 4.6)
        mir = ((lx - W / 2) / 230, (ly - 1080) / 150)
        pj.pegar(L, pj.caja(s, lt, "nervioso", (10, 10), mirar=mir), W / 2 + 7 * math.sin(lt * 45), _SUELO)
        _lupa(L, lx, ly, 150)
    else:
        q = lt - c
        y = _SUELO - 190 * math.sin(math.pi * min(1, q / 0.55))
        pj.pegar(L, pj.caja(s, lt, "feliz", (160, 160)), W / 2, y)
        p = min(1, q / 0.35); r = 120 * (p * (1 + 0.25 * math.sin(p * math.pi)))
        if r > 1:                                                     # sello verde con check
            d = ImageDraw.Draw(L); x0, y0 = 820, 820
            d.ellipse([x0 - r, y0 - r, x0 + r, y0 + r], fill=(34, 180, 90, 255), outline=(255, 255, 255, 255), width=12)
            d.line([(x0 - r * .45, y0), (x0 - r * .1, y0 + r * .35), (x0 + r * .5, y0 - r * .35)], fill=(255, 255, 255, 255), width=int(r * .2), joint="curve")

def _a_llegada(L, e, lt):
    s = 380
    rnd = _random.Random(9); d = ImageDraw.Draw(L)
    colores = [ORANGE, (255, 214, 64), (80, 200, 255), (236, 72, 153), (255, 255, 255), (60, 220, 120)]
    for i in range(70):                                               # explosión de confeti
        ang = rnd.uniform(-math.pi * 0.95, -math.pi * 0.05); v = rnd.uniform(900, 1900)
        x = W / 2 + math.cos(ang) * v * lt * 0.8; y = 1100 + math.sin(ang) * v * lt + 1300 * lt * lt
        if y > H: continue
        a = lt * 9 + i; w2 = 16
        d.polygon([(x + w2 * math.cos(a), y + w2 * math.sin(a)), (x - w2 * math.sin(a), y + w2 * 0.5 * math.cos(a)),
                   (x - w2 * math.cos(a), y - w2 * math.sin(a)), (x + w2 * math.sin(a), y - w2 * 0.5 * math.cos(a))], fill=colores[i % 6])
    for i in range(6):                                                # corazones que suben
        k = (lt * 0.7 + i / 6) % 1
        pj._corazon(d, W / 2 + (i - 2.5) * 140 + 30 * math.sin(lt * 4 + i), 1300 - k * 750, 34 * (1 - k * 0.5), (235, 40, 80))
    ph = (lt / 0.5) % 1
    y = _SUELO - 150 * math.sin(math.pi * ph)
    sq = 0.14 * max(0, 1 - min(ph, 1 - ph) / 0.12)
    pj.sombra(L, W / 2, _SUELO - 8, s * 1.4 * (1 - 0.3 * math.sin(math.pi * ph)))
    pj.pegar(L, pj.caja(s, lt, "enamorado", (150 + 20 * math.sin(lt * 15), 150 - 20 * math.sin(lt * 15)), piernas=lt * 12),
             W / 2, y, 1 + sq, 1 - sq)

ANIMACIONES = {"hola": _a_hola, "vuelo": _a_vuelo, "aduana": _a_aduana, "llegada": _a_llegada}

# --- escenas de humor "Paqui en aduana" (fila, lupa, sonrisa, rayosx, sello) ---
def _nota(d, x, y, a=255):
    d.ellipse([x - 16, y - 11, x + 16, y + 11], fill=(255, 255, 255, a))
    d.line([(x + 13, y), (x + 13, y - 60)], fill=(255, 255, 255, a), width=7)
    d.line([(x + 13, y - 60), (x + 36, y - 44)], fill=(255, 255, 255, a), width=7)

def _a_fila(L, e, lt):
    """Paqui entra caminando, silbando y mirando a los lados ("aquí no pasa nada")."""
    s = 380; k = ease(lt / 1.1)
    cx = -300 + (W / 2 + 300) * k
    andando = lt < 1.1
    y = _SUELO - (14 * abs(math.sin(lt * 11)) if andando else 0)
    mir = (-1 if math.sin(lt * 2.6) < 0 else 1, -0.2)
    d = ImageDraw.Draw(L)
    for i in range(3):                                                # notitas del silbido
        q = (lt * 0.9 + i / 3) % 1
        _nota(d, cx + 230 + 80 * q + 25 * math.sin(lt * 5 + i), 1000 - 330 * q, int(255 * (1 - q)))
    pj.sombra(L, cx, _SUELO - 8, s * 1.4)
    pj.pegar(L, pj.caja(s, lt, "silbando", (8 + 6 * math.sin(lt * 11), 8 - 6 * math.sin(lt * 11)), mirar=mir,
                        parpadeo=False, piernas=lt * 11 if andando else 0), cx, y, ang=4 * math.sin(lt * 11) if andando else 0)

def _a_lupa(L, e, lt):
    """Llega una lupa gigante y Paqui entra en pánico (tiembla, suda, grita)."""
    s = 420
    pj.sombra(L, W / 2, _SUELO - 8, s * 1.4)
    amp = 4 + 10 * min(1, lt / 0.6)
    pj.pegar(L, pj.caja(s, lt, "panico", (150 + 12 * math.sin(lt * 40), 150 - 12 * math.sin(lt * 40)), parpadeo=False),
             W / 2 + amp * math.sin(lt * 55), _SUELO + 3 * math.sin(lt * 47), 1.0 + 0.03 * math.sin(lt * 30), 1.0)
    k = ease(lt / 0.7)
    _lupa(L, W + 300 - (W / 2 + 230) * k + 20 * math.sin(lt * 3), 1010 + 30 * math.sin(lt * 2.4), int(150 + 40 * k))

def _a_sonrisa(L, e, lt):
    """Primer plano: sonrisa forzada, tic en el ojo, sudor... y grillos."""
    s = 560 + 40 * ease(lt / 1.5)
    pj.pegar(L, pj.caja(int(s), lt, "forzada", (5, 5), parpadeo=False), W / 2, _SUELO + 60)
    if lt > 0.7:
        a = min(1, (lt - 0.7) / 0.3)
        for i, (x, y) in enumerate([(230, 1500), (850, 1470)]):
            dy = 6 * math.sin(lt * 20 + i)
            texto_borde(L, (x, y + dy), "cri cri...", font("Bold", 50), (220, 230, 240), a * 0.95, borde=5)

def _rayosx(L, x0, x1, s, cx, base):
    """Dibuja la vista de rayos X (contorno de la caja y lo que hay dentro) entre x0 y x1."""
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    u = s / 100; ox = cx - 95 * u; oy = base - 175 * u
    P = lambda x, y: (ox + x * u, oy + y * u)
    d.rectangle([0, 0, W, H], fill=(8, 30, 40, 235))
    for gx in range(0, W, 60): d.line([(gx, 0), (gx, H)], fill=(60, 255, 200, 40), width=2)
    for gy in range(0, H, 60): d.line([(0, gy), (W, gy)], fill=(60, 255, 200, 40), width=2)
    c = (120, 255, 230, 255)
    d.rounded_rectangle([*P(40, 50), *P(140, 136)], int(4 * u), outline=c, width=6)
    d.polygon([P(40, 50), P(58, 34), P(158, 34), P(140, 50)], outline=c, width=5)
    d.line([P(140, 136), P(158, 120), P(158, 34)], fill=c, width=5)
    blanco = (230, 255, 250, 255)
    d.polygon([P(48, 120), P(52, 100), P(66, 100), P(72, 110), P(92, 114), P(94, 124), P(48, 124)], fill=blanco)   # zapatilla
    d.polygon([P(100, 62), P(112, 58), P(118, 62), P(124, 58), P(136, 62), P(132, 72), P(127, 70), P(127, 92), P(109, 92), P(109, 70), P(104, 72)], fill=blanco)  # polo
    d.arc([*P(56, 58), *P(86, 88)], 180, 360, fill=blanco, width=int(4 * u))                                     # audífonos
    d.rounded_rectangle([*P(52, 72), *P(60, 88)], int(2 * u), fill=blanco); d.rounded_rectangle([*P(82, 72), *P(90, 88)], int(2 * u), fill=blanco)
    d.rectangle([*P(102, 100), *P(126, 124)], outline=blanco, width=5)                                           # regalo con lazo
    d.line([P(114, 100), P(114, 124)], fill=blanco, width=5)
    d.ellipse([*P(106, 92), *P(114, 100)], outline=blanco, width=4); d.ellipse([*P(114, 92), *P(122, 100)], outline=blanco, width=4)
    mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).rectangle([x0, 380, x1, 1560], fill=255)
    L.paste(capa, (0, 0), mask)
    dd = ImageDraw.Draw(L)
    dd.rectangle([x0 - 8, 380, x0 + 8, 1560], fill=(60, 255, 200, 255)); dd.rectangle([x1 - 8, 380, x1 + 8, 1560], fill=(60, 255, 200, 255))

def _a_rayosx(L, e, lt):
    """Escáner de rayos X: se ve lo que lleva Paqui y le da vergüenza."""
    s = 420; c = float(e.get("cambio", 1.7))
    expr = "panico" if lt < c else "verguenza"
    pj.sombra(L, W / 2, _SUELO - 8, s * 1.4)
    pj.pegar(L, pj.caja(s, lt, expr, (10, 10) if lt < c else (150, 150), parpadeo=False), W / 2 + (3 * math.sin(lt * 50) if lt < c else 0), _SUELO)
    k = ease(min(1, lt / 1.4))
    xc = -150 + (W / 2 + 150) * k
    if lt < c + 0.1:
        _rayosx(L, xc - 330, xc + 330, s, W / 2, _SUELO)

def _a_sello(L, e, lt):
    """Sello gigante de APROBADO que cae de golpe; Paqui se relaja y baila."""
    s = 330; rnd = _random.Random(3); d = ImageDraw.Draw(L)
    if lt > 0.35:
        colores = [ORANGE, (255, 214, 64), (80, 200, 255), (236, 72, 153), (255, 255, 255), (60, 220, 120)]
        q = lt - 0.35
        for i in range(60):
            ang = rnd.uniform(-math.pi * 0.95, -math.pi * 0.05); v = rnd.uniform(800, 1800)
            x = W / 2 + math.cos(ang) * v * q * 0.8; y = 1150 + math.sin(ang) * v * q + 1300 * q * q
            if y < H: d.rectangle([x - 10, y - 6, x + 10, y + 6], fill=colores[i % 6])
    baile = lt > 0.9
    expr = "alivio" if lt < 0.9 else "feliz"
    hop = 60 * abs(math.sin(lt * 8)) if baile else 0
    br = (150 + 30 * math.sin(lt * 8), 30 + 30 * math.sin(lt * 8)) if baile else (40, 40)
    pj.sombra(L, W / 2, _SUELO - 8, s * 1.4)
    pj.pegar(L, pj.caja(s, lt, expr, br, piernas=lt * 16 if baile else 0), W / 2, _SUELO - hop, ang=10 * math.sin(lt * 8) if baile else 0)
    p = min(1, lt / 0.22)                                              # el sello cae de 3x a 1x
    esc = 3 - 2 * p if p < 1 else 1 + 0.06 * math.exp(-(lt - 0.22) * 10) * math.cos((lt - 0.22) * 40)
    st = Image.new("RGBA", (760, 230), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
    verde = (34, 170, 80, 240)
    sd.rounded_rectangle([8, 8, 752, 222], 30, outline=verde, width=16)
    sd.text((380, 117), e.get("sello", "APROBADO"), font=font("Black", 128), fill=verde, anchor="mm")
    st = st.resize((int(600 * esc), int(182 * esc)), Image.BICUBIC).rotate(-12 if p >= 1 else -12 - 20 * (1 - p), Image.BICUBIC, expand=True)
    if esc < 2.6:
        L.alpha_composite(st, (int(W / 2 - st.width / 2), int(640 - st.height / 2)))

ANIMACIONES.update({"fila": _a_fila, "lupa": _a_lupa, "sonrisa": _a_sonrisa, "rayosx": _a_rayosx, "sello": _a_sello})

# --- "duo": Paqui y su amigo saliendo de aduana (modo charla | verde | rojo | abrazo) ---
def _semaforo(L, lt, activo):
    """Semáforo horizontal de aduana con la luz activa ('verde' o 'rojo') parpadeando y su cartel."""
    d = ImageDraw.Draw(L); cx, cy = W / 2, 760
    d.rounded_rectangle([cx - 230, cy - 80, cx + 230, cy + 80], 40, fill=(30, 34, 48, 255), outline=(255, 255, 255, 255), width=6)
    luces = [("verde", (40, 210, 90)), ("naranja", (255, 150, 30)), ("rojo", (235, 50, 50))]
    on = (lt * 4) % 1 < 0.75
    for i, (nombre, col) in enumerate(luces):
        x = cx - 140 + i * 140
        prendida = nombre == activo and on
        if prendida:
            d.ellipse([x - 78, cy - 78, x + 78, cy + 78], fill=col + (90,))
        d.ellipse([x - 52, cy - 52, x + 52, cy + 52], fill=col + (255,) if prendida else tuple(c // 4 for c in col) + (255,))
    if activo:
        col = dict(luces)[activo]; txt = "CANAL " + activo.upper()
        p = ease(lt / 0.3); f = font("Black", 64); tw = f.getlength(txt)
        y = cy + 125
        d.rounded_rectangle([cx - tw / 2 - 30, y - 50, cx + tw / 2 + 30, y + 50], 26, fill=col + (int(255 * p),))
        d.text((cx, y), txt, font=f, fill=(255, 255, 255, int(255 * p)), anchor="mm")

def _ja(L, x, y, lt, i):
    q = (lt * 1.6 + i / 3) % 1
    texto_borde(L, (x + 30 * math.sin(i * 2 + lt * 3), y - 200 * q), "JA", font("Black", int(70 + 30 * (1 - q))), (255, 230, 80), 1 - q, borde=7)

def _a_duo(L, e, lt):
    modo = e.get("modo", "charla")
    s, xp, xa = 290, 300, 790
    SU = _SUELO + 130                                                         # más abajo para dejar sitio al semáforo
    d = ImageDraw.Draw(L)
    if modo in ("verde", "rojo"):
        _semaforo(L, lt, modo)
    elif modo == "charla":
        _semaforo(L, lt, None)
    # expresiones y gestos de cada uno
    ep, ea = "feliz", "feliz"; bp, ba = (20, 20), (20, 20); mp, ma = (1, 0), (-1, 0)
    yp = ya = SU; angp = anga = 0.0; sxp = 1.0
    if modo == "charla":
        bp = (20, 110 + 20 * math.sin(lt * 9)); ep = "abierta" if (lt * 3) % 1 < 0.5 else "feliz"
        ea = "sorpresa" if lt > 1.2 else "feliz"
    elif modo == "verde":
        ep = "risa"; bp = (160, 40 + 15 * math.sin(lt * 20))                  # se ríe agarrándose la panza
        yp = SU - 18 * abs(math.sin(lt * 18)); angp = -8 + 4 * math.sin(lt * 18)
        ea = "nervioso"; ma = (-1, 0)
        for i in range(3): _ja(L, xp + 130, 1180, lt, i)
    elif modo == "rojo":
        ea = "llanto"; ba = (165 + 10 * math.sin(lt * 14), 165 - 10 * math.sin(lt * 14))
        ya = SU - 6 * abs(math.sin(lt * 14))
        ep = "sorpresa"; mp = (1, 0.2)
        r = 60 + 160 * min(1, lt / 2.5)                                          # charco de lágrimas
        d.ellipse([xa - r, SU - 18, xa + r, SU + 22], fill=(110, 190, 255, 230))
    elif modo == "grito":                                                          # gancho: el amigo entra gritando en pánico
        k = ease(lt / 0.5)
        xa = W + 200 - (W + 200 - 790) * k + 22 * math.sin(lt * 40)              # entra corriendo y tiembla
        ya = SU - 60 * abs(math.sin(lt * 11))
        ea = "panico"; ba = (170 + 15 * math.sin(lt * 25), 170 - 15 * math.sin(lt * 25)); anga = 6 * math.sin(lt * 30)
        ep = "sorpresa"; mp = (1, 0); bp = (20, 20)
        yp = SU - 25 * ease(min(1, lt / 0.25)) * (1 if lt < 0.5 else 0)        # Paqui da un saltito del susto
    elif modo == "abrazo":
        k = ease(lt / 0.6)
        xp = 300 + 120 * k; xa = 790 - 110 * k
        ep = "feliz"; bp = (20, 150)
        ea = "llanto" if lt < 0.9 else "feliz"
        if lt > 1.2:                                                               # saltan juntos de alegría
            yp = SU - 90 * abs(math.sin((lt - 1.2) * 7)); ya = SU - 90 * abs(math.sin((lt - 1.2) * 7 + 0.6))
            bp = (160, 160); ba = (160, 160)
        r = max(0, 160 - 200 * lt)
        if r > 2: d.ellipse([xa - r, SU - 18, xa + r, SU + 22], fill=(110, 190, 255, 230))
    for desde, hasta, quien, *_ in e.get("lineas", []):                    # boca que se mueve al hablar
        if desde <= lt < hasta and (lt * 7.5) % 1 < 0.5:
            if quien == "paqui" and ep in ("feliz", "sorpresa", "nervioso"): ep = "abierta"
            if quien == "amigo" and ea in ("feliz", "sorpresa", "nervioso"): ea = "abierta"
    pj.sombra(L, xp, SU - 8, s * 1.4); pj.sombra(L, xa, SU - 8, s * 1.3)
    pj.pegar(L, pj.caja(s, lt, ea, ba, mirar=ma, color="amigo"), xa, ya, 0.92, 1.12, anga)
    pj.pegar(L, pj.caja(s, lt, ep, bp, mirar=mp), xp, yp, sxp, 1.0, angp)

ANIMACIONES["duo"] = _a_duo

# --- "aplastado": Paqui llega aplastado (cae del cielo, ¡PLAF!) y vuelve a su forma con un ¡BOING! ---
def _estrella(d, cx, cy, r, color):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=color, outline=(60, 40, 0, 255))

def _a_aplastado(L, e, lt):
    """modo: llega (cae y se aplasta, ¡PLAF!) | pizza (el amigo se ríe) | charla (aplastado conversando) |
    boing (en "pop" segundos recupera la forma con rebote) | feliz (los dos contentos saltando)."""
    modo = e.get("modo", "charla")
    s, xp, xa = 290, 330, 800
    SU = _SUELO + 60
    d = ImageDraw.Draw(L)
    ep, ea = "nervioso", "sorpresa"; bp, ba = (60, 60), (20, 20); mp, ma = (1, 0), (-1, 0)
    yp = ya = SU; angp = 0.0; sx, sy = 1.5, 0.48; mareo = True
    if modo == "llega":
        caida = 0.38
        if lt < caida:                                                            # cae del cielo
            k = lt / caida
            yp = -200 + (SU + 200) * k * k; sx, sy = 0.9, 1.15; ep = "panico"; mareo = False; bp = (160, 160)
        else:
            q = lt - caida
            rebote = math.exp(-q * 7) * math.cos(q * 30)                          # aplastado que todavía vibra
            sx, sy = 1.5 + 0.18 * rebote, 0.48 - 0.1 * rebote
            ep = "panico" if q < 0.8 else "nervioso"
            if q < 0.9:                                                           # ¡PLAF! + polvo
                a_ = max(0, 1 - q / 0.9); z = 1 + q * 0.6
                texto_borde(L, (W / 2, 640), "¡PLAF!", font("Black", int(190 * z)), (255, 230, 80), a_, borde=12)
                for i in range(8):
                    ang = i * math.pi / 4; r = 120 + 380 * min(1, q / 0.5)
                    rr = 34 * (1 - q / 0.9)
                    if rr > 1: d.ellipse([xp + r * math.cos(ang) - rr, SU - 20 + 0.35 * r * math.sin(ang) - rr,
                                          xp + r * math.cos(ang) + rr, SU - 20 + 0.35 * r * math.sin(ang) + rr], fill=(235, 225, 210, 200))
            ea = "panico" if q > 0.1 else "feliz"; ba = (160, 160) if q > 0.1 else (20, 20)
            ya = SU - 40 * abs(math.sin(min(q, 0.6) * 10)) if q < 0.6 else SU
    elif modo == "pizza":
        ea = "risa"; ba = (160, 40 + 15 * math.sin(lt * 20)); ya = SU - 18 * abs(math.sin(lt * 18))
        for i in range(3): _ja(L, xa - 60, SU - 420, lt, i)
        ep = "forzada"; bp = (150, 20 + 20 * math.sin(lt * 8))
    elif modo == "charla":
        ep = "nervioso"; ea = "nervioso"; bp = (40, 120 + 20 * math.sin(lt * 6))
    elif modo == "boing":
        pop = float(e.get("pop", 2.0))
        ep = "feliz"; ea = "sorpresa"; bp = (40, 120)
        if lt >= pop:
            q = lt - pop
            rebote = math.exp(-q * 5) * math.cos(q * 22)
            sx, sy = 1.0 - 0.35 * rebote, 1.0 + 0.45 * rebote; mareo = False
            yp = SU - 260 * max(0, math.sin(min(q, 0.5) * math.pi / 0.5)) * (1 if q < 0.5 else 0)
            ep = "risa" if q < 1.2 else "feliz"; bp = (160, 160); ea = "sorpresa" if q < 1.5 else "feliz"; ba = (160, 160) if q > 1.5 else (20, 20)
            if q < 1.0:
                texto_borde(L, (W / 2, 640), "¡BOING!", font("Black", int(170 * (1 + q * 0.4))), (120, 255, 140), 1 - q, borde=12)
                for i in range(10):
                    ang = i * math.pi / 5 + q; r = 150 + 420 * q
                    _estrella(d, xp + r * math.cos(ang), yp - 150 + r * math.sin(ang), 26 * (1 - q), (255, 220, 60, int(255 * (1 - q))))
    elif modo == "feliz":
        sx, sy = 1.0, 1.0; mareo = False
        ep = ea = "feliz"; bp = ba = (160, 160)
        yp = SU - 90 * abs(math.sin(lt * 7)); ya = SU - 90 * abs(math.sin(lt * 7 + 0.6))
    for desde, hasta, quien, *_ in e.get("lineas", []):                    # boca que se mueve al hablar
        if desde <= lt < hasta and (lt * 7.5) % 1 < 0.5:
            if quien == "paqui" and ep in ("feliz", "sorpresa", "nervioso", "forzada"): ep = "abierta"
            if quien == "amigo" and ea in ("feliz", "sorpresa", "nervioso"): ea = "abierta"
    pj.sombra(L, xp, SU - 8, s * 1.4 * max(1, sx * 0.8)); pj.sombra(L, xa, SU - 8, s * 1.3)
    pj.pegar(L, pj.caja(s, lt, ea, ba, mirar=ma, color="amigo"), xa, ya, 0.92, 1.12)
    pj.pegar(L, pj.caja(s, lt, ep, bp, mirar=mp), xp, yp, sx, sy, angp)
    if mareo and (modo != "llega" or lt > 0.5):                               # estrellitas de mareo sobre Paqui
        d = ImageDraw.Draw(L)
        for i in range(3):
            ang = lt * 4 + i * 2 * math.pi / 3
            _estrella(d, xp + 150 * math.cos(ang), yp - s * sy - 150 + 26 * math.sin(ang), 30, (255, 220, 60, 255))

ANIMACIONES["aplastado"] = _a_aplastado

# --- subtítulos cortos estilo TikTok: 1 a 3 palabras a la vez, palabra clave entre *asteriscos* en amarillo ---
_COLOR_QUIEN = {"paqui": (255, 170, 60), "amigo": (120, 200, 255), "copito": (140, 255, 170), "clienta": (255, 120, 200), "maleta": (210, 160, 255), "abuelita": (255, 150, 150)}

def _trozos(frase):
    palabras = limpiar(frase).split()
    trozos, act = [], []
    chicas = {"de", "a", "en", "el", "la", "los", "las", "que", "y", "tu", "un", "una", "con", "por",
              "para", "mi", "se", "te", "del", "al", "me", "lo", "le", "o", "es", "su", "no"}
    for w in palabras:
        act.append(w)
        if w[-1:] in ".,!?…:" or w.endswith("*") and w[-2:-1] in ".,!?":
            trozos.append(act); act = []
        elif len(act) == 3:
            if act[-1].strip("*¡¿").lower() in chicas:          # no cortar en "de", "la"...
                trozos.append(act[:-1]); act = act[-1:]
            else:
                trozos.append(act); act = []
    if act: trozos.append(act)
    return trozos

def _subt_corto(L, quien, frase, t, dur, a):
    trozos = _trozos(frase)
    pesos = [sum(len(w.strip("*")) for w in tr) + 3 for tr in trozos]
    total = sum(pesos); acc = 0; idx = len(trozos) - 1; t0 = 0
    for i, pw in enumerate(pesos):
        fin = acc + pw / total * dur
        if t < fin: idx = i; t0 = acc; break
        acc = fin
    else:
        t0 = acc - pesos[-1] / total * dur
    tr = trozos[idx]; k = t - t0
    z = 1 + 0.28 * max(0, 1 - k / 0.14)                                     # entra de golpe
    f = font("Black", int(118 * z))
    while sum(f.getlength(w.strip("*") + " ") for w in tr) > W - 120 and f.size > 60:
        f = font("Black", f.size - 6)
    nombre = {"paqui": "PAQUI", "amigo": "SU AMIGO", "copito": "COPITO", "clienta": "LA CLIENTA", "maleta": "LA MALETA", "abuelita": "LA ABUELITA"}.get(quien, quien.upper())
    texto_borde(L, (W / 2, 300), nombre, font("Black", 50), _COLOR_QUIEN.get(quien, (255, 255, 255)), a, borde=7)
    anchos = [f.getlength(w.strip("*")) for w in tr]; esp = f.getlength(" ")
    x = W / 2 - (sum(anchos) + esp * (len(tr) - 1)) / 2
    for w, aw in zip(tr, anchos):
        clave = w.startswith("*") or w.endswith("*") or w.rstrip(".,!?…").endswith("*")
        texto_borde(L, (x + aw / 2, 420), w.replace("*", ""), f, (255, 214, 64) if clave else WHITE, a, borde=11)
        x += aw + esp

# --- "copito": Paqui y Copito, un muñeco animatrónico navideño (original) que sale de su caja de regalo ---
def _copito_sprite(t, hablando=False, brazos=(30, 30), ojos="normal"):
    S = 2; Wc, Hc = 380 * S, 560 * S
    im = Image.new("RGBA", (Wc, Hc), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    P = lambda x, y: (x * S, y * S)
    C = (45, 45, 70, 255); lw = 5 * S
    cx = 190
    # brazos mecánicos (detrás del cuerpo)
    for lado, ang in ((-1, brazos[0]), (1, brazos[1])):
        x0, y0 = cx + lado * 95, 330
        r = math.radians(ang)
        x1, y1 = x0 + lado * 90 * math.cos(r), y0 - 90 * math.sin(r)
        d.line([P(x0, y0), P(x1, y1)], fill=(150, 160, 175, 255), width=16 * S)
        d.ellipse([*P(x0 - 14, y0 - 14), *P(x0 + 14, y0 + 14)], fill=(120, 130, 150, 255), outline=C, width=3 * S)
        d.ellipse([*P(x1 - 26, y1 - 26), *P(x1 + 26, y1 + 26)], fill=(220, 40, 50, 255), outline=C, width=4 * S)   # guante
    # cuerpo
    d.rounded_rectangle([*P(cx - 100, 270), *P(cx + 100, 480)], 40 * S, fill=(240, 244, 252, 255), outline=C, width=lw)
    for i, col in enumerate([(220, 40, 50), (40, 170, 80), (230, 180, 40)]):
        y = 330 + i * 48
        d.ellipse([*P(cx - 15, y - 15), *P(cx + 15, y + 15)], fill=col + (255,), outline=C, width=3 * S)
    d.rectangle([*P(cx - 100, 455), *P(cx + 100, 480)], fill=(150, 160, 175, 255))     # base metálica
    # bufanda
    d.rounded_rectangle([*P(cx - 110, 250), *P(cx + 110, 290)], 18 * S, fill=(220, 40, 50, 255), outline=C, width=4 * S)
    for i in range(5):
        d.rectangle([*P(cx - 95 + i * 42, 252), *P(cx - 78 + i * 42, 288)], fill=(255, 255, 255, 255))
    d.polygon([P(cx + 50, 285), P(cx + 85, 285), P(cx + 95, 360), P(cx + 60, 360)], fill=(220, 40, 50, 255), outline=C)
    # cabeza
    d.ellipse([*P(cx - 115, 50), *P(cx + 115, 270)], fill=(250, 252, 255, 255), outline=C, width=lw)
    for lado in (-1, 1):                                                       # tornillos
        d.ellipse([*P(cx + lado * 118 - 16, 150), *P(cx + lado * 118 + 16, 182)], fill=(150, 160, 175, 255), outline=C, width=3 * S)
    # gorro navideño genérico
    d.polygon([P(cx - 100, 95), P(cx + 100, 95), P(cx + 150, 0), P(cx + 40, 25)], fill=(220, 40, 50, 255), outline=C)
    d.rounded_rectangle([*P(cx - 112, 80), *P(cx + 112, 112)], 16 * S, fill=(255, 255, 255, 255), outline=C, width=4 * S)
    d.ellipse([*P(cx + 132, -14), *P(cx + 172, 26)], fill=(255, 255, 255, 255), outline=C, width=4 * S)
    # antena con luz que parpadea
    d.line([P(cx - 60, 85), P(cx - 90, 30)], fill=C, width=5 * S)
    luz = (255, 60, 60, 255) if (t * 3) % 1 < 0.5 else (120, 30, 30, 255)
    d.ellipse([*P(cx - 104, 16), *P(cx - 76, 44)], fill=luz, outline=C, width=3 * S)
    # ojos LED
    parp = (t % 3.1) < 0.12
    for lado in (-1, 1):
        ex = cx + lado * 48
        if ojos == "feliz":
            d.arc([*P(ex - 26, 140), *P(ex + 26, 190)], 200, 340, fill=(40, 200, 255, 255), width=9 * S)
        elif parp:
            d.rectangle([*P(ex - 26, 163), *P(ex + 26, 170)], fill=(40, 200, 255, 255))
        else:
            d.rounded_rectangle([*P(ex - 24, 140), *P(ex + 24, 190)], 12 * S, fill=(40, 200, 255, 255), outline=C, width=3 * S)
            d.rounded_rectangle([*P(ex - 10, 148), *P(ex + 2, 164)], 5 * S, fill=(220, 250, 255, 255))
    for lado in (-1, 1):                                                       # cachetes
        d.ellipse([*P(cx + lado * 78 - 20, 196), *P(cx + lado * 78 + 20, 216)], fill=(255, 170, 180, 200))
    # boca de rejilla (mandíbula animatrónica)
    ab = 34 if hablando and (t * 8) % 1 < 0.5 else 10
    d.rounded_rectangle([*P(cx - 48, 205), *P(cx + 48, 205 + ab)], 8 * S, fill=(50, 40, 60, 255), outline=C, width=3 * S)
    for i in range(1, 4):
        d.line([P(cx - 48 + i * 24, 205), P(cx - 48 + i * 24, 205 + ab)], fill=(200, 200, 210, 255), width=2 * S)
    return im.resize((Wc // S, Hc // S), Image.LANCZOS)

def _caja_regalo(L, cx, base, tapa_dy=0.0, tapa_ang=0.0, tapa=True, solo="todo"):
    d = ImageDraw.Draw(L); C = (45, 45, 70, 255)
    if solo in ("todo", "frente"):
        d.rectangle([cx - 175, base - 210, cx + 175, base], fill=(205, 35, 45, 255), outline=C, width=6)
        d.rectangle([cx - 22, base - 210, cx + 22, base], fill=(40, 170, 80, 255))
        d.rectangle([cx + 70, base - 80, cx + 150, base - 30], fill=(255, 255, 255, 255))     # etiqueta sin datos
        d.polygon([(cx + 92, base - 45), (cx + 130, base - 62), (cx + 112, base - 40)], fill=(255, 130, 30, 255))
    if tapa and solo in ("todo", "tapa"):
        capa = Image.new("RGBA", (420, 200), (0, 0, 0, 0)); dc = ImageDraw.Draw(capa)
        dc.rectangle([10, 100, 410, 160], fill=(225, 45, 55, 255), outline=C, width=6)
        dc.rectangle([185, 100, 235, 160], fill=(40, 170, 80, 255))
        dc.ellipse([130, 40, 210, 110], fill=(40, 170, 80, 255), outline=C, width=5)          # lazo
        dc.ellipse([210, 40, 290, 110], fill=(40, 170, 80, 255), outline=C, width=5)
        if abs(tapa_ang) > 0.5: capa = capa.rotate(tapa_ang, Image.BICUBIC, expand=True)
        L.alpha_composite(capa, (int(cx - capa.width / 2), int(base - 210 - 130 - tapa_dy - (capa.height - 200) / 2)))

def _nieve(L, lt):
    d = ImageDraw.Draw(L); rnd = _random.Random(7)
    for i in range(70):
        x0 = rnd.uniform(0, W); v = rnd.uniform(60, 160); r = rnd.uniform(4, 11); fase = rnd.uniform(0, H)
        y = (fase + lt * v) % (H + 40) - 20; x = x0 + 25 * math.sin(lt * 1.3 + i)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 190))

def _a_copito(L, e, lt):
    """modo: sorpresa (la caja tiembla, sale Copito de golpe y Paqui se asusta) | charla | baile."""
    modo = e.get("modo", "charla")
    s, xp, xc = 270, 270, 760
    SU = _SUELO + 120
    _nieve(L, lt)
    habla_c = habla_p = False
    for desde, hasta, quien, *_ in e.get("lineas", []):
        if desde <= lt < hasta:
            if quien == "copito": habla_c = True
            if quien == "paqui": habla_p = True
    ep = "feliz"; bp = (20, 20); yp = SU; mp = (1, 0)
    brazos = (20, 20); ojos = "normal"; alto = 1.0; inclina = 0.0; dx = 0.0
    tq = math.floor(lt * 6) / 6                                                # movimiento "a saltitos" de animatrónico
    tapa = True; tapa_dy = 0.0; tapa_ang = 0.0
    if modo == "sorpresa":
        sale = float(e.get("sale", 0.55))
        if lt < sale:                                                          # la caja tiembla
            dx = 14 * math.sin(lt * 70); alto = 0.0; ep = "sorpresa"
            texto_borde(L, (xc + 150, SU - 330 - 20 * math.sin(lt * 20)), "?", font("Black", 120), (255, 230, 80), 1, borde=9)
        else:
            q = lt - sale
            alto = min(1.0, 1 - math.exp(-q * 9) * math.cos(q * 26))          # resorte con rebote
            tapa_dy = 900 * q + 40; tapa_ang = 260 * q
            tapa = tapa_dy < 1400
            brazos = (150, 150) if q < 1.5 else (20 + 60 * (tq * 3 % 2), 20)
            ep = "panico" if q < 1.6 else "nervioso"; bp = (160, 160) if q < 1.6 else (40, 40)
            yp = SU - 70 * max(0, math.sin(min(q, 0.45) / 0.45 * math.pi)) if q < 0.45 else SU
            mp = (1, -0.3)
            if q < 0.8:
                texto_borde(L, (W / 2, 700), "¡POP!", font("Black", int(200 * (1 + q * 0.5))), (255, 230, 80), 1 - q / 0.8, borde=12)
                d = ImageDraw.Draw(L)
                for i in range(14):
                    ang = i * math.pi / 7; r = 120 + 520 * q
                    _estrella(d, xc + r * math.cos(ang), SU - 330 + r * math.sin(ang) * 0.8, 24 * (1 - q / 0.8), (255, 220, 60, 255))
    elif modo == "charla":
        tapa = False
        inclina = 8 * math.sin(tq * 2.2); brazos = (20 + 40 * (math.floor(lt * 2) % 2), 25)
        ep = "feliz"; bp = (20, 90 + 20 * math.sin(lt * 6))
    elif modo == "baile":
        tapa = False; ojos = "feliz"
        paso = math.floor(lt * 4) % 2
        brazos = (150, 30) if paso else (30, 150); inclina = 12 if paso else -12
        ep = "risa" if (lt % 2) < 1 else "feliz"; bp = (160, 40) if paso else (40, 160)
        yp = SU - 70 * abs(math.sin(lt * 7.5))
        d = ImageDraw.Draw(L)
        for i in range(9):                                                     # lucecitas de colores
            col = [(255, 70, 70), (70, 220, 110), (255, 210, 60), (90, 170, 255)][(i + int(lt * 4)) % 4]
            x = 80 + i * 115; y = 560 + 30 * math.sin(i * 0.9)
            d.ellipse([x - 20, y - 20, x + 20, y + 20], fill=col + (255,))
    if habla_p and ep in ("feliz", "sorpresa", "nervioso") and (lt * 7.5) % 1 < 0.5: ep = "abierta"
    # caja + Copito (sale desde dentro de la caja)
    if alto > 0.02:
        spr = _copito_sprite(lt, habla_c, brazos, ojos).crop((0, 0, 380, 482))    # sin el espacio vacío de abajo
        tope = SU - 195                                                          # borde de la caja
        y_b = tope + 482 * (1 - alto)                                            # base del robot (sube con el resorte)
        vis = int(482 - max(0, y_b - tope))
        if vis > 4:
            spr = spr.crop((0, 0, 380, vis))
            if abs(inclina) > 0.3:
                ancho0 = spr.width; spr = spr.rotate(inclina, Image.BICUBIC, expand=True)
            L.alpha_composite(spr, (int(xc + dx - spr.width / 2), int(min(y_b, tope) - spr.height + 10)))
    pj.sombra(L, xc, SU - 6, 380); pj.sombra(L, xp, SU - 8, s * 1.4)
    _caja_regalo(L, xc + dx, SU, solo="frente")
    if tapa: _caja_regalo(L, xc + dx, SU, tapa_dy, tapa_ang, True, solo="tapa")
    pj.pegar(L, pj.caja(s, lt, ep, bp, mirar=mp), xp, yp)

ANIMACIONES["copito"] = _a_copito

import show as _show
ANIMACIONES["show"] = _show.a_show

def esc_anim(L, e, lt, a):
    ANIMACIONES[e.get("escena", "hola")](L, e, lt)
    if e.get("lineas"):                                       # diálogo hablado: el texto sigue a la voz
        activa = None
        for desde, hasta, quien, frase in e["lineas"]:
            if lt >= desde: activa = (desde, quien, frase)
        if e.get("subt_cortos"):
            act = None                                       # solo una frase a la vez (la última que empezó)
            for desde, hasta, quien, frase in e["lineas"]:
                if desde <= lt < hasta + 0.25: act = (desde, hasta, quien, frase)
            if act:
                desde, hasta, quien, frase = act
                _subt_corto(L, quien, frase, lt - desde, max(0.3, hasta - desde), a)
            return
        if activa:
            nombre = {"paqui": "Paqui", "amigo": "Su amigo", "copito": "Copito"}.get(activa[1], activa[1])
            esc_clip(L, dict(e, texto=f"{nombre}: {activa[2]}", resaltado=None, globo=None), lt - activa[0], a)
        return
    c = e.get("cambio")
    if e.get("texto_despues") and c is not None and lt >= float(c):
        esc_clip(L, dict(e, texto=e["texto_despues"], resaltado=e.get("resaltado_despues"), globo=None), lt - float(c), a)
    else:
        esc_clip(L, e, lt, a)

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

TIPOS = {"cierre": esc_cierre, "titulo": esc_titulo, "punto": esc_punto, "texto": esc_texto, "cta": esc_cta, "clip": esc_clip, "anim": esc_anim}

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
    if not es_clip and not es_cierre and esc["tipo"] != "anim":
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
    efectos = [(s0 + float(off), tipo) for s0, _, e in escenas for off, tipo in e.get("sfx", [])]
    if efectos:                                                # efectos de sonido sintetizados (escena "show")
        ruta_sfx = os.path.join(tmp, "sfx.wav"); _show.sfx_wav(efectos, total, ruta_sfx)
        voces.append((0.0, {"archivo": ruta_sfx, "inicio": 0, "dur": total + 1, "sfx": True}))
    for s0, _, e in escenas:                                   # voces de los personajes animados
        for off, archivo in e.get("voces", []):
            voces.append((s0 + float(off), {"archivo": archivo, "inicio": 0, "dur": 30}))
    entradas = ["-i", muda, "-i", wav]
    if not voces:
        filtro, mapa = None, "1:a"
    else:
        partes = ["[1:a]volume=0.22[mus]"]; etiquetas = ["[mus]"]
        for k, (s0, e) in enumerate(voces):
            entradas += ["-ss", str(e.get("inicio", 0)), "-t", str(e["dur"]), "-i", e["archivo"]]
            ms = int(s0 * 1000)
            if e.get("sfx"): partes.append(f"[{k + 2}:a]aresample=44100,volume=0.9[v{k}]")
            else: partes.append(f"[{k + 2}:a]aresample=44100,highpass=f=90,dynaudnorm=f=150:g=15,volume=1.3,adelay={ms}|{ms}[v{k}]")
            etiquetas.append(f"[v{k}]")
        partes.append("".join(etiquetas) + f"amix=inputs={len(etiquetas)}:duration=first:normalize=0,alimiter=limit=0.95[a]")
        filtro, mapa = ";".join(partes), "[a]"
    cmd = ["ffmpeg", "-y", "-loglevel", "error"] + entradas
    if filtro: cmd += ["-filter_complex", filtro]
    cmd += ["-map", "0:v", "-map", mapa, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
            "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    main()
