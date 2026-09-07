# Solicitud de espacio — texto listo para copiar y enviar

> **No enviado. No existe ninguna cotización ni compromiso.** Este archivo es el
> texto que el titular puede copiar tal cual. Pedir una **cotización** suele ser
> más rápido que pedir una carta de compromiso, y las bases aceptan cualquiera de
> las dos.

---

## A · Correo para pedir COTIZACIÓN — la vía rápida

Copiar desde aquí. Reemplazar sólo lo que está entre corchetes.

---

**Asunto:** Cotización de arriendo de espacio — [4 semanas, septiembre-octubre 2027 / 8 sesiones, agosto-noviembre 2027]

Estimados:

Quisiera cotizar el arriendo de un espacio en [NOMBRE DEL ESPACIO] para un
proyecto cultural que postulo al Fondart Regional 2027.

**Lo que necesito cotizar:**

[OPCIÓN EXHIBICIÓN]
- Uso de sala durante **4 semanas continuas**, entre [mes] y [mes] de 2027.
- Superficie aproximada: la de una mesa de trabajo más circulación de visitantes.
- Requiere conexión eléctrica corriente. Sin obra civil, sin perforaciones y sin
  fijaciones: se monta y desmonta sin alterar el lugar.
- Horario de apertura al público según el del propio espacio.

[OPCIÓN LABORATORIO]
- Sala para **8 sesiones de 3 horas**, para 16 personas, entre [mes] y [mes] de 2027.
- Requiere mesas, sillas y conectividad a internet.
- Adicionalmente, **12 jornadas** de una sala pequeña para tutorías individuales.

**Para la postulación necesito que la cotización indique:** nombre y dirección
del espacio, el periodo, qué incluye el valor y el valor total con impuestos si
corresponde. Con una cotización en PDF o correo formal es suficiente.

Le agradezco indicarme también si el espacio tiene acceso para personas con
movilidad reducida y su cercanía al transporte público, porque son criterios de
accesibilidad del proyecto.

Quedo atento/a.

[NOMBRE] · [CORREO] · [TELÉFONO]

---

## B · Carta de compromiso — si el espacio prefiere comprometerse en vez de cotizar

Texto para que **el espacio** lo emita en su papelería y lo firme. No es un
documento que el titular pueda firmar por su cuenta.

---

**CARTA DE COMPROMISO DE ESPACIO**

[Ciudad], [fecha]

Señores
Secretaría Regional Ministerial de las Culturas, las Artes y el Patrimonio
Región de [REGIÓN]

Yo, [NOMBRE], cédula de identidad N° [RUT], en mi calidad de [director/a ·
administrador/a · encargado/a] de [NOMBRE DEL ESPACIO], domiciliado en
[DIRECCIÓN], declaro que:

1. Conozco el proyecto **"[NOMBRE DEL PROYECTO]"**, presentado por [RESPONSABLE],
   RUT [RUT], a la línea [Creación Artística / Actividades Formativas] del
   Fondart Regional, Concurso 2027.

2. [NOMBRE DEL ESPACIO] **se compromete**, en caso de que el proyecto resulte
   seleccionado, a:
   - facilitar [sala / superficie / m²] durante [N] [semanas / sesiones], entre
     [mes] y [mes] de 2027;
   - proveer conexión eléctrica adecuada y condiciones de seguridad para las
     actividades descritas;
   - permitir el acceso de público en los horarios de funcionamiento del espacio;
   - [difundir la actividad por sus canales / co-organizar la apertura /
     facilitar mobiliario] — *dejar sólo lo que el espacio efectivamente acepte*;
   - [gratuitamente / por un valor de $__________] — *marcar lo que corresponda*.

3. Este compromiso está **sujeto a que el proyecto resulte seleccionado** y a la
   suscripción del acuerdo operativo correspondiente.

Firma: ______________________
Nombre / Cargo / Institución / RUT:
Correo electrónico y teléfono:

---

## Qué hacer con la respuesta

| Lo que llegue | Qué hacer |
|---|---|
| **Si llegara una cotización con valor** | Adjuntar al FUP. Copiar el valor a `presupuestos/02_fondart_creacion.csv` línea `O-CRE-01` o `presupuestos/04_fondart_formativas.csv` línea `O-FOR-01`, y volver a ejecutar `verificador/verificar_presupuestos.py` |
| **Si llegara una carta con firma y uso gratuito** | Adjuntar al FUP. En el presupuesto, bajar esa línea a cero y reasignar dentro del mismo ítem Operación |
| **Si llegara una carta con firma y con valor** | Igual que la cotización |
| **Respuesta informal por correo, sin firma** | **No adjuntar.** No es ninguno de los dos documentos que las bases aceptan |
| **Sin respuesta antes del cierre** | Ver abajo |

## Si no llega nada a tiempo

En orden de preferencia:

1. **Postular Difusión en lugar de Creación.** Sus bases eximen este documento
   cuando *"el soporte lo constituya un medio de difusión no existente (ejemplo:
   un sitio web) y que será desarrollado por el proyecto en concurso"*. Es la
   razón por la que Difusión es la Fondart recomendada del paquete.
2. **Cotizar en un espacio de arriendo comercial.** Cumple igual y no requiere
   que nadie se comprometa con el proyecto.
3. **Postular sin el documento.** Es de evaluación, no taxativo: baja el criterio
   Viabilidad (10%) pero **no** deja el proyecto fuera de bases.

Al día de hoy no ha llegado ninguna de las tres: no existe carta ni
cotización de ningún espacio. **Nunca** adjuntar una carta sin firma, ni presentar una respuesta informal como
compromiso, ni declarar en el FUP un espacio que no respondió.
