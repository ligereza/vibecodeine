# MAIN transport classification — 2026-09-12

Responsable: **ROOT-0**.

## Registro vigente

`tools/capabilities.py --no-live --format json` mide actualmente **39 refs**
(16 heads, 15 remote-tracking, 4 tags ligeros y 4 tags anotados), **33 objetos
SHA** y **2 grupos de alias de heads/remotes**. La medición incluye `sync`,
commits exclusivos, `git cherry`, object SHA y peeled commit SHA; un tag
anotado no se agrupa como alias sólo por apuntar al mismo commit. No se
eliminó, movió ni recreó ningún branch o tag; sólo se podó un remote-tracking
ref cuyo worktree ya había sido eliminado en el remoto.

La semántica vigente es:

| ref actual | canonical_ref | lane/kind | destino | disposición |
|---|---|---|---|---|
| `main` | `main` | `integrated/integrated` | `main` | canonical |
| `MAK` | `MAK` | `MAK/operational` | `main` | canonical |
| `FLUJO` | `FLUJO` | `FLUJO/operational` | `main` | canonical |
| `historia`, `DIRECTOR`, `archive/*` | propia/histórica | historical | — | historical_preserve |
| `integration/*`, `main-union-*` | según integración | integration-alias | `main`/lane | alias_or_checkpoint |
| `worktree-*` | lane heredado | worktree | `MAK` | worktree_checkpoint |
| `docs/*`, `feat/*`, `fix/*`, `test/*` | lane heredado | topic | lane | revisión selectiva |
| `dependabot/*` | lane heredado | automated | lane | reevaluar |

`current_ref` se obtiene de Git. `branch_profile.json` aporta semántica
heredada y conserva `branch` por compatibilidad. `comparison_ref` es la base
inmediata de sincronización (`MAK` para MAK, `FLUJO` para FLUJO); entonces
`integration_target` es el destino final (`main` para ambos). Una topic puede
heredar `MAK`/`FLUJO` sin convertirse en ese ref. Un `main-union-*` que sólo
hereda `branch=MAK` queda correctamente resuelto como integración `main`; sólo
`canonical_ref` o `lane` explícitos contradictorios generan issue.

## Auditoría de contenido y genealogía

Los cuatro refs canónicos locales/remotos están en paridad `0/0`; la siguiente
es la medición de refs canónicos antes de la reconciliación CI
(`audit_base_sha=f1d1d512` para `main`):

| ref | commit publicado |
|---|---|
| `main` | `audit_base_sha=f1d1d512` |
| `MAK` | `ef85f6be` |
| `FLUJO` | `87c849fd` |
| `integration/flujo-canonical-20260911` | `87c849fd` |

El alias de integración FLUJO es el mismo contenido que `FLUJO`. En la base de
auditoría `f1d1d512`, el alias `main-union-mak-flujo` estaba **2 commits
exclusivos / 31 commits detrás** de `main`: uno es
patch-equivalente al borrado de instrucciones de agente ya representado en
`main`, y el segundo es un commit vacío intermedio; no queda trabajo portable
nuevo que transportar. Los commits de ROOT-0 posteriores a esa base son
reconciliación CI y registro/gate; no alteran esa interpretación. El inventario
debe volver a medirse para cifras vivas; esta relación 2/31
queda fijada sólo contra la base `f1d1d512`.
`worktree-ciclo02-obras` y
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
`integration_target`; la capa expone además `comparison_ref`. No se añadió
`current_ref` al perfil porque esa propiedad debe medirse en el checkout.

`historia` y `archive/house-history` se modelan como historical, sin profile
obligatorio, sin comparación y sin destino de deployment. El tag anotado
`archive/house-history` conserva su object SHA
`4b477309565405f9c9424b9f4dda8b96aba574d9` y su peeled commit SHA
`b9f9a472deaeee6002a96fc8236d75b06bfe24c4`.

El runtime preflight identifica `/home/mak/flujo` por lane FLUJO aunque el
checkout físico sea el alias de integración, y el probe de Flujo valida la
forma real `python -c ... flujo.web.hub ... run_server`. Resultado live:
**5 ok, 0 warn, 0 unknown, 0 error**. El release gate queda en
`IMPLEMENTATION_COMPLETE_TESTS_DEFERRED`, sin blockers ni unknowns de
topología; sus warnings restantes son higiene, referencias históricas o
suites que el gate no ejecuta.

El workflow remoto `CI integrated main` correspondiente al HEAD publicado al
cierre de esta reconciliación terminó verde: **5152 passed, 110 skipped, 9
deselected**. El run reproducible queda enlazado por el historial de Actions
del commit de cierre, no por un SHA escrito dentro de este mismo registro.

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
