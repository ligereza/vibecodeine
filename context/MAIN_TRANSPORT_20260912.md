# MAIN transport classification — 2026-09-12

Responsable: **ROOT-0**.

## Resultado

`main` local (`0be7eba97eff`) ya no se trata como una caja negra frente a
`vibecodeine-legacy/main` (`5187d354`). El rango contiene 204 commits, pero no
204 unidades pendientes de transporte:

| clasificación | cantidad | decisión |
| --- | ---: | --- |
| alcanzable desde una ref publicada o de integración | 188 | efecto ya representado; no duplicar |
| merge de unión MAK/FLUJO | 3 | conservar como genealogía de integración |
| patch-equivalente en otra rama | 1 | `d62a97e2` ya está representado por `23a413e7`; no duplicar |
| único frente a esas refs | 12 | revisar destino explícito abajo |

Los conteos se solapan entre refs: por ejemplo, 146 commits son alcanzables
desde `vibecodeine-legacy/MAK`, 38 desde `vibecodeine-legacy/FLUJO` y 186 desde
`vibecodeine-legacy/main-union-mak-flujo`. No se suman como unidades distintas.

## Únicos y destino

| commits | contenido | destino actual |
| --- | --- | --- |
| `12abf3c9`, `8ff6427d`, `a0371852` | corrección de rutas MAK, backup opcional y guardia RD | ya integrados en la rama local `MAK` |
| `6050725f`, `204d8d30`, `780e29ef`, `452cef90`, `0be7eba9` | puente XIO con endpoint explícito, modos cron y medición read-only de transporte/mounts | código portable de MAK; se conserva en esta integración `main` como destino coherente |
| `06a85e35`, `a94be576`, `690a7db0` | release gate, verificación y decisión documental de `main` | integración `main`; no pertenece a FLUJO ni a estado físico |
| `fb897abb` | vista de portafolio que cruza Hub MAK, ISKVW y conocimiento FLUJO | integración transversal `main`; no se duplica en una rama secundaria |

La única divergencia restante de representación es de publicación de refs, no
de contenido: `MAK` local está 27 commits por delante de
`vibecodeine-legacy/MAK`, y `integration/flujo-canonical-20260911` está 1
commit por delante de su remoto. El envío de esos refs es una operación
posterior separada; no se hace rebase ni se fuerza ningún historial.

## Revalidación remota posterior

Entre la primera medición y la publicación, el remoto `main` avanzó con
`b5452cbb` y `7f3b97dc`, ambos orientados a retirar instrucciones de agente.
Se fusionaron como segundo padre en `7b1cae65`; `AGENTS.md` quedó eliminado,
coincidiendo con el borrado local preexistente, y `main` quedó publicado en
fast-forward con divergencia `0/0`.

El checkpoint de FLUJO `7c1ff0e7` quedó publicado en
`integration/flujo-canonical-20260911`. La rama remota `MAK` había avanzado de
forma independiente a `b7267021` con dos commits de limpieza. La comparación
3-way encontró sólo el borrado común de `AGENTS.md`; el merge no-forzado
`6a3da7a8` conservó los 27 commits locales, incorporó los 2 remotos y quedó
publicado en `MAK`.

## Estado físico/local

No se encontró un commit del rango cuyo conjunto de rutas sea exclusivamente
`run/`, `work/`, `workspaces/`, `.net/`, `.foundry/`, `.aitk/` o `rollback/`.
Esos directorios siguen siendo estado local no versionado y se preservan. La
comparación de contenido no autoriza convertirlos en commits portables.

## Criterio de continuidad

`main` se conserva como punto de integración general. `MAK` y `FLUJO` siguen
siendo las superficies de responsabilidad de sus componentes; un cambio ya
contenido por `main-union-mak-flujo`, o con patch-id equivalente, no vuelve a
entrar por cherry-pick. ROOT-0 debe revisar sólo los nueve commits de código
portable aún no reflejados en las refs remotas principales antes de una futura
publicación.
