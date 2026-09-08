# Cómo usar la planilla de compromisos de asistencia

Archivo: `FORMATO_COMPROMISOS_FORMativas_15_FILAS.csv` — **15 filas vacías**, sin
nombres, RUT ni firmas inventadas.

## Para qué es

Las bases de Actividades Formativas exigen, como documento de evaluación, un
*"documento que dé cuenta del compromiso de asistencia a la actividad formativa,
**de al menos 15 personas**"*. Piden **un documento**, no quince cartas: una
planilla con quince filas firmadas cumple y es mucho más rápida de reunir.

## Texto que debe encabezar la planilla al imprimirla

> **COMPROMISO DE ASISTENCIA**
> Laboratorio *Dimensiones del Orden: cómo ordenar un archivo propio*
> Postulación a Fondart Regional 2027, línea Actividades Formativas
> Responsable: [nombre del titular], RUT [RUT]
>
> Las personas que firmamos declaramos conocer el programa formativo y
> comprometemos nuestra asistencia a las ocho sesiones del laboratorio, en caso
> de que el proyecto resulte seleccionado y se ejecute durante 2027 en [comuna,
> región]. Declaramos ser mayores de 18 años y mantener un archivo de trabajo
> propio. Entendemos que la actividad es **gratuita** y que **no conduce a grado
> académico** ni entrega certificación académica.

## Columnas

| Columna | Qué va | Obligatoria |
|---|---|---|
| `n` | 1 a 15, ya numerado | — |
| `nombre_completo` | nombre y apellidos | **sí** |
| `rut` | formato 12.345.678-9 | **sí** |
| `correo` | contacto | **sí** |
| `telefono` | contacto | no |
| `disciplina` | artes visuales, diseño, artesanía, arquitectura u otra | **sí** |
| `tiene_archivo_propio_si_no` | `si` o `no` — es el criterio de participación | **sí** |
| `mayor_de_18_si_no` | `si` o `no` — las bases lo exigen | **sí** |
| `comuna` | debe estar en la región de ejecución | **sí** |
| `fecha_firma_aaaa_mm_dd` | fecha en que firma | **sí** |
| `firma_marcar_x` | `x` en la versión digital; firma manuscrita en la impresa | **sí** |
| `observaciones` | libre | no |

## Cómo reunirlas en pocos días

1. **Empezar por quienes ya tienen el problema.** El criterio es tener archivo,
   no tener método: cualquier colega con años de trabajo acumulado califica.
2. **Explicar que el compromiso es condicional.** Sólo obliga si el proyecto se
   adjudica, y la ejecución es en 2027. Nadie se compromete a nada inmediato.
3. **Firma digital sirve.** Las bases no exigen notaría para este documento.
4. **Reunir dieciocho, no quince.** El mínimo es quince y siempre alguien se cae.

## Validación antes de adjuntar

```bash
python3 - <<'P'
import csv
f="FORMATO_COMPROMISOS_FORMativas_15_FILAS.csv"
r=[x for x in csv.DictReader(open(f,encoding="utf-8"))]
oblig=["nombre_completo","rut","correo","disciplina",
       "tiene_archivo_propio_si_no","mayor_de_18_si_no","comuna",
       "fecha_firma_aaaa_mm_dd","firma_marcar_x"]
completas=[x for x in r if all(x[c].strip() for c in oblig)]
print(f"filas totales: {len(r)}   completas: {len(completas)}")
menores=[x['n'] for x in completas if x['mayor_de_18_si_no'].strip().lower()!='si']
sinarch=[x['n'] for x in completas if x['tiene_archivo_propio_si_no'].strip().lower()!='si']
if menores: print("ATENCION filas que no declaran mayoria de edad:", menores)
if sinarch: print("AVISO filas que no declaran archivo propio:", sinarch)
print("CUMPLE el minimo de 15" if len(completas)>=15 else
      f"NO cumple: faltan {15-len(completas)} firmas")
P
```

## Si no se reúnen a tiempo

**Postular igual.** El documento es de evaluación: su ausencia baja el criterio
Viabilidad, que pondera 10% en esta línea y es el de menor peso. Perder diez
puntos es preferible a no postular. Lo que **no** corresponde es declarar
participantes que no firmaron.
