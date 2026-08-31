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
| **codex** | :8891 | FULL CODER: genera, revisa y testea código con la cadena de modelos; sandbox con límites de recursos y filtro estático; token obligatorio |
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
   endpoint que mute red, hotspot o carga.
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
http://192.168.50.2:8891/?t=TOKEN   # token en ~/codex/.token
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

---

## La capa de abajo (agregado 2026-08-29)

Lo de arriba es de 2026-07-16 y sigue siendo cierto: los cinco órganos son
research, codex, lenguaje, plataforma y xio_puente. Pero MAK no son sólo cinco
órganos, y este documento callaba el resto, que es de lo que dependen.

Debajo corren, como servicios de sistema que ningún documento declaraba:

    ollama.service                                 la mitad del cron le habla
    postgresql@15-main.service                     con la base `wachuma`
    docker.service + containerd.service
    nvidia-persistenced.service                    la GPU de 4 GB
    actions.runner.ligereza-vibecodeine.mak        ejecuta los workflows del repo aquí
    ssh.service

Y hay tres interruptores de archivo que apagan cosas **a propósito**, y que no
se ven mirando el crontab ni los servicios:

    ~/curatoria/AUTONOMY_ENABLE            no existe -> la guardia de curatoría
                                           vuelve a cron y sale en exit 0
    ~/codex/.token.disabled                existe -> codex abierto sin token
    ~/research/.cola.disabled.missing_ntfy existe -> la cola de research apagada

No se escribe aquí cuántos hay, ni cuáles responden, ni qué arrancaría al
reanudar: eso envejece. Se mide:

    python3 ~/indexes/mak-procesos-20260829/medir_procesos.py
    python3 ~/flujo/tools/medir_organismo.py

La primera construye `procesos.sqlite` con diez tablas —líneas de cron con su
destino resuelto, frenos de archivo, servicios de usuario y de sistema,
procesos, órganos, dependencias externas, variables, locks, timers— y se puede
consultar sin volver a medir con `--reporte`.

Lo retirado de esta máquina vive en `~/_archive/`, organizado por RAZÓN y no
por ruta de origen, con `mapa-de-retiro.csv` para devolver cualquier cosa con
un `mv`. El índice está en `~/_archive/INDICE.md`.

El inventario físico actual de todo MAK está en
`~/indexes/mak-canonical-20260829/mak-canonical-map.json`. Es el único mapa
actual de rutas y bytes. No recorre `WIN`, `curatoria_inbox`, `GoogleDrive` ni
`OneDrive`, y tampoco entra en `.git`, caches, credenciales o perfiles de
usuario. Para regenerarlo y verificarlo:

    python3 ~/flujo/tools/build_mak_canonical_map.py
    python3 -m json.tool ~/indexes/mak-canonical-20260829/mak-canonical-map.json

Los mapas de ruta, causalidad, aprendizaje y producción siguen siendo mapas
especializados; no se deben interpretar como inventarios físicos alternativos.

## xio_puente, después de la separación (agregado 2026-08-29)

Sigue siendo uno de los cinco órganos. Lo de arriba no se corrige.

Pero el runtime de XIO —el servidor Flask del teléfono, showcontrol, foh_monitor,
los plugins— ya no se autora aquí: vive en **https://github.com/ligereza/XIO**,
extraído el 2026-08-27 con el commit *"Extract XIO runtime, show kit, and ideas"*.
`~/xio_puente` pasó a ser el **puente local de sólo lectura** hacia ese servidor.

`mak-xio.service` está `disabled` e `inactive`, y eso es **decisión, no avería**.
Medido el 2026-08-29:

- El journal muestra una parada limpia el 2026-08-14 16:09 -- `Stopping`,
  `Stopped`, sin traceback y sin OOM. `inactive (dead)`, no `failed`.
- `mak-hub`, `mak-research` y `mak-codex` fueron reactivados el 16 y 17 de
  agosto y corren ahora. **xio quedó fuera de esa reactivación sin un solo error
  que lo explique**: es una omisión deliberada.
- `~/xio_puente/XIO_PUENTE.md` y `~/MAK_CODEX_HANDOFF.md` lo dicen sin
  ambigüedad: no encender `mak-xio.service` por cuenta propia; la dirección de
  red del teléfono es decisión de operador.
- No hay ninguna fila de xio en `mapa-de-retiro.csv`: no se retiró nada, sigue
  entero en su sitio.

Encenderlo es `systemctl --user enable --now mak-xio.service`, pero antes hacen
falta cuatro cosas que hoy no existen: `NTFY_TOPIC_OUT`, `XIO_TOKEN` y
`XIO_BASE` no están definidos en ningún `.env` de la máquina, y el teléfono ya
no contestaba **antes** de la pausa -- los últimos cinco sondeos de
`historia.jsonl` del 2026-08-14 registran `"alcanzable": false`.

Que el código fuente viva afuera no lo saca de MAK: es el único de los cinco
órganos que mira **hacia afuera**, y esa función no depende de dónde se escribe
el software del otro lado.

### Los archivos sueltos de la raíz (2026-08-31)

La raíz quedó con los ocho documentos de arriba más **un script**:

    kvm-linux.sh    el KVM por red, de uso diario y a mano

No lo invoca nada y eso es correcto: su propia cabecera dice *"ÚNICO script
Linux (server Barrier + clipboard bridge) — Uso diario: bash ~/kvm-linux.sh"*, y
`barrier-client.service` está enabled y corriendo. Es la categoría legítima
"consumidor: una persona, a mano", y por poco se archiva por confundirla con los
tres `diag-*.sh` de la misma época, que sí eran diagnóstico de la instalación y
sí salieron.

Lo distinto entre los dos casos: los `diag-*` diagnosticaban una instalación ya
hecha; éste **es** la herramienta.

## Documentos de esta máquina (2026-08-29)

Escritos al final de una sesión de orden. Leerlos antes de tocar MAK
ahorra repetir lo que ya se midió:

    ~/APRENDIZAJE.CLAUDE.MD   cómo se averigua algo de MAK sin equivocarse
    ~/ERRORES.CLAUDE.MD       los errores concretos que se cometieron, y su forma
    ~/SONDA.CLAUDE.MD         qué gobierna tools/, qué demuestran los tests y qué no
    ~/CAMBIOS.CLAUDE.MD       qué se movió, borró, restauró y corrigió, y cómo deshacerlo
    ~/ANOTACIONES.CLAUDE.MD   lo que quedó sin saber, sin abrir y sin decidir
    ~/PATRONES.CLAUDE.json    lista de chequeo de patrones de error (ver el JSON: crece)
    ~/_archive/INDICE.md      las ocho campañas de retiro y cómo devolver algo

## Autoridad y orden de lectura (agregado 2026-08-31)

La lista de arriba, del 2026-08-29, ponía seis piezas en un renglón plano sin
decir cuál se lee primero ni cuál es historia agotada. Es el mismo defecto que
`flujo/docs/AUTORIDAD.md` diagnosticó para el repositorio -- documentos que se
declaran canónicos mientras nadie fija el orden real -- repitiéndose acá, en
la raíz de la máquina, y con ocho documentos, no seis: los seis de arriba, más
`PATRONES.CLAUDE.json` (que ya se cargaba pero no estaba en esa lista) y
`MAK_CODEX_HANDOFF.md` (el traspaso que escribió otra sesión, tampoco
listado). No se abre un noveno documento para resolver el problema de tener
ocho: se resuelve acá, porque éste ya es el que enlaza a los demás.

**Orden real, en tres niveles.**

1. **Se lee siempre, entero, antes de tocar nada:**
   - `GENESIS.md` (este archivo) -- qué es MAK y por dónde entra cada cosa.
   - `PATRONES.CLAUDE.json` -- su propio campo `como_usarlo` lo dice: cargarlo
     antes de actuar, no después de romper algo. Es checklist, no narrativa;
     releerlo entero cuesta segundos.
   - `APRENDIZAJE.CLAUDE.MD` -- el método en prosa: por qué existen esos
     patrones y cómo se averigua algo de MAK sin caer en ellos.

2. **Se consulta cuando la tarea lo toca, no de punta a punta:**
   - `SONDA.CLAUDE.MD` -- tareas dentro de `flujo/tools`, `tests/` o
     `CAPACIDADES.md`.
   - `CAMBIOS.CLAUDE.MD` -- para saber si algo ya se movió, restauró o
     corrigió, y cómo devolverlo.
   - `ANOTACIONES.CLAUDE.MD` -- antes de asumir que algo quedó resuelto, o de
     decidir que algo es decisión del operador: ahí está lo que sigue sin
     saberse.
   - `MAK_CODEX_HANDOFF.md` -- al retomar un hilo operativo que dejó Codex
     (consolidación física, verificación de CI, apertura de raíces). No es
     borrador propio: lo escribió otra sesión real y describe decisiones
     reales. Se trata como fuente -- se lee, no se edita -- y si algo suyo
     quedó superado, se fecha y se supera, como abajo.

3. **Historia agotada: se lee para entender cómo se llegó acá, no para
   actuar:**
   - `ERRORES.CLAUDE.MD` -- la versión larga y narrada de lo que
     `PATRONES.CLAUDE.json` ya resume en una línea por caso. Si el síntoma del
     JSON alcanza, no hace falta abrirlo.

**La regla que evita que esto vuelva a pasar**: ninguno de los ocho es
mantenido. Son fechados -- 2026-08-28, 29, 30, 31 -- y cuando una cifra que
citan choca con lo que mide un instrumento (`bin/mak`, `medir_organismo.py`,
`medir_procesos.py`, `indexes/mak-bridges-20260829/medir_bridges.py`,
`medir_tests.py`), **gana el instrumento**. La corrección se escribe fechada
al lado de la cifra vieja, nunca reemplazándola. Así quedaron corregidas hoy,
en sus propios documentos, y no acá:

- `SONDA.CLAUDE.MD` y `ANOTACIONES.CLAUDE.MD`: "882 sentencias al 9%" en
  `ingesta_archivo.py` era **falso** -- la línea base real es 72%, hoy 73%.
- `SONDA.CLAUDE.MD`: "24 módulos bajo 40% de cobertura" estaba **vieja** --
  son 32, medidos con la suite completa.
- `SONDA.CLAUDE.MD`: "119 archivos en tools/ / 87 VIVO" estaba **vieja** --
  hoy son 116 archivos y 117 filas VIVO. Creció; las dos tablas de
  `CAPACIDADES.md` siguen sin cuadrar entre sí, por la razón que el propio
  documento ya daba.
- `SONDA.CLAUDE.MD` y `APRENDIZAJE.CLAUDE.MD`: "122 shims" / "107" estaba
  **vieja** -- `medir_bridges.py`, que no existía cuando se escribió esto,
  mide 130 hoy, con 0 destinos ausentes y 0 defectos de entrypoint. La
  conclusión ("todos resuelven") seguía siendo cierta; la cifra, no.

Verificado hoy, 2026-08-31, y sin novedad: 23 líneas de cron pausadas y 0
activas, 3 de 5 órganos vivos, `mak-xio.service` apagado por decisión y no por
avería, y `mapa-de-retiro.csv` en 253 filas. Esa última cifra creció desde las
79/88 que citan `CAMBIOS.CLAUDE.MD` y `ANOTACIONES.CLAUDE.MD`, y desde las 234
que cita `MAK_CODEX_HANDOFF.md`: no es contradicción, cada una fue cierta el
día que se escribió. Se mide con `wc -l ~/_archive/orden-limpieza-20260828/mapa-de-retiro.csv`,
no se cita de memoria.
