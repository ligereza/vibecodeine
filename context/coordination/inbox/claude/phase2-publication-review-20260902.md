# Claude nuevo — Fase 2: revisión y preparación de publicación

## Encargo

Revisa el write-set local que Faro/Codex dejó después de auditar y reparar el
trabajo de Claude sobre la separación física `MAK` / `FLUJO`. La Fase 1 ya está
cerrada. Tu tarea es preparar una recomendación de publicación, no inventar una
nueva solución ni reabrir IRIS.

El resultado debe responder si el write-set es publicable tal como está, qué
archivos pertenecen a cada commit de rama y qué bloqueo concreto queda, si
queda alguno.

## Lectura mínima obligatoria

No leas el repositorio completo, el ODT, logs antiguos, `WIN`, `main` ni
`historia`. Lee solamente:

1. `/home/mak/AGENTS.md`.
2. Las líneas actuales iniciales de
   `/home/mak/context/LAST_HANDOFF.md` hasta antes de `# Operational Handoff`
   (incluyen la traza Claude, la reparación y la reejecución de suites).
3. El estado y el diff local de los dos checkouts, mediante estos comandos:

```bash
git -C /home/mak branch --show-current
git -C /home/mak status --short
git -C /home/mak diff --stat
git -C /home/mak/flujo branch --show-current
git -C /home/mak/flujo status --short
git -C /home/mak/flujo diff --stat
git -C /home/mak diff --check
```

Después inspecciona únicamente los diffs de los paths que esos estados
enumeren. No hagas un `find` o `rg` masivo del repositorio para sustituir esta
lectura. Si necesitas verificar un contrato, abre el archivo puntual y la
prueba puntual que lo consume.

## Estado conocido de entrada

- Checkout MAK: `/home/mak`, rama `MAK`, HEAD `fe4d3fab`.
- Checkout FLUJO: `/home/mak/flujo`, rama `FLUJO`, HEAD `27ede605`.
- Suites ya ejecutadas con `/home/mak/.venv/bin/python` y
  `PYTHONDONTWRITEBYTECODE=1`: MAK `2175 passed, 5 skipped`; higiene MAK
  `89 passed`; integración `372 passed`; FLUJO `1611 passed, 44 skipped`;
  higiene FLUJO `54 passed`; ratchets de handoff/idioma `15 passed`;
  `python -m flujo verify` terminó `verify OK`.
- Preflight: cinco superficies OK, cero errores/unknowns/warnings.
- `release_gate.py --check` da `IMPLEMENTATION_COMPLETE_TESTS_DEFERRED`,
  cero blockers y cero unknowns; su exit 5 es el código documentado de tests
  diferidos, no un fallo de pytest.
- Los puertos `8900`, `8890`, `8891`, `8765` y `11434` están activos en
  `127.0.0.1`.

## Alcance permitido

Revisa y clasifica el write-set que ya existe. El cambio esperado está limitado
a:

- contratos/workflows y requisitos de composición MAK/FLUJO;
- resolución de imports y rutas hacia el checkout físico hermano;
- `runtime_preflight.py`, `release_gate.py`, `verify_all.py` y sus tests;
- tests de regresión de esos límites;
- el handoff actual y documentación directamente afectada.

La presencia de `tests/test_render_flyer_mak.py` como archivo nuevo es esperada.
No añadas archivos, no regeneres outputs y no conviertas un path lógico
`src/flujo` de una allowlist en un import activo sin evidencia de ejecución.

## Límites duros

- No tocar IRIS, el lector IRIS, `iskvw/datos/*`, `campo.json`,
  `animadas.json`, `iskvw/piel/*`, bases de datos ni outputs artísticos.
- No hacer `git add -A`, `git add .`, `git checkout`, `git reset`, `git clean`,
  `git switch`, crear ramas, commit, push, merge ni reinicio de servicios.
- No cambiar los cinco procesos o sus puertos.
- No corregir supuestos problemas fuera del write-set. Si encuentras uno,
  reporta path, línea, evidencia y riesgo; no lo parches en esta fase.
- No repetir las suites completas salvo que una discrepancia específica del
  diff lo exija. Las mediciones de entrada son válidas y están registradas.
- No tratar un HTTP 200, un nombre de archivo o una posición como evidencia de
  autoría o verdad artística.

## Procedimiento acotado

1. Comprueba ramas, estado, estadísticas y `git diff --check` en ambos árboles.
2. Confirma que cada path modificado cae en la clasificación permitida y que no
   hay archivos IRIS/datos en el write-set.
3. Lee los diffs operativos y de tests, no los archivos completos salvo que una
   línea de diff requiera contexto.
4. Para cada cambio, determina: consumidor, checkout dueño, riesgo de runtime,
   prueba que lo cubre y si debe ir al commit MAK o FLUJO.
5. Ejecuta solo checks focales si son necesarios para resolver una duda. Usa el
   venv `/home/mak/.venv/bin/python` y `PYTHONDONTWRITEBYTECODE=1`.
6. Produce un informe final con una de estas dos etiquetas:
   `WRITESET_OK_FOR_OPERATOR_REVIEW` o `REVIEW_NEEDED`.

## Entrega obligatoria

Devuelve:

1. conteo exacto de paths por checkout y clasificación;
2. lista de paths fuera de alcance (debe ser vacía);
3. propuesta de dos grupos de commit, MAK y FLUJO, sin ejecutarlos;
4. discrepancias, warnings y blockers separados;
5. comandos ejecutados y códigos de salida;
6. siguiente acción mínima.

Al terminar, añade únicamente una sección breve y fechada a
`/home/mak/context/LAST_HANDOFF.md` con ese resultado. No modifiques código,
datos, ramas ni servicios. Si no puedes verificar algo sin ampliar el alcance,
decláralo como `unverified` y detente ahí.
