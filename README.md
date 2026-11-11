# Reels de prueba

La skill para Claude Code con la que saco **5 copias distintas de cada reel** y las subo como «Reels de prueba» de
Instagram, una al día. Solo las ve gente que no te sigue y no salen en tu perfil.

**Cada copia tiene que ser otro vídeo de verdad**: al menos 3 cambios grandes frente al original (otro comienzo
grabado, otra frase quitada, otro titular, otra canción). El color, la velocidad o el espejo solos no bastan:
Instagram reconoce el vídeo igual. Si tus copias no llegan, la skill te avisa y no las hace hasta que digas que sí.
Mejor 3 distintas que 5 parecidas.

Por Gonzalo López · [@gonzalo_lopezg](https://www.instagram.com/gonzalo_lopezg/)

## Instalar

Necesitas [Claude Code](https://claude.com/claude-code), Python 3 y ffmpeg (`brew install ffmpeg` en Mac,
`winget install ffmpeg` en Windows).

```bash
git clone https://github.com/gonzalolopezgarcia/reels-de-prueba ~/.claude/skills/reels-de-prueba
```

## Usar

Abre Claude Code y dile: «Haz las pruebas de este reel» con la ruta de tu vídeo. Te pide lo que hace falta para que
las copias sean distintas (otros comienzos si los grabaste, 5 canciones, qué frases sobran), te propone 5 titulares,
hace las copias con tu sí y te deja los pies y el horario: una al día, desde la app, con «Reel de prueba» activado.

Todo lo que hace y por qué está en [SKILL.md](SKILL.md).
