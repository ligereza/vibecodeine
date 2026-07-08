---
name: relevo-web
description: >
  Workflow Reader/Web/Coder 100% por chat WEB gratis (sin API, sin Aider, sin gastar
  cuota Claude en lectura/escritura masiva). Reader = Gemini web analiza/resume repo o
  docs largos. Web = Gemini web con busqueda para info externa/actual. Coder = Qwen web
  (chat.qwen.ai) escribe/edita codigo. Claude solo prepara los prompts cortos, aplica el
  resultado final y verifica -- nunca lee/escribe el volumen el mismo.
  Invocar cuando el usuario pida "usa Gemini y Qwen por web", "orquesta reader/coder/web",
  "sin API", "sin Aider", o cuando una tarea implica leer mucho material o escribir
  codigo de volumen y conviene no gastar tokens de Claude en eso.
---

# Relevo web: Reader (Gemini) + Web (Gemini busqueda) + Coder (Qwen) + Claude arma

Tres roles, tres pestanas de navegador gratis, cero API keys. Claude Code (yo) actua de
relevo: preparo el prompt corto, VOS pegas en la web correspondiente, pegas la respuesta
de vuelta, y yo la uso para el siguiente paso o para aplicar el cambio final. Nunca leo
ni escribo el material pesado directamente -- eso lo hacen los gratis.

No confundir con `docs/AIDER_API_SETUP.md` (ese es API + Aider, plata real). Esta skill
es la version cero-costo: 100% chat web manual.

## Los tres roles

| Rol | Donde (web gratis) | Para que |
|---|---|---|
| **Reader** | gemini.google.com (o aistudio.google.com) | Leer/resumir codigo, docs largos, un archivo grande, "que hace este modulo" |
| **Web** | gemini.google.com con busqueda activada | Info externa/actual: version de una libreria, doc de una API de terceros, noticias |
| **Coder** | chat.qwen.ai (Qwen3-Coder) | Escribir/editar codigo dado un contexto ya reducido |

## Protocolo (por tarea)

1. **Vos me das la tarea.** Yo decido que rol(es) hacen falta (a veces solo Coder, a veces Reader->Coder).
2. **Preparo el prompt del rol** (bloque corto, listo para copiar — ver plantillas abajo).
3. **Vos pegas** en la pestana web correspondiente y me traes la respuesta (pegada o resumida).
4. Si el siguiente rol necesita esa respuesta como contexto, preparo el prompt siguiente
   YA con eso adentro (vos no resumis nada a mano).
5. Cuando Coder devuelve codigo: yo lo aplico a los archivos reales (edicion mecanica,
   no re-derivo nada) y corro la verificacion del repo (`py -m compileall`, `pytest`,
   `flujo verify`).
6. Reporto: que se hizo, que verifique, que quedo pendiente.

## Plantillas

### Reader (Gemini web)
```
Eres lector de contexto del repo 'flujo'. NO propongas cambios, NO escribas codigo.
Material pegado abajo (o archivo/carpeta: <ruta>).
Devuelve en <= 20 lineas:
- que hace cada archivo/bloque (1 linea c/u)
- funciones/simbolos clave y donde se usan
- riesgos o zonas fragiles
- que hace falta saber para: <tarea>
Sin relleno. Si algo no esta en el material, di "no visible".

<pegar aqui el archivo/codigo/doc>
```

### Web (Gemini web, con busqueda)
```
Busca informacion actual y confiable sobre: <pregunta concreta>.
Contexto: repo 'flujo' (Python/Typer + web React/Vite), estoy evaluando <para que>.
Devuelve: respuesta directa, fuente/version si aplica, en <= 10 lineas. Sin relleno.
```

### Coder (Qwen web — chat.qwen.ai, modelo Qwen3-Coder)
```
Tarea: <tarea concreta>.
Contexto ya reducido (de un lector, no re-leas nada mas):
<pegar el resumen del Reader aca>

Escribe SOLO el codigo/diff para: <archivo(s) exacto(s)>.
Cambios minimos y completos, sin TODO ni stubs, sin explicacion larga -- solo el codigo
final listo para pegar. Si falta info para decidir, dilo en 1 linea y elegi la opcion
mas segura vos mismo (no preguntes de vuelta).
```

## Cuando NO usar esto

- Tarea de 1-2 lineas que yo ya se responder: contestar directo, no arranques el relevo
  (el copy-paste manual cuesta MAS que resolverlo ahi mismo).
- Decision de arquitectura, seguridad, o algo que ya se intento y fallo (ver
  `src/flujo/version.py` `get_changelog()`): eso es mio (Claude), no se delega.
- Codigo critico del "nucleo duro" del repo (noisette/VJ/timecode, mapping Resolume,
  ver CLAUDE.md seccion Mision): ahi Claude ejecuta directo, sin relevo.

## Verificacion (obligatoria antes de dar por bueno lo que trajo Coder)

```bash
py -m compileall src/flujo
py -m pytest tests/ -q
py -m flujo verify
```
Si tocaste `web/`: `cd web && npm run typecheck && npm run build:context && cd ..`.
No aceptes el codigo de Coder sin esto en verde.
