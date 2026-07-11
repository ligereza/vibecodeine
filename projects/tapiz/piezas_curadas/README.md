# Piezas curadas del tapiz

Serie curada de piezas SVG generadas con el instrumento real
(`projects/tapiz/vibecode_spaces.py`), nunca dibujadas a mano. Cada pieza
teje los espacios de un archivo vivo del repo: el codigo elige la trama,
el instrumento solo la revela. Paleta flujo oficial en todas.

Nota: esta carpeta se llama `piezas_curadas/` porque `projects/tapiz/piezas/`
esta gitignorada (salida efimera del instrumento); lo curado se versiona aqui.

## Piezas

| Pieza | Modo | Fuente tejida | Lectura |
|---|---|---|---|
| `field_compete_engine.svg` | field (gul) | `tools/compete_engine.py` | El motor de diagnostico del ecosistema como campo repetido de guls: la telemetria vuelta alfombra. |
| `border_validate_airdrop.svg` | border (boteh) | `scripts/validate_airdrop.py` | El validador que custodia la frontera del repo tejido como cenefa boteh: el borde que decide que entra. |
| `medallion_loom.svg` | medallion | `projects/tapiz/vibecode/loom.py` | El telar tejiendose a si mismo: su codigo ocupa el centro como medallon. |
| `mihrab_spaces.svg` | mihrab | `projects/tapiz/vibecode/spaces.py` | El render principal orientado hacia un nicho: el codigo que dibuja apunta a donde mira. |
| `cauce_cauce.svg` | cauce (animada, SMIL) | `projects/tapiz/vibecode/cauce.py` | El cauce leyendo su propia recurrencia: mismo token, mismo color, patron reconocido y no impuesto. |

## Regeneracion exacta

Desde la raiz del repo:

```bash
py projects/tapiz/vibecode_spaces.py tools/compete_engine.py -m field --svg projects/tapiz/piezas_curadas/field_compete_engine.svg
py projects/tapiz/vibecode_spaces.py scripts/validate_airdrop.py -m border --svg projects/tapiz/piezas_curadas/border_validate_airdrop.svg
py projects/tapiz/vibecode_spaces.py projects/tapiz/vibecode/loom.py -m medallion --svg projects/tapiz/piezas_curadas/medallion_loom.svg
py projects/tapiz/vibecode_spaces.py projects/tapiz/vibecode/spaces.py -m mihrab --svg projects/tapiz/piezas_curadas/mihrab_spaces.svg
py projects/tapiz/vibecode_spaces.py projects/tapiz/vibecode/cauce.py -m cauce -a --svg projects/tapiz/piezas_curadas/cauce_cauce.svg
```

Las piezas son deterministas respecto de su fuente: si el archivo tejido
cambia, la pieza cambia. La serie fija el estado 2026-07-11.
