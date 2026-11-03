"""Personajes animados para los cortos de Jetport Courier (dibujados con Pillow, sin imágenes externas).

- caja(s, t, ...)  -> "Paqui", la cajita de cartón con cara, brazos y piernas (sprite RGBA).
- avion(s)         -> avión blanco con franja naranja y "JP" en la cola (sprite RGBA).
- pegar(L, spr, cx, base_y, sx, sy, ang) pega un sprite con estiramiento/aplastamiento y giro.
Todo se dibuja al doble de tamaño y se reduce, para que los bordes salgan suaves.
"""
import math
from PIL import Image, ImageDraw

CARTON = (212, 158, 98); CARTON_TOP = (232, 184, 124); CARTON_LADO = (172, 120, 66)
CONTORNO = (96, 60, 30); AZUL = (30, 95, 216); NAVY = (11, 37, 84); NARANJA = (255, 122, 26)
BLANCO = (255, 255, 255)
K = 2  # sobremuestreo


def _corazon(d, cx, cy, r, color):
    pts = []
    for i in range(40):
        a = 2 * math.pi * i / 40
        x = 16 * math.sin(a) ** 3
        y = 13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)
        pts.append((cx + x * r / 16, cy - y * r / 16))
    d.polygon(pts, fill=color)


def _brazo(d, u, x0, y0, ang, lado, largo=32):
    """ang en grados: 0 = brazo hacia abajo y afuera, 90 = horizontal, 160 = arriba."""
    a = math.radians(ang)
    x1 = x0 + lado * math.sin(a) * largo * u
    y1 = y0 + math.cos(a) * largo * u
    d.line([(x0, y0), (x1, y1)], fill=CONTORNO, width=int(7 * u))
    r = 8 * u
    d.ellipse([x1 - r, y1 - r, x1 + r, y1 + r], fill=BLANCO, outline=CONTORNO, width=int(2.5 * u))


PALETAS = {
    "paqui": (CARTON, CARTON_TOP, CARTON_LADO, AZUL),
    "amigo": ((186, 124, 70), (210, 150, 94), (146, 94, 48), NARANJA),   # el amigo: cartón más oscuro y cinta naranja
}

def caja(s, t, expr="feliz", brazos=(20, 20), mirar=(0.0, 0.0), parpadeo=True, piernas=0.0, sudor=0, color="paqui"):
    """Sprite de la cajita. s = ancho del frente en px. expr: feliz, abierta, nervioso, sorpresa, enamorado,
    silbando, panico, forzada, verguenza, alivio, risa, llanto. color: "paqui" o "amigo". sudor = cantidad de gotas de sudor (0 = según la expresión).
    brazos = (izq, der) en grados. piernas = fase de caminar/saltar (0 = quietas)."""
    u = s * K / 100.0
    Wc, Hc = int(190 * u), int(175 * u)
    img = Image.new("RGBA", (Wc, Hc), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    P = lambda x, y: (x * u, y * u)
    lw = int(3.2 * u)
    c_frente, c_tapa, c_lado, c_cinta = PALETAS[color]
    # piernas y zapatos
    for lx, fase in ((70, 0), (112, math.pi)):
        dy = 4 * math.sin(piernas + fase) if piernas else 0
        d.line([P(lx, 132), P(lx, 152 + dy)], fill=CONTORNO, width=int(7 * u))
        d.ellipse([*P(lx - 12, 146 + dy), *P(lx + 14, 160 + dy)], fill=NARANJA, outline=CONTORNO, width=int(2.5 * u))
    # brazos (detrás del cuerpo)
    _brazo(d, u, *P(44, 98), brazos[0], -1)
    _brazo(d, u, *P(150, 98), brazos[1], 1)
    # cuerpo: lado, tapa y frente
    d.polygon([P(140, 50), P(158, 34), P(158, 120), P(140, 136)], fill=c_lado, outline=CONTORNO, width=lw)
    d.polygon([P(40, 50), P(140, 50), P(158, 34), P(58, 34)], fill=c_tapa, outline=CONTORNO, width=lw)
    d.polygon([P(85, 50), P(97, 50), P(115, 34), P(103, 34)], fill=c_cinta)          # cinta en la tapa
    d.rounded_rectangle([*P(40, 50), *P(140, 136)], int(4 * u), fill=c_frente, outline=CONTORNO, width=lw)
    d.rectangle([*P(85, 51), *P(97, 64)], fill=c_cinta)                                # cinta que baja
    d.rounded_rectangle([*P(112, 112), *P(134, 130)], int(3 * u), fill=BLANCO)      # etiqueta sin datos
    d.polygon([P(117, 124), P(129, 118), P(124, 126)], fill=NARANJA)                # avioncito
    # cachetes
    for cx in (60, 120):
        if expr == "verguenza":
            d.ellipse([*P(cx - 13, 92), *P(cx + 13, 108)], fill=(240, 80, 90))
        else:
            d.ellipse([*P(cx - 8, 98), *P(cx + 8, 106)], fill=(232, 140, 112))
    # ojos
    cierra = parpadeo and (t % 2.9) < 0.12
    for ex in (72, 108):
        if expr == "risa":                                                         # ojos > <
            k = 1 if ex == 72 else -1
            d.line([P(ex - 9 * k, 75), P(ex + 8 * k, 82), P(ex - 9 * k, 89)], fill=NAVY, width=int(4.5 * u), joint="curve")
            continue
        if expr == "llanto":                                                       # ojos cerrados tristes + chorros
            d.arc([*P(ex - 10, 74), *P(ex + 10, 90)], 200, 340, fill=NAVY, width=int(4 * u))
            for j in range(3):
                yy = 86 + ((t * 3 + j / 3) % 1) * 46
                d.ellipse([*P(ex - 5, yy - 5), *P(ex + 5, yy + 6)], fill=(110, 190, 255))
            d.rectangle([*P(ex - 3, 86), *P(ex + 3, 134)], fill=(110, 190, 255, 255))
            continue
        if expr in ("verguenza", "alivio"):                                       # ojos cerrados ^^ o felices
            if expr == "verguenza":
                d.arc([*P(ex - 10, 78), *P(ex + 10, 94)], 200, 340, fill=NAVY, width=int(4 * u))
            else:
                d.arc([*P(ex - 10, 72), *P(ex + 10, 88)], 20, 160, fill=NAVY, width=int(4 * u))
            continue
        if expr == "forzada" and ex == 72 and (t % 0.7) < 0.18:                     # tic en el ojo
            d.line([P(ex - 11, 83), P(ex + 11, 83)], fill=NAVY, width=int(4 * u))
            continue
        if expr == "enamorado":
            _corazon(d, ex * u, 82 * u, 13 * u * (1 + 0.12 * math.sin(t * 12)), (235, 40, 80))
        elif cierra:
            d.arc([*P(ex - 10, 76), *P(ex + 10, 90)], 200, 340, fill=NAVY, width=int(3.5 * u))
        else:
            r = 15 if expr == "panico" else 13 if expr == "sorpresa" else 11
            d.ellipse([*P(ex - r, 82 - r * 1.15), *P(ex + r, 82 + r * 1.15)], fill=BLANCO, outline=NAVY, width=int(2.5 * u))
            px, py = ex + mirar[0] * 4, 84 + mirar[1] * 4
            rp = 3 if expr == "panico" else 4.5 if expr == "sorpresa" else 6
            d.ellipse([*P(px - rp, py - rp), *P(px + rp, py + rp)], fill=NAVY)
            d.ellipse([*P(px - 2.5 + 2, py - 4), *P(px + 2.5 + 2, py + 1)], fill=BLANCO)
    if expr in ("nervioso", "forzada"):                                              # cejas preocupadas
        d.line([P(62, 70), P(80, 63)], fill=NAVY, width=int(3 * u)); d.line([P(118, 70), P(100, 63)], fill=NAVY, width=int(3 * u))
    # boca
    if expr in ("feliz", "enamorado"):
        d.chord([*P(78, 96), *P(102, 116)], 0, 180, fill=(120, 25, 40), outline=NAVY, width=int(2 * u))
        d.ellipse([*P(85, 107), *P(95, 115)], fill=(255, 120, 130))
    elif expr == "abierta":
        d.chord([*P(74, 94), *P(106, 124)], 0, 180, fill=(120, 25, 40), outline=NAVY, width=int(2 * u))
        d.ellipse([*P(83, 110), *P(97, 121)], fill=(255, 120, 130))
    elif expr == "sorpresa":
        d.ellipse([*P(84, 100), *P(96, 116)], fill=(120, 25, 40), outline=NAVY, width=int(2 * u))
    elif expr == "nervioso":
        pts = [P(76 + i * 4, 108 + (3 if i % 2 else -3)) for i in range(8)]
        d.line(pts, fill=NAVY, width=int(3 * u))
    elif expr == "silbando":                                                         # boquita de silbido
        d.line([P(64, 66), P(80, 64)], fill=NAVY, width=int(3 * u)); d.line([P(100, 60), P(116, 64)], fill=NAVY, width=int(3 * u))
        d.ellipse([*P(96, 102), *P(106, 112)], fill=(120, 25, 40), outline=NAVY, width=int(2.5 * u))
    elif expr == "panico":                                                           # grito "¡aaah!"
        d.line([P(60, 62), P(80, 56)], fill=NAVY, width=int(3 * u)); d.line([P(120, 62), P(100, 56)], fill=NAVY, width=int(3 * u))
        h = 22 + 3 * math.sin(t * 30)
        d.ellipse([*P(80, 98), *P(100, 98 + h)], fill=(120, 25, 40), outline=NAVY, width=int(2 * u))
    elif expr == "forzada":                                                          # sonrisa forzada con dientes
        d.rounded_rectangle([*P(70, 98), *P(110, 114)], int(5 * u), fill=BLANCO, outline=NAVY, width=int(2.5 * u))
        d.line([P(70, 106), P(110, 106)], fill=NAVY, width=int(1.5 * u))
        for x in range(76, 110, 6):
            d.line([P(x, 98), P(x, 114)], fill=NAVY, width=int(1.5 * u))
    elif expr == "risa":
        h = 26 + 4 * math.sin(t * 28)
        d.chord([*P(72, 92), *P(108, 92 + h)], 0, 180, fill=(120, 25, 40), outline=NAVY, width=int(2 * u))
        d.ellipse([*P(82, 92 + h * 0.55), *P(98, 92 + h * 0.95)], fill=(255, 120, 130))
    elif expr == "llanto":
        h = 16 + 3 * math.sin(t * 25)
        d.chord([*P(76, 104), *P(104, 104 + 2 * h)], 180, 360, fill=(120, 25, 40), outline=NAVY, width=int(2 * u))
    elif expr == "verguenza":
        d.arc([*P(82, 100), *P(98, 112)], 20, 160, fill=NAVY, width=int(3 * u))
    elif expr == "alivio":
        d.chord([*P(74, 94), *P(106, 124)], 0, 180, fill=(120, 25, 40), outline=NAVY, width=int(2 * u))
        d.ellipse([*P(83, 110), *P(97, 121)], fill=(255, 120, 130))
    gotas = sudor or {"nervioso": 1, "forzada": 2, "panico": 3}.get(expr, 0)
    for g, (gx0, gy0) in enumerate([(136, 58), (46, 62), (128, 40)][:gotas]):     # gotas de sudor que caen
        k = (t * 1.4 + g * 0.37) % 1
        gx, gy = gx0, gy0 + 22 * k
        d.polygon([P(gx, gy - 9), P(gx - 6, gy + 2), P(gx + 6, gy + 2)], fill=(120, 200, 255))
        d.ellipse([*P(gx - 6, gy - 3), *P(gx + 6, gy + 8)], fill=(120, 200, 255))
    return img.resize((Wc // K, Hc // K), Image.LANCZOS)


def avion(s):
    """Avión de perfil mirando a la derecha. s = largo en px."""
    u = s * K / 300.0
    img = Image.new("RGBA", (int(310 * u), int(160 * u)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    P = lambda x, y: (x * u, y * u)
    lw = int(2.5 * u)
    d.polygon([P(150, 66), P(128, 30), P(146, 30), P(180, 66)], fill=(200, 215, 240), outline=NAVY, width=lw)  # ala lejana
    d.polygon([P(36, 66), P(14, 14), P(50, 14), P(84, 66)], fill=NAVY)                                       # cola
    d.rounded_rectangle([*P(18, 56), *P(290, 104)], int(24 * u), fill=BLANCO, outline=NAVY, width=lw)        # fuselaje
    d.ellipse([*P(240, 56), *P(300, 104)], fill=BLANCO, outline=NAVY, width=lw)
    d.rectangle([*P(240, 58), *P(268, 102)], fill=BLANCO)
    d.line([P(240, 57), P(268, 57)], fill=NAVY, width=lw); d.line([P(240, 103), P(268, 103)], fill=NAVY, width=lw)
    d.rectangle([*P(24, 86), *P(286, 93)], fill=NARANJA)                                                     # franja
    d.chord([*P(268, 62), *P(296, 84)], 270, 90, fill=NAVY)                                                  # cabina
    for x in range(90, 250, 19):
        d.ellipse([*P(x - 5, 67), *P(x + 5, 77)], fill=(80, 170, 255), outline=NAVY, width=int(1.5 * u))
    d.polygon([P(130, 92), P(96, 146), P(128, 146), P(184, 92)], fill=AZUL, outline=NAVY, width=lw)          # ala
    d.rounded_rectangle([*P(118, 104), *P(156, 120)], int(8 * u), fill=(220, 225, 235), outline=NAVY, width=lw)  # motor
    return img.resize((img.width // K, img.height // K), Image.LANCZOS)


def pegar(L, spr, cx, base_y, sx=1.0, sy=1.0, ang=0.0):
    """Pega el sprite con su borde inferior centrado en (cx, base_y). sx/sy estiran o aplastan; ang gira."""
    w, h = max(1, int(spr.width * sx)), max(1, int(spr.height * sy))
    im = spr.resize((w, h), Image.BILINEAR) if (w, h) != spr.size else spr
    if abs(ang) > 0.1:
        im = im.rotate(ang, Image.BICUBIC, expand=True)
    L.alpha_composite(im, (int(cx - im.width / 2), int(base_y - im.height + (im.height - h) / 2)))


def sombra(L, cx, y, ancho, a=0.35):
    capa = Image.new("RGBA", (int(ancho) + 4, int(ancho * 0.22) + 4), (0, 0, 0, 0))
    ImageDraw.Draw(capa).ellipse([2, 2, capa.width - 2, capa.height - 2], fill=(0, 0, 0, int(255 * a)))
    L.alpha_composite(capa, (int(cx - capa.width / 2), int(y - capa.height / 2)))
