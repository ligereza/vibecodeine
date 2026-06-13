# flujo — Dimensiones del Orden

Repositorio para ordenar proyectos creativos, automatizaciones e IAs.

Funciona como una **zapatilla/alargador organizador**: conecta proyectos, herramientas, contexto y checkpoints en un solo lugar.

No reemplaza el trabajo manual. Ayuda a no empezar desde cero.

## Entrada rápida

Si eres una IA o asistente, lee primero:

```txt
PARA_IA.md
```

Luego lee:

```txt
docs/DIMENSIONES_DEL_ORDEN.md
context/ESTADO.md
tools/flyer_eventos/SPEC.md
```

## Herramienta activa

```txt
flyer_eventos
```

## Comandos actuales

Crear proyecto flyer:

```bash
bash scripts/new_flyer_evento.sh "nombre evento"
```

Listar flyers:

```bash
bash scripts/flyer_list.sh
```

Ver último flyer:

```bash
bash scripts/flyer_latest.sh
```

Setear input demo:

```bash
bash scripts/flyer_set_input_latest_demo.sh
```

Ver status:

```bash
bash scripts/flyer_status_latest.sh
```

Ver estado general del orden:

```bash
bash scripts/orden_status.sh
```

Guardar avance:

```bash
bash scripts/checkpoint.sh "mensaje"
```

## Reglas

- Avanzar paso a paso.
- No subir archivos pesados.
- No automatizar Photoshop/Blender todavía.
- No borrar sin confirmación.
- Usar `py` para Python en Windows.
- Después de cada mejora, hacer checkpoint.
