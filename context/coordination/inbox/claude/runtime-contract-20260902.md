# Contrato ejecutable de runtime — 2026-09-02

## Problema concreto encontrado

`tools/capabilities.py` responde "¿la superficie declarada existe y está
viva?". No responde "¿el proceso vivo ejecuta la fuente canónica?". Por eso un
HTTP 200 se venía leyendo como salud de runtime: los cinco puertos responden
200 y ninguna herramienta demostraba, con datos del momento, qué archivo está
ejecutando cada servicio.

La medición encontró tres cosas concretas, y una de ellas es la que importa:

1. **La FLUJO App importa su fuente a través del adaptador.** El proceso vivo
   (pid 809778) corre `-m flujo`, así que la ruta del script no aparece en la
   línea de comandos. Sondeando su intérprete: `flujo.web.hub.__file__` =
   `/home/mak/flujo/src/flujo/web/hub.py`. El archivo detrás de eso es
   `/home/mak/.venv/lib/python3.11/site-packages/__editable__.flujo-0.56.1.pth`,
   cuya única línea es `/home/mak/flujo/src`. Resuelve al inodo canónico
   13524904, el mismo que `/home/mak/src/flujo/web/hub.py`, así que hoy no
   ejecuta código histórico. Pero la *declaración* pasa por el adaptador: si
   ese symlink cambia o desaparece, la app cambia de fuente en silencio.

2. **Las tres unidades MAK cargan su cuerpo a través del adaptador.** Los
   fragmentos son symlinks:
   `/home/mak/.config/systemd/user/mak-hub.service ->
   /home/mak/flujo/cultura/mak_plataforma/mak-hub.service`, y lo mismo para
   research y codex. Resuelven a los archivos canónicos del repo, mismo inodo
   y mismo SHA-256, verificado uno por uno.

3. **La FLUJO App declara 8765 y atiende en 8766.** `curl` a 8765 da
   connection refused; 8766 responde 200. No es una falla: es
   `_find_free_port(start_port=8765, max_tries=8)` en
   `src/flujo/web/hub.py:2567`, que autodetecta sólo cuando el puerto pedido es
   exactamente el default. Sondear 8766 a secas habría reportado éxito sin
   notar que el puerto declarado nunca se ligó.

## Cambios reales realizados

**`tools/runtime_preflight.py`** (nuevo, SHA-256
`8243c711e456e1ef2349a2cf6055b357d9a321881ac523856bc82feef5e057bf`). Prueba
cada superficie con cuatro evidencias independientes: la fuente declarada bajo
la raíz física con su SHA-256; el fragmento de unidad y su `ExecStart`
expandido, o un sondeo de importación contra el intérprete vivo para las
superficies manuales; la línea de comandos leída de `/proc/<pid>/cmdline`, que
es lo único que refleja lo que realmente se lanzó; y sólo al final el socket y
el estado HTTP.

Decisiones de contrato dentro del archivo:

- `/home/mak` es la raíz física. `--root /home/mak/flujo` se normaliza a
  `/home/mak` y la sustitución queda registrada en `root_normalized_from`; sin
  eso, `root / "flujo"` inventaba `/home/mak/flujo/flujo`.
- `sys.argv[0]` se conserva sin resolver: `realpath()` colapsa el adaptador, y
  con la ruta resuelta sola una invocación
  `python3 /home/mak/flujo/tools/runtime_preflight.py` se reportaba a sí misma
  como "no vía adaptador". Ahora `invoked_via_adapter=true`.
- `/home/mak/flujo` se reporta siempre como `compatibility_adapter`, con
  `is_symlink`, `own_git_dir`, `is_git_worktree`, symlinks a hermanos,
  recursivos y rotos medidos, nunca como repositorio ni raíz independiente.
- Git anota; no decide. Los perfiles de rama se leen con `git show
  <rama>:branch_profile.json`, sin checkout.
- No falla abierto: fuente ausente, fuente ejecutada distinta de la declarada,
  fuente modificada después del arranque del proceso, `ExecStart` fuera de la
  raíz física o dentro de `_archive`/`WIN`, y listener abierto cuya fuente no
  se pudo verificar, todos son `error`. Unidad ausente es `unknown`, salvo
  superficie manual declarada.
- Un 200 no cierra nada: `listener_source_unverified` se dispara cuando el
  puerto responde y la fuente no quedó probada.

**Dos defectos de modelado propios, corregidos antes de cerrar.** La primera
corrida del preflight inventó hallazgos, y eso es exactamente lo que esta
herramienta existe para evitar:

- Comparaba el puerto de *toda* superficie MAK contra el único `hub.default_port`
  del perfil de rama, convirtiendo Research (8890) y Codex (8891) en deriva
  falsa contra 8900. Ahora `_declared_port_from_branch` compara sólo cuando la
  fuente declarada de la superficie ES el `hub.module` de esa rama.
- Declaraba `cultura/mak_research/research_lib.py` como fuente de Ollama.
  Ollama es un binario del sistema: eso dejaba el ejecutable real sin verificar
  y hacía que una edición MAK-side pareciera deriva del demonio. Ahora existe
  `source_kind="native_binary"`, la fuente declarada es `/usr/local/bin/ollama`
  verificada contra `argv[0]`, y las librerías del repo pasaron a
  `consumer_sources`.

**Las tres unidades MAK quedaron sin cambios, a propósito.** Sus cuerpos ya
nombran `%h/cultura/...`:

| Unidad | ExecStart literal |
|---|---|
| `cultura/mak_plataforma/mak-hub.service` | `%h/plataforma/.venv/bin/python %h/cultura/mak_plataforma/hub.py` |
| `cultura/mak_research/interfaz.service` | `%h/research/.venv/bin/python %h/cultura/mak_research/interfaz.py` |
| `cultura/mak_codex/mak-codex.service` | `/usr/bin/python3 %h/cultura/mak_codex/interfaz_codex.py` |

Cero referencias `%h/flujo` dentro de los tres archivos. La indirección por
adaptador está en los symlinks de `.config/systemd/user/` y en el `.pth` del
venv, ambos fuera del conjunto de escritura permitido. Cambiar rutas dentro de
las unidades habría sido estética, no corrección. Ningún servicio fue
reiniciado, porque ninguna unidad fue modificada.

Regla de hardlink: `stat -c '%h %i'` corrido antes de cada escritura. Los tres
archivos escritos son nuevos y quedaron con `nlink=1`
(`tools/runtime_preflight.py` inodo 30277903, el JSON inodo 30305599, el
Markdown inodo 30305605). Los tres
`.service` inspeccionados también son `nlink=1`, así que ni siquiera habría
hecho falta el procedimiento de temporal + reemplazo atómico; no se editó
ninguno en sitio.

## Fuente declarada versus fuente ejecutada

| Superficie | Declarada | Ejecutada (evidencia) | Coincide | Adaptador |
|---|---|---|---|---|
| MAK Hub | `/home/mak/cultura/mak_plataforma/hub.py` | `/proc/854934/cmdline`: `…/plataforma/.venv/bin/python /home/mak/cultura/mak_plataforma/hub.py` | sí | fragmento de unidad |
| Research | `/home/mak/cultura/mak_research/interfaz.py` | `/proc/854932/cmdline`: `…/research/.venv/bin/python /home/mak/cultura/mak_research/interfaz.py` | sí | fragmento de unidad |
| Codex bridge | `/home/mak/cultura/mak_codex/interfaz_codex.py` | `/proc/854933/cmdline`: `/usr/bin/python3 /home/mak/cultura/mak_codex/interfaz_codex.py` | sí | fragmento de unidad |
| FLUJO App | `/home/mak/src/flujo/web/hub.py` | sondeo de importación: `/home/mak/flujo/src/flujo/web/hub.py` -> inodo 13524904 | sí | `.pth` del venv |
| Ollama | `/usr/local/bin/ollama` | `/proc/2822/cmdline`: `/usr/local/bin/ollama serve` | sí | no |

SHA-256 de cada fuente (16 primeros): hub `3a3fea172840f62f`, interfaz
`ad7aa992730bf0a3`, codex `62881502660dc4d3`, flujo hub `3f070a7a6e9056d1`,
ollama `e010ce570cfa0433`. Ninguna resuelve dentro de `WIN` ni de `_archive`.

`cultura/mak_codex/interfaz_codex.py` está modificado en el árbol de trabajo
(`git status` ` M`), con mtime 03:31:38 contra un arranque de proceso a
04:13:56: el proceso arrancó después de la edición, así que los bytes que corre
son los del disco. Si la relación se invirtiera, el preflight lo marcaría
`error/source_changed_after_start`.

## Puertos declarados versus efectivos

| Superficie | Declarado | Origen de la declaración | Abierto | Efectivo | Fallback |
|---|---|---|---|---|---|
| MAK Hub | 8900 | `branch_profile.json` rama MAK, `hub.default_port` | sí | 8900 | — |
| Research | 8890 | registro del preflight | sí | 8890 | — |
| Codex bridge | 8891 | registro del preflight | sí | 8891 | — |
| FLUJO App | 8765 | `branch_profile.json` rama FLUJO, `hub.default_port` | **no** | **8766** | **8766** |
| Ollama | 11434 | registro del preflight | sí | 11434 | — |

## Medición ANTES y DESPUÉS

ANTES: rama `main`, `branch_profile.json` local con `kind: historical`,
`default_test_selector: null`, `hub: null`; tres archivos modificados y cuatro
sin seguimiento. Las tres unidades user activas desde 04:13:56 con
`ActiveState=active`; `ollama.service` activa, MainPID 2822. `ss -ltnp`:
8890/854932, 8891/854933, 8900/854934, 8766/809778, 11434 sin dueño visible
para un lector no root, 8765 sin listener. HTTP en las rutas declaradas:
8900 `/health` 200, 8900 `/api/status` 200, 8890 `/` 200, 8891 `/` 200,
8765 `/` connection refused, 8766 `/` 200, 11434 `/api/version` 200, 11434
`/api/tags` 200. Referencias a `/home/mak/flujo` medidas en los directorios
operativos del repo: 92 en total, 17 de clase fuente-de-código, 3 symlinks de
unidad, 1 `.pth`, 0 lanzadores de nivel 1, 0 dentro de los tres cuerpos de
unidad.

DESPUÉS: mismos procesos, mismos puertos, mismos hashes; no se reinició ni se
detuvo nada. `python3 tools/runtime_preflight.py --check` sale 0 con
`ok=1 ok_via_adapter=3 warn=1 unknown=0 error=0`.
`--check --check-adapter` sale 3, que es la escalada opcional por indirección.
`--root /home/mak/flujo` normaliza a `/home/mak` y lo declara.
`python3 /home/mak/flujo/tools/runtime_preflight.py` reporta
`invoked_via_adapter=true` con `physical_root=/home/mak`.

Prueba negativa, porque un detector que sólo puede devolver 0 no sirve de nada:
con `--root` apuntando a un directorio vacío sale **1** por `source_missing`;
con `--root` apuntando a un árbol señuelo que replica las rutas relativas sale
**1** por `exec_start_outside_root` más `listener_source_unverified` en las
cuatro superficies Python.

## Pruebas

`git diff --check` → 0.
`python3 -m py_compile tools/runtime_preflight.py` → 0.
`python3 tools/runtime_preflight.py --check` → 0.

Suite focal, sin editar ningún test:

```
/home/mak/.venv/bin/python -m pytest tests/test_operational_entrypoints.py \
  tests/test_mak_hub_salud.py tests/test_mak_research_interfaz_http.py \
  tests/test_mak_codex_nodos.py -q
exit=0   88 puntos de progreso, 0 fallos, 0 errores
```

Cero fallos, así que no hay nada que atribuir al cambio ni nada preexistente
que reportar. Dos aclaraciones honestas: la configuración `-q` de este repo no
emite línea final de conteos, así que las 88 se leyeron del flujo de puntos y
se cruzaron contra 88 funciones `test_` declaradas en los cuatro archivos; y la
suite focal se ejecutó tres veces, no una — las dos primeras capturas
perdieron la cola de salida y la tercera fue la que registró el código de
salida. No hubo ediciones entre corridas.

## Archivos no tocados

`context/LAST_HANDOFF.md`, `CAPACIDADES.md`, `CAPACIDADES_MAK.md`,
`branch_profile.json`, los cuatro tests focales y cualquier otro test, las tres
unidades `.service` (inspeccionadas, sin cambios), `.config/systemd/user/*`,
`/etc/systemd/system/ollama.service` (sólo lectura), el `.pth` del venv, los
symlinks de compatibilidad, `/home/mak/flujo` como directorio, `_archive`,
`WIN`, y toda base de datos. No hubo commit, push, reset, checkout, rama,
remoto, proceso muerto ni servicio reiniciado. `writes_outside_allowed_set`
está vacío.

## Unknowns

- **Bytes en memoria.** Ningún método de sólo lectura aquí prueba qué bytes ya
  cargó un intérprete vivo. El preflight prueba la fuente declarada, el
  `ExecStart`, la línea de comandos y el mtime de la fuente contra el arranque
  del proceso, y falla con `source_changed_after_start`; no puede inspeccionar
  los objetos de código cargados.
- **Alcance del sondeo de importación.** Para `flujo_app` la ruta del módulo
  sale de correr el mismo intérprete otra vez, así que refleja su `sys.path`
  actual, no el que usó el proceso vivo a las 02:17:14. El `.pth` queda
  registrado como la evidencia de archivo detrás de ese sondeo.
- **Salida 2 no ejercitada.** `unit_missing` mapea a `unknown` y a salida 2.
  `systemctl` resuelve unidades por nombre sin importar `--root`, así que esa
  rama no se pudo probar sin retirar una unidad, que está fuera del conjunto de
  escritura. Hoy es sólo camino de código.
- **Dueño del listener de Ollama.** `ss` como usuario no root no muestra el pid
  que sostiene 11434. La superficie se prueba por `MainPID=2822` y
  `/proc/2822/cmdline`, no por propiedad del socket.
- **La indirección real está fuera del conjunto de escritura.** Los tres
  symlinks de fragmento en `/home/mak/.config/systemd/user/` y
  `/home/mak/.venv/lib/python3.11/site-packages/__editable__.flujo-0.56.1.pth`
  son las referencias `%h/flujo` de clase fuente-de-código que quedan. Se
  reportan, no se reparan.
- **`tools/mak_ops/check_mak_mirror.py`** arma rutas
  `/home/mak/flujo/cultura/...` en las líneas 97-103 y 209, y
  `tests/test_operational_entrypoints.py` fija su mapa `UNIT_FILES` de forma
  exacta. Ambos archivos están fuera del conjunto de escritura; tocar
  cualquiera necesita su propia tarea.
- **Rama contra checkout.** El checkout físico está en `main`, cuyo perfil se
  autodeclara `kind: historical` sin selector ni hub, mientras las superficies
  medidas pertenecen a los perfiles MAK y FLUJO. El preflight anota cada
  superficie con la rama del checkout y lee el perfil de la rama dueña con
  `git show`; no decide qué rama debería estar activa.

No se declara "todo sano". Cuatro de las cinco superficies prueban su fuente
ejecutada sólo porque el adaptador resuelve hoy al inodo canónico, y esa
resolución no está protegida por ningún test ni por ninguna unidad.
