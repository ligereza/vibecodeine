# Errores / pendientes — portfolio-auto

Fecha: 2026-06-12

## ERROR-PROD-001 — Automatización incompleta Curator/n8n

### Estado

Abierto.

### Descripción

`CURATOR.html` prepara y envía un payload a un webhook n8n, pero el flujo completo n8n → GitHub API → commit en `data/works.json` → deploy no está confirmado como funcional.

### Riesgo

- El usuario cree que el panel publica obras, pero puede fallar silenciosamente si n8n no está configurado.
- Puede exponer webhook si se publica mal.
- Puede romper `works.json` si no hay validación.

### Próxima acción

Crear primero un validador local de payload/works.json antes de conectar n8n.

---

## ERROR-PROD-002 — Assets/obras reales no integradas

### Estado

Abierto.

### Descripción

`data/works.json` usa placeholders externos, no obras reales optimizadas dentro de `assets/works/`.

### Riesgo

- El portfolio no representa el trabajo real.
- Dependencia de URLs externas.
- Carga/performance variable.
- Falta pipeline de thumbnails/posters.

### Próxima acción

Crear pipeline:

```txt
assets originales
> optimizar previews
> generar metadata
> crear entrada JSON
> validar works.json
> commit/deploy
```

---

## ERROR-PROD-003 — Falta integración con sistema de checkpoints

### Estado

Abierto.

### Descripción

`README-AGENTS.txt` contiene memoria útil, pero no está sincronizado con `ai-workflow-checkpoints`.

### Próxima acción

Crear checkpoint puente y decidir si futuras decisiones viven en ambos repos o solo se reflejan mediante resúmenes.
