# Gate de cierre local — 2026-09-02

`RESULTADO_GATE: NOT_READY`

`tools/release_gate.py` juzga **coherencia del estado local del repositorio**.
No corre pytest, así que `READY_TO_PUSH` nunca significaría "los tests están
verdes": significaría "nada bloquea el commit y el plan de push es ejecutable".
Hoy no llega ahí.

## Qué quedó comprobado

**Las cuatro ramas tienen el perfil correcto.** MAK `runtime` con selector
`-m mak` y hub `cultura/mak_plataforma/hub.py`; FLUJO `runtime` con `-m flujo` y
`src/flujo/web/hub.py`; main e historia `kind: historical`, sin selector y sin
hub. Cada selector nombra un marker que el `pyproject.toml` de su propia rama
registra. Ningún archivo declarado falta en ninguna rama.

| Rama | Local | Remoto | ahead/behind |
|---|---|---|---|
| MAK | `a62f9019585f` | `72b0e5e43d7b` | 2 / 0 |
| FLUJO | `ad9ee8811325` | `127f37476d13` | 1 / 0 |
| main | `3d83ed606f9c` | `77333b4c5a94` | 1 / 0 |
| historia | `09f7e7d9059d` | `ab9afa13fb4d` | 1 / 0 |

Las cuatro son fast-forward: `behind=0` y el remoto es ancestro del local. No
hay divergencia.

**Frontera de hubs intacta.** Con `git archive` a un temporal y AST — sin
checkout — ninguno de los dos hubs importa la implementación del otro en
ninguna rama operativa. Sí hay deriva menor: el hub MAK importa
`flujo.diagnostics`, `flujo.knowledge.project_context`, `product_view` y
`contracurator`, que el `shared_consumers` del perfil no declara. El contrato
prohíbe importar el hub contrario, no el paquete, así que eso queda como
warning, no como bloqueador.

**Mapa de carriles legible**, parseado sin ejecutarlo: 5 carriles y 387
entradas (`flujo` 173, `repo_hygiene` 118, `mak` 86, `integration` 10).

**Runtime sano**: `runtime_preflight` corre y devuelve `error=0 unknown=0`, con
las cinco superficies probando su fuente ejecutada.

**Dependencia del adaptador registrada explícitamente**, nunca como OK
silencioso: el `.pth` `/home/mak/.venv/.../__editable__.flujo-0.56.1.pth` sigue
apuntando a `/home/mak/flujo/src`, `flujo_app` resuelve su fuente por esa ruta,
y su puerto declarado 8765 responde en 8766. Las tres son severidad
`dependency`: no cambian los bytes que llevaría un push — el `.pth` vive fuera
del repositorio — pero no desaparecen del reporte.

**Árbol sucio clasificado, nada incluido automáticamente**: 3
`release_candidate`, 1 `session_dossier`, 1 `checkpoint`, 1 `durable_doc`, 1
`operational_code`, 2 `generated_data`, 2 `root_agent_script`. El plan de push
lista rutas explícitas y prohíbe `git add -A`, `git add .` y `git commit -a`.

## Qué bloquea

1. **`uncommitted_work_on_historical_branch`** — HEAD está en `main`, que su
   propio perfil declara `kind: historical`, y arrastra tres archivos
   rastreados modificados: `context/LAST_HANDOFF.md`,
   `cultura/mak_codex/interfaz_codex.py`, `docs/MAK_CURRENT_STATE.md`. Trabajo
   operativo sin commitear sobre una rama que se declara no-desplegable.
   Evidencia: `git branch --show-current`, `git status --porcelain`.
2. **`root_agent_script_present` (x2)** — `inventario_mak.sh` e
   `inventario_externo.sh` en la raíz del repositorio. `CLAUDE.md` prohíbe
   entregar scripts de un solo uso en la raíz, y además no son material de
   release clasificable. Evidencia: `git status --porcelain`.

**Dos bloqueadores que el gate reportó primero y retiré por ser defectos de mis
propias reglas, no del repo:**

- `MAK` "faltaba" `plataforma/hub.py`. El perfil lo declara como
  `hub.compatibility_module`, y `/plataforma/` está excluido en
  `.git/info/exclude` línea 81. Es una proyección de runtime en la caja
  (presente, inodo 1866508, 1044 bytes), no material del repo. Ahora se
  verifica en el filesystem físico y se reporta como info.
- `historia` "faltaba" `tools/test_lane_map.py`. Es un snapshot congelado que
  legítimamente precede a esa herramienta. Exigir tooling actual a una rama
  histórica contradice lo que significa `historical`. Los requisitos base
  quedaron separados: rama operativa exige perfil, pyproject, requirements y
  mapa de carriles; rama histórica exige sólo el perfil que la declara
  histórica.

## Qué no se comprobó porque se difirió

`tests_deferred=true`. Esta fase prohíbe pytest en cualquier forma, colección
incluida, así que la salud de la suite no está medida y el gate no la finge. Ese
es el veredicto que falta y por eso es el primer paso del plan de push. Tampoco
se comprobó: la matriz de CI (sólo la da un PR), ni los bytes en memoria de los
procesos vivos, ni las 89 referencias al adaptador restantes fuera de las cinco
superficies.

## Qué habría que ejecutar después

Hoy no aplica: el veredicto es `NOT_READY`. Primero hay que resolver los tres
bloqueadores — decidir a qué rama va el trabajo modificado y qué se hace con los
dos scripts de la raíz. Cuando el gate devuelva `READY_TO_PUSH`, el plan exacto
que ya emite es:

```bash
python3 -m pytest tests/ -q                              # el veredicto que falta
git switch -c codex/runtime-preflight MAK                # requiere tu aprobación explícita
git add tools/runtime_preflight.py tools/release_gate.py \
        tests/test_runtime_preflight.py \
        context/coordination/inbox/claude/
git commit -m 'feat(runtime): prove executed source per surface'
git push vibecodeine-legacy codex/runtime-preflight
# PR hacia MAK; el veredicto lo da la matriz de CI
```

Excluidos a propósito: `context/git_history_local_20260814_20260901.json`,
`context/python_census_20260901.json`, `inventario_externo.sh`,
`inventario_mak.sh`.

Rama destino MAK porque el preflight y este gate inspeccionan las superficies de
la caja Linux y MAK es su perfil operativo; HEAD está hoy en una rama histórica.

## Escrituras

`tools/release_gate.py` (nuevo, nlink=1, inodo 30305608) y estos dos dossiers.
Nada más. Sin commit, push, reset, checkout, rama, remoto, reinicio de servicio,
`find -L` ni recorrido de FUSE. `writes_outside_allowed_set` vacío.
