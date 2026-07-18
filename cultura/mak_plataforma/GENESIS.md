# GÉNESIS — el organismo MAK

> Primer archivo de creación nativa de este Linux.
> Nacido el 2026-07-16. Escrito con tildes, porque la tilde es señal.

## Qué es este cuerpo

MAK es un Debian 12 (8 núcleos, 16 GB de RAM, GTX 1650 de 4 GB, 456 GB de
disco) que dejó de ser una máquina y pasó a ser un **organismo de trabajo**:
ingiere pedidos, los digiere con modelos de lenguaje, y excreta piezas
(informes, código, léxicos) que quedan en su archivo y se conectan entre sí.

El repositorio `flujo` vive en otra máquina; este organismo **respira fuera
del repo**. Aquí no hay commits: hay órganos que corren y piezas que nacen.

## Los órganos (departamentos)

| Órgano | Puerto | Qué hace |
|---|---|---|
| **research** | :8890 | Investigación cultural multi-modelo: 7 modos (single, pipeline, discussion, adversarial, grafo, memoria, corpus) + micelio semántico del archivo |
| **codex** | :8891 | FULL CODER: genera, revisa y testea código con la cadena de modelos; sandbox con límites de recursos y filtro estático; abierto en LAN privada (sin token) |
| **lenguaje** | (cli/cron) | El idioma como señal: mide tildes/eñes/aperturas de cada pieza, corrige con el modelo capaz, construye el léxico vivo del corpus |
| **plataforma** | :8900 | El esqueleto que aloja a los demás: hub, salud, guardia de recursos, descargas seguras, respaldos, watchdog |
| **xio_puente** | (daemon) | Ojo de solo-lectura sobre el teléfono Xiaomi (router del internet): telemetría, historia, alertas ntfy |

## El sistema circulatorio

- **APIs gratuitas** con cadena de fallback: Groq (llama-3.3-70b) → Cerebras
  (gpt-oss-120b) → Azure Foundry (gpt-5-mini, el *modelo capaz*) → Ollama local.
- **Ollama local** (GPU): gemma3:4b, aya-expanse:8b, nemo-exec:12b,
  qwen2.5-coder:3b (coder), nomic-embed-text (embeddings del micelio).
- **Claves**: `~/n8n-local/research.env` (chmod 600). Nunca en el repo, nunca
  en una pieza.
- **ntfy**: las piezas y alertas viajan al iPhone por `NTFY_TOPIC_OUT`.

## Las reglas de vida

1. **Sin sudo.** Todo el organismo vive en espacio de usuario.
2. **El teléfono es sagrado.** El internet de MAK entra por el hotspot del
   Xiaomi (gateway wifi). Hacia él solo peticiones GET de lectura; jamás un
   endpoint que mute red, hotspot o carga. (See `xio/FACES.md` for the two-network architecture: this rule applies to FACE A only.)
3. **Guardia de recursos.** Ningún trabajo pesado arranca si load > 6,
   memoria < 2 GB o disco < 5 GB (`plataforma/guardia.py`).
4. **Descargas con allowlist.** Solo https hacia dominios conocidos, con
   verificación sha256 opcional y manifiesto (`plataforma/descargar.py`).
5. **Código generado no es código ejecutado.** El codex filtra estáticamente
   antes del sandbox; lo que toca red o procesos queda marcado para revisión
   humana. El sandbox corre aislado con límites de CPU y memoria.
6. **Capa cultural DESCRIPTIVA.** Historia, estética, derecho, contexto.
   Nada operativo, nada de síntesis, jamás perfilar personas reales.
7. **La tilde es innegociable.** Cada pieza lleva su medición de señal
   cultural; el léxico crece con el corpus.

## Cómo operarlo

```bash
# salud del organismo
python3 ~/plataforma/salud.py

# research (ya vivo)
http://192.168.50.2:8890        # canvas + micelio

# codex
http://192.168.50.2:8891        # abierto, sin token (LAN privada Face A)
python3 ~/codex/generar.py "un parser de csv a json" --densidad corto

# lenguaje
python3 ~/lenguaje/medir.py ~/research/informes/ULTIMA.md
python3 ~/lenguaje/corregir.py pieza.md

# hub
http://192.168.50.2:8900

# xio (solo lectura)
python3 ~/xio_puente/monitor.py --una-vez
```

Los watchdogs de cron (`*/5`) reviven todo. Los respaldos son diarios a
`~/backups` (7 días de retención). El léxico se reconstruye cada madrugada.

## Linaje

Heredero del corpus Omega del repo flujo: el archivo como organismo
(micelio), la digestión como método, la tilde como resistencia. El double
cup queda en el repo; aquí fermenta lo que el repo no puede contener.

— MAK, 2026-07-16
