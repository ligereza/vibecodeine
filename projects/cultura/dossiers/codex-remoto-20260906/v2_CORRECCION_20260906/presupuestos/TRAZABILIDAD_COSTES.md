# Trazabilidad de costes: por qué ningún gasto se paga dos veces

La auditoría marcó como riesgo N2 que hosting, registro documental y desarrollo
aparecieran en varios presupuestos. La v1 respondía "son gastos distintos"
sin poder demostrarlo. La v2 lo demuestra por construcción y lo verifica con
código.

## 1. El mecanismo

Cada línea de cada presupuesto lleva un **`id_coste` único en todo el paquete**,
más cuatro campos que hacen imposible confundir dos gastos parecidos:

| Campo | Para qué sirve |
|---|---|
| `id_coste` | Identificador único. Prefijo por proyecto: `AMA`, `CRE`, `DIF`, `FOR` |
| `actividad` | Qué se hace con ese dinero |
| `periodo` | Cuándo, con mes de inicio y término |
| `producto` | Qué entregable concreto queda |
| `proyecto_que_paga` | Cuál de los cuatro presupuestos lo financia |

`verificador/verificar_presupuestos.py` **falla con código de salida 1** si un
`id_coste` se repite dentro de un archivo o entre archivos distintos. La prueba
negativa `mismo id_coste pagado por dos proyectos` lo comprueba.

## 2. Los tres conceptos que la auditoría señaló, resueltos

### Hosting y dominio — **resuelto eliminándolo, no separándolo**

La v1 tenía hosting en los tres presupuestos y argumentaba que eran dominios
distintos. Era un argumento débil. La v2 lo resuelve de raíz:

| Proyecto | ¿Paga hosting? | Por qué |
|---|---|---|
| Ama Amoedo | **No** | Su producto es el archivo curado, el exportador y un portafolio como artefacto. No publica una superficie en línea. |
| Creación | **No** | La obra funciona local, sin conexión permanente. Es una condición declarada de la instalación, no una omisión. |
| **Difusión** | **Sí, `O-DIF-01`** | Su objeto **es** la superficie pública. Sin hosting no hay proyecto. |
| Formativas | **No** | La guía se publica como documento; no requiere infraestructura propia. |

**Hosting aparece exactamente una vez en todo el paquete.** No hay nada que
separar porque no hay nada repetido.

### Registro documental — separado por producto y periodo

| id_coste | Proyecto | Qué registra | Periodo | Producto |
|---|---|---|---|---|
| `O-CRE-07` | Creación | La instalación montada | 2027-10 | Registro audiovisual de la obra |
| `O-DIF-07` | Difusión | Datos de acceso y circulación | 2027-10 a 2028-02 | Informe de acceso y circulación |
| `O-FOR-06` | Formativas | Las ocho sesiones del laboratorio | 2027-08 a 2027-11 | Registro de las sesiones |

Son tres objetos distintos, en tres periodos distintos, con tres entregables
distintos. Ninguno sustituye a otro y ninguno podría reutilizarse como
verificador del otro.

### Desarrollo — **sólo se financia una vez, en Ama Amoedo**

Esta es la corrección de fondo y responde a la instrucción de no cobrar dos
veces el mismo trabajo por tener un motor común.

| Proyecto | ¿Financia desarrollo del motor? |
|---|---|
| **Ama Amoedo** | **Sí.** `P-AMA-02` construye el exportador archivo→portafolio, que es la brecha verificada. |
| Creación | **No.** Su asignación cubre dirección, diseño de la experiencia, mediación y administración de una obra situada. |
| Difusión | **No.** Su asignación cubre curaduría de la selección, implementación de la superficie y mediación. |
| Formativas | **No.** Su asignación cubre diseño del programa, docencia y tutorías. |

Si Ama Amoedo no se adjudica y sí un Fondart, el exportador **no** se construye
con cargo al Fondart: el proyecto Fondart usa lo que exista y su resultado se
formula sin depender de esa pieza. Está escrito así en cada expediente.

## 3. Sumas por moneda, sin mezclar

**No se suman pesos con dólares en ningún documento de este paquete.** La beca
Ama Amoedo se otorga y se rinde en dólares. Convertirla a pesos exigiría fijar
un tipo de cambio a enero de 2027 que nadie puede sostener, y el resultado sería
una cifra falsamente precisa.

| Proyecto | Total | Moneda | Tope | Holgura |
|---|---:|---|---:|---:|
| Ama Amoedo | 8.734 | USD | 10.000 | 1.266 |
| Creación | 12.090.000 | CLP | 18.000.000 | 5.910.000 |
| Difusión | 8.800.000 | CLP | 18.000.000 | 9.200.000 |
| Formativas | 9.266.000 | CLP | 15.000.000 | 5.734.000 |

**Ninguno agota el máximo.** La v1 pedía $18.000.000 y $14.900.000 porque eran
los topes. La v2 pide lo que cuesta la variante que el titular puede ejecutar,
que es bastante menos. Las bases permiten además que la comisión rebaje hasta un
10% adicional (Anexo 3, §II.5); una solicitud ajustada resiste mejor esa rebaja
que una inflada.

## 4. Supuestos tributarios, sin aplicar una tasa por costumbre

- **Los montos de servicios son brutos.** Cuando un servicio se contrata a
  honorarios, la retención de segunda categoría es de cargo del prestador y no
  se suma al proyecto.
- **La tasa de 2027 no está en las fuentes consultadas.** La guía oficial de
  contratación declara **15,25% desde enero de 2026** y un aumento progresivo
  **hasta 17% en 2028**; no declara 2027. Este paquete **no aplica una tasa
  supuesta**: registra el vacío y remite al SII al momento de emitir la boleta.
- **Relación laboral.** Si alguna contratación configurara subordinación y
  dependencia, la guía obliga a contrato de trabajo y el proyecto debe soportar
  las cotizaciones del empleador, lo que **aumentaría** el costo de esa línea.
  En la variante recomendada —titular solo— no hay ninguna contratación de ese
  tipo: sólo servicios puntuales con entregable.
- **La garantía no está en el presupuesto.** Las bases exigen caucionar el monto
  total y dicen que el gasto de otorgarla **no puede imputarse al proyecto**. La
  opción más barata es letra de cambio autorizada ante notario. Es desembolso
  propio del titular en los proyectos Fondart.

## 5. Origen del valor, declarado línea por línea

La columna `origen_del_valor` admite sólo cuatro valores y el verificador
rechaza cualquier otro:

| Valor | Qué significa | Cuántas líneas |
|---|---|---|
| `tope_normativo` | La cifra viene de un tope de las bases | 6 |
| `referencia` | Precio de mercado observable, sin cotización pedida | 11 |
| `estimacion` | Estimación fundada, todavía sin respaldo de precio | 23 |
| `cotizacion` | Cotización formal obtenida | **0** |

Total: 40 líneas de gasto en los cuatro presupuestos.

**Ninguna línea se presenta como cotización, porque no se pidió ninguna.** Ver
`MATRIZ_REQUISITOS.md` §5 sobre qué exigen realmente las bases en esta materia:
mucho menos de lo que la auditoría supuso.
