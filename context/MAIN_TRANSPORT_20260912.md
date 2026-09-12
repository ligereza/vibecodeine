# MAIN transport classification — 2026-09-12

Responsable: **ROOT-0**.

## Registro vigente

`tools/capabilities.py --no-live --format json` mide actualmente **31 refs**
(locales y `vibecodeine-legacy`), **25 SHAs únicos** y **2 grupos de alias**.
La medición incluye `sync`, commits exclusivos y `git cherry` para separar
parches únicos de parches ya representados. No se eliminó ninguna ref de
VIBECODEINE; sí se podó el remote-tracking ref de un worktree que el remoto ya
había eliminado.

La semántica vigente es:

| ref actual | canonical_ref | lane/kind | destino | disposición |
|---|---|---|---|---|
| `main` | `main` | `integrated/integrated` | `main` | canonical |
| `MAK` | `MAK` | `MAK/operational` | `MAK` | canonical |
| `FLUJO` | `FLUJO` | `FLUJO/operational` | `FLUJO` | canonical |
| `historia`, `DIRECTOR`, `archive/*` | propia/histórica | historical | — | historical_preserve |
| `integration/*`, `main-union-*` | según integración | integration-alias | `main`/lane | alias_or_checkpoint |
| `worktree-*` | lane heredado | worktree | `MAK` | worktree_checkpoint |
| `docs/*`, `feat/*`, `fix/*`, `test/*` | lane heredado | topic | lane | revisión selectiva |
| `dependabot/*` | lane heredado | automated | lane | reevaluar |

`current_ref` se obtiene de Git. `branch_profile.json` aporta semántica
heredada y conserva `branch` por compatibilidad; una topic o worktree puede
heredar `MAK`/`FLUJO` sin convertirse en ese ref. Un `main-union-*` que sólo
hereda `branch=MAK` queda correctamente resuelto como integración `main`; sólo
`canonical_ref` o `lane` explícitos contradictorios generan issue.

## Auditoría de contenido y genealogía

Los cuatro refs canónicos locales/remotos están en paridad `0/0`:

| ref | commit publicado |
|---|---|
| `main` | `6f38729b` |
| `MAK` | `efa6125b` |
| `FLUJO` | `c8b92702` |
| `integration/flujo-canonical-20260911` | `c8b92702` |

El alias de integración FLUJO es el mismo contenido que `FLUJO`. El alias
`main-union-mak-flujo` está 2 commits por encima de `main`: uno es
patch-equivalente al borrado de instrucciones de agente ya representado en
`main`, y el segundo es un commit vacío intermedio; no queda trabajo portable
nuevo que transportar. `worktree-ciclo02-obras` y
`worktree-hub-portafolio-trim` contienen, respectivamente, commits cuya
modificación ya es patch-equivalente en `MAK`; sus refs se conservan como
checkpoints, no como entidades nuevas.

Los topics, worktrees y Dependabot permanecen explícitamente clasificados y
no se fusionaron indiscriminadamente: el inventario muestra sus commits
exclusivos y equivalentes para una futura decisión por contenido. `DIRECTOR` y
`historia` se preservan como historia separada, sin tratarlos como destinos de
deployment. El estado físico no versionado (`run/`, `work/`, `workspaces/`,
`.net/`, `.foundry/`, `.aitk/`, `rollback/`) se conserva localmente porque no
hay evidencia de que sea trabajo portable.

## Consumidores y operación

`tools/branch_contract.py` es la única capa compartida de interpretación y la
consumen `capabilities`, `runtime_preflight` y `release_gate`. El perfil
canónico de cada superficie declara `canonical_ref`, `lane`, `kind` e
`integration_target`; no se añadió `current_ref` al perfil porque esa
propiedad debe medirse en el checkout.

El runtime preflight identifica `/home/mak/flujo` por lane FLUJO aunque el
checkout físico sea el alias de integración, y el probe de Flujo valida la
forma real `python -c ... flujo.web.hub ... run_server`. Resultado live:
**5 ok, 0 warn, 0 unknown, 0 error**. El release gate queda en
`IMPLEMENTATION_COMPLETE_TESTS_DEFERRED`, sin blockers ni unknowns de
topología; sus warnings restantes son higiene, referencias históricas o
suites que el gate no ejecuta.

## Decisiones

`2026-09-12 | ROOT-0 |` mantener `main`/`MAK`/`FLUJO`/`historia` como refs
principales, conectar aliases por identidad y no crear entidades por herencia
de perfil; `git cherry`, paridad remota y los consumidores existentes son la
evidencia reproducible. El trabajo portable exclusivo futuro se decide por
contenido y destino, no por el contador de commits.

Pendientes reales: revisión humana futura de topics/Dependabot que sigan
siendo útiles y ejecución de las suites que el release gate marca como
deferred. No queda una divergencia canónica opaca ni un cambio operativo
pendiente de esta auditoría.
