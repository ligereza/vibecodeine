# Compartir el repo con una IA

Fecha: 2026-06-12

## ¿Privado o público?

### Recomendación base: privado

Usa repo privado cuando el proyecto pueda contener:

- nombres de clientes o jefe
- briefs reales
- fotos descargadas o referencias con derechos
- precios, campañas o datos internos
- rutas locales de tu PC
- respuestas de IA con información sensible
- scripts que revelen tu estructura de trabajo
- archivos de diseño o previews que no quieres publicar

### Cuándo puede ser público

Puede ser público si haces una versión sanitizada, sin datos privados, por ejemplo:

- solo estructura del sistema
- prompts genéricos
- scripts reutilizables
- documentación sin nombres reales
- ejemplos ficticios
- checkpoints limpiados

## Problema importante

Muchas IAs no pueden abrir repos privados aunque les pases el link.

Un link privado sirve para ti y para colaboradores con acceso, pero un chat de IA normalmente no podrá leerlo si no tiene autenticación.

Por eso hay tres formas recomendadas de compartir contexto.

---

# Opción A — Repo público sanitizado

Crear un repo público solo con el sistema limpio:

```txt
ai-workflow-public-context
```

Contenido:

- docs generales
- prompts
- scripts sin datos sensibles
- checkpoints resumidos
- ejemplos ficticios

No incluir:

- clientes reales
- imágenes reales
- briefs privados
- archivos pesados
- rutas personales

## Ventaja

Puedes pasar el link a casi cualquier IA con navegación web.

## Desventaja

Debes cuidar mucho no subir información privada.

---

# Opción B — Repo privado + paquete para IA

Mantienes tu repo privado, pero generas un paquete limpio para subir o pegar a la IA.

Paquete recomendado:

```txt
_ai_share_pack/
├─ MASTER_CONTEXT.md
├─ TOOLS_INVENTORY.md
├─ PRODUCCION_TECNICA.md
├─ FLUJOS_ASISTENTES_AGENTES.md
├─ FLUJO_IA_AVANZADA_OPTIMIZACION.md
├─ CHECKPOINTS_RECIENTES.md
├─ PROMPTS_CLAVE.md
└─ README_PARA_IA.md
```

## Ventaja

Más seguro. Compartes solo lo necesario.

## Desventaja

Tienes que subir archivos o pegar contenido manualmente.

---

# Opción C — Copiar/pegar contexto mínimo

Para chats con poca cuota o sin capacidad de leer archivos, pegas solo:

1. resumen del sistema
2. checkpoint más reciente
3. pregunta concreta

Ejemplo:

```md
Estoy trabajando en un sistema de checkpoints para diseño + IA. Lee este resumen y continúa desde aquí...
```

## Ventaja

Funciona en cualquier chat.

## Desventaja

Menos contexto.

---

# Recomendación para este proyecto

Usar dos niveles:

```txt
Repo privado = memoria completa real
Paquete para IA = contexto limpio compartible
```

Más adelante, si quieres, puedes crear un segundo repo público con una versión sanitizada del sistema.

---

# Script disponible

Para generar un paquete limpio para IA:

```bash
bash scripts/create_ai_share_pack.sh
```

Ese script crea:

```txt
_ai_share_pack/
```

con los archivos más importantes para subirlos a un chat o copiarlos.
