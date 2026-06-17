# flujo — Dimensiones del Orden

**arte + automatización + trabajo real**

Repo personal de un diseñador y artista visual que trabaja en la ONG "Reduciendo Daño" + proyectos personales.

## Propósito

Este repo existe para:
- Reducir fricción en el flujo de trabajo diario
- Mantener contexto cuando se cambia de máquina o de IA
- Servir como base portable de proyectos creativos

## Flujo principal

```bash
flujo flyer-import inbox/correo.txt
flujo analyze
flujo export <proyecto>
```

## Estructura importante

```
projects/
├── flyer_eventos/        # Trabajo principal (ONG)
├── piezas_vectoriales/   # Segunda línea de trabajo
└── tapiz/                # Proyecto personal (mantener)

src/flujo/                # CLI moderno (fuente de verdad)
```

## Reglas

- No automatizar Photoshop / Illustrator / Blender
- Solo instaloader para Instagram
- Mantener checkpoints y contexto
- Respetar ramas en pausa (`tapiz`, jobs, briefs, etc.)

## Documentación

- `docs/AGENT_GUIDE.md` — Para IAs
- `context/ESTADO.md` — Estado actual
- `docs/AIRDROP.md` — Sistema de airdrop

---

**Versión actual:** camino a v0.15 (Track M)
