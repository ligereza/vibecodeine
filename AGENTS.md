# README para agentes — base flexible

Este archivo ayuda a entrar al trabajo y continuarlo. Está abierto a cambios cuando la experiencia los justifique. Completa únicamente lo que ayude a decidir o actuar; los espacios vacíos no impiden empezar una tarea clara.

## Dónde están los hechos

Este archivo no los tiene a propósito. Antes de asumir nomenclatura, estado o vocabulario del sistema:

- **Decisiones cerradas, con fecha:** `DECISIONES.md`.
- **Estado medido de la máquina:** `.venv/bin/python tools/mak_status.py` — nunca en prosa.
- **Vocabulario y continuidad ya resueltos** (qué es MAK, `vibecodeine`, IRIS, RD, Portfolio): `MEMORIAS.md`.
- **Registro histórico, no instrucción:** `context/HANDOFF_HISTORICO.md`.

`MAK`, `vibecodeine` y las ramas/checkouts MAK y FLUJO son nombres fijados por el operador (`DECISIONES.md`, 2026-09-03) que se confunden seguido. No re-derivarlos desde código o commits sueltos sin pasar antes por los punteros de arriba.

## Lo que buscamos

**Intención del usuario:** _Por completar desde el encargo real._

**Resultado que permitiría darlo por resuelto:** _Por concretar; si estamos explorando, indicar qué queremos descubrir._

**Límites o decisiones que debemos respetar:** _Sólo los que correspondan al trabajo actual._

## Criterio para trabajar

- Entiende la intención y elige un bloque útil que puedas llevar hasta un resultado revisable. Ajusta el método según lo que encuentres.
- Resuelve las decisiones técnicas dentro del encargo. Consulta cuando falte una decisión de significado, preferencia, autoridad o consecuencias que corresponda al usuario; explica las opciones sin exigir conocimientos especializados.
- Aprovecha lo que existe y conserva el trabajo ajeno. Inspecciona las partes de las que depende tu intervención; amplía la lectura cuando aparezca una dependencia relevante.
- Trata las notas anteriores como orientación. Comprueba los hechos que sostienen tu siguiente decisión. Mantén visibles los supuestos y las contradicciones que afecten al resultado.
- Comprueba el comportamiento que importa y cumple los controles aplicables. Añade pruebas cuando cubran un riesgo relevante; evita duplicarlas por el mero hecho de haber cambiado algo.
- Comunica resultados y limitaciones útiles. Un intento fallido puede aportar conocimiento; descríbelo como tal. Si repites sin aprender, cambia el enfoque.

## Para quien continúe

_Completar cuando haya algo que merezca conservarse. Actualizar al cambiar la situación o dejar trabajo pendiente; no hace falta registrar cada acción._

**Punto actual:** _Qué quedó utilizable y qué sigue en curso._

**Para continuar:** _Próxima intervención razonable, su motivo y dónde trabajar. Añadir una referencia de comprobación o una incógnita sólo si condiciona ese paso._

**Aprendizaje que evita repetir un error:** _Opcional. Dejar únicamente lo que siga siendo relevante._

## Cómo puede evolucionar

El agente puede aclarar, completar y simplificar este archivo. Las instrucciones y decisiones del usuario conservan su autoridad; cualquier contradicción material debe hacerse visible.

Añade una sección cuando resuelva una necesidad concreta y recurrente. Conserva el historial en su lugar existente y mantén aquí una síntesis vigente con referencias cuando hagan falta. El texto escrito por un agente sigue sujeto a comprobación.

## Limites Git vigentes (2026-09-14)

- Este directorio es `ligereza/vibecodeine`, la estación MAK y su historia.
- `ligereza/flujo` es un repositorio autónomo. Su checkout activo local es
  `/home/mak/flujo`; no es un worktree de este repositorio.
- El antiguo worktree se conserva, rotulado, en
  `/home/mak/flujo-vibecodeine-legacy-20260914`. No lo uses como fuente activa
  ni lo mezcles de vuelta con FLUJO.
- En el remoto del padre, `main` es la única rama operativa permanente y
  `historia` es la referencia histórica. Las ramas `archive/*` son tags de
  procedencia, no superficies de trabajo. `dependabot/*` puede aparecer como
  automatización efímera.
- No crees ni uses ramas `FLUJO`, `MAK` o `integration/flujo-*` para continuar
  FLUJO. Entra por `https://github.com/ligereza/flujo` y lee su `AGENTS.md`.

La frontera completa y el inventario están en `REPOS.md`. El estado local
medido está en `STATUS.md`; no lo confundas con una autoridad remota ni con
una instrucción de código.

La edición de este README debe facilitar el próximo trabajo. No es una tarea que deba crecer en cada sesión.
