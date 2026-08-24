# Operational Handoff

## Current objective — 2026-08-24

Conservar una única ruta de autoría MAK/WIN y una política determinista para
imágenes y videos. Este checkpoint quedó publicado en `origin/main` como
`ed9c6e2` después de la validación completa; el siguiente agente debe trabajar
solo sobre los items abiertos que siguen abajo.

## Physical authority and migration status

- Autoría e integración: `/home/mak/flujo`.
- Evidencia histórica protegida: `/home/mak/WIN`; no se edita ni se usa como
  fuente operativa.
- Estado y consumidores runtime: `/home/mak/plataforma`, `/home/mak/research`,
  `/home/mak/codex`, `/home/mak/curatoria`, `/home/mak/RD` y otros roots de
  MAK; no se reemplazan bases, logs, media ni outputs generados.
- `flujo-deploy` no es una segunda fuente: queda retirado como ruta activa.
- XIO queda fuera de este slice y no se toca. `RD` creativo queda fuera de la
  limpieza de duplicados.

## Completed work with command and result

1. Consolidación física ya realizada: las familias de código canónicas viven
   bajo `flujo/cultura/`; las rutas runtime externas que se conservaron son
   links o wrappers de compatibilidad. Las copias históricas, datos, bases,
   logs y media se preservaron. Los duplicados no consumidos fueron enviados a
   la Papelera del sistema, no borrados de forma irreversible.
2. Reparación visual en
   `src/flujo/eventos/blender_nodes.py` y
   `src/flujo/eventos/blender_nodes_video.py`: imágenes y videos usan una sola
   política de producción, `fitwidth_fade`. El source no se edita; Blender
   conserva proporción, hace coincidir los bordes laterales de la ventana y
   entrega el sobrante o faltante vertical al grafo de fade. `cover_center` y
   `contain_bars` quedan únicamente como helpers históricos/diagnósticos.
3. El consumidor de imagen es `tools/render_flyer_mak.py`, que importa el
   módulo real de nodos y llama `build_flyer_nodes`; no hay un swap artesanal de
   textura. El consumidor de video es
   `tools/render_video_sequence_mak.py`; ambos quedaron alineados.
4. El reproceso por etiquetas quedó cerrado en
   `.github/workflows/issue_descarga_ig.yml`: en eventos de issues solo pasa
   `opened` o el agregado exacto de `action/descargar-ig`; una etiqueta
   posterior como `gmail` no relanza el render.

## Regression lock — visual and event safety

No cambiar estos invariantes sin actualizar código, pruebas, documentación y
un smoke render real aislado:

- `IMAGE_LAYOUT_POLICY == "fitwidth_fade"` y el video usa el mismo valor.
- Nunca modificar, recomprimir, recortar ni redimensionar el archivo fuente
  recibido. La transformación vive en el mapping/nodos de Blender.
- Los límites X de la ventana medida deben mapear a X=0 y X=1 del source; el
  eje Y puede salir del rango para que el fade maneje el exceso vertical.
- No reintroducir una bifurcación automática por aspect ratio entre
  `cover_center` y `contain_bars`.
- No relanzar un issue como prueba: validar primero con un directorio
  aislado en `/tmp`, un `.blend` copiado/enlazado de forma segura y el flyer
  fuente sin tocar.
- No procesar de nuevo por eventos `labeled` ajenos a
  `action/descargar-ig`; revisar siempre `github.event.action` y
  `github.event.label.name`.

Validación visual ya obtenida: el smoke render de Blender con la imagen no
convencional entregada por el usuario terminó con `RENDER_OK` en
`/tmp/mak-render-check.BquJO6/out/render_output.png`; la inspección mostró
bordes laterales calzados, proporción preservada y fade vertical. El smoke no
tocó issue, OneDrive, `.blend` original ni source.

## ClaudeCode continuation protocol

ClaudeCode debe retomar desde este bloque y desde `agents.md`, no desde una
sesión vieja ni desde `WIN`. Para cada cambio debe dejar en el handoff: objetivo,
path exacto, consumidor, motivo, comando foreground, exit code, resultado
observado, archivos cambiados o prueba de no-cambio, riesgo y siguiente acción.
La búsqueda correcta es: (1) filesystem físico bajo `/home/mak`, (2)
`/home/mak/flujo/agents.md` y este handoff, (3) consumidor real y sus imports,
(4) pruebas y smoke/entrypoint, (5) `WIN` solo como evidencia histórica. Usar
`rg --files`/`rg` acotado; no escanear ni fusionar árboles completos por nombre.

La consolidación requiere comparar contenido, propietario, consumidor,
dependencias y hash; un nombre parecido, timestamp o reporte antiguo no prueba
que sea duplicado. Integrar el mínimo componente en `flujo`, mantener wrappers
solo cuando haya consumidor externo, preservar `WIN`, `RD`, `XIO`, bases, logs,
media y outputs, y mover descartes recuperables a la Papelera. Nunca usar
`git reset --hard`, copiar árboles enteros, regenerar artwork protegido ni
editar un estado JSON para simular trabajo ejecutado. Antes de `git add`, revisar
el diff por archivo y separar cambios no autorizados.

## Open integration items

- Publicación cerrada: `git ls-remote origin refs/heads/main` confirmó que el
  commit funcional `ed9c6e2` está en `origin/main`; el checkout local quedó
  limpio antes de este ajuste documental.
- El runner/Actions tomará este SHA mediante su checkout normal; no se inició
  un job ni se relanzó un issue para validar el cambio, y no se tocaron outputs
  históricos.
- XIO sigue diferido y explícitamente no es un duplicado resuelto.

## Tool and dependency verification matrix

| Slice | Consumer | Verification | Result |
|---|---|---|---|
| Image Blender | `tools/render_flyer_mak.py` -> `blender_nodes.build_flyer_nodes` | focused pytest + isolated Blender smoke | 71 focused tests passed; full suite exit 0; `RENDER_OK` |
| Video Blender | `tools/render_video_sequence_mak.py` -> `blender_nodes_video` | focused pytest + `py_compile` | passed; `fitwidth_fade` only |
| Issue trigger | `.github/workflows/issue_descarga_ig.yml` | static condition review | only `opened` or exact action label |
| Consolidated departments | `cultura/mak_*` and external compatibility paths | bounded physical/hash/consumer audit | source-only runtime code paths: 0 |

## Conflicts and risks

- El write set de ClaudeCode y esta reparación fueron revisados por archivo y
  publicados por autorización explícita del usuario en `ed9c6e2`.
- Los reportes históricos dentro de este handoff pueden contener rutas y
  estados viejos; este bloque superior es la continuidad vigente.
- La prevención de reproceso evita el evento de etiqueta ajena; no convierte
  un issue fallido en éxito y no autoriza relanzar históricos automáticamente.

## Next concrete action

ClaudeCode debe retomar el siguiente item real de integración desde este bloque,
registrar evidencia antes de cambiar estado y no tocar XIO, `WIN`, RD creativo,
bases, logs, media ni outputs. Si no existe un slice autorizado fuera de XIO,
mantenerlo como diferido explícito y no inventar trabajo.

## Last verified

2026-08-24 America/Santiago — full pytest exit 0; 71 focused tests exit 0;
`py_compile` exit 0; `git diff --check` exit 0; Blender aislado `RENDER_OK`;
commit funcional `ed9c6e2` verificado en `origin/main`; no hay proceso de
render activo.

## Current filesystem consolidation — 2026-08-24

`/home/mak/flujo` is the single active authoring/integration baseline. The
historical `/home/mak/WIN` tree was left untouched. The former duplicate
checkout, deploy projection and synchronizer were retired after physical
comparison; none remains an active source or route.

The current Claude write set in `/home/mak/flujo` was preserved, reviewed and
published as part of `ed9c6e2`. Historical phase and recovered-source material
is not an operational owner; only this handoff, `agents.md`, the runtime source
and focused tests define the active baseline.

Department consolidation continued on 2026-08-24. The four canonical code
families under `cultura/mak_plataforma`, `cultura/mak_research`,
`cultura/mak_codex` and `cultura/mak_curatoria` contain every corresponding
runtime code path found in `/home/mak/plataforma`, `/home/mak/research`,
`/home/mak/codex` and `/home/mak/curatoria` (`source_only=0` in the bounded
code scan). Most runtime entrypoints are compatibility projections that load
the canonical files, not independent implementations.

Thirteen exact runtime duplicates were retired from the live department paths
and replaced by links to their canonical files in `flujo`: the ISKVW mounting
script, five Curatoria utilities, six Research helper/unit files and two
Platform utilities. Fifty-two additional Python runtime paths were converted
to compatibility projections that load their canonical implementation from
`flujo`, including the Codex `motor_semantico` package with a package-aware
bridge. Curatoria now has no remaining independent top-level implementation:
its entrypoints are canonical wrappers or links. Runtime state, databases,
logs, inboxes, media and environment files were not moved or overwritten.
Remaining non-wrapper department files are utility/test/runtime-specific
candidates for later per-file consumer review; no whole-tree merge was
performed.

The clutter pass also retired 32 timestamp-clustered prompt-generated utility
files from `/home/mak/plataforma/utilidades` and five orphaned Research patch/
test artifacts. They had no active cron/process consumer and no canonical
source counterpart; they were moved to the system Trash, not hard-deleted.
Runtime-specific `backup.sh`, databases, logs and media remain untouched;
service units were then audited under their own consumer contracts. `backup.sh` and
`watchdog_mak.sh` were then verified as compatibility projections to the
canonical Platform scripts; their external paths remain for cron compatibility.
The active Hub, Research and Codex user units were consolidated to the single
contracts in `flujo` while retaining the external `plataforma`, `research` and
`codex` working directories for state. Their runtime copies are now symlinks;
XIO was intentionally left unchanged for a later pass.

Service switch evidence, 2026-08-24: `systemctl --user daemon-reload` and a
controlled restart of `mak-research.service`, `mak-codex.service` and
`mak-hub.service` all returned active. The live `ExecStart` paths are
`/home/mak/flujo/cultura/mak_research/interfaz.py`,
`/home/mak/flujo/cultura/mak_codex/interfaz_codex.py` and
`/home/mak/flujo/cultura/mak_plataforma/hub.py`; HTTP smoke checks returned
200 for `:8890/api/jobs`, `:8891/api/jobs` and `:8900/health`. Both research
environment files remain loaded, with the existing `n8n-local/research.env`
kept as an overlay. `WIN`, databases, logs, media and XIO were not touched.

The remaining non-XIO code departments were also consolidated: `vigia` now
has one canonical code family under `cultura/mak_vigia`, and `lenguaje` one
under `cultura/mak_lenguaje`; their external code/config entrypoints are
symlinks. `vigia/estado`, Hunspell dictionaries and `lenguaje/lexico` remain
in place as runtime data. The old unconsumed `vigia/rollback/vigia-race-20260811`
snapshot was moved to the system Trash because it was an older divergent code
copy; it is recoverable there. `RD` was not classified as duplicate code: it
is a 58G creative/media workspace and was left untouched.

The active GitHub Actions runner checkout was clean and idle when reconciled.
It was fast-forwarded from `ee9e789` to the canonical remote
`db6659b`; its `issue_descarga_ig.yml` now has the same SHA-256 as `flujo`, and
the extra disabled `claude.yml` was removed by that fast-forward. The runner
service remains active; no job was running during the update.

The detached Codex worktree at `/home/mak/.codex/worktrees/31af/flujo` was an
old, dirty surface with six tracked edits and 806 untracked phase artifacts.
Its useful Hub/tools content was already newer in `flujo`; its only material
exclusive implementation was the experimental Blender `glass_fitwidth`
change, explicitly awaiting visual approval. It was moved to the system Trash
and its stale Git worktree record was pruned; the experiment was not promoted
to production. The 143-file historical snapshot tree was also moved to Trash
after confirming no process or cron consumer. Both remain
recoverable there. `codex/piezas` and `plataforma/director_runs` remain because
they are generated outputs/runtime state, not duplicate source trees.

The documentation cleanup pass on 2026-08-24 removed the retired migration
record and the detached-worktree review from the active context; both were
moved to the system Trash and remain recoverable. `MAPA.md`, this handoff,
`MD_CONTEXT_MASTER.md` and `PHASE_REPORTS_INDEX.md` now identify `flujo` as
the only active source and explicitly fence archival phase/recovered material
as evidence, not instructions. The code structure index was regenerated from
the current tree: 849 Python files, 206,848 lines, 9,442 symbols and zero
syntax errors. Historical phase reports may still contain absolute paths from
their original checks; they are not current commands.

The visual mapping repair on 2026-08-24 keeps the source image untouched and
unifies still-image and video Blender composition under `fitwidth_fade`: the
measured lateral borders match the glass, proportions are preserved, and the
vertical excess/shortfall is handled by the fade graph. The former video-only
`cover_center`/`contain_bars` split is retained only as historical geometry
helpers, not as a production policy. A real Blender smoke render with the
user-supplied non-conventional image passed with `RENDER_OK` in an isolated
`/tmp` check directory. The change is published in `ed9c6e2`; it was not used
to relaunch an issue.

## Active checkpoint — recovery after Claude quota — 2026-08-23

### Current objective

Recuperar y cerrar el slice de ordenamiento epistemico que Claude dejo a medias,
sin repetir el workflow de investigacion ni convertir sus resultados en verdad
automatica. La politica de features debe ser ejecutable por la cola de
clasificacion, no solo un documento de razonamiento.

### Recovered Claude work

Claude Code session `3428381a-02ad-4101-9da5-8176cf72c147` launched the
read-only workflow `wmff24999` with 14 agents. Nine returned and five stopped
at the session quota: `reconciliation`, `histories`, `other`, `track key` and
`synthesis`. The durable result is seven identity records and two measurement
probes. The result was not a complete SSD-to-Instagram join or a final
catalogue. It is summarized in `docs/ordering_research_snapshot.md` so the
temporary `/tmp/claude-1000/` output is not the only record.

Claude also created the ordering policy artifacts, which were present in the
worktree and had not yet been committed:

- `docs/ordering_chaos.md`
- `data/ordering_features.json`
- `src/flujo/knowledge/feature_policy.py`
- `tests/test_feature_policy.py`

The `.gitignore` exception for `data/ordering_features.json` was already
present in the worktree when recovery began. The language ratchet also passed;
the new Python files did not add an offender.

### Integration completed in this recovery

`src/flujo/knowledge/classification_queue.py` now calls
`feature_policy.may_decide()` before emitting either automatic proposal:

- `declared_marker` plus the PEP 405 authority for virtual environments;
- `content_hash` plus the full-hash authority for canonical copies.

Each proposal carries the serialized policy permission in its evidence. If the
registry is missing, malformed or denies the question, the queue raises
`ClassificationQueueError` with `ordering_policy_refused` and emits no
proposal. `tests/test_classification_queue.py` covers both the evidence link
and fail-closed behavior.

### Validation evidence

- Focused policy, queue, language and repository tests: exit 0, 58 passed.
- Full `./.venv/bin/python -m pytest -q`: exit 0, 100 percent passed; only
  existing Pillow deprecation warnings were emitted.
- `compileall` for the touched Python files: exit 0.
- `python3 -m json.tool data/ordering_features.json`: exit 0.
- `git diff --check`: exit 0.

### Files modified in this checkpoint

`.gitignore`, `data/ordering_features.json`, `docs/ordering_chaos.md`,
`docs/ordering_research_snapshot.md`,
`src/flujo/knowledge/feature_policy.py`,
`src/flujo/knowledge/classification_queue.py`,
`tests/test_feature_policy.py` and `tests/test_classification_queue.py`.

No source database, SSD file, service or runtime process was modified. The
checkpoint is committed locally as `02eeea0`; it has not been pushed.

### Risks and boundaries

The seven identities and the two probes are evidence-backed candidates, not
operator attestation. `FELINA` remains unknown, `SCD` remains probable, and
the five failed probes must not be inferred from the nine successful agents.
The policy is now enforced at the automatic classification proposal boundary,
but it does not yet train a model or promote authorship/publication.

## Continuidad tras el corte de cuota — 2026-08-23

CONTEXTO. La orquesta de descubrimiento (`wmff24999`, 14 agentes sonnet en
esfuerzo high) se corto por cuota: 9 agentes terminaron, 5 no
(reconciliacion, historias, other, llave-del-track, sintesis). Otro agente
continuo, publico `35c88ad` con la politica de evidencia y dejo tres archivos
sin commit. Este slice cierra eso, verifica sus cifras y rescata lo que la
orquesta habia averiguado y nadie habia guardado.

VERIFICADO, no asumido. `35c88ad` esta en origin/main y contiene
`data/ordering_features.json`, `docs/ordering_chaos.md`,
`src/flujo/knowledge/feature_policy.py` y `tests/test_feature_policy.py`.
Sin commit quedaban `tools/reconcile_iskvw_media.py`,
`tests/test_reconcile_iskvw_media.py` y una ampliacion de
`docs/ordering_research_snapshot.md`.

EL TOOL DE RECONCILIACION reproduce exactamente las cifras reportadas, comando y
salida:

    ./.venv/bin/python tools/reconcile_iskvw_media.py \
      --archive iskvw/datos/archivo.json \
      --media-root /home/mak/portfolio_media/media --output <tmp>/rec.json
    exit 0
    archive_numeric_ids            1599
    archive_records_with_numeric_id 1818
    archive_records_without_numeric_id 216
    ids_with_one_surface           1591
    ids_with_cross_surface_collision   8
    ids_with_same_surface_multiple_files 0
    orphan_ids                        0
    matched_files                  1607
    superficies: posts 775, other 329, stories 240, archived_posts 154,
                 reels 88, igtv 5

Las 8 colisiones se revisaron UNA POR UNA: las 8 son el archivo original
(`posts` o `reels`) junto a su derivado en `_contact_sheets`. Ninguna es obra
duplicada.

UNA CIFRA QUE NADIE HABIA NOMBRADO: 1818 registros con ID dan solo 1599 IDs
distintos, o sea **219 registros del archivo comparten ID con otro registro**.
Es duplicacion en el INDICE, no en el disco (0 duplicados dentro de una misma
superficie). Esto explica la diferencia con la medicion previa por registros
(posts 998) frente a esta por IDs (posts 775): son unidades distintas, no una
contradiccion.

DEFECTO DE TEST QUE SI ARREGLE. El otro agente pidio verificar que la
correccion de precedencia (`medio.src` antes que `piezas[].id`) permanezca, y el
test la cubria POR ACCIDENTE: en su fixture el ID compuesto falla por numero de
digitos (9, y el patron exige 10), no por precedencia. Se agregaron cuatro tests
donde las dos fuentes DISCREPAN a proposito, mas el caso real de los 1807
registros sin `medio.src`, mas el de los 216 sin ID que deben abstenerse, mas
que `--output` no toque ninguna de las dos fuentes. Verificado invirtiendo la
precedencia en el codigo: 3 tests caen, incluido el nuevo con el mensaje
"the composite record id was preferred over medio.src". Restaurado despues.

RATCHET QUE HIZO SU TRABAJO: `test_tools_en_registro` cayo porque
`reconcile_iskvw_media.py` no tenia entrada en `CAPACIDADES.md`. Registrado con
las cifras medidas.

RESCATE. La orquesta habia investigado 7 identidades con URLs y **55 tracks con
fecha de estreno**, y eso no estaba guardado en ninguna parte del repo: vivia en
`/tmp` y en el journal del workflow. `data/ordering_features.json` declara la
autoridad `artist_discography` como el unico modo de que un nombre de carpeta
decida un track -- una autoridad que nadie puede abrir no es exigible. Ahora
existe `data/artist_discographies.json`:

    LYON          music_artist  confirmed  24 tracks
    DREFGIRA      music_artist  confirmed  17 tracks
    HARRY         music_artist  confirmed  10 tracks
    MARLONLOLLA   music_artist  confirmed   4 tracks
    DREFMOVISTAR  event         confirmed   0 tracks (evento, no discografia)
    SCD           venue         probable    0 tracks
    FELINA        unknown       unknown     0 tracks

Cada track trae `source_url`; 0 descartados por falta de fuente. El archivo
declara explicitamente que la AUSENCIA de un nombre no es evidencia de que no
sea un track: significa que la busqueda no se hizo. Cuatro tests nuevos fijan
que ningun track entre sin URL, que un contenedor sin tracks explique por que, y
que los matches que establecieron la llave (La Merecedora 2025-12, NEBULA
2025-10, Comando Estelar, Pasajero) sigan presentes.

DOS DUDAS MIAS QUE ESTAS SONDAS CERRARON:

1. `other` NO es una clase semantica. 330 archivos, geometria mezclada (265
   cuadrados o casi, 50 verticales, 15 horizontales) y video en los tres
   formatos. Y lo decisivo: **los 330 mtime caen entre 2026-07-22T14:20:15 y
   14:21:10** -- 55 segundos. Eso es una operacion de export o copia, no fechas
   de creacion. Esas mtime no pueden usarse como cronologia de obra. Las 329
   piezas que el archivo etiqueta `obra` ahi NO se resuelven por superficie.
2. La regla de ancla del operador quedo medida sobre los 917 proyectos:
   774 solo `.blend` = 85,29 GB; 43 solo `.aep/.psd/.ai/.svg` = 159,63 GB;
   25 con AMBOS = 502,18 GB; 75 sin ancla = 193,61 GB. La correccion que
   importa: **la obra de VJ terminada y grande vive en la clase MIXTA**,
   mientras la mayoria de los `.blend` chicos son assets descargados. La columna
   `projects.dimensionality` coincide exactamente con la clase de 774, o sea
   estaba midiendo assets y no obras.

Comandos y codigos de salida: `pytest -q tests/test_reconcile_iskvw_media.py
tests/test_classification_queue.py tests/test_feature_policy.py` exit 0;
`pytest tests/` COMPLETA exit 0; `repo_audit.py` exit 0; `compileall` exit 0;
`git diff --check` exit 0; el tool real exit 0.

LO QUE SIGUE ABIERTO, sin adornos: la sonda de las 5659 historias no indexadas
no se corrio, y la llave-del-track sistematica (cruzar TODOS los nombres de
carpeta contra las 55 canciones) tampoco -- hoy solo estan verificados a mano
los de LYON y DREFGIRA. Ningun registro se promovio a autoria, publicacion,
consumidor ni postulacion, y los 216 sin ID siguen absteniendose.

## El motor de consulta certificada — 2026-08-23

Se construyo dentro del repo, como UN sistema y no una secuencia de scripts:
`src/flujo/certified/` con `summary.py`, `contracts.py`, `certify.py`, `tree.py`,
`metrics.py`, `oracle.py`, mas `data/certified_queries.json` y
`tools/certified_query.py`.

LA REGLA QUE LO GOBIERNA, y esta implementada en un solo lugar: un negativo por
ausencia se vuelve UNKNOWN si la autoridad no cubrio a TODOS los miembros del
grupo. El veto vive en `certify()`, no en las reglas, asi que ninguna regla
puede olvidarlo. Cada resumen carga `n_members` y `covered[autoridad]`, y
`complete_for()` es la unica puerta entre "no observe X" y "no hay X".

DOS DECISIONES DE DISENO QUE CARGAN PESO. Los universales se CUENTAN en vez de
marcarse (`counts[X] == n_members`), porque un booleano `all_X` necesita un AND
en cada join y tiene un elemento identidad peligroso: un grupo vacio afirmaria
todo universal de forma vacua. Y los rangos cargan su FUENTE: un casco de fechas
sobre estrenos es sano y el mismo casco sobre mtimes no significa nada, con la
prueba medida de que los 330 archivos de `other` comparten una ventana de 55
segundos escrita por un export.

MEDIDO SOBRE EL CORPUS REAL, sin datos de juguete:

    SSD  917 proyectos, arbol de 1001 nodos, profundidad 7, G=0,17s
    IG   7321 archivos, arbol de 7515 nodos, profundidad 4, G=0,24s

    q2_dimension   poda 100,0%  160 certs  170 nodos visitados de 1001
    q4_obra        poda  95,2%    5 certs
    q7_cuando      poda  90,3%  167 certs  -- con la RAIZ en UNKNOWN
    q5_publica     poda  82,7%    2 certs
    q3_track       poda   1,0%    9 certs  (discografia cubre 46,1%)
    q11, q12, q13, q8, q9, q10, q14  poda 0%

**FALSE_CERTIFIED_CLAIMS = 0**, con 21.090 verificaciones miembro-por-miembro.
`audit_soundness` hace a proposito lo caro: toma cada certificado sobre un nodo
interno y abre TODOS sus descendientes para comprobar que ninguno lo contradice.
Es la unica medicion cuyo valor aceptable es cero, y por eso existe el camino
caro: para que el barato se pueda creer.

q7 es la mejor demostracion del diseno: la raiz dice UNKNOWN con razon precisa
-- "710 de 7321 miembros no traen fecha de la fuente declarada" -- y aun asi
**6611 miembros quedaron podados por debajo**. Abstenerse arriba no impide
certificar abajo.

q11 poda 0% A PROPOSITO. Su negativo murio en el endurecimiento adversarial
(ausencia de `pyvenv.cfg` no es "es mio": blenderkit aporta 138 assets y las
descargas 173, ninguna en un virtualenv) y el motor lo respeta en vez de
recordarlo. La auditoria ahora es codigo.

EL RATCHET ENCONTRO UN HUECO EN SU PRIMERA CORRIDA. `test_the_declared_3d_format_set_still_covers_the_corpus`
fallo por `.3dm` sin declarar. Medido: 1 archivo, en `descargas hasta RDFLYER
2050`, y **0 proyectos donde sea el unico formato 3D** -- o sea ningun
certificado fue falso, pero el conjunto SI estaba incompleto. Se arreglo con una
declaracion en dos capas en vez de agregar lo que el test nombro:
`SCENE_FORMATS` (lo que una aplicacion 3D autora y reabre) y
`PIPELINE_3D_FORMATS` (`.vdb`, `.mtl`, `.spp`: datos que solo un pipeline 3D
produce). Y `EXCLUDED_FROM_3D` deja escrito por que `.exr` (6835 assets) y
`.hdr` NO entran: son imagenes que un pipeline 2D tambien emite, y agregarlas
romperia el certificado POSITIVO en vez del negativo.

ESTADOS EPISTEMICOS, exigidos por codigo. `validate_fold()` rechaza cuatro
cosas, cada una un defecto que este proyecto vivio: un `≈` que se presenta como
`≡`; un pliegue sin residuo; un pliegue que no nombra la autoridad que le falta
(sin el nombre, ninguna herramienta que llegue puede despertarlo); y un monitor
construido sobre el rasgo que al pliegue le falta -- circular, y falla en
silencio. `assert_may_act()` niega borrar, publicar, deduplicar, enviar o
sobrescribir sobre cualquier estado que no sea `≡`.

EL ORACULO pregunta solo donde ninguna autoridad alcanza, de lo mas somero a lo
mas profundo (una respuesta arriba resuelve su subarbol entero), con piso de
miembros, y `record_answer()` rechaza una respuesta sin actor, sin razon, sin
claim o sin scope. Nunca se pregunta para vaciar una cola.

CUDA: no se toco. La Fase 1 del experimento anterior ya establecio que no hay
backend usable (modulos del driver compilados solo para el kernel 6.1.0-50
mientras corre 6.12.95) y que el TU117 no tiene RT cores. El motor no lo
necesita: su medicion decisiva son conteos, no wall-time.

Comandos y codigos de salida: `pytest -q tests/test_certified_engine.py` exit 0
(30 tests); `certified_query.py contracts/ask/queue/audit/provenance/heterogeneity`
exit 0; invocacion en seco exit 2; `--help` exit 0.

LO QUE NO HACE, y es deliberado: 0 certificados sobre el MUNDO en ambos corpus.
Los 169 certificados del SSD son CORPUS_CLAIM y los 7 de IG son POLICY_CLAIM.
El unico contrato con negativo sano sobre el mundo es `q12` y necesita hashes
completos, que en el SSD existen para 112 de 45.536 assets (0,25%). Eso no es un
defecto del motor: es el estado real de la evidencia, y ahora esta medido en vez
de supuesto.

## Next concrete action

The final staged diff was reviewed and committed locally as `02eeea0`. Do not
push it without publication authority. After publication, resume only the five
missing research probes as a separate read-only slice;
do not rerun the completed identity probes and do not mark any SSD project as
authored, published, client-owned or postulation-ready from filenames alone.

## Active checkpoint — 2026-08-21

### Current objective

Conectar DREFGIRA con el contexto de operador VJ, DrefQuila, album Después del
Sol, alcance de presentaciones de noviembre 2025, shows y venues, usando una
base existente y evidencia con estados conservadores.

### Completed work with command and result

Se agregaron `src/flujo/knowledge/project_context.py`,
`tools/triangulate_project_context.py`,
`knowledge/project_context/drefgira_2025.json` y sus pruebas. La ejecucion
foreground fue:

```text
./.venv/bin/python tools/triangulate_project_context.py --context-json knowledge/project_context/drefgira_2025.json --db data/mak_knowledge.db --out-dir /home/mak/curatoria_inbox/project_reconstruction/2026-08-21/drefgira/context --apply
```

Resultado: 10 entidades, 9 fuentes, 12 relaciones, 3 verificadas, 4
`human_attested`, 5 candidatas, 5 Project IR enlazados, 0 cambios de estado y
0 postulaciones. `PRAGMA integrity_check` devolvio `ok`; la segunda ejecucion
fue idempotente. Los derivados `project_ir.jsonl` y `routes.jsonl` quedaron
regenerados y los cinco routes siguen `abstain` por
`project_state_requires_evidence`.

El consumidor read-only quedo expuesto en ambos hubs como
`GET /api/project/context?context_id=drefgira-despues-del-sol-chile-2025` o por
`project_id`. Las dos superficies respondieron HTTP 200 en servidores
efimeros, con `schema=mak-project-context-read-v1`, `read_only=true` y las 12
relaciones; ambos procesos fueron detenidos al terminar la prueba.

### Open integration items

- `formal_tour_scope_not_independently_verified`: el agrupamiento de gira es
  candidato, no un hecho promocionado.
- `antofagasta_show_needs_independent_confirmation`: Evently/La Isla es una
  sola fuente para Club Montecarlo, 2025-11-28.
- `album_release_date_not_normalized_across_sources`: se preservan fechas
  crudas; no se fuerza una fecha unica.
- `operator_contract_not_verified`: la relacion VJ/artista es atestiguada
  por el operador, no una afirmacion contractual.
- `physical_source_mount_unverified`: DREFGIRA sigue review-only hasta montar
  o verificar el SSD; no convertirlo en activo por el grafo contextual.

### Venue projection topology from real show files — 2026-08-21

ANTES: MAK podia describir la planta de una sala y nada de las superficies sobre
las que se proyecta. El unico registro real, `data/venues/scd-plaza-egana.json`,
lo decia con sus propias palabras: `"proyeccion": {"superficie":
"desconocido", "notas": "sin datos: el plano de referencia es una planta, no dice
nada de proyeccion."}`.

DESPUES: MAK puede leer un ScreenSetup de Resolume y emitir la topologia de
proyeccion medida de una sala -- superficies con el nombre que les puso el
operador, pixeles de salida, warp decidido por aritmetica exacta y residuos que
declaran lo que el archivo no prueba -- y proponerla como el bloque `proyeccion`
del contrato `schemas/venue.schema.json` que ya existia.

DESCUBRIMIENTO: el SSD estaba montado (`/dev/sdc1` en
`/media/mak/PortableSSD`, exfat, 932 GB al 98 %) y en su raiz hay 9 archivos
`.xml` que son composiciones de Resolume Arena, no basura: `ANDACOLLO`,
`BERLIN 1`, `berlin 2`, `Black Boss Estandar TEMUCO`, `CHILLAN`, `cobquecura`,
`harry`, `KAYAKAZE 2025 2` y `la`. Todas son ScreenSetup: geometria de
proyeccion, sin identidad de personas ni direcciones, que es exactamente el
artefacto seguro segun la regla `geometria si, identidad no`.

Primera hipotesis FALSIFICADA y conservada: se busco en ellos la lista de clips
usados por show, que habria dado dependencia medida de assets. No existe --
`grep` de referencias a `.mov`/`.mp4` devolvio 0 en los tres archivos mas
grandes. Son ScreenSetup, no composiciones con capas.

TEORIA/ALGORITMO: no hace falta reconstruccion de superficies. La unica pregunta
geometrica que hay que decidir es si se aplico un warp, y eso es aritmetica
exacta: un slice sin tocar guarda un retículo bezier `controlWidth x
controlHeight` cuyos puntos caen sobre la interpolacion bilineal de las esquinas
del `OutputRect`. Comparar el retículo contra esa interpolacion decide
`plano` / `deformado` sin ajustar nada. La tolerancia `WARP_TOLERANCE_PX = 0.5`
existe porque Resolume guarda ruido de coma flotante (`-1.52587890625e-05`), esta
declarada como umbral y sus dos lados estan cubiertos por tests.

IMPLEMENTACION: `src/flujo/venues/resolume_screen_setup.py` (parser, features,
identidad de rig), `tools/venue_screen_setup.py` (CLI + vista HTML + indice de
rigs) y el subcomando `venue.py proyeccion` como consumidor. No se creo un
segundo contrato: los 9 fragmentos `proyeccion` y sus `residuos` validan contra
`schemas/venue.schema.json` sin modificar el schema.

FALSIFICACION, medida y conservada: la primera version de `rig_signature()`
trataba todo nombre de superficie como identificante y produjo 3 falsos
positivos sobre material real -- `ANDACOLLO.xml` y `berlin 2.xml` compartian
exactamente `('Slice 1', 1920, 1080)`, el nombre y el lienzo POR DEFECTO de
Resolume, presentes en cualquier composicion nueva; `CHILLAN.xml` y `la.xml`
compartian solo `('11', 128, 256)`. La reparacion fue en la representacion, no
en una lista de excepciones: `name_class()` separa `tool_default`,
`low_entropy` y `operator`, y la identidad de rig exige al menos una superficie
nombrada por una persona. Los 3 falsos positivos desaparecieron y la unica
relacion sostenida sobrevivio.

RESULTADO REAL: `CHILLAN.xml` y `harry.xml` comparten sus 11 superficies de
salida (mismos nombres, mismos pixeles) con lienzos distintos (3400x1920 contra
1080x1920) y regiones de entrada distintas. Es el mismo rig fisico alimentado por
composiciones distintas, decidido por topologia y no porque exista una carpeta
`HARRY CHILLAN`. Se guarda como `same_rig_candidate` EMPIRICAL con la alternativa
`una plantilla reutilizada en otra sala` intacta y el desempate declarado. Sobre
los 9 archivos: 8 topologias distintas, 0 superficies deformadas, 0 salidas DMX
en CHILLAN pero si en otros, y vocabulario real del operador
(`CENTRAL ATRAS`, `TOTEM L 2`, `BANNER CENITAL`, `rombo izquierda 1`,
`Banner Frontal`).

COSTO: parseo de 9 archivos de hasta 385 KB. Stdlib, determinista, sin GPU, sin
tokens, sin red -- el molde de `mak_lenguaje`. No se hasheo el SSD de 940 GB y no
se reindexo nada.

LA FRONTERA HONESTA: un ScreenSetup mide PIXELES. No contiene escala metrica, asi
que ninguna dimension fisica, altura de cuelgue, tiro de proyeccion ni carga se
deriva de el; todo eso sigue `no_verificado` y el limite esta escrito en
`residuos`, no implicito. El nombre del archivo es CANDIDATO de identidad de
sala, nunca identificacion: `venue.py proyeccion` avisa cuando no coincide y
**no escribe** el registro sin `--aplicar`, porque la sala la nombra una persona.
`superficie` se deja en `desconocido` a proposito: el archivo no puede ver si la
luz cae sobre LED, gasa o muro.

BUG PROPIO ENCONTRADO Y CORREGIDO: la primera version escribia la propuesta
dentro de `data/venues/`, y `cargar_todos()` recorre ese directorio con
`glob("*.json")`, asi que `venue.py validar` la leyo como un venue invalido y
devolvio 8 errores de esquema. Las propuestas viven ahora en
`data/venues_propuestas/`, fuera del glob, con una regresion que lo fija.

Comandos y codigos de salida:

- `python3 tools/venue_screen_setup.py --glob "/media/mak/PortableSSD/*.xml" --out-dir <salida> --index`: exit 0, 9 parseados, 0 fallidos.
- `./.venv/bin/python -m pytest -q tests/test_resolume_screen_setup.py -rs`: exit 0 (ground truth controlado, contraejemplos, consumidor y los 9 archivos reales).
- `./.venv/bin/python -m pytest -q tests/`: exit 0, suite completa.
- `python3 tools/venue.py validar`: exit 0, 3 venues, 0 errores.
- `tools/repo_audit.py`, `compileall -q src tools tests`, `pip check`, `git diff --check`: exit 0 los cuatro.
- `npm run typecheck` con el Node local v24.19.0: exit 0.

Salida persistida e inspeccionable, fuera del repo:
`/home/mak/curatoria_inbox/venue_projection/2026-08-21/` con 9
`*.projection.json`, `rig_index.json` y `projection.html`.

Fuentes intactas: el indice SSD conserva el fingerprint
`d3afb072fe1633125ac20da82aa1d3c7...` y los 9 `.xml` mantienen su mtime original
aunque el montaje sea `rw`. No se escribio nada en el SSD.

RESIDUO, lo que no sabemos: que superficie fisica es cada slice (LED, gasa,
muro), a que sala corresponde cada archivo, y si `CHILLAN`/`harry` son el mismo
rig o una plantilla. Nada de eso se resuelve leyendo mas: requiere una foto, una
fecha de contrato o la palabra del operador.

TRANSFERIBLE: la operacion es `archivo de configuracion de un dispositivo ->
geometria medida -> normalizacion con confianza por dato -> identidad marcada
como no verificada`. La misma forma aparece en MVR/GDTF para iluminacion y en un
patch de audio; si reaparece, se reconoce por esa firma y no por el dominio.

SIGUIENTE ACCION DE ESTE BLOQUE: el item 3 del orden de la memoria de direccion
(`esquema venue-JSON en schemas/`, el que bloqueaba el item 5) ya tiene su
primera fuente medida. Lo que falta para cerrarlo NO es codigo: es que una
persona diga a que sala corresponde cada uno de los 9 ScreenSetup. Con eso,
`venue.py proyeccion <archivo> <venue-id> --aplicar` escribe el registro; sin
eso la maquina se niega, y esa negativa es correcta.

La siguiente accion ejecutable sin decision humana es el reporte de huerfanos
(item 4 del mismo orden, `MEMORIA_DIRECCION.md` §2.12 pasos 1-3): inventario y
dedup por hash sobre el indice del SSD, solo lectura, sin mover un archivo. Es
la primera pieza vendible como informe y no depende de licencia, montaje ni
firma. Ojo con la frontera medida aca: `full_sha256` existe solo para 112 de
45536 assets, asi que la duplicacion exacta es demostrable en 0,25 % del indice
y el resto debe quedar como candidato, nunca como duplicado.

HALLAZGO QUE CORRIGE ESA SIGUIENTE ACCION (medido al aplicar la regla de
externalidad, buscando la misma operacion fuera de su dominio): la hipotesis
falsificada arriba SI es recuperable, en otro tipo de archivo. Las composiciones
de Resolume no son `.xml` sino `.avc`, y hay 4 en el indice:
`DREFGIRA/TALCA DREF.avc`, `DREFGIRA/IMPORT CLAUDIO/SHOWCAUPOLICAN FINAL ANTES
DE CAUPO.avc`, `LYON/sampier.avc` y `descargas hasta RDFLYER 2050/Perrys 2025
V2.avc`. `LYON/sampier.avc` (615 KB) contiene 107 etiquetas `<VideoFile>` y 10
`<AudioFile>` con rutas de clip reales. Eso es el grafo de referencias del paso 2
de `MEMORIA_DIRECCION.md` §2.12, o sea que el reporte de huerfanos del paso 3
deja de ser inventario ciego y pasa a poder responder "que assets usa un show de
verdad".

Dos restricciones medidas antes de construirlo:

- Las rutas dentro de los `.avc` son de Windows y traen nombres de usuario
  reales (`C:\Users\<usuario>`, y hay mas de uno distinto). `tests/test_privacidad_repo.py`
  prohibe exactamente ese patron en el repo, asi que esas rutas NO pueden entrar
  a un archivo versionado: se referencian por hash o se anonimizan al leerlas.
- Resolver una ruta Windows contra un asset del SSD es un problema de
  emparejamiento por basename, con la misma trampa de similitud que este bloque
  ya documento: dos clips distintos pueden llamarse igual. Requiere abstencion
  explicita, no un match optimista.

Tambien aparecieron mas ScreenSetup dentro de carpetas y no solo en la raiz
(`DREFGIRA/Los Vilos.xml`, `HARRY/cobquecura.xml`, `HARRY/show/sin culpa.xml`,
`BAHPARTY/bah/KAYAKAZE 2025 2.xml`, `LYON/1.xml`), asi que el parser de este
bloque tiene mas material real que los 9 de la raiz sin cambiar una linea.

## Show asset usage: which clips a real gig used — 2026-08-21

ANTES: MAK sabia que archivos existen en el SSD y no podia distinguir material
que se toco en un show de material que quedo en una carpeta. `DREFGIRA` eran 467
assets iguales entre si.

DESPUES: MAK puede leer una composicion `.avc` de Resolume, extraer sus
referencias de clip y resolverlas contra el indice del SSD con abstencion
explicita, reportando por composicion los assets usados, los ambiguos y los no
encontrados. Sobre el show real de Caupolican: 52 referencias, 28 resueltas sin
ambiguedad (53,85 %), 6 ambiguas y 18 no encontradas, y los assets resueltos son
el setlist en orden dentro de `DREFGIRA/BLOQUE 01 LSDR/` y
`DREFGIRA/BLOQUE 02 CLASICOS/`.

Relacion nueva que la estructura de carpetas no mostraba: ese show tomo material
de DOS contenedores, `DREFGIRA` y `descargas hasta RDFLYER 2050`. Ninguna
inferencia por carpeta lo habria dicho.

TEORIA: es record linkage entre dos catalogos con regla de abstencion, no una
busqueda. La composicion guarda rutas absolutas de otra maquina, asi que la unica
clave de union disponible es el basename. La hipotesis "en este corpus un
basename identifica un archivo" NO se asume: se comprueba, y cada referencia cuyo
basename lo llevan varios assets vuelve como `ambiguous` y no aporta nada a la
afirmacion de uso.

LA TASA ES UNA MEDICION, NO UN SUPUESTO. Las cuatro composiciones del indice dan
`TALCA DREF` 1/1, `SHOWCAUPOLICAN` 28/52, `sampier` 0/81 y `Perrys 2025 V2` 0/1.
`sampier.avc` cita el Escritorio y OneDrive de otra maquina, asi que no resuelve
nada y el reporte lo dice en vez de fingir. Un unico numero de "que tan bien
funciona esto" habria mentido sobre las cuatro.

LIMITES ESCRITOS EN LA SALIDA: una coincidencia de basename es candidata, no
identidad de bytes -- `full_sha256` existe para 112 de 45536 assets, o sea que la
verificacion por contenido no esta disponible para el 99,75 %. Una referencia no
encontrada NO prueba que el archivo no exista: puede vivir en la maquina que
produjo la composicion. Y `orphan_candidates()` se llama candidates a proposito:
451 de 467 assets de `DREFGIRA` no aparecen en la unica composicion legible de
ese contenedor, lo que NO los vuelve inutilizados, porque solo hay cuatro
composiciones en el indice y los shows del artista no son cuatro. La salida lo
dice y aclara que no es una lista de borrado.

DOS DEFECTOS PROPIOS ENCONTRADOS Y CORREGIDOS EN ESTE BLOQUE:

1. El archivo de test nuevo llevaba un usuario de Windows REAL tomado de las
   rutas del `.avc`. Se reemplazo por los placeholders que el repo ya declara
   exentos (`alguien`, `ejemplo`).
2. Al buscar por que el ratchet de privacidad no lo habia detectado aparecio el
   hueco de fondo: `tests/test_privacidad_repo.py` enumeraba con `git ls-files`,
   o sea SOLO archivos rastreados, asi que un archivo NUEVO con un dato sensible
   pasaba el gate local sin ser visto y recien fallaba una vez commiteado -- con
   el dato ya en la historia. Ahora tambien mira
   `git ls-files --others --exclude-standard`, que respeta `.gitignore`. El gate
   mejorado detecto de inmediato mis propios placeholders `x` y `someone`, que es
   la prueba de que servia. Fijado por
   `test_the_ratchet_sees_new_untracked_files`.

Comandos y codigos de salida:

- `python3 tools/show_asset_usage.py --composition ... --index ... --out-dir ... --orphans DREFGIRA`: exit 0, 4 composiciones, 0 fallidas.
- `./.venv/bin/python -m pytest -q tests/test_resolume_composition.py -rs`: exit 0.
- `./.venv/bin/python -m pytest -q tests/`: exit 0, suite completa.
- `tools/repo_audit.py`, `compileall -q src tools tests`, `pip check`, `git diff --check`: exit 0 los cuatro.
- `npm run typecheck` con el Node local: exit 0.

Salida persistida: `/home/mak/curatoria_inbox/show_usage/2026-08-21/` con
`*.usage.json` por composicion, `drefgira.orphans.json` y `usage.html`.

Fuentes intactas: el indice conserva el fingerprint
`d3afb072fe1633125ac20da82aa1d3c7...` y los `.avc` mantienen su mtime original.
Nada se escribio en el SSD, y ninguna ruta persistida lleva un usuario real.

RESIDUO: 18 referencias del show de Caupolican no estan en este disco y 6 son
ambiguas; resolverlas necesita el disco de origen o hashes de contenido, no mas
lectura. Y el reporte de huerfanos solo sera confiable cuando existan mas
composiciones leidas: hoy mide "no referenciado por las cuatro que hay", que es
una afirmacion mucho mas debil que "sin usar".

REFINAMIENTO MEDIDO EN EL MISMO BLOQUE: las 6 referencias ambiguas del show de
Caupolican no eran indecidibles. Al mirar los metadatos, las dos candidatas de
cada una coinciden en tamano en bytes Y en `sample_sha256`: es el MISMO clip
guardado dos veces, una suelto en `DREFGIRA` y otra dentro de un bloque del
setlist. Abstenerse ahi tiraba una respuesta usable, porque QUE clip sono estaba
decidido desde el principio; lo indeciso era en cual de las copias. Son dos
preguntas distintas y ahora llevan etiquetas distintas:
`resolved_multi_location` frente a `ambiguous`.

Efecto: Caupolican pasa de 28/52 a 34/52 con clip decidido (65 %) y 0 ambiguas,
y aparecen 6 duplicados explicitos en `copias_duplicadas`. El mecanismo
discrimina en vez de resolver en bloque: en `sampier.avc` recupero 3 y dejo 1
genuinamente ambigua. La tasa sin ambiguedad se mantiene aparte
(`tasa_resolucion_inequivoca`) porque la ubicacion sigue sin decidirse, y el
limite dice que sin `full_sha256` la coincidencia de tamano y sample es fuerte
pero no prueba de contenido. Un `sample_sha256` vacio o un candidato sin
metadatos NO cuenta como acuerdo.

Esto tambien alimenta la pregunta de `MEMORIA_DIRECCION.md` §2.12 que "se vende
sola" (que puedo borrar): una copia duplicada es candidata a borrado de una
manera en que un archivo unico no lo es. Los duplicados quedan listados, no
colapsados en silencio.

CORRECCION DE ENCUADRE, provocada por una pregunta del operador ("que relacion
tiene screen setup con los venue?") y resuelta midiendo, no argumentando: la
relacion es MAS DEBIL de lo que este bloque afirmo primero. Un ScreenSetup no es
una huella de sala. `BERLIN 1.xml` y `berlin 2.xml` nombran el mismo lugar y no
comparten NINGUNA superficie -- 59 contra 9, lienzo 3043x272 contra 1920x1080,
clasificado `different_rig`. En cambio `cobquecura.xml` en la raiz y en `HARRY/`
si son el mismo rig, porque es el mismo archivo copiado.

Lo que el archivo describe es un DESPLIEGUE de una fecha, y no puede separar tres
cosas que estan mezcladas en el: lo que es del recinto (la grilla real de una
pantalla LED de casa, la forma de una superficie de proyeccion), lo que es del rig
que se llevo esa noche (cuantas salidas, que procesador) y lo que es decision del
operador (donde corto el lienzo, como nombro las superficies).

Consecuencia aplicada al codigo, no solo anotada: el fragmento `proyeccion`
empieza ahora con `DESPLIEGUE, no configuracion permanente de la sala`, el
contraejemplo de Berlin viaja como residuo dentro de cada registro, y
`TestDeploymentNotVenue` lo fija sobre los archivos reales. Para una sala esto
sigue siendo evidencia util y FECHADA -- mejor que el PDF de 2014 que el venue
mandaria -- pero nunca su configuracion permanente, y una segunda noche puede no
parecerse en nada.


## Cola de leads: preguntarle al catalogo antes de catalogar — 2026-08-21

ANTES: la cola de productoras candidatas de RD proponia como cliente potencial
cualquier cluster con >=2 obras. El conteo era la unica calificacion. Medido
sobre el corpus real (1742 fichas rd -> 984 obras tras colapso de secuencias):
de 3 propuestas escritas, una era `CARTERELA TEstEAMDO` -- la cartelera de
testeo de RD corrompida por OCR, producto propio y no un cliente -- y otra era
`Banco de Chile`, un patrocinador que el OCR levanta del flyer. Ademas
`TEATRO CAUPOLICAN` y `TEATRO ROMA` figuraban como productoras candidatas
siendo venues.

DESPUES: un candidato nuevo pasa por descalificadores nombrados antes de
volverse propuesta, y el informe dice cual y por que en vez de que desaparezca
en silencio. Propuestas escritas: de 3 a 1, y la que queda (`TECHMOTION CHILE Y
DEL AVERNO`) es el lead real.

CORRECCION DE METODO, indicada por el operador: la primera version escaneaba el
corpus para deducir que strings eran venues. Eso era REPAIR sobre una
adivinanza. Lo correcto es REMOVE NEED: **un venue no es una productora, y la
pregunta se le hace al CATALOGO** -- `cargar_catalogo_venues()` y el mismo
`mejor_match` que el modulo ya usa -- antes de catalogar. Se elimino la
heuristica de corpus.

Y lo que ningun dato puede decidir se DEFINE en vez de deducirse:
`data/productoras/no_organizadores.txt`, una linea por nombre. Definir una vez
es mas barato que perseguir una regla perfecta. Ahi entran los patrocinadores
vistos en el corpus (Banco de Chile, Red Bull, Schweppes, CoolBet) y las marcas
de equipamiento (Funktion-One), que aparecen en un flyer sin organizarlo. Si el
archivo no existe, no hay descalificacion por esa via.

Las cuatro vias, cada una comprobable por separado:
`identidad_propia_rd` (la cartelera propia, incluidas sus corrupciones de OCR,
con guarda para que "Cartel Norte" NO caiga), `notacion_de_lineup` (`B2B`,
`VS`: una alineacion de DJs no es un organizador), `declarado_no_organizador`
(el archivo) y `es_un_venue_del_catalogo`. Lo que no cae en ninguna via NO se
descalifica: sigue siendo candidato y el borrador lleva su evidencia.

CORRECCION DE UN JUICIO PROPIO: primero llame "basura" a esas propuestas. Fue
duro y equivocado. El borrador ya mostraba los handles (`@RedBull, @Schweppes`
en el de Banco de Chile) y dice "convertir via PR humano, NO escribir directo".
La maquina propone con evidencia y la persona firma, que es la regla dura #4 del
contrato. El defecto real era mas chico y mas concreto: la cartelera propia y
los venues no debian llegar a la cola.

CONTEXTO QUE ORDENA ESTO, aportado por el operador: no es VJ de RD. Es DISENADOR
de RD, y aparte VJ de artistas (Drefquila, Harry Nach). Por eso los dos corpus NO
se cruzan por nombre de artista -- medido: `nach` 0, `drefquila` 0, `bah` 0 en
las 3385 fichas. El puente entre ambos rubros no es el artista: es que RD da el
lenguaje y el acceso a PRODUCTORAS, que son los clientes potenciales, y lo que
se les ofrece es rider/plano/zona de descanso con el respaldo tecnico de
pantallas. De ahi que la calidad de esta cola importe comercialmente.

Tambien confirmado por el operador y ya no candidato: `harry.xml` y `CHILLAN.xml`
son el MISMO show, Harry Nach en Chillan. El `same_rig_candidate` que este
trabajo dedujo por topologia era correcto, y la atestacion humana resuelve el
desempate que el codigo dejo declarado.

Comandos y codigos de salida:

- `python3 cultura/mak_curatoria/extraccion_db.py ~/curatoria/fichas/fichas.jsonl --outdir <temp> --fuente rd`: exit 0; 984 obras, 20 clusters nuevos, 1 propuesta escrita, 2 descalificados con motivo.
- `./.venv/bin/python -m pytest -q tests/test_extraccion_db.py`: exit 0.
- `./.venv/bin/python -m pytest -q tests/`: exit 0, suite completa.
- `tools/repo_audit.py`, `compileall`, `git diff --check`: exit 0.

Fuentes intactas: no se escribio en `~/curatoria/fichas/`; las salidas fueron a
directorios temporales y el unico archivo nuevo del repo es la lista declarada.

RESIDUO: `MATUCANA #100, TECHNO YOUTH, MIDO, PANAL RECORDS, toliv` sigue siendo
UN candidato con cinco entidades adentro, y dos de ellas (TECHNO YOUTH, PANAL
RECORDS) ya son canonicas. Partir ese campo recuperaria entidades conocidas,
pero es un cambio en la extraccion y no en la calificacion; queda anotado, no
hecho.

## Puertas de entrada: cerrar la clase, no la instancia — 2026-08-21

Reclamo del operador, correcto: yo mismo violé cuatro veces la regla de idioma
que `agents.md` declara y que lei al empezar (`NOTACION_LINEUP`,
`cargar_no_organizadores`, `tiene_notacion_lineup`, nombres de test en
espanol), dejando que el ratchet me corrigiera en vez de acertar. Y peor: habia
arreglado el hueco de enumeracion SOLO en el ratchet de privacidad, que es
exactamente el parche parcial que se me senalo. Este bloque cubre la clase.

CLASE 1 -- una puerta que protege contra la ENTRADA de algo tiene que mirar lo
que esta entrando. Enumerar con `git ls-files` a secas ve solo lo rastreado, asi
que un archivo NUEVO pasa la puerta local sin ser visto y falla recien
commiteado, con la cosa ya en la historia. Miembros medidos:

- `tests/test_higiene_docs.py`: lo tenia en su PROPIO docstring -- "cuatro
  README vendorizados pasaron el pytest local y tumbaron el CI" -- resuelto con
  un workaround manual (`git add` primero). Un workaround que vive en la memoria
  de una persona vuelve a fallar. CERRADO.
- `tests/test_privacidad_repo.py`: ya cerrado antes, ahora comparte la
  implementacion en vez de tener su propia copia.
- `tools/idioma.py`: ya lo hacia bien, y por eso fue el unico que me caz
  al instante. Sin cambios.
- `tests/test_higiene_repo.py::test_config_del_usuario_versionada`: NO es
  miembro. Afirma que la config ESTA versionada, asi que incluir untracked
  destruiria su proposito. Se deja como esta, con la razon escrita.

La regla queda dicha una vez, en `tests/repo_scan.py`: una puerta que pregunta
"esto ya esta commiteado?" usa `git ls-files`; una que pregunta "puede entrar
esto?" usa `versionable_files()`. Verificado ejecutando, no leyendo: una sonda
`.md` sin rastrear con una cifra de suite en prosa AHORA falla antes del commit,
y al borrarla vuelve a verde.

CLASE 2 -- el cero silencioso, que la memoria de direccion §2.3 ya nombra ("0
resultados por primera vez es ERROR, no silencio"). Un barrido AST sobre los
tests marco 69 candidatos, pero eran ruido: casi todos son unitarios con
fixtures literales donde "vacio" es imposible. Acotado a puertas que escanean el
repo quedaron 18, y de esas las reales son tres, todas en
`test_higiene_repo.py`:

- `test_tools_en_registro`: si `tools/` se mueve o se vacia, la lista queda
  vacia y el ratchet informa "nada falta" para siempre. Ahora exige haber medido
  algo. Verificado apuntandolo a un directorio vacio: antes pasaba, ahora falla.
- `test_registro_sin_herramientas_fantasma`: si la tabla de `CAPACIDADES.md`
  cambia de formato, el regex deja de matchear y el ratchet pasa sin medir. Ahora
  exige filas declaradas Y herramientas existentes.
- `test_config_del_usuario_versionada`: hacia `return` cuando git no estaba
  disponible, o sea verde sin medir. Ahora hace `pytest.skip` explicito.
  Verificado ejecutando esa rama contra un directorio sin git: devuelve
  `Skipped`, no verde.

Defecto propio encontrado al hacerlo: la primera version de ese cambio usaba
`pytest.skip` sin `import pytest` en el archivo -- un `NameError` esperando la
rama sin git. Detectado ejecutando la rama, no leyendola.

Comandos y codigos de salida: `pytest -q tests/` exit 0; `repo_audit`,
`compileall`, `pip check`, `git diff --check` exit 0; `npm run typecheck` exit 0.

RESIDUOS CERRADOS (no quedan declarados sin resolver):

1. Las 15 restantes de la lista de 18 SI se verificaron una por una. Catorce son
   `tmp_path`/`TemporaryDirectory` y su `assert not list(...)` recorre un
   directorio que el propio test acaba de poblar: vacio ahi ES la afirmacion
   ("no quedaron temporales"), no una falta de medicion, asi que un pase en
   vacio es imposible por construccion. La numero 15 era real y quedo cerrada:
   `test_campo_filtro.py::test_ningun_trazo_publicado_es_de_una_obra_excluida`
   comparaba `campo.json` contra `glob(iskvw/piel/trazos/*.svg)`, y si ese
   directorio se mueve el glob devuelve vacio, `huerfanos` queda vacio y el
   ratchet informa "todo limpio" para siempre mientras los trazos reales viven
   sin vigilancia. Su propio docstring registra que el incidente ya paso ("441
   trazos de obras que el filtro dejaba fuera"). Medido hoy: 219 piezas en
   campo.json, 208 svg en disco, 208 en el indice. Ahora exige haber medido algo,
   y su gate hermano (`test_el_indice_de_trazos_dice_la_verdad`) tambien, porque
   comparar dos conjuntos vacios no prueba que el indice diga la verdad.
   Verificado apuntandolo a un directorio vacio: antes pasaba, ahora falla.

2. El ratchet de idioma para codigo no-Python se MIDIO y se DECLINA con razon,
   no por omision. En `web/src` hay 36 archivos ts/tsx y 17 declaraciones con
   raiz espanola en 9 de ellos. Pero estan mezcladas: `ProductoraRef`,
   `productoras.ts` y `ArchivoReg` usan terminos de DOMINIO sin equivalente
   ingles que no pierda significado -- "productora" es vocabulario de la
   industria de eventos chilena, igual que se conserva "venue" --, mientras
   `carpetaDe`, `estadoLegible`, `salidas` y `archivo` si son deriva de estilo
   con equivalente directo. Un ratchet duro sobre esa poblacion forzaria
   renombres malos y necesitaria una lista curada a mano de terminos de dominio,
   que es exactamente el patron que la memoria de direccion advierte ("una lista
   escrita a mano es lo que este repo hitio tres veces"). Resultado negativo
   registrado: 17 casos, mezcla de dominio legitimo y deriva, no justifica un
   gate. Si la poblacion crece, la decision se revisa con el numero a la vista.

RESIDUO QUE SI QUEDA: la regla de idioma en Python sigue dependiendo de que el
ratchet la haga cumplir en tiempo de test; no hay verificacion mas temprana. En
esta sesion me caz cuatro veces, lo que significa que funciona, y tambien que yo
no la aplique antes de escribir.

## Puertas que no disparan y puertas mas angostas que su regla — 2026-08-21

Dos clases mas, medidas y cerradas.

CLASE 3 -- una herramienta declarada como dependencia, reportada como ausente.
`src/flujo/laser.py` resolvia vpype con `shutil.which("vpype")`, que solo mira
`PATH`. Pero vpype esta declarado en `pyproject.toml` (extra `dev`),
`.venv/bin/vpype` existe y `import vpype` funciona: pip pone los console scripts
al lado del interprete, y ese directorio NO esta en `PATH` cuando la suite corre
como `./.venv/bin/python -m pytest`. Resultado: `laser.verificar()` devolvia
`{"vpype": False}` y `test_estado_reporta_la_cadena_real` se saltaba con "vpype
not installed" en una maquina donde SI esta instalado. Una puerta que no dispara
donde la dependencia existe no es una puerta.

Es la misma clase que ya arregle para Blender y Node en esta sesion, asi que la
resolucion vive en el mismo lugar: `runtime_tools.resolve_console_script()`
mira override explicito, `PATH`, y el `bin` del interprete. `laser.py` lo usa y
ahora `verificar()` devuelve `vpype: True`; el test dispara y pasa, y ese archivo
quedo con cero skips. Los skips de la suite bajaron de 6 a 5.

Trampa propia encontrada al escribirlo: la primera version usaba
`Path(sys.executable).resolve().parent`, y como `.venv/bin/python` es un SYMLINK
a `/usr/bin/python3`, resolverlo sale del venv y el script nunca se encuentra. Se
usa el dirname sin resolver, mas `sys.prefix`. Detectado midiendo el valor real,
no leyendo el codigo.

Verificado tambien que los otros `shutil.which` del repo NO son miembros:
`rasterizador.py` ya usa lista de candidatos antes de `PATH`, y `gh`, `npm`,
`ffprobe`, `pdfinfo` y `7z` son herramientas de sistema donde `PATH` es correcto.

DIVERGENCIA DE UNA MISMA VERDAD: Blender se resolvia con `BLENDER_EXE` en
`runtime_tools` y con `MAK_BLENDER` en
`cultura/mak_curatoria/diagnostico_proyectos.py`, y con nada mas en ninguna otra
parte. `MAPA.md` documenta `BLENDER_EXE`, asi que quien seguia la documentacion
resolvia Blender en un lado y NO en el otro, en silencio. Ahora los dos nombres
funcionan en los dos lugares y gana el documentado; el alias quedo documentado
como alias. No se unifico por import a proposito: ese archivo tambien corre
proyectado desde `/home/mak/curatoria` con otro interprete, y un import fragil
seria peor que la duplicacion.

CLASE 4 -- una puerta mas angosta que la regla que dice hacer cumplir.
`test_toda_variable_de_entorno_esta_documentada` exige que toda variable de
entorno este en `MAPA.md` seccion 4, pero escaneaba SOLO `src/flujo`. Todo
`cultura/` y `tools/` -- donde viven el Hub, Research y Codex -- escapaba a la
regla. Se descubrio de rebote: al agregar el alias `MAK_BLENDER` en `src/` la
puerta angosta por fin lo vio y fallo.

Medido al ensanchar: 82 variables leidas fuera de `src/flujo` sin documentar.
Documentar 82 en un commit no es verificar, y una puerta que no puede pasar se
desactiva en vez de obedecerse, asi que las zonas anchas quedan con un pin que
SOLO puede bajar -- el mismo patron que el ratchet de idioma ya usa:
`tests/fixtures/env_documentado_baseline.txt` mas `tools/env_baseline.py`
(`--write` lo reescribe a proposito). El ratchet nuevo falla ante una variable
NUEVA, exige que el pin no conserve variables ya documentadas, y comprueba que el
escaneo ancho siga viendo `cultura/` para que no se angoste en silencio.

Verificado ejecutando, no leyendo: se agrego un archivo temporal en `cultura/`
leyendo `MAK_PROBE_UNDOCUMENTED_VAR`, la puerta fallo nombrandola, y al borrarlo
volvio a verde.

Comandos y codigos de salida: `pytest -q tests/` exit 0 (5 skips, todos por
cairosvg/navegador ausentes en esta maquina, presentes en CI via el extra
`render`); `tools/env_baseline.py` exit 0 con 82 pineadas y 0 nuevas;
`repo_audit`, `compileall`, `pip check`, `git diff --check` exit 0.

RESIDUO: las 82 variables siguen sin documentar y el pin mide esa deuda; bajarlo
es trabajo de documentacion, no de codigo. Y vuelvo a anotar lo mismo de antes,
porque volvio a pasar dos veces en este bloque: escribi comentarios nuevos en
espanol y el ratchet de idioma me corrigio. La regla la hace cumplir la puerta,
no yo.

## Un VIVO que no se sostiene al invocarlo — 2026-08-21

CLASE 5 -- el registro dice "toda herramienta declara consumidor o no entra",
pero `test_tools_en_registro` solo comprueba que el NOMBRE aparezca en
`CAPACIDADES.md`. No comprueba que la herramienta siga corriendo, asi que una
fila puede seguir afirmando VIVO sobre un script que revienta al importar.

Medido antes de tocar nada. Las 61 rutas que las filas del registro reclaman
existen todas: 0 faltantes, resultado negativo que no habia que arreglar. De las
40 herramientas VIVO, 21 no nombran un test en su fila y 4 no tienen NINGUN test
en `tests/` que las mencione (`execute_research_job.py`,
`gen_iskvw_prototipo.py`, `gen_propuesta_directiva.py`,
`interpretive_garden_workflow.py`). No se escribieron 4 tests arbitrarios: eso es
volumen. La pregunta falsificable que cubre las 40 es mas barata -- una
herramienta declarada viva tiene que sostenerse cuando se le pregunta que hace.

Resultado: 40/40 compilan. 39/40 responden `--help`; la que no
(`system_map.py`) tiene subcomandos propios (`validate`/`show`), imprime su
usage y sale 2, que es error de uso y no rotura -- mi supuesto de contrato era
demasiado estrecho y se corrigio, no el codigo. Una sola largaba traceback sin
manejar: `gen_campo_iskvw.py` con `ModuleNotFoundError: sklearn`.

Ese fallo era DELIBERADO y su docstring lo dice: "Sin el, no se inventa una
proyeccion peor y se falla: un campo con posiciones falsas es peor que no tener
campo", y el comentario de `main()` aclara que sklearn vive en la caja que
proyecta, no en MAK. Lo que NO era deliberado es entregarlo como stack trace.
Ahora falla igual -- exit 1, sin inventar posiciones -- pero diciendo por que y
que hacer. La puerta nueva pide exactamente eso: un fallo puede ser correcto,
pero tiene que decir su razon en vez de dejar un traceback.

DANO QUE ME HICE Y REPARE, porque la primera version de esa puerta invocaba cada
herramienta con `--help` Y SIN ARGUMENTOS: eso MUTO el repositorio.
`update_readme_svg.py` regenero la capa de texto de `arte-ascii-readme.svg`, que
`agents.md` declara activo protegido; `gen_propuestas_rd.py` escribio
`docs/rd/propuestas_mineria/`; y la peor, invisible para `git status` porque esta
gitignoreada: `iskvw/datos/archivo.json` quedo en 11 KB cuando debe tener ~1,79
MB, regenerada sin el micelio privado, lo que tumbo
`test_iskvw_piel_smoke.py` y `test_readme_svg.py`.

Reparacion completa y verificada: el SVG protegido restaurado desde HEAD (0
cambios), el directorio generado apartado a la carpeta temporal del job en vez de
borrado, y `archivo.json` regenerado con el comando de CI
(`tools/gen_archivo_iskvw.py --fuente todo`, 2034 piezas, 5812 vinculos, 1790.8
KB). Los cuatro tests que habia roto vuelven a pasar. `campo.json` esta rastreado
y su contenido no cambio.

La puerta ahora pregunta SOLO `--help`, y
`test_the_tool_ratchet_never_writes_to_the_repo` fija esa regla leyendo el cuerpo
del test: si alguien vuelve a iterar formas de invocacion, falla. Descubrir que
una herramienta muta con invocacion pelada no puede costar la mutacion.

Hallazgo que queda anotado y NO se toca en esta pasada: dos herramientas VIVAS
escriben cuando se las invoca sin argumentos (`update_readme_svg.py`,
`gen_propuestas_rd.py`). Para `update_readme_svg.py` puede ser su diseño -- su
fila declara un `--check` para deteccion sin escribir --, pero un generador que
muta por invocacion pelada es un riesgo real para cualquiera que lo pruebe. Es
una decision de contrato de esas herramientas, no de esta puerta.

Comandos y codigos de salida: `pytest -q tests/` exit 0 y el repo queda sin
cambios despues de correr la suite completa; `repo_audit`, `compileall`,
`git diff --check` exit 0.

RESIDUO: las 4 herramientas VIVAS sin test siguen sin test propio. La puerta
nueva prueba que se sostienen al preguntarles que hacen, que es mucho menos que
probar que hacen bien su trabajo. Y por sexta vez en la sesion escribi
identificadores nuevos en espanol y el ratchet de idioma me corrigio; esta vez
liste los flagueados antes de renombrar, lo que deberia haber hecho desde el
principio.

## Copias entre contenedores: 543 grupos que NO son basura — 2026-08-21

Contexto que solo el operador podia dar, y que cambia una herramienta: LYON es
un cliente (`@LyonLaF`); `ESCARLATA` y `CDR` son canciones de Drefquila, y
Escarlata es un REMIX en el que participa Harry Nach.

Con eso, una medicion que ya estaba ahi se vuelve legible: 543 pares
(basename, bytes) identicos viven bajo mas de un contenedor, 31,3 GB contando
solo las copias extra. Un deduplicador ve una sola cosa; son al menos tres, y
borrar la copia equivocada es una perdida distinta en cada caso:

- el mismo clip en dos shows: `HARRY CHILLAN/ESCARLATA.mp4` y
  `HARRY/show/VINA/ESCARLATA.mp4`, que es el set del VJ viajando;
- el mismo clip bajo tres artistas porque el tema es una colaboracion:
  `escarlata.mp4` en DREFGIRA, DrefQuila y HARRY;
- la carpeta de una gira y la obra propia del artista con la misma pieza:
  `enrolar.mp4` (3,37 GB) y `misionar.mov` (2,56 GB) en DREFGIRA y DrefQuila.

`cross_container_copies()` los nombra y se NIEGA a rankearlos. La advertencia es
explicita: ninguno es candidato a borrado, porque borrar la copia equivocada
rompe un set, una colaboracion o el cuerpo de obra de OTRA persona. La lista
existe para que una persona la lea, no para liberar disco. El aviso del reporte
de huerfanos ahora lleva esa medicion adentro en vez de una prudencia generica.

Detalle que valida el diseño: `escarlata.mp4` aparece como DOS grupos de tamaños
distintos -- 2,11 GB con tres artistas y 251 MB entre HARRY y HARRY CHILLAN --
y agrupar por (basename, bytes) los mantiene separados. Son relaciones
diferentes, no un duplicado. El test lo fija asi, distinguiendo la colaboracion
del set que viaja.

DOS DEFECTOS PROPIOS EN LAS PRUEBAS, no en el codigo: la primera version del test
indexaba por basename y se comia uno de los dos grupos de escarlata; y la fixture
de indice sintetico no tenia la columna `sample_sha256` que la funcion lee, o
sea probaba una base distinta de la que existe. Las dos corregidas.

LA LEY CUESTIONADA, Y SE SOSTIENE. El operador señalo que la regla de idioma es
por ASCII ("si hay N con virgulilla se rompe el codigo") e invito a cuestionar la
ley. Medido: el ratchet SI atrapa un identificador no-ASCII -- una sonda con
`tamaño` fue marcada -- y hoy hay CERO identificadores no-ASCII en todo el arbol.
La misma puerta cubre la restriccion dura (ASCII) y la convencion documentada
(ingles, con su medicion en `docs/GLOSSARY.md`: 236 archivos con comentarios en
espanol contra 36 en ingles). Mi hipotesis de que la puerta vigilaba la
convencion y no el peligro queda FALSIFICADA. Las seis violaciones de esta sesion
fueron mias, no de la regla.

Comandos y codigos de salida: `pytest -q tests/` exit 0; `repo_audit`,
`compileall`, `git diff --check` exit 0.

RESIDUO: no se clasifica automaticamente cual de las tres relaciones es cada
grupo, y no deberia sin evidencia: distinguir "colaboracion" de "copia de
respaldo" necesita saber quien es el artista, que es justo lo que la maquina no
puede leer del disco. Quedan 543 grupos listados para lectura humana, no 543
decisiones.

## LYON LA F catalogado — 2026-08-21

El operador atestiguo que LYON LA F es un CLIENTE ACTIVO de su trabajo de VJ y
pidio catalogarlo. Era el contenedor mas grande del disco y el unico grande sin
tocar: 15.055 assets, 250,9 GB, 387 filas del escaneo por carpetas.

MATERIAL. Se reconstruyo con la herramienta que ya se uso para DREFGIRA,
FELINA/LOGO y BAHPARTY/bah, sin inventar formato: 387 filas -> 1 unidad de
proyecto, 24 subproyectos, 314 dependencias de biblioteca y 48 recursos
compartidos, con los 15.055 assets reconciliados, cero sin asignar y cero
decisiones UNKNOWN. Las obras nombradas mas grandes: Pajsaera (84,4 GB),
MERECEDORA (28,5), COMANDO (24,6), DEJA (15,5), NEBULA (14,0), CIUDAD (12,0),
la ferrari (6,6), LOGO ENTREGA (5,9), CORAZON (4,0).

ACTIVIDAD MEDIDA, no afirmada: 14.039 assets con mtime de 2025 y 899 de 2026,
contra 60 de 2016 y menos de 40 por ano entre 2020 y 2024. El cuerpo de obra es
reciente, lo que concuerda con "cliente activo" sin depender de esa palabra.

PROJECT IR. El puente existente (`tools/import_project_reconstruction.py`)
escribio 25 registros derivados en `data/mak_knowledge.db`, TODOS en
`review_required`, y sus 25 rutas quedaron en `abstain`. La maquina cataloga el
material y no afirma nada sobre el hasta que un humano lo revise.
`PRAGMA integrity_check` = ok; se tomo copia previa de la base.

FICHA DE CLIENTE: `data/productoras/lyon-la-f.json`. Vive ahi porque ese
directorio YA cataloga artistas -- `frvr.json` tiene `tipo: artist_dj` con una
nota que aclara que es el artista y no la productora --, no porque LYON organice
eventos. La ficha declara esa consecuencia en vez de dejarla implicita: al estar
ahi, el fuzzy-match de `extraccion_db.py` puede resolver un "LYON" leido por OCR
en un flyer contra esta ficha. Se verifico que no altera la cola de leads: sigue
dando 1 propuesta y las mismas canonicas.

Lo que la ficha NO afirma: `instagram` queda VACIO. El handle `@LyonLaF` aparece
dentro de un nombre de archivo (`COMO TU - @LyonLaF (AUDIO OFICIAL) [PROD.NACHO
G FLOW].wav`), lo que es evidencia de nombre y no una cuenta verificada.
Tampoco se inventaron venues, fechas ni eventos.

HALLAZGO QUE NO SE CODIFICO, a proposito: al menos 8 de los 24 "subproyectos" no
son obras sino artefactos de herramienta que el escaneo por carpetas no
distingue -- `Adobe After Effects Auto-Save`, `LYIONGIF.aep_AME`,
`(Material de archivo)`, `blenderkit/blendfiles` y modelos descargados como
`uploads_files_2475145_la+ferrari` y `nissan-skyline-gt-r-r34-1999`. Se midio
sobre TODO el indice: solo 8 filas de 917 caen en ese patron, ~0,08 GB. Seis
regex para ocho filas es sobreajuste y seria una lista escrita a mano, que es
justo el patron que la memoria de direccion advierte. Quedan anotadas en la
ficha para que una persona las confirme, no convertidas en regla.

Tambien medido: LYON comparte 48 items de biblioteca con BAHPARTY, bah, SCD y
"descargas hasta RDFLYER 2050". Son assets comprados o descargados reutilizados
entre trabajos, y NO son las 543 copias entre contenedores documentadas antes:
esas son la misma obra en dos cuerpos de trabajo, estas son insumos comunes.

Comandos y codigos de salida: `tools/project_reconstruction.py --scope LYON`
exit 0; `tools/import_project_reconstruction.py --db data/mak_knowledge.db`
exit 0; `pytest -q tests/` exit 0; `repo_audit`, `git diff --check` exit 0; la
cola de leads reejecutada sin cambios.

Salida persistida: `/home/mak/curatoria_inbox/project_reconstruction/2026-08-21/lyon/`
con `reconstruction.json`, `reconstruction.html` y `project_ir/`.

RESIDUO: cuales de los 24 subproyectos son obras entregadas y cuales material de
trabajo no se decide desde el disco, y no deberia. Los 25 registros siguen en
`review_required` esperando esa lectura humana.

## La cola de revision tenia productores y no tenia puerta — 2026-08-23

MEDIDO antes de tocar nada, y es el hallazgo que ordena todo lo demas:

    project_records        34 review_required | 4 active | 1 candidate
    project_transitions    0 filas
    transition_project()   1 llamada en todo el repo, dentro de su propio test
    classification_queue   8273 pending

Cero transiciones en toda la historia de la base. Se construyeron cuatro
productores que escriben registros que una persona tiene que leer, la maquina de
estados que registra la respuesta de esa persona estaba escrita y validada, y
nunca se construyo una superficie para llegar a ella. Lo unico que ha movido el
estado de un proyecto en este repo es un unit test sobre una base temporal.

Al intentar construir esa puerta aparecieron tres defectos, en orden de gravedad
creciente. Ninguno se habia visto por la razon mas simple posible: el vocabulario
de relaciones tenia UN productor, CERO consumidores y CERO tests, asi que ningun
codigo habia leido nunca una arista.

DEFECTO 1 — direccion invertida en la mitad de las aristas. `_relations_for` en
`reconstruction_adapter.py` re-ancla cada arista en el registro actual como
sujeto y conserva el predicado. Cuando el registro es el lado derecho, eso emite
lo contrario de lo que la fuente dijo. Medido: las 24 aristas `contains` de LYON
se volvieron 56 en el grafo persistido, la mitad al reves. En `depends_on` es
peor que cosmetico: decia que una textura comprada depende de la obra que la usa,
que es exactamente como un item de biblioteca se disfraza de proyecto.
Corregido declarando `RELATION_INVERSES` en el productor y emitiendo el predicado
INVERSO al re-anclar. Ahora: 28 `contains` y 28 `contained_by`, balanceadas.
`inverse_relation()` se NIEGA ante un predicado sin inverso declarado en vez de
adivinar, porque una adivinanza silenciosa es como sobrevivio la primera
inversion.

DEFECTO 2 — un nombre con dos significados. `shared_resource` se usaba para la
relacion SIMETRICA entre dos contenedores ("estos dos cuerpos de obra reutilizan
compras") y para la DIRIGIDA entre un dueno y su carpeta de recursos. Con un solo
nombre la direccion no era recuperable. Se definio en vez de inferirla: la
simetrica ahora es `shares_library_with`. Verificado que ningun
`reconstruction.json` persistido contenia la simetrica, asi que el renombre no
deja datos ambiguos atras.

DEFECTO 3, el que importa mas — una re-derivacion podia BORRAR una decision
humana. `save_project` hace upsert con `state=excluded.state`, y todos los
adaptadores emiten `review_required` porque una maquina no tiene permitido
afirmar. Es decir: reimportar sobre un proyecto que una persona ya habia movido a
`active` lo arrastraba de vuelta a la cola y destruia lo unico de esta base que
una maquina no puede regenerar. Era inofensivo solo porque nunca se habia
decidido nada. Ahora una re-derivacion refresca la EVIDENCIA y nunca el
VEREDICTO: si existe una transicion registrada, el estado guardado gana.
Verificado sobre datos reales -- reimport completo de LYON con 4 decisiones
tomadas, las 4 sobrevivieron.

LA PUERTA. `src/flujo/knowledge/review_queue.py` + `tools/project_review.py`.
El problema debajo no es mostrar una lista: la atencion del operador es el
recurso mas escaso del sistema y la cola solo crece. La pregunta real es cual
pregunta, hecha primero, resuelve mas registros -- y eso se contesta sin inventar
un puntaje, porque las aristas de contencion forman un bosque y un tipo de
respuesta se propaga por el. Es un CONTEO, no un juicio.

Asimetria, y es falsable: el RECHAZO se hereda hacia abajo (una carpeta que es un
Auto-Save de After Effects no puede contener una obra entregada; la afirmacion es
sobre lo que el contenedor ES). La ACEPTACION no se hereda (una obra real
contiene material de trabajo). Si el operador alguna vez anula un rechazo
heredado, eso es un contraejemplo y lo que hay que registrar es la anulacion.
Nada se propaga solo: `--cascade` nombra la herencia.

La palanca se llama `rejection_leverage` a proposito. Llamarla "leverage" a secas
prometia un ahorro que solo una de las dos respuestas paga.

Dos pasos, porque son dos y quieren ordenes opuestos:

    --pass prune       encabeza por rejection_leverage: LYON 25, DREFGIRA 5,
                       LYON/Pajsaera 4, LYON/1 4, LYON/3 3, LYON/golden 3
    --pass recognize   encabeza por material: LYON 250,9 GB, DREFGIRA 102,6,
                       LYON/Pajsaera 85,7, FELINA/LOGO 41,2, MERECEDORA 28,8

LO QUE ESTO CAMBIA EN LA CUENTA: la cola no son 36 preguntas, son **8**. Ocho
raices cubren los 36 registros por contencion. Y `LYON/golden` con
`rejection_leverage 3` propone exactamente las dos carpetas
`(Material de archivo)/...` que el 2026-08-21 se decidio NO codificar como regla
(seis regex para ocho filas de 917 era sobreajuste). Ya no hace falta la regla:
el operador rechaza el contenedor una vez y se hereda.

VALIDACION CRUZADA que vale la pena anotar: el subarbol de LYON en el grafo de
Project IR suma 250,9 GB, identico a la medicion independiente del indice del
SSD. Dos caminos distintos dan el mismo total.

DOS CORRECCIONES A LO QUE YO MISMO REPORTE ANTES:

1. Dije que cuatro cuerpos de obra estaban puenteados a Project IR. Falso:
   `FELINA/LOGO` y `BAHPARTY/bah` tenian su `reconstruction.json` en disco pero
   nunca se habian importado a la base. Ahora si -- 41 registros, ninguno perdido,
   35 actualizados en sitio.
2. Dije que LYON comparte 48 items de biblioteca con BAHPARTY, bah, SCD y
   descargas. Incompleto: son NUEVE raices --
   `descargas hasta RDFLYER 2050` (32), SCD (13), BAHPARTY (4), bah (4),
   KISZ (4), FELINA (3), OBER (2), `3D JJJ` (1), interplanetary (1).

Comandos y codigos de salida: `pytest tests/` exit 0 (13 nuevos en
`test_review_queue.py`, 4 en `test_reconstruction_adapter.py`, 3 en
`test_project_ir.py`); `repo_audit.py` exit 0, `integrity=ok` en las 4 bases;
ratchets de idioma, docs, privacidad, higiene y mapa exit 0. Se verifico que los
tests nuevos FALLAN sobre el codigo viejo (`assert 2 == 0`), no que solo pasan.
`tools/project_review.py list/summary/show` deja el sha256 de la base intacto.
`data/mak_knowledge.db` sigue ignorada por `.gitignore:179`, asi que la
re-derivacion es local y regenerable.

LO QUE NO HICE, y es deliberado: no decidi ni una sola de las 36. Las obras las
reconoce el operador; la maquina propone con evidencia y el humano firma. Las
pruebas de escritura se hicieron sobre una COPIA de la base.

RESIDUO: los 8273 `classification_queue` pendientes son otra cola, con otra
forma, y todavia sin puerta. Y la asimetria rechazo/aceptacion es una hipotesis
con una prediccion clara: si el operador anula un rechazo heredado, esta mal.

## La segunda cola: 8273 filas que no eran 8273 preguntas — 2026-08-23

`classification_queue` tenia la misma enfermedad que la cola de proyectos, en un
segundo lugar: 8273 filas TODAS `pending`, cuatro plantillas de pregunta, y
ningun codigo en todo el repo que escriba `status`. Un productor, cero
consumidores. Pero la FORMA del problema es distinta y copiar la puerta anterior
habria estado mal.

8273 ES UN NUMERO DE FILAS, NO DE PREGUNTAS. Descompuesto por evidencia
verificable:

    1463  dentro de un virtualenv        pyvenv.cfg probado en disco
    2566  byte-identica a un archivo     sha256 igual + ruta canonica nombrada
          del repo vivo
    1035  en el repo vivo                necesita una persona
    3209  en cualquier otra parte        necesita una persona

4029 filas -- el 48,7% -- no son preguntas para un humano, y no en el sentido de
"probablemente no": cada una carga un chequeo que cualquiera puede repetir.

CAUSA RAIZ de 1463 de ellas, y es una sola: TODAS vienen de UN directorio,
`/home/mak/curatoria_inbox/3d/NEW/env`, un virtualenv de Windows copiado a esta
maquina (tiene `pyvenv.cfg`, `Include`, `Lib`, `Scripts`). `should_skip_dir`
probaba NOMBRES -- `ACTIVE_SKIP` tiene `venvs`, `.venvs`, `venv-providers` -- y no
tenia ni `env` ni el layout Windows `env/Lib/site-packages`. Una lista de nombres
solo atrapa los nombres que alguien penso. Arreglado con una DEFINICION:
`pyvenv.cfg` no es una convencion de nombre, PEP 405 obliga al interprete a
escribirlo en la raiz del entorno y `sys.prefix` se deriva de ahi. La regla ahora
vale para un directorio llamado como sea. `build_mak_knowledge_db.py` no tenia
NINGUN test, que es como una lista de nombres se queda siendo la regla completa;
ahora tiene `tests/test_knowledge_scanner_skips.py`, incluido uno que falla si
alguien vuelve a la lista.

LA PREGUNTA ESTABA MAL FORMADA, y por eso nunca avanzo. "python implementation
requires purpose and consumer classification" junta dos preguntas cuyas unidades
naturales son distintas, y ninguna decision unica puede contestar las dos. El
contraejemplo esta en los datos: 44 de las filas son `__init__.py` de CERO bytes.
Contenido byte-identico, o sea PROPOSITO identico (marcador de paquete), y viven
en 5 arboles distintos, o sea CONSUMIDORES distintos.

    purpose / project    funcion del contenido  -> una respuesta por clase
    consumer / route     funcion de la posicion -> una respuesta por archivo

Juntas, la mitad barata queda de rehen de la mitad cara, 8273 veces.
`QUESTION_PARTS` declara el corte en vez de dejarlo implicito.

LO QUE UNA PERSONA REALMENTE TIENE QUE CONTESTAR: las 4244 filas restantes se
doblan por `(candidate_kind, directorio)`, porque la mitad gruesa de cada
pregunta es una propiedad del directorio. Resultado medido:

    576 grupos | 3 respuestas cubren la MITAD de las filas | 64 cubren el 80%

Los tres grandes: `/home/mak/research/corpus` (1599 filas, archivos .md con
nombre de hash y sufijo epoch -- corpus generado, no propuestas),
`/home/mak/research/informes/archive` (520) y `/home/mak/flujo/tests` (255).

LA MISMA ASIMETRIA que en la cola de proyectos, y no es coincidencia: una
respuesta gruesa NEGATIVA subsume la fina (si la carpeta es corpus generado,
preguntar a que propuesta pertenece cada archivo es moot); una POSITIVA no.
`--covers coarse_only` deja registrada la mitad abierta y
`fine_questions_still_open` la cuenta, en vez de que desaparezca del conteo de
pendientes como si la pregunta entera estuviera cerrada.

Verificado extremo a extremo sobre una COPIA de la base: `apply-rules --rule
inside_virtual_environment` resolvio 1463 y reaplicarlo resolvio 0 sin pisar nada;
una sola respuesta a `/home/mak/research/corpus` resolvio 1599 filas dejando
`fine_questions_still_open: 1599`. Cada resolucion queda en
`classification_resolutions` con actor, razon, regla y evidencia (tabla
append-only creada al primer uso; leer la cola no la necesita).

Comandos y codigos: `pytest tests/` exit 0 (15 nuevos en
`test_classification_queue.py`, 5 en `test_knowledge_scanner_skips.py`);
`repo_audit.py` exit 0; `git diff --check` exit 0; `classification_review.py
list/propose/summary` deja el sha256 de la base intacto; bare exit 2, `--help`
exit 0.

NO APLIQUE LAS REGLAS SOBRE LA BASE VIVA. Son chequeos probables, no juicios,
pero el acto lleva la firma de alguien y esa firma es del operador. El comando
exacto, cuando quiera:

    ./.venv/bin/python tools/classification_review.py apply-rules \
      --actor mak --reason "installed dependencies and byte-identical copies are \
      not authored material" --dry-run

(sin `--dry-run` para escribir; se puede acotar con `--rule`.)

RESIDUO: los 3209 de "cualquier otra parte" incluyen 308 filas en
`/home/mak/WIN/flujo` que NO son byte-identicas al repo vivo -- copias
divergentes, que es informacion y no ruido. Y para `candidate_kind = consumer` la
unidad declarada es el import, mientras `classify` responde por directorio: mas
grueso que la unidad real, y por eso ese caso deberia usar `coarse_only`.

## Next concrete action

Publicar este write set en `main` solo cuando exista autorizacion explicita de
commit/push. No ampliar la gira ni crear postulacion hasta obtener una segunda
fuente para Antofagasta y evidencia fisica del proyecto. Mantener BAH como
entidad separada del artista y no fusionar prefijos DREF por similitud textual.

### Last verified

2026-08-21 America/Santiago — tests focalizados `6 passed`, py_compile exit 0,
`git diff --check` exit 0, CLI de triangulacion exit 0, segunda ejecucion sin
cambios semanticos, endpoints de ambos hubs HTTP 200, pytest completo exit 0,
`repo_audit` OK, compileall exit 0, `pip check` sin errores, DB integra y sin
procesos permanentes iniciados. El commit/push queda fuera de este cierre hasta
recibir autorizacion explicita para publicar este write set.

## Current objective

Mantener el repo web y el runtime local en un estado coherente y verificable,
con una primera capa artistica-cultural-investigativa comun para curatoria,
portfolio, research y matematicas. La hipotesis P versus NP se usa aqui como
modelo conceptual de representacion, busqueda y certificados; no como un
teorema ya demostrado.
El estado operacional ya no depende de releer este archivo: se consulta en la
CLI y en el Hub real de 8900 mediante `mak-system-status-v1`, que reúne el
ledger con los consumidores locales y deja las atenciones explícitas. Los
gates de esta tanda quedaron cerrados: se preserva la incertidumbre
matematica y Research 4 tiene un consumidor local simbólico, con licencia y
revisión humana aún pendientes. La continuidad de ideas se consulta en el lane
registry, no releyendo la memoria historica completa.

## Session transfer checkpoint — 2026-08-21

La fase web/DB queda validada y lista para publicar. El conjunto propio de esta
fase es la limpieza de superficies Windows obsoletas, la preservacion de XIO
como workflow manual diferido, el gate `tools/repo_audit.py`, su regresion,
`tools/gen_rd_standalone.py`, la fila de `CAPACIDADES.md`, los cambios de CI/
Makefile y este handoff. No se debe hacer `git add .`: el worktree contiene
otros cambios de sesiones anteriores que deben permanecer intactos y sin
mezclarse.

Pruebas cerradas: pytest completo exit 0; `npm run typecheck` exit 0;
`repo_audit` exit 0 (36 modulos, 35 alcanzables, 0 muertos, 0 referencias
obsoletas, cuatro SQLite integras); compileall y `git diff --check` exit 0.
No hay procesos de pytest, intake, Blender ni render activos. La siguiente
accion exacta es revisar el staging del conjunto propio, crear el commit y
hacer push de `main`; despues la nueva sesion debe continuar desde `Next
concrete action` sin repetir la auditoria.

CERRADO: ese checkpoint se completo en `69e7fba` + `268ef4b` y el resto del
worktree se publico en `90f92be`. Se conserva como registro; la accion vigente
esta en `Next concrete action`.

## Physical authority and migration status

- La autoridad física es `/home/mak/*`; `/home/mak/flujo` es el baseline de
  autoría y `/home/mak/WIN` es evidencia histórica de Windows.
- No se copia ni se borra el árbol histórico. Los datos locales ignorados y los
  productos generados se preservan fuera del commit salvo que una regla del
  repo los declare artefactos versionables.
- Git tiene una sola rama local (`main`) y una sola rama remota operativa
  (`origin/main`). El README y su SVG protegido no se modifican.
- En la inspección actual se observaron `cron`, el runner local de GitHub
  Actions y Open WebUI ya instalados; esta tarea no inició ninguno. El Hub
  existente `mak-hub.service` fue reiniciado de forma controlada para activar
  la nueva ruta read-only y quedó activo en 8900; no se inició ningún servicio
  nuevo ni se dejó un render adicional.
- La interfaz temporal del Research local ya estaba activa antes de esta
  tanda; no fue iniciada, detenida ni modificada aquí.

## Completed work with command and result

- Se agregó `src/flujo/knowledge/learning_policy.py`: learner categórico
  auditable, split por `project_id`, abstención ante evidencia insuficiente y
  registro de política solo como candidata.
- Se agregó `tools/project_learning.py` y
  `tests/test_learning_policy.py`. El adaptador
  `mak-verified-result-v1` exige proyecto existente, evidencia, validador y
  checks pasados; es idempotente y falla cerrado.
- `src/flujo/knowledge/project_api.py` expone `learning.policy` en modo
  read-only. `CAPACIDADES.md` y `docs/MAK_CURRENT_STATE.md` declaran el
  contrato.
- Se integró `operational_status()` en
  `src/flujo/knowledge/project_api.py`, `tools/mak_status.py` y el campo
  `operational` de `GET /api/status`. CLI y Hub comparten el mismo contrato
  read-only: estado general, evidencia pendiente, bloqueos, abstenciones y
  siguientes acciones. El Hub conserva sus campos históricos de servicio.
- Se agregó `src/flujo/knowledge/system_status.py`, el sobre
  `mak-system-status-v1` que conecta el ledger con once consumidores físicos:
  fuente/Hub 8900, Research 8890, Codex 8891, SearXNG 8888, runner de eventos,
  Blender/RD, portafolio, runtimes, configuración de proveedores y el registro
  transversal de lanes. Solo lee
  rutas, `/proc`, listeners loopback y nombres de variables; no hace requests
  externos, no inicia jobs y nunca devuelve valores de claves.
- El Hub canónico `/home/mak/plataforma/hub.py` ahora expone
  `GET /api/status` y una pestaña `● estado` en 8900. El endpoint real fue
  verificado con HTTP 200, esquema `mak-system-status-v1`, once componentes y
  `read_only=true` después del reinicio controlado.
- El componente `lanes` del mismo sobre valida, sin mutar, el registro
  `mak-cross-domain-lane-registry-v1`: 19 lanes bajo
  `cultural_research_first` (1 implementada, 7 parciales, 11 propuestas).
  El CLI y el estado del Hub comparten ahora el módulo
  `src/flujo/knowledge/lane_registry.py`.
- Se agregó `runtime_tools.resolve_blender()`: resuelve la instalación real
  `/home/mak/blender/blender` aunque no esté en `PATH`. `contract_registry` y
  `episode_runner` comparten esa resolución, eliminando el falso faltante de
  `blender_optional` sin instalar ni ejecutar Blender desde el estado.
- El probe de render cuenta procesos por el ejecutable real de `/proc`, no por
  texto de argumentos: una orden de inventario que mencionaba la ruta de
  Blender había producido un falso `active`. La lectura final muestra
  `render=ready` y `process.running=false`; no hay render en segundo plano.
- La auditoría de contratos más reciente se registró explícitamente como
  `simulation_consumer_20260820`: 59 contratos, 59 verificados, 0 con
  evidencia pendiente y 0 no disponibles. El ledger actual queda con 2
  atenciones accionables (4 proyectos en revisión y 3 episodios sin evidencia)
  y 2 informativas (abstención segura y falta de holdout independiente).
- `tools/source_learning_bridge.py` y
  `src/flujo/knowledge/source_learning.py` conectan dos raices fisicas por
  referencias: `/home/mak/WIN/claude_sesiones` como memoria de hipotesis y
  `/home/mak/curatoria_inbox/MAK_TODO_SESION_2026-08-19` como auditoria y
  contratos de investigacion. El caso versionado valida 2 raices, 9 archivos,
  9 mensajes por UUID/hash, 7 hallazgos y 5 unidades de aprendizaje sin copiar
  los arboles ni el texto privado de las conversaciones.
- La ingestion real se registro como proyecto activo
  `mak-pnp-search-ecology-2026-08-19` y episodio verificado
  `episode-source-learning-c6f328491b44e1af7828ec1b`. El alcance guardado es
  `source_integrity_and_epistemic_contract_only` y
  `mathematical_truth_validated=false`: no afirma una solucion de P versus NP.
- `src/flujo/knowledge/math_kernel.py` agrega un scheduler metadata-only sobre
  el mismo Project IR y la misma base SQLite: una capsula `MILLENNIUM-PNP-001`,
  requests acotados y ResultCards sellados. El proyecto conserva los dominios
  `cultura`, `curatoria`, `portfolio`, `research` y `mathematics`; como la
  fidelidad semantica esta `UNTRUSTED`, su estado es `review_required` y el
  ciclo real solo dejo una request `METADATA_ONLY` en cola. No se ejecuta un
  worker ni se promueve verdad por ausencia de contraejemplos.
- `knowledge/lane_registry/mak_cross_domain_registry_2026-08-20.json` y
  `tools/project_lanes.py` agregan un mapa read-only de 19 lineas bajo la misma
  primera capa: P=NP, tenis, captura/scraping, deep learning/micelio,
  transpilacion, eventos, simulacion de crecimiento, XIO, claims, lenguas, patentes, crops, dental,
  jardin/geometria, vibe coding, storage, patronage y autoria. Cada linea
  conserva dialectos, estado epistemico, evidencia, consumidor si existe,
  guardrails y un siguiente gate; las propuestas no se presentan como trabajo
  implementado.
- El lane de tenis ya tiene `src/flujo/tennis/shot_events.py` y el consumidor
  read-only `tools/tennis_shot_events.py`: proyectan a
  `schemas/tennis/shot_event.schema.json`, conservan `raw_ref`, hash,
  `transform_chain` y tokens desconocidos, y el router solo lo selecciona para
  un Project IR activo/verified del dominio `tennis`.
- Se registró el primer episodio verificable del lane: proyecto
  `mak-tennis-decision-lab-fixture-20260820`, episodio
  `episode-tennis-shot-fixture-20260820`, 4 eventos, hash de fixture y 2
  tokens desconocidos preservados; `network_calls=0` y sin contrafactuales.
- El probe de ruta del mismo proyecto selecciona
  `tennis_shot_event_consumer` y queda registrado como
  `episode-tennis-consumer-probe-20260820`; prepara un comando local acotado,
  no lo ejecuta ni escribe salida generada.
- Scraping y deep learning ya tienen consumidores acotados: `research_source_capture.py`
  separa plan/captura y registra una sola URL con hash en `SourceCorpusStore`;
  `deep_learning_gate.py` exige labels, holdout independiente, agrupación
  anti-leakage y validador, pero nunca autoriza entrenamiento por sí solo.
- La evidencia física de Research 4 quedó enlazada al Project IR como proyecto
  `mak-research-capture-job4-20260820` y episodio
  `episode-research-capture-job4-20260820`: 4 fuentes capturadas, hashes y
  etapas verificadas; licencia pendiente; el consumidor simbólico queda sujeto
  a revisión humana y no afirma crecimiento biológico.
- Research 4 ya tiene un consumidor `research_simulation_consumer`:
  `knowledge/research_simulations/job4_lsystem_candidate_20260820.json` usa
  reglas explícitas, límite de símbolos y alcance `visual_grammar`; la salida
  se etiqueta `simulated`/`model_not_reality` y no se interpreta como biología.
- El dataset existente de logo-clean quedó enlazado como
  `mak-logo-clean-learning-gate-20260820`; su episodio
  `episode-deep-learning-gate-logo-clean-20260820` abstiene correctamente:
  solo hay 3 ejemplos y no existe holdout independiente, por lo que no se
  autoriza entrenamiento.
- `tests/test_system_status.py` cubre resolución local, redacción de secretos
  y ausencia de escrituras. El cambio de `providers.provider_registry()` hace
  que un entorno explícito no cargue silenciosamente otro `.env`.
- `web/src/components/HubDashboard.tsx` muestra el estado unificado antes del
  ledger, y `web/src/api/flujoApi.ts` consume `/api/status` como fuente única;
  las páginas generadas de `context/` fueron reconstruidas con Node 24.19.0.
- La consulta actual del ledger devuelve `attention` con 2 asuntos accionables
  y 2 informativos: cuatro proyectos en revisión, tres episodios sin evidencia,
  abstención segura y falta de holdout independiente. Los 59 contratos,
  incluido Blender y el puente de memoria, quedaron verificados.
- Research job 4 sobre `JARDINES_INTERPRETATIVOS.md` capturó cuatro fuentes,
  extrajo claims, relaciones, contexto e interpretación y dejó el siguiente
  paso en `simulate`; el runner histórico no tenía una función ejecutable para
  ese paso (`interpretive_simulation_callables=[]`,
  `research_router_simulation_callables=[]`), pero ahora existe el consumidor
  local simbólico `research_simulation_consumer`; el resultado permanece
  marcado como modelo y no como hecho. No se clonaron ni instalaron repos
  candidatos; la licencia y la revisión humana siguen pendientes.
- La revision de procedencia P versus NP incorporó
  `knowledge/math_targets/p_vs_np_official_statement_capture_2026-08-20.json`,
  con la pagina oficial de Clay, hash de la nota canonica y estado `Unsolved`.
  El artefacto formal local tiene hash completo y ambos hashes se guardan en la
  capsula; la fidelidad semantica permanece `UNTRUSTED` y el kernel sigue
  bloqueando cualquier promocion de verdad.
- La base local ignorada `data/mak_knowledge.db` contiene ocho episodios
  elegibles en cuatro proyectos; incluye el fixture verificado, el probe del
  consumidor de tenis. La política medida es `abstain` con razón
  `no_independent_holdout`, `eligible_examples=8`, `train_count=8` y
  `holdout_count=0`. No se promovió ninguna regla.
- La contradicción detectada en el handoff fue eliminada: ya no se escribe un
  total fijo de tests ni se recicla el conteo antiguo del learner.
- Se declaró en `web/package.json`, `web/package-lock.json` y
  `web/README.md` el requisito real `Node >=20.19.0`; con el Node 24.19.0
  disponible en MAK los builds reproducibles pasan.
- Los cambios de esta tanda se publicaron en `main` mediante el commit
  `7674c49` y el push normal a `origin/main`; la evidencia generada dentro de
  `data/mak_knowledge.db` sigue siendo estado local ignorado. La
  evidencia generada dentro de `data/mak_knowledge.db` es estado local
  ignorado; los writes explícitos fueron el refresh de contratos y la
  ingestion verificada del caso de memoria descrito arriba.
- Se retiraron Watsonx, AWS y Azure de la superficie operativa activa. Se eliminaron
  sus adaptadores, alias, capacidades, rutas de fallback, opciones CLI, UI y
  políticas de proveedores en `cultura/mak_plataforma/providers.py`,
  `cultura/mak_research/research_lib.py`, `research.py`, `refutar.py`,
  `cultura/mak_codex/codex_lib.py`, `cultura/mak_plataforma/hub.py`,
  `iskvw/editor.html`, `src/flujo/autonomia.py` y `src/flujo/cli.py`.
  Research queda con Groq -> Gemini -> Ollama; Cerebras permanece solo como
  opcion explicita porque el probe real devuelve HTTP 402. Codex conserva
  NVIDIA NIM -> Ollama; vision del portafolio queda local con el lector
  Ollama existente.
- Las herramientas Watson exclusivas se movieron, sin borrarlas, a
  `/home/mak/_archive/watsonx-retired-20260820/`: cuatro sondas/benchmarks y
  copias protegidas de `n8n-local/research.env` y `research/research.env` antes
  de retirar sus líneas Watson/AWS. No se tocaron `/home/mak/WIN`, ledgers,
  productos ni resultados históricos.
- Se retiró `boto3` de `pyproject.toml` y `requirements.txt`. La matriz y el
  mapa ahora describen los proveedores retirados como evidencia histórica, no
  como capacidad disponible. `python3 -m compileall` terminó con exit 0,
  `./.venv/bin/python -m pytest -q` terminó con exit 0 (warnings existentes de
  Pillow), y `git diff --check` quedó limpio.
- Se verificó el reemplazo de proveedores en el runtime y sus espejos. El
  adaptador Gemini usa `gemini-3.6-flash`, carga solo `GEMINI_API_KEY` y
  `GEMINI_MODEL` desde el `.env` secundario, y devuelve texto y JSON válidos.
  Los probes foreground de Groq, Gemini y Ollama devolvieron texto no vacío;
  Firecrawl capturó `https://example.com` mediante el backend configurado
  (`167` caracteres). El probe explícito de Cerebras devolvió HTTP 402
  `payment_required`, por lo que no participa en la cadena automática.
  Azure no conserva llamadas ni configuración activa; las coincidencias que
  quedan son comentarios, vocabulario de arqueología o resultados históricos.
  La copia vieja de `research_lib.py` y el workflow n8n retirado siguen
  preservados en `/home/mak/_archive/provider-retirement-20260820/`.
- El adaptador estructurado de `cultura/mak_plataforma/providers.py` fue
  endurecido para no truncar JSON cuando el llamador pide un presupuesto muy
  pequeño; su probe Gemini devolvió un objeto JSON válido. La suite completa
  pasó después de actualizar el test que aún esperaba Cerebras al frente de
  la ruta de riesgo alto.
- Se probó la regla arquitectónica "salir del espacio de soluciones" con dos
  fallos reales. Primero, una respuesta Gemini simulada con
  `finishReason=MAX_TOKENS` y sin `content.parts` no obligó a reparar Gemini:
  `LLM.call` la clasificó como vacía y continuó con Ollama (`status=ok`).
  Segundo, Firecrawl capturó la documentación oficial de Gemini con `236737`
  caracteres de navegación y contenido; una selección acotada de ventanas
  relevantes redujo la evidencia a `3119` caracteres y Ollama identificó
  `MAX_TOKENS` y la decisión de rechazar el resultado truncado. La conclusión
  es que la captura funciona y la dependencia que debe cambiar es el paso de
  evidencia-a-análisis, no Firecrawl. Este experimento fue read-only y no
  cambió código ni datos.
- En el primer lote de apuestas predictivas se eligieron dos verificaciones de
  alto aprendizaje y bajo costo. El contrato de proveedores (`PROVIDER_ORDER`,
  `PROVIDER_CAPABILITIES`, `PROVIDER_ENV_KEY` y métodos `LLM._*`) quedó
  consistente (`all_provider_contracts_consistent=true`). La búsqueda de
  interfaces antiguas solo encontró un comentario de endpoint legacy,
  resultados históricos y tres copias bajo `/home/mak/rollback/`; no encontró
  un consumidor activo roto. Ambas predicciones se descartan sin parche.
  El lote confirma que la unidad útil es `prediccion -> prueba barata ->
  descarte o patron`, no volumen de archivos.
- Se compararon los enfoques externo y resiliente. En la ruta externa,
  Firecrawl capturó la página oficial de precios de Cerebras (`4053`
  caracteres; ventana relevante `1424`), pero el resumen Ollama inventó un
  crédito de `$5`; la salida fue rechazada por falta de evidencia. La fuente
  confirma solo tier Free `$0` y límites menores, mientras el probe local real
  sigue en HTTP 402. La conclusión es `captura externa -> evidencia acotada ->
  validación`, nunca `captura -> verdad`.
- En la ruta resiliente se encontró y corrigió un bug real en
  `cultura/mak_plataforma/providers.py`: `TASK_CAPABILITIES["research"]`
  pedía la capacidad inexistente `research`, por lo que el router devolvía
  `local_deterministic` aun con proveedores disponibles. Ahora Research usa
  la capacidad declarada `hypothesis` y enruta `Groq -> Gemini -> Ollama`.
  Se agregó `test_research_route_uses_declared_hypothesis_capability`; el test
  enfocado y la suite completa terminaron con exit 0, y `git diff --check`
  quedó limpio.
- Se inició el experimento dual de depuración sobre Research/proveedores
  reutilizando `src/flujo/diagnostics.py` y el comando `flujo diagnose`, sin
  crear otro framework. Para el agente externo se generaron dos paquetes
  `mak-diagnostic-v1` read-only: ambos rutearon a Research, redacted datos
  sensibles, excluyeron WIN y entregaron contrato, rutas existentes, gate y
  reproducción. El primer postprocesador falló con `python: command not found`;
  al repetirlo con `.venv/bin/python`, el diagnóstico terminó con exit 0.
- El mismo slice para MAK validó `route_task("research")` como
  `hypothesis`, `Groq -> Gemini -> Ollama`, y simuló una respuesta Gemini sin
  `content.parts`: la salida pasó a Ollama sin bloquearse. El paquete Research
  tenía además una ruta inexistente (`src/flujo/research`); se eliminó de
  `src/flujo/diagnostics.py` y `context/diagnostics/domains.json`, y se agregó
  una regresión que exige `missing_read_paths=[]`. Tests enfocados, suite
  completa y compileall terminaron con exit 0; no se inició ningún servicio.
- Se agregó `src/flujo/index/code_index.py` y el comando `flujo code-index`.
  Construye `mak-code-structure-v1` con AST, símbolos, imports, consumidores,
  entradas, efectos y hashes, sin guardar texto fuente. Excluye `WIN`,
  `.agents`, `.codex`, `.claude`, entornos, caches y builds. El índice real
  `context/code_structure_index.json` contiene 781 módulos Python, 8552
  símbolos, 186593 líneas declaradas y cero errores de sintaxis; ocupa
  2671255 bytes. `--query` devuelve un `mak-code-brief-v1` acotado para que
  un agente abra solo candidatos relevantes. Se agregó regresión para
  consumidores relativos y errores de sintaxis aislados, y se sincronizaron
  `MAPA.md`/`context/comandos.json` con el generador oficial.
- El primer push del índice expuso dos fallos de portabilidad en CI: una ruta
  histórica con el usuario Windows real y un test que exigía un artefacto
  formal guardado fuera del clon. Se anonimizó la ruta en
  el registro histórico retirado y `tests/test_math_kernel.py` ahora valida el
  hash si el artefacto externo existe, pero hace `skip` explícito en clones
  limpios. `./.venv/bin/python -m flujo verify` y la privacidad local pasan;
  el commit `6743467` se publicó y CI #22/seguridad de ese SHA terminaron en
  `success`.

## Open integration items

| Item | Path | Status | Proof required |
| --- | --- | --- | --- |
| Python learning layer | `src/flujo/knowledge/learning_policy.py` | verified, published | full pytest exit 0; py_compile exit 0; diff check exit 0 |
| Web source | `web/` | verified, published | Node 24.19.0: `npm ci`, audit 0 vulnerabilities, typecheck and all three builds exit 0 |
| Documentation contract | `CAPACIDADES.md`, `docs/MAK_CURRENT_STATE.md`, this file | verified, published | docs hygiene included in full pytest exit 0 |
| Watson/AWS/Azure retirement and provider replacement | provider registries, research/codex chains, Hub/UI, env files, `pyproject.toml`, `requirements.txt`, `/home/mak/research/` | verified and published in `90f92be`; live runtime reloaded | full pytest exit 0; compileall exit 0; Groq/Gemini/Ollama/Firecrawl probes pass; Cerebras HTTP 402; recoverable archive present; `/api/status` after the Hub restart no longer reports watsonx |
| Operational status | `src/flujo/knowledge/system_status.py`, `cultura/mak_plataforma/hub.py`, `tools/mak_status.py`, `web/` | verified, published in `90f92be` and reloaded at 8900; lane registry included read-only | focused pytest; temporary/live `/api/status` HTTP 200; eleven components; read-only endpoint |
| Python structure index | `src/flujo/index/code_index.py`, `context/code_structure_index.json`, `tests/test_code_index.py` | published in `90f92be`; index regenerated from the published tree (783 modules, 8565 symbols, 0 syntax errors) | focused/full pytest exit 0; CLI probe; zero syntax errors; diff check exit 0 |
| Source learning bridge | `src/flujo/knowledge/source_learning.py`, `tools/source_learning_bridge.py`, `knowledge/learning_cases/`, `schemas/knowledge/source_learning_case.schema.json` | verified locally and recorded; published in `7674c49` | source roots/files/messages/claim boundaries pass; Project IR episode verified; no truth promotion |
| Cultural-first math kernel | `src/flujo/knowledge/math_kernel.py`, `tools/math_kernel.py`, `knowledge/math_targets/`, `schemas/knowledge/math_*.schema.json` | verified locally; one bounded metadata request queued; published in `7674c49` | capsule validation, common Project IR domains, sealed ResultCard guard and truth-promotion block |
| Cross-domain lane registry | `knowledge/lane_registry/`, `tools/project_lanes.py`, `schemas/knowledge/cross_domain_lane_registry.schema.json` | published in `90f92be`; 19 lanes, 3 priority-0 lanes, no new consumer claimed for proposals; `lanes` component ready in the live Hub | registry validation, common first-layer rule, evidence refs, guardrails and next gates |
| Tennis MCP first slice | `src/flujo/tennis/mcp.py`, `tools/tennis_mcp_ingest.py`, `tests/test_tennis_mcp.py` | verified locally; conservative parser and hash-linked JSONL projection; no external acquisition | focused pytest, syntax check, diff check; feeds the shot-event consumer |
| Tennis shot-event consumer | `src/flujo/tennis/shot_events.py`, `tools/tennis_shot_events.py`, `schemas/tennis/shot_event.schema.json` | verified locally; router-selected read-only consumer with explicit uncertainty and provenance; first episode recorded | schema validation, Project IR route test, focused pytest, verified episode; next is an independent second fixture |
| Tennis Project IR probe | `tools/project_gate.py`, `src/flujo/knowledge/episode_runner.py` | verified locally; route selects tennis consumer and probe status is `succeeded` without executing it | read-only project gate, recorded probe episode; next is independent evidence |
| Research source capture | `tools/research_source_capture.py`, `cultura/mak_research/source_pipeline.py` | verified locally; existing Research 4 capture linked, license remains pending, no broad crawl | 4 source hashes, verified capture/extract/interpret results; next is license review |
| Research simulation | `src/flujo/knowledge/research_simulation.py`, `tools/research_simulation.py`, `schemas/knowledge/research_simulation_manifest.schema.json` | verified locally; bounded symbolic trajectory, model-not-reality marker, no external calls | manifest schema, deterministic trajectory, budget abstention and Project IR route; next is human review |
| Deep-learning task gate | `src/flujo/knowledge/deep_learning_gate.py`, `tools/deep_learning_gate.py`, `schemas/knowledge/deep_learning_task_gate.schema.json` | verified locally; logo-clean episode abstains on 3-row/no-holdout evidence, training remains disabled | manifest schema, gate tests, Project IR episode; next is an independent holdout |
| Research learning | `/home/mak/research/jobs/4/` | captured/interpreted; bounded symbolic simulate consumer available; license review pending | review candidate grammar and license; no candidate install |
| Publication | `main` -> `origin/main` | verified at `90f92be`; remote CI green | `git rev-parse HEAD` equals `git ls-remote origin refs/heads/main`; CI, seguridad and Git topology guard all `success` |

## Tool and dependency verification matrix

| Surface | Command | Current result |
| --- | --- | --- |
| Python suite | `./.venv/bin/python -m pytest -q` | exit 0; warnings only from existing Pillow deprecation |
| Learning policy | `./.venv/bin/python tools/project_learning.py --db data/mak_knowledge.db` | exit 0; abstain; 8 eligible in 4 projects; no independent holdout |
| Source learning | `PYTHONPATH=src ./.venv/bin/python tools/source_learning_bridge.py knowledge/learning_cases/mak_pnp_search_ecology_2026-08-19.json --db data/mak_knowledge.db --record` | exit 0; 2 roots, 9 artifacts, 9 messages, 5 learning units; verified ingestion only |
| Python syntax | `./.venv/bin/python -m py_compile ...` | exit 0 |
| Diff hygiene | `git diff --check` | exit 0 after code-index and map synchronization |
| Python structure index | `./.venv/bin/python -m flujo code-index --root . --output context/code_structure_index.json --query "research provider route" --format json` | exit 0; 781 modules, 8552 symbols, 0 syntax errors; source-free index; 20 bounded query matches |
| Python dependencies | `./.venv/bin/python -m pip check` | exit 0; no broken requirements |
| Provider replacement probes | foreground `LLM(groq|gemini|ollama)` + platform `providers.call(gemini, response_format=json)` | exit 0; all text responses non-empty; Gemini structured response parsed as JSON object |
| Firecrawl capture | foreground `capture_url("https://example.com", backend="firecrawl")` | exit 0; backend `firecrawl`; 167 captured characters |
| Cerebras availability | foreground explicit `LLM(cerebras)` probe | expected failure; HTTP 402 `payment_required`; excluded from automatic route |
| Azure runtime audit | `rg` over active provider/runtime surfaces | no active Azure call/configuration; remaining matches are historical/comments/vocabulary |
| Web typecheck/build | `NODE_BIN=.../node ./node_modules/typescript/bin/tsc --noEmit`; `NODE_BIN=.../node ./node_modules/vite/bin/vite.js build`; `NODE_BIN=.../node scripts/copy-context.mjs` | exit 0 with Node 24.19.0; 1840 modules; `dist/index.html` 777.98 kB |
| Math Kernel cycle | `PYTHONPATH=src ./.venv/bin/python tools/math_kernel.py cycle --db data/mak_knowledge.db --target knowledge/math_targets/p_vs_np_target_capsule_2026-08-19.json --iterations 1 --compute-units 1 --max-expanded-cost 100` | exit 0; `mak-math-ledger-v1`; target `UNTRUSTED`; one `METADATA_ONLY` request; truth promotion blocked |
| Lane registry | `PYTHONPATH=src ./.venv/bin/python tools/project_lanes.py validate` | exit 0; `mak-cross-domain-lane-registry-v1`; 19 lanes; common `cultural_research_first` layer; read-only |
| Tennis MCP slice | `PYTHONPATH=src ./.venv/bin/python -m pytest -q tests/test_tennis_mcp.py tests/test_project_lanes.py` | exit 0; parser preserves raw notation, unknown tokens, source hash and `ANNOTATED` status |
| Tennis shot-event route | `PYTHONPATH=src ./.venv/bin/python -m pytest -q tests/test_tennis_mcp.py tests/test_project_router.py tests/test_project_contracts.py` | exit 0; schema-shaped events, unknowns/provenance preserved, Project IR selects `tennis_shot_event_consumer` |
| Scraping/deep-learning/simulation gates | `PYTHONPATH=src ./.venv/bin/python -m pytest -q tests/test_research_source_capture.py tests/test_deep_learning_gate.py tests/test_research_simulation.py` | exit 0; default scraping is plan-only, deep-learning gate abstains without independent holdout, simulation is bounded/model-labelled |
| Unified status CLI | `./.venv/bin/python tools/mak_status.py --db data/mak_knowledge.db --json` | exit 0; `mak-system-status-v1`; 11 components, including valid 19-lane registry; `render=ready`, no Blender process; 2 actionable and 2 informational ledger items; read-only; 59 contracts audited |
| Unified status HTTP | temporary `ThreadingHTTPServer` + live `127.0.0.1:8900` -> `GET /api/status` | HTTP 200 in both; `mak-system-status-v1`; `read_only=true`; temporary server shut down; live Hub active |
| Catalog federation | `src/flujo/knowledge/catalog_federation.py`, `tests/test_catalog_federation.py`, `data/mak_knowledge.db` | verified locally and integrated additively; 7 read-only sources, 124 tables, 2,075,337 observed rows, 0 copied; integrity and FK checks pass |
| Operational DB bridge | `src/flujo/knowledge/operational_bridge.py`, `tests/test_operational_bridge.py`, `data/mak_knowledge.db` | verified locally and refreshed; 6,132 normalized records, 106,895 curation links, exact package/project/fund links; source rows copied 0; integrity and FK checks pass |
| Web/DB audit gate | `tools/repo_audit.py`, `tests/test_repo_audit.py`, `.github/workflows/ci.yml`, `Makefile` | verified locally; 36 web modules, 35 reachable, 0 dead, 0 stale active references; four DBs have resolved consumer paths and integrity `ok`; published in `69e7fba` |
| RD live/standalone projection | `src/flujo/rd/panel.py`, `tools/gen_rd_standalone.py`, `web/src/data/rdDbEmbebida.json` | verified locally; generated and tracked JSON are equal (6 records, identical SHA-256); generator now accepts absolute output paths |
| SSD application intake | `tools/build_application_intake.py`, `/home/mak/labs/portable-ssd-index-20260813/archivo_index.sqlite` | verified in `/tmp`; 917 projects scanned, 3 bounded Fondart packages emitted, derived SQLite integrity `ok`; status remains `draft_with_evidence_gaps` |
| Latent project reconstruction | `src/flujo/knowledge/project_reconstruction.py`, `tools/project_reconstruction.py`, `tests/test_project_reconstruction.py`, `tools/build_application_intake.py` | verified and published in `96dd8cd`; durable outputs in `/home/mak/curatoria_inbox/project_reconstruction/2026-08-21/` |
| DB -> Research -> Curatoria -> Postulacion | temporary foreground pipeline using existing Research corpus, Curatoria diagnostic and `tools/build_application_intake.py` | exit 0; Research 5,179 applications/14 captures; Curatoria 917 projects/13,121 families/45,536 members; Postulacion emitted `drefgira-fondart` with explicit evidence gaps; source trees untouched |
| RD event fixture | read-only query over `operational_records` and `operational_curation_links` | exit 0; 7 events retain producer, raw date, venue and flyer/source evidence; 0 false ISO dates; 0 orphan curation links |
| Contract audit refresh | `PYTHONPATH=src ./.venv/bin/python -m flujo.knowledge.contract_registry --db data/mak_knowledge.db audit --root . --record --run-id simulation_consumer_20260820` | exit 0; 59/59 verified; Blender, source-learning bridge, math kernel, tennis, scraping, deep-learning and simulation consumers resolved |
| Hub smoke | `./.venv/bin/python scripts/hub_smoke.py --port 0 --timeout 20` | exit 0; temporary port 48545; no persistent hub |
| Remote parity | `git rev-parse HEAD` vs `git ls-remote origin refs/heads/main` | equal when the commands return the same value |

## Conflicts and risks

- `abstain` is intentional. Eight eligible episodes now span four projects, but
  the deterministic split still produced no independent holdout; promoting a
  general route policy would overstate the evidence.
- `data/mak_knowledge.db` and generated research SQLite/report files are local
  operational state and are not Git inventory. Their current state is noted,
  not copied into the web repo.
- Historical phase documents and recovered sessions remain evidence. They are
  not the current handoff and must not override this file.
- A green local check does not prove external GitHub Actions or provider
  credentials. The push completed normally and remote parity was checked;
  external CI remains an independent gate.
- The official P versus NP capture is a normalized curator note, not a
  verbatim source transcript or semantic-equivalence certificate. It supplies
  provenance and hashes but intentionally cannot change `UNTRUSTED`.
- The current `attention` state is intentional and concrete: two ledger
  evidence gaps plus two informational safety states. Do not silence it by
  deleting episodes or promoting same-project data. The Blender dependency is
  no longer an open gap; its fresh audit is verified.
- Watsonx, AWS and Azure historical labels remain in preserved ledgers, old
  visual records, comments and legacy triangulation filenames. They are data
  provenance, not executable integrations. Do not delete or reinterpret those
  records as current provider health. Cerebras remains configured only for
  explicit diagnostic use; its current billing response is HTTP 402 and it is
  not part of the default chain.

## Active cleanup audit — 2026-08-21

Se depuro la configuracion activa para que MAK Linux no presente superficies
Windows obsoletas como si fueran runtime. Se retiraron los lanzadores
`abrir_hub.bat`, `instalar.bat`, `launch-flujo.bat`, `launch-flujo.ps1`, el
puente `tools/bridge_issue_render.py`, sus helpers SendTo y su e2e, y el
workflow Claude deshabilitado. Sus copias historicas siguen en
`/home/mak/WIN` o en la evidencia recuperada. Se retiro solo el test que
ratcheaba esos lanzadores; se conservaron el mirror y los tests de seguridad
que aun tienen consumidores reales.

XIO fue corregido durante la auditoria: no es basura ni se elimina. Se
restauro `.github/workflows/build-xio-apk.yml` como build manual diferido y
se documento como integracion futura Chataigne/OSC para shows, venues y VJ.
No se ejecuta en cada CI ni se confunde con la ruta diaria de FLUJO/RD.

Tambien se actualizaron `CAPACIDADES.md`, `docs/MAK_CURRENT_STATE.md`,
`docs/FLUJO_AREAS_EVENTOS_SUPLEMENTOS.md`, `src/flujo/web/hub.py`, los
paneles web de automatizaciones/eventos, `Makefile`, `pyproject.toml` y los
tests afectados. Se regeneraron `tests/fixtures/idioma_baseline.txt`,
`context/code_structure_index.json` y los HTML de `context/`.

Validacion en primer plano:

- `./.venv/bin/python -m pytest -q` -> exit 0; suite completa, skips esperados.
- Tests focalizados de higiene, contratos Git/web, mirror, GPU, idioma,
  code-index y status -> exit 0.
- `npm run typecheck` en `web/` -> exit 0.
- `npm run build:context` -> exit 0; Node 18 emitio advertencia porque el
  requisito declarado es Node >=20.19, pero el bundle se genero.
- `git diff --check` -> exit 0.

Se agrego `tools/repo_audit.py` como gate read-only del arbol web y las cuatro
SQLite locales. La auditoria real devuelve 36 modulos, 35 alcanzables, 0
muertos, 0 referencias activas obsoletas; `data/rd.db` tiene 20 tablas/7,585
filas, `data/rd_datos.db` 3/0, `data/mak_knowledge.db` 30/369,157 y
`data/flujo.db` 1/6; las cuatro pasan `integrity_check` y todas sus rutas de
consumidor existen. Se corrigio el mapa para no declarar `src/flujo/rd/panel.py`
como lector de `data/rd.db`: el panel lee JSON/YAML canonicos y solo proyecta.

La validacion de `gen_rd_standalone.py` genero en `/tmp` los mismos 6 registros
que `web/src/data/rdDbEmbebida.json`, con SHA-256 identico; el unico fallo
encontrado era el reporte de una ruta absoluta externa y quedo corregido sin
alterar la salida. El intake real uso el indice fuente
`/home/mak/labs/portable-ssd-index-20260813/archivo_index.sqlite`, no el
`intake.sqlite` derivado: con limite 3 y fondo Fondart produjo tres paquetes
`drefgira-fondart`, `felina-logo-fondart` y
`descargas-hasta-rdflyer-2050-fondart` en `/tmp/mak-intake-audit-20260821`.
La salida queda correctamente en `draft_with_evidence_gaps`; no se escribio
la DB de aprendizaje ni se modifico la fuente del SSD.

Riesgos conservados deliberadamente: `tools/mak_ops/check_mak_mirror.py`
todavia contiene una ruta SSH historica y requiere una fase separada de
reemplazo local; `src/flujo/version.py` y `docs/recovered/` conservan
referencias de changelog/evidencia, no runtime. No se borraron `/home/mak/WIN`,
XIO, bases, artefactos ni cambios ajenos.

## Post-publication runtime sync — 2026-08-21

El commit `90f92be` ("chore: publish provider and cross-domain runtime")
publico en un solo commit atomico los tres conjuntos que quedaban fuera de
`69e7fba`: retiro de Watsonx/AWS/Azure, write set cross-domain completo y la
correccion del paquete de diagnostico Research. 81 archivos, +2172/-1905.
`main` y `origin/main` quedaron sincronizados en `90f92be`; el CI remoto pasa
en los tres jobs: `CI` (run 32454523320), `seguridad` (32454523238) y
`Git topology guard` (32454523301). Los cuatro tests que estaban rojos en
`268ef4b` pasan: `test_tools_en_registro`,
`test_registro_sin_herramientas_fantasma`,
`test_no_new_file_carries_spanish_comments` y
`test_the_manifest_is_not_stale_against_the_real_cli`. La causa raiz fue
publicar artefactos derivados generados desde un worktree sucio mientras sus
fuentes quedaban sin stagear; no volver a publicar `CAPACIDADES.md`,
`context/comandos.json`, `idioma_baseline.txt` o el code index sin las fuentes
que describen.

Resolucion del Grupo 4, sin consultar: en `src/flujo/version.py` se revirtio
el unico hunk que falsificaba evidencia temporal, de modo que el incidente de
claves de 2026-07-16 conserva sus proveedores reales
(Tavily/Groq/Cerebras/Azure); `tests/test_privacidad_repo.py` volvio al estado
publicado porque su exencion nueva no tenia sujeto
 (el registro histórico ya no forma parte del árbol activo y tiene 0
coincidencias). Las versiones de worktree quedaron en
`/home/mak/_archive/group4-reverted-20260821/`.

El indice `context/code_structure_index.json` se regenero desde el arbol
publicado: 783 modulos Python, 8565 simbolos, 187046 lineas declaradas, 0
errores de sintaxis, sin texto fuente. Ya no declara los cuatro modulos
watsonx y `lane_registry` resuelve su consumidor real
(`imported_by = src.flujo.knowledge.system_status`).

El Hub existente `mak-hub.service` es un unit de usuario
(`systemctl --user`), no de sistema; su launcher
`/home/mak/plataforma/hub.py` es una proyeccion que carga la implementacion
canonica `cultura/mak_plataforma/hub.py` del repo. Se reinicio solo ese
servicio. Evidencia del reload: antes del reinicio `/api/status` aun
mencionaba `watsonx`; despues menciona `gemini` y ya no `watsonx`. GET
verificados: `/health` 200 (`mak-hub-health-v1`), `/api/status` 200
(`mak-system-status-v1`, `read_only=true`, 11 componentes, `status=attention`
con 2 accionables y 2 informativos, componente `lanes` `ready` y valido),
`/api/research/catalog` 200, `/api/project/learning` 200, `/api/rd/summary`
200 y `/api/rd/crosswalk` 200. `/api/rd-db` devuelve 404
`ruta_api_no_encontrada`: esa ruta no existe, las reales son `/api/rd/*`. No
se llamo ningun mutador y no se inicio ningun servicio nuevo;
`mak-codex.service` y `mak-research.service` siguen activos sin tocarse.

Proveedores probados una sola vez en primer plano con los adaptadores
existentes: `research_lib.LLM` devolvio texto no vacio para `groq`, `gemini` y
`ollama`; `cerebras` devolvio HTTP 402 `payment_required`;
`providers.call("gemini", response_format="json")` devolvio JSON valido; y
`source_pipeline.capture_url("https://example.com", backend="firecrawl")`
capturo 167 caracteres con backend `firecrawl`. El registro
`faro-provider-registry-v1` lista groq, gemini, cerebras y ollama como
`configured`, sin Watsonx, AWS ni Azure. `route_task("research")` resuelve
capacidad `hypothesis` con proveedor `groq`.

## Continuity after Claude quota interruption — 2026-08-21

Claude Code agoto su cuota despues de publicar `4c12bba` mientras anunciaba
el inicio de la validacion del slice de portabilidad/pipeline. No quedo un
comando de intake, render, pytest ni Blender corriendo. El archivo temporal
`/tmp/mak_continuation_result.json` es evidencia de una ejecucion anterior y
termina en `9841cc8`; no usarlo como estado actual ni como fuente para repetir
trabajo.

Estado fisico comprobado en primer plano: `main == origin/main == 4c12bba`,
worktree limpio; `mak-hub.service`, `mak-research.service` y
`mak-codex.service` siguen activos como unidades de usuario existentes. GET
read-only de Hub `/health`, `/api/status`, `/api/research/catalog`,
`/api/project/learning`, `/api/rd/summary` y `/api/rd/crosswalk` devolvieron
HTTP 200. Research `8890` y Codex `8891` devolvieron HTTP 200 en su raiz.

Validacion actual, sin mutar fuentes: `route_task` devolvio las cadenas
automaticas `groq -> gemini -> ollama` para research, curation y review;
judge resolvio `ollama -> local_deterministic`; Cerebras solo aparece cuando
el caller lo nombra explicitamente. Tests de intake, puente operativo,
source-learning y tandas pasaron (`pytest`, exit 0). Integridad read-only de
`data/rd.db`, `data/rd_datos.db`, `data/mak_knowledge.db` y `data/flujo.db`
devolvio `ok` en las cuatro bases. `compileall` y `git diff --check` pasaron,
exit 0. No se modificaron archivos del runtime durante esta comprobacion.

Advertencia de evidencia CORREGIDA el 2026-08-21: esa afirmacion era falsa.
El indice fisico externo si esta presente en
`/home/mak/labs/portable-ssd-index-20260813/archivo_index.sqlite`
(175689728 bytes, 2026-08-13). El generador de intake se re-ejecuto y el
pipeline quedo medido de punta a punta; ver la seccion
`Pending-slice closure` mas abajo. No usar la advertencia anterior como razon
para no medir.

Riesgo residual: el nombre historico `PROVIDER_ORDER` aun contiene Cerebras
para poder mostrarlo en el registro diagnostico; esto no lo vuelve fallback,
porque `provider_plan` lo excluye sin `available=["cerebras"]`. No cambiarlo
sin actualizar el contrato de registro y sus tests.

Archivos modificados en esta continuidad: solo este handoff dentro del repo.
Fuera del repo se agrego una fuente de evidencia acotada bajo
`/home/mak/curatoria_inbox/tennis_sources/2026-08-21/` y se agrego de forma
append-only el Project IR/episodio correspondiente a `data/mak_knowledge.db`.
No hubo borrado, instalacion ni nuevo servicio.

## Independent tennis evidence — 2026-08-21

La segunda fuente independiente ya fue ingerida y validada. Fuente publica:
`https://raw.githubusercontent.com/JeffSackmann/tennis_MatchChartingProject/master/charting-m-points-2020s.csv`.
El archivo completo quedo fuera del repo en
`/home/mak/curatoria_inbox/tennis_sources/2026-08-21/charting-m-points-2020s.csv`
con SHA-256
`2cd43f73e0530a47ac02b99dae40177ca6d58a8ccf9189358eb05dffb4be9a`.
La licencia y atribucion CC BY-NC-SA 4.0 estan registradas en
`SOURCE_MANIFEST.json`; no se permite uso comercial.

Se extrajeron solo dos filas reales del partido
`20260521-M-Roland_Garros-Q3-Jesper_De_Jong-Michael_Zheng` a
`charting-m-points-2020s-extract.csv`, hash
`ac618e8222d02aa051b6d92dfd6414796974bc90fe362c65067f0c031faea822`.
`tools/tennis_shot_events.py` produjo 11 eventos; el validador JSON Schema
paso, el hash del extracto se propago a cada evento y 35 tokens desconocidos
se conservaron sin inferencia.

Project IR `mak-tennis-decision-lab-external-20260821` quedo `active` con
episodio verificado `episode-tennis-external-mcp-20260821`. La primera ruta
abstuvo correctamente porque el proyecto fue etiquetado tambien como
`research`; al corregir su dominio a solo `tennis`, la ruta selecciono
`tennis_shot_event_consumer` con `execute_read_only`. El aprendizaje global
se consulto en modo read-only: `status=abstain`, `eligible_examples=9`,
`holdout_count=0`, `recordable=false`; la nueva evidencia no se transformo en
entrenamiento ni en regla promovida.

## RD thematic integration — 2026-08-21

La seccion RD de `flujo serve` ahora separa la proyeccion canonica en cinco
temas read-only: operacion en terreno, calendario/red de eventos, testeo y
evidencia, productos/activos de entrega y puentes con Cultura/Portfolio. La
separacion es una vista, no una segunda base: `data/rd.db` sigue siendo la
proyeccion canonica y `data/rd_datos.db` sigue vacia como frontera de runtime.

Se agrego el contrato `mak-rd-topics-v1` en `src/flujo/departments.py` y se
expuso en los dos servidores locales: `flujo serve` (`/api/rd/topics`) y el
Hub 8900 (`/api/rd/topics`). `flujo serve` tambien recupero `/api/rd-db` y
los logos en GET read-only, por lo que la interfaz RD ya no queda desconectada
cuando se abre por el servidor stdlib. El panel muestra los cinco temas y los
puentes sin habilitar mutaciones.

Validacion de esta fase:

- `./.venv/bin/pytest -q tests/test_serve_api.py tests/test_departments.py tests/test_rd_db_logos.py tests/test_tarifa_una_sola_fuente.py`: exit 0, 46 tests.
- `./.venv/bin/pytest -q --disable-warnings`: exit 0, suite completa.
- `npm run typecheck`: exit 0.
- `npm run build:context`: exit 0; warning no bloqueante: Node 18.20.4 esta bajo el minimo recomendado por Vite 7.
- `npm run build:rd`: primero exit 1 por `import.meta.dirname` en `copy-rd-share.mjs`; corregido con `fileURLToPath`, segundo intento exit 0.
- servidor temporal de `flujo serve`: `/api/rd/topics`, `/api/rd/summary`, `/api/rd-db` y HTML respondieron HTTP 200; se detuvo al terminar.
- `git diff --check` y `compileall`: exit 0.

Write set: `src/flujo/departments.py`, `src/flujo/serve/`,
`src/flujo/web/hub.py`, `cultura/mak_plataforma/hub.py`,
`web/src/components/RdDbPanel.tsx`, `web/scripts/copy-rd-share.mjs`, pruebas y
los HTML compilados de `context/`. No se modificaron bases, WIN, README/SVG
protegido ni se dejaron servicios nuevos.

## Pending-slice closure — 2026-08-21

Se retomaron exclusivamente los slices que quedaron abiertos en la sesion
interrumpida por cuota. Los slices ya cerrados (`a5b1900`, `1f474e7`,
`4c12bba`, `7f99a50`, `2a6e2e0`, `5d915cb`) no se repitieron ni se revirtieron.

Estado verificado antes de tocar nada: `main == origin/main == 5d915cb`,
worktree limpio. Cerebras: `route_task` devolvio `groq -> [gemini, ollama]`
para research, curation y review, y `ollama -> [local_deterministic]` para
judge; `OPT_IN_PROVIDERS == {'cerebras'}`. Guards de proyecciones, proveedores
y hub: exit 0. Ese conjunto ya estaba cerrado y solo se comprobo.

Defecto real encontrado y reparado: el mismo par de bugs que se habia
corregido en `cultura/mak_plataforma/hub.py` seguia intacto en
`src/flujo/web/hub.py`, el hub de `flujo serve`. Publicaba
`registry: "research/jardines_interpretativos/jardines_interpretativos.sqlite"`,
una ruta relativa que no resuelve desde ningun directorio de trabajo porque el
registro vive fuera del repo, y `/api/research/job` sin `id` devolvia el
`ValueError` crudo de `int()`. Reparar una sola superficie fue lo que permitio
que el bug sobreviviera, asi que ahora
`tests/test_research_registry_contract.py` fija el contrato en las dos y
compara sus respuestas campo por campo.

Segundo defecto real: `system_status` mantenia su propia lista de candidatos de
Node que terminaba en `PATH` mas un runtime de codex, por lo que informaba
`node available` para el 18.20.4 de `PATH` mientras `web/package.json` declara
`>=20.19.0` y en la misma maquina existen 20.20.2 y 24.x sin listar. La
resolucion se unifico en `runtime_tools` (`node_candidates`, `resolve_node`,
`declared_node_minimum`, que lee el minimo del manifiesto en vez de copiarlo) y
`flujo doctor` ahora nombra el binario que cumple en lugar de dejar que el
build avise y el llamador adivine. Se retiro el `import shutil` que quedo
muerto en `system_status`.

Comandos exactos y codigos de salida:

- `./.venv/bin/python -m pytest -q tests/test_physical_projections.py tests/test_mak_tandas.py tests/test_mak_hub_salud.py -rs`: exit 0.
- `./.venv/bin/python -m pytest -q tests/test_research_registry_contract.py -rs`: exit 0.
- `./.venv/bin/python -m pytest -q tests/test_node_runtime_requirement.py -rs`: exit 0.
- `./.venv/bin/python -m pytest -q tests/`: exit 0, suite completa.
- `./.venv/bin/python scripts/hub_smoke.py --port 0 --timeout 25`: exit 0, puerto efimero 60831, detenido.
- servidor temporal de `flujo.web.hub` en puerto efimero: `/api/research/catalog` HTTP 200 con ruta absoluta y `registry_exists=true`; `/api/research/job` sin `id` HTTP 400 `id_requerido`; `?id=4` HTTP 200; `?id=abc` HTTP 400 `id_requerido`; servidor detenido y thread confirmado muerto.
- `./.venv/bin/python -m flujo doctor`: exit 0; fila `node` avisa que `/usr/bin/node` v18.20.4 esta bajo `>=20.19.0` y nombra un v24.19.0 local.
- `./.venv/bin/python -m flujo diagnose --area research`: exit 0; `route_contract=True`, `local_hub_8900=True`.
- `./.venv/bin/python -m flujo verify --no-pytest`: exit 0; hub smoke en puerto efimero 38231, detenido.
- `flujo health`, `flujo version`, `flujo rd-db packs|eventos|venues|productora creamfields`, `flujo knowledge list`: exit 0 cada uno.
- `tools/research_job_router.py ... --db <temp>`: exit 0; `job_id=5`, `validation=PASS`, `external_calls=0`; la politica emitida dice `Groq o Gemini`, lo que valida el fix de proveedores de punta a punta.
- `tools/execute_research_job.py --job-id 5 --db <temp> --max-sources 1`: exit 0; captura firecrawl con hash, `model_calls=0`, `license_policy` exige revision humana.
- `cultura/mak_curatoria/diagnostico_proyectos.py --db <copia temp> --out <temp>`: exit 0; 45536 miembros, 917 proyectos, cinco salidas derivadas.
- `tools/build_application_intake.py --source-index <SSD real> --out-dir <temp> --fund Fondart --candidate-limit 3 --mak-db data/mak_knowledge.db`: exit 0; tres paquetes `drefgira-fondart`, `felina-logo-fondart`, `descargas-hasta-rdflyer-2050-fondart`; `learning_materialized=[]`; el paquete es `mak-application-package-v1` con `status=draft_with_evidence_gaps`, `readiness=90.0`, fondo `candidate_unverified`, `gaps` con severidad `blocking` y `next_action` explicito; SHA-256 del indice fuente identico antes y despues (`d3afb072fe163312...`).
- `tools/repo_audit.py`, `compileall -q src tools tests`, `pip check`, `git diff --check`: exit 0 los cuatro.
- `npm run typecheck` en `web/` con el Node local v24.19.0: exit 0, sin el aviso de version.
- publicacion: commit `fe104ee`, push a `origin/main` exit 0, `HEAD == origin/main`, worktree limpio. CI remoto de `fe104ee` en los tres jobs: `CI` success, `seguridad` success, `Git topology guard` success.

Archivos modificados: `src/flujo/web/hub.py`,
`src/flujo/knowledge/runtime_tools.py`,
`src/flujo/knowledge/system_status.py`, `src/flujo/cli.py`,
`tests/test_research_registry_contract.py` (nuevo),
`tests/test_node_runtime_requirement.py` (nuevo) y este handoff. No se tocaron
bases, WIN, README/SVG, XIO ni el mirror SSH. No se instalo nada y no quedo
ningun servicio ni proceso nuevo: los unicos servidores fueron temporales en
primer plano y se detuvieron.

Riesgos: (1) `PATH` sigue resolviendo Node 18.20.4, asi que un build hecho sin
`NODE_EXE` seguira emitiendo el aviso de Vite; el arreglo hace visible el
binario correcto, no cambia el `PATH` del sistema. (2) `PROVIDER_ORDER` sigue
nombrando Cerebras a proposito para poder mostrarlo en el registro
diagnostico; `provider_plan` lo excluye sin `available=["cerebras"]` y dos
tests lo fijan. (3) Las tres unidades de usuario `mak-hub`, `mak-research` y
`mak-codex` siguen sirviendo el codigo anterior en memoria hasta que se
reinicien; esta fase no las reinicio porque solo cambio `flujo serve`, que no
es un servicio permanente.

## Ledger open-state repair and probe closure — 2026-08-21

Se cerraron los dos unicos items accionables que quedaban en el ledger, y en el
camino aparecio un defecto mas importante que ellos.

Defecto encontrado: `operational_status` construia su lista de atenciones desde
`SELECT status,COUNT(*) FROM project_episodes GROUP BY status`, es decir sobre
el historial completo, y los episodios son append-only por diseno. Eso hacia
que un item como `3 episode(s) need evidence` **no pudiera limpiarse haciendo
el trabajo que el propio item pedia**: al registrar la ejecucion verificada, la
fila antigua seguia contando y el operador perdia la diferencia entre "hay
trabajo" y "el trabajo se hizo". El defecto era latente, no activo: en ese
momento los tres `needs_evidence` eran el episodio mas reciente de su proyecto,
asi que el conteo aun era verdadero. Por eso habia que arreglarlo ANTES de
cerrarlos, no despues.

Reparacion minima: se agrego `_open_episode_states()` en
`src/flujo/knowledge/project_api.py`. El histograma historico sigue publicado
sin cambios en `episodes` porque es evidencia; la lista de atenciones lee ahora
`episodes_open`, donde un episodio no aceptado sigue abierto solo mientras su
proyecto no tenga uno aceptado posterior, que es literalmente lo que describe
su propio `next_action`. El conjunto de estados que cuentan como cerrados se
reutiliza de `learning_policy.VERIFIED_OUTCOME_STATUSES` en vez de escribir una
segunda copia.

Trabajo cerrado con esa base: `episode-research-simulation-probe-20260820` y
`episode-tennis-consumer-probe-20260820` estaban en `needs_evidence` con
`plan_fingerprint` vacio porque el probe solo prepara el comando y por
contrato nunca ejecuta el consumidor. Se ejecutaron los dos consumidores reales
en primer plano y se validaron:

- `tools/research_simulation.py knowledge/research_simulations/job4_lsystem_candidate_20260820.json --output <evidencia>`: exit 0. Validador `deterministic_rerun_and_marker_check`: una segunda corrida produjo salida byte-identica (mismo sha256), `schema=mak-research-simulation-result-v1`, `observed_or_simulated=simulated`, `model_not_reality=true`, `environment.biological_claim=false`, `errors=[]`.
- `tools/tennis_shot_events.py tests/fixtures/tennis_mcp_fixture.csv <evidencia>`: exit 0, 4 eventos. Validador `schemas/tennis/shot_event.schema.json` con `Draft202012Validator`: 0 errores de esquema, cada evento conserva `source`, `provenance` y `epistemic_status`, y `observed` y `derived` siguen separados.
- Registro por el adaptador sancionado, no a mano:
  `tools/project_learning.py --db data/mak_knowledge.db --record-result <packet>`
  exit 0 en ambos, con paquetes `mak-verified-result-v1`; el adaptador falla
  cerrado si falta proyecto, evidencia, validador o checks.

Efecto medido: `episodes:needs_evidence` bajo de 3 a 1. Sin la reparacion
anterior habria seguido marcando 3. El historial quedo intacto: las tres filas
`needs_evidence` siguen existiendo, se agregaron dos episodios `succeeded`,
`PRAGMA integrity_check` devolvio `ok` y no se reescribio ni borro nada. Se
tomo copia previa de la base antes de escribir.

El `needs_evidence` restante NO es un defecto y no se debe cerrar
mecanicamente. Es `episode_scd_evidence_closure_20260819` del proyecto
`project-5047cc3a2269b5031460` (SCD, `review_required`), y sus checks mecanicos
estan todos en verde (`source_root_exists=true`,
`representative_artifacts_missing=0`). Lo que lo mantiene abierto son seis
`unknowns_preserved` que exigen evidencia humana u oficial: convocatoria
vigente no verificada, problema y contexto que deben formularse desde el
proyecto y no inferirse del nombre de la carpeta, metodo artistico, presupuesto
autorizado, cronograma verificable y equipo sin promover identidades por nombre
de carpeta. El sistema se esta negando correctamente a convertir metadata de
carpeta en una postulacion.

Archivos modificados: `src/flujo/knowledge/project_api.py`,
`tests/test_open_episode_state.py` (nuevo) y este handoff. Fuera del repo se
agrego evidencia en `/home/mak/curatoria_inbox/probe_closures/2026-08-21/`
(las dos salidas de consumidor con hash y los dos paquetes) y dos episodios
append-only en `data/mak_knowledge.db`, que es estado local ignorado.

Validacion: `pytest -q tests/` exit 0; `tests/test_open_episode_state.py` exit
0; `compileall`, `tools/repo_audit.py` y `git diff --check` exit 0.

Riesgo: `projects:review_required` sigue en 4 y se cuenta sobre el estado del
proyecto, no sobre episodios, asi que esa via no la toca esta reparacion. Antes
de tratarla hay que decidir que evidencia autoriza una transicion de proyecto;
no cambiarla sin ese contrato.

## Latent project reconstruction and quota recovery — 2026-08-21

La sesion de Claude Code `3428381a-02ad-4101-9da5-8176cf72c147` termino por
cuota despues de escribir el nucleo no publicado
`src/flujo/knowledge/project_reconstruction.py`. Se recupero la transcripcion
linea por linea y no se repitio su investigacion. Claude habia medido que el
indice real contiene 917 filas de proyecto y que 758 (82,7 %) tienen la firma
de biblioteca descargada `assets/<kind>/<name>_<uuid4>`. Tambien confirmo que
`DREFGIRA`, `DREFMOVISTAR`, `DREF CHOCOLATE` y `DrefQuila` no deben fusionarse
por compartir el prefijo `DREF`.

El nucleo quedo completado y validado como `mak-project-reconstruction-v1`:
usa una cascada lexicografica falsificable, no un score universal; conserva
RAW INPUT, OBSERVATION, DERIVED FEATURE, RELATION, INTERPRETATION e UNKNOWN;
no hashea el SSD de 940 GB y abre el indice en modo read-only. La salida incluye
decisiones, features, relaciones, asignacion de cada asset, fingerprint,
resumen por unidad y una proyeccion HTML inspeccionable.

El consumidor `tools/build_application_intake.py` acepta ahora
`--reconstruction`. Filtra bibliotecas y recursos compartidos para que no
compitan como postulaciones y conserva la decision de reconstruccion dentro de
la evidencia del paquete `mak-application-package-v1`.

Resultados reales persistidos fuera del repo:

- DREFGIRA: baseline 8 filas, 3 bibliotecas; reconstruccion 1 unidad, 4
  subproyectos, 3 dependencias; 467/467 assets reconciliados; 2 relaciones
  cross-root UNKNOWN. El intake produjo `drefgira-fondart` con gaps humanos
  explicitos y SQLite derivada integra.
- FELINA/LOGO: baseline 21 filas, 20 bibliotecas; reconstruccion 1 unidad,
  15 dependencias y 5 recursos compartidos; 2219/2219 assets reconciliados.
- BAHPARTY/bah: baseline 50 filas, 49 bibliotecas; reconstruccion 1 unidad y
  49 recursos compartidos; 87/87 assets reconciliados. La comparacion con
  `BAHPARTYCONCERESI` queda `UNKNOWN` por un sample hash sin `full_sha256`,
  preservando las alternativas y sin convertir la marca en postulacion.
- Los dos runs conservan el fingerprint del indice
  `d3afb072fe1633125ac20da82aa1d3c7514f763cb8cac28655f19216ac53d8df`.

Rutas durables:
`/home/mak/curatoria_inbox/project_reconstruction/2026-08-21/`.
En ese write set la fuente SSD y `data/mak_knowledge.db` no fueron
modificadas; el slice posterior de Project IR se describe a continuacion.

Validacion de esta tanda: tests focalizados 14 passed; suite completa
`./.venv/bin/python -m pytest -q --disable-warnings` exit 0; `repo_audit.py`
exit 0 (36 modulos, 35 alcanzables, 0 muertos); `py_compile`, `pip check` y
`git diff --check` exit 0; las dos SQLite derivadas verificaron
`PRAGMA integrity_check = ok`.

Archivos del write set: `src/flujo/knowledge/project_reconstruction.py`,
`tools/project_reconstruction.py`, `tests/test_project_reconstruction.py`,
`tools/build_application_intake.py`, `CAPACIDADES.md`,
`docs/MAK_CURRENT_STATE.md` y este handoff.

## Next concrete action

El write set de reconstruccion ya esta publicado en `96dd8cd` y el tercer scope
`BAHPARTY/bah` tambien fue validado. No repetir DREFGIRA, FELINA/LOGO ni la
sesion de Claude. El puente de este slice ya conecto un scope real DREFGIRA
con Project IR y el router compartido: se generaron 5 registros review-only,
467 artefactos indexados, 5 abstenciones por evidencia y 0 postulaciones o
publicaciones. `data/mak_knowledge.db` recibio esos 5 registros mediante
`--db`; el indice SSD mantuvo el mismo fingerprint e integridad.

Mantener `BAHPARTYCONCERESI` como `UNKNOWN` hasta obtener evidencia adicional.
No generar una postulacion de BAH solo por la clasificacion mecanica de su
carpeta. El siguiente slice ejecutable es cerrar la evidencia del montaje
fisico para DREFGIRA o, si el SSD sigue desmontado, integrar el siguiente
consumidor read-only que pueda trabajar con referencias indexadas; no cambiar
`review_required` a `active` por una inferencia de carpeta.

Los slices de proveedores, contratos de hub, rutas de registro,
proyecciones fisicas, portabilidad de entrypoints, pipeline
DB -> Research -> Curatoria -> Postulacion y requisito de Node estan medidos y
cerrados; releerlos no aporta evidencia nueva.

El recargado del runtime YA SE HIZO en esta misma fase y no hay que
repetirlo. Se reinicio unicamente `mak-hub.service`, porque es el unico
servicio que carga los modulos tocados (`system_status`); `mak-research.service`
y `mak-codex.service` no dependen de este write set y quedaron intactos y
activos. Evidencia: MainPID paso de 245666 a 297744; antes del reinicio la
evidencia de node en `/api/status` solo traia `['available', 'path']` y despues
trae `declared_minimum` `>=20.19.0` y cuatro candidatos; `/api/status` sigue en
`read_only=true` con once componentes; `/api/research/catalog` devuelve la ruta
absoluta con `registry_exists=true`; `/api/research/job` sin `id` devuelve HTTP
400 `id_requerido` y con `id=4` devuelve HTTP 200.

Auditoria adicional de esta fase, sin hallazgos nuevos: los dos hubs comparten
nueve rutas y se comprobo que ya no divergen. `/api/rd/topics` delega en el
contrato compartido `rd_topics` de `src/flujo/departments.py` en ambos;
`/api/status` del hub de `serve` conserva sus campos historicos de servicio y
anida el mismo sobre `mak-system-status-v1` en `operational` con
`read_only=true`, que es el diseno documentado y no una divergencia;
`/api/organismo` del hub de `serve` es un proxy al 8900, no una segunda
implementacion. Los unicos contratos que si divergian eran los dos reparados
aqui.

No queda una accion de integracion segura y ejecutable pendiente en este
alcance. El siguiente agente debe partir del commit de esta fase y elegir un
slice nuevo con fuente, consumidor y validacion propios.

Fuera de alcance y deliberadamente pendientes, porque dependen de licencia,
decision humana o hardware externo: la licencia de Research 4
(`result.license_review = pending`), el holdout independiente del gate de deep
learning (`abstain` con 9 elegibles y holdout 0), XIO (solo
`workflow_dispatch`), el mirror SSH historico
(`tools/mak_ops/check_mak_mirror.py`) y cualquier promocion de verdad
matematica (`MILLENNIUM-PNP-001` sigue `UNTRUSTED`).

## Previous completed checkpoint

The operational DB bridge is complete for the current source contracts. The
master now carries a normalized projection without replacing source authority:
RD events/producers/venues, Fondart v5 applications, intake projects/funds/
packages, and the existing `mak_links` curation surface. The real bridge
returned exit 0, wrote 6,132 normalized records, transferred 106,895 curation
links, copied 0 source rows, and a foreground SQL check resolved
`SCD package -> SCD project -> Fondart -> 12 curation links`.

The foreground `DB -> Research -> Curatoria -> Postulacion` check is complete:
Research exposed 5,179 applications and 14 captures read-only; Curatoria
processed 917 projects, 13,121 families and 45,536 members in a temporary
SQLite copy; Postulacion generated `drefgira-fondart` with explicit evidence
gaps. Exit was 0 and source trees were untouched. Preserve unknown dates as
`date_raw`, accept exact source-key joins as exact, and retain candidate venue
links with confidence.

The DB pipeline and RD event fixture are green. The next action belongs to the
separate operational audit: run the next real consumer/event fixture only if
it represents a different path, and fix only a runtime blocker. Do not start
autonomy, deep learning, broad reindexing or another database until the
declared current consumers are green.

## Last verified

2026-08-21 America/Santiago — cierre de los slices que quedaron abiertos por la
interrupcion de cuota. Se comprobo primero que Cerebras ya estaba solo como
opt-in y que los guards de proyecciones pasaban (exit 0), y solo se
modifico lo que seguia roto: los dos contratos de `src/flujo/web/hub.py` (ruta
de registro relativa y `id` sin validar), que eran el mismo defecto ya
corregido en el hub de plataforma pero nunca replicado; y la resolucion de Node,
que informaba `available` para el 18.20.4 de `PATH` mientras el manifiesto
declara `>=20.19.0` y en la maquina hay 20.20.2 y 24.x. Suite completa exit 0;
typecheck web exit 0 con el Node local v24.19.0 y sin aviso de version;
`repo_audit`, `compileall`, `pip check` y `git diff --check` exit 0; hub smoke y
un servidor temporal de `flujo.web.hub` en puertos efimeros, ambos detenidos.
Pipeline medido de punta a punta contra fuentes reales con salidas temporales:
Research `job_id=5` `validation=PASS` con politica `Groq o Gemini`, captura
firecrawl con hash y `model_calls=0`, Curatoria 917 proyectos / 45536 miembros
sobre copia temporal, y Postulacion con tres paquetes Fondart en
`draft_with_evidence_gaps`, `gaps` bloqueantes explicitos y el SHA-256 del
indice SSD identico antes y despues. Se corrigio en este archivo la afirmacion
falsa de que el indice SSD no estaba visible: si lo esta.

2026-08-21 America/Santiago — continuidad posterior a la cuota verificada y
publicada en `7f99a50`: `main == origin/main`, worktree limpio, servicios de
usuario activos, cuatro SQLite integras, tests focalizados exit 0 y segunda
fuente de tenis verificada con ruta `tennis_shot_event_consumer`. El learner
sigue en `abstain` por `holdout_count=0`; no se promovio aprendizaje.

## Current slice: reconstruction to Curatoria/Portfolio Project IR — 2026-08-21

Se agrego `src/flujo/knowledge/reconstruction_adapter.py` y el CLI
`tools/import_project_reconstruction.py`. El adaptador lee un
`mak-project-reconstruction-v1` persistido y su indice SQLite en modo
read-only, convierte solo `project_unit`, `subproject` y `exported_product` a
`mak-project-ir-v1`, deja bibliotecas/recursos compartidos como artefactos o
relaciones y agrega la politica `portfolio=never_auto_publish` y
`postulacion=not_created_by_this_adapter`.

Validacion real: DREFGIRA produjo 5 registros review-only y 467 artefactos
indexados en
`/home/mak/curatoria_inbox/project_reconstruction/2026-08-21/drefgira/project_ir/`;
el router produjo 5 abstenciones por `project_state_requires_evidence`, 0
selecciones y 0 paquetes de postulacion. Con `--db` se guardaron esos 5
registros en el LearningStore existente; no se registraron episodios ni se
promovio una regla. El fingerprint del indice siguio siendo
`d3afb072fe1633125ac20da82aa1d3c7514f763cb8cac28655f19216ac53d8df` y
`PRAGMA integrity_check` devolvio `ok`.

Tests del puente, reconstruccion, Project IR y router: 22 passed. La prueba
de no mutacion del indice comparo sus bytes antes/despues. Cambios de codigo
pendientes de publicar en el commit de este slice: adaptador, CLI, pruebas,
`CAPACIDADES.md`, `docs/MAK_CURRENT_STATE.md` y este handoff.

2026-08-21 America/Santiago — publicacion `90f92be` y sincronizacion del
runtime verificadas. Validado antes del commit en un clon git limpio con el
patch staged aplicado, no en el worktree sucio: pytest completo exit 0,
`flujo verify` exit 0 con hub smoke en puerto efimero, typecheck web exit 0 con
Node 24.18.0, `npm run build:context` exit 0, `gen_archivo_iskvw` exit 0,
`tools/repo_audit.py` exit 0, compileall exit 0, `pip check` exit 0 y
`git diff --check` exit 0. `main` == `origin/main` == `90f92be`; CI, seguridad
y Git topology guard en `success`. Despues de publicar: indice regenerado (783
modulos), Hub de usuario reiniciado y sirviendo el codigo publicado, cinco
familias de GET verificadas read-only, y cinco proveedores auditados con una
sola llamada cada uno. Abiertos confirmados sin fabricar evidencia: Research 4
`license_pending` (`result.license_review = pending` en
`/home/mak/research/jobs/4/verified_result.json`); gate de deep learning
`abstained` con `rows=3`, `independent_holdout=false` y
`training_permitted=false`, y el learner en `abstain` por
`no_independent_holdout` con 9 elegibles y holdout 0; tenis
segunda fuente independiente verificada en
`/home/mak/curatoria_inbox/tennis_sources/2026-08-21/`; XIO diferido en
`workflow_dispatch`;
mirror SSH intacto y fuera de alcance.

2026-08-21 America/Santiago — web/DB cleanup gate and bounded intake verified;
published in commit `69e7fba` and pushed to `origin/main`:
the active web graph has 36 modules, 35 reachable and 0 dead; stale active
references are 0; `rd.db`, `rd_datos.db`, `mak_knowledge.db` and `flujo.db`
pass read-only integrity checks with all declared consumers present. RD live
and standalone projections are equal by SHA-256. The source-index intake used
the physical SSD index, emitted three bounded Fondart packages in `/tmp`, and
left the source and learning DB untouched. The only runtime defect found was
the standalone generator's absolute-output display path; it was fixed and
focused tests passed. The remaining worktree changes are intentionally outside
that commit and must be handled by the next bounded slice.

2026-08-20 America/Santiago — Python structure index and dual debugging slice
verified: `flujo code-index` generated the source-free 781-module index,
consumer resolution and bounded query brief; focused and full pytest passed,
map synchronization passed, compileall and diff check passed. Watsonx/AWS/Azure
retirement and provider
replacement verified: active registries/chains/UI/configuration removed,
Gemini 3.6 Flash works in both LLM and structured platform adapters, Groq,
Ollama and Firecrawl probes pass, Cerebras returns HTTP 402 and is opt-in only,
four exclusive tools and two env snapshots archived, boto3 dependency removed,
compileall exit 0, full pytest exit 0, pip check exit 0 and diff check clean.
Historical WIN/ledgers/results preserved. Official
P versus NP source/formal hashes
recorded without changing `UNTRUSTED`, Research 4 capture and bounded
simulation were checked without biological claims, 59-contract audit refreshed,
source-learning case preserved, 19-lane cross-domain registry validated
locally, tennis MCP parser/shot-event route and fixture episode passed,
Research 4 capture and logo-clean abstention were linked to Project IR, live
status and full pytest rechecked, and the published baseline remains
`7674c49`/`17ccff7`. The cross-domain write set is not yet published.

2026-08-20 America/Santiago — catalog federation slice verified: focused
tests `3 passed`, py_compile exit 0, diff check exit 0; real metadata-only
federation exit 0; 7 sources, 124 tables, 2,075,337 observed rows, 0 copied;
master integrity `ok`, foreign-key issues `[]`, orphan tables/links `0`.
Added source/target contract files; full suite `./.venv/bin/python -m pytest -q`
completed at 100% with exit 0 (warnings only); no source database contents were
rewritten and no commit or push has been made for this slice.

2026-08-20 America/Santiago — operational bridge slice verified: focused
bridge tests `2 passed`, py_compile and diff check exit 0; real refresh exit 0;
6,132 normalized records and 106,895 curation links; source rows copied `0`;
master integrity `ok`, foreign-key issues `[]`; SQL pipeline sample resolved
application package `SCD` to project `SCD`, fund `Fondart` and 12 curation
links. Seven RD event records retain producer/venue/source payloads; non-ISO
date strings remain unnormalized. Full repository suite completed at 100% with
exit 0; only existing deprecation warnings were emitted.

2026-08-20 America/Santiago — foreground pipeline verified: Research read-only
source exposed 5,179 Fondart applications and 14 captures; Curatoria ran on a
temporary SQLite backup and produced 917 projects, 13,121 families and 45,536
members; Postulacion ran against the existing index and emitted
`drefgira-fondart` with status `draft_with_evidence_gaps`; all commands exit 0,
temporary outputs only, no source mutation. Operational closure comes before
the autonomy phase.

2026-08-20 America/Santiago — RD event fixture audit verified read-only: 7
events all retain producer, raw date, venue and flyer/source evidence; 0 were
forced into ISO dates and 0 curation links are orphaned. No source mutation or
new process remained.
