# Herramienta — flyer_eventos

Estado: flujo base funcional / en mejora gradual
Prioridad: alta

## Objetivo

Ordenar y acelerar el flujo de flyers para eventos sin quitar control manual al diseñador.

El flujo real parte muchas veces desde un correo del jefe que contiene uno o varios links de Instagram. Cada link apunta al flyer base que será usado como referencia/input.

## Idea

```txt
correo con links Instagram
> extraer links
> crear proyecto por link
> guardar manifest
> marcar revisión manual
> preparar input
> Photoshop manual/semi-automático
> Blender manual/semi-automático
> export final para jefe
```

## Información que interesa rescatar

- nombre del evento
- productora / usuario que publicó
- lugar o venue
- fecha
- tipo de publicación: post, reel, tv
- si parece imagen/carrusel/video
- si requiere descarga manual

## Casos especiales

- Post normal `/p/`: puede ser imagen o carrusel.
- Reel `/reel/`: probablemente video.
- TV `/tv/`: probablemente video.
- Perfil privado / shadowban / login requerido: descarga manual.
- Flyer sin ubicación escrita: queda pendiente para revisión manual.

## Estructura de proyecto

```txt
projects/flyer_eventos/YYYY-MM-DD_nombre/
├─ input/
├─ working/
├─ exports/
├─ refs/
├─ manifest.json
└─ README.md
```

## Scripts actuales

Crear proyecto manual:

```bash
bash scripts/new_flyer_evento.sh "nombre evento"
```

Crear proyectos desde correo:

```bash
py scripts/flyer_from_email.py "inbox/correo_prueba.txt"
```

Listar proyectos:

```bash
bash scripts/flyer_list.sh
```

Último proyecto:

```bash
bash scripts/flyer_latest.sh
```

Setear imagen demo en último proyecto:

```bash
bash scripts/flyer_set_input_latest_demo.sh
```

Ver estado del último proyecto:

```bash
bash scripts/flyer_status_latest.sh
```

Generar índice de proyectos:

```bash
bash scripts/flyer_index.sh
```

Abrir último proyecto en Explorer:

```bash
bash scripts/flyer_open_latest.sh
```

## Estado actual

- [x] Crear proyecto manual.
- [x] Crear carpetas con `.gitkeep`.
- [x] Copiar imagen input demo.
- [x] Actualizar `manifest.json`.
- [x] Listar proyectos.
- [x] Detectar último proyecto.
- [x] Leer correo `.txt`.
- [x] Extraer links Instagram.
- [x] Detectar tipo `/p/`, `/reel/`, `/tv/`.
- [x] Guardar `media_guess`.
- [x] Marcar revisión manual.
- [x] Aplicar mejoras por `_airdrop/`.
- [ ] Evitar duplicados por URL/shortcode.
- [ ] Preparar descarga manual guiada.
- [ ] Extraer colores dominantes.
- [ ] Preparar salida Photoshop.
- [ ] Preparar integración Blender.

## Reglas

- No automatizar Photoshop/Blender todavía.
- No borrar archivos sin confirmación.
- No intentar saltar privacidad/login de Instagram.
- Si una publicación no se puede descargar, marcar `manual_download_needed`.
- Cada cambio debe terminar en checkpoint.
