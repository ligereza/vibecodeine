# Recomendación de herramientas thi.ng para vibecodeine

## Contexto

Este documento está dirigido al agente local que trabaja sobre el repositorio:

- Repo: https://github.com/ligereza/vibecodeine
- Ecosistema evaluado: https://thi.ng/#tags

`vibecodeine` es un sistema híbrido que combina procesamiento de conocimiento, ingesta y transformación de datos, grafo semántico, automatizaciones, generación de SVG y una interfaz web TypeScript.

La recomendación prioriza herramientas que puedan integrarse gradualmente sin reemplazar la arquitectura existente.

---

## Ranking: top 15

| # | Paquete | Prioridad | Uso recomendado |
|---:|---|---|---|
| 1 | [`@thi.ng/rstream`](https://docs.thi.ng/umbrella/rstream/) | Muy alta | Flujos reactivos para ingesta, procesamiento, render y publicación |
| 2 | [`@thi.ng/transducers`](https://docs.thi.ng/umbrella/transducers/) | Muy alta | Pipelines composables para transformar documentos y colecciones |
| 3 | [`@thi.ng/graph`](https://docs.thi.ng/umbrella/graph/) | Muy alta | Relaciones entre documentos, conceptos, artistas, eventos y fuentes |
| 4 | [`@thi.ng/rstream-graph`](https://docs.thi.ng/umbrella/rstream-graph/) | Muy alta | Construcción declarativa de pipelines de datos observables |
| 5 | [`@thi.ng/hiccup-svg`](https://docs.thi.ng/umbrella/hiccup-svg/) | Muy alta | Generación programática de flyers, contraportadas y diagramas SVG |
| 6 | [`@thi.ng/geom`](https://docs.thi.ng/umbrella/geom/) | Alta | Geometría 2D, formas, trazados y transformaciones |
| 7 | [`@thi.ng/color`](https://docs.thi.ng/umbrella/color/) | Alta | Paletas, gradientes y variaciones cromáticas generativas |
| 8 | [`@thi.ng/hiccup`](https://docs.thi.ng/umbrella/hiccup/) | Alta | Representación declarativa de HTML y SVG como estructuras de datos |
| 9 | [`@thi.ng/rdom`](https://docs.thi.ng/umbrella/rdom/) | Alta | Interfaz web reactiva y liviana sobre DOM |
| 10 | [`@thi.ng/atom`](https://docs.thi.ng/umbrella/atom/) | Alta | Estado global, transacciones y undo/redo |
| 11 | [`@thi.ng/associative`](https://docs.thi.ng/umbrella/associative/) | Media-alta | Consultas y actualizaciones de estructuras anidadas |
| 12 | [`@thi.ng/validate`](https://docs.thi.ng/umbrella/validate/) | Media-alta | Validación de documentos, metadatos y configuraciones |
| 13 | [`@thi.ng/parse`](https://docs.thi.ng/umbrella/parse/) | Media | Parsers para formatos, frontmatter y vocabularios propios |
| 14 | [`@thi.ng/fuzzy`](https://docs.thi.ng/umbrella/fuzzy/) | Media | Búsqueda tolerante de documentos, conceptos y etiquetas |
| 15 | [`@thi.ng/intervals`](https://docs.thi.ng/umbrella/intervals/) | Media | Fechas, rangos temporales, eventos y ventanas de publicación |

---

## Prioridad de implementación

### Fase 0: investigación antes de modificar código

El agente local debe:

1. Revisar `package.json`, `web/package.json` y cualquier lockfile.
2. Identificar si el frontend usa TypeScript directamente, Vite u otro bundler.
3. Localizar el código relacionado con:
   - grafo semántico;
   - pipelines de ingesta;
   - render SVG;
   - estado de la interfaz;
   - búsqueda y filtrado.
4. No instalar las 15 librerías de una vez.
5. Verificar versiones actuales y compatibilidad con el runtime del proyecto.
6. Ejecutar el typecheck y los tests antes de cualquier cambio.

### Fase 1: bajo riesgo y alto beneficio

Instalar y evaluar primero:

```bash
npm install @thi.ng/transducers @thi.ng/graph @thi.ng/validate
```

Objetivos:

- extraer una transformación real de documentos a un pipeline con transducers;
- crear una representación de grafo sobre una muestra de datos existente;
- validar los metadatos de una pieza antes de persistirlos o publicarlos.

No reemplazar todavía los pipelines productivos. Crear adaptadores o módulos experimentales.

### Fase 2: flujos y estado

Evaluar:

```bash
npm install @thi.ng/rstream @thi.ng/rstream-graph @thi.ng/atom
```

Objetivos:

- modelar el flujo `entrada -> extracción -> clasificación -> render -> publicación`;
- representar errores y reintentos de manera explícita;
- observar estados de tareas desde la interfaz;
- evitar introducir una segunda arquitectura global de estado si ya existe una solución funcional.

### Fase 3: SVG y diseño generativo

Evaluar:

```bash
npm install @thi.ng/hiccup @thi.ng/hiccup-svg @thi.ng/geom @thi.ng/color
```

Objetivos:

- generar una pieza SVG mínima desde datos JSON;
- reutilizar geometría y estilos;
- producir paletas o variaciones visuales reproducibles;
- comparar la salida byte por byte o visualmente con los generadores actuales.

### Fase 4: experiencia de búsqueda e interfaz

Evaluar:

```bash
npm install @thi.ng/rdom @thi.ng/fuzzy @thi.ng/intervals
```

Objetivos:

- agregar búsqueda tolerante sobre el corpus;
- explorar filtros por conceptos, fechas, tipos y relaciones;
- usar rdom únicamente si aporta una ventaja clara frente al frontend existente.

---

## Correspondencia con problemas del repositorio

### 1. Pipeline de curaduría y automatización

Combinación recomendada:

```text
rstream + transducers + validate + parse + graph
```

Flujo conceptual:

```text
fuente de entrada
  -> parseo
  -> normalización
  -> validación
  -> clasificación
  -> enriquecimiento
  -> actualización del grafo
  -> render/publicación
```

`rstream` debería encargarse de la coordinación observable. `transducers` debería encargarse de las transformaciones puras. `validate` debería actuar como límite de seguridad antes de persistir o publicar.

### 2. Grafo semántico

Combinación recomendada:

```text
graph + rstream-graph + fuzzy
```

Tipos de nodos potenciales:

- documento;
- proyecto;
- artista;
- evento;
- concepto;
- fuente;
- pieza gráfica.

Tipos de relaciones potenciales:

- `mentions`;
- `related-to`;
- `created-by`;
- `presented-at`;
- `derived-from`;
- `belongs-to`.

El grafo de thi.ng no tiene que reemplazar el almacenamiento actual. Puede utilizarse como capa de análisis en memoria sobre datos ya indexados.

### 3. Generación de flyers y SVG

Combinación recomendada:

```text
geom + color + hiccup + hiccup-svg
```

La pieza podría modelarse como datos declarativos:

```ts
const piece = [
  "svg",
  { width: 1080, height: 1350, viewBox: "0 0 1080 1350" },
  ["rect", { width: 1080, height: 1350, fill: "#111" }],
  [
    "text",
    { x: 80, y: 180, fill: "#fff" },
    "Nombre del evento",
  ],
];
```

El agente debe probar primero una sola plantilla y comparar:

- dimensiones;
- fuentes;
- posiciones;
- colores;
- compatibilidad con el pipeline actual;
- tamaño y validez del SVG generado.

### 4. Interfaz web

Combinación recomendada:

```text
rdom + hiccup + rstream + atom + fuzzy
```

Usos posibles:

- explorador del grafo;
- panel de estados de automatizaciones;
- filtros reactivos;
- búsqueda del corpus;
- vista de relaciones y documentos relacionados.

No migrar toda la interfaz a `rdom` sin una comparación explícita con el stack existente.

---

## Criterios técnicos de evaluación

Para cada paquete evaluado, el agente debe registrar:

1. Qué problema actual resuelve.
2. Qué archivos modifica.
3. Si introduce una segunda abstracción innecesaria.
4. Compatibilidad con Node, TypeScript y bundler actuales.
5. Tamaño añadido al bundle, si aplica.
6. Calidad de tipos y documentación.
7. Facilidad de eliminarlo si el experimento no funciona.
8. Tests agregados.
9. Impacto en rendimiento.
10. Impacto en mantenibilidad.

Formato sugerido para cada experimento:

```text
Paquete:
Problema resuelto:
Módulo experimental:
Datos de entrada:
Resultado esperado:
Métricas antes:
Métricas después:
Tests:
Decisión: adoptar / mantener experimental / descartar
```

---

## Recomendación de arquitectura

Mantener separadas estas capas:

```text
Datos y dominio
  -> funciones puras y tipos propios

Transformaciones
  -> @thi.ng/transducers

Orquestación
  -> @thi.ng/rstream

Relaciones
  -> @thi.ng/graph

Validación
  -> @thi.ng/validate

Render
  -> @thi.ng/geom + @thi.ng/hiccup-svg + @thi.ng/color

Interfaz
  -> stack actual; evaluar @thi.ng/rdom sólo cuando corresponda
```

La prioridad es usar thi.ng como piezas pequeñas y composables, no convertirlo en un framework central del repositorio.

---

## Qué no priorizar ahora

No comenzar por herramientas de:

- WebGL;
- shaders;
- física;
- partículas;
- audio;
- simulaciones;
- hardware;
- fabricación digital.

Pueden ser útiles para futuras visualizaciones o instalaciones, pero no parecen resolver los problemas principales actuales de vibecodeine.

---

## Decisión resumida

Si sólo se pueden probar cinco paquetes, probar en este orden:

1. `@thi.ng/transducers`
2. `@thi.ng/graph`
3. `@thi.ng/validate`
4. `@thi.ng/rstream`
5. `@thi.ng/hiccup-svg`

Si el objetivo inmediato es mejorar los generadores visuales, cambiar el orden a:

1. `@thi.ng/hiccup-svg`
2. `@thi.ng/geom`
3. `@thi.ng/color`
4. `@thi.ng/transducers`
5. `@thi.ng/validate`

Si el objetivo inmediato es mejorar el explorador de conocimiento, cambiar el orden a:

1. `@thi.ng/graph`
2. `@thi.ng/fuzzy`
3. `@thi.ng/transducers`
4. `@thi.ng/rstream`
5. `@thi.ng/rdom`

La recomendación general es comenzar con un experimento pequeño, reversible y cubierto por tests antes de adoptar cualquiera de estas librerías en producción.

---

## Fuentes

- [Repositorio vibecodeine](https://github.com/ligereza/vibecodeine)
- [thi.ng](https://thi.ng/#tags)
- [thi.ng umbrella](https://github.com/thi-ng/umbrella)
- [Documentación de thi.ng](https://docs.thi.ng/)
- [`@thi.ng/rdom`](https://docs.thi.ng/umbrella/rdom/)
- [`@thi.ng/rstream`](https://docs.thi.ng/umbrella/rstream/)
- [`@thi.ng/color`](https://docs.thi.ng/umbrella/color/)
- [`@thi.ng/hiccup-svg`](https://docs.thi.ng/umbrella/hiccup-svg/)
