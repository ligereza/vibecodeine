#!/usr/bin/env python3
"""
Espanglish Optimizer Generator
Comando de voz: "crea la tarea" en vibo_voz (lo llama Gemini como funcion).
Genera un skill que traduce espanol -> formato ultra-comprimido -> Claude procesa
-> responde espanol. Crea archivos en: tools/vibo_voz/espanglish/
"""

import json
import re
import unicodedata
from pathlib import Path


def _slug(nombre: str) -> str:
    """Nombre corto -> slug de carpeta (minusculas, guiones, acentos a ASCII)."""
    s = (nombre or "").strip().lower()
    # folding de acentos: cafe' -> cafe, nino -> nino
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "idea"


def guardar_proyecto(nombre, comprimido, json_str="", idea_original=""):
    """Guarda una idea YA comprimida por REDU en su propia carpeta, lista para que
    Claude la arranque con la skill 'go <nombre>'.
    Crea tools/vibo_voz/proyectos/<slug>/ con idea.md (+ idea.json si aplica)."""
    try:
        slug = _slug(nombre)
        base = Path(__file__).parent / "proyectos" / slug
        base.mkdir(parents=True, exist_ok=True)

        md = [f"# Idea: {nombre}", "",
              f"> Formato ahorrativo generado por REDU (voz). "
              f"Para arrancar en Claude: skill `go {slug}`.", ""]
        if idea_original:
            md += ["## Idea original (voz)", "", idea_original.strip(), ""]
        md += ["## Formato comprimido", "", "```", (comprimido or "").strip(), "```", ""]
        (base / "idea.md").write_text("\n".join(md), encoding="utf-8")

        if (json_str or "").strip():
            (base / "idea.json").write_text(json_str.strip(), encoding="utf-8")

        return {"ok": True, "nombre": nombre, "slug": slug, "ruta": str(base),
                "go": f"go {slug}",
                "mensaje": f"Guardado en proyectos/{slug}. En Claude di: go {slug}"}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e)}


def crear_tarea():
    """
    Genera la estructura del skill Espanglish.
    Se ejecuta desde vibo cuando el usuario dice "crea la tarea".
    Crea todo en tools/vibo_voz/espanglish/ (ruta relativa a ESTE script).
    """

    # Ruta basada en donde esta este script (robusto ante el CWD).
    script_dir = Path(__file__).parent
    base = script_dir / "espanglish"

    try:
        base.mkdir(parents=True, exist_ok=True)

        # 1. SKILL.md
        skill_md = """---
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
"""

        (base / "SKILL.md").write_text(skill_md, encoding="utf-8")

        # 2. Compression rules reference
        rules_md = """# Reglas de Hipercompresion

## Sistema de notacion

### Definicion de tarea
```
task: [verbo_infinitivo]
input: [archivo/dato]
output: [archivo/dato]
lang: [lenguaje_programacion]
cols/rows/fields: [lista]
context: [descripcion_breve]
```

### Operadores
- `->` : produce/resulta en
- `|` : o/alternativa
- `[]` : lista/array
- `{}` : objeto/diccionario
- `+` : y/tambien
- `~` : aproximadamente/similar

### Abreviaturas comunes
- req = requirement/requerimiento
- attr = attribute/atributo
- calc = calculate/calcular
- agg = aggregate/agregar
- comp = compress/comprimir
- fmt = format/formato
- val = validate/validar

## Ejemplos

### Procesamiento de datos
**Natural:** "Necesito agrupar este dataframe por region y calcular el promedio de ventas por region, luego guardar en CSV"
**Comprimido:**
```
task: agg_by_group
input: sales_df
group_by: region
calc: avg(sales)
output: region_avg.csv
```

### Revision de codigo
**Natural:** "Puedes revisar este codigo Python para problemas de seguridad y tambien buscar problemas de rendimiento?"
**Comprimido:**
```
task: code_review
input: code.py
check: [security, performance]
format: markdown_report
```

### Conversion de archivo
**Natural:** "Tengo un archivo Excel con multiples sheets. Necesito convertir la primera hoja a formato CSV"
**Comprimido:**
```
task: convert
input: data.xlsx[0]
format: csv
output: data.csv
```

## Reglas principales

1. **Omitir sujetos cuando es claro por contexto**
   - "Necesito" -> solo la tarea
   - "Puedes" -> omitir

2. **Usar imperativo/infinitivo para acciones**
   - "extraer columnas" -> `extract_cols`
   - "deberia calcular" -> `calc`

3. **Agrupar informacion relacionada**
   - Condiciones juntas
   - Separar conceptos con saltos de linea

4. **Preservar especificidad**
   - "alrededor de 100" -> `~100`
   - "columnas A y C" -> `cols: [A, C]`
   - "ingles o espanol" -> `lang: [en, es]`

5. **Un concepto por linea**
   - Facil de parsear
   - Estructura clara
"""

        (base / "references").mkdir(exist_ok=True)
        (base / "references" / "compression_rules.md").write_text(rules_md, encoding="utf-8")

        # 3. Evaluation set
        evals = {
            "skill_name": "espanglish",
            "evals": [
                {
                    "id": 1,
                    "name": "technical-task-verbose",
                    "prompt": "Mira, tengo este problema que lleva dias sin resolver. Estoy intentando crear un script en Python para leer un archivo CSV, y bueno, despues procesarlo. Lo que quiero hacer es, en realidad, extraer ciertas columnas especificas - columnas A y C - y luego guardar el resultado en un archivo nuevo. Como deberia hacerlo exactamente? Necesito que sea reproducible.",
                    "expected_output": "Python script que lee CSV, extrae columnas A+C, guarda en archivo nuevo. Input comprimido a ~50% del original. Respuesta en espanol."
                },
                {
                    "id": 2,
                    "name": "data-analysis-with-context",
                    "prompt": "Tengo un dataframe de pandas que se llama 'ventas' y bueno, lo que quiero es, digamos, calcular el promedio de ventas por region. El dataframe tiene columnas: ['region', 'mes', 'ventas']. La verdad es que necesito agrupar por region y sacar el promedio. Despues, necesito guardar el resultado en un CSV llamado 'promedio_ventas.csv'. Como lo hago?",
                    "expected_output": "Solucion pandas con groupby+mean y export a CSV. Compresion ~45%. Respuesta en espanol."
                },
                {
                    "id": 3,
                    "name": "conceptual-explanation",
                    "prompt": "Tengo una duda conceptual. Estoy aprendiendo sobre tokens en modelos de lenguaje, verdad? Y bueno, no termino de entender por que el espanol gasta mas tokens que el ingles. Es decir, cual es la razon exacta? Ademas, hay estrategia para minimizar tokens cuando trabajo en espanol?",
                    "expected_output": "Explicacion de eficiencia de tokens, espanol vs ingles vs hipercomprimido. Compresion ~35%. Respuesta completa en espanol."
                }
            ]
        }

        (base / "evals").mkdir(exist_ok=True)
        (base / "evals" / "evals.json").write_text(json.dumps(evals, indent=2, ensure_ascii=False), encoding="utf-8")

        # 4. README
        readme = """# Espanglish Optimizer - Skill de Cowork

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
"""

        (base / "README.md").write_text(readme, encoding="utf-8")

        resultado = {
            "ok": True,
            "mensaje": "[OK] Skill 'Espanglish' creado exitosamente",
            "ubicacion": str(base),
            "archivos": [
                "SKILL.md",
                "evals/evals.json",
                "references/compression_rules.md",
                "README.md"
            ]
        }

        print(f"\n[OK] Espanglish generado en: {base}")
        print("  - SKILL.md")
        print("  - evals/evals.json")
        print("  - references/compression_rules.md")
        print("  - README.md\n")

        return resultado

    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e)}


# Declaracion para que Gemini (REDU) sepa que puede llamar a esta funcion por voz.
# Perfil unico REDU: su unica herramienta es guardar la idea comprimida.
DECLARACIONES = [
    {
        "name": "guardar_proyecto",
        "description": (
            "Guarda una idea YA comprimida (formato ahorrativo) en su carpeta "
            "tools/vibo_voz/proyectos/<nombre>/ para arrancarla luego en Claude con "
            "'go <nombre>'. Llamar tras comprimir la idea que explico el usuario."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "nombre": {"type": "string", "description": "Nombre corto de la idea (1-3 palabras)."},
                "comprimido": {"type": "string", "description": "La idea en notacion comprimida (task:/input:/output:/...)."},
                "json_str": {"type": "string", "description": "Opcional: version JSON del formato."},
                "idea_original": {"type": "string", "description": "Opcional: la idea en espanol tal como la dijo el usuario."},
            },
            "required": ["nombre", "comprimido"],
        },
    },
]

# Exportar funciones ejecutables para vibo. crear_tarea se conserva (genera el skill
# Espanglish de referencia) pero ya no se declara: REDU usa guardar_proyecto.
FUNCIONES = {
    "guardar_proyecto": guardar_proyecto,
    "crear_tarea": crear_tarea,
}

if __name__ == "__main__":
    resultado = crear_tarea()
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
