# Checkpoint — Inventario inicial de automatizaciones diseño/motion

Fecha: 2026-06-12

## Resumen corto

Se registran automatizaciones existentes y líneas futuras del sistema: flyers de eventos con Photoshop + Blender, slowmo Blender + After Effects, asistente de pedidos del jefe, generación de datos para Canva/Illustrator y scripts de limpieza/orden por carpeta.

## Automatizaciones existentes

### Flyer eventos

Flujo:

```txt
Download Instagram photo > droplet Photoshop > PS exporta JPG > Blender usa JPG > composición 3D con colores predominantes > export final > envío al jefe de eventos
```

### Slowmo Blender/After Effects

Flujo:

```txt
Blender slowmo > separar elementos/fondo/vfx > export time stretching > exportar solo rangos de slowmo > renombrar exports anteriores para calzar render > ordenar carpetas para After Effects > consolidar frames como video > eliminar EXR/PNG pesados con cuidado
```

## Herramientas disponibles

- Blender
- Photoshop
- Illustrator
- After Effects
- Canva
- Python
- Git Bash
- GitHub
- Arena.ai
- Chats IA gratuitos

## Necesidades futuras

1. Asistente de texto que entienda pedidos del jefe.
2. Clasificar pedidos por área: evento, ventas, informativo, motion.
3. Crear planes de automatización usando apps disponibles.
4. Generar tablas/CSV/JSON para Canva e Illustrator.
5. Crear scripts tipo botones personalizados para limpieza y orden de carpetas.

## Decisiones tomadas

- Separar flujo de asistentes y flujo de agentes.
- Primero construir asistentes que ordenen pedidos y datos.
- Después crear agentes/scripts que ejecuten acciones.
- Todo script destructivo debe tener modo dry-run.

## Archivos creados relacionados

- `context/TOOLS_INVENTORY.md`
- `docs/PRODUCCION_TECNICA.md`
- `docs/FLUJOS_ASISTENTES_AGENTES.md`
- `prompts/asistente_pedido_jefe.md`
- `prompts/asistente_limpieza_carpeta.md`
- `scripts/python_tools/folder_cleaner_dryrun.py`

## Próximo paso recomendado

Probar el prompt `prompts/asistente_pedido_jefe.md` con un pedido real del jefe y convertirlo en un plan estructurado.

Luego probar `folder_cleaner_dryrun.py` en una carpeta de recursos desordenada para generar un reporte sin mover ni borrar nada.
