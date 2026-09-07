# Verificación aritmética de presupuestos y topes

Generado el 2026-09-06 recalculando los CSV de esta carpeta. Cada subtotal
se recomputó como cantidad x precio unitario y se comparó con el valor escrito.

## `01_ama_amoedo.csv`

| Categoría | Subtotal (USD) | % del total |
|---|---:|---:|
| Personal | 8,700 | 87.05% |
| Operacion | 1,294 | 12.95% |
| **TOTAL** | **9,994** | 100% |

- Subtotales mal calculados: **0** 
- Total 9,994 USD contra tope 10,000 USD: **CUMPLE**

## `02_fondart_creacion.csv`

| Categoría | Subtotal (CLP) | % del total |
|---|---:|---:|
| Personal | 11,450,000 | 63.61% |
| Operacion | 3,100,000 | 17.22% |
| Inversion | 3,130,000 | 17.39% |
| Imprevistos | 320,000 | 1.78% |
| **TOTAL** | **18,000,000** | 100% |

- Subtotales mal calculados: **0** 
- Total 18,000,000 CLP contra tope 18,000,000 CLP: **CUMPLE**
- Asignación del responsable 7,000,000 = **38.89%** del solicitado (tope 40%): **CUMPLE**
- Imprevistos 320,000 = **1.78%** del solicitado (tope 2%): **CUMPLE**
- Ítem Inversión: 3,130,000 CLP — permitido, con destino posterior declarado en cada fila

## `03_fondart_formativas.csv`

| Categoría | Subtotal (CLP) | % del total |
|---|---:|---:|
| Personal | 9,940,000 | 66.71% |
| Operacion | 4,696,000 | 31.52% |
| Imprevistos | 264,000 | 1.77% |
| **TOTAL** | **14,900,000** | 100% |

- Subtotales mal calculados: **0** 
- Total 14,900,000 CLP contra tope 14,900,000 CLP: **CUMPLE**
- Asignación del responsable 5,400,000 = **36.24%** del solicitado (tope 40%): **CUMPLE**
- Imprevistos 264,000 = **1.77%** del solicitado (tope 2%): **CUMPLE**
- Ítem Inversión: 0 CLP — la línea NO contempla este ítem, debe ser 0

## Supuestos declarados

1. **Honorarios en bruto.** Los valores de honorarios son montos brutos. La
   retención de segunda categoría es de cargo del prestador y no se suma al
   proyecto. La guía oficial de contratación declara **15,25% desde enero de
   2026** y un aumento progresivo **hasta 17% en 2028**; no declara la tasa de
   2027. Antes de firmar convenio corresponde verificar la tasa vigente en el SII.
2. **Contratación laboral.** Si alguna función configura relación laboral
   (subordinación, horario, supervisión), la guía obliga a contrato de trabajo y
   el proyecto debe soportar las cotizaciones del empleador. Eso **aumentaría** el
   costo de esa línea. La forma de contratación de cada rol se decide con la
   persona y no está decidida aquí.
3. **Costo de la garantía fuera del presupuesto.** Las bases exigen caucionar el
   monto total y dicen que el gasto de otorgar la garantía **no puede imputarse al
   proyecto**. La opción más barata es letra de cambio autorizada ante notario. Es
   un desembolso propio del artista y no aparece en ninguna tabla.
4. **Precios de referencia, no cotizaciones.** Toda fila marcada como
   "Referencia" o "Estimacion" en `origen_del_valor` debe reemplazarse por
   cotización antes de enviar en los casos de espacio, sala y equipamiento
   (`RESOLUCIONES_EXTERNAS.md` R-5). Ninguna cifra se presenta como cotización
   obtenida.
5. **Tipo de cambio.** El presupuesto de Ama Amoedo está en dólares porque la beca
   se otorga en dólares. No se convierte a pesos: hacerlo introduciría un supuesto
   de tipo de cambio a enero de 2027 que nadie puede sostener.
6. **Contratación futura, no compromiso confirmado.** Ningún proveedor, espacio ni
   colaborador de estas tablas ha sido contratado ni ha comprometido nada. Son
   costos previstos de contrataciones futuras.
