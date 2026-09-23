# Formula de generadores IA (MakeSong / Suno-class)

MakeSong.com no publica codigo fuente ni API documentada.
La formula operativa es la de custom mode Suno / MusicGPT / musicapi.ai.
No se incorpora scraping ni reverse de endpoints privados.

## Formula canonica

```
custom_mode     true
prompt          LETRA con etiquetas de seccion
style / tags    genero, mood, voz, tempo, produccion, exclusiones
title           titulo corto
instrumental    false | true
model           V6
variety         Off
```

Etiquetas: [Intro] [Verse] [Chorus] [Bridge] [Break] [Outro]

Separar LETRA (prompt) de PRODUCCION (style box).

## Formula Troya

Style box:

```
spoken word, intimate male voice in Spanish,
sparse arrangement, almost spoken, dark, no pop chorus,
no festival drop, no bright synth lead,
dry room, close mic, low reverb
```

Bajar WAV. HPF 170 Hz. Montar sobre 00B o 00C a 118 Dm.

## APIs publicas equivalentes

- sunoapi.org POST /api/v1/generate
- musicapi.ai POST /api/v1/sonic/create
- MusicGPT POST /api/public/v2/MusicAI

Usar solo con clave del usuario. Este repo no guarda API keys.

## Open source real

ACE-Step, MusicGen, InspireMusic, YuE2. MakeSong no.
