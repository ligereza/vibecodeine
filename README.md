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

Crear proyecto flyer manual:

```bash
bash scripts/new_flyer_evento.sh "nombre evento"
```

Crear proyectos desde correo con links de Instagram:

```bash
py scripts/flyer_from_email.py "inbox/correo_prueba.txt"
```

Listar flyers:

```bash
bash scripts/flyer_list.sh
```

Ver último flyer:

```bash
bash scripts/flyer_latest.sh
```

Setear input demo en último flyer:

```bash
bash scripts/flyer_set_input_latest_demo.sh
```

Ver status del último flyer:

```bash
bash scripts/flyer_status_latest.sh
```

Generar índice de flyers:

```bash
bash scripts/flyer_index.sh
```

Abrir último flyer en Explorer:

```bash
bash scripts/flyer_open_latest.sh
```

Ver estado general del orden:

```bash
bash scripts/orden_status.sh
```

Aplicar mejoras por airdrop:

```bash
bash scripts/apply_airdrop.sh --dry-run
bash scripts/apply_airdrop.sh --apply
```

Guardar avance:

```bash
bash scripts/checkpoint.sh "mensaje"
```

## Flujo actual recomendado

```bash
py scripts/flyer_from_email.py "inbox/correo_prueba.txt"
bash scripts/flyer_list.sh
bash scripts/flyer_index.sh
bash scripts/flyer_status_latest.sh
bash scripts/checkpoint.sh "mensaje"
```

## Reglas

- Avanzar paso a paso.
- No subir archivos pesados.
- No automatizar Photoshop/Blender todavía.
- No borrar sin confirmación.
- Usar `py` para Python en Windows.
- Después de cada mejora, hacer checkpoint.
