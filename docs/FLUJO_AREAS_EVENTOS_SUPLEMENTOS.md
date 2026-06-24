# Flujo por areas: EVENTOS y SUPLEMENTOS

Este documento aclara como se conectan los correos con el repo.

## Regla principal

No hace falta que el asunto diga "flujo".

Usaremos asuntos simples:

```txt
Eventos - ...
Suplementos - ...
```

Gmail se procesa por busqueda de asunto:

```txt
subject:eventos    -> EVENTOS
subject:suplementos -> SUPLEMENTOS
```

---

## EVENTOS

### Entrada normal

Correo con asunto que contiene:

```txt
eventos
evento
```

Normalmente trae un link de Instagram.

### Resultado esperado

Google Apps Script crea un Issue:

```txt
[EVENTOS] asunto del correo
```

Labels:

```txt
pedido
area/eventos
estado/por-revisar
gmail
instagram
action/descargar-ig
```

### Trabajo local

Si es link Instagram:

```bash
py -m flujo flyer-import inbox/correo_evento.txt
```

Luego sigue la automatizacion local de carpetas/Photoshop del usuario.

### Casos especiales EVENTOS

EVENTOS tambien puede pedir:

```txt
brief
plano / plano app
SVG
pieza visual
```

En ese caso se crea job normal:

```bash
py -m flujo job new "brief evento" --email inbox/correo_evento.txt
py -m flujo job prepare jobs/<job>
```

---

## SUPLEMENTOS

### Entrada normal

Correo con asunto que contiene:

```txt
suplementos
suplemento
```

Puede ser:

```txt
nuevo pedido
modificacion
correccion
cotizacion
paquete mensual
revision
```

Piezas posibles:

```txt
etiqueta
flyer
pendon
post Instagram
stickers
stand
logo / sello
brief comercial
```

### Resultado esperado

Google Apps Script crea un Issue:

```txt
[SUPLEMENTOS] asunto del correo
```

Labels:

```txt
pedido
area/suplementos
estado/por-revisar
gmail
```

### Trabajo local

Abrir hub:

```bash
py -m flujo app
```

O crear intake/job:

```bash
py -m flujo intake json inbox/pedido_suplementos.json
```

Cotizacion multiformato:

```bash
py -m flujo brief paquete-cotizacion jobs/<job>
```

---

## Apps Script properties

```txt
GITHUB_TOKEN = github_pat_...
GITHUB_REPO = ligereza/vibecodeine
GMAIL_LABEL_DONE = flujo-procesado
MAX_THREADS = 10
GMAIL_ROUTES = {subject:eventos subject:evento}|EVENTOS|pedido,area/eventos,estado/por-revisar,gmail,instagram,action/descargar-ig;{subject:suplementos subject:suplemento}|SUPLEMENTOS|pedido,area/suplementos,estado/por-revisar,gmail
```

Solo necesitas crear esta etiqueta Gmail:

```txt
flujo-procesado
```

El sistema usa asunto, no etiquetas de entrada.

---

## Si algun dia prefieres etiquetas

Tambien funciona:

```txt
label:flujo-eventos|EVENTOS|pedido,area/eventos,estado/por-revisar,gmail,instagram,action/descargar-ig;label:flujo-suplementos|SUPLEMENTOS|pedido,area/suplementos,estado/por-revisar,gmail
```

Pero por ahora la recomendacion es asunto:

```txt
Eventos - ...
Suplementos - ...
```

---

## Proxima mejora

```bash
py -m flujo issue import <numero-o-url>
```

Reglas esperadas:

```txt
Issue [EVENTOS] + instagram -> preparar descarga
Issue [SUPLEMENTOS] -> crear job/intake/cotizacion
```
