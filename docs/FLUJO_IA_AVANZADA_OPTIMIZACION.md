# Flujo — IA avanzada para optimización visual/composición

Fecha: 2026-06-12

## Objetivo

Tener una opción especial para cuando exista acceso temporal a una IA más poderosa/moderna capaz de analizar contexto, composición visual, jerarquía, copy, layout, branding o mockups.

La IA avanzada no debe reemplazar el flujo base. Debe funcionar como una capa de revisión/optimización sobre una versión ya guardada.

---

## Principio de seguridad

Antes de pedir cambios fuertes a una IA avanzada:

```txt
Guardar versión actual en Git
Crear rama/branch experimental
Crear paquete de revisión
Pedir análisis y propuesta
Aplicar cambios de forma controlada
Comparar antes/después
Merge solo si mejora
```

GitHub mantiene la versión anterior mediante commits y ramas.

---

# Flujo recomendado

## 1. Congelar versión actual

```bash
bash scripts/git_checkpoint.sh "checkpoint antes de revision IA avanzada"
```

## 2. Crear branch experimental

```bash
git checkout -b ai-optimizacion/nombre-proyecto
```

O usando script:

```bash
bash scripts/git_ai_experiment.sh "nombre-proyecto"
```

## 3. Preparar paquete para IA avanzada

El paquete debe incluir lo mínimo necesario:

```txt
- Brief resumido
- Objetivo de la pieza
- Público
- Restricciones de marca
- Preview JPG/PNG actual
- Versiones anteriores si ayudan
- Cambios pedidos por jefe/cliente
- Preguntas concretas
- Qué NO debe cambiar
```

Evitar subir:

```txt
- PSD/AI/INDD pesados
- Archivos privados innecesarios
- Credenciales
- Material sensible del cliente
```

## 4. Pedir análisis, no solo rediseño

La IA debe responder con:

```txt
Diagnóstico
Problemas priorizados
Cambios propuestos
Riesgos
Qué mantener
Plan de implementación
Checklist de comparación
```

## 5. Aplicar cambios

Aplicar cambios manualmente o mediante scripts, pero mantenerlos en la rama experimental.

## 6. Comparar antes/después

Criterios:

- ¿Mejoró la jerarquía?
- ¿Se entiende más rápido?
- ¿El CTA es más claro?
- ¿Mantiene marca?
- ¿Se ve mejor en mobile?
- ¿El jefe/cliente lo entenderá mejor?
- ¿Aumentó complejidad innecesaria?

## 7. Decidir

### Si mejora

```bash
git checkout main
git merge ai-optimizacion/nombre-proyecto
bash scripts/git_checkpoint.sh "merge optimizacion IA avanzada nombre-proyecto"
```

### Si no mejora

```bash
git checkout main
```

La rama queda como intento documentado.

---

# Tipos de uso

## Optimización visual

Para flyers, posts, stories, composiciones 3D, layouts y mockups.

## Optimización de copy

Para titulares, CTA, texto de venta, tono de marca y reducción de texto.

## Optimización de flujo

Para que una IA revise una automatización y proponga simplificar pasos.

## Optimización técnica

Para scripts Python, JSX, Blender, After Effects o pipelines de carpetas.

---

# Regla importante

La IA avanzada puede sugerir cambios, pero el sistema debe preservar:

```txt
Versión anterior
Motivo del cambio
Archivos modificados
Antes/después
Decisión final
```
