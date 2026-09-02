# Desacople del runtime y blindaje del preflight — 2026-09-02

Continúa `runtime-contract-20260902`. No se repitió la auditoría general.

## Baseline

`git status --short` con tres modificados y cinco sin seguimiento, entre ellos
`tools/runtime_preflight.py` y `context/coordination/` de la fase anterior.

Los tres symlinks systemd de usuario, **los tres pasando por el adaptador**:

| Symlink | `readlink` | `nlink inode` | SHA-256 del destino resuelto |
|---|---|---|---|
| `mak-hub.service` | `/home/mak/flujo/cultura/mak_plataforma/mak-hub.service` | `1 655789` | `fbb5292a38bfc0be…` |
| `mak-research.service` | `/home/mak/flujo/cultura/mak_research/interfaz.service` | `1 655791` | `c0edad00de66c264…` |
| `mak-codex.service` | `/home/mak/flujo/cultura/mak_codex/mak-codex.service` | `1 655792` | `aa689e31176ba48c…` |

`systemctl --user show`: los tres `active/running`, fragmento en
`/home/mak/.config/systemd/user/…`, `MainPID` 854934 / 854932 / 854933,
arrancados a las 04:13:56. `ExecStart` expandido apuntando ya a
`%h/cultura/...`, sin `%h/flujo` dentro de ningún cuerpo.

Puertos y HTTP: 8900 `/health` 200 (pid 854934), 8890 `/` 200 (pid 854932),
8891 `/` 200 (pid 854933).

Preflight antes: `ok=1 ok_via_adapter=3 warn=1 unknown=0 error=0`, con
`unit_fragment_via_adapter` en las tres superficies MAK y
`exec_start_via_adapter` + `port_fallback` en la FLUJO App.

Ningún symlink apuntaba ya directo, así que los tres calificaron para el
reemplazo. Ninguno quedó `unchanged`.

## Symlinks reemplazados

Procedimiento aplicado a los tres, en orden, uno por uno: `stat`; `ln -s` al
destino directo como `.<unidad>.new` en el mismo directorio; verificación de
`readlink` y `readlink -f`; comparación de SHA-256 del destino nuevo contra el
viejo; `mv -T` sobre el symlink (`rename(2)`, atómico); el archivo destino nunca
se borró.

| Symlink | Target antes | Target después | SHA antes | SHA después | Idénticos |
|---|---|---|---|---|---|
| `mak-hub.service` | `…/flujo/cultura/mak_plataforma/mak-hub.service` | `/home/mak/cultura/mak_plataforma/mak-hub.service` | `fbb5292a38bfc0be…` | `fbb5292a38bfc0be…` | sí |
| `mak-research.service` | `…/flujo/cultura/mak_research/interfaz.service` | `/home/mak/cultura/mak_research/interfaz.service` | `c0edad00de66c264…` | `c0edad00de66c264…` | sí |
| `mak-codex.service` | `…/flujo/cultura/mak_codex/mak-codex.service` | `/home/mak/cultura/mak_codex/mak-codex.service` | `aa689e31176ba48c…` | `aa689e31176ba48c…` | sí |

Los inodos del symlink cambiaron (655789→655431, 655791→655495,
655792→655498), que es lo esperado: `mv -T` crea una entrada nueva. Los
archivos destino conservan sus inodos originales intactos: 30308886 / 30308810
/ 30308850, con 389 / 633 / 451 bytes. No quedaron temporales `.new` en el
directorio.

**Los tres cuerpos `.service` no se tocaron**, verificado por SHA-256 después
del cambio: `fbb5292a…`, `c0edad00…`, `aa689e31…`, idénticos al baseline.

## daemon-reload y salud

```
systemctl --user daemon-reload                                  exit 0
systemctl --user is-active mak-hub mak-research mak-codex        exit 0 -> active active active
```

**Ningún servicio se reinició**, y hay prueba: los `MainPID` siguen siendo
854934, 854932 y 854933, con el mismo `start_time` 04:13:56. `daemon-reload`
sólo releyó los fragmentos, y el contenido cargado es byte-idéntico porque el
symlink nuevo apunta al mismo archivo.

| Unidad | Activa antes | Activa después | MainPID antes | MainPID después | HTTP antes | HTTP después |
|---|---|---|---|---|---|---|
| `mak-hub` | active | active | 854934 | 854934 | 8900 `/health` 200 | 8900 `/health` 200 |
| `mak-research` | active | active | 854932 | 854932 | 8890 `/` 200 | 8890 `/` 200 |
| `mak-codex` | active | active | 854933 | 854933 | 8891 `/` 200 | 8891 `/` 200 |

## Blindaje del preflight

`tools/runtime_preflight.py`, SHA-256 `8243c711e456e1ef…` →
`96f9c8d9130e37c2…`.

**El cambio que importa: contar condiciones aparte del estado.** Un solo
estado por superficie esconde una segunda condición debajo. La FLUJO App
arrastra dos cosas a la vez — el fallback de puerto y la dependencia del
adaptador — y con un `max()` sólo se veía `warn`. Tras arreglar los tres
symlinks eso habría sido peligroso: el contador de estados ahora dice
`ok_via_adapter=0` y sonaría a que la dependencia del adaptador desapareció,
cuando la FLUJO App sigue importando por el `.pth` del venv. Por eso hay dos
filas:

```
- summary (worst status per surface): ok=4 ok_via_adapter=0 warn=1 unknown=0 error=0
- conditions (surfaces carrying each, independent): error=0 unknown=0 warn=1 adapter_dependency=1
```

Y cada superficie declara lo que arrastra:
`[WARN] FLUJO App (flujo_app, manual_process) carries=warn,adapter_dependency`.

Tabla de códigos, uno por condición, precedencia
`error > unknown > warn > adapter_dependency`:

| Condición | modo normal | `--strict` | `--check-adapter` |
|---|---|---|---|
| `error` | **1** | **1** | **1** |
| `unknown` | **2** | **2** | **2** |
| `warn` | 0 | **3** | 0 |
| `adapter_dependency` | 0 | **4** | **4** |
| limpio | 0 | 0 | 0 |

El modo normal mantiene su contrato anterior: un warning operativo no bloquea a
quien sólo pregunta si el runtime es sano. `--check-adapter` sigue siendo
independiente de `--strict`: escala la dependencia del adaptador con o sin él, y
`--strict` llega al 4 sin necesitarlo.

**Un cambio incompatible, deliberado:** `--check-adapter` devolvía 3 en la fase
anterior y ahora devuelve 4. Con la tabla nueva el 3 pasó a significar
"warning", así que dejarlo en 3 habría hecho ambiguo ese código. Ahora el 3
siempre es warning y el 4 siempre es dependencia del adaptador, sin importar qué
flag lo produjo. `--strict` y `--check-adapter` además implican el chequeo;
pasar `--check` explícito sigue funcionando igual.

El fallback 8765→8766 **no** se convirtió en éxito silencioso: sigue emitiendo
`warn/port_fallback`, es lo que hace que `--strict` devuelva 3 hoy, y hay un
test que lo fija.

## Tests nuevos

`tests/test_runtime_preflight.py`, 14 pruebas, SHA-256 `276dcfd629169cdf…`.
Cubren los ocho casos pedidos:

| Caso pedido | Prueba |
|---|---|
| raíz vacía ⇒ error | `test_empty_root_is_an_error_not_a_silent_pass` |
| árbol señuelo ⇒ error | `test_decoy_tree_is_an_error_because_the_live_process_runs_elsewhere` |
| raíz `/home/mak/flujo` ⇒ normalización registrada | `test_adapter_root_is_normalized_and_the_substitution_is_recorded` |
| `--strict` distingue warning de éxito | `test_strict_distinguishes_warning_from_success`, `test_one_exit_code_per_condition_worst_first`, `test_check_adapter_is_independent_of_strict` |
| fuente nativa de Ollama por `argv[0]` | `test_native_binary_surface_is_verified_by_argv0`, `test_ollama_surface_declares_a_binary_and_keeps_repo_libs_as_consumers` |
| fuente ejecutada distinta ⇒ error | `test_executed_source_different_from_declared_is_an_error`, `test_source_inside_frozen_evidence_is_an_error` |
| `ok_via_adapter` con el estado correcto | `test_source_reached_through_the_adapter_is_flagged_not_hidden`, `test_adapter_is_never_reported_as_a_repository_or_a_worktree` |
| el reporte no altera archivos | `test_the_report_alters_no_file_it_inspects` |

Más `test_port_fallback_never_becomes_a_silent_success`.

Todo lo que puede ser hermético lo es: las pruebas del adaptador construyen su
propia raíz temporal con un directorio `flujo` de symlinks a hermanos, y la del
binario nativo usa un archivo temporal, así que no dependen de que los servicios
MAK estén arriba. Las dos que llaman a `build_report` sobre una raíz temporal
afirman sólo el código de salida, nunca un código de hallazgo concreto, porque
cuál error salta primero depende de qué esté corriendo en la caja.

Un defecto propio corregido antes de cerrar: el cargador con
`importlib.util.module_from_spec` hacía que `@dataclass` fallara con
`AttributeError: 'NoneType' object has no attribute '__dict__'`. El módulo se
registra en `sys.modules` antes de `exec_module`; el arreglo está sólo en el
cargador del test.

## Pruebas

```
systemctl --user daemon-reload                                   exit 0
systemctl --user is-active (3 unidades)                          exit 0  active x3
curl 8900/health, 8890/, 8891/                                   200, 200, 200
python3 -m py_compile tools/runtime_preflight.py                 exit 0
pytest tests/test_runtime_preflight.py -q                        exit 0  14 pasan
pytest (4 focales existentes) -q                                 exit 0  88 pasan
python3 tools/runtime_preflight.py --check                       exit 0
python3 tools/runtime_preflight.py --check --strict              exit 3
python3 tools/runtime_preflight.py --check --check-adapter       exit 4
git diff --check                                                 exit 0
```

Los cuatro focales corrieron **una vez** en esta fase: 88 puntos, sin cadenas
`fail` ni `error` en la salida capturada, exit 0. Ningún test existente fue
editado. No se ejecutó la suite completa.

## Diferencia entre modo normal y estricto, hoy

Normal devuelve 0: no hay error ni unknown, el runtime es sano y las cinco
superficies prueban su fuente ejecutada. Estricto devuelve 3 por el fallback
8765→8766 de la FLUJO App. `--check-adapter` devuelve 4 porque esa misma
superficie sigue resolviendo su fuente por el adaptador a través del `.pth` del
venv. Los tres números describen tres cosas distintas y ninguno tapa a otro.

## Unknowns

- **La última referencia por adaptador sigue en pie.**
  `/home/mak/.venv/lib/python3.11/site-packages/__editable__.flujo-0.56.1.pth`
  todavía dice `/home/mak/flujo/src`. Es la única referencia de clase
  fuente-de-código que queda entre las cinco superficies, y no está en el
  conjunto de escritura de esta fase; por eso `--check-adapter` sigue en 4, y
  eso es correcto, no un residuo.
- **El código 2 sigue sin ejercitarse en vivo.** `unknown` está cubierto por un
  test unitario sobre `exit_code`, pero ninguna corrida real lo produjo:
  `systemctl` resuelve unidades por nombre sin importar `--root`, y retirar una
  unidad está fuera del conjunto de escritura.
- **Bytes en memoria**, sin cambio respecto de la fase anterior: se prueba la
  fuente declarada, el `ExecStart`, la línea de comandos y el mtime contra el
  arranque; no los objetos de código ya cargados.
- **Alcance de `daemon-reload`.** Releyó los fragmentos y el contenido cargado
  es byte-idéntico, así que no hizo falta reinicio y no se hizo ninguno. Si una
  futura edición de un cuerpo de unidad necesita reinicio, eso no se decide
  aquí.
- **Las otras referencias al adaptador siguen ahí.** De las 92 medidas en la
  fase anterior (17 de clase fuente-de-código) se corrigieron 3.
  `tools/mak_ops/check_mak_mirror.py` y el test que fija su mapa `UNIT_FILES`
  siguen fuera de todo conjunto de escritura.

## Escrituras

Sólo estos seis caminos, los seis permitidos:

- `/home/mak/.config/systemd/user/mak-hub.service` (symlink reemplazado)
- `/home/mak/.config/systemd/user/mak-research.service` (symlink reemplazado)
- `/home/mak/.config/systemd/user/mak-codex.service` (symlink reemplazado)
- `tools/runtime_preflight.py`
- `tests/test_runtime_preflight.py`
- estos dos dossiers

No hubo commit, push, reset, checkout, rama, remoto, reinicio de servicio,
proceso muerto ni archivo borrado. No se convirtió `/home/mak/flujo` en
worktree. No se tocaron cuerpos `.service`, hubs, código de negocio, tests
existentes, handoffs, `CAPACIDADES*`, `branch_profile.json`, `_archive`, `WIN`
ni ninguna base de datos. `writes_outside_allowed_set` está vacío.

`status: complete`
