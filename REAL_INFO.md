# REAL_INFO.md — información vigente y fácil de encontrar

Actualizado a partir de `main` observado el **2026-09-20** en el commit `974bfccdbb3df3bc1b90fa98d14b55191d4bac1d`.

Este archivo contiene el **modelo mental vigente** del repositorio. No intenta congelar procesos, servicios, conteos ni resultados que pueden cambiar; esos se miden en el momento.

## 1. Qué es este repositorio

`ligereza/vibecodeine` es la base Git integrada del sistema creativo/operativo. El perfil versionado de la rama está en `branch_profile.json`.

En `main`:

- tipo de rama: `integrated`;
- rol: baseline integrado MAK + FLUJO para validación y composición de release;
- MAK y FLUJO conviven en el mismo árbol, pero **no son el mismo runtime**;
- el paquete Python se declara en `pyproject.toml` como `mak-box` y requiere Python >= 3.10.

## 2. Las dos superficies principales

| Área | Fuente principal | Superficie |
|---|---|---|
| MAK | `cultura/mak_*/` y `cultura/mak_plataforma/hub.py` | Hub MAK, puerto por defecto 8900 |
| FLUJO | `src/flujo/` y `src/flujo/web/hub.py` | workflow/CLI/App portátil, puerto por defecto 8765 |

`main` valida la composición de ambas. Las capacidades específicas de cada carril pueden consultarse en `CAPACIDADES_MAK.md` y `CAPACIDADES_FLUJO.md`, pero esos inventarios **no son lectura inicial ni autoridad de estado en vivo**.

## 3. Mapa rápido del árbol

- `cultura/mak_*`: departamentos y lógica ligada a MAK.
- `src/flujo/`: motor y CLI FLUJO.
- `web/`: frontend React/Vite y paneles.
- `iskvw/`: archivo/curatoría/editor y superficies relacionadas con la práctica pública.
- `data/`: fuentes y proyecciones de datos con autoridades distintas.
- `projects/`: proyectos y productos concretos.
- `xio/`: material XIO presente en el árbol integrado actual; no deduzcas su autoridad runtime desde versiones históricas que lo declaraban extraído o retirado.
- `docs/` y `context/`: documentación de dominio, evidencia y legado. No son una cola de trabajo.
- `context-history/`: historia explícita. Nunca es bootstrap.

## 4. Nombres y fronteras que ya están resueltos

### MAK
MAK es el sistema/máquina Linux y su capa de departamentos. Cuando se hable de una rama o checkout se debe nombrar explícitamente “rama MAK” o “checkout MAK”; `MAK` a secas no significa una rama.

### FLUJO
FLUJO es el motor/workflow portátil, con CLI y App propios. En la base integrada sigue siendo una frontera separada de MAK.

### IRIS
IRIS nombra el **sistema interno de orden y relación del archivo**. Históricamente también existió un repositorio separado `ligereza/IRIS`; no confundas ese repositorio con el sistema interno que vive dentro del árbol MAK/iskvw.

IRIS puede producir insumos para portafolio, dossier, investigación o postulación, pero **no es el portafolio público**.

### iskvw / Portfolio
`iskvw` representa la práctica/archivo y sus superficies de curatoría/publicación. La interfaz interna de orden puede compartir archivos o rutas con iskvw sin que sistema interno y producto público sean equivalentes.

### RD
RD mantiene su propia autoridad para eventos, datos, piezas y productos. Compartir entidades o contratos con Portfolio/MAK no autoriza a fusionar bases ni semánticas automáticamente.

### XIO
XIO es una frontera relacionada con operación visual/show y dispositivos. La historia contiene varias migraciones y copias; para cualquier cambio actual hay que comprobar el consumidor y ruta presentes en el código/árbol de la rama actual.

## 5. Qué información se mide, no se escribe como “estado”

Cuando el agente tenga acceso a la máquina MAK:

```bash
.venv/bin/python tools/mak_status.py --json
```

Para el carril Git actual:

```bash
git branch --show-current
git status --short
git log -1 --oneline
```

Para FLUJO:

```bash
python -m flujo --help
```

No copies a este archivo números de servicios, tests, bases, listeners o archivos si no son una decisión durable. Los números envejecen y fueron una causa histórica de documentación falsa.

## 6. Qué manda cuando dos documentos discrepan

Orden de precedencia:

1. instrucción actual del usuario;
2. código/datos medidos en la rama y máquina relevantes;
3. `branch_profile.json`, contratos y tests ejecutables;
4. este archivo para vocabulario y arquitectura durable;
5. documentación específica del dominio;
6. `HISTORICO.md` y Git para explicar el pasado.

Un documento viejo nunca gana por llamarse `CURRENT`, `CANONICAL`, `MASTER`, `STATUS` o `LAST_HANDOFF`.

## 7. Decisiones durables que siguen importando

- Hablar al operador en español; código/identificadores nuevos tienden a inglés. Los productos humanos de RD/iskvw usan español correcto con diacríticos.
- El trabajo actual se define por el encargo actual, no por un handoff heredado.
- No reintroducir múltiples archivos de contrato para agentes.
- No tratar historia de branches/worktrees como topología actual sin medirla.
- No convertir co-localización física en autoridad semántica.
- No aceptar “listo” como evidencia: verificar el comportamiento que importa.
- No crear frameworks o herramientas duplicadas sin buscar primero lo que ya existe.
- Mantener separado hecho observado, inferencia y decisión humana.

## 8. Cómo encontrar información sin perderse

Si la tarea es de:

- **arquitectura Git / lanes:** `branch_profile.json`, `CAPACIDADES_MAIN.md`, `tools/test_lane_map.py`;
- **CLI FLUJO:** `src/flujo/cli.py`, `MAPA.md`;
- **Hub MAK:** `cultura/mak_plataforma/hub.py`;
- **Hub FLUJO:** `src/flujo/web/hub.py`;
- **IRIS/archivo/curatoría:** empieza por `iskvw/` y los consumidores MAK que lo sirven; no por documentos históricos;
- **RD:** `src/flujo/rd/`, `docs/rd/`, fuentes bajo `data/` según el consumidor;
- **XIO:** inspecciona el `xio/` actual y el consumidor exacto antes de seguir runbooks viejos;
- **por qué se tomó una decisión:** `HISTORICO.md`, luego `git log -- <ruta>`.

## 9. Qué NO es una fuente de trabajo pendiente

No uses como backlog:

- `NEXT.md` histórico;
- cierres de sesión;
- “single next action” dentro de PHASE/handoff;
- planes fechados;
- auditorías que dicen “open” o “pending” sin confirmar en el presente;
- archivos recuperados de Claude/Codex;
- un comentario de commit antiguo.

Si el usuario no dejó una tarea actual, no inventes una desde esos materiales.

## 10. Regla de mantenimiento

Este archivo debe seguir corto y estable. Si una frase puede quedar falsa por un reinicio, un merge, un test nuevo o una cifra cambiante, no pertenece aquí: debe medirse.

Para la historia resumida, usa `HISTORICO.md`.
