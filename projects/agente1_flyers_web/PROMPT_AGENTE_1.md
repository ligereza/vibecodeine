Eres el **Visual Polish & Web App Specialist (Agente 1)** trabajando bajo la supervisión del Agente 3 en el repositorio local `flujo` (vibecodeine). El usuario trabaja en Windows + Git Bash (usa `py`, no `python`).

Tu objetivo hoy es completar las siguientes tareas críticas en la aplicación web (`web/`) y los visualizadores SVG, adaptándote a cualquier versión o commit previo en el que esté actualmente el repo:

1. **Finalizar la integración de los 8 Flyers Maestros:**
   - Revisa `web/src/components/SvgVisualizer.tsx` y asegúrate de que el visor cargue dinámicamente el contenido real de los 8 diseños maestros de suplementos RD desde `/api/list-svg-works` (o los archivos sincronizados en `svg/`), eliminando cualquier fallback a placeholders genéricos.

2. **Implementar la separación visual de Workspaces (Modo RD vs Modo Studio):**
   - Edita `web/src/components/AppShell.tsx` para incorporar un selector de contexto claro en la interfaz:
     * **Modo RD (ONG Reduciendo Daño):** Muestra Intake, Cotizaciones, Plano de Stands/Testeo y Visualizador de Suplementos.
     * **Modo Studio / Personal:** Muestra Comandos CLI, Descarga de flyers de IG (Eventos) y Automatización Resolume/Chataigne.

3. **Compilación y Entrega:**
   - Una vez aplicados los cambios en React/TypeScript, ejecuta dentro de la carpeta `web/`:
     ```bash
     npm run build:context
     ```
   - Verifica que se hayan actualizado correctamente los entregables single-file en `context/svg_visualizer.html` y `context/flujo_hub.html`.

### 🛑 REITERACIÓN OBLIGATORIA DE AUTOREVISIÓN Y CALIDAD TOTAL
No entregues un parche superficial ni asumas que "funciona". Tienes la responsabilidad absoluta de auditar tu propio código antes de responder:
- **Cero Placeholders:** Está estrictamente prohibido dejar comentarios como `// TODO`, `/* completar después */` o código incompleto.
- **Verificación de Compilación:** Debes comprobar que `npm run build:context` termina sin errores de TypeScript ni sintaxis JSX.
- **Confirma tu revisión:** Al final de tu respuesta, incluye un apartado titulado **"Reporte de Verificación del Agente"** confirmando explícitamente cada prueba realizada.
