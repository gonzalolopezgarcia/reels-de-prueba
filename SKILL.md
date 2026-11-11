---
name: reels-de-prueba
description: Saca copias distintas (5 por defecto) de un reel que ya has subido, para publicarlas como «Reels de prueba» de Instagram (solo las ve quien no te sigue y no salen en tu perfil), una al día. Entre el vídeo y sus copias no se repite canción, estilo de subtítulos, contenido ni titular, para que Instagram no las trate como el mismo vídeo; si algo se repite, avisa y no las hace sin tu sí. Úsala con «haz las pruebas de este reel», «saca las copias de prueba», «trial reels de este vídeo». Necesita ffmpeg; no toca tu cuenta.
---

# Reels de prueba: 5 copias de cada reel, una al día

Un **Reel de prueba** de Instagram solo se enseña a gente que no te sigue y nunca sale en tu perfil. Instagram lo
pensó para probar un vídeo antes de subirlo. Con esta skill lo usas para otra cosa: cada reel que ya te funciona
vuelve a salir cinco veces más, a gente nueva, sin cansar a tus seguidores.

La clave para que no te frenen: **cada copia tiene que ser otro vídeo**, no el mismo con otro nombre. Cinco copias
iguales, o varias el mismo día, se quedan en 0 visualizaciones y pueden costarte alcance.

## 🚨 La regla de mínimos: entre los 6 vídeos, nada se repite

El vídeo y sus 5 copias son 6 vídeos. **Entre ellos no puede haber dos con:**

| Lo mismo en… | Cómo cambia en cada copia | Opción |
|---|---|---|
| **la canción** | Una canción de fondo distinta por copia, nunca la del vídeo | `--musica` (5 canciones) |
| **el estilo de subtítulos** | Los mismos subtítulos, en otro estilo cada copia: blanco con borde, caja negra, amarillo, caja blanca, mayúsculas, caja amarilla | `--srt` (y el vídeo exportado **sin** subtítulos) |
| **el contenido** | Otro comienzo grabado y/o otra frase fuera en cada copia: ninguna combinación repetida | `--ganchos`, `--quitar` |
| **el titular de arriba** | Otra frase cada copia, la misma idea dicha de otra forma | `--titulos` |

Y encima, todo lo distinto que se pueda: velocidad (tampoco se repite), encuadre, color, grano, arranque y final. Solos
no bastan: Instagram reconoce el vídeo por lo que se ve y se oye.

- `copias.py` lo comprueba antes de empezar (`distintas.py`) y **para con un aviso** si algo se repite.
- **Si no llega para 5, haz menos** (`--n 3`). Mejor 3 que cumplan que 5 que se repitan.
- Un vídeo en el que no habla nadie (sin voz ni subtítulos): `--sin-voz`, y el estilo de subtítulos no se pide.
- 🚨 **Si aun así la persona las quiere hacer**: enséñale el aviso entero, con lo que se repite, y pregúntale una vez:
  «Estas copias se parecen demasiado y pueden quedarse en 0 o costarte alcance. ¿Las hago así igualmente?». Solo con
  un sí claro a ese aviso, `--aun-asi`. Nunca por tu cuenta, ni aunque te haya dicho «hazlo todo» antes: tiene que
  haber leído el aviso. Queda un `AVISO-poco-distintas.txt` en la carpeta.

## Qué necesita

- **Un reel ya terminado** (el .mp4 que subiste), vertical.
- **ffmpeg** instalado: en Mac `brew install ffmpeg`, en Windows `winget install ffmpeg`, en Linux `apt install ffmpeg`.
  Compruébalo con `ffmpeg -version` antes de nada; si no está, díselo y para.
- Python 3 (viene con el Mac).
- Una **cuenta profesional** de Instagram (creador o empresa) que ya tenga la opción «Reel de prueba» al compartir un
  reel. Si no le sale, todavía no la tiene: díselo antes de hacer copias que no podrá subir.

## Paso a paso

1. **Pídele el vídeo** (la ruta del .mp4), el **pie** con el que lo subió y **de qué va** (para los hashtags). Y estas
   cuatro cosas, que deciden si las copias cumplen la regla de mínimos (arriba):
   - **Sus subtítulos**: el vídeo exportado **sin** subtítulos y su `.srt` (CapCut, Premiere, DaVinci o Edits lo
     exportan; si no, que Claude lo transcriba con Whisper si lo tiene instalado). Sin `.srt`, todas las copias llevan
     el mismo estilo que el vídeo y no se cumple. Si no habla nadie, `--sin-voz`.
   - **¿Grabó otros comienzos** (otros «ganchos»)? Pídeselos y en qué segundo acaba el comienzo de su vídeo. Si no, dile
     que con 2 o 3 comienzos más, de un minuto de grabar, las copias son mucho más distintas; si no quiere, se sigue.
   - **¿El vídeo lleva música de fondo metida?** Si no, pídele 5 canciones (.mp3/.m4a) para `--musica`. Si la lleva,
     lo mejor es que exporte el vídeo sin ella desde su editor y cada copia lleve la suya; si no puede, ese cambio no
     está y hacen falta los otros tres.
   - **¿Qué frases sobran?** Pregúntale qué frases del cuerpo se pueden quitar sin que se deje de entender (ni el
     comienzo ni el final). Con `--ver-pausas` ves dónde empieza y acaba cada frase: cada `--quitar` va de una pausa a
     otra, nunca cortando una palabra (el script se niega si cae encima de la voz).
     - **Aunque tenga otros comienzos, que cada copia quite además una frase distinta**: el cuerpo es casi todo el
       vídeo, y una copia que solo cambia los primeros segundos repite el resto entero.
     - **Frases pegadas**: en un vídeo ya editado, muchas frases empiezan sin pausa (el editor la quitó) y solo queda
       un fotograma en silencio. `--ver-pausas` lo marca como «silencio de un fotograma» con el segundo exacto: el
       corte va ahí, ni antes (se lleva la cola de la frase anterior) ni después (se come el principio de la siguiente).

2. **Mira el vídeo antes de tocar nada.** Saca un fotograma del segundo 1 y otro de la mitad:
   ```bash
   ffmpeg -v error -ss 1 -i video.mp4 -frames:v 1 -vf "drawgrid=w=1080:h=50:t=1:c=red@0.5" f1.jpg
   ```
   Míralos y apunta:
   - **¿Lleva su propio titular arriba?** Entonces cada copia lo difumina y pone el nuevo encima: `--tapa Y0-Y1` con
     la franja que ocupa (en píxeles de un vídeo de 1080×1920, con 70 px de margen por arriba y por abajo, porque cada
     copia hace un poco de zoom). Si no lleva, el titular nuevo va en `--titulo-y 260`.
   - **¿Lleva letras en el vídeo** (subtítulos, una pantalla, un cartel)? Entonces **sin `--espejo`**: saldrían del
     revés. Solo si no hay ninguna letra, `--espejo` voltea la 2.ª y la 4.ª.
   - Dónde está su cara: el titular nunca encima.

3. **Escribe 5 titulares** en `titulos.txt`, uno por línea (` / ` parte el titular en dos líneas):
   - **La misma idea que el titular del vídeo, dicha de cinco formas**, no cinco temas distintos. Si el vídeo va de
     «Claude ya usa tu móvil», todos van de eso: «Tu móvil ya trabaja / solo con Claude», «La IA ya maneja / tu móvil».
   - Que cada uno diga **el nombre de lo que trata** (la herramienta, la marca, el tema).
   - Si hay **un número real** (guardados, estrellas, vistas, euros), que uno lo lleve: suele enganchar más.
   - Dos líneas de unas 5 palabras como mucho. **Sin comas**: dos puntos o un «=».
   - 🚨 **Enséñaselos y espera su sí** antes de hacer las copias.

4. **Hazlas** (unos minutos por copia):
   ```bash
   python3 copias.py video.mp4 --ver-pausas      # dónde empieza y acaba cada frase
   python3 copias.py video-sin-subtitulos.mp4 --srt subtitulos.srt \
     --titulos titulos.txt --titulo-original "El titular que ya lleva" --pie pie.txt \
     --hashtags "#tema1 #tema2 #tema3 #tema4 #tema5 #tema6" \
     --quitar "8.0-10.5" "10.6-14.2" "14.2-16.3" "16.3-21.0" "21.0-22.1" \
     --musica c1.mp3 c2.mp3 c3.mp3 c4.mp3 c5.mp3 [--tapa 180-430] [--espejo] \
     [--ganchos gancho2.mp4 gancho3.mp4 --corte 3.4] [--desde AAAA-MM-DD] [--n 3]
   ```
   Si para con «⚠ ESTAS COPIAS NO SON LO BASTANTE DISTINTAS», arregla lo que dice que se repite (otra canción, el
   `.srt`, otra frase fuera u otro comienzo, otro titular) o baja `--n`. Solo si la persona, después de leer el aviso, dice que las quiere igual: `--aun-asi`.
   Cada copia cambia a la vez: el titular, la velocidad (del 3 al 10 % más rápida, la voz sin cambiar de tono), el
   encuadre (un poco de zoom y otro centro), el color, un grano invisible, el arranque y el final (solo en los
   silencios, nunca cortando una palabra), el sonido (un matiz de ecualización) y el fichero (nuevo, sin los datos del
   original). Con `--ganchos`, además, cada una empieza con otro comienzo.
   Deja en `<vídeo>-pruebas/`: las 5 copias, el pie de cada una (el suyo, con 5 hashtags en otro orden: nunca
   #viral ni #fyp), `horario.txt` (una al día, a distinta hora) y `hoja.jpg`.

5. **Mira `hoja.jpg`** (el titular de cada copia): que se lea a la primera, que no tape la cara y que no se vea el
   titular viejo detrás. Si algo falla, corrige `--tapa` o `--titulo-y` y rehaz esa copia.
   El script también comprueba que cada copia dura lo que debe y tiene sonido. Que sea otro vídeo para Instagram lo
   deciden los cambios grandes, comprobados antes de empezar.

6. **Súbelas, una al día, según `horario.txt`.**
   - **Desde el móvil (lo normal):** pásale los 5 vídeos al móvil (AirDrop, Drive…). Cada día: Instagram → «+» →
     Reel → la copia de ese día → Siguiente → pega su pie → activa **«Reel de prueba»** → Compartir. Si quiere
     dejarlas todas listas de una vez, en «Configuración avanzada» → «Programar» elige el día y la hora de cada una.
   - **Por la API oficial** (solo si ya la tiene montada): el contenedor del reel con `media_type=REELS`,
     `share_to_feed=false` y `trial_params={"graduation_strategy":"MANUAL"}`.
   - 🚨 **Nunca desde instagram.com en el navegador ni con nada que pulse la app por él**: Meta marca la cuenta por
     «comportamiento automatizado».

## Para que no le frenen la cuenta

- **Una al día.** Nunca dos copias del mismo vídeo el mismo día: con nueve el mismo día, las copias bajaron de unas
  3.400 visualizaciones a 190 en una semana, y varias se quedaron a 0.
- **Cada copia, otro vídeo**: entre los 6, ni canción, ni estilo de subtítulos, ni contenido, ni titular repetidos
  (la regla, arriba). No quites ninguno de los cambios del paso 4 para «que se parezca más».
- **No más de una prueba al día en total las dos primeras semanas** (aunque sean de reels distintos), mientras miras
  cómo responde la cuenta. Es precaución, no algo medido.
- **En manual**: que no se comparta sola con sus seguidores si funciona. Ya la vieron en su perfil.
- **Solo vídeos suyos.** Lo que Instagram castiga es subir vídeos de otros.
- **La primera semana**, que mire el alcance y «Estado de la cuenta». Si bajan, o una prueba se queda por debajo de
  ~100 visualizaciones en 24 h, para las que quedan de ese reel y no hagas más en una semana.

## Después

Cuando salga la última, que mire las visualizaciones de cada prueba (en la app, en cada una o en el Panel
profesional). El titular (o el gancho) de la que más saca es el que engancha a quien no le conoce: ese tipo de
comienzo, en el próximo vídeo. Y el reel que siga funcionando, una copia nueva cada semana, hasta que deje de hacerlo.
