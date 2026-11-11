#!/usr/bin/env python3
"""Cinco copias distintas de un reel ya hecho, para subirlas como «Reels de prueba» de Instagram, una al día.

Solo necesita Python 3 y ffmpeg (con ffprobe) en el PATH. No toca tu cuenta: deja los vídeos, sus pies y el horario.

    python3 copias.py mi-reel.mp4 --titulos titulos.txt --pie pie.txt --hashtags "#ia #claude #reels #marketing #negocio"

🚨 Antes de hacer nada comprueba la regla de mínimos (distintas.py): entre el vídeo y sus copias (6 vídeos), ninguno
repite canción, estilo de subtítulos, contenido (otro comienzo u otra frase fuera) ni titular, y la velocidad tampoco.
Si no se cumple, para con el aviso; --aun-asi las hace igual, solo si la persona ha leído el aviso y dice que sí.

Cada copia cambia varias cosas a la vez, para que Instagram la vea como otro vídeo y no como el mismo repetido:
velocidad (la voz no cambia de tono), encuadre (un poco de zoom y otro centro), color, grano invisible, el arranque y
el final (solo dentro de los silencios, nunca encima de la voz), un fichero nuevo sin los datos del original y, si
le pasas `--titulos`, otro titular arriba los primeros segundos. Con `--ganchos` (otros comienzos que grabaste),
cada copia empieza con uno distinto. Con `--espejo`, la 2.ª y la 4.ª van volteadas (solo si el vídeo no lleva letras:
saldrían del revés).

Opciones:
  --titulos FICHERO   5 líneas, una por copia. « / » parte el titular en dos líneas.
  --titulo-y PX       dónde empieza el titular (por defecto 260: debajo de lo que tapa Instagram arriba).
  --titulo-s SEG      cuánto dura el titular (por defecto 3).
  --tapa Y0-Y1        si el vídeo ya trae su titular arriba: esa franja (px, en 1080×1920) se difumina mientras
                      dura el titular nuevo, y el nuevo va encima, centrado en ella.
  --caja negra|blanca|ninguna   el fondo del titular (por defecto negra).
  --ganchos A.mp4 B.mp4 …  otros comienzos grabados; --corte SEG: dónde acaba el comienzo en el vídeo original.
  --espejo            voltea la 2.ª y la 4.ª.
  --musica A.mp3 B.mp3 …   una canción de fondo distinta por copia, bajo la voz (sin la del original).
  --quitar "12.3-15.8" "40.1-44.0+51.0-53.2" …   lo que se quita en cada copia (una entrada por copia, en segundos
                      del vídeo original; «+» une dos tramos): frases enteras, de pausa a pausa. --ver-pausas las lista.
  --ver-pausas        solo imprime las pausas de la voz (para elegir de dónde a dónde va cada frase) y sale.
  --titulo-original "…"   el titular que ya lleva el vídeo, para que ninguna copia repita el mismo.
  --srt FICHERO       los subtítulos del vídeo (.srt): cada copia los quema con otro estilo (blanco con borde, caja
                      negra, amarillo, caja blanca, mayúsculas, caja amarilla). El vídeo, exportado SIN subtítulos.
  --sin-voz           el vídeo no tiene voz ni subtítulos: el estilo de subtítulos no se pide.
  --aun-asi           hacerlas aunque el aviso diga que se parecen demasiado (solo con el sí de la persona).
  --pie FICHERO       el pie del reel original; cada copia lo lleva con 5 hashtags en otro orden.
  --hashtags "…"      de 5 a 10, del tema del vídeo (nunca #viral, #fyp).
  --desde AAAA-MM-DD  el día de la primera (por defecto, mañana). --horas "11:00,13:00,16:00,19:00,21:00".
  --salida CARPETA    dónde dejarlas (por defecto, <vídeo>-pruebas/ al lado del vídeo).
  --n N               cuántas (por defecto 5).
"""
import argparse
import datetime as dt
import json
import random
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import distintas  # noqa: E402

# Lo que cambia en cada copia (una fila por copia; si pides más de 5, vuelve a empezar con otro color)
VELOCIDAD = [1.05, 1.08, 1.03, 1.10, 1.06]
ZOOM = [1.05, 1.08, 1.04, 1.07, 1.06]
DESPLAZA = [0, -14, 12, -8, 9]                    # px a izquierda/derecha del centro, después del zoom
COLOR = [  # contraste, brillo, saturación, gamma, (rojo, azul) en sombras
    (1.04, 0.01, 1.10, 0.98, (0.03, -0.03)),
    (0.97, 0.02, 0.92, 1.03, (-0.02, 0.03)),
    (1.07, -0.01, 1.05, 0.96, (0.02, 0.00)),
    (1.00, 0.03, 1.15, 1.00, (0.00, -0.02)),
    (1.03, 0.00, 0.97, 1.02, (-0.03, 0.02)),
]
ARRANQUE = [0.00, 0.15, 0.30, 0.10, 0.22]         # s que se quitan al principio, solo si ahí no hay voz
FINAL = [0.00, 0.20, 0.10, 0.30, 0.15]            # s que se quitan al final, solo si ahí no hay voz
ESPEJO = [False, True, False, True, False]
CALIDAD = [18, 19, 17, 20, 18]
HORAS = "11:00,13:00,16:00,19:00,21:00"
# Un estilo de subtítulos por copia (--srt): ninguna repite el de otra ni el del vídeo (que va sin ellos o con los suyos).
# Medidas de libass sobre un alto de 288: 11 ≈ 73 px en 1920, MarginV 95 ≈ a la altura del pecho
_BASE = "FontName=Arial,FontSize=11,Bold=1,Alignment=2,MarginV=95,Shadow=0"
SUBS = {
    "blanco con borde": _BASE + ",PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=1.6",
    "caja negra": _BASE + ",PrimaryColour=&H00FFFFFF,OutlineColour=&H38000000,BackColour=&H38000000,BorderStyle=3,Outline=3",
    "amarillo": _BASE + ",PrimaryColour=&H004DE1FF,OutlineColour=&H00000000,BorderStyle=1,Outline=1.6",
    "caja blanca": _BASE + ",PrimaryColour=&H00111111,OutlineColour=&H00FFFFFF,BackColour=&H00FFFFFF,BorderStyle=3,Outline=3",
    "mayúsculas": _BASE.replace("FontSize=11", "FontSize=10") + ",PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=1.8",
    "caja amarilla": _BASE + ",PrimaryColour=&H00111111,OutlineColour=&H004DE1FF,BackColour=&H004DE1FF,BorderStyle=3,Outline=3",
}


def sale(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def info(video):
    r = sale(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", str(video)])
    if r.returncode:
        sys.exit(f"No puedo leer {video}: {r.stderr.strip()}")
    j = json.loads(r.stdout)
    v = next((s for s in j["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in j["streams"] if s["codec_type"] == "audio"), None)
    if not v:
        sys.exit(f"{video} no tiene vídeo")
    w, h = int(v["width"]), int(v["height"])
    rot = int((v.get("tags") or {}).get("rotate", 0) or 0)
    for sd in v.get("side_data_list") or []:
        rot = int(sd.get("rotation", rot) or rot)
    if abs(rot) in (90, 270):
        w, h = h, w
    num, den = (v.get("r_frame_rate") or "30/1").split("/")
    fps = round(float(num) / float(den or 1)) or 30
    return {"w": w, "h": h, "fps": min(fps, 60), "dur": float(j["format"]["duration"]), "audio": a is not None}


def silencios(video, dur):
    """(silencio al principio, silencio al final) en segundos, medidos (no se toca nada que suene)."""
    r = sale(["ffmpeg", "-hide_banner", "-nostats", "-i", str(video), "-af", "silencedetect=n=-38dB:d=0.08", "-vn", "-f", "null", "-"])
    ini = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", r.stderr)]
    fin = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    al_principio = fin[0] if ini and ini[0] <= 0.02 and fin else 0.0
    al_final = dur - ini[-1] if ini and len(ini) > len(fin) else 0.0
    return max(0.0, al_principio - 0.04), max(0.0, al_final - 0.04)


def pausas(video, minimo=0.25):
    """[(inicio, fin)] de cada pausa de la voz de al menos `minimo` s: ahí se puede cortar sin pisar una palabra."""
    r = sale(["ffmpeg", "-hide_banner", "-nostats", "-i", str(video), "-af", f"silencedetect=n=-38dB:d={minimo}", "-vn", "-f", "null", "-"])
    ini = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", r.stderr)]
    fin = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    return [(max(0.0, a), b) for a, b in zip(ini, fin)]


def leer_quitar(spec):
    """«12.3-15.8+40-41» → [(12.3, 15.8), (40.0, 41.0)]; «-» o vacío → []."""
    tramos = []
    for t in filter(None, (spec or "").replace(" ", "").split("+")):
        if t == "-":
            continue
        a, _, b = t.partition("-")
        tramos.append((float(a), float(b)))
        if tramos[-1][1] <= tramos[-1][0]:
            sys.exit(f"--quitar «{spec}»: cada tramo es inicio-fin, con el fin después del inicio")
    return tramos


def comprobar_cortes(tramos, huecos, nombre):
    """Cada borde de lo que se quita cae en una pausa de la voz: si no, la copia cortaría una palabra."""
    for a, b in tramos:
        for borde in (a, b):
            if not any(x - 0.05 <= borde <= y + 0.05 for x, y in huecos):
                cerca = sorted(huecos, key=lambda h: abs((h[0] + h[1]) / 2 - borde))[:3]
                sys.exit(f"{nombre}: el corte en {borde:.2f} s cae encima de la voz. Pausas cercanas: "
                         + ", ".join(f"{x:.2f}-{y:.2f}" for x, y in sorted(cerca)))


def leer_srt(fichero):
    """[(inicio, fin, texto)] de un .srt."""
    def seg(t):
        h, m, r = t.strip().replace(",", ".").split(":")
        return int(h) * 3600 + int(m) * 60 + float(r)
    bloques = re.split(r"\n\s*\n", Path(fichero).expanduser().read_text(encoding="utf-8-sig").strip())
    salida = []
    for b in bloques:
        lineas = b.strip().splitlines()
        k = next((n for n, l in enumerate(lineas) if "-->" in l), None)
        if k is not None:
            x, y = lineas[k].split("-->")
            salida.append((seg(x), seg(y), "\n".join(lineas[k + 1:])))
    if not salida:
        sys.exit(f"{fichero}: no encuentro subtítulos (formato .srt: número, «00:00:01,000 --> 00:00:02,500», texto)")
    return salida


def escribir_srt(cues, fichero, mayusculas=False):
    def t(x):
        x = max(0.0, x)
        return f"{int(x // 3600):02d}:{int(x % 3600 // 60):02d}:{x % 60:06.3f}".replace(".", ",")
    Path(fichero).write_text("\n\n".join(f"{n}\n{t(a)} --> {t(b)}\n{x.upper() if mayusculas else x}"
                                          for n, (a, b, x) in enumerate(cues, 1)) + "\n", encoding="utf-8")


def fuente():
    for f in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/Library/Fonts/Arial Bold.ttf",
              "C:/Windows/Fonts/arialbd.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf"):
        if Path(f).exists():
            return f
    sys.exit("No encuentro una fuente en negrita para el titular: pásala con --fuente <fichero .ttf>")


def ruta_ffmpeg(p):
    return str(p).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")


def titular(lineas, tmp, i, y0, segs, caja, fnt):
    """drawtext de cada línea del titular, centrado, con su caja. El texto va en fichero: nada que escapar."""
    fil = []
    tam = 64 if max(len(l) for l in lineas) <= 22 else 54
    for k, linea in enumerate(lineas):
        f = Path(tmp) / f"titular-{i}-{k}.txt"
        f.write_text(linea, encoding="utf-8")
        color, fondo = ("white", "black@0.88") if caja != "blanca" else ("black", "white@0.95")
        partes = [f"fontfile='{ruta_ffmpeg(fnt)}'", f"textfile='{ruta_ffmpeg(f)}'", f"fontsize={tam}",
                  f"fontcolor={color}", "x=(w-text_w)/2", f"y={y0 + k * int(tam * 1.32)}", f"enable='lt(t,{segs})'"]
        if caja == "ninguna":
            partes += ["borderw=4", "bordercolor=black"]
        else:
            partes += ["box=1", f"boxcolor={fondo}", "boxborderw=14"]
        fil.append("drawtext=" + ":".join(partes))
    return fil


def una_copia(i, base, meta, a, tmp, lineas, salida):
    W, H, FPS = 1080, 1920, meta["fps"]
    vel, z, dx = VELOCIDAD[i % 5], ZOOM[i % 5], DESPLAZA[i % 5]
    c, b, s, g, (rs, bs) = COLOR[i % 5]
    if i >= 5:  # más de cinco: otro color sobre la misma fila
        c, s = c + 0.03, s - 0.05
    ini, fin = meta["recorte"][i]
    fuera = meta["quitar"][i]
    dur = meta["dur"] - ini - fin - sum(b - a for a, b in fuera)
    filtro_fuera = "+".join(f"between(t,{a:.3f},{b:.3f})" for a, b in fuera)
    subs = []
    if meta["srt"] is not None:   # en el tiempo de la base, antes de quitar, recortar y acelerar: todo se mueve con ella
        estilo = meta["subs"][i]
        f = Path(tmp) / f"subs-{i}.srt"
        escribir_srt(meta["srt"], f, mayusculas=estilo == "mayúsculas")
        subs = [f"scale={W}:{H}:force_original_aspect_ratio=increase", f"crop={W}:{H}",
                f"subtitles=filename='{ruta_ffmpeg(f)}':force_style='{SUBS[estilo]}'"]
    v = subs + ([f"fps={FPS}", f"select='not({filtro_fuera})'", f"setpts=N/({FPS}*TB)"] if fuera else []) + [
         f"trim=start={ini:.3f}:duration={dur:.3f}", "setpts=PTS-STARTPTS",
         f"scale={W}:{H}:force_original_aspect_ratio=increase", f"crop={W}:{H}",
         f"scale={round(W * z / 2) * 2}:{round(H * z / 2) * 2}",
         f"crop={W}:{H}:(in_w-{W})/2+{dx}:(in_h-{H})/2"]
    if a.espejo and ESPEJO[i % 5]:
        v.append("hflip")
    v += [f"eq=contrast={c}:brightness={b}:saturation={s}:gamma={g}",
          f"colorbalance=rs={rs}:bs={bs}", f"noise=alls=3:allf=t:all_seed={1000 + i * 37}",
          f"setpts=PTS/{vel}", f"fps={FPS}", "format=yuv420p"]
    txt = []
    if lineas:
        y0 = a.titulo_y
        if a.tapa:
            t0, t1 = a.tapa
            alto = (64 if max(len(l) for l in lineas) <= 22 else 54) * 1.32
            y0 = int(t0 + max(0, (t1 - t0 - alto * len(lineas)) / 2))
        txt = titular(lineas, tmp, i, y0, a.titulo_s, a.caja, a.fuente or fuente())
    cancion = meta["musica"][i]
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(base)] + (["-stream_loop", "-1", "-i", str(cancion)] if cancion else [])
    cmd += ["-filter_complex"]
    if a.tapa and lineas:
        t0, t1 = a.tapa
        graf = (f"[0:v]{','.join(v)},split[x][y];[y]crop={W}:{t1 - t0}:0:{t0},boxblur=24:3[z];"
                f"[x][z]overlay=0:{t0}:enable='lt(t,{a.titulo_s})',{','.join(txt)}[v]")
    else:
        graf = f"[0:v]{','.join(v + txt)}[v]"
    if meta["audio"]:
        sel = f"aselect='not({filtro_fuera})',asetpts=N/SR/TB," if fuera else ""
        graf += (f";[0:a]{sel}atrim=start={ini:.3f}:duration={dur:.3f},asetpts=PTS-STARTPTS,atempo={vel},"
                 f"equalizer=f={[180, 2500, 6000, 320, 4000][i % 5]}:t=q:w=1:g={[1.5, -1, 1, -1.5, 0.8][i % 5]}"
                 + ("[voz]" if cancion else "[a]"))
        if cancion:   # la canción, bajo la voz (unos 15 dB por debajo), con fundido al final
            largo = dur / vel
            graf += (f";[1:a]atrim=0:{largo:.3f},asetpts=PTS-STARTPTS,aresample=48000,loudnorm=I=-30:TP=-6:LRA=7,"
                     f"afade=t=out:st={max(0.0, largo - 1.5):.3f}:d=1.5[m];[voz][m]amix=inputs=2:duration=first:normalize=0[a]")
    cmd += [graf, "-map", "[v]"] + (["-map", "[a]", "-c:a", "aac", "-b:a", "192k", "-ar", "48000"] if meta["audio"] else [])
    cmd += ["-c:v", "libx264", "-preset", "fast", "-crf", str(CALIDAD[i % 5]), "-r", str(FPS),
            "-g", str(FPS * 2), "-map_metadata", "-1", "-map_chapters", "-1", "-fflags", "+bitexact",
            "-metadata", f"creation_time={dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')}",
            "-movflags", "+faststart", str(salida)]
    r = sale(cmd)
    if r.returncode:
        sys.exit(f"La copia {i + 1} falló:\n{r.stderr[-1500:]}")


def con_gancho(gancho, original, corte, meta, tmp, i):
    """Otro comienzo grabado + el vídeo desde donde acaba el suyo, todo a 1080×1920 y los mismos fps."""
    out = Path(tmp) / f"base-{i}.mp4"
    ig = info(gancho)
    norm = f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps={meta['fps']},format=yuv420p,setsar=1"
    if meta["audio"] and ig["audio"]:
        graf = (f"[0:v]{norm}[g];[1:v]trim=start={corte},setpts=PTS-STARTPTS,{norm}[c];"
                f"[0:a]aresample=48000[ga];[1:a]atrim=start={corte},asetpts=PTS-STARTPTS,aresample=48000[ca];"
                f"[g][ga][c][ca]concat=n=2:v=1:a=1[v][a]")
        mapa = ["-map", "[v]", "-map", "[a]", "-c:a", "aac", "-b:a", "256k"]
    else:
        graf = f"[0:v]{norm}[g];[1:v]trim=start={corte},setpts=PTS-STARTPTS,{norm}[c];[g][c]concat=n=2:v=1:a=0[v]"
        mapa = ["-map", "[v]"]
    r = sale(["ffmpeg", "-v", "error", "-y", "-i", str(gancho), "-i", str(original), "-filter_complex", graf, *mapa,
              "-c:v", "libx264", "-preset", "veryfast", "-crf", "14", str(out)])
    if r.returncode:
        sys.exit(f"No pude unir el gancho {gancho}:\n{r.stderr[-1200:]}")
    return out


def diferencia(a, b, dur):
    """Cuánto se parecen dos vídeos a ojo: media de la diferencia de 6 fotogramas en gris 32×32 (0 = idénticos)."""
    def miniaturas(v):
        out = []
        for k in range(6):
            t = dur * (k + 0.5) / 6
            r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", str(v), "-frames:v", "1",
                                "-vf", "scale=32:32,format=gray", "-f", "rawvideo", "-"], capture_output=True)
            out.append(r.stdout)
        return out
    ma, mb = miniaturas(a), miniaturas(b)
    difs = [sum(abs(x - y) for x, y in zip(p, q)) / max(len(p), 1) for p, q in zip(ma, mb) if p and q]
    return sum(difs) / max(len(difs), 1)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("video")
    p.add_argument("--titulos")
    p.add_argument("--titulo-y", type=int, default=260)
    p.add_argument("--titulo-s", type=float, default=3.0)
    p.add_argument("--caja", choices=["negra", "blanca", "ninguna"], default="negra")
    p.add_argument("--tapa", type=lambda x: tuple(int(n) for n in x.split("-")))
    p.add_argument("--fuente")
    p.add_argument("--ganchos", nargs="*")
    p.add_argument("--corte", type=float)
    p.add_argument("--espejo", action="store_true")
    p.add_argument("--pie")
    p.add_argument("--hashtags", default="")
    p.add_argument("--desde")
    p.add_argument("--horas", default=HORAS)
    p.add_argument("--salida")
    p.add_argument("--n", type=int, default=5)
    p.add_argument("--musica", nargs="*")
    p.add_argument("--quitar", nargs="*")
    p.add_argument("--ver-pausas", action="store_true")
    p.add_argument("--titulo-original")
    p.add_argument("--aun-asi", action="store_true")
    p.add_argument("--srt")
    p.add_argument("--sin-voz", action="store_true")
    a = p.parse_args()

    for prog in ("ffmpeg", "ffprobe"):
        if not shutil.which(prog):
            sys.exit(f"Falta {prog}. En Mac: brew install ffmpeg · En Windows: winget install ffmpeg · En Linux: apt install ffmpeg")
    video = Path(a.video).expanduser().resolve()
    if not video.exists():
        sys.exit(f"No existe {video}")
    if a.ganchos and a.corte is None:
        sys.exit("Con --ganchos hace falta --corte: el segundo en que acaba el comienzo en tu vídeo")
    meta = info(video)
    if a.ver_pausas:
        print(f"Pausas de la voz en {video.name} ({meta['dur']:.1f} s); una frase va de una pausa a la siguiente:")
        print("\n".join(f"  {x:7.2f} - {y:7.2f}" for x, y in pausas(video)))
        return
    if a.musica and not meta["audio"]:
        sys.exit("--musica: el vídeo no tiene sonido")
    for c in a.musica or []:
        if not Path(c).expanduser().exists():
            sys.exit(f"No existe {c}")
    if meta["w"] > meta["h"]:
        print("⚠ El vídeo es horizontal: las copias salen en vertical (1080×1920) recortando los lados.")
    titulos = []
    if a.titulos:
        titulos = [l.strip() for l in Path(a.titulos).expanduser().read_text(encoding="utf-8").splitlines() if l.strip()]
        if len(titulos) < a.n:
            sys.exit(f"{a.titulos} tiene {len(titulos)} titulares y hacen falta {a.n}")
    quitar = [leer_quitar(q) for q in (a.quitar or [])]
    if quitar:
        huecos = pausas(video, 0.12)
        for k, q in enumerate(quitar):
            comprobar_cortes(q, huecos, f"--quitar de la copia {k + 1}")
            if a.corte is not None and any(x < a.corte for x, _ in q):
                sys.exit(f"--quitar de la copia {k + 1}: con --ganchos solo se quita después de --corte ({a.corte} s)")

    # 🚨 La regla de mínimos (distintas.py): entre el vídeo y sus copias no se repite canción, estilo de subtítulos,
    # contenido ni titular (ni velocidad). Si no se cumple, el aviso y para, salvo --aun-asi con el sí de la persona
    estilos = list(SUBS)
    copias = [{"cancion": str(Path(a.musica[i % len(a.musica)]).expanduser().resolve()) if a.musica else None,
               "subtitulos": ("sin subtítulos" if a.sin_voz else estilos[i % len(estilos)] if a.srt else None),
               "contenido": (str(Path(a.ganchos[i % len(a.ganchos)]).expanduser().resolve()) if a.ganchos else "su comienzo",
                             "+".join(f"{x:.2f}-{y:.2f}" for x, y in quitar[i % len(quitar)]) or "entero"
                             if quitar else "entero"),
               "titular": titulos[i] if titulos else None,
               "velocidad": VELOCIDAD[i % len(VELOCIDAD)] if i < len(VELOCIDAD) else None}
              for i in range(a.n)]
    original = {"cancion": "la del vídeo", "subtitulos": "sin subtítulos" if a.sin_voz else "los del vídeo",
                "contenido": ("su comienzo", "entero"), "titular": a.titulo_original or "el del vídeo", "velocidad": 1.0}
    avisos = distintas.revisar(copias, original)
    if avisos and not a.aun_asi:
        sys.exit(distintas.aviso(avisos, arreglos=(
            "Canción: --musica con 5 canciones, una por copia (si el vídeo ya trae música, mejor exportarlo sin ella).",
            "Subtítulos: --srt con los subtítulos del vídeo (y el vídeo exportado SIN ellos): cada copia los lleva en\n"
            "     otro estilo. Si no habla nadie, --sin-voz.",
            "Contenido: --ganchos (otros comienzos grabados) y/o --quitar, una frase distinta fuera en cada copia\n"
            "     (--ver-pausas para elegirlas). Ninguna combinación repetida.",
            "Titular: --titulos, 5 frases distintas (y --titulo-original con el que ya lleva el vídeo).",
            "Menos copias: --n 3. Mejor 3 que cumplan que 5 que se repitan.")))
    salida = Path(a.salida).expanduser() if a.salida else video.with_name(video.stem + "-pruebas")
    salida.mkdir(parents=True, exist_ok=True)

    ini_libre, fin_libre = silencios(video, meta["dur"])
    meta["recorte"] = [(min(ARRANQUE[i % 5], ini_libre), min(FINAL[i % 5], fin_libre)) for i in range(a.n)]
    meta["quitar"] = [quitar[i % len(quitar)] if quitar else [] for i in range(a.n)]
    meta["musica"] = [Path(a.musica[i % len(a.musica)]).expanduser() if a.musica else None for i in range(a.n)]
    meta["srt"] = leer_srt(a.srt) if a.srt else None
    meta["subs"] = [estilos[i % len(estilos)] for i in range(a.n)]
    if avisos:
        (salida / "AVISO-poco-distintas.txt").write_text(distintas.aviso(avisos), encoding="utf-8")
        print("⚠ Hechas igual con --aun-asi:\n  " + "\n  ".join(avisos))
    print(f"{video.name}: {meta['dur']:.1f} s, {meta['w']}×{meta['h']}, {meta['fps']} fps · silencio al principio "
          f"{ini_libre:.2f} s y al final {fin_libre:.2f} s (solo ahí se recorta)")

    with tempfile.TemporaryDirectory() as tmp:
        hechas = []
        for i in range(a.n):
            base, m = video, dict(meta)
            if a.ganchos:
                base = con_gancho(Path(a.ganchos[i % len(a.ganchos)]).expanduser(), video, a.corte, meta, tmp, i)
                m.update(info(base))
                m["recorte"] = [(0.0, meta["recorte"][i][1])] * a.n
                corre = m["dur"] - (meta["dur"] - a.corte)   # el original, desde --corte, empieza aquí en esta base
                m["quitar"] = [[(x + corre, y + corre) for x, y in meta["quitar"][i]]] * a.n
                if meta["srt"] is not None:   # los subtítulos del vídeo desde --corte; el comienzo nuevo va sin ellos
                    m["srt"] = [(x + corre, y + corre, t) for x, y, t in meta["srt"] if x >= a.corte - 0.05]
            lineas = [x.strip() for x in titulos[i].split(" / ")] if titulos else []
            out = salida / f"{video.stem}-prueba-{i + 1}.mp4"
            print(f"  copia {i + 1}/{a.n}…", end="", flush=True)
            una_copia(i, base, m, a, tmp, lineas, out)
            hechas.append(out)
            print(f" {out.name}")

    # Pies: el del original (su primera línea igual, así la respuesta automática de «comenta X» también contesta)
    # y 5 hashtags en otro orden en cada copia
    tags = a.hashtags.split()
    pie = Path(a.pie).expanduser().read_text(encoding="utf-8").strip() if a.pie else ""
    for i, out in enumerate(hechas):
        random.Random(i).shuffle(tags)
        texto = (pie + ("\n\n" + " ".join(tags[:5]) if tags else "")).strip()
        out.with_suffix(".pie.txt").write_text(texto + "\n", encoding="utf-8")

    # Horario: una al día, a una hora distinta cada día, desde mañana (o --desde)
    dia0 = dt.date.fromisoformat(a.desde) if a.desde else dt.date.today() + dt.timedelta(days=1)
    horas = [h.strip() for h in a.horas.split(",") if h.strip()]
    filas = [f"{(dia0 + dt.timedelta(days=i)).isoformat()}  {horas[(i * 2 + 1) % len(horas)]}  {o.name}"
             for i, o in enumerate(hechas)]
    (salida / "horario.txt").write_text("\n".join(filas) + "\n", encoding="utf-8")

    # Comprobación: cada copia dura lo que debe, tiene sonido si el original lo tenía, y no se parece al original
    print("\nComprobación técnica (diferencia de imagen con el original; por debajo de 4 algo no se aplicó). No dice si\n"
          "Instagram la ve distinta: eso lo deciden los cambios grandes, que ya se comprobaron antes de empezar.")
    for i, out in enumerate(hechas):
        m = info(out)
        d = diferencia(video, out, min(m["dur"], meta["dur"]))
        aviso = "" if d >= 4 else "  ⚠ casi idéntica al original: revisa que se aplicaron los cambios"
        print(f"  {out.name}: {m['dur']:.1f} s · {m['w']}×{m['h']} · {'con' if m['audio'] else 'SIN'} sonido · diferencia {d:.1f}{aviso}")
    hoja = salida / "hoja.jpg"
    entradas = []
    for o in hechas:
        entradas += ["-ss", str(min(1.0, a.titulo_s - 0.5) if titulos else 1.0), "-i", str(o)]
    sale(["ffmpeg", "-v", "error", "-y", *entradas, "-filter_complex",
          "".join(f"[{k}:v]scale=270:480[v{k}];" for k in range(len(hechas))) +
          "".join(f"[v{k}]" for k in range(len(hechas))) + f"hstack=inputs={len(hechas)}", "-frames:v", "1", str(hoja)])
    print(f"\nListo en {salida}\n  Horario:\n    " + "\n    ".join(filas) + f"\n  Hoja para revisarlas: {hoja}")


if __name__ == "__main__":
    main()
