"""Miniatura estilo "miniatura de YouTube" (mucho texto, burbujas y caras exageradas) para Paqui tracking.

Uso:  python3 generador/miniatura_intensa.py videos/paqui-tracking_miniatura.jpg

Fondo y personajes salen de la escena "show" (video.py): la clienta intensa reclamando con el celular
y Paqui sudando. Encima van las burbujas de preguntas, el título grande y el logo en tarjeta blanca.
"""
import json
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
NAVY = (11, 37, 84); NAVY_OSC = (14, 18, 40); ORANGE = (255, 122, 26); BLANCO = (255, 255, 255)
AMARILLO = (255, 222, 40); ROJO = (226, 30, 44)
FUENTES = "/usr/share/fonts/opentype/inter/"


def f(tam, peso="Black", italic=True):
    nombre = f"InterDisplay-{peso}Italic.otf" if italic else f"Inter-{peso}.otf"
    return ImageFont.truetype(FUENTES + nombre, int(tam))


def emoji(ch, size):
    fe = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((80, 80), ch, font=fe, embedded_color=True, anchor="mm")
    im = im.crop(im.getbbox())
    r = size / max(im.size)
    return im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)


def escena():
    """Cuadro de la escena 'show' con la clienta y Paqui (sin barra ni logo del video: se tapan luego)."""
    esc = {"tipo": "anim", "escena": "show", "dur": 3, "estilo_fondo": "rayos", "transicion": "ninguna",
           "actores": [
               {"quien": "mujer", "x": 380, "y": 1420, "s": 152, "expr": "enojada", "brazos": "reclama", "obj": "📱", "ropa": "roja"},
               {"quien": "paqui", "x": 850, "y": 1235, "s": 285, "expr": "panico", "brazos": "agita", "mov": "quieto", "mirar": [-1, 0]}],
           "props": []}
    with tempfile.TemporaryDirectory() as tmp:
        g = os.path.join(tmp, "g.json"); png = os.path.join(tmp, "f.png")
        json.dump({"cierre": False, "musica_semilla": 1, "escenas": [esc]}, open(g, "w"), ensure_ascii=False)
        subprocess.run([sys.executable, os.path.join(AQUI, "video.py"), g, png, "1.37"], check=True, stdout=subprocess.DEVNULL)
        return Image.open(png).convert("RGBA")


def burbuja(im, cx, cy, partes, tam, cola, ang=0, fondo=BLANCO):
    """Burbuja de diálogo con texto en dos colores. partes = [[("¿Ya ", NAVY), ("llegó?", ROJO)], ...] (renglones)."""
    fn = f(tam, "ExtraBold")
    anchos = [sum(fn.getlength(t) for t, _ in r) for r in partes]
    lh = tam * 1.12
    w = int(max(anchos) + 90); h = int(lh * len(partes) + 60)
    pad = 120
    L = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    caja = [pad, pad, pad + w, pad + h]
    tx, ty = cola                                            # punta de la cola, relativa al centro de la burbuja
    px, py = pad + w / 2 + tx, pad + h / 2 + ty
    bx = pad + w / 2 + max(-w / 3, min(w / 3, tx * 0.4))
    base_y = pad + h - 4 if ty > 0 else pad + 4
    sombra = Image.new("RGBA", L.size, (0, 0, 0, 0)); ds = ImageDraw.Draw(sombra)
    ds.ellipse([caja[0] + 10, caja[1] + 14, caja[2] + 10, caja[3] + 14], fill=(0, 0, 0, 120))
    L.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(10)))
    d.polygon([(bx - 40, base_y), (bx + 40, base_y), (px, py)], fill=fondo, outline=NAVY_OSC)
    d.ellipse(caja, fill=fondo, outline=NAVY_OSC, width=7)
    d.polygon([(bx - 34, base_y), (bx + 34, base_y), (px, py)], fill=fondo)
    d.line([(bx - 40, base_y), (px, py)], fill=NAVY_OSC, width=7); d.line([(bx + 40, base_y), (px, py)], fill=NAVY_OSC, width=7)
    y = pad + h / 2 - lh * len(partes) / 2 + lh / 2
    for r, aw in zip(partes, anchos):
        x = pad + w / 2 - aw / 2
        for t, col in r:
            d.text((x, y), t, font=fn, fill=col, anchor="lm"); x += fn.getlength(t)
        y += lh
    L = L.rotate(ang, resample=Image.BICUBIC, expand=False)
    im.alpha_composite(L, (int(cx - L.width / 2), int(cy - L.height / 2)))


def rayitas(d, cx, cy, ang0, n=3, largo=70, col=ROJO):
    """Rayitas de grito (!!!) saliendo de un punto."""
    import math
    for i in range(n):
        a = math.radians(ang0 + (i - (n - 1) / 2) * 24)
        x0, y0 = cx + math.cos(a) * 30, cy - math.sin(a) * 30
        x1, y1 = cx + math.cos(a) * (30 + largo), cy - math.sin(a) * (30 + largo)
        d.line([(x0, y0), (x1, y1)], fill=NAVY_OSC, width=22); d.line([(x0, y0), (x1, y1)], fill=col, width=13)


def banda(im, y0, y1, col, inclin=-3.0, margen=40):
    """Franja de color tipo brochazo, algo inclinada."""
    L = Image.new("RGBA", (W + 400, y1 - y0 + 200), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.polygon([(margen + 200, 100 + 10), (W + 200 - margen, 100), (W + 200 - margen + 20, 100 + (y1 - y0)), (margen + 200 - 15, 100 + (y1 - y0) + 8)],
              fill=col, outline=NAVY_OSC, width=8)
    L = L.rotate(inclin, resample=Image.BICUBIC)
    im.alpha_composite(L, (-200, y0 - 100))


def titulo(im, cx, cy, txt, tam, col, borde=14, sombra=True, ang=-3.0, ancho_max=W - 90):
    while f(tam).getlength(txt) > ancho_max and tam > 40: tam -= 4
    fn = f(tam)
    L = Image.new("RGBA", (W + 300, int(tam * 1.8)), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    c = (L.width / 2, L.height / 2)
    if sombra:
        d.text((c[0] + 10, c[1] + 12), txt, font=fn, fill=NAVY_OSC, anchor="mm", stroke_width=borde, stroke_fill=NAVY_OSC)
    d.text(c, txt, font=fn, fill=col, anchor="mm", stroke_width=borde, stroke_fill=BLANCO if col != BLANCO else NAVY_OSC)
    if col != BLANCO and borde:                             # borde doble: blanco por dentro, oscuro por fuera
        d2 = Image.new("RGBA", L.size, (0, 0, 0, 0)); dd = ImageDraw.Draw(d2)
        dd.text(c, txt, font=fn, fill=col, anchor="mm", stroke_width=borde + 7, stroke_fill=NAVY_OSC)
        d2.alpha_composite(L); L = d2
    L = L.rotate(ang, resample=Image.BICUBIC)
    im.alpha_composite(L, (int(cx - L.width / 2), int(cy - L.height / 2)))


def main(salida):
    im = escena()
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 16], fill=(0, 0, 0, 0))           # se tapa la barra de progreso con el fondo de abajo
    top = im.crop((0, 20, W, 40)).resize((W, 20)); im.paste(top, (0, 0))

    # avioncito Miami -> Lima arriba a la derecha (el paquete "sigue volando")
    av = emoji("✈️", 150).rotate(8, expand=True, resample=Image.BICUBIC)
    for i in range(5):
        d.ellipse([560 + i * 52, 170 + i * 9, 590 + i * 52, 192 + i * 9], fill=(255, 255, 255, 180))
    im.alpha_composite(av, (840, 105))

    # burbujas de la clienta
    burbuja(im, 300, 300, [[("¿Ya ", NAVY), ("llegó?", ROJO)]], 78, (60, 190), ang=4)
    burbuja(im, 760, 420, [[("¿Dónde está", NAVY)], [("mi ", NAVY), ("paquete?", ROJO)]], 64, (-260, 150), ang=-3)
    burbuja(im, 255, 545, [[("¿Y ", NAVY), ("ahorita?", ROJO)]], 62, (120, 120), ang=-4)
    burbuja(im, 800, 640, [[("¿Ya salió de ", NAVY)], [("Miami?", ROJO)]], 50, (-200, 110), ang=3)

    d = ImageDraw.Draw(im)
    rayitas(d, 560, 830, 25, n=3, largo=75)                 # gritos junto a la cabeza
    rayitas(d, 215, 790, 150, n=3, largo=60)

    # contador de mensajes en el celular
    bx, by = 160, 925
    d.ellipse([bx - 54, by - 54, bx + 54, by + 54], fill=ROJO, outline=BLANCO, width=7)
    d.text((bx, by), "50", font=f(58, "Black", False), fill=BLANCO, anchor="mm")

    # título abajo (dentro de la zona segura 3:4 del feed)
    banda(im, 1255, 1395, AMARILLO, inclin=-3)
    titulo(im, W / 2, 1322, "LA CLIENTA", 128, NAVY_OSC, borde=0, sombra=False)
    titulo(im, W / 2 + 70, 1500, "INTENSA", 250, ROJO, borde=10, ancho_max=W - 250)
    em = emoji("😱", 170).rotate(10, expand=True, resample=Image.BICUBIC)
    im.alpha_composite(em, (-6, 1400))
    banda(im, 1610, 1730, ROJO, inclin=-3, margen=90)
    titulo(im, W / 2 - 40, 1668, "vs. PAQUI", 96, AMARILLO, borde=0, sombra=False)
    caja = emoji("📦", 130).rotate(-12, expand=True, resample=Image.BICUBIC)
    im.alpha_composite(caja, (W - 220, 1600))

    # logo sobre tarjeta blanca
    logo = Image.open(os.path.join(AQUI, "logo_horizontal.png")).convert("RGBA")
    lw = 330; logo = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    x0 = (W - lw) // 2 - 22; y0 = 1765
    d.rounded_rectangle([x0 - 4, y0 + 6, x0 + lw + 48, y0 + logo.height + 30], 26, fill=(0, 0, 0, 90))
    d.rounded_rectangle([x0, y0, x0 + lw + 44, y0 + logo.height + 24], 26, fill=BLANCO, outline=NAVY_OSC, width=4)
    im.alpha_composite(logo, (x0 + 22, y0 + 12))

    # etiqueta de la serie
    et = "PAQUI #5"; fe = f(50, "Black", False); tw = fe.getlength(et)
    d.rounded_rectangle([50, 40, 50 + tw + 60, 40 + 82], 41, fill=ORANGE, outline=NAVY_OSC, width=6)
    d.text((50 + 30 + tw / 2, 81), et, font=fe, fill=BLANCO, anchor="mm")

    im.convert("RGB").save(salida, quality=92)
    print(salida)


if __name__ == "__main__":
    main(sys.argv[1])
