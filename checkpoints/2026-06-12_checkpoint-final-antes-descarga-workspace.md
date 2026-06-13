# Checkpoint — Final antes de descargar workspace

Fecha: 2026-06-12

## Resumen corto

Se consolidó el sistema inicial de checkpoints para diseño gráfico + automatización + múltiples IAs gratuitas. Se agregó una capa especial para usar IAs avanzadas cuando estén disponibles, con protección mediante Git/GitHub, ramas experimentales y rollback.

## Estado actual del proyecto

El repo `ai-workflow-checkpoints` contiene:

- Estructura base para checkpoints.
- Contexto maestro.
- Inventario de herramientas y automatizaciones.
- Documentación de producción técnica.
- Separación conceptual entre asistentes y agentes.
- Prompt para continuar desde checkpoints.
- Prompt para registrar intentos fallidos.
- Prompt para entender pedidos del jefe.
- Prompt para limpieza/orden de carpetas.
- Prompt para IA avanzada de composición/optimización.
- Scripts Git Bash para setup, checkpoints, import de Arena, experimentos IA y publicación a GitHub.
- Script Python inicial de limpieza en modo dry-run.

## Automatizaciones registradas

### Flyers de eventos

```txt
Download Instagram photo
> droplet Photoshop
> Photoshop exporta JPG
> Blender usa JPG
> composición 3D con colores predominantes
> export final
> envío al jefe de eventos
```

### Slowmo Blender + After Effects

```txt
Blender
> separar elementos/fondo/vfx
> time stretching
> exportar rangos de frames slowmo
> renombrar exports
> ordenar carpetas para After Effects
> consolidar frames como video
> eliminar EXR/PNG pesados después de validar
```

## Nueva idea integrada: IA avanzada para optimización

Cuando exista acceso a una IA más poderosa o moderna, se usará como consultor externo temporal para analizar:

- composición visual
- contexto
- jerarquía
- copy
- estilo
- automatización
- orden técnico
- scripts

Pero siempre con control de versiones:

```txt
main = versión estable
ai-optimizacion/... = rama experimental
```

## Flujo IA avanzada

1. Guardar checkpoint estable.
2. Crear rama experimental con `scripts/git_ai_experiment.sh`.
3. Preparar paquete mínimo para la IA.
4. Pedir diagnóstico y propuestas.
5. Aplicar cambios en rama experimental.
6. Comparar antes/después.
7. Fusionar a `main` solo si mejora.
8. Si no mejora, volver a `main` y dejar el experimento documentado.

## Scripts importantes

### Inicio rápido después de descargar workspace

```bash
bash START_HERE_GITBASH.sh
```

### Publicar/actualizar GitHub con URL

```bash
bash scripts/publish_to_github.sh https://github.com/TU_USUARIO/TU_REPO.git "checkpoint inicial"
```

### Checkpoint normal

```bash
bash scripts/git_checkpoint.sh "mensaje del checkpoint"
```

### Experimento IA avanzada

```bash
bash scripts/git_ai_experiment.sh "nombre experimento"
```

### Importar workspace Arena ZIP

```bash
bash scripts/import_arena_workspace.sh /c/Users/TU_USUARIO/Downloads/workspace.zip
```

## Próximo paso recomendado

1. Descargar workspace desde Arena.
2. Extraer carpeta `ai-workflow-checkpoints` en el PC.
3. Crear repo privado en GitHub.
4. Abrir Git Bash dentro de la carpeta.
5. Ejecutar:

```bash
bash START_HERE_GITBASH.sh
```

6. Pegar la URL del repo cuando el script la pida.
7. Confirmar que se subió a GitHub.
8. Compartir el link del repo con otra IA usando el prompt `prompts/continuar_desde_checkpoint.md`.

## Prompt corto para continuar en otro chat

```md
Lee este repo y continúa desde el checkpoint más reciente. Primero revisa:

1. context/MASTER_CONTEXT.md
2. context/TOOLS_INVENTORY.md
3. docs/PRODUCCION_TECNICA.md
4. docs/FLUJOS_ASISTENTES_AGENTES.md
5. docs/FLUJO_IA_AVANZADA_OPTIMIZACION.md
6. checkpoints/ más reciente

No empieces desde cero. Resume el estado actual, identifica lo que quedó a medias y propone el siguiente paso concreto.
```
