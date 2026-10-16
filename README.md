# jetport-media

Videos y generador de contenido para las redes de Jetport Courier (TikTok @jetport_courier, Instagram @jetportcourier,
Facebook "Jetport Courier"). Metricool descarga los videos desde aquí para publicarlos.

## Carpetas
- `generador/video.py` — crea videos verticales 1080x1920 a partir de un guion JSON (instrucciones al inicio del archivo).
- `generador/musica.py` — música original sin derechos de autor (4 estilos, 120 combinaciones según la semilla).
- `generador/logo_*.png` — logo oficial (horizontal, vertical, transparente, con contorno).
- `guiones/` — guion de cada video (AAAA-MM-DD_tema.json, fecha = día de publicación).
- `videos/` — videos finales (.mp4).
- `material/` — clips reales del negocio grabados por el dueño (aún vacío). Registro en material/LEEME.md.
- `referencias/` — material solo de referencia (avatar). NO se usa en los videos.
- `temas_publicados.md` — registro de temas, semillas y clips usados para no repetir.
- `TRASPASO.md` — resumen completo del proyecto, decisiones y próximos pasos.

## Uso rápido
    pip install pillow numpy scipy --break-system-packages   # ffmpeg también es necesario
    python3 generador/video.py guiones/X.json videos/X.mp4          # video completo
    python3 generador/video.py guiones/X.json vista.png 7.5         # un fotograma (segundo 7.5) para revisar
URL pública para Metricool: https://raw.githubusercontent.com/Jetportcourier/jetport-media/main/videos/X.mp4
