HANDOFF - FIX dispatcher (v0.40.1)  *** APLICAR ESTE FIX ***
============================================================
Fecha: 2026-06-28
Causa: el airdrop v0.40 REEMPLAZO src/flujo/__main__.py con un dispatcher
       propio, ocultando tu CLI Typer (health/doctor/job/eventos/airdrop...).
       Sintoma: "py -m flujo health" -> "subcomando desconocido: health".

QUE HACE ESTE FIX
- Restaura tu __main__.py original (4 lineas: delega a flujo.cli:app).
- Agrega src/flujo/cli_addons.py: registra los nuevos comandos bajo el
  namespace 'hub' (NO pisa nada):
      py -m flujo hub serve [--port 8777] [--open]
      py -m flujo hub index <build|stats|find|versions|dupes|cleanup|agent-brief> ...
      py -m flujo hub route <where|cuna|doctor> ...
- aplicar_fix.py inserta 2 lineas en cli.py (import + register_addons(app)),
  idempotente y con backup (cli.py.bak).

COMO APLICAR (desde C:\IA\flujo)
  1) copiar src/flujo/__main__.py  y  src/flujo/cli_addons.py  al repo.
  2) py aplicar_fix.py            (o:  py aplicar_fix.py --dry-run  para previsualizar)
  3) verificar:
       py -m flujo health         -> debe volver a funcionar (tus comandos vivos)
       py -m flujo hub serve --open
       py -m flujo hub route where --area eventos --pieza flyer
       py -m flujo hub index agent-brief "etiqueta creatina"

NOTA: serve/index/route ya quedaron instalados por el airdrop v0.40
(src/flujo/serve, /index, /route). Este fix solo arregla el ENRUTAMIENTO.

VERIFICADO
- Sobre tu cli.py real (2155 lineas): inserta sin romper; health y doctor intactos.
- Idempotente (2da pasada no duplica). Crea cli.py.bak.
- cli_addons (Typer): registra hub{serve,index,route} sin colision; imports lazy.

SI PREFIERES HACERLO A MANO (sin aplicar_fix.py)
  En src/flujo/cli.py, al final del archivo agrega:
      from flujo.cli_addons import register_addons
      register_addons(app)
  Y deja src/flujo/__main__.py como:
      from .cli import app
      if __name__ == "__main__":
          app()

REGLAS: Windows + py. ASCII-only. Sin tokens. No toca tus comandos.
Airdrop: py scripts/validate_airdrop.py ; py scripts/run_airdrop_checks.py "fix: restaurar cli + addons hub (v0.40.1)"
