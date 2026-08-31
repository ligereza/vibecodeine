# Phase 452 — Tapiz Void variant consolidation gate

## Alcance

Se auditó `projects/tapiz/vibecode_void.html` y se comparó conceptualmente
con el hermano `projects/tapiz/vibecode_spaces.html`. Ambos leen código local y
visualizan espacios con la paleta `flujo`, pero no son duplicados de contrato:

| Superficie | Consumidor principal | Operación distintiva |
|---|---|---|
| `vibecode_spaces.html` | diseñador/editor | ocho modos, fuente editable, export HTML protegido |
| `vibecode_void.html` | pieza/proyección en flujo | generador automático, ventana deslizante, negative/blocks, sin export |

La decisión segura es consolidar documentalmente como familia Tapiz Spaces,
manteniendo dos skins hasta que exista un consumidor que pida una interfaz
unificada. No se fusionó código por similitud superficial ni se eliminó la
variante Void.

## Validación foreground

Ejecutado desde `/home/mak/flujo`:

```text
Node new Function + marker contract check          -> exit 0
HTMLParser/dependency/brand assertions             -> exit 0
JSON parse projects/flujo/flujo.json               -> exit 0
cmp contra flujo-deploy/projects/tapiz/...         -> exit 0
```

El HTML tiene 14,463 bytes, 48 tags, un script inline, un enlace de retorno al
hub y cero `src` externos, `fetch`, XMLHttpRequest, WebSocket, localStorage o
URLs HTTP(S). El script real parsea con 8,241 bytes. Los cinco colores se
comparan contra `projects/flujo/flujo.json` y coinciden. La copia de deploy es
idéntica, SHA-256
`855a5994a5152da52216d24c026b9b55785d26d8ea3ee53c8b655aa46e4d935d`.

## Dictamen

```text
TAPIZ_VOID_OWNER_GREEN
TAPIZ_VOID_BRAND_SOURCE_GREEN
TAPIZ_VOID_LOCAL_INPUT_GREEN
TAPIZ_VOID_AUTOGENERATOR_LOCAL_ONLY
TAPIZ_VOID_VARIANT_SEPARATED_BY_CONSUMER
TAPIZ_VOID_DEPLOY_COPY_EXACT
```

Void es una variante funcional legítima, no basura: su auto-generador y su
ventana de proyección no existen en Spaces. A la vez, no se promueve como
segunda herramienta independiente de primer nivel; queda registrada como
skin/variant de la familia Tapiz Spaces.

## Riesgos y rollback

- `Math.random()` genera código sintético para la proyección; nunca se
  presenta como fuente real ni se persiste.
- La exportación no existe en Void; añadirla sin un consumidor real duplicaría
  el contrato de Spaces.
- No hubo cambios en HTML, JSON, fuente, despliegue o evidencia; rollback:
  no-op.

## Siguiente acción

Continuar con el siguiente HTML no cubierto de la familia cultural/portfolio,
manteniendo Void y Spaces bajo un mismo grupo conceptual pero con owners de
skin separados. No volver a auditar XIO ni los gates ya cerrados.
