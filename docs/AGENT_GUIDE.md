# AGENT_GUIDE — flujo (Actualizado)

> Para IAs que trabajan en este repo. Lee esto primero.

**Repo:** `flujo` — **arte + automatización + trabajo real**
**Dueño:** Diseñador y artista visual en ONG "Reduciendo Daño" + proyectos personales.

## Contexto importante del trabajo real

Este repo no es solo una herramienta técnica. Es la **base de trabajo portable** del usuario. Se usa para:

- Flyers y material visual para la ONG "Reduciendo Daño" (eventos)
- Proyectos personales artísticos (`tapiz` y otros)
- Piezas vectoriales y etiquetas
- Flujo de Instagram → análisis → Photoshop/Illustrator

**Reglas sagradas:**
- **No automatizar** Photoshop, Illustrator ni Blender
- Solo usar **instaloader** para descargar de Instagram
- Mantener varias capas de contexto porque el usuario cambia frecuentemente de IA/chat
- Los checkpoints y el historial son importantes para retomar el trabajo

## Stack actual

- Python 3.10+
- `py -m pip install -e .`
- CLI principal: `flujo` (Typer)
- Descarga IG: **solo instaloader**
- Análisis: colores + OCR opcional
- Export: ZIP + preparación para diseño

## Comandos principales (usar estos)

```bash
flujo health
flujo flyer-import inbox/correo.txt
flujo analyze
flujo index --rebuild
flujo export <proyecto>
flujo open <proyecto> --ps     # (próximamente)
flujo open <proyecto> --ai     # (próximamente)
```

## Estructura principal que importa

```
projects/
  flyer_eventos/          ← Trabajo principal ONG
  piezas_vectoriales/     ← Segunda línea de trabajo
  tapiz/                  ← Proyecto personal (mantener)

src/flujo/                ← Paquete CLI moderno (fuente de verdad)

tools/
  flyer_eventos/SPEC.md
  piezas_vectoriales/SPEC.md
```

## Qué NO hacer

- No eliminar `jobs/`, `briefs/` ni `recipes/` sin confirmación (pueden ser ramas en pausa)
- No tocar `projects/tapiz/`
- No automatizar herramientas de diseño
- No romper el sistema de airdrop y checkpoints
- No hacer limpiezas agresivas sin consultar

## Flujo típico de trabajo

1. Correo con links IG → `flujo flyer-import`
2. Descarga automática
3. Análisis de colores → `flujo analyze`
4. Exportar ZIP preparado → `flujo export`
5. (Próximo) Abrir scripts directos en Photoshop/Illustrator

---

**Última actualización:** Junio 2026
Mantener este documento actualizado cuando se hagan cambios importantes.
