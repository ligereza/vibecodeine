# Inventario de herramientas y automatizaciones

Última actualización: 2026-06-12

## Rol del sistema

Este repo funciona como centro de producción técnica para automatizaciones de diseño gráfico, motion, flyers, asistencia con IA y futuros agentes locales/semi-locales.

## Apps principales

- Blender
- Adobe Photoshop
- Adobe Illustrator
- Adobe After Effects
- Canva
- Git Bash
- GitHub
- Arena.ai
- Chats IA gratuitos con cuota diaria
- Python/scripts locales

---

# Automatizaciones ya implementadas

## 1. Automatización de flyers para eventos

### Flujo actual

```txt
Descargar foto de Instagram
> Droplet de Photoshop
> Photoshop exporta JPG
> Blender abre usando ese JPG
> Blender genera composición 3D del flyer
> Se extraen/usan colores predominantes
> Blender exporta archivo final
> Se envía al jefe de eventos
```

### Objetivo del flujo

Agilizar la creación de flyers visuales para eventos usando una imagen base y una composición 3D ya preparada.

### Herramientas involucradas

- Instagram / descarga de imagen
- Photoshop droplet
- Blender
- Scripts o automatización de export

### Posibles mejoras

- Crear manifest JSON por flyer.
- Registrar imagen fuente, fecha, evento, versión y salida final.
- Automatizar naming estándar.
- Generar preview comprimido para IA.
- Guardar checkpoint por evento.
- Crear checklist antes de enviar al jefe.

---

## 2. Slowmo en Blender + After Effects

### Flujo actual

```txt
Blender
> Exportar elementos separados
> Separar carpetas: elementos / fondo / vfx
> Time stretching
> Script exporta solo rangos de frames que tendrán slowmo
> Script renombra exports anteriores para calzar con número de render
> Orden de carpetas para abrir en After Effects
> Optimización de espacio convirtiendo carpetas de frames a video
> Eliminar carpetas pesadas EXR/PNG después de consolidar
```

### Objetivo del flujo

Reducir tiempos y espacio en disco al trabajar slowmo/VFX, exportando solo lo necesario y manteniendo estructura limpia para After Effects.

### Herramientas involucradas

- Blender
- After Effects
- Python/scripts
- Posiblemente FFmpeg

### Posibles mejoras

- Crear archivo `render_manifest.json` por render.
- Guardar rangos de slowmo en CSV/JSON.
- Crear validador: confirmar que videos finales existen antes de borrar frames.
- Crear modo dry-run para no eliminar por error.
- Crear reporte de espacio ahorrado.

---

# Automatizaciones por construir

## 3. Asistente de misión/pedido del jefe

### Necesidad

Un asistente de texto que entienda lo que pide el jefe y transforme el pedido en un plan de automatización usando las apps disponibles:

- Blender
- Illustrator
- Photoshop
- After Effects
- Canva

### Debe separar pedidos por área

- Flyer para evento
- Flyer para ventas
- Flyer informativo
- Motion/slowmo
- Adaptación para redes
- Entrega interna para jefe
- Material para cliente externo

### Salida ideal

```md
## Tipo de pedido
## Objetivo
## Inputs necesarios
## Apps recomendadas
## Flujo sugerido
## Automatizaciones disponibles
## Qué se puede automatizar
## Qué requiere decisión humana
## Archivos a preparar
## Checklist de entrega
```

---

## 4. Canva lote + generación de tablas/JSON

### Necesidad

Usar IA/asistente para armar tablas o JSON que luego sirvan como input para Canva, Illustrator u otras apps.

### Casos de uso

- Flyers informativos
- Flyers de ventas
- Variantes de copy
- Lotes de datos para Canva
- Datos estructurados para Illustrator scripts

### Formatos recomendados

- CSV para Canva bulk create
- JSON para scripts personalizados
- Markdown para revisión humana

### Ejemplo JSON

```json
{
  "tipo_pieza": "flyer_ventas",
  "cliente": "",
  "campania": "",
  "formato": "1080x1350",
  "items": [
    {
      "titulo": "",
      "subtitulo": "",
      "precio": "",
      "cta": "",
      "fecha": "",
      "imagen_ref": ""
    }
  ]
}
```

---

## 5. Orden y limpieza de recursos/capas/carpetas

### Necesidad

Crear botones/scripts personalizados por carpeta para limpiar, ordenar y preparar recursos de diseño.

### Posibles acciones

- Renombrar archivos por convención.
- Separar assets por tipo.
- Detectar duplicados.
- Crear carpetas estándar.
- Mover previews a carpeta `02_exports`.
- Mover editables pesados a carpeta local ignorada por Git.
- Comprimir previews.
- Crear índice de recursos.
- Crear reporte para IA.

### Concepto de botones

Cada carpeta puede tener scripts tipo:

```txt
_limpiar_flyer_evento.py
_ordenar_assets.py
_crear_contexto_ia.py
_generar_contact_sheet.py
_preparar_entrega.py
```

Estos scripts pueden luego ejecutarse desde:

- Git Bash
- VS Code Tasks
- Atajos de Windows
- Botones `.bat`
- Panel personalizado futuro

---

# Estado de revisión / errores abiertos

Fecha: 2026-06-12

## ERROR-TOOL-001 — Automatización flyers eventos requiere revisión

### Herramienta

Download Instagram photo > Photoshop droplet > JPG > Blender composición 3D > colores predominantes > export > envío al jefe.

### Estado

Funciona como prototipo implementado, pero queda marcada como **ERROR / REVISIÓN PENDIENTE** hasta auditar archivos reales.

### Motivo

- Falta documentación completa.
- Falta manifest por flyer.
- Falta manejo de errores.
- Falta validar rutas, naming, inputs y outputs.
- Falta comprobar si el flujo es reproducible en otro equipo/chat/agente.
- Falta definir rollback/versionado de outputs.

### Próxima acción

Cuando el usuario suba archivos, revisar estructura real y crear reporte técnico.

---

## ERROR-TOOL-002 — Slowmo Blender/After Effects requiere revisión

### Herramienta

Blender slowmo > separar elementos/fondo/vfx > export rangos > renombrar renders > preparar AE > consolidar frames a video > borrar frames pesados.

### Estado

Funciona como prototipo implementado, pero queda marcada como **ERROR / REVISIÓN PENDIENTE** hasta auditar archivos reales.

### Motivo

- Alto riesgo por eliminación de frames EXR/PNG pesados.
- Falta modo dry-run confirmado.
- Falta validación antes de borrar.
- Falta reporte de rangos exportados.
- Falta manifest de render.
- Falta documentación de estructura esperada para After Effects.

### Próxima acción

Crear validador antes de cualquier script destructivo:

```txt
verificar frames > verificar video consolidado > comparar duración/tamaño > pedir confirmación > mover frames a quarantine antes de borrar
```
