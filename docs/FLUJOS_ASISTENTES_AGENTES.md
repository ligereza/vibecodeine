# Flujos: asistentes vs agentes

## Diferencia principal

```txt
Asistente = piensa, ordena, redacta, estructura, recomienda.
Agente = ejecuta acciones en archivos/apps con permisos.
```

---

# Flujo de asistentes

## Objetivo

Usar IAs gratuitas para pensar mejor y preparar inputs sin depender de automatización riesgosa.

## Flujo base

```txt
Pedido del jefe
> Asistente clasifica pedido
> Asistente detecta datos faltantes
> Asistente arma plan
> Asistente genera JSON/CSV/prompts
> Humano revisa
> Scripts/apps ejecutan
> Se guarda checkpoint
```

## Asistentes propuestos

### 1. Asistente de pedido del jefe

Entrada:

```txt
Texto o audio transcrito del jefe
```

Salida:

```md
Tipo de pedido
Área
Urgencia
Inputs necesarios
Flujo recomendado
Apps
Checklist
```

### 2. Asistente Canva/CSV

Entrada:

```txt
Lista de productos, eventos o información
```

Salida:

```csv
titulo,subtitulo,precio,fecha,cta,imagen
```

### 3. Asistente Illustrator/JSON

Entrada:

```txt
Datos de flyer informativo o ventas
```

Salida:

```json
{
  "documento": {},
  "textos": [],
  "imagenes": [],
  "estilos": {}
}
```

### 4. Asistente de limpieza de carpeta

Entrada:

```txt
Listado de archivos o estructura de carpeta
```

Salida:

```md
Qué mover
Qué renombrar
Qué borrar con cuidado
Qué comprimir
Qué subir a GitHub
```

### 5. Asistente de producción motion

Entrada:

```txt
Descripción de render, slowmo, rangos, elementos
```

Salida:

```json
render_manifest.json
slowmo_ranges.json
plan_after_effects.md
```

---

# Flujo de agentes

## Objetivo

Ejecutar tareas repetitivas de manera controlada.

## Flujo base

```txt
Plan aprobado
> Agente lee manifest JSON
> Ejecuta acciones en modo dry-run
> Muestra cambios propuestos
> Humano confirma
> Ejecuta cambios reales
> Genera reporte
> Commit/checkpoint
```

## Agentes propuestos

### 1. Agente creador de proyecto

Crea estructura estándar según tipo:

- evento
- ventas
- informativo
- motion/slowmo

### 2. Agente ordenador de assets

Ordena archivos por tipo:

```txt
_editables
_previews
_exports
_referencias
_fuentes
_video
_audio
_frames
```

### 3. Agente generador de datos

Convierte Markdown o tabla simple en:

- CSV para Canva
- JSON para Illustrator
- JSON para Blender

### 4. Agente consolidador de renders

- Verifica frames.
- Convierte secuencia a video.
- Valida duración.
- Borra frames solo con confirmación.

### 5. Agente checkpoint GitHub

- Crea checkpoint.
- Actualiza changelog.
- Commit.
- Push.

---

# Regla de oro

Primero asistentes. Después agentes.

Porque los asistentes reducen ambigüedad y los agentes ejecutan mejor cuando el input está estructurado.
