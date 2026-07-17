# Base de datos RD

SQLite consultable con los datos de Reduciendo Dano. Es una **proyeccion
regenerable**, no una fuente de verdad: se construye desde los archivos
canonicos y se puede reconstruir cuando quieras sin desincronizarse.

`data/rd.db` esta gitignored (patron `*.db`): se genera, no se versiona.

## Tablas y sus fuentes

| Tabla | Fuente canonica |
|---|---|
| `reactivos` + `meta` | `projects/cultura/identidad/reactivos.json` |
| `packs` + `inclusiones` | `src/flujo/plano/packs.py` (PACKS) |
| `suplementos` | `projects/piezas_vectoriales/suplementos_rd/01_contenido/contenido_suplementos_rd.json` |
| `productoras` | `data/productoras/*.json` |
| `eventos` | `jobs/**/evento*.json` + `projects/plano/ejemplos/evento*.json` |

`eventos.pack_sugerido` es una pista DERIVADA (match del numero de voluntarios
contra los packs), por eso vive en la DB y no en la fuente.

Nota: la tabla `eventos` incluye jsons de `jobs/` que son gitignored (jobs
reales locales). En un checkout limpio/CI solo aparece el ejemplo TRACKED de
`projects/plano/ejemplos/`, asi que el contenido de esa tabla depende de la
maquina -- es una DB de operador, no un dato versionado.

## Uso

CLI:
```bash
py -m flujo rd-db build                  # (re)construye data/rd.db
py -m flujo rd-db reactivo --familia MDMA
py -m flujo rd-db reactivo --reactivo Marquis
py -m flujo rd-db packs
py -m flujo rd-db eventos
py -m flujo rd-db lookup MDMA         # operador en terreno: reactivos + packs con testeo
```

`lookup` es el JOIN que justifica la DB sobre JSON planos: cruza la colorimetria
(reactivos) con el servicio (packs que incluyen testeo) en una sola vista.

Python:
```python
from flujo.rd import build_rd_db, reactivos_por_familia, packs, eventos, productoras, disclaimer
build_rd_db()
reactivos_por_familia("MDMA")   # las reacciones cruzadas de cada reactivo
```

## Seguridad del dominio

El test de reactivo es **PRESUNTIVO**: indica una familia de sustancias posible,
no la identifica con certeza ni mide pureza. Un color no vuelve segura una
sustancia. El disclaimer canonico viaja en la tabla `meta`
(`reactivos_disclaimer`) y `disclaimer()` lo devuelve: toda salida que muestre un
color deberia poder citarlo.
