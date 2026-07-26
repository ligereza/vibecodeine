# CHECKPOINT UNICO -- estado del repo

Este es el UNICO archivo de estado. Antes habia siete compitiendo (LAST_HANDOFF,
SESSION_STATE, PLAN_SIGUIENTE_AGENTE, PLAN_SEMANAL_OPUS, ORQUESTACION_SUCESOR,
WALKTHROUGH, failed-handoff) y por eso cada agente reconstruia todo y volvia a
preguntarle al usuario lo mismo. Se fundieron aca el 2026-07-26. Lo anterior
sigue en el historial de git y en docs/handoffs/archive/.

Con `CLAUDE.md` y `MAPA.md`, esto es todo lo que necesita leer un agente que entra.

**Como se mantiene:** guarda RESPUESTAS, no preguntas. Cuando el usuario decide
algo, se escribe aca en la MISMA sesion. Un pendiente sigue abierto SOLO si nadie
lo contesto todavia; apenas se contesta, se mueve a "Ya decidido" y se borra de
pendientes.

**No va aca:** rutas absolutas, IPs, telefonos ni nada personal. Este repo es
publico. Eso vive en la memoria local del asistente.

---

## Regla de trabajo (2026-07-26, palabra del usuario)

> El usuario no es experto en informatica; es experto en saber lo que quiere.
> Si el asistente cree que un camino es optimo POR RAZONES TECNICAS, adelante,
> sin preguntar -- sea codigo, regla o configuracion. Si el asistente asume un
> ESTILO, una estetica, o lo que el usuario quiere, es un error: eso se pregunta.

Corolarios, sacados de las sesiones que fallaron:

- **No hay entregable.** Se hace lo que se pidio. No se inventa un producto, un
  plan, un informe ni un respaldo que nadie pidio. Un hallazgo al paso se anota
  en una linea y se sigue de largo.
- **Avances grandes, no pasos de bebe.** No commitear y esperar CI cada dos
  cambios; el usuario lo pidio explicitamente.
- El repo es un pendrive. El centro es la conversacion, no el repo.
- Medir sirve para contestar algo que se pregunto. Medir de mas es perder el hilo.

## Quien es cada agente (define que reglas le aplican)

- **Claude Code local** (esta sesion): lee el repo y pushea. Le aplican los tests
  que protegen el software. Los validadores de airdrop no son su camino.
- **Agente web / arena**: clona el repo pero NO pushea. Entrega un ZIP que el
  usuario aplica y despues pide "revisa". Para el existen `_airdrop/`,
  `scripts/validate_airdrop.py` y los ratchets de documentacion.
- **MAK** (box Linux): corre research/codex/plataforma. Su doctrina vive en
  `cultura/mak_plataforma/doctrina/`, NO en `context/`.

## Estado

Version 0.56.1. Topologia: TRES ramas y ninguna mas -- `main` (todo, funcional y
comprobable), `rd` (ONG/datos/becas), `iskvw` (curatoria/obra). `mejoras` se
fundio en main y se retiro. Nadie pushea a main directo: esta protegida con
`enforce_admins`, todo entra por PR con CI verde.

Funcionando y verificado en vivo: la cadena del show DREF (LTC -> Chataigne ->
OSC -> telefono -> panel PWA), la DB de RD con eventos normalizados, el hub
dividido en 3 perfiles, y los ratchets de doc (`test_mapa_completo`,
`test_higiene_docs`).

Roto y conocido: `tests/test_ig_cffi_fallback.py` falla en la maquina del usuario
porque el test simula que `curl_cffi` no esta instalado, y ahi si lo esta. En CI
pasa. Es dependencia del entorno, no un bug del codigo.

## Ya decidido -- no reabrir

| Fecha | Decision |
|---|---|
| 2026-07-26 | Los worktrees de agente en `.claude/worktrees/` se podan al terminar la tarea. Habia 7 abandonados, cada uno una copia completa del repo: multiplicaban por 8 cada handoff, checkpoint y doctrina, y por eso una busqueda devolvia cientos de resultados sin decir cual mandaba |
| 2026-07-26 | La doctrina de MAK (`CAPATAZ.md`, `DOCTRINA_CLAUDE.md`) vive en `cultura/mak_plataforma/doctrina/`. Estaba escrita para el modelo local del box, y los Claude la leian como propia y se confundian |
| 2026-07-26 | **El portafolio es `iskvw`: la linea automatizada y la UNICA pagina. Este repo se mantiene PUBLICO.** Queda descartado el repo aparte `portfolio-auto`: existio porque un agente recomendo volver privado este repo y el siguiente parcheo eso creando un segundo repo para la pagina. Las dos movidas fueron un error; no repetirlas ni reabrir el tema |
| 2026-07-25 | Panel de suplementos en la app: INNECESARIO. Palabra del usuario: "los flyers los presentan" |
| 2026-07-25 | No se respalda la carpeta de disenos desde el repo. Se pidio extraer estructura y datos; un agente lo convirtio en un encargo de respaldo de 1 GB que nadie pidio |
| 2026-07-25 | Los dos planes grandes propuestos ("separar el motor del contenido" y "de repo a tres productos") quedaron RECHAZADOS. No ejecutarlos por autoridad propia |
| 2026-07-25 | `desktop/` (el flotante Tkinter) archivado |
| 2026-07-22 | Instagram: `parth-dl` primaria, `curl_cffi` secundaria en Linux. imginn muerto, instaloader no sirve, yt-dlp no se usa |
| 2026-07-16 | n8n: descartado, no reintentar |
| 2026-07-10 | Gemini: fuera hasta que el usuario anuncie una API util |
| 2026-07-26 | No reinstalar Oh My Posh ni nada que meta glifos o ANSI en el prompt: ensucia la salida que los agentes tienen que parsear |

## Bloqueado esperando al usuario

- **Referencias esteticas del portafolio.** El destino ya no esta en duda: es la
  linea `iskvw`, en este repo publico. Lo que falta es la estetica: las
  referencias reales se mandaron en sesiones cloud, los contenedores son efimeros
  y nunca se commitearon. Se diseno dos veces sobre notas viejas y las dos se
  rechazo, asi que no se disena de nuevo sobre suposiciones. Cuando lleguen:
  **commitearlas en el acto** en `iskvw`, o ingerirlas con `flujo datadrop`, que
  existe justamente para eso y nunca se uso. Lo unico que se puede construir
  mientras tanto es el pipeline, que no depende de la estetica.

## Abierto

- Sacar del codigo los telefonos de relleno de la config de suplementos y su uso
  en el exportador: orden del usuario, "no debe haber info personal".
- Catalogo de simbolos personalizados del plano. Criterio de aceptacion textual:
  "la jefa puede agregar un icono? si no, no es configurable".
- Dos exports de diseno quedaron atras de su fuente. Es re-exportar, no respaldar.
