# Lo que aprendí de MAK

Escrito el 2026-08-29, al final de una sesión larga de ordenar y limpiar.
Para el próximo agente, o para mí mismo dentro de un mes.

Esto no reemplaza a `GENESIS.md`, que dice qué es MAK. Dice cómo **se
averigua** algo sobre MAK sin equivocarse, que es distinto y me costó caro.

---

## 1. MAK es la máquina, no el repositorio

`MAK = /home/mak`. El repositorio `flujo` es **un directorio dentro** de MAK,
no MAK. Lo dice el propio `GENESIS.md`: *"El repositorio flujo vive en otra
máquina; este organismo respira fuera del repo."*

Buscar algo sólo dentro de `/home/mak/flujo` y concluir que no existe es el
error más caro que se puede cometer aquí, y lo cometí tres veces en un día.
`research/`, `labs/` e `indexes/` viven un nivel más arriba.

## 2. Hay una capa debajo de los cinco órganos

`GENESIS.md` declara research, codex, lenguaje, plataforma y xio_puente.
Debajo, sin que ningún documento lo declarara hasta ahora, corren como
servicios de **sistema**:

    ollama.service                  la mitad del cron le habla
    postgresql@15-main.service      con la base `wachuma`
    docker.service                  con searxng y open-webui dentro
    nvidia-persistenced.service     la GPU de 4 GB
    actions.runner.ligereza-...     ejecuta los workflows del repo aquí

Un inventario que lee sólo `systemctl --user` es **estructuralmente ciego** a
todo eso. Yo escribí uno así y por eso retiré un entorno Python creyendo que no
había PostgreSQL en la máquina.

## 3. Lo apagado no siempre está roto

MAK tiene interruptores de archivo que apagan cosas **a propósito**, y no se
ven mirando el crontab ni los servicios:

    ~/curatoria/AUTONOMY_ENABLE            no existe -> la guardia de curatoría
                                           vuelve al cron y sale en `exit 0`
    ~/codex/.token.disabled                existe -> codex abierto sin token,
                                           documentado en mak_codex/DEPLOY_OPEN.md
    ~/research/.cola.disabled.missing_ntfy existe -> cola de research apagada

Antes de llamar "avería" a algo caído, hay que buscar su interruptor. En esta
máquina la probabilidad de que sea decisión es al menos tan alta como la de que
sea falla.

## 4. El cron está pausado a propósito, y eso no lo desactiva

23 líneas, 0 activas, pausadas el 2026-08-14 19:03 con tres marcas distintas.
Trece minutos después de la pausa, `context/GIT_HISTORY_STRATEGIC_REVIEW.md`
escribió la especificación del orden que había que hacer. **MAK fue detenido
para ser ordenado.**

Consecuencia práctica: **una línea pausada sigue siendo un consumidor.** Si algo
aparece invocado en una línea pausada, ese algo está vivo y no se retira.

Una de las 23, `curatoria_guardia.sh`, lleva marca `PAUSED-FARO`: se pausó tres
días antes que las otras 22 y por otra razón. Reanudar en bloque la reanuda
también.

## 5. La arquitectura de shims

Los siete directorios de órgano (`plataforma`, `research`, `codex`, `lenguaje`,
`curatoria`, `vigia`, `xio_puente`) contienen 122 archivos-puente que delegan al
código real en `flujo/cultura/mak_*/`. Reemplazaron a un cron `MAK-REPO-SYNC`
que hacía `git reset --hard` y `cp -ru` cada diez minutos.

Casi ninguno escribe la ruta como literal. La construyen así:

    Path(__file__).resolve().parents[1] / "flujo" / "cultura" / "mak_X" / "y.py"

Buscar el string `/home/mak/flujo` dentro de ellos encuentra 5 de 107. Hay que
evaluar la expresión, no buscar el texto.

Excepción: `xio_puente` **no** usa shims. Su `monitor.py` es la copia viva y el
propio `.service` lo declara así.

**Vieja 2026-08-31**: el 122 y el 107 de arriba eran ciertos el día que se
escribieron y no se habían vuelto a medir desde entonces. Hoy existe
`indexes/mak-bridges-20260829/medir_bridges.py` (no existía el 29 de agosto) y
mide **130** puentes con destino resuelto al 100% (0 ausentes, 0 defectos de
entrypoint). No hace falta reconciliar el 107 con el 130 a mano — son
recuentos de sesiones distintas sobre un árbol que crece — hace falta correr
el instrumento antes de citar cualquiera de los dos.

## 6. Cómo se retira algo aquí

Convención medida en el historial de git, no inventada: `.archive/` dentro del
repo (jun-jul 2026) → renombrado a `_archive/legacy_historico_previo/` (27-jul)
→ borrado entero (30-jul, 458 archivos). Desde entonces:

    /home/mak/_archive/<qué>-<por-qué>-<yyyymmdd>/

**Fuera del repo, y organizado por RAZÓN, no por ruta de origen.** Se lee con
una sola pregunta —*¿por qué se sacó esto?*— nunca con *¿dónde estaba?*.

Cada categoría lleva un `POR-QUE.txt` que dice **qué se midió**, no sólo la
conclusión. Y `mapa-de-retiro.csv` permite devolver cualquier cosa con un `mv`.
Un archivo de retiros que no registra sus propios errores no sirve para
revertir nada: cuando una medición resultó falsa, la corrección quedó escrita
ahí mismo.

Índice de las ocho campañas: `~/_archive/INDICE.md`.

## 7. La suite verde no dice lo que parece decir

3741 tests pasaron durante toda la sesión. Pasaron mientras el cron llevaba dos
semanas muerto, CI seis corridas en rojo, `xio_puente` caído y `copilot.py`
prometiendo un CLI inexistente. **La suite estuvo verde sobre una máquina
completamente detenida.**

La causa concreta: `experiments/pilots/` está en `.gitignore` a propósito
(evidencia real de pilotos) y varias suites lo leían sin comprobar que
existiera. En MAK están; en un checkout limpio no. La suite certificaba **esta
máquina**, no el repositorio.

Lo que sí prueba que MAK funciona:

    python3 ~/indexes/mak-procesos-20260829/medir_procesos.py
    python3 ~/flujo/tools/medir_organismo.py

La suite se queda donde sirve: frenando a los agentes que degradan el repo. Ver
`SONDA.CLAUDE.MD`.

## 8. Antes de declarar que algo no existe, tres lugares

1. **La papelera** `~/.local/share/Trash` — cada archivo tiene un `.trashinfo`
   con su `Path=` original y `DeletionDate=`. Un árbol en la papelera puede
   venir de un worktree de Codex y no del repo: la procedencia cambia todo.
2. **Los directorios hermanos** bajo `/home/mak/`.
3. **`~/.codex/memories/rollout_summaries/`**.

Y una cuarta que aprendí tarde: **pregúntale al sistema, no al texto.**
`systemctl`, `docker ps`, `ss -ltnp`, `dpkg -l`. Grepear código nunca iba a
encontrar PostgreSQL ni searxng.

## 9. Fuentes para triangular sin investigar

- `~/GENESIS.md` — qué es MAK, fechado 2026-07-16
- `~/Descargas/historia git.odt` — 403 eventos de decisión, 450 recorridos de ruta
- `~/flujo/out/archaeology/claude-codex-mak-20260815.sqlite` — 1028 commits,
  9054 eventos de archivo, 83835 turnos
- `~/indexes/mak-reality-20260813/archivo_index.sqlite` — 1904 activos con sha256
- `~/.codex/memories/rollout_summaries/`
- **El historial de git**: el mensaje del commit que introdujo algo dice para
  qué se introdujo. Leer 350 archivos para inferir su propósito es la vía cara;
  leer los 164 mensajes de commit que los trajeron es la barata.

## 10. Reglas que me dejó esta sesión

- **Ordenar por fecha de creación primero**, después triangular con git. Sale
  más barato y el commit ya trae el motivo.
- **Nunca deduplicar con hardlinks** contenido que algún proceso reescribe:
  `write_text`/`write_bytes` truncan en sitio y corrompen al gemelo.
- **La identidad es el hash del contenido.** Nunca el nombre, nunca el tamaño,
  nunca la fecha.
- **La historia no se corrige, se fecha y se supera.** Si un handoff se
  contradice entre la línea 1 y la 1000, arreglar la línea 1 no arregla nada.
- **La prosa que afirma cifras se reemplaza por un comando que las mide.**
- **Un resultado demasiado limpio es motivo de desconfianza del instrumento**,
  no de satisfacción. Ver `ERRORES.CLAUDE.MD`.

## 11. Una autoridad física y varias autoridades especializadas

El inventario actual de rutas y bytes debe vivir en un solo mapa físico:
`~/indexes/mak-canonical-20260829/mak-canonical-map.json`. Un mapa de rutas del
repo, un mapa causal y un índice específico de producción no son duplicados
aunque sus nombres contengan `mapa` o `inventory`: contestan preguntas distintas
y conservan autoridades distintas.

Hash igual tampoco significa que dos rutas sean intercambiables. Si un
registro de Curatoría conserva dos `ruta_rel` diferentes, ambas son artefactos
físicos distintos aunque sus bytes sean idénticos. Primero se preserva la
procedencia; después se puede declarar la igualdad de contenido.

Los montajes rclone se deben medir como montajes, no como carpetas vacías. El
mapa los registra en la raíz y no entra a resolver contenido remoto. Del mismo
modo, el hogar contiene caches, credenciales y runtimes que se inventarían si
se confundieran con material MAK.

Cada limpieza debe auditar el destino después del movimiento, no solo el origen
antes de moverlo. Una fila de reversión que contiene una palabra como
`BORRADO-no-archivado` es un destino vacío aunque el resto del archivo parezca
correcto; se debe convertir en un registro explícito de pérdida o repararse con
una copia real, nunca dejarla como si fuera reversible.

Los snapshots fechados de runtime también deben tener una sola autoridad viva.
Un archivo con fecha no es automáticamente basura: primero hay que comprobar
referencias y conservarlo en el archivo. Una vez comprobado que no tiene
consumidor actual, se aparta por razón y el mapa canónico pasa a ser la única
fuente física vigente.

## 16. Consolidar sin confundir bytes con elementos

La medicion exacta hallo 128 grupos candidatos fuera de Git, las raices
protegidas, runtimes tecnicos y caches. Solo el hash no decide: un mismo SVG
puede ser plantilla y export, un mismo texto puede vivir en varias corridas de
research, y un `.blend1` puede ser un respaldo aunque sea identico al `.blend`.

La regla aplicada fue: un unico archivo regular canonico para el elemento
aprobado; si un consumidor conserva la ruta vieja, symlink relativo; si el
archivo es una evidencia, una corrida, una version o un output con identificador
propio, se conserva. La copia retirada se mueve antes de crear el symlink, se
verifica por SHA-256 y se anota en el CSV de reversión.

Esto corrigio una afirmacion previa: las copias de `RD/MAPA_RD_por_secciones.json`
si se consolidaron fisicamente. Curatoria conserva sus registros historicos de
procedencia y las rutas antiguas resuelven al unico archivo actual.
