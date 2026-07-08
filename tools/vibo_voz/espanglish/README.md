# Espanglish Optimizer - Skill de Cowork

## Carpeta: espanglish/

Creado automaticamente por el comando "crea la tarea" en vibo_voz.

### Archivos generados

```
espanglish/
+-- SKILL.md                    # Definicion del skill
+-- evals/
|   +-- evals.json              # 3 test cases
+-- references/
    +-- compression_rules.md    # Reglas de compresion
```

## Que hacer ahora

1. **Copia estos archivos a Cowork** (o envia a Cauce para procesarlos)
2. **Revisa SKILL.md** para entender el concepto
3. **Lee compression_rules.md** para aprender el formato
4. **Los test cases** estan en evals.json

## Ahorro de tokens esperado

- **vs espanol natural:** 40-50%
- **vs ingles natural:** 15-25%
- **vs ingles comprimido:** ~10-15% adicional

## Proximos pasos

1. Envia estos archivos a Cauce (en Cowork o Claude Code)
2. Cauce crea el skill/artifact final
3. Usalo en Cowork para procesar prompts en espanol

## Como usar Espanglish

Cuando tengas un prompt en espanol:

1. Convierte a formato hipercomprimido (consulta compression_rules.md)
2. Envia a Cauce
3. Recibes respuesta en espanol, procesada con ~40-50% menos tokens

Ejemplo:
```
Input espanol: "Necesito extraer columnas A y C de un CSV..."
-> Formato: task: csv_extract | input: file.csv | cols: [A,C] | output: new.csv
-> Respuesta: Script Python completo en espanol
```
