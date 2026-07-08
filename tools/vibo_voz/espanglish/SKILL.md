---
name: espanglish
description: |
  Translate Spanish to hypercompressed format, process efficiently, return in Spanish.

  Use this skill whenever you write a Spanish prompt. Espanglish converts your Spanish to
  ultra-compact notation (40-50% fewer tokens than Spanish, 15-25% fewer than English),
  Claude processes the compressed version, and returns the full response in Spanish.

  Triggers: Spanish prompts, questions in Spanish, analysis in Spanish, documentation in Spanish.
  Token savings: 40-50% vs natural Spanish, 15-25% vs English natural.
---

# Espanglish Optimizer

## Como funciona

1. **Recibe input en espanol** — cualquier prompt, cualquier extension, cualquier dominio
2. **Convierte a formato hipercomprimido** — elimina toda redundancia, usa notacion estructurada
3. **Claude procesa version comprimida** — 40-50% menos tokens que espanol, 15-25% vs ingles
4. **Devuelve respuesta en espanol** — calidad completa, nada perdido

## Reglas de compresion

### Se elimina (sin perdida de contenido)
- Articulos (el, la, un, una) cuando el contexto es claro
- Conjugaciones verbales -> forma base + indicadores de contexto
- Inflexiones de adjetivos -> forma raiz
- Palabras de relleno ("bueno", "entonces", "digamos")
- Contexto repetido
- Amabilidades de sobra

### Se preserva
- Todos los terminos tecnicos, nombres de variables, rutas
- Numeros especificos, fechas, montos
- Muestras de codigo (exactas)
- Intencion principal y matices
- Ejemplos proporcionados
- Casos edge y restricciones

## Formato ejemplo

**Input en espanol:**
```
Mira, lo que quiero hacer es crear un script en Python que lea un archivo CSV,
verdad? Despues, lo que necesito es extraer las columnas A y C, y guardar el
resultado en un archivo nuevo. Como deberia hacerlo?
```

**Formato hipercomprimido:**
```
task: csv_extract
input: file.csv
extract_cols: [A, C]
output: new.csv
lang: python
req: script
```

**Ahorro de tokens:** ~45% (vs espanol natural) | ~18% (vs ingles natural)

## Contenido mixto (codigo + espanol)

- Bloques de codigo: preservados exactamente
- Rutas/URLs: sin cambios
- Narrativa en espanol: comprimida a notacion estructurada
- Respuesta: espanol completo

## Cuando NO comprimir

Auto-skip si:
- Input ya esta en ingles
- Input es codigo puro (sin espanol)
- Oracion simple muy corta
