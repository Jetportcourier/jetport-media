"""Escena "show": un escenario libre para los sketches hablados de Paqui (se arma todo desde el guion JSON).

{"tipo": "anim", "escena": "show", "dur": 8, "estilo_fondo": "rayos",
 "actores": [ {"quien": "paqui"|"amigo"|"maleta"|"emoji", "x": 540, "y": 1470, "s": 290,
               "expr": "feliz" o [[0, "panico"], [2.1, "feliz"]],          (valores con tiempo: cambian en ese segundo)
               "brazos": "normal|habla|arriba|agita|senala|taza|cintura" o [izq, der],
               "mov": "quieto|salta|tiembla|baila|camina|flota|entra_der|entra_izq|cae|pop|sale_der|vibra",
               "sx": 1, "sy": 1, "ang": 0, "mirar": [1, 0], "color": "paqui",
               "acc": ["lentes", "corbata", "gorro", "cafe"], "desde": 0, "hasta": 99,
               "e": "😍" (solo para quien=emoji), "habla": "clienta" (para mover la boca/rebote con esa voz)} ],
 "props": [ {"tipo": "emoji|texto|cartel|burbuja|comentario|balanza|medidas|cajas_caen|fuegos|bodega|ruta|escritorio|corazones|destello",
             "desde": 0, "hasta": 99, "capa": "atras"|"frente", ...} ],
 "sacudir": [[desde, hasta, px]], "sfx": [[segundo, "ding|beep|boing|crash|pop|sello|turbulencia|fuegos|tada|swish|risas"]]}
Números con tiempo: [[0, 300], [1.5, 700]] interpola suave entre puntos.
"""
import math
import random
from PIL import Image, ImageDraw, ImageFont

import personajes as pj

W, H = 1080, 1920
SU = 1470
NAVY = (11, 37, 84); ORANGE = (255, 122, 26); WHITE = (255, 255, 255); AMARILLO = (255, 214, 64)
_FONTS = {}
_EMOJI = {}
_EMOJI_FONT = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"


def font(w, s):
    k = (w, int(s))
    if k not in _FONTS:
        _FONTS[k] = ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{w}.otf", int(s))
    return _FONTS[k]


def ease(x):
    x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3


def elastico(x):
    if x <= 0: return 0.0
    if x >= 1: return 1.0
    return 1 + 2 ** (-10 * x) * math.sin((x - 0.075) * 2 * math.pi / 0.3)


def _es_kf(v):
    return isinstance(v, list) and v and isinstance(v[0], list)


def paso(v, t):
    """Valor escalonado: [[t0, v0], [t1, v1]] -> el último cuyo tiempo ya pasó."""
    if not _es_kf(v): return v
    r = v[0][1]
    for tt, vv in v:
        if t >= tt: r = vv
    return r


def num(v, t):
    """Número interpolado (suave) entre fotogramas clave."""
    if not _es_kf(v): return v
    if t <= v[0][0]: return v[0][1]
    for (t0, a), (t1, b) in zip(v, v[1:]):
        if t < t1:
            k = (t - t0) / max(1e-6, t1 - t0); k = k * k * (3 - 2 * k)
            return a + (b - a) * k
    return v[-1][1]


def emoji(ch, size):
    k = (ch, int(size))
    if k not in _EMOJI:
        f = ImageFont.truetype(_EMOJI_FONT, 109)
        im = Image.new("RGBA", (220, 220), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((110, 110), ch, font=f, embedded_color=True, anchor="mm")
        bb = im.getbbox()
        im = im.crop(bb) if bb else im
        z = size / max(im.size)
        _EMOJI[k] = im.resize((max(1, int(im.width * z)), max(1, int(im.height * z))), Image.LANCZOS)
    return _EMOJI[k]


def pegar_centro(L, im, x, y, ang=0.0, alfa=1.0):
    if abs(ang) > 0.1: im = im.rotate(ang, Image.BICUBIC, expand=True)
    if alfa < 0.999:
        im = im.copy(); a = im.getchannel("A").point(lambda p: int(p * max(0, alfa))); im.putalpha(a)
    L.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))


def texto_borde(L, xy, s, f, color, a=1.0, borde=8, anchor="mm"):
    al = int(255 * max(0, min(1, a)))
    ImageDraw.Draw(L).text(xy, s, font=f, fill=tuple(color[:3]) + (al,), anchor=anchor,
                           stroke_width=borde, stroke_fill=(0, 0, 0, al))


def _wrap(texto, f, maxw):
    lineas, act = [], ""
    for w in texto.split():
        prueba = (act + " " + w).strip()
        if f.getlength(prueba) <= maxw or not act: act = prueba
        else: lineas.append(act); act = w
    if act: lineas.append(act)
    return lineas


# ---------------------------------------------------------------- personajes
BRAZOS = {"normal": lambda k: (20, 20), "arriba": lambda k: (160, 160),
          "habla": lambda k: (20, 110 + 20 * math.sin(k * 9)),
          "agita": lambda k: (160 + 15 * math.sin(k * 14), 160 - 15 * math.sin(k * 14)),
          "senala": lambda k: (20, 150 + 6 * math.sin(k * 6)), "senala_izq": lambda k: (150 + 6 * math.sin(k * 6), 20),
          "taza": lambda k: (20, 95), "cintura": lambda k: (55, 55), "cruzados": lambda k: (100, 100),
          "baile": lambda k: (90 + 70 * math.sin(k * 8), 90 - 70 * math.sin(k * 8))}


def _hablando(e, quien, lt):
    for desde, hasta, q, *_ in e.get("lineas", []):
        if q == quien and desde <= lt < hasta:
            return True
    return False


def _pt(x, y, s, sx, sy, px, py):
    """Punto (en unidades del sprite de la caja) -> píxeles en pantalla."""
    return x + (px - 95) * s / 100 * sx, y - (175 - py) * s / 100 * sy


def _accesorios(L, acc, x, y, s, sx, sy, lt):
    d = ImageDraw.Draw(L)
    u = s / 100
    if "lentes" in acc:
        for ex in (72, 108):
            cx, cy = _pt(x, y, s, sx, sy, ex, 82)
            d.rounded_rectangle([cx - 15 * u, cy - 10 * u, cx + 15 * u, cy + 10 * u], int(6 * u), fill=(15, 15, 25, 255))
            d.line([cx - 9 * u, cy - 5 * u, cx - 2 * u, cy - 5 * u], fill=(255, 255, 255, 160), width=max(2, int(2 * u)))
        a, b = _pt(x, y, s, sx, sy, 87, 80), _pt(x, y, s, sx, sy, 93, 80)
        d.line([a, b], fill=(15, 15, 25, 255), width=max(3, int(3 * u)))
    if "corbata" in acc:
        cx, cy = _pt(x, y, s, sx, sy, 91, 131)
        d.polygon([(cx - 13 * u, cy - 7 * u), (cx, cy), (cx - 13 * u, cy + 7 * u)], fill=(200, 30, 40, 255))
        d.polygon([(cx + 13 * u, cy - 7 * u), (cx, cy), (cx + 13 * u, cy + 7 * u)], fill=(200, 30, 40, 255))
        d.ellipse([cx - 4 * u, cy - 4 * u, cx + 4 * u, cy + 4 * u], fill=(150, 20, 30, 255))
    if "gorro" in acc:
        bx, by = _pt(x, y, s, sx, sy, 99, 36)
        d.polygon([(bx - 45 * u, by), (bx + 45 * u, by), (bx + 30 * u, by - 55 * u)], fill=(220, 30, 40, 255))
        d.rounded_rectangle([bx - 50 * u, by - 9 * u, bx + 50 * u, by + 9 * u], int(8 * u), fill=WHITE + (255,))
        d.ellipse([bx + 22 * u, by - 66 * u, bx + 40 * u, by - 48 * u], fill=WHITE + (255,))
    if "cafe" in acc:
        cx, cy = _pt(x, y, s, sx, sy, 186, 108)
        pegar_centro(L, emoji("☕", 70 * u), cx, cy)
        for i in range(2):                                                  # vapor
            k = (lt * 0.8 + i * 0.5) % 1
            d.arc([cx - 12 * u + i * 10 * u, cy - 70 * u - 40 * u * k, cx + 4 * u + i * 10 * u, cy - 40 * u - 40 * u * k],
                  200, 340, fill=(255, 255, 255, int(200 * (1 - k))), width=max(2, int(3 * u)))


def _maleta(L, x, y, s, lt, hablando, expr):
    """Maleta elegante de primera clase (morada con franjas doradas, ojos 'de sobrada')."""
    w, h = s * 1.15, s * 1.35
    d = ImageDraw.Draw(L)
    x0, y0 = x - w / 2, y - h
    d.rounded_rectangle([x - w * 0.2, y0 - h * 0.18, x + w * 0.2, y0 + 8], int(s * 0.08), outline=(60, 30, 70, 255), width=int(s * 0.06))
    d.rounded_rectangle([x0, y0, x0 + w, y], int(s * 0.12), fill=(120, 60, 160, 255), outline=(60, 30, 70, 255), width=6)
    for fx in (0.22, 0.78):
        d.rectangle([x0 + w * fx - s * 0.04, y0, x0 + w * fx + s * 0.04, y], fill=(230, 190, 80, 255))
    for fx in (0.15, 0.85):
        d.ellipse([x0 + w * fx - s * 0.07, y - s * 0.02, x0 + w * fx + s * 0.07, y + s * 0.1], fill=(40, 30, 40, 255))
    # cara: ojos con párpado a media asta (sobrada) y pestañas
    for ex in (0.36, 0.64):
        cx, cy = x0 + w * ex, y0 + h * 0.38
        r = s * 0.11
        d.ellipse([cx - r, cy - r * 1.1, cx + r, cy + r * 1.1], fill=WHITE + (255,), outline=(40, 20, 50, 255), width=4)
        d.ellipse([cx - r * 0.45, cy - r * 0.2, cx + r * 0.45, cy + r * 0.7], fill=(40, 20, 50, 255))
        if expr != "sorpresa":
            d.chord([cx - r - 2, cy - r * 1.1 - 2, cx + r + 2, cy + r * 1.1], 180, 360, fill=(150, 90, 190, 255))
            d.line([cx - r, cy, cx + r, cy], fill=(40, 20, 50, 255), width=5)
        for j in range(3):
            d.line([cx - r * 0.6 + j * r * 0.6, cy - r * (1.1 if expr == "sorpresa" else 0.1),
                    cx - r * 0.75 + j * r * 0.75, cy - r * (1.5 if expr == "sorpresa" else 0.45)], fill=(40, 20, 50, 255), width=4)
    mx, my = x, y0 + h * 0.66
    if hablando and (lt * 7.5) % 1 < 0.5:
        d.chord([mx - s * 0.12, my - s * 0.06, mx + s * 0.12, my + s * 0.14], 0, 180, fill=(110, 20, 50, 255), outline=(40, 20, 50, 255), width=3)
    else:
        d.arc([mx - s * 0.1, my - s * 0.08, mx + s * 0.1, my + s * 0.06], 20, 160, fill=(40, 20, 50, 255), width=5)
    # moño
    bx, by = x, y0 - 4
    d.polygon([(bx - s * 0.13, by - s * 0.08), (bx, by), (bx - s * 0.13, by + s * 0.08)], fill=(230, 60, 140, 255))
    d.polygon([(bx + s * 0.13, by - s * 0.08), (bx, by), (bx + s * 0.13, by + s * 0.08)], fill=(230, 60, 140, 255))


def _actor(L, e, a, lt):
    desde, hasta = a.get("desde", 0), a.get("hasta", 999)
    if not desde <= lt < hasta: return
    k = lt - desde
    quien = a.get("quien", "paqui")
    s = num(a.get("s", 290), lt)
    x, y = num(a.get("x", 540), lt), num(a.get("y", SU), lt)
    sx, sy, ang = num(a.get("sx", 1.0), lt), num(a.get("sy", 1.0), lt), num(a.get("ang", 0.0), lt)
    expr = paso(a.get("expr", "feliz"), lt)
    br = paso(a.get("brazos", "normal"), lt)
    mov = paso(a.get("mov", "quieto"), lt)
    mirar = paso(a.get("mirar", [0, 0]), lt)
    piernas = 0.0
    if mov == "salta":
        y -= 70 * abs(math.sin(k * 7)); piernas = k * 10
    elif mov == "tiembla":
        x += 9 * math.sin(k * 55); ang += 2 * math.sin(k * 40)
    elif mov == "vibra":
        x += 4 * math.sin(k * 70); y -= 3 * abs(math.sin(k * 60))
    elif mov == "baila":
        ang += 10 * math.sin(k * 8); y -= 35 * abs(math.sin(k * 8)); piernas = k * 8
        if br == "normal": br = "baile"
    elif mov == "camina":
        piernas = k * 12; y -= 8 * abs(math.sin(k * 12))
    elif mov == "flota":
        y -= 22 * math.sin(k * 2.2); ang += 3 * math.sin(k * 1.7)
    elif mov == "entra_der":
        x = W + 320 - (W + 320 - x) * ease(k / 0.55); piernas = k * 14 if k < 0.55 else 0
    elif mov == "entra_izq":
        x = -320 + (x + 320) * ease(k / 0.55); piernas = k * 14 if k < 0.55 else 0
    elif mov == "sale_der":
        x = x + (W + 400 - x) * min(1, (k / 0.6) ** 2); piernas = k * 14
    elif mov == "cae":
        q = min(1, k / 0.45); y = -200 + (y + 200) * q * q
        if 0.45 <= k < 0.7:
            z = math.sin((k - 0.45) / 0.25 * math.pi); sx *= 1 + 0.25 * z; sy *= 1 - 0.25 * z
    elif mov == "pop":
        z = max(0.01, elastico(k / 0.6)); sx *= z; sy *= z
    voz = a.get("habla", quien)
    habla = _hablando(e, voz, lt)
    if quien == "emoji":
        ch = paso(a.get("e", "😀"), lt)
        z = 1 + (0.08 * abs(math.sin(lt * 14)) if habla else 0)
        im = emoji(ch, s * z)
        im = im.resize((max(1, int(im.width * sx)), max(1, int(im.height * sy))), Image.BILINEAR)
        if a.get("sombra", True): pj.sombra(L, x, y - 6, s * 0.9)
        pegar_centro(L, im, x, y - im.height / 2, ang)
        return
    if quien == "maleta":
        if a.get("sombra", True): pj.sombra(L, x, y - 6, s * 1.3)
        _maleta(L, x, y + (-6 * abs(math.sin(lt * 12)) if habla else 0), s, lt, habla, expr)
        return
    if habla and (lt * 7.5) % 1 < 0.5 and expr in ("feliz", "sorpresa", "nervioso", "alivio"):
        expr = "abierta"
    brazos = tuple(br) if isinstance(br, list) else BRAZOS.get(br, BRAZOS["normal"])(lt)
    if a.get("sombra", True): pj.sombra(L, x, num(a.get("y", SU), lt) - 8, s * 1.4 * sx)
    spr = pj.caja(s, lt, expr, brazos, mirar=tuple(mirar), piernas=piernas, color=a.get("color", "paqui"),
                  sudor=a.get("sudor", 0))
    pj.pegar(L, spr, x, y, sx, sy, ang)
    _accesorios(L, paso(a.get("acc", []), lt), x, y, s, sx, sy, lt)


# ---------------------------------------------------------------- utilería
def _p_emoji(L, p, lt, k):
    anim = p.get("anim", "pop")
    x, y, r = num(p.get("x", 540), lt), num(p.get("y", 900), lt), num(p.get("r", 160), lt)
    ang, alfa = num(p.get("ang", 0), lt), 1.0
    if anim == "pop":
        r *= max(0.01, elastico(k / 0.5)); y -= 10 * math.sin(lt * 3 + x)
    elif anim == "flota":
        r *= max(0.01, elastico(k / 0.5)); y -= 25 * math.sin(lt * 2.5 + x / 100); ang += 6 * math.sin(lt * 2 + x)
    elif anim == "cae":
        q = min(1, k / 0.5); y = -150 + (y + 150) * q * q
    elif anim == "gira":
        ang += k * 360
    elif anim == "late":
        r *= 1 + 0.12 * abs(math.sin(lt * 7))
    elif anim == "vuela":
        x0, y0 = p.get("de", [x - 600, y])
        q = ease(k / p.get("t", 0.8)); x = x0 + (x - x0) * q; y = y0 + (y - y0) * q - 120 * math.sin(q * math.pi)
    elif anim == "corta":                                                  # cuchillo que va y viene
        ang += 25 * math.sin(k * 16); x += 30 * math.sin(k * 16)
    im = emoji(p["e"], max(4, r))
    pegar_centro(L, im, x, y, ang, alfa)
    if p.get("tachado") and k > p.get("tachado_t", 0.3):
        q = ease((k - p.get("tachado_t", 0.3)) / 0.25); d = ImageDraw.Draw(L); rr = r * 0.62
        d.line([x - rr, y - rr, x - rr + 2 * rr * q, y - rr + 2 * rr * q], fill=(230, 30, 40, 255), width=int(r * 0.11))
        if q >= 1: d.line([x + rr, y - rr, x - rr, y + rr], fill=(230, 30, 40, 255), width=int(r * 0.11))
    if p.get("texto"):
        f = font("Black", p.get("tam", 54))
        texto_borde(L, (x, y + r / 2 + 40), p["texto"], f, tuple(p.get("color", WHITE)), min(1, k / 0.2), borde=7)


def _p_texto(L, p, lt, k):
    x, y = num(p.get("x", 540), lt), num(p.get("y", 800), lt)
    z = max(0.01, elastico(k / 0.45)) if p.get("pop", True) else 1
    tam = p.get("tam", 120) * z
    ang = num(p.get("ang", 0), lt) + (3 * math.sin(lt * 10) if p.get("tiembla") else 0)
    f = font(p.get("peso", "Black"), max(8, tam))
    col = tuple(p.get("color", AMARILLO))
    if p.get("estilo") == "sello":
        tw = f.getlength(p["texto"]); hh = tam * 1.25
        im = Image.new("RGBA", (int(tw + tam), int(hh + tam * 0.5)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([tam * 0.25, tam * 0.2, im.width - tam * 0.25, im.height - tam * 0.2], int(tam * 0.15),
                            outline=col + (235,), width=max(4, int(tam * 0.1)))
        d.text((im.width / 2, im.height / 2), p["texto"], font=f, fill=col + (235,), anchor="mm")
        pegar_centro(L, im, x, y, ang if ang else -12)
        return
    im = Image.new("RGBA", (int(f.getlength(p["texto"]) + 60), int(tam * 1.6)), (0, 0, 0, 0))
    texto_borde(im, (im.width / 2, im.height / 2), p["texto"], f, col, 1, borde=max(4, int(tam * 0.09)))
    pegar_centro(L, im, x, y, ang)


def _p_cartel(L, p, lt, k):
    """Banda con texto arriba (EXPECTATIVA / REALIDAD / 27 NOV)."""
    y = p.get("y", 640); q = ease(k / 0.35)
    f = font("Black", p.get("tam", 78)); tw = f.getlength(p["texto"])
    col = tuple(p.get("fondo", ORANGE)); x = W / 2 + (1 - q) * (W if p.get("lado", 1) > 0 else -W)
    im = Image.new("RGBA", (int(tw + 110), int(p.get("tam", 78) * 1.6)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, im.width - 1, im.height - 1], int(im.height / 2), fill=col + (255,), outline=(0, 0, 0, 255), width=6)
    d.text((im.width / 2, im.height / 2), p["texto"], font=f, fill=tuple(p.get("color", WHITE)) + (255,), anchor="mm")
    pegar_centro(L, im, x, y, p.get("ang", -3))


def _p_burbuja(L, p, lt, k, estilo="chat"):
    x, y, w = num(p.get("x", 540), lt), num(p.get("y", 760), lt), p.get("w", 640)
    z = max(0.01, elastico(k / 0.45))
    txt = paso(p.get("texto", ""), lt)
    f = font("Bold", p.get("tam", 56)); lines = _wrap(txt, f, w - 80 - (190 if estilo == "comentario" else 0))
    lh = p.get("tam", 56) * 1.25; h = 70 + lh * len(lines)
    extra = 120 if estilo == "comentario" else 0
    im = Image.new("RGBA", (int(w + 40), int(h + 70 + 20)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    fondo = tuple(p.get("fondo", (255, 255, 255)))
    d.rounded_rectangle([10, 10, w + 30, h + 10], 38, fill=fondo + (250,), outline=(0, 0, 0, 255), width=5)
    cola = p.get("cola", "abajo")
    if cola == "abajo":
        d.polygon([(w * 0.3, h + 4), (w * 0.3 + 60, h + 4), (w * 0.3 + 5, h + 70)], fill=fondo + (250,), outline=(0, 0, 0, 255))
        d.line([(w * 0.3 + 4, h + 9), (w * 0.3 + 56, h + 9)], fill=fondo + (255,), width=8)
    if estilo == "comentario":
        d.ellipse([34, 30, 34 + 76, 30 + 76], fill=(200, 205, 215, 255))
        d.ellipse([34 + 22, 30 + 12, 34 + 54, 30 + 44], fill=(150, 155, 170, 255))
        d.chord([34 + 8, 30 + 46, 34 + 68, 30 + 106], 180, 360, fill=(150, 155, 170, 255))
    for i, ln in enumerate(lines):
        d.text((40 + extra if estilo == "comentario" else (w + 40) / 2, 10 + 35 + lh * (i + 0.5)), ln, font=f,
               fill=tuple(p.get("color", NAVY)) + (255,), anchor="lm" if estilo == "comentario" else "mm")
    if estilo == "comentario":
        pegar_centro(im, emoji("❤", 46), w - 10, h / 2 + 10)
    im = im.resize((max(1, int(im.width * z)), max(1, int(im.height * z))), Image.BILINEAR)
    pegar_centro(L, im, x, y, p.get("ang", 0))
    if p.get("contador"):
        a, b = p["contador"]; dur = p.get("t_contador", 2.0)
        n = int(a + (b - a) * min(1, max(0, k - 0.2) / dur) ** 1.6)
        bx, by = x + w * z / 2 - 10, y - h * z / 2 - 10
        d = ImageDraw.Draw(L); r = 52 + 6 * abs(math.sin(lt * 12))
        d.ellipse([bx - r, by - r, bx + r, by + r], fill=(235, 30, 50, 255), outline=WHITE + (255,), width=6)
        d.text((bx, by), str(n), font=font("Black", 56 if n < 100 else 44), fill=WHITE + (255,), anchor="mm")


def _p_balanza(L, p, lt, k):
    x, base = p.get("x", 540), p.get("y", SU + 40)
    d = ImageDraw.Draw(L); ancho = p.get("w", 520)
    d.rounded_rectangle([x - ancho / 2, base - 40, x + ancho / 2, base + 20], 16, fill=(150, 160, 175, 255), outline=(40, 45, 60, 255), width=6)
    d.rectangle([x - ancho / 2 + 20, base - 54, x + ancho / 2 - 20, base - 38], fill=(190, 198, 210, 255), outline=(40, 45, 60, 255), width=4)
    px = x + ancho / 2 + 40
    d.rectangle([px - 14, base - 520, px + 14, base], fill=(120, 130, 145, 255), outline=(40, 45, 60, 255), width=4)
    d.rounded_rectangle([px - 150, base - 690, px + 120, base - 510], 22, fill=(60, 66, 80, 255), outline=(30, 32, 40, 255), width=6)
    lect = str(paso(p.get("lectura", "0.0"), lt))
    parpadea = p.get("parpadea") and (lt * 3) % 1 < 0.35
    d.rounded_rectangle([px - 128, base - 668, px + 98, base - 532], 12, fill=(20, 40, 25, 255))
    if not parpadea:
        f = font("Black", 84 if len(lect) <= 4 else 64)
        d.text((px - 15, base - 600), lect, font=f, fill=(90, 255, 130, 255), anchor="mm")
    if p.get("unidad"):
        d.text((px - 15, base - 700), p["unidad"], font=font("Black", 40), fill=WHITE + (255,), anchor="md")


def _flecha(d, a, b, col, w=8):
    d.line([a, b], fill=col, width=w)
    for (p0, p1) in ((a, b), (b, a)):
        ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
        for s in (-1, 1):
            d.line([p1, (p1[0] - 34 * math.cos(ang + s * 0.5), p1[1] - 34 * math.sin(ang + s * 0.5))], fill=col, width=w)


def _p_medidas(L, p, lt, k):
    """Flechas de largo, ancho y alto alrededor de una caja (aparecen una por una)."""
    x, y, w, h = p.get("x", 540), p.get("y", SU), p.get("w", 330), p.get("h", 300)
    d = ImageDraw.Draw(L); col = tuple(p.get("color", AMARILLO)) + (255,)
    f = font("Black", 52)
    pasos = [((x - w / 2, y + 50), (x + w / 2, y + 50), (x, y + 105), "LARGO"),
             ((x + w / 2 + 40, y - 20), (x + w / 2 + 130, y - h * 0.32), (x + w / 2 + 210, y - h * 0.08), "ANCHO"),
             ((x - w / 2 - 50, y), (x - w / 2 - 50, y - h), (x - w / 2 - 70, y - h - 50), "ALTO")]
    for i, (a, b, tpos, nombre) in enumerate(pasos):
        q = ease((k - i * p.get("cada", 0.9)) / 0.35)
        if q <= 0: continue
        bb = (a[0] + (b[0] - a[0]) * q, a[1] + (b[1] - a[1]) * q)
        _flecha(d, a, bb, col, 9)
        if q >= 1: texto_borde(L, tpos, nombre, f, col[:3], 1, borde=7)


def _p_cajas_caen(L, p, lt, k):
    """Avalancha: cajas que caen y se apilan (para Black Friday)."""
    rnd = random.Random(p.get("semilla", 3))
    n = p.get("n", 26); x0, x1 = p.get("x0", 80), p.get("x1", W - 80); base = p.get("y", SU + 30)
    alturas = {}
    d = ImageDraw.Draw(L)
    for i in range(n):
        w = rnd.randint(150, 260); h = int(w * rnd.uniform(0.6, 0.9))
        cx = rnd.uniform(x0 + w / 2, x1 - w / 2); col = int((cx - x0) / 140)
        t0 = i * p.get("cada", 0.07)
        fondo = alturas.get(col, base)
        if fondo - h < p.get("techo", 1000):                                   # columna muy alta: a la más baja
            ncol = int((x1 - x0) / 140) + 1
            col = max(range(ncol), key=lambda c: alturas.get(c, base)); fondo = alturas.get(col, base)
            cx = min(x1 - w / 2, max(x0 + w / 2, x0 + col * 140 + 70))
        alturas[col] = fondo - h * 0.85
        if k < t0: continue
        q = min(1, (k - t0) / 0.35)
        yy = -h - 100 + (fondo - h + 100 + h) * q * q
        ang = rnd.uniform(-14, 14) * (1 - q * 0.5)
        im = Image.new("RGBA", (w + 8, h + 8), (0, 0, 0, 0)); di = ImageDraw.Draw(im)
        tono = rnd.choice([(212, 158, 98), (196, 140, 82), (225, 175, 115)])
        di.rectangle([4, 4, w, h], fill=tono + (255,), outline=(96, 60, 30, 255), width=5)
        di.rectangle([w / 2 - w * 0.08, 4, w / 2 + w * 0.08, h], fill=(30, 95, 216, 255) if i % 3 else (255, 122, 26, 255))
        di.rectangle([w * 0.62, h * 0.58, w * 0.9, h * 0.84], fill=(255, 255, 255, 255))
        pegar_centro(L, im, cx, yy + h / 2, ang)


def _p_fuegos(L, p, lt, k):
    rnd = random.Random(p.get("semilla", 9)); d = ImageDraw.Draw(L)
    cols = [(255, 214, 64), (255, 90, 120), (90, 200, 255), (140, 255, 140), (255, 140, 40), (220, 120, 255)]
    for i in range(p.get("n", 7)):
        per = rnd.uniform(1.1, 1.6); fase = rnd.uniform(0, per)
        q = ((k + fase) % per) / per
        n_ciclo = int((k + fase) // per)
        r2 = random.Random(i * 97 + n_ciclo)
        cx, cy = r2.uniform(120, W - 120), r2.uniform(250, 1000)
        col = cols[r2.randrange(len(cols))]
        if q < 0.25:                                                          # cohete subiendo
            yy = 1400 - (1400 - cy) * (q / 0.25)
            d.ellipse([cx - 7, yy - 7, cx + 7, yy + 7], fill=col + (255,))
            continue
        qq = (q - 0.25) / 0.75; r = 40 + 230 * ease(qq); al = int(255 * (1 - qq))
        for j in range(16):
            a = j * math.pi / 8
            x1, y1 = cx + r * math.cos(a), cy + r * math.sin(a) + 60 * qq * qq
            x0, y0 = cx + r * 0.7 * math.cos(a), cy + r * 0.7 * math.sin(a) + 50 * qq * qq
            d.line([x0, y0, x1, y1], fill=col + (al,), width=7)
            d.ellipse([x1 - 6, y1 - 6, x1 + 6, y1 + 6], fill=(255, 255, 255, al))


def _p_bodega(L, p, lt, k):
    """Interior de la bodega del avión: paredes curvas, costillas, red de carga y ventanita con nubes."""
    d = ImageDraw.Draw(L)
    d.rectangle([0, 0, W, H], fill=(28, 40, 66, 255))
    for i in range(9):
        x = -60 + i * 150
        d.rectangle([x, 0, x + 26, H], fill=(44, 60, 92, 255))
    d.rectangle([0, SU + 10, W, H], fill=(52, 58, 72, 255))
    for i in range(14):
        d.line([i * 90, SU + 10, i * 90 - 200, H], fill=(70, 78, 95, 255), width=5)
    # ventanita redonda
    vx, vy, r = p.get("vx", 860), p.get("vy", 860), 120
    d.ellipse([vx - r - 18, vy - r * 1.3 - 18, vx + r + 18, vy + r * 1.3 + 18], fill=(200, 205, 215, 255))
    ven = Image.new("RGBA", (2 * r, int(2.6 * r)), (120, 190, 255, 255)); dv = ImageDraw.Draw(ven)
    for j in range(4):
        cx = (j * 170 - lt * 260) % (2 * r + 260) - 130; cy = 40 + j * 70
        for dx, dy, rr in [(0, 10, 34), (35, -4, 44), (78, 10, 32)]:
            dv.ellipse([cx + dx - rr, cy + dy - rr, cx + dx + rr, cy + dy + rr], fill=(255, 255, 255, 255))
    m = Image.new("L", ven.size, 0); ImageDraw.Draw(m).ellipse([0, 0, ven.width - 1, ven.height - 1], fill=255)
    ven.putalpha(m); L.alpha_composite(ven, (vx - r, int(vy - r * 1.3)))
    # red de carga a la izquierda
    for i in range(7):
        d.line([40 + i * 40, 760, 40 + i * 40 + 120, SU], fill=(230, 190, 80, 200), width=5)
        d.line([40 + i * 40 + 120, 760, 40 + i * 40, SU], fill=(230, 190, 80, 200), width=5)


def _p_ruta(L, p, lt, k):
    """Barra de ruta: MIAMI → LIMA → CASA con avioncito avanzando."""
    pasos = p.get("pasos", ["MIAMI", "LIMA", "🏠"]); y = p.get("y", 1640)
    x0, x1 = 140, W - 140; d = ImageDraw.Draw(L)
    q = num(p.get("progreso", [[0, 0], [3, 1]]), k)
    d.rounded_rectangle([x0, y - 10, x1, y + 10], 10, fill=(255, 255, 255, 120))
    d.rounded_rectangle([x0, y - 10, x0 + (x1 - x0) * q, y + 10], 10, fill=ORANGE + (255,))
    for i, s in enumerate(pasos):
        x = x0 + (x1 - x0) * i / (len(pasos) - 1)
        d.ellipse([x - 22, y - 22, x + 22, y + 22], fill=(ORANGE if q >= i / (len(pasos) - 1) - 1e-3 else (255, 255, 255)) + (255,),
                  outline=NAVY + (255,), width=5)
        if len(s) <= 2: pegar_centro(L, emoji(s, 70), x, y - 75)
        else: texto_borde(L, (x, y - 70), s, font("Black", 44), WHITE, 1, borde=6)
    pegar_centro(L, emoji("✈", 80), x0 + (x1 - x0) * q, y + 2, -10 if q < 1 else 0)


def _p_escritorio(L, p, lt, k):
    d = ImageDraw.Draw(L); y = p.get("y", SU - 140); x0, x1 = p.get("x0", 90), p.get("x1", 680)
    d.rectangle([x0, y, x1, y + 34], fill=(150, 95, 50, 255), outline=(80, 45, 20, 255), width=5)
    d.rectangle([x0 + 20, y + 34, x1 - 20, SU + 30], fill=(125, 78, 40, 255), outline=(80, 45, 20, 255), width=5)
    d.rounded_rectangle([x0 + 150, y + 90, x1 - 150, y + 180], 12, fill=(240, 230, 210, 255))
    d.text(((x0 + x1) / 2, y + 135), p.get("placa", "JEFE"), font=font("Black", 50), fill=NAVY + (255,), anchor="mm")


def _p_corazones(L, p, lt, k):
    rnd = random.Random(4)
    for i in range(p.get("n", 9)):
        per = rnd.uniform(1.2, 2.0); q = ((k + rnd.uniform(0, per)) % per) / per
        x = p.get("x", 540) + rnd.uniform(-260, 260) + 30 * math.sin(q * 6 + i)
        y = p.get("y", 1100) - 500 * q
        pegar_centro(L, emoji(p.get("e", "💖"), 70 + 30 * rnd.random()), x, y, 0, 1 - q)


def _p_destello(L, p, lt, k):
    a = max(0, 1 - k / p.get("dur", 0.35))
    if a > 0:
        ov = Image.new("RGBA", (W, H), (255, 255, 255, int(220 * a))); L.alpha_composite(ov)


def _p_ventana(L, p, lt, k):
    """Ventana de una casa (para la abuelita) con cortinas."""
    d = ImageDraw.Draw(L); x, y, w, h = p.get("x", 540), p.get("y", 900), p.get("w", 520), p.get("h", 560)
    d.rectangle([x - w / 2 - 30, y - h / 2 - 30, x + w / 2 + 30, y + h / 2 + 30], fill=(250, 240, 220, 255), outline=(120, 80, 40, 255), width=8)
    d.rectangle([x - w / 2, y - h / 2, x + w / 2, y + h / 2], fill=(120, 170, 230, 255))
    d.line([x, y - h / 2, x, y + h / 2], fill=(250, 240, 220, 255), width=16)
    d.line([x - w / 2, y, x + w / 2, y], fill=(250, 240, 220, 255), width=16)
    for s in (-1, 1):
        d.polygon([(x + s * (w / 2 + 40), y - h / 2 - 40), (x + s * (w / 2 - 120), y - h / 2 - 40),
                   (x + s * (w / 2 - 20), y + h / 2 + 40), (x + s * (w / 2 + 40), y + h / 2 + 40)], fill=(220, 60, 70, 255))


PROPS = {"emoji": _p_emoji, "texto": _p_texto, "cartel": _p_cartel, "burbuja": _p_burbuja,
         "comentario": lambda L, p, lt, k: _p_burbuja(L, p, lt, k, "comentario"),
         "balanza": _p_balanza, "medidas": _p_medidas, "cajas_caen": _p_cajas_caen, "fuegos": _p_fuegos,
         "bodega": _p_bodega, "ruta": _p_ruta, "escritorio": _p_escritorio, "corazones": _p_corazones,
         "destello": _p_destello, "ventana": _p_ventana}


def _props(L, e, lt, capa):
    for p in e.get("props", []):
        cap = p.get("capa", "frente" if p["tipo"] in ("cajas_caen", "destello", "escritorio") else "atras")
        if cap != capa: continue
        desde, hasta = p.get("desde", 0), p.get("hasta", 999)
        if desde <= lt < hasta:
            PROPS[p["tipo"]](L, p, lt, lt - desde)


def a_show(L, e, lt):
    capa = Image.new("RGBA", L.size, (0, 0, 0, 0))
    _props(capa, e, lt, "atras")
    actores = sorted(e.get("actores", []), key=lambda a: a.get("z", 0))
    for a in actores:
        _actor(capa, e, a, lt)
    _props(capa, e, lt, "frente")
    dx = dy = 0
    for d0, d1, amp in e.get("sacudir", []):
        if d0 <= lt < d1:
            dx += amp * math.sin(lt * 61); dy += amp * 0.7 * math.cos(lt * 47)
    L.alpha_composite(capa, (int(dx), int(dy)))


# ---------------------------------------------------------------- efectos de sonido (sintetizados, sin derechos)
def sfx_wav(lista, total, ruta, sr=44100):
    """lista = [(segundo, tipo), ...] -> escribe un wav mono con los efectos."""
    import numpy as np
    from scipy.io import wavfile
    out = np.zeros(int((total + 2) * sr), dtype=np.float32)
    rng = np.random.default_rng(11)

    def tono(f0, f1, dur, forma="sin", dec=6.0, vol=0.5):
        t = np.arange(int(dur * sr)) / sr
        f = f0 + (f1 - f0) * t / dur; fase = 2 * np.pi * np.cumsum(f) / sr
        w = np.sin(fase) if forma == "sin" else np.sign(np.sin(fase)) * 0.6
        return w * np.exp(-t * dec) * vol

    def ruido(dur, dec=8.0, vol=0.4):
        t = np.arange(int(dur * sr)) / sr
        return rng.standard_normal(len(t)) * np.exp(-t * dec) * vol

    for t0, tipo in lista:
        if tipo == "ding":
            w = np.concatenate([tono(1320, 1320, 0.18, dec=10), tono(1760, 1760, 0.5, dec=6)])
        elif tipo == "beep":
            w = np.concatenate([tono(1000, 1000, 0.1, "sq", 0, 0.3), np.zeros(int(0.08 * sr)), tono(1500, 1500, 0.22, "sq", 2, 0.3)])
        elif tipo == "boing":
            t = np.arange(int(0.6 * sr)) / sr
            w = np.sin(2 * np.pi * (180 + 120 * np.sin(t * 40) * np.exp(-t * 4)) * t) * np.exp(-t * 5) * 0.6
        elif tipo == "crash":
            w = ruido(1.2, 3.5, 0.5); w[:int(1.0 * sr)] += tono(70, 40, 1.0, dec=4, vol=0.8)
        elif tipo == "pop":
            w = tono(600, 1400, 0.09, dec=25, vol=0.5)
        elif tipo == "sello":
            w = tono(110, 50, 0.3, dec=14, vol=0.9)
            w[: int(0.06 * sr)] += ruido(0.06, 40, 0.5)
        elif tipo == "turbulencia":
            n = int(2.5 * sr); t = np.arange(n) / sr
            w = rng.standard_normal(n) * (0.25 + 0.2 * np.sin(t * 9)) * np.minimum(1, t * 4) * np.minimum(1, (2.5 - t) * 3)
            w = np.convolve(w, np.ones(60) / 60, mode="same") * 3
        elif tipo == "fuegos":
            w = np.zeros(int(3.0 * sr))
            for j in range(6):
                i0 = int(j * 0.45 * sr); b = ruido(0.5, 9, 0.45)
                w[i0:i0 + len(b)] += b[: len(w) - i0]
        elif tipo == "tada":
            w = np.zeros(int(1.2 * sr))
            for j, f in enumerate([523, 659, 784, 1047]):
                b = tono(f, f, 1.0 - j * 0.1, "sq", 2.2, 0.16); i0 = int(j * 0.07 * sr); w[i0:i0 + len(b)] += b
        elif tipo == "swish":
            n = int(0.3 * sr); t = np.arange(n) / sr
            w = rng.standard_normal(n) * np.sin(np.pi * t / 0.3) * 0.35
        elif tipo == "risas":
            w = np.concatenate([tono(420 + 40 * (j % 2), 380, 0.13, dec=8, vol=0.35) for j in range(6)])
        else:
            continue
        i = int(t0 * sr); j = min(len(out), i + len(w)); out[i:j] += w[: j - i]
    out = np.clip(out, -0.98, 0.98)
    wavfile.write(ruta, sr, (out * 32767).astype(np.int16))
