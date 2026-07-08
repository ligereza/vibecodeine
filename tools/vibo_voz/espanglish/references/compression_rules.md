# Reglas de Hipercompresion

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
