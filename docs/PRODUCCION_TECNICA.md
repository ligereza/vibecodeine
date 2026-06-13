# Producción técnica del proyecto

Fecha: 2026-06-12
Productor técnico: Arena.ai Agent Mode

## Misión

Convertir automatizaciones sueltas de diseño/motion en un sistema ordenado, documentado y reutilizable, con checkpoints que permitan continuar el trabajo desde cualquier chat de IA o herramienta.

## Principio central

No construir un agente gigante desde el inicio. Primero construir una capa de producción técnica:

```txt
Inventario de herramientas
+ taxonomía de pedidos
+ estructura de carpetas
+ manifests JSON/CSV
+ prompts de asistencia
+ scripts pequeños
+ checkpoints
+ GitHub
```

## Objetivos por fase

### Fase 1 — Documentar lo existente

- Registrar automatización de flyers con Photoshop + Blender.
- Registrar automatización slowmo Blender + After Effects.
- Identificar scripts existentes.
- Crear diagramas simples de cada flujo.
- Guardar riesgos y puntos manuales.

### Fase 2 — Crear asistente de pedidos

El asistente debe convertir un pedido del jefe en:

- Tipo de pieza.
- Área del pedido.
- Inputs faltantes.
- Apps recomendadas.
- Flujo paso a paso.
- Automatizaciones disponibles.
- Archivos que hay que crear.
- Checklist final.

### Fase 3 — Estandarizar datos

Crear formatos de datos para:

- Canva lote: CSV.
- Illustrator scripts: JSON.
- Flyers eventos: JSON manifest.
- Slowmo renders: JSON manifest.
- Checkpoints: Markdown.

### Fase 4 — Scripts de orden y limpieza

Crear scripts pequeños para carpetas:

- Ordenar recursos.
- Renombrar archivos.
- Separar editables/pesados/previews.
- Generar índice de assets.
- Generar contexto IA.
- Crear previews/contact sheets.

### Fase 5 — Flujo de asistentes

Asistentes = IA que no controla directamente apps, pero ayuda a preparar decisiones, datos, prompts y pasos.

Ejemplos:

- Asistente de pedido del jefe.
- Asistente de copy para Canva.
- Asistente de limpieza de carpeta.
- Asistente de checklist de entrega.
- Asistente de producción motion.

### Fase 6 — Flujo de agentes

Agentes = scripts o automatizaciones que sí ejecutan acciones en el sistema, con permisos controlados.

Ejemplos:

- Agente que crea estructura de proyecto.
- Agente que prepara CSV/JSON.
- Agente que mueve/renombra archivos.
- Agente que abre Blender/Photoshop con inputs.
- Agente que genera reporte y commit en Git.

## Reglas de seguridad/producción

1. Todo script destructivo debe tener modo `dry-run`.
2. No borrar frames pesados hasta confirmar que el video consolidado existe.
3. No subir archivos privados o pesados a GitHub sin revisión.
4. Cada automatización debe tener README corto.
5. Cada flujo debe registrar input, output y errores.
6. Cada pedido del jefe debe transformarse primero en plan antes de ejecutar.

## Próximo paso recomendado

Crear el primer módulo: `asistente_pedido_jefe`.

Este módulo no ejecuta apps todavía. Solo toma texto libre y devuelve:

- clasificación del pedido
- plan
- estructura de archivos
- JSON/CSV si corresponde
- checklist
