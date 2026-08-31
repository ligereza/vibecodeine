# Cambios de la sesión de orden — 2026-08-28 / 29

Todo lo que se movió, borró, restauró o corrigió, con su ubicación actual.
Escrito para poder deshacer cualquiera de estas cosas sin reconstruir la sesión.

Convención: **nada se borró salvo un caso, marcado como BORRADO.** Todo lo demás
está en `~/_archive/orden-limpieza-20260828/por-razon/<razón>/`, con fila en
`mapa-de-retiro.csv` (79 filas) que dice `razon, ahora_en, ruta_original,
por_que`. Devolver algo es un `mv`.

---

## 1. BORRADO (único caso)

| qué | tamaño | por qué | cómo se revierte |
|---|---|---|---|
| `~/blender-4.5.3-viejo` | 1,2 GB | Blender **4.5.3 LTS**, una versión detrás del **4.5.4 LTS** que vive en `~/blender`. El nombre no mentía. | Descargar 4.5.3 de download.blender.org. **No es un `mv`.** |

Es el único porque es software redistribuible, no dato. Liberó disco de verdad:
`df` pasó de 85G a 86G libres.

## 2. RESTAURADO (cosas que retiré por error)

| qué | por qué se retiró | por qué volvió |
|---|---|---|
| `~/venvs/knowledge-migration` | afirmé "no hay PostgreSQL en MAK" | **Falso.** `postgresql@15-main.service` corre activo, base `wachuma` con credenciales del 2026-08-27, y un consumidor de psycopg en `state/knowledge-migration-20260813/runner/`. Verificado tras devolverlo: importa psycopg 3.3.4. |
| 176 hardlinks en `research/corpus/` | "deduplicación" justificada por fecha | `source_pipeline.py` usa `write_text`/`write_bytes`, que truncan en sitio y habrían corrompido al gemelo, con research corriendo. Deshecho: −37,6 MB de ahorro falso. |

## 3. RAÍZ DE MAK

Antes tenía archivos sueltos y directorios duplicados por mayúscula o idioma.
Ahora el único archivo suelto no oculto es `GENESIS.md`, más estos cuatro
documentos.

**Archivos retirados** a `por-razon/raiz-de-mak-suelto/`:

- `crontab.bak-20260727` — foto de julio. Trae `MAK-REPO-SYNC` con `git reset
  --hard`, reemplazado por los shims; apunta a un `agente_real.py` inexistente;
  le faltan tres líneas que hoy sí están. Restaurarlo habría perdido trabajo.
- `PENDIENTES_SUDO.md` — cada pendiente medido: linger ya activo, `mak-hub` y
  `mak-codex` ya enabled, `~/codex/.token` inexistente. (Su afirmación sobre
  `ufw` era falsa y quedó corregida en el `POR-QUE.txt`.)
- `diag-red-linux.sh`, `diag-kvm-linux.sh`, `diag-barrier-now.sh` — del 15 de
  julio, diagnóstico de la instalación del KVM por red. Nada los invoca; sólo
  aparecen en inventarios.
- `WINDOWS---` — 21 bytes de un comando de shell mal cerrado.

**Directorios fusionados o eliminados por vacíos:**

| qué | acción |
|---|---|
| `documentos`, `Documentos`, `__pycache__` | vacíos → eliminados |
| `descargas` (1 archivo) | fusionado en `Descargas/manifest-descargas-20260716.jsonl` |
| `Apps` | fusionado en `apps/` (antigravity, llama.cpp, vscode) |
| `model-config` | su `Modelfile` declara un modelo que ollama no tiene → a `por-razon/dependencia-ausente/` |

**Consolidación de las tres áreas de retiro.** MAK tenía `_archive`,
`quarantine` y `rollback`: tres nombres para *apartar sin borrar*. Ahora:

    ~/quarantine  ->  ~/_archive/quarantine-20260806-20260809
    ~/rollback    ->  ~/_archive/rollback-20260811-20260814

Ocho campañas bajo `~/_archive/`, indexadas en `~/_archive/INDICE.md`.

## 4. ÓRGANOS (fuera del repo)

- **13 respaldos manuales** `.bak` y `.bak-FECHA` retirados de `plataforma`,
  `research`, `codex` y `curatoria` a `por-razon/respaldo-manual-obsoleto/`.
  Son ediciones a mano del 23, 26 y 27 de julio, anteriores a que esos archivos
  se convirtieran en shims el 24 de agosto. Divergen entre 7 y 1200 líneas del
  archivo vigente.
- **`plataforma/copilot.py` corregido**: se le quitó el bloque `__main__` que
  llamaba a `_MODULE.main()`, función que el destino canónico no define y que la
  copia pre-proyección tampoco definía. Verificado que sigue importando como
  biblioteca (51 símbolos, que es como `hub.py` lo usa) y que ejecutado como
  script sale limpio. El hub en `:8900` respondió 200 después.
- **`plataforma/workspace/tools/doc_parser/` y `simple_doc_parser/`**:
  completamente vacíos, eliminados.

## 5. CURATORÍA

- **`drenaje_fix/` consolidado en `drenaje/`, no retirado.** Parecía una corrida
  y su corrección doce minutos después. Medido: son **preguntas distintas**
  —`drenaje` investiga el evento del 26/11/2023, `drenaje_fix` el del
  23/12/2023— con cero JSON idénticos por hash. 80 salidas fechadas movidas sin
  una sola colisión de nombre; `drenaje.jsonl` anexado, de 56 a 96 líneas. El
  original queda aparte en `por-razon/evidencia-de-corrida/` por si hay que
  volver a separar las dos corridas.
- `_tmp/` vaciado (un intermedio de OCR de `percepcion.py`, regenerable) y el
  `_tmp` vacío de `pasadas/v4_watsonx_20260801/` eliminado.

## 6. RESEARCH

`research/corpus`: **108 MB → 60 MB**. Seis corridas del scrape de Fondart del
2026-08-13 retiradas por ser byte-idénticas a otras que se quedan. Comparadas
por tres criterios, ninguno el nombre: conjunto de URLs en `sources.sqlite`,
hash de cada captura, y registro de fallas. Verificado que la única URL fallida
que registraban `_v4`/`_v5` sigue registrada como fallida en una corrida viva.

Las cuatro que quedan tienen capturas propias que ninguna otra tiene.

## 7. ENTORNOS PYTHON

De siete que sumaban 16,6 GB:

| entorno | destino | razón |
|---|---|---|
| `venvs/visual-index-pilot` | **se queda** | único con torch + mobileclip + faiss juntos; `visual_index.py:320` los importa y `hub.py` lo usa |
| `venvs/mak-gpu` | **se queda** | nada lo selecciona, pero el historial de bash lo muestra armado a mano el 2026-08-23. Trabajo en curso, no residuo |
| `venvs/knowledge-migration` | **restaurado** | ver sección 2 |
| `venvs/flujo` | retirado | sin ninguna referencia. (La razón escrita decía "subconjunto estricto de `flujo/.venv`" y era falsa: cuatro paquetes difieren de versión. Corregida en su `POR-QUE.txt`.) |
| `venv-providers` | **se queda** | cero por ruta completa, pero dos tests lo nombran por nombre suelto |

## 8. REPO (consecuencia, no objetivo)

Rama `orden/limpieza-archivo-20260828`, 13 commits, mergeada a `main` **local**
en `98b24ae8` con `--no-ff` para dejar un punto de reversión único. **Sin push:
`origin/main` sigue en `15ee50d6`.** Todo lo de abajo es reversible aquí y es
invisible afuera.

- **Cadena airdrop retirada entera**: `cli.py` de 3198 a 3004 líneas. Se había
  retirado a medias el 2026-08-14 (docs y rutas), dejando código, tests y
  workflow en pie. `flujo doctor` chequeaba un directorio inexistente, así que
  la ausencia se leía como salud.
- **Prosa reemplazada por comandos**: `tools/medir_organismo.py` y
  `tools/medir_tests.py`. `docs/MAK_ORGANISMO.md` de 496 a 164 líneas.
- **`docs/AUTORIDAD.md`** resuelve nueve documentos que se declaraban canónicos
  contra los tres que el bootstrap lee de verdad.
- La suite dejó de escribir en los logs de producción de MAK.
- **`tests/fixtures/idioma_baseline.txt`**: 12 entradas apuntaban a archivos
  borrados. 409 → 397.
- Cuatro `.sh` de `cultura/` recuperaron su bit de ejecución: la reanudación
  pasó de 19/23 a 23/23 líneas viables.
- **5 herramientas retiradas** de `tools/` sin consumidor medido, y 25
  registradas que no tenían fila. Tras auditarlo, corregí tres referencias que
  quedaron apuntando al vacío: la lista blanca de `tandas.py`, el docstring del
  comando `tapiz`, y una fila superviviente en la segunda tabla de
  `CAPACIDADES.md`.
- **CI en rojo, causa reproducida**: `experiments/pilots/` gitignoreado y leído
  sin guarda por cuatro suites; más dos tests que lanzaban `.venv/bin/python`,
  inexistente en CI. Corregido y verificado en un checkout limpio: de 10 fallas
  a 3. **Quedan 3 fallas y 24 errores sin identificar.**

## 9. CORRECCIONES AL PROPIO ARCHIVO DE RETIROS

Un auditor adversarial salió a refutar lo afirmado en esta campaña. Encontró:

- El error de PostgreSQL (sección 2).
- **24 archivos archivados sin fila en el mapa**, es decir sin la reversión que
  el mapa promete. Agregados: 79 filas, ninguna apuntando al vacío.
- **Una fila que restauraba lo equivocado**: el `.remember` de `~/puente` se
  archivó como `.remember-de-puente` para no chocar con el otro, pero la fila
  decía `.remember` a secas.
- Dos razones escritas falsas, corregidas en su `POR-QUE.txt`.

Confirmó, resistiendo el intento de tumbarlas: ninguna fila del mapa tiene
consumidor vivo —incluidas las 23 líneas del cron pausado revisadas una por
una—, los hashes del corpus, `visual-index-pilot` como único entorno viable para
el índice visual, la cadena airdrop sin código que rompa, y el diff exacto del
`crontab.bak-20260727`.

## 10. LO QUE NO SE TOCÓ, A PROPÓSITO

- **El crontab**: 0 activas, 23 pausadas. Se pidió ordenar y limpiar, no
  reanudar.
- **La papelera**: 628 MB. 430 son `vibecodeine-legacy-20260824`, un clon con su
  propio `.git`; de 25 archivos muestreados, 16 los tiene git y 9 no. Vaciarla
  es decisión del operador.
- **`RD`** (58 GB, material de clientes), **`WIN`** (evidencia histórica
  declarada inmodificable), **`curatoria_inbox`** (migración en curso).
- **`searxng`**: cero consumidores en código porque corre en un contenedor
  docker vivo. Casi lo retiro.

## 11. ORDENAMIENTO CANÓNICO MAK — 2026-08-29

- Se construyó el único mapa físico actual de MAK en
  `indexes/mak-canonical-20260829/mak-canonical-map.json`. Incluye rutas,
  tipo, tamaño, modo, inode, symlink y SHA-256 cuando la lectura fue posible.
  El resumen del propio JSON manda sobre cualquier cifra copiada en prosa.
- El generador quedó en `flujo/tools/build_mak_canonical_map.py`. No recorre
  `WIN`, `curatoria_inbox`, `GoogleDrive` ni `OneDrive`; tampoco entra en
  `.git`, caches, credenciales, perfiles o runtimes ocultos. Esas exclusiones
  quedan registradas con razón y no se presentan como ausencia.
- Se retiraron de los runtimes activos, de forma reversible, siete archivos:
  una versión `ORDENES_DIRECTOR.md.v1` y seis respaldos sin consumidor ni
  proceso abierto. Cada uno tiene fila en `mapa-de-retiro.csv` y conserva su
  byte-identidad en el archivo.
- No se movieron locks, logs activos, producción, repositorios Git, `WIN`,
  `curatoria_inbox` ni montajes remotos.
- Las dos copias de `RD/MAPA_RD_por_secciones.json` no se deduplicaron: tienen
  el mismo SHA-256, pero Curatoría conserva ambas rutas relativas como
  evidencia física. Quitar una habría alterado la procedencia.
- La auditoría del CSV encontró una fila histórica `BORRADO-no-archivado` para
  `blender-4.5.3-viejo`. Se corrigió para apuntar a un registro de pérdida
  explícito; no se inventó una reversión de algo que ya no existe. Las 88 filas
  actuales apuntan a destinos existentes.
- Tres snapshots `mak-runtime-*` del 2026-08-13 sin referencias actuales se
  apartaron de `indexes/` a `por-razon/mapa-runtime-historico/`. El contador del
  CSV pasó a 88 filas y se actualizará tras cada retiro futuro.

## 12. CONSOLIDACION FISICA FUERA DE GIT — 2026-08-29

- La medicion MAK-wide encontro 128 grupos exactos en la superficie de decision
  antes del cambio. Se distinguieron duplicados de bytes de versiones,
  evidencias, resultados, exports y rutas con funcion propia.
- Se consolidaron 15 copias fisicas redundantes y se dejaron 6 rutas canonicas
  descriptivas. Veinte rutas antiguas siguen disponibles como symlinks
  verificados, por compatibilidad con consumidores que no se pueden tocar en
  esta orden.
- Se consolidaron los documentos RD repetidos y sus dos materiales compartidos
  en rutas estables; los duplicados retirados estan en
  `_archive/orden-limpieza-20260828/por-razon/duplicado-exacto-consolidado/`.
- Se creo `tools/consolidate_static_duplicates.py` como write-set reproducible y
  seco por defecto. Cada retiro se registro en `mapa-de-retiro.csv` con hash.
- Correccion de la nota anterior: RD ya no esta intocable en esta sesion; se
  tocaron unicamente los duplicados estaticos aprobados. No se tocaron sus
  versiones Blender, resultados, exports o archivos con rol ambiguo.
- Research y plataforma quedaron sin movimientos mientras sus procesos estaban
  vivos. Sus duplicados exactos estan clasificados, no ignorados, en la matriz
  de decisiones.
- El snapshot general `indexes/mak-consolidation-20260813/` se movio completo y
  de forma reversible a `por-razon/mapa-inventario-superado/`. Se conserva el
  indice especializado `mak-reality-20260813` porque no es el mismo elemento ni
  responde la misma pregunta que el mapa fisico actual.

---

# Segunda jornada — 2026-08-29 tarde

## El push, y lo que salió mal

`main` se pusheó: `15ee50d6..72bd5cdf`, 27 commits, fast-forward limpio. De los
seis workflows que dispara, **cinco pasaron** (Git topology guard, Render piezas
vectoriales, seguridad, y los dos de issues) y **CI falló**.

Dije que no había riesgo. Lo había, y el error fue de método, no de suerte.

**La causa**: `ModuleNotFoundError: No module named 'psd_tools'`. El código de
producción trata psd-tools como capacidad **opcional** y degrada bien —
`archive_toolchain.py:761` usa `_module_version(...) is not None`,
`diagnostico_proyectos.py:265,291` usa `find_spec`. Pero dos tests la importaban
sin guarda. Está instalada en MAK y no declarada en las dependencias, así que la
suite local nunca lo iba a ver.

Corregido con `pytest.importorskip`, el mismo criterio de toda la sesión: saltar
**nombrando** lo que falta.

**El defecto de fondo, que es lo que importa**: verifiqué en un `git worktree`
usando el `.venv` de MAK. Un worktree da los **archivos** limpios, no el
**entorno** limpio. CI hace `pip install -e ".[dev,render]"` sobre una máquina
sin nada; mi venv arrastra todo lo instalado aquí y no declarado. Queda como
patrón `worktree-no-es-entorno` en `PATRONES.CLAUDE.json`, que ya va en 21.

**Y una cosa que sigue rota y nadie prueba**: el camino de **ausencia** de las
dependencias opcionales. El código dice manejarlo y ningún test lo comprueba.

## Portafolio: MAK produce

El pipeline corre entero y da **más** que la corrida documentada del 2026-08-28:
287 afirmaciones contra 279, `externally_attested` de 2 a 14, y **5 formatos
renderizados contra 3**. `F2-capacidad-barbería` sigue siendo el único no
factible, y eso es **correcto**: este archivo no tiene evidencia de barbería. Es
la prueba de generalización pasando.

Defecto encontrado y corregido: siete insumos del compilador tienen default
`None` y viven fuera del repo, así que **corría degradado en silencio** — 256
afirmaciones y F7 declarado no factible. Ahora hay un flag `--mak` que rellena
las rutas canónicas y reproduce la corrida documentada, y un aviso que nombra en
stderr cada evidencia que falta.

## Correcciones que aparecieron sin buscarlas

- **`operational_bridge.py` leía dos rutas que nunca existieron.** Usaba
  `parents[3]` para `research/`, que resuelve a `flujo/research/` — inexistente.
  Es el error de alcance que este repo documenta como el más frecuente, y estaba
  **dentro del código desde el 2026-08-20**, leyendo nada en silencio.
- **`plataforma/copilot.py`** prometía un `main()` que su destino canónico nunca
  definió. De los 30 bridges que lo prometen, era el único roto.
- **Doce bridges más** usan `runpy.run_path` sobre destinos sin bloque
  `__main__`: arrancan y no hacen nada.

## XIO: decisión, no avería

`mak-xio.service` está apagado porque XIO se separó a `github.com/ligereza/XIO`
el 2026-08-27. El journal muestra parada limpia; hub, research y codex fueron
reactivados el 16-17 de agosto y **xio quedó fuera sin un solo error que lo
explique**. Encenderlo necesita `NTFY_TOPIC_OUT`, `XIO_TOKEN`, `XIO_BASE` — que
no existen en ningún `.env` — y un teléfono que conteste: los últimos cinco
sondeos antes de la pausa ya daban `"alcanzable": false`.

## RD y runtime: medidos, cero movidos

35 grupos de RD (20 entrega, 5 evidencia, 10 que necesitan al operador) y 44 de
runtime (0 sin resolver). Ninguno consolidado, cada uno con su razón. La regla
escrita: **un duplicado conservado cuesta disco, una entrega perdida cuesta un
cliente**.

## Protección de rama: pendiente, y es tuya

`main` no tiene protección clásica (404: repo privado sin esa función en su plan)
ni rulesets. Crear uno quedó bloqueado por el clasificador de permisos, porque
cambia la configuración del repositorio hacia afuera. Importa porque
`revisor.py --enforce` llama a `gh pr merge` cada 6 horas y, con CI en rojo,
mergearía igual.
