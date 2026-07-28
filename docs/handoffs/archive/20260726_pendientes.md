# Pendientes del 2026-07-26

Archivado del checkpoint el 2026-07-27 por el tope de 350 lineas.

### Still open from 2026-07-26, in one place

- `cultura/mak_plataforma/ideas.py` is written and committed but NOT wired into
  MAK's hub and never tested. The user's ask: declare an idea, have the archive
  say which of his works it relates to (semantic micelio search, already
  verified working), put it at the front of the queue, or prioritise by pattern.
  Missing: endpoints in `plataforma/hub.py` (`/api/ejecutar` is the mould), a
  page, and a test.
- **MAK should be the default renderer, not Windows** (user's reason: outdoors he
  can get internet for MAK; if Windows is required there is no render). One
  measurement is missing first -- nothing was ever rendered on the box, which has
  4 GB of VRAM and already OOMed with ollama resident. Windows keeps the heavy
  work (the 600-frame video, proven there). When MAK renders it does NOT close
  the issue: it comments and leaves it open, because a bad render costs GPU.
- **Root on the Samsung J6+: decided, postponed.** SMS -> turns on mobile data ->
  MAK has internet depending on nobody. Non-negotiable condition: charge control
  like the Xiaomi's, or an old phone plugged in 24/7 is a fire risk. httpSMS does
  NOT serve this (it needs permanent internet via Firebase push and forwards SMS
  to a server; it assumes solved exactly what we want to achieve). Waking MAK is
  already solved (`cultura/mak_plataforma/WAKE_ON_LAN.md`): Xiaomi by WoWLAN,
  Windows by ethernet; the `wake_mak.py` plugin is staged, not deployed.
- `tools/bridge_issue_render.py` does NOT run on its own: it is foreground and
  has to be launched by hand on Windows because it opens Blender. That is the
  link the Automations panel draws as automatic and is not.
