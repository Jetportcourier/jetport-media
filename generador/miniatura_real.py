"""Miniaturas "adultas" para los videos: foto REAL del almacén/equipo de fondo, título grande con palabras
resaltadas, recuadro con un cuadro del video (Paqui) y logo en tarjeta blanca.

Uso:  python3 generador/miniatura_real.py portadas/miniaturas_reales.json [nombre]   (sin nombre: todas)

Cada entrada del JSON:
{"nombre": "paqui-tracking", "salida": "videos/paqui-tracking_miniatura.jpg",
 "fondo": "material/foto_almacen_05.jpg" | {"video": "material/x.mp4", "t": 1.5},
 "foco": [0.5, 0.5], "zoom": 1.0, "oscuro": 0.75,
 "titulo": [["¿Y SI MI PAQUETE", "blanco"], ["SE PIERDE?", "amarillo"]],   (colores: blanco|amarillo|rojo|naranja; "caja_X" = texto oscuro sobre franja X)
 "y_titulo": 250, "tam_titulo": 150,
 "sub": "El seguimiento empieza en Miami",          (opcional: renglón chico en tarjeta)
 "pip": {"video": "videos/paqui-x.mp4", "t": 2.0, "x": 770, "y": 1250, "w": 420, "ang": 4},
 "chat": ["¿Ya llegó?", ...], "chat_y": 640,          (opcional: tarjeta tipo chat del celular)
 "sello": ["¡OJO!", "rojo", x, y, ang]}               (opcional: sello/etiqueta)
Las fotos reales nunca deben mostrar etiquetas legibles (ver material/LEEME.md).
"""
import json
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1080, 1920
OSC = (10, 14, 30)
COL = {"blanco": (255, 255, 255), "amarillo": (255, 214, 0), "rojo": (232, 36, 46), "naranja": (255, 122, 26),
       "azul": (24, 92, 200), "verde": (40, 190, 90)}
F = "/usr/share/fonts/opentype/inter/"


def fuente(tam, peso="Black"):
    return ImageFont.truetype(F + f"InterDisplay-{peso}.otf", int(tam))


def ruta(p):
    if os.path.isabs(p) or os.path.exists(os.path.join(RAIZ, p)):
        return os.path.join(RAIZ, p)
    return os.path.join("/mnt/project-files", p)


def cuadro_video(video, t):
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "c.png")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(t), "-i", ruta(video), "-frames:v", "1", out], check=True)
        return Image.open(out).convert("RGB")


def fondo(spec):
    src = spec["fondo"]
    im = cuadro_video(src["video"], src.get("t", 1.0)) if isinstance(src, dict) else Image.open(ruta(src)).convert("RGB")
    z = spec.get("zoom", 1.0); fx, fy = spec.get("foco", [0.5, 0.5])
    esc = max(W / im.width, H / im.height) * z
    im = im.resize((int(im.width * esc), int(im.height * esc)), Image.LANCZOS)
    x0 = int(min(max(0, fx * im.width - W / 2), im.width - W)); y0 = int(min(max(0, fy * im.height - H / 2), im.height - H))
    im = im.crop((x0, y0, x0 + W, y0 + H))
    if spec.get("bajar"):                                   # bajar la foto (p. ej. para que el título no tape la cara)
        b = spec["bajar"]; nuevo = Image.new("RGB", (W, H), OSC); nuevo.paste(im.crop((0, 0, W, H - b)), (0, b))
        tira = im.crop((0, 0, W, 8)).resize((W, b)).filter(ImageFilter.GaussianBlur(30))
        nuevo.paste(Image.blend(tira, Image.new("RGB", (W, b), OSC), 0.5), (0, 0)); im = nuevo
    if esc > 1.4:                                           # fotos chicas (480p): suavizar y luego dar nitidez
        im = im.filter(ImageFilter.GaussianBlur(1.2)).filter(ImageFilter.UnsharpMask(4, 80, 2))
    im = ImageEnhance.Contrast(im).enhance(1.15); im = ImageEnhance.Color(im).enhance(1.12)
    im = ImageEnhance.Brightness(im).enhance(spec.get("oscuro", 0.78))
    im = im.convert("RGBA")
    # degradados oscuros arriba (título) y abajo (logo) + viñeta
    g = Image.new("L", (1, H))
    for y in range(H):
        a = 0
        if y < 900: a = int(215 * (1 - y / 900) ** 1.3)
        if y > 1450: a = max(a, int(200 * ((y - 1450) / 470) ** 1.5))
        g.putpixel((0, y), a)
    capa = Image.new("RGBA", (W, H), OSC + (0,)); capa.putalpha(g.resize((W, H)))
    im.alpha_composite(capa)
    vin = Image.new("L", (W, H), 0); dv = ImageDraw.Draw(vin)
    dv.ellipse([-300, -200, W + 300, H + 200], fill=255)
    vin = vin.filter(ImageFilter.GaussianBlur(160))
    oscura = Image.new("RGBA", (W, H), (0, 0, 0, 150)); oscura.putalpha(Image.eval(vin, lambda v: int((255 - v) * 0.6)))
    im.alpha_composite(oscura)
    return im


def sombra_de(L, rad=14, alfa=170, dx=10, dy=14):
    s = Image.new("RGBA", L.size, (0, 0, 0, 0)); s.putalpha(L.getchannel("A").point(lambda v: alfa if v > 10 else 0))
    s = s.filter(ImageFilter.GaussianBlur(rad))
    out = Image.new("RGBA", (L.width + abs(dx), L.height + abs(dy)), (0, 0, 0, 0))
    out.alpha_composite(s, (max(0, dx), max(0, dy))); out.alpha_composite(L, (0, 0))
    return out


def titulo(im, lineas, y, tam0):
    for txt, col in lineas:
        caja = col.startswith("caja_")
        c = COL[col[5:] if caja else col]
        tam = tam0 * (0.82 if caja else 1.0)
        while fuente(tam).getlength(txt) > W - (150 if caja else 90) and tam > 50: tam -= 3
        fn = fuente(tam); tw = fn.getlength(txt)
        h = int(tam * 1.18)
        L = Image.new("RGBA", (W, h + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        cy = (h + 40) / 2
        if caja:
            d.rectangle([W / 2 - tw / 2 - 30, cy - tam * 0.58, W / 2 + tw / 2 + 30, cy + tam * 0.62], fill=c)
            d.text((W / 2, cy + tam * 0.03), txt, font=fn, fill=OSC if col != "caja_rojo" else (255, 255, 255), anchor="mm")
            L = L.rotate(-2, resample=Image.BICUBIC)
        else:
            d.text((W / 2, cy), txt, font=fn, fill=c, anchor="mm", stroke_width=max(6, int(tam / 14)), stroke_fill=OSC)
        L = sombra_de(L, rad=10, alfa=150, dx=0, dy=8)
        im.alpha_composite(L, (0, int(y - 20)))
        y += h * (1.08 if caja else 0.95)
    return y


def pip(im, p):
    fr = cuadro_video(p["video"], p.get("t", 2.0))
    w = p.get("w", 420); recorte = p.get("recorte")             # recorte: [x0, y0, x1, y1] en 0..1 del cuadro
    if recorte:
        fr = fr.crop((int(recorte[0] * fr.width), int(recorte[1] * fr.height), int(recorte[2] * fr.width), int(recorte[3] * fr.height)))
    h = int(fr.height * w / fr.width); fr = fr.resize((w, h), Image.LANCZOS).convert("RGBA")
    b = 12
    L = Image.new("RGBA", (w + 2 * b, h + 2 * b), (255, 255, 255, 255)); L.alpha_composite(fr, (b, b))
    m = Image.new("L", L.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, L.width - 1, L.height - 1], 26, fill=255); L.putalpha(m)
    L = L.rotate(p.get("ang", 0), expand=True, resample=Image.BICUBIC)
    L = sombra_de(L)
    im.alpha_composite(L, (int(p["x"] - L.width / 2), int(p["y"] - L.height / 2)))


def chat(im, mensajes, y0, x0=None):
    """Tarjeta tipo chat del celular con los mensajes de la clienta (genérica, sin marcas de apps)."""
    fn = fuente(52, "Bold"); fh = fuente(30, "SemiBold")
    w = int(max(fn.getlength(t) for t, _ in mensajes) + 210); x0 = x0 if x0 is not None else W - w - 50
    alto = 40 + len(mensajes) * 104 + 20
    L = Image.new("RGBA", (w, alto), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle([0, 0, w - 1, alto - 1], 40, fill=(245, 246, 250, 238))
    y = 30
    for i, (txt, hora) in enumerate(mensajes):
        tw = fn.getlength(txt)
        bx1 = w - 30; bx0 = bx1 - tw - 150
        verde = (220, 248, 198) if i < len(mensajes) - 1 else (255, 214, 0)
        d.rounded_rectangle([bx0, y, bx1, y + 88], 26, fill=verde)
        d.text((bx0 + 26, y + 44), txt, font=fn, fill=OSC, anchor="lm")
        d.text((bx1 - 18, y + 70), hora, font=fh, fill=(90, 100, 110), anchor="rs")
        y += 104
    L = L.rotate(-3, expand=True, resample=Image.BICUBIC)
    im.alpha_composite(sombra_de(L), (x0, y0))


def sello(im, txt, col, x, y, ang):
    fn = fuente(64); tw = fn.getlength(txt)
    L = Image.new("RGBA", (int(tw + 80), 110), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle([0, 0, L.width - 1, 109], 22, fill=COL[col])
    d.text((L.width / 2, 57), txt, font=fn, fill=(255, 255, 255) if col != "amarillo" else OSC, anchor="mm")
    L = L.rotate(ang, expand=True, resample=Image.BICUBIC)
    im.alpha_composite(sombra_de(L, rad=8, dx=6, dy=8), (int(x - L.width / 2), int(y - L.height / 2)))


def logo(im):
    lg = Image.open(os.path.join(RAIZ, "generador", "logo_horizontal.png")).convert("RGBA")
    lw = 320; lg = lg.resize((lw, int(lg.height * lw / lg.width)), Image.LANCZOS)
    card = Image.new("RGBA", (lw + 44, lg.height + 24), (0, 0, 0, 0)); d = ImageDraw.Draw(card)
    d.rounded_rectangle([0, 0, card.width - 1, card.height - 1], 24, fill=(255, 255, 255, 255))
    card.alpha_composite(lg, (22, 12))
    im.alpha_composite(sombra_de(card, rad=10, dx=0, dy=8), ((W - card.width) // 2, H - card.height - 60))


def hacer(spec):
    im = fondo(spec)
    if spec.get("pip"): pip(im, spec["pip"])
    if spec.get("chat"): chat(im, spec["chat"], spec.get("chat_y", 650), spec.get("chat_x"))
    y = titulo(im, spec["titulo"], spec.get("y_titulo", 240), spec.get("tam_titulo", 150))
    if spec.get("sub"):
        fn = fuente(52, "ExtraBold"); tw = fn.getlength(spec["sub"])
        d = ImageDraw.Draw(im); ys = spec.get("y_sub", y + 20)
        d.rounded_rectangle([W / 2 - tw / 2 - 34, ys, W / 2 + tw / 2 + 34, ys + 88], 44, fill=(255, 255, 255, 235))
        d.text((W / 2, ys + 45), spec["sub"], font=fn, fill=OSC, anchor="mm")
    if spec.get("sello"): sello(im, *spec["sello"])
    logo(im)
    salida = os.path.join(RAIZ, spec["salida"])
    im.convert("RGB").save(salida, quality=90)
    print(salida)


if __name__ == "__main__":
    specs = json.load(open(sys.argv[1]))
    for s in specs:
        if len(sys.argv) < 3 or s["nombre"] in sys.argv[2:]:
            hacer(s)
