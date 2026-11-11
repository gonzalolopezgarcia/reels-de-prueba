# Reels de prueba

La skill para Claude Code con la que saco **5 copias distintas de cada reel** y las subo como «Reels de prueba» de
Instagram, una al día. Solo las ve gente que no te sigue y no salen en tu perfil.

**Cada copia tiene que ser otro vídeo de verdad.** Entre tu vídeo y sus 5 copias no se repite **la canción, el estilo
de subtítulos, el contenido** (otro comienzo u otra frase fuera) **ni el titular**, y encima cambian velocidad,
encuadre y color. Si algo se repite, la skill te avisa y no las hace hasta que digas que sí. Mejor 3 que cumplan que 5
que se repitan.

Por Gonzalo López · [@gonzalo_lopezg](https://www.instagram.com/gonzalo_lopezg/)

## Instalar

Necesitas [Claude Code](https://claude.com/claude-code), Python 3 y ffmpeg (`brew install ffmpeg` en Mac,
`winget install ffmpeg` en Windows).

```bash
git clone https://github.com/gonzalolopezgarcia/reels-de-prueba ~/.claude/skills/reels-de-prueba
```

## Usar

Abre Claude Code y dile: «Haz las pruebas de este reel» con la ruta de tu vídeo. Te pide lo que hace falta para que
las copias sean distintas (tus subtítulos en .srt, 5 canciones, qué frases sobran y otros comienzos si los grabaste), te propone 5 titulares,
hace las copias con tu sí y te deja los pies y el horario: una al día, desde la app, con «Reel de prueba» activado.

Todo lo que hace y por qué está en [SKILL.md](SKILL.md).
