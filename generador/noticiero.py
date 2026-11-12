"""JP NOTICIAS: personajes y utilería del noticiero animado (se usan dentro de la escena "show").

Personajes nuevos (actores de "show"):
  "lucho"  -> Don Lucho, presentador del noticiero (señor con bigote, terno azul y corbata naranja).
              brazos: mesa | habla | senala (a la pantalla) | golpe (golpea la mesa) | papeles | arriba | saluda
              expr: feliz | serio | sorpresa | risa | guino ; "acc": ["lentes"]
  "jetito" -> Jetito, el avioncito reportero (blanco con franjas azul/naranja, micrófono en el ala).
              expr: feliz | sorpresa | panico | risa ; "dir": 1 mira a la derecha, -1 a la izquierda.
  "vale"   -> Vale, la reportera de aduanas (joven, cola de caballo, chaleco naranja y casco blanco, tablet).
              brazos: abajo | habla | tablet | senala | arriba | pulgar ; expr: feliz | sorpresa | risa | guino
Utilería ("props"): estudio (fondo del set) | pantalla (pantalla gigante con emoji + título) | mesa (mesa JP NOTICIAS)
  | zocalo (banda inferior: "tag" + "texto") | ticker (cinta que corre) | en_vivo ("lugar") | sirena (luces de
  último minuto) | almacen (almacén en Miami) | intro (logo animado JP NOTICIAS) | aduana_set (oficina de aduana en Lima).
Efectos de sonido nuevos: "sirena", "jingle" (cortina del noticiero), "tecleo".
"""
import math
from PIL import Image, ImageDraw

W, H = 1080, 1920
NAVY = (11, 37, 84); ORANGE = (255, 122, 26); WHITE = (255, 255, 255); AMARILLO = (255, 214, 64)
ROJO = (220, 30, 45); AZUL = (30, 99, 200)
OUT = (45, 30, 30, 255)


def _sh():
    import show as sh
    return sh


# =============================================================== DON LUCHO (presentador)
PIEL_L, PELO_L, TERNO = (236, 188, 150), (120, 118, 125), (22, 44, 98)


def lucho(L, x, y, s, lt, habla, expr, br, k, acc=()):
    """y = borde inferior del torso (queda tapado por la mesa); s = escala (100 = cabeza de radio ~100)."""
    u = s / 100; d = ImageDraw.Draw(L); lw = max(3, int(5 * u))
    hx, hy = x, y - 340 * u
    # ---- torso: terno, camisa y corbata
    d.rounded_rectangle([x - 185 * u, y - 235 * u, x + 185 * u, y + 80 * u], int(80 * u), fill=TERNO + (255,), outline=OUT, width=lw)
    d.polygon([(hx - 62 * u, y - 238 * u), (hx + 62 * u, y - 238 * u), (hx, y - 95 * u)], fill=WHITE + (255,))
    d.polygon([(hx - 62 * u, y - 238 * u), (hx - 8 * u, y - 120 * u), (hx - 95 * u, y - 150 * u)], fill=(14, 30, 72, 255))   # solapas
    d.polygon([(hx + 62 * u, y - 238 * u), (hx + 8 * u, y - 120 * u), (hx + 95 * u, y - 150 * u)], fill=(14, 30, 72, 255))
    d.polygon([(hx - 16 * u, y - 232 * u), (hx + 16 * u, y - 232 * u), (hx + 10 * u, y - 206 * u), (hx - 10 * u, y - 206 * u)], fill=(220, 95, 10, 255))
    d.polygon([(hx - 10 * u, y - 206 * u), (hx + 10 * u, y - 206 * u), (hx + 24 * u, y - 105 * u), (hx, y - 80 * u), (hx - 24 * u, y - 105 * u)], fill=ORANGE + (255,))
    d.line([hx - 6 * u, y - 180 * u, hx + 14 * u, y - 160 * u], fill=(255, 190, 120, 255), width=max(2, int(4 * u)))
    # pin JP en la solapa
    px, py = x + 105 * u, y - 165 * u
    d.ellipse([px - 20 * u, py - 20 * u, px + 20 * u, py + 20 * u], fill=WHITE + (255,), outline=ORANGE + (255,), width=max(2, int(4 * u)))
    d.polygon([(px - 11 * u, py + 5 * u), (px + 12 * u, py - 9 * u), (px + 2 * u, py + 9 * u)], fill=ORANGE + (255,))
    # ---- brazos
    hd, hi = (x - 160 * u, y - 185 * u), (x + 160 * u, y - 185 * u)
    golpe = abs(math.sin(k * 7))
    if br == "habla": md, mi = (x - 230 * u, y - 250 * u - 45 * u * abs(math.sin(k * 5))), (x + 150 * u, y - 10 * u)
    elif br == "senala": md, mi = (x - 270 * u, y - 520 * u + 8 * u * math.sin(k * 6)), (x + 150 * u, y - 10 * u)
    elif br == "golpe": md, mi = (x - 170 * u, y - 10 * u - 150 * u * golpe), (x + 170 * u, y - 10 * u - 150 * u * golpe)
    elif br == "papeles": md, mi = (x - 70 * u, y - 40 * u), (x + 70 * u, y - 40 * u)
    elif br == "arriba": md, mi = (x - 170 * u, y - 560 * u), (x + 170 * u, y - 560 * u)
    elif br == "saluda": md, mi = (x - 250 * u + 30 * u * math.sin(k * 12), y - 480 * u), (x + 150 * u, y - 10 * u)
    else: md, mi = (x - 150 * u, y - 10 * u), (x + 150 * u, y - 10 * u)               # "mesa"
    for a_, b_ in ((hd, md), (hi, mi)):
        d.line([a_, b_], fill=OUT, width=int(78 * u))
        d.ellipse([a_[0] - 39 * u, a_[1] - 39 * u, a_[0] + 39 * u, a_[1] + 39 * u], fill=OUT)
    for a_, b_ in ((hd, md), (hi, mi)):
        d.line([a_, b_], fill=(34, 62, 130, 255), width=int(66 * u))
        d.ellipse([a_[0] - 33 * u, a_[1] - 33 * u, a_[0] + 33 * u, a_[1] + 33 * u], fill=(34, 62, 130, 255))
        d.ellipse([b_[0] - 30 * u, b_[1] - 30 * u, b_[0] + 30 * u, b_[1] + 30 * u], fill=WHITE + (255,))     # puño de camisa
    # ---- cuello y cabeza
    d.rectangle([hx - 34 * u, hy + 70 * u, hx + 34 * u, hy + 115 * u], fill=PIEL_L + (255,))
    for s_ in (-1, 1):                                                                  # orejas
        d.ellipse([hx + s_ * 100 * u - 22 * u, hy - 5 * u, hx + s_ * 100 * u + 22 * u, hy + 45 * u], fill=PIEL_L + (255,), outline=OUT, width=lw)
    d.ellipse([hx - 102 * u, hy - 108 * u, hx + 102 * u, hy + 112 * u], fill=PIEL_L + (255,), outline=OUT, width=lw)
    # pelo canoso peinado hacia atrás con jopo
    d.chord([hx - 106 * u, hy - 118 * u, hx + 106 * u, hy + 30 * u], 180, 360, fill=PELO_L + (255,))
    d.ellipse([hx - 75 * u, hy - 140 * u, hx + 60 * u, hy - 70 * u], fill=PELO_L + (255,))
    d.pieslice([hx - 20 * u, hy - 150 * u, hx + 110 * u, hy - 40 * u], 180, 300, fill=(150, 148, 155, 255))
    for s_ in (-1, 1):                                                                  # patillas
        d.rectangle([hx + s_ * 96 * u - 8 * u, hy - 40 * u, hx + s_ * 96 * u + 8 * u, hy + 20 * u], fill=PELO_L + (255,))
    # cejas y ojos
    guino = expr == "guino"
    for s_ in (-1, 1):
        ex, ey = hx + s_ * 40 * u, hy + 2 * u
        ceja_y = ey - (46 if expr in ("sorpresa", "panico") else 36) * u
        inc = 8 * u if expr == "serio" else 0
        d.line([ex - 24 * u, ceja_y + (inc if s_ < 0 else -inc) * -1, ex + 24 * u, ceja_y + (inc if s_ < 0 else -inc)], fill=(90, 88, 95, 255), width=max(4, int(11 * u)))
        parp = (lt % 3.4) < 0.11
        if expr == "risa" or parp or (guino and s_ > 0):
            d.arc([ex - 18 * u, ey - 10 * u, ex + 18 * u, ey + 14 * u], 200, 340, fill=OUT, width=max(3, int(5 * u))); continue
        g = 1.3 if expr in ("sorpresa", "panico") else 1.0
        d.ellipse([ex - 17 * u * g, ey - 19 * u * g, ex + 17 * u * g, ey + 19 * u * g], fill=WHITE + (255,), outline=OUT, width=max(2, int(3 * u)))
        r = 8 * u if g > 1 else 10 * u
        d.ellipse([ex - r, ey - r + 2 * u, ex + r, ey + r + 2 * u], fill=(40, 30, 25, 255))
        d.ellipse([ex - 4 * u, ey - 5 * u, ex, ey - 1 * u], fill=WHITE + (255,))
    if "lentes" in acc:
        for s_ in (-1, 1):
            ex, ey = hx + s_ * 40 * u, hy + 2 * u
            d.ellipse([ex - 30 * u, ey - 27 * u, ex + 30 * u, ey + 27 * u], outline=(30, 30, 40, 255), width=max(3, int(5 * u)))
        d.line([hx - 10 * u, hy, hx + 10 * u, hy], fill=(30, 30, 40, 255), width=max(3, int(5 * u)))
    # nariz grande
    d.ellipse([hx - 22 * u, hy + 18 * u, hx + 22 * u, hy + 58 * u], fill=(225, 160, 125, 255), outline=OUT, width=max(2, int(3 * u)))
    # boca (debajo del bigote)
    my = hy + 80 * u
    abierta = habla and (lt * 7.5) % 1 < 0.5
    if abierta or expr in ("sorpresa", "panico"):
        d.ellipse([hx - 24 * u, my - 6 * u, hx + 24 * u, my + 34 * u], fill=(140, 40, 50, 255), outline=OUT, width=max(2, int(3 * u)))
        d.ellipse([hx - 12 * u, my + 18 * u, hx + 12 * u, my + 30 * u], fill=(230, 110, 110, 255))
    elif expr in ("risa", "feliz", "guino"):
        d.chord([hx - 34 * u, my - 10 * u, hx + 34 * u, my + 32 * u], 0, 180, fill=(140, 40, 50, 255), outline=OUT, width=max(2, int(3 * u)))
        d.rectangle([hx - 24 * u, my + 10 * u, hx + 24 * u, my + 16 * u], fill=WHITE + (255,))
    else:
        d.line([hx - 22 * u, my + 10 * u, hx + 22 * u, my + 10 * u], fill=OUT, width=max(3, int(5 * u)))
    # bigote frondoso (se mueve un poco al hablar)
    bv = 4 * u * math.sin(lt * 30) if habla else 0
    for s_ in (-1, 1):
        d.pieslice([hx + (0 if s_ > 0 else -66 * u), hy + 44 * u + bv, hx + (66 * u if s_ > 0 else 0), hy + 92 * u + bv],
                   180 if s_ < 0 else 270, 360 if s_ < 0 else 180 + 270, fill=(95, 92, 98, 255))
    d.ellipse([hx - 62 * u, hy + 46 * u + bv, hx + 62 * u, hy + 80 * u + bv], fill=(95, 92, 98, 255))
    d.ellipse([hx - 30 * u, hy + 50 * u + bv, hx + 30 * u, hy + 66 * u + bv], fill=(120, 118, 125, 255))
    # mejillas
    for s_ in (-1, 1):
        d.ellipse([hx + s_ * 68 * u - 14 * u, hy + 34 * u, hx + s_ * 68 * u + 14 * u, hy + 52 * u], fill=(240, 150, 140, 200))
    # manos (encima de todo; en "papeles" sostiene hojas)
    if br == "papeles":
        d.rectangle([x - 110 * u, y - 140 * u, x + 110 * u, y - 25 * u], fill=(250, 250, 245, 255), outline=(150, 150, 160, 255), width=3)
        for j in range(4):
            d.line([x - 85 * u, y - 115 * u + j * 22 * u, x + 85 * u, y - 115 * u + j * 22 * u], fill=(170, 175, 190, 255), width=max(2, int(4 * u)))
    for m in (md, mi):
        d.ellipse([m[0] - 25 * u, m[1] - 25 * u, m[0] + 25 * u, m[1] + 25 * u], fill=PIEL_L + (255,), outline=OUT, width=max(2, int(3 * u)))


# =============================================================== JETITO (avioncito reportero)
def jetito(L, x, y, s, lt, habla, expr, k, dir_=1, mic=True):
    """Avioncito de perfil (nariz hacia 'dir_'), con ojos en la cabina y boca en la nariz. (x, y) = centro."""
    S = 2; u = s / 100 * S
    Wc, Hc = int(380 * u), int(260 * u)
    im = Image.new("RGBA", (Wc, Hc), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    cx, cy = Wc * 0.48, Hc * 0.58
    lw = max(3, int(5 * u))
    C = (30, 35, 60, 255)
    # cola (aleta naranja con avioncito blanco)
    d.polygon([(cx - 150 * u, cy - 20 * u), (cx - 175 * u, cy - 125 * u), (cx - 130 * u, cy - 125 * u), (cx - 85 * u, cy - 25 * u)], fill=ORANGE + (255,), outline=C, width=lw)
    d.polygon([(cx - 160 * u, cy - 75 * u), (cx - 128 * u, cy - 98 * u), (cx - 140 * u, cy - 70 * u)], fill=WHITE + (255,))
    # ala trasera (al fondo)
    d.polygon([(cx - 10 * u, cy - 10 * u), (cx + 40 * u, cy - 10 * u), (cx - 30 * u, cy - 85 * u), (cx - 60 * u, cy - 85 * u)], fill=(20, 80, 170, 255), outline=C, width=lw)
    # fuselaje
    d.rounded_rectangle([cx - 170 * u, cy - 55 * u, cx + 150 * u, cy + 55 * u], int(55 * u), fill=WHITE + (255,), outline=C, width=lw)
    d.ellipse([cx + 60 * u, cy - 58 * u, cx + 180 * u, cy + 58 * u], fill=WHITE + (255,), outline=C, width=lw)
    d.rectangle([cx + 60 * u, cy - 52 * u, cx + 120 * u, cy + 52 * u], fill=WHITE + (255,))
    # franjas de marca
    d.rectangle([cx - 160 * u, cy + 12 * u, cx + 120 * u, cy + 26 * u], fill=AZUL + (255,))
    d.rectangle([cx - 160 * u, cy + 30 * u, cx + 100 * u, cy + 38 * u], fill=ORANGE + (255,))
    # ventanitas
    for j in range(4):
        wx = cx - 120 * u + j * 38 * u
        d.ellipse([wx - 9 * u, cy - 22 * u, wx + 9 * u, cy - 4 * u], fill=(120, 190, 250, 255), outline=C, width=max(2, int(3 * u)))
    # cabina = ojos
    big = 1.25 if expr in ("sorpresa", "panico") else 1.0
    parp = (lt % 2.9) < 0.1
    for j, ex in enumerate((cx + 92 * u, cx + 132 * u)):
        ey = cy - 18 * u
        if expr == "risa" or parp:
            d.arc([ex - 17 * u, ey - 12 * u, ex + 17 * u, ey + 14 * u], 200, 340, fill=C, width=max(3, int(5 * u))); continue
        rw, rh = 17 * u * big, 22 * u * big
        d.ellipse([ex - rw, ey - rh, ex + rw, ey + rh], fill=WHITE + (255,), outline=C, width=max(2, int(4 * u)))
        rp = 8 * u if big > 1 else 10 * u
        d.ellipse([ex + 2 * u - rp, ey - rp + 2 * u, ex + 2 * u + rp, ey + rp + 2 * u], fill=(20, 40, 90, 255))
        d.ellipse([ex - 2 * u, ey - 6 * u, ex + 3 * u, ey - 1 * u], fill=WHITE + (255,))
    if expr == "panico":                                                     # gotita de sudor
        d.ellipse([cx + 150 * u, cy - 60 * u, cx + 166 * u, cy - 38 * u], fill=(110, 190, 255, 255))
    # boca en la nariz
    mx, my = cx + 125 * u, cy + 26 * u
    if (habla and (lt * 7.5) % 1 < 0.5) or expr in ("sorpresa", "panico"):
        d.ellipse([mx - 18 * u, my - 10 * u, mx + 18 * u, my + 18 * u], fill=(150, 40, 60, 255), outline=C, width=max(2, int(3 * u)))
    else:
        d.chord([mx - 24 * u, my - 14 * u, mx + 24 * u, my + 16 * u], 0, 180, fill=(150, 40, 60, 255), outline=C, width=max(2, int(3 * u)))
    # mejilla
    d.ellipse([cx + 52 * u, cy + 4 * u, cx + 76 * u, cy + 18 * u], fill=(255, 160, 170, 220))
    # ala delantera (sostiene el micrófono)
    aleteo = 6 * u * math.sin(k * 9)
    d.polygon([(cx - 30 * u, cy + 10 * u), (cx + 30 * u, cy + 10 * u), (cx + 5 * u, cy + 95 * u + aleteo), (cx - 40 * u, cy + 95 * u + aleteo)],
              fill=AZUL + (255,), outline=C, width=lw)
    # turbina
    d.rounded_rectangle([cx - 40 * u, cy + 50 * u, cx + 10 * u, cy + 78 * u], int(12 * u), fill=(200, 205, 215, 255), outline=C, width=max(2, int(3 * u)))
    # gorrita de prensa
    d.chord([cx + 55 * u, cy - 95 * u, cx + 150 * u, cy - 30 * u], 180, 360, fill=ORANGE + (255,), outline=C, width=max(2, int(3 * u)))
    d.rounded_rectangle([cx + 120 * u, cy - 70 * u, cx + 185 * u, cy - 58 * u], int(5 * u), fill=ORANGE + (255,), outline=C, width=max(2, int(3 * u)))
    d.rounded_rectangle([cx + 72 * u, cy - 88 * u, cx + 128 * u, cy - 70 * u], int(4 * u), fill=WHITE + (255,))
    textos = [((cx + 100 * u, cy - 79 * u), "PRENSA", max(8, int(12 * u)), NAVY)]
    if mic:
        mx0, my0 = cx + 18 * u, cy + 90 * u + aleteo
        mx1, my1 = cx + 120 * u, cy + 70 * u
        d.line([mx0, my0, mx1, my1], fill=(60, 60, 70, 255), width=max(4, int(10 * u)))
        d.ellipse([mx1 - 18 * u, my1 - 18 * u, mx1 + 18 * u, my1 + 18 * u], fill=(40, 40, 50, 255), outline=C, width=2)
        d.rectangle([mx0 + 20 * u, my0 - 30 * u, mx0 + 52 * u, my0 - 4 * u], fill=ORANGE + (255,))
        textos.append(((mx0 + 36 * u, my0 - 17 * u), "JP", max(8, int(15 * u)), WHITE))
    if dir_ < 0: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    d = ImageDraw.Draw(im)
    for (tx, ty), t_, tam, col in textos:
        d.text((Wc - tx if dir_ < 0 else tx, ty), t_, font=_sh().font("Black", tam), fill=col + (255,), anchor="mm")
    im = im.resize((Wc // S, Hc // S), Image.LANCZOS)
    return im


# =============================================================== VALE (reportera de aduanas)
PIEL_V, PELO_V = (198, 140, 100), (40, 25, 20)


def vale(L, x, y, s, lt, habla, expr, br, k):
    """Reportera joven con casco blanco y chaleco naranja reflectivo, tablet en mano. y = borde inferior del torso."""
    u = s / 100; d = ImageDraw.Draw(L); lw = max(3, int(4 * u))
    hx, hy = x, y - 330 * u
    # cola de caballo (detrás)
    sw = 14 * u * math.sin(lt * 5)
    d.ellipse([hx + 60 * u + sw, hy - 40 * u, hx + 150 * u + sw, hy + 150 * u], fill=PELO_V + (255,))
    # torso: polo azul + chaleco naranja con cintas reflectivas
    d.rectangle([hx - 26 * u, hy + 70 * u, hx + 26 * u, hy + 125 * u], fill=PIEL_V + (255,))
    d.rounded_rectangle([x - 160 * u, y - 215 * u, x + 160 * u, y + 60 * u], int(70 * u), fill=(28, 58, 128, 255), outline=OUT, width=lw)
    d.polygon([(x - 150 * u, y - 190 * u), (x - 40 * u, y - 215 * u), (x - 20 * u, y + 60 * u), (x - 150 * u, y + 60 * u)], fill=ORANGE + (255,))
    d.polygon([(x + 150 * u, y - 190 * u), (x + 40 * u, y - 215 * u), (x + 20 * u, y + 60 * u), (x + 150 * u, y + 60 * u)], fill=ORANGE + (255,))
    for yy in (y - 100 * u, y - 50 * u):
        d.rectangle([x - 150 * u, yy, x - 26 * u, yy + 14 * u], fill=(235, 235, 225, 255))
        d.rectangle([x + 26 * u, yy, x + 150 * u, yy + 14 * u], fill=(235, 235, 225, 255))
    # brazos
    hd, hi = (x - 135 * u, y - 170 * u), (x + 135 * u, y - 170 * u)
    if br == "habla": md, mi = (x - 210 * u, y - 280 * u - 40 * u * abs(math.sin(k * 5))), (x + 150 * u, y - 60 * u)
    elif br == "tablet": md, mi = (x - 90 * u, y - 120 * u), (x + 90 * u, y - 120 * u)
    elif br == "senala": md, mi = (x - 260 * u, y - 430 * u + 8 * u * math.sin(k * 6)), (x + 150 * u, y - 60 * u)
    elif br == "arriba": md, mi = (x - 150 * u, y - 540 * u), (x + 150 * u, y - 540 * u)
    elif br == "pulgar": md, mi = (x - 200 * u, y - 360 * u), (x + 150 * u, y - 60 * u)
    else: md, mi = (x - 170 * u, y - 30 * u), (x + 170 * u, y - 30 * u)
    for a_, b_ in ((hd, md), (hi, mi)):
        d.line([a_, b_], fill=OUT, width=int(64 * u))
    for a_, b_ in ((hd, md), (hi, mi)):
        d.line([a_, b_], fill=(28, 58, 128, 255), width=int(54 * u))
        d.ellipse([a_[0] - 27 * u, a_[1] - 27 * u, a_[0] + 27 * u, a_[1] + 27 * u], fill=(28, 58, 128, 255))
    # cabeza
    d.ellipse([hx - 92 * u, hy - 95 * u, hx + 92 * u, hy + 98 * u], fill=PIEL_V + (255,), outline=OUT, width=lw)
    d.chord([hx - 95 * u, hy - 100 * u, hx + 95 * u, hy + 5 * u], 180, 360, fill=PELO_V + (255,))
    # casco blanco
    d.chord([hx - 112 * u, hy - 150 * u, hx + 112 * u, hy + 10 * u], 180, 360, fill=(248, 248, 250, 255), outline=OUT, width=lw)
    d.rounded_rectangle([hx - 125 * u, hy - 78 * u, hx + 125 * u, hy - 60 * u], int(8 * u), fill=(248, 248, 250, 255), outline=OUT, width=max(2, int(3 * u)))
    d.rectangle([hx - 12 * u, hy - 148 * u, hx + 12 * u, hy - 80 * u], fill=ORANGE + (255,))
    # ojos
    parp = (lt % 3.0) < 0.11
    for s_ in (-1, 1):
        ex, ey = hx + s_ * 36 * u, hy + 10 * u
        if expr == "risa" or parp or (expr == "guino" and s_ > 0):
            d.arc([ex - 18 * u, ey - 10 * u, ex + 18 * u, ey + 14 * u], 200, 340, fill=OUT, width=max(3, int(5 * u))); continue
        g = 1.25 if expr in ("sorpresa", "panico") else 1.0
        d.ellipse([ex - 18 * u * g, ey - 22 * u * g, ex + 18 * u * g, ey + 22 * u * g], fill=WHITE + (255,), outline=OUT, width=max(2, int(3 * u)))
        r = 10 * u
        d.ellipse([ex - r, ey - r + 3 * u, ex + r, ey + r + 3 * u], fill=(50, 30, 20, 255))
        d.ellipse([ex - 4 * u, ey - 4 * u, ex + 1 * u, ey + 1 * u], fill=WHITE + (255,))
        d.line([ex + s_ * 12 * u, ey - 21 * u * g, ex + s_ * 24 * u, ey - 31 * u * g], fill=OUT, width=max(2, int(4 * u)))
        d.line([ex - 18 * u, hy - 30 * u, ex + 18 * u, hy - 32 * u], fill=PELO_V + (255,), width=max(3, int(6 * u)))
    for s_ in (-1, 1):
        d.ellipse([hx + s_ * 60 * u - 15 * u, hy + 40 * u, hx + s_ * 60 * u + 15 * u, hy + 56 * u], fill=(230, 120, 120, 220))
    my = hy + 58 * u
    if (habla and (lt * 7.5) % 1 < 0.5) or expr in ("sorpresa", "panico"):
        d.ellipse([hx - 18 * u, my - 10 * u, hx + 18 * u, my + 20 * u], fill=(150, 40, 60, 255), outline=OUT, width=max(2, int(3 * u)))
    else:
        d.chord([hx - 26 * u, my - 16 * u, hx + 26 * u, my + 20 * u], 0, 180, fill=(150, 40, 60, 255), outline=OUT, width=max(2, int(3 * u)))
    # tablet
    if br == "tablet":
        d.rounded_rectangle([x - 115 * u, y - 210 * u, x + 115 * u, y - 70 * u], int(14 * u), fill=(30, 30, 40, 255))
        d.rounded_rectangle([x - 102 * u, y - 198 * u, x + 102 * u, y - 82 * u], int(8 * u), fill=(120, 200, 140, 255))
        d.text((x, y - 140 * u), "OK", font=_sh().font("Black", max(10, int(50 * u))), fill=WHITE + (255,), anchor="mm")
    for m in (md, mi):
        d.ellipse([m[0] - 24 * u, m[1] - 24 * u, m[0] + 24 * u, m[1] + 24 * u], fill=PIEL_V + (255,), outline=OUT, width=max(2, int(3 * u)))
    if br == "pulgar":
        sh = _sh(); sh.pegar_centro(L, sh.emoji("👍", 90 * u), md[0], md[1] - 30 * u)


# =============================================================== UTILERÍA
def _grad(L, top, bot, y0=0, y1=H):
    d = ImageDraw.Draw(L)
    for yy in range(int(y0), int(y1), 4):
        q = (yy - y0) / max(1, y1 - y0)
        c = tuple(int(a + (b - a) * q) for a, b in zip(top, bot))
        d.rectangle([0, yy, W, yy + 4], fill=c + (255,))


def p_estudio(L, p, lt, k):
    """Set del noticiero: fondo azul profundo, paneles LED, focos y líneas de luz."""
    _grad(L, (6, 16, 46), (18, 58, 128))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for i in range(6):                                                       # haces de luz desde arriba
        bx = 90 + i * 180 + 30 * math.sin(lt * 0.8 + i)
        d.polygon([(bx - 18, 0), (bx + 18, 0), (bx + 160, H * 0.75), (bx - 160, H * 0.75)], fill=(120, 170, 255, 16))
    for col in range(2):                                                     # paneles LED a los lados
        x0 = 20 if col == 0 else W - 120
        for r in range(14):
            for c in range(3):
                on = (math.sin(lt * 3 + r * 0.7 + c + col * 2) + 1) / 2
                cc = ORANGE if (r + c) % 4 == 0 else (60, 130, 255)
                d.rectangle([x0 + c * 34, 520 + r * 62, x0 + c * 34 + 26, 520 + r * 62 + 50], fill=cc + (int(40 + 90 * on),))
    for i in range(9):                                                       # luces del techo
        lx = 60 + i * 120
        d.ellipse([lx - 16, 470 - 16, lx + 16, 470 + 16], fill=(255, 240, 200, 200))
    L.alpha_composite(ov)


def p_pantalla(L, p, lt, k):
    """Pantalla gigante del set: emoji grande + título (y subtítulo) con barrido de entrada."""
    sh = _sh(); d = ImageDraw.Draw(L)
    x0, y0, x1, y1 = p.get("caja", [150, 540, 930, 940])
    d.rounded_rectangle([x0 - 14, y0 - 14, x1 + 14, y1 + 14], 30, fill=(10, 14, 30, 255), outline=ORANGE + (255,), width=10)
    inner = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0)); di = ImageDraw.Draw(inner)
    top, bot = tuple(p.get("fondo", [20, 70, 170])), tuple(p.get("fondo2", [8, 25, 70]))
    for yy in range(0, inner.height, 4):
        q = yy / inner.height; c = tuple(int(a + (b - a) * q) for a, b in zip(top, bot))
        di.rectangle([0, yy, inner.width, yy + 4], fill=c + (255,))
    for j in range(0, inner.height, 8):                                      # líneas de TV
        di.line([0, j, inner.width, j], fill=(255, 255, 255, 12))
    q = sh.ease(k / 0.35)
    if p.get("e"):
        im = sh.emoji(p["e"], p.get("r", 230) * (1 + 0.05 * math.sin(lt * 4)))
        sh.pegar_centro(inner, im, inner.width * (0.25 if p.get("titulo") else 0.5), inner.height * 0.5 + 6 * math.sin(lt * 3))
    if p.get("titulo"):
        cx = inner.width * (0.64 if p.get("e") else 0.5)
        f = sh.font("Black", p.get("tam", 120))
        while f.getlength(p["titulo"]) > inner.width * (0.6 if p.get("e") else 0.9) and f.size > 40:
            f = sh.font("Black", f.size - 6)
        sh.texto_borde(inner, (cx, inner.height * (0.42 if p.get("sub") else 0.5)), p["titulo"], f, tuple(p.get("color", AMARILLO)), 1, borde=7)
        if p.get("sub"):
            fs = sh.font("Black", p.get("tam_sub", 52))
            while fs.getlength(p["sub"]) > inner.width * (0.6 if p.get("e") else 0.9) and fs.size > 26:
                fs = sh.font("Black", fs.size - 4)
            sh.texto_borde(inner, (cx, inner.height * 0.68), p["sub"], fs, WHITE, 1, borde=6)
    if q < 1:                                                                # barrido de entrada
        m = Image.new("L", inner.size, 0); ImageDraw.Draw(m).rectangle([0, 0, inner.width * q, inner.height], fill=255)
        vacio = Image.new("RGBA", inner.size, (0, 0, 0, 0)); inner = Image.composite(inner, vacio, m)
    L.alpha_composite(inner, (x0, y0))


def p_mesa(L, p, lt, k):
    """Mesa del noticiero con el nombre JP NOTICIAS (va al frente de Don Lucho)."""
    sh = _sh(); d = ImageDraw.Draw(L)
    y = p.get("y", 1340); x0, x1 = p.get("x0", 70), p.get("x1", W - 70); y1 = p.get("y1", 1575)
    d.rounded_rectangle([x0 - 20, y - 30, x1 + 20, y + 14], 14, fill=(230, 235, 245, 255), outline=(20, 30, 60, 255), width=5)
    d.polygon([(x0, y + 10), (x1, y + 10), (x1 - 50, y1), (x0 + 50, y1)], fill=(16, 34, 82, 255), outline=(8, 16, 40, 255))
    d.rectangle([x0 + 20, y + 40, x1 - 20, y + 58], fill=ORANGE + (255,))
    d.rectangle([x0 + 40, y1 - 40, x1 - 40, y1 - 30], fill=(60, 130, 255, 255))
    cx, cy = (x0 + x1) / 2, (y + y1) / 2 + 22
    r = 50; cx -= 45; d.ellipse([cx - 255 - r, cy - r, cx - 255 + r, cy + r], fill=ORANGE + (255,), outline=WHITE + (255,), width=5)
    d.arc([cx - 255 - r * 0.5, cy - r, cx - 255 + r * 0.5, cy + r], 0, 360, fill=WHITE + (255,), width=4)
    d.line([cx - 255 - r, cy, cx - 255 + r, cy], fill=WHITE + (255,), width=4)
    d.text((cx + 75, cy), p.get("texto", "JP NOTICIAS"), font=sh.font("Black", 78), fill=WHITE + (255,), anchor="mm")


def p_zocalo(L, p, lt, k):
    """Banda inferior tipo TV: etiqueta roja + texto blanco (entra deslizando)."""
    sh = _sh()
    y = p.get("y", 1600); q = sh.ease(k / 0.4)
    tag, txt = p.get("tag", "ÚLTIMO MINUTO"), p.get("texto", "")
    ft, fx = sh.font("Black", 40), sh.font("Black", p.get("tam", 50))
    while fx.getlength(txt) > W - 120 and fx.size > 30:
        fx = sh.font("Black", fx.size - 2)
    im = Image.new("RGBA", (W, 170), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    tw = ft.getlength(tag) + 50
    d.rectangle([40, 70, W - 40, 160], fill=WHITE + (255,))
    d.rectangle([40, 150, W - 40, 160], fill=ORANGE + (255,))
    d.text((70, 112), txt, font=fx, fill=NAVY + (255,), anchor="lm")
    col = tuple(p.get("color_tag", ROJO))
    d.rectangle([40, 14, 40 + tw, 70], fill=col + (255,))
    if (lt * 2) % 1 < 0.75 or not p.get("parpadea", True):
        d.text((40 + tw / 2, 42), tag, font=ft, fill=WHITE + (255,), anchor="mm")
    L.alpha_composite(im, (int(-W * (1 - q)), int(y - 85)))


def p_ticker(L, p, lt, k):
    """Cinta de noticias que corre en la parte de abajo."""
    sh = _sh(); d = ImageDraw.Draw(L)
    y = p.get("y", 1722); h = 62
    d.rectangle([0, y, W, y + h], fill=ORANGE + (255,))
    f = sh.font("Black", 38)
    txt = "   •   ".join(p.get("textos", ["JP NOTICIAS"])) + "   •   "
    tw = f.getlength(txt)
    off = (lt * p.get("vel", 230)) % tw
    x = 190 - off
    while x < W:
        d.text((x, y + h / 2), txt, font=f, fill=WHITE + (255,), anchor="lm"); x += tw
    d.rectangle([0, y, 170, y + h], fill=NAVY + (255,))
    d.text((85, y + h / 2), "JP", font=sh.font("Black", 44), fill=ORANGE + (255,), anchor="mm")


def p_en_vivo(L, p, lt, k):
    sh = _sh(); d = ImageDraw.Draw(L)
    txt = "EN VIVO" + (" · " + p["lugar"] if p.get("lugar") else "")
    f = sh.font("Black", 42); tw = f.getlength(txt)
    x, y = p.get("x", 60), p.get("y", 140)
    d.rounded_rectangle([x, y, x + tw + 100, y + 70], 35, fill=ROJO + (255,), outline=WHITE + (255,), width=4)
    if (lt * 1.6) % 1 < 0.6:
        d.ellipse([x + 26, y + 22, x + 52, y + 48], fill=WHITE + (255,))
    d.text((x + 70, y + 35), txt, font=f, fill=WHITE + (255,), anchor="lm")


def p_sirena(L, p, lt, k):
    """Luces de alarma de último minuto: destellos rojos/azules y haces giratorios."""
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    fase = (lt * 4) % 1
    col = ROJO if fase < 0.5 else AZUL
    d.rectangle([0, 0, W, H], fill=col + (int(60 * abs(math.sin(lt * 12))),))
    for i, cx in enumerate((150, W - 150)):
        a = lt * 6 + i * math.pi
        for s_ in (0, math.pi):
            ang = a + s_
            d.polygon([(cx, 120), (cx + 900 * math.cos(ang - 0.18), 120 + 900 * math.sin(ang - 0.18)),
                       (cx + 900 * math.cos(ang + 0.18), 120 + 900 * math.sin(ang + 0.18))], fill=(ROJO if i == 0 else AZUL) + (70,))
        d.ellipse([cx - 55, 65, cx + 55, 175], fill=(ROJO if i == 0 else AZUL) + (255,), outline=WHITE + (255,), width=6)
    L.alpha_composite(ov)


def p_almacen(L, p, lt, k):
    """Almacén en Miami: pared, estantes con cajas, ventana con palmera y sol."""
    sh = _sh(); d = ImageDraw.Draw(L)
    _grad(L, (250, 214, 160), (236, 170, 110), 0, 1400)
    d.rectangle([0, 1400, W, H], fill=(150, 150, 160, 255))
    for j in range(0, W, 120): d.line([j, 1400, j - 200, H], fill=(135, 135, 145, 255), width=3)
    # ventana con palmera
    wx0, wy0, wx1, wy1 = 640, 560, 1000, 900
    d.rectangle([wx0, wy0, wx1, wy1], fill=(120, 205, 250, 255), outline=WHITE + (255,), width=14)
    d.ellipse([wx1 - 120, wy0 + 30, wx1 - 40, wy0 + 110], fill=(255, 220, 60, 255))
    d.line([wx0 + 120, wy1, wx0 + 150, wy0 + 120], fill=(130, 85, 40, 255), width=18)
    for a in range(5):
        ang = math.radians(200 + a * 35 + 6 * math.sin(lt * 2 + a))
        d.line([wx0 + 150, wy0 + 120, wx0 + 150 + 110 * math.cos(ang), wy0 + 120 + 70 * math.sin(ang) + 20], fill=(40, 160, 70, 255), width=22)
    d.rectangle([wx0, wy0, wx1, wy1], outline=WHITE + (255,), width=14)
    d.line([(wx0 + wx1) / 2, wy0, (wx0 + wx1) / 2, wy1], fill=WHITE + (255,), width=10)
    # cartel MIAMI
    d.rounded_rectangle([50, 540, 600, 650], 18, fill=NAVY + (255,), outline=ORANGE + (255,), width=6)
    d.text((325, 595), p.get("cartel", "ALMACÉN MIAMI"), font=sh.font("Black", 54), fill=WHITE + (255,), anchor="mm")
    # estantes con cajas
    for fila, yy in enumerate((800, 1050, 1300)):
        d.rectangle([40, yy, 600, yy + 22], fill=(60, 110, 200, 255))
        for c in range(4):
            bw = 110 + 15 * ((c + fila) % 2); bx = 60 + c * 135
            bh = 120 + 25 * ((c * 3 + fila) % 3)
            d.rectangle([bx, yy - bh, bx + bw, yy], fill=(212, 158, 98, 255), outline=(96, 60, 30, 255), width=4)
            d.rectangle([bx + bw / 2 - 9, yy - bh, bx + bw / 2 + 9, yy], fill=(30, 95, 216, 255) if (c + fila) % 2 else ORANGE + (255,))
    for xx in (40, 600):
        d.rectangle([xx - 8, 650, xx + 8, 1400], fill=(40, 80, 160, 255))


def p_aduana_set(L, p, lt, k):
    """Oficina de aduana en Lima: pared verde agua, mostrador, banderita y cartel."""
    sh = _sh(); d = ImageDraw.Draw(L)
    _grad(L, (205, 235, 230), (150, 200, 200), 0, 1400)
    d.rectangle([0, 1400, W, H], fill=(120, 130, 140, 255))
    d.rounded_rectangle([110, 520, 970, 640], 18, fill=(250, 250, 250, 255), outline=NAVY + (255,), width=6)
    d.text((540, 580), p.get("cartel", "ADUANA · LIMA"), font=sh.font("Black", 62), fill=NAVY + (255,), anchor="mm")
    fx, fy = 860, 700                                                      # banderita del Perú
    d.line([fx, fy, fx, fy + 260], fill=(90, 90, 90, 255), width=8)
    ond = 8 * math.sin(lt * 4)
    for j, col in enumerate(((215, 20, 40), WHITE, (215, 20, 40))):
        d.polygon([(fx + j * 50, fy + ond * (j / 3)), (fx + (j + 1) * 50, fy + ond * ((j + 1) / 3)),
                   (fx + (j + 1) * 50, fy + 100 + ond * ((j + 1) / 3)), (fx + j * 50, fy + 100 + ond * (j / 3))], fill=col + (255,))


def p_intro(L, p, lt, k):
    """Cortina animada: globo que gira, anillos y el nombre JP NOTICIAS con rebote."""
    sh = _sh()
    _grad(L, (8, 18, 52), (22, 70, 150))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    cx, cy = W / 2, p.get("y", 880)
    for i in range(16):                                                      # rayos de luz giratorios
        a = lt * 0.6 + i * math.pi / 8
        d.polygon([(cx, cy), (cx + 1400 * math.cos(a), cy + 1400 * math.sin(a)), (cx + 1400 * math.cos(a + 0.12), cy + 1400 * math.sin(a + 0.12))],
                  fill=(255, 255, 255, 14 if i % 2 else 26))
    z = max(0.01, sh.elastico(k / 0.7)); r = 220 * z
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(30, 110, 230, 255), outline=WHITE + (255,), width=10)
    for j in range(5):                                                       # meridianos que giran
        ph = (lt * 0.7 + j / 5) % 1; rx = abs(math.cos(ph * math.pi)) * r
        d.ellipse([cx - rx, cy - r, cx + rx, cy + r], outline=(255, 255, 255, 140), width=5)
    for yy in (-0.5, 0, 0.5):
        ry = r * yy; rw = math.sqrt(max(0, r * r - ry * ry))
        d.line([cx - rw, cy + ry, cx + rw, cy + ry], fill=(255, 255, 255, 140), width=5)
    for j in range(2):                                                       # anillo naranja orbitando
        a = lt * 3 + j * math.pi
        ox, oy = cx + (r + 70) * math.cos(a), cy + (r + 20) * 0.35 * math.sin(a)
        d.ellipse([ox - 26, oy - 26, ox + 26, oy + 26], fill=ORANGE + (255,))
    L.alpha_composite(ov)
    t2 = max(0.0, k - 0.35)
    if t2 > 0:
        z2 = max(0.01, sh.elastico(t2 / 0.6))
        sh.texto_borde(L, (cx, cy + 330), "JP", sh.font("Black", int(150 * z2)), ORANGE, 1, borde=12)
        sh.texto_borde(L, (cx, cy + 470), "NOTICIAS", sh.font("Black", int(130 * z2)), WHITE, 1, borde=12)
    if k > 1.0:
        sh.texto_borde(L, (cx, cy + 590), p.get("sub", "Lo último de tus compras"), sh.font("Bold", 50), AMARILLO, min(1, (k - 1.0) / 0.3), borde=6)


PROPS = {"estudio": p_estudio, "pantalla": p_pantalla, "mesa": p_mesa, "zocalo": p_zocalo, "ticker": p_ticker,
         "en_vivo": p_en_vivo, "sirena": p_sirena, "almacen": p_almacen, "intro": p_intro, "aduana_set": p_aduana_set}
FRENTE = ("mesa", "zocalo", "ticker", "en_vivo", "sirena")


def sfx(tipo, tono, ruido, sr, np):
    """Efectos extra para el noticiero (devuelve None si no es uno de estos)."""
    if tipo == "sirena":
        n = int(1.6 * sr); t = np.arange(n) / sr
        f = 700 + 350 * np.sin(2 * np.pi * 2.5 * t)
        w = np.sign(np.sin(2 * np.pi * np.cumsum(f) / sr)) * 0.13 * np.minimum(1, (1.6 - t) * 4)
        return w
    if tipo == "jingle":                                                     # cortina de noticiero (original)
        w = np.zeros(int(1.8 * sr))
        notas = [(0.0, 587), (0.12, 784), (0.24, 988), (0.42, 1175), (0.42, 784), (0.42, 988)]
        for t0, f in notas:
            b = tono(f, f, 1.2 if t0 > 0.4 else 0.2, "sq", 2.5 if t0 > 0.4 else 8, 0.12); i0 = int(t0 * sr)
            w[i0:i0 + len(b)] += b[: len(w) - i0]
        b = tono(80, 40, 0.5, dec=7, vol=0.8); i0 = int(0.42 * sr); w[i0:i0 + len(b)] += b
        return w
    if tipo == "tecleo":
        w = np.zeros(int(1.0 * sr))
        for j in range(9):
            b = ruido(0.03, 120, 0.35); i0 = int((j * 0.1 + 0.02 * (j % 3)) * sr); w[i0:i0 + len(b)] += b
        return w
    return None
