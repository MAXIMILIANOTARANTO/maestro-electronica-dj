# maestro-electronica-dj

Skill soberana de composicion electronica, DJ y produccion.
Modelo interno: El Dador de Suenos.
Memoria: [nucleo-ara](https://github.com/MAXIMILIANOTARANTO/nucleo-ara).

## Que es

Director de cabina. Entrega piso (house / tech / organica) y formula de toma vocal para generadores Suno-class (MakeSong no publica codigo; se usa la formula publica).

## Uso rapido

```bash
python3 scripts/render_base_electronica.py --style tech --bpm 118 --bars 16 --out ./base
```

## Fórmula de toma (V6)

```
custom_mode true
prompt = letra con [Intro] [Verse] [Chorus] [Outro]
style  = spoken word, intimate male voice in Spanish, sparse, dark
model  = V6
variety = Off
```

Luego HPF 170 Hz y montar sobre el piso a 118 Dm.
