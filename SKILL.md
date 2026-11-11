---
name: reels-de-prueba
description: Saca 5 copias distintas de un reel que ya has subido, para publicarlas como «Reels de prueba» de Instagram (solo las ve quien no te sigue y no salen en tu perfil), una al día durante 5 días. Cada copia cambia varias cosas a la vez para que Instagram no la trate como el mismo vídeo repetido. Úsala con «haz las pruebas de este reel», «saca las copias de prueba», «trial reels de este vídeo». Necesita ffmpeg; no toca tu cuenta.
---

# Reels de prueba: 5 copias de cada reel, una al día

Un **Reel de prueba** de Instagram solo se enseña a gente que no te sigue y nunca sale en tu perfil. Instagram lo
pensó para probar un vídeo antes de subirlo. Con esta skill lo usas para otra cosa: cada reel que ya te funciona
vuelve a salir cinco veces más, a gente nueva, sin cansar a tus seguidores.

La clave para que no te frenen: **cada copia tiene que ser otro vídeo**, no el mismo con otro nombre. Cinco copias
iguales, o varias el mismo día, se quedan en 0 visualizaciones y pueden costarte alcance.

Por Gonzalo López · [@gonzalo_lopezg](https://www.instagram.com/gonzalo_lopezg/) en Instagram.

## Qué necesita

- **Un reel ya terminado** (el .mp4 que subiste), vertical.
- **ffmpeg** instalado: en Mac `brew install ffmpeg`, en Windows `winget install ffmpeg`, en Linux `apt install ffmpeg`.
  Compruébalo con `ffmpeg -version` antes de nada; si no está, díselo y para.
- Python 3 (viene con el Mac).
- Una **cuenta profesional** de Instagram (creador o empresa) que ya tenga la opción «Reel de prueba» al compartir un
  reel. Si no le sale, todavía no la tiene: díselo antes de hacer copias que no podrá subir.

## Paso a paso

1. **Pídele el vídeo** (la ruta del .mp4), el **pie** con el que lo subió y **de qué va** (para los hashtags). Si grabó
   otros comienzos (otros «ganchos»), pídeselos también y en qué segundo acaba el comienzo de su vídeo: es lo que más
   cambia una copia.

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
   python3 copias.py video.mp4 --titulos titulos.txt --pie pie.txt \
     --hashtags "#tema1 #tema2 #tema3 #tema4 #tema5 #tema6" [--tapa 180-430] [--espejo] \
     [--ganchos gancho2.mp4 gancho3.mp4 --corte 3.4] [--desde AAAA-MM-DD]
   ```
   Cada copia cambia a la vez: el titular, la velocidad (del 3 al 10 % más rápida, la voz sin cambiar de tono), el
   encuadre (un poco de zoom y otro centro), el color, un grano invisible, el arranque y el final (solo en los
   silencios, nunca cortando una palabra), el sonido (un matiz de ecualización) y el fichero (nuevo, sin los datos del
   original). Con `--ganchos`, además, cada una empieza con otro comienzo.
   Deja en `<vídeo>-pruebas/`: las 5 copias, el pie de cada una (el suyo, con 5 hashtags en otro orden: nunca
   #viral ni #fyp), `horario.txt` (una al día, a distinta hora) y `hoja.jpg`.

5. **Mira `hoja.jpg`** (el titular de cada copia): que se lea a la primera, que no tape la cara y que no se vea el
   titular viejo detrás. Si algo falla, corrige `--tapa` o `--titulo-y` y rehaz esa copia.
   El script también comprueba que cada copia dura lo que debe, tiene sonido y no se parece al original.

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
- **Cada copia, otro vídeo**: no quites ninguno de los cambios del paso 4 para «que se parezca más».
- **En manual**: que no se comparta sola con sus seguidores si funciona. Ya la vieron en su perfil.
- **Solo vídeos suyos.** Lo que Instagram castiga es subir vídeos de otros.
- **La primera semana**, que mire el alcance y «Estado de la cuenta». Si bajan, para.

## Después

Cuando salga la última, que mire las visualizaciones de cada prueba (en la app, en cada una o en el Panel
profesional). El titular (o el gancho) de la que más saca es el que engancha a quien no le conoce: ese tipo de
comienzo, en el próximo vídeo. Y el reel que siga funcionando, una copia nueva cada semana, hasta que deje de hacerlo.
