# Checkpoint — Privacidad y forma de compartir con IA

Fecha: 2026-06-12

## Pregunta

¿Por qué recomendar repo privado si luego se quiere compartir con una IA?

## Decisión

Usar dos niveles:

```txt
Repo privado = memoria completa real del proyecto
Paquete para IA = contexto limpio compartible
```

## Motivo

El repo puede contener datos sensibles, nombres de clientes, briefs reales, previews, rutas locales, prompts, decisiones internas o scripts que no conviene publicar.

Además, muchas IAs no pueden leer repos privados desde un link. Por eso conviene generar un paquete limpio con solo los archivos necesarios.

## Archivos creados

- `docs/COMPARTIR_REPO_CON_IA.md`
- `scripts/create_ai_share_pack.sh`

## Comando nuevo

```bash
bash scripts/create_ai_share_pack.sh
```

Genera:

```txt
_ai_share_pack/
ai_share_pack_FECHA.zip
```

## Próximo paso

Antes de compartir con una IA:

1. Generar paquete.
2. Revisar que no tenga datos privados.
3. Subir el zip o copiar los archivos clave.
4. Pegar `PROMPT_COPIAR_PEGAR.md` en el chat.
