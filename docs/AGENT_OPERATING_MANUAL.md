# AGENT OPERATING MANUAL — flujo (token-efficient)

**Leer esto primero. Solo esto + el hub.**

## Flujo 1: Pedido Reciente (operativo)
Recibes: link del repo + correo o mensaje WhatsApp/Gmail.

**Proceso exacto:**
1. Abre `context/flujo_hub.html`
2. Pega el texto completo en la caja "Pedidos"
3. Pulsa "Generar brief ordenado"
4. Revisa el "Format match" en la salida.
5. Si hay match → genera brief + comando + archivos para AI/PS/Blender usando flujo.
6. Si no hay match →
   - Propón sección nueva mínima en flujo, **o**
   - Agrega tarea clara en LAST_HANDOFF.md

**Salida mínima esperada:**
- Brief estructurado (copia-pega)
- 1-2 comandos exactos
- Nota de herramienta final + flujo
- Decisión: "Usar formato X" o "Nueva sección / tarea de mejora"

## Flujo 2: Mejoras al Repo
Recibes: repo + "continúa con las mejoras".

**Proceso:**
1. Abre el hub + lee LAST_HANDOFF.md
2. Lee este manual
3. Elige 1-2 tareas de la sección de tareas simples
4. Trabaja
5. Actualiza LAST_HANDOFF al final

## Reglas (ambos flujos)

**Delegación de agentes (recomendado):**
- Brand Guardian: asegura que todo use la identidad flujo.
- Pipeline Agent: jobs, renders, export.
- Visual Agent: pulido de HTMLs, tapiz, visualizers (debe verse profesional).
- Future/Integrations: modern tools, tokens, etc.

## Reglas (ambos flujos)
- Windows: `py -m flujo ...`
- Español primero
- Siempre usa flujo
- Archivos finales listos para Illustrator/Photoshop/Blender
- Mantén respuestas cortas. Hub = verdad

## Formatos actuales (chequea rápido)
- flyer 10x14 (illustrator)
- etiqueta 16.5x6.5 (illustrator)
- plano/stand + cotizacion (dual)
- cartelera IG / post (ps + blender)

Si no calza → nueva sección o tarea.

**Este archivo + hub + visualizadores = única fuente para agentes (bajo consumo de tokens).**

El hub hace el matching básico y te da la decisión lista.
- Abre `context/flujo_hub.html`
- Pega pedido → genera brief + match
- Para ver piezas reales: `context/svg_visualizer.html` (embebidos, grupos Eventos/Suplementos, botones Usar como base)
- Para planos: `context/plano_demo.html`

Usa siempre la salida del hub como base. Nunca abras índices de carpetas svg/.
