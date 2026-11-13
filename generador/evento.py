"""Utilería "evento" para anuncios elegantes (afiches de eventos, webinars) dentro de la escena "show".

Props (todos admiten "desde"/"hasta"; números con tiempo como en show.py):
 {"tipo": "fondo_gala", "imagen": "ruta.webp" (opcional, se desenfoca detrás)}  fondo azul noche con destellos dorados
 {"tipo": "imagen", "src": "ruta", "x": 540, "y": 900, "w": 600, "recorte": [x0,y0,x1,y1], "circulo": false,
   "marco": "oro"|"blanco"|null, "radio": 30, "anim": "pop|sube|izq|der|zoom|nada", "ang": 0, "flota": true,
   "brillo": true (barrido de luz dorado)}
 {"tipo": "tarjeta", "x": 540, "y": 900, "w": 900, "titulo": "...", "icono": "📅",
   "lineas": [[t, "texto", tam, "color"|null], ...] (cada línea aparece en su segundo), "anim": "pop|sube"}
 {"tipo": "qr", "src": "ruta png", "x": 540, "y": 980, "w": 640, "titulo": "ESCANEA Y", "sub": "INSCRÍBETE"}
 {"tipo": "cinta", "texto": "...", "y": 560, "tam": 64, "fondo": "oro"|[r,g,b], "color": [r,g,b]}  banda que entra
"""
import math
import random
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
NAVY = (8, 22, 58); NAVY2 = (14, 40, 96); ORO = (232, 186, 92); ORO2 = (255, 226, 150)
BLANCO = (255, 255, 255); NARANJA = (255, 122, 26)


def _font(w, s):
    return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{w}.otf", int(max(8, s)))


def _num(v, t):
    if not (isinstance(v, list) and v and isinstance(v[0], list)): return v
    if t <= v[0][0]: return v[0][1]
    for (t0, a), (t1, b) in zip(v, v[1:]):
        if t < t1:
            k = (t - t0) / max(1e-6, t1 - t0); k = k * k * (3 - 2 * k)
            return a + (b - a) * k
    return v[-1][1]


def _ease(x):
    x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3


def _elast(x):
    if x <= 0: return 0.0
    if x >= 1: return 1.0
    return 1 + 2 ** (-10 * x) * math.sin((x - 0.075) * 2 * math.pi / 0.3)


def _pegar(L, im, x, y, ang=0.0, alfa=1.0):
    if abs(ang) > 0.05: im = im.rotate(ang, Image.BICUBIC, expand=True)
    if alfa < 0.999:
        im = im.copy(); im.putalpha(im.getchannel("A").point(lambda p: int(p * max(0, alfa))))
    L.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))


def _oro_grad(w, h):
    """Degradado dorado vertical (para marcos y textos)."""
    g = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(g)
    for y in range(h):
        k = y / max(1, h - 1); s = 0.5 + 0.5 * math.cos(k * math.pi * 2)
        c = tuple(int(ORO[i] + (ORO2[i] - ORO[i]) * s) for i in range(3))
        d.line([(0, y), (w, y)], fill=c + (255,))
    return g


@lru_cache(maxsize=8)
def _fondo_base(imagen):
    base = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(base)
    for y in range(H):
        k = y / H
        c = tuple(int(NAVY[i] * (1 - k) + NAVY2[i] * k * 0.9 + 4 * k) for i in range(3))
        d.line([(0, y), (W, y)], fill=c + (255,))
    if imagen:
        im = Image.open(imagen).convert("RGBA")
        z = max(W / im.width, H / im.height) * 1.1
        im = im.resize((int(im.width * z), int(im.height * z)), Image.LANCZOS).filter(ImageFilter.GaussianBlur(28))
        im = im.crop(((im.width - W) // 2, (im.height - H) // 2, (im.width - W) // 2 + W, (im.height - H) // 2 + H))
        im.putalpha(95)
        base.alpha_composite(im)
    # viñeta
    v = Image.new("L", (W, H), 0); dv = ImageDraw.Draw(v)
    dv.ellipse([-300, -200, W + 300, H + 200], fill=255)
    v = v.filter(ImageFilter.GaussianBlur(160))
    osc = Image.new("RGBA", (W, H), (0, 0, 0, 170)); osc.putalpha(v.point(lambda p: int((255 - p) * 0.75)))
    base.alpha_composite(osc)
    return base


def p_fondo_gala(L, p, lt, k):
    L.alpha_composite(_fondo_base(p.get("imagen")))
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    # haces de luz dorados en diagonal que se desplazan
    for i, (off, an, al) in enumerate(((0, 90, 34), (520, 40, 46), (900, 140, 22))):
        x0 = (off + lt * 140) % (W + 1400) - 700
        d.polygon([(x0, 0), (x0 + an, 0), (x0 + an + 900, H), (x0 + 900, H)], fill=ORO + (al,))
    capa = capa.filter(ImageFilter.GaussianBlur(18))
    L.alpha_composite(capa)
    # curvas doradas (como el afiche)
    c2 = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d2 = ImageDraw.Draw(c2)
    for j, (yb, amp, an) in enumerate(((1700, 120, 6), (1760, 90, 3), (230, 80, 4))):
        pts = [(x, yb + amp * math.sin(x / 260 + lt * 0.9 + j)) for x in range(-20, W + 40, 20)]
        d2.line(pts, fill=ORO + (150,), width=an)
    L.alpha_composite(c2.filter(ImageFilter.GaussianBlur(1.2)))
    # chispas
    rnd = random.Random(7); d3 = ImageDraw.Draw(L)
    for i in range(46):
        x = rnd.uniform(0, W); y0 = rnd.uniform(0, H); vel = rnd.uniform(20, 70)
        y = (y0 - lt * vel) % H; r = rnd.uniform(1.5, 4.2)
        a = int(200 * (0.5 + 0.5 * math.sin(lt * rnd.uniform(2, 5) + i)))
        d3.ellipse([x - r, y - r, x + r, y + r], fill=ORO2 + (a,))


_IMG = {}


def _cargar(src, recorte, w, circulo, marco, radio):
    clave = (src, tuple(recorte or ()), int(w), circulo, marco, radio)
    if clave in _IMG: return _IMG[clave]
    im = Image.open(src).convert("RGBA")
    if recorte: im = im.crop(tuple(recorte))
    z = w / im.width
    im = im.resize((int(im.width * z), int(im.height * z)), Image.LANCZOS)
    b = {"oro": 12, "blanco": 14}.get(marco, 0)
    Wc, Hc = im.width + 2 * b, im.height + 2 * b
    out = Image.new("RGBA", (Wc + 60, Hc + 60), (0, 0, 0, 0))
    # sombra
    sm = Image.new("L", out.size, 0); ds = ImageDraw.Draw(sm)
    if circulo: ds.ellipse([30, 42, 30 + Wc, 42 + Hc], fill=150)
    else: ds.rounded_rectangle([30, 42, 30 + Wc, 42 + Hc], radio + b, fill=150)
    sombra = Image.new("RGBA", out.size, (0, 0, 0, 255)); sombra.putalpha(sm.filter(ImageFilter.GaussianBlur(16)))
    out.alpha_composite(sombra)
    if b:
        mk = Image.new("L", (Wc, Hc), 0); dm = ImageDraw.Draw(mk)
        if circulo: dm.ellipse([0, 0, Wc - 1, Hc - 1], fill=255)
        else: dm.rounded_rectangle([0, 0, Wc - 1, Hc - 1], radio + b, fill=255)
        borde = _oro_grad(Wc, Hc) if marco == "oro" else Image.new("RGBA", (Wc, Hc), BLANCO + (255,))
        borde.putalpha(mk); out.alpha_composite(borde, (30, 30))
    mk = Image.new("L", im.size, 0); dm = ImageDraw.Draw(mk)
    if circulo: dm.ellipse([0, 0, im.width - 1, im.height - 1], fill=255)
    else: dm.rounded_rectangle([0, 0, im.width - 1, im.height - 1], radio, fill=255)
    im.putalpha(mk)
    out.alpha_composite(im, (30 + b, 30 + b))
    _IMG[clave] = out
    return out


def _entrada(anim, k, x, y):
    """Devuelve (x, y, escala, alfa) según la animación de entrada."""
    if anim == "pop": return x, y, max(0.01, _elast(k / 0.55)), 1.0
    q = _ease(k / 0.5)
    if anim == "sube": return x, y + (1 - q) * 380, 1.0, q
    if anim == "izq": return x - (1 - q) * 900, y, 1.0, 1.0
    if anim == "der": return x + (1 - q) * 900, y, 1.0, 1.0
    if anim == "zoom": return x, y, 0.6 + 0.4 * q, q
    return x, y, 1.0, 1.0


def _brillo(im, k):
    """Barrido de luz que cruza la imagen una vez cada 2,6 s."""
    fase = (k % 2.6) / 0.9
    if fase > 1: return im
    w, h = im.size; luz = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(luz)
    x = -w * 0.5 + fase * w * 2
    d.polygon([(x, 0), (x + w * 0.18, 0), (x + w * 0.18 - h * 0.5, h), (x - h * 0.5, h)], fill=(255, 255, 255, 90))
    luz = luz.filter(ImageFilter.GaussianBlur(10))
    a = im.getchannel("A"); r = im.copy(); r.alpha_composite(luz); r.putalpha(a)
    return r


def p_imagen(L, p, lt, k):
    x, y, w = _num(p.get("x", 540), lt), _num(p.get("y", 900), lt), _num(p.get("w", 600), lt)
    im = _cargar(p["src"], p.get("recorte"), p.get("w_base", w if not isinstance(p.get("w"), list) else max(v for _, v in p["w"])),
                 p.get("circulo", False), p.get("marco"), p.get("radio", 28))
    x, y, z, alfa = _entrada(p.get("anim", "pop"), k, x, y)
    base_w = p.get("w_base", w if not isinstance(p.get("w"), list) else max(v for _, v in p["w"]))
    z *= w / base_w
    if p.get("flota", True): y += 10 * math.sin(lt * 2.2 + x / 200)
    if p.get("brillo"): im = _brillo(im, k)
    if abs(z - 1) > 0.01: im = im.resize((max(2, int(im.width * z)), max(2, int(im.height * z))), Image.BICUBIC)
    _pegar(L, im, x, y, _num(p.get("ang", 0), lt), alfa)


def _texto_oro(texto, f):
    tw = int(f.getlength(texto)) + 20; th = int(f.size * 1.35)
    m = Image.new("L", (tw, th), 0); ImageDraw.Draw(m).text((10, th / 2), texto, font=f, fill=255, anchor="lm")
    g = _oro_grad(tw, th); g.putalpha(m)
    return g


def p_tarjeta(L, p, lt, k):
    x, y, w = p.get("x", 540), p.get("y", 900), p.get("w", 920)
    lineas = p.get("lineas", [])
    pad = 46
    f_t = _font("Black", p.get("tam_titulo", 58))
    alto = pad + (f_t.size * 1.4 if p.get("titulo") else 0)
    for _, txt, tam, *_ in lineas:
        alto += tam * 1.28
    alto += pad - 10
    alto = max(alto, p.get("h", 0))
    x, y, z, alfa = _entrada(p.get("anim", "sube"), k, x, y)
    card = Image.new("RGBA", (int(w + 60), int(alto + 60)), (0, 0, 0, 0)); d = ImageDraw.Draw(card)
    sm = Image.new("L", card.size, 0); ImageDraw.Draw(sm).rounded_rectangle([30, 44, 30 + w, 44 + alto], 40, fill=170)
    sombra = Image.new("RGBA", card.size, (0, 0, 0, 255)); sombra.putalpha(sm.filter(ImageFilter.GaussianBlur(18)))
    card.alpha_composite(sombra)
    borde = _oro_grad(int(w), int(alto)); mk = Image.new("L", borde.size, 0)
    ImageDraw.Draw(mk).rounded_rectangle([0, 0, w - 1, alto - 1], 40, fill=255); borde.putalpha(mk)
    card.alpha_composite(borde, (30, 30))
    d.rounded_rectangle([36, 36, 24 + w, 24 + alto], 35, fill=(10, 28, 72, 245))
    cy = 30 + pad
    if p.get("titulo"):
        t = p["titulo"]; ico = p.get("icono")
        g = _texto_oro(t, f_t)
        card.alpha_composite(g, (int(30 + w / 2 - g.width / 2), int(cy - 6)))
        cy += f_t.size * 1.4
        d.line([30 + w * 0.2, cy - 12, 30 + w * 0.8, cy - 12], fill=ORO + (200,), width=3)
    for t0, txt, tam, *resto in lineas:
        col = tuple(resto[0]) if resto and resto[0] else BLANCO
        q = _ease((k - t0) / 0.35)
        if q > 0:
            f = _font(resto[1] if len(resto) > 1 else "Bold", tam)
            while f.getlength(txt) > w - 70 and f.size > 20: f = _font(resto[1] if len(resto) > 1 else "Bold", f.size - 2)
            tl = Image.new("RGBA", (int(w), int(tam * 1.4)), (0, 0, 0, 0))
            ImageDraw.Draw(tl).text((w / 2, tam * 0.7), txt, font=f, fill=col + (int(255 * q),), anchor="mm")
            card.alpha_composite(tl, (30, int(cy + (1 - q) * 30 - tam * 0.06)))
        cy += tam * 1.28
    if z != 1: card = card.resize((max(2, int(card.width * z)), max(2, int(card.height * z))), Image.BICUBIC)
    _pegar(L, card, x, y, p.get("ang", 0), alfa)
    ico = p.get("icono")
    if ico and z > 0.3:
        import show
        e = show.emoji(ico, 110 * min(1, z))
        _pegar(L, e, x - w / 2 + 30, y - alto / 2 + 10 + 6 * math.sin(lt * 3), -10 + 6 * math.sin(lt * 2), alfa)


def p_qr(L, p, lt, k):
    x, y, w = p.get("x", 540), p.get("y", 980), p.get("w", 640)
    q = _elast(k / 0.6)
    qr = Image.open(p["src"]).convert("RGBA").resize((int(w), int(w)), Image.NEAREST)
    pad = 34; f1 = _font("Black", 62); f2 = _font("Black", 76)
    cab = 175
    while f1.getlength(p.get("titulo", "ESCANEA Y")) > w + 2 * pad - 70 and f1.size > 30: f1 = _font("Black", f1.size - 2)
    card = Image.new("RGBA", (int(w + 2 * pad + 60), int(w + 2 * pad + cab + 60)), (0, 0, 0, 0)); d = ImageDraw.Draw(card)
    cw, ch = w + 2 * pad, w + 2 * pad + cab
    sm = Image.new("L", card.size, 0); ImageDraw.Draw(sm).rounded_rectangle([30, 46, 30 + cw, 46 + ch], 44, fill=190)
    sombra = Image.new("RGBA", card.size, (0, 0, 0, 255)); sombra.putalpha(sm.filter(ImageFilter.GaussianBlur(20)))
    card.alpha_composite(sombra)
    borde = _oro_grad(int(cw), int(ch)); mk = Image.new("L", borde.size, 0)
    ImageDraw.Draw(mk).rounded_rectangle([0, 0, cw - 1, ch - 1], 44, fill=255); borde.putalpha(mk)
    card.alpha_composite(borde, (30, 30))
    d.rounded_rectangle([42, 42, 18 + cw, 18 + ch], 34, fill=BLANCO + (255,))
    d.text((30 + cw / 2, 30 + 62), p.get("titulo", "ESCANEA Y"), font=f1, fill=(11, 37, 84, 255), anchor="mm")
    d.text((30 + cw / 2, 30 + 135), p.get("sub", "INSCRÍBETE"), font=f2, fill=NARANJA + (255,), anchor="mm")
    card.alpha_composite(qr, (int(30 + pad), int(30 + cab + pad - 10)))
    # esquinas animadas de "escáner"
    if k > 0.6:
        pul = 0.5 + 0.5 * math.sin(lt * 6); L2 = 70; g = 10 + 10 * pul
        x0, y0 = 30 + pad - g, 30 + cab + pad - 10 - g; x1, y1 = x0 + w + 2 * g, y0 + w + 2 * g
        col = NARANJA + (255,)
        for (cx, cy, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
            d.line([cx, cy, cx + sx * L2, cy], fill=col, width=12); d.line([cx, cy, cx, cy + sy * L2], fill=col, width=12)
        # línea láser que recorre el código (fina y semitransparente para no estorbar al escanear)
        if p.get("laser", True) and k < p.get("laser_hasta", 3.0):
            ly = y0 + g + (w) * (0.5 + 0.5 * math.sin(lt * 2.4))
            d.line([x0 + 20, ly, x1 - 20, ly], fill=(255, 60, 60, 120), width=4)
    z = max(0.01, q)
    if z != 1: card = card.resize((max(2, int(card.width * z)), max(2, int(card.height * z))), Image.BICUBIC)
    _pegar(L, card, x, y, 0, 1)


def p_cinta(L, p, lt, k):
    y = p.get("y", 560); q = _ease(k / 0.4)
    f = _font("Black", p.get("tam", 64)); tw = f.getlength(p["texto"])
    wb, hb = tw + 120, p.get("tam", 64) * 1.7
    im = Image.new("RGBA", (int(wb), int(hb)), (0, 0, 0, 0))
    fondo = p.get("fondo", "oro")
    if fondo == "oro":
        g = _oro_grad(int(wb), int(hb)); mk = Image.new("L", g.size, 0)
        ImageDraw.Draw(mk).rounded_rectangle([0, 0, wb - 1, hb - 1], int(hb / 2), fill=255); g.putalpha(mk); im.alpha_composite(g)
        col = tuple(p.get("color", NAVY))
    else:
        ImageDraw.Draw(im).rounded_rectangle([0, 0, wb - 1, hb - 1], int(hb / 2), fill=tuple(fondo) + (255,))
        col = tuple(p.get("color", BLANCO))
    ImageDraw.Draw(im).text((wb / 2, hb / 2), p["texto"], font=f, fill=col + (255,), anchor="mm")
    x = p.get("x", 540) + (1 - q) * W * (1 if p.get("lado", 1) > 0 else -1)
    _pegar(L, im, x, y, p.get("ang", 0))


PROPS = {"fondo_gala": p_fondo_gala, "imagen": p_imagen, "tarjeta": p_tarjeta, "qr": p_qr, "cinta": p_cinta}
