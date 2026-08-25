# C03 — entrada pública y puente ciego

## Pregunta

C02 demostró que el extremo nativo puede observar documentos, recursos,
capacidades y referencias reales, pero dejó el vínculo con publicación como
`unknown`. C03 prueba la frontera complementaria:

1. ¿Puede MAK aceptar un export público sin asumir una versión estable,
   authorship inferida o nombres suficientes?
2. ¿Puede comparar publicación, media exportado y artefactos nativos sin usar
   la respuesta correcta como oracle durante la recuperación?
3. ¿Abstenerse cuando falta el catálogo o cuando la evidencia es ambigua queda
   representado mecánicamente?

## Estado de datos

No existe hoy un export público real local con posts, reels, stories y sus
medios. El caso real del ciclo es, por tanto, `catalog_status=unavailable` y
`public_join=unknown`. No se reemplaza esa ausencia con archivos sintéticos.

El subexperimento ciego usa fixtures pequeños como benchmark controlado. La
verdad de evaluación se guarda separada de la entrada del resolver y nunca se
entrega a la función que genera candidatos. Sus resultados sirven para probar
el contrato y los falsos enlaces, no para afirmar que ARICA ya fue reconciliado.

## Raíz de procedencia

`archive-arica-001` es una raíz fija de un solo archivo artístico. No se
aprende autoría. La relación que se investiga es interna:

```text
public record -> exported media -> candidate local artifact
                                      -> native evidence
```

Un `post` puede quedar sin artifact; un artifact puede quedar sin `post`; una
coincidencia visual o técnica queda como `candidate`; sólo evidencia explícita
y compatible puede elevar el estado.

## Contratos y límites

- El normalizador produce una forma canónica con `archive_id` explícito,
  publicación, media, evidencia de origen, hashes cuando existan y estado de
  completitud.
- HTML, JSON y rutas desconocidas se conservan como observaciones o errores;
  no se inventan campos de fecha, URL, tipo o media.
- La evaluación ciega separa `candidate`, `confirmed`, `contradicted`,
  `ambiguous` y `unknown`.
- Similaridad, basename, dimensiones o extensión sólo generan candidatos.
- No se crean `generated`, `RENDERS_TO` ni `publication -> authoring` por
  proximidad.
- La ausencia del catálogo público es un resultado válido y debe cerrar el
  puente con `unknown`, no producir un grafo vacío presentado como completo.

## Resultado esperado

El gate debe mostrar que la entrada pública se puede validar sin depender de
un modelo grande y que el puente ciego mide enlaces correctos, falsos enlaces,
abstenciones y cobertura de casos. Después, el siguiente paso será correr el
normalizador sobre un export real entregado por el artista y conectar sólo las
observaciones que existan.
