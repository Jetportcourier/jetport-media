"""Portadas "PAQUI #N" para los sketches hablados.

Uso:  python3 generador/portada.py portadas/archivo.json videos/salida_portada.jpg

JSON:
{"num": 4,                                  (sale como etiqueta "PAQUI #4"; omitir para no ponerla)
 "titulo": [["¡ME PESARON", "blanco"], ["DOS VECES!", "amarillo"]],   (1 a 4 renglones grandes)
 "abajo": ["¡¿QUÉ?!", "naranja"],           (opcional: golpe de texto abajo)
 "ocultar": ["cartel"],                     (opcional: quitar utilería que tapa el título)
 "t": 0.6,                                  (segundo de la escena que se usa de fondo)
 "escena": { ...escena "show"... }}   o bien  "guion": "guiones/x.json", "escena_n": 0
Las líneas, voces y efectos de la escena se quitan solos.
El fondo se dibuja con video.py (un cuadro de esa escena) y encima van los textos con borde.
"""
import json
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
COLORES = {"blanco": (255, 255, 255), "amarillo": (255, 226, 64), "naranja": (255, 122, 26),
           "rojo": (255, 70, 70), "celeste": (120, 210, 255), "verde": (110, 230, 120)}
NAVY_OSC = (20, 20, 40)


def f(s):
    return ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Black.otf", int(s))


def texto(d, xy, s, tam, col, borde):
    d.text(xy, s, font=f(tam), fill=col, anchor="mm", stroke_width=borde, stroke_fill=NAVY_OSC)


def main(spec_path, salida):
    spec = json.load(open(spec_path))
    if "guion" in spec:                     # o tomar la escena N de un guion existente
        spec["escena"] = json.load(open(spec["guion"]))["escenas"][spec.get("escena_n", 0)]
    esc = dict(spec["escena"]); esc.setdefault("tipo", "anim"); esc.setdefault("escena", "show")
    esc.setdefault("dur", 3); esc["transicion"] = "ninguna"
    for k in ("lineas", "voces", "sfx"): esc.pop(k, None)
    if spec.get("ocultar"):                 # tipos de utilería que estorban al título (p. ej. ["cartel", "texto"])
        esc["props"] = [p for p in esc.get("props", []) if p["tipo"] not in spec["ocultar"]]
    with tempfile.TemporaryDirectory() as tmp:
        g = os.path.join(tmp, "g.json"); png = os.path.join(tmp, "f.png")
        json.dump({"cierre": False, "escenas": [esc]}, open(g, "w"), ensure_ascii=False)
        subprocess.run([sys.executable, os.path.join(AQUI, "video.py"), g, png, str(spec.get("t", 0.8))],
                       check=True, stdout=subprocess.DEVNULL)
        im = Image.open(png).convert("RGB")
    d = ImageDraw.Draw(im)
    W = im.width
    # títulos: tamaño que entre en el ancho
    lineas = spec["titulo"]; y = spec.get("y_titulo", 230)
    for txt, col in lineas:
        tam = 150
        while f(tam).getlength(txt) > W - 120 and tam > 60: tam -= 4
        texto(d, (W / 2, y + tam * 0.5), txt, tam, COLORES.get(col, col if isinstance(col, tuple) else (255, 255, 255)), 12)
        y += tam * 1.0
    if spec.get("abajo"):
        txt, col = spec["abajo"]; tam = 150
        while f(tam).getlength(txt) > W - 140 and tam > 60: tam -= 4
        texto(d, (W / 2, spec.get("y_abajo", 1620)), txt, tam, COLORES.get(col, (255, 122, 26)), 12)
    if spec.get("num") is not None:
        et = f"PAQUI #{spec['num']}"; fe = f(52); tw = fe.getlength(et)
        x0, y0 = 60, 70
        d.rounded_rectangle([x0, y0, x0 + tw + 60, y0 + 84], 42, fill=(255, 122, 26), outline=NAVY_OSC, width=6)
        d.text((x0 + 30 + tw / 2, y0 + 42), et, font=fe, fill=(255, 255, 255), anchor="mm")
    im.save(salida, quality=92)
    print(salida)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
