# AI Provider Routing - flujo

Como repartir el trabajo entre modelos. Regla base: **el modelo mas barato que haga bien la tarea. Claude dirige y hace lo critico; NO teclea boilerplate ni debuggea a Qwen.**

## Quien es quien (Claude dirige un equipo)

| Proveedor | Rol | Cuando usarlo | Notas |
|---|---|---|---|
| **Claude Code / Opus** | Director + codigo critico + arquitectura | Decide el enfoque, hace el codigo que no admite malentendido, emite ordenes para los demas | Techo. Recibe pedidos ya comprimidos por el interprete. NO revisa cada diff de Qwen |
| **Gemini API** | Interprete + voz + busqueda en vivo + lector pesado | Traduce/organiza el pedido del usuario (voz o texto en espanol) a un order liviano en tokens; grounding de busqueda en tiempo real; resume rutas gordas (`tools/vibo_voz/pedir_a_gemini.py`) | Tiene API -> automatable. Free tier con limites; ojo con datos privados |
| **Arena (LMArena)** | Frontier gratis on-demand | Arquitectura dura cuando quieres un cerebro frontier sin gastar Claude | Sin API -> manual, airdrop chico. No es fuente de verdad automatica |
| **Qwen API/web** (DashScope) | Coder bruto de volumen | Ediciones acotadas, tests, boilerplate, mascar contexto | Su salida pasa por el GATE (CI + revisor gratis), nunca por Claude directo |
| **NVIDIA NIM / OpenRouter** | Alternativa / fallback barato | Cuando Qwen no rinde o para probar otro modelo; endpoint OpenAI-compatible | Igual que Qwen |

## Gate de Qwen (reemplaza "Claude revisa el diff")

Claude NO gasta cuota debuggeando a Qwen. La salida de Qwen se atrapa gratis:

1. **CI (obligatorio, branch protection):** `py -m pytest`, compile, `flujo verify`. Gate funcional.
2. **Revisor gratis:** Gemini o Arena miran lo que CI no ve (diseno, alcance, creep).
3. **Claude entra SOLO si el gate escala** un problema de arquitectura. No como paso fijo.

## Escalar a Claude (solo lo caro)

Escala a Claude cuando la tarea tiene una o mas:
- decision de arquitectura o de que enfoque tomar;
- toca seguridad, credenciales, workflows CI, o `src/flujo/airdrop.py`;
- cambia comportamiento publico (CLI, API, formato de entrega);
- ya se intento antes y fallo (ver `src/flujo/version.py` get_changelog);
- es codigo critico donde un malentendido cuesta caro.

Deja en Qwen/NIM/OpenRouter (barato) cuando:
- hay un plan claro y el cambio es mecanico/local;
- generar tests, docstrings, boilerplate, o mascar/resumir contexto;
- traducir un order de Claude a ediciones concretas.

## Flujo tipo (bajo consumo)

1. **Pedido:** el usuario habla/escribe en espanol -> **Gemini** lo comprime y organiza a un order liviano (o a un qwen_order en chino).
2. **Direccion:** **Claude** decide: delega a Qwen (order chino) o lo hace el mismo como Claude Code si es critico.
3. **Implementa:** Qwen en una rama -> PR. (o Claude Code para lo critico.)
4. **Gate:** CI corre la verificacion; revisor gratis (Gemini/Arena) mira alcance/diseno. Merge si esta en verde.
5. **Escala:** Claude solo si el gate levanta un problema de diseno.
6. **Cierre:** actualizar `context/LAST_HANDOFF.md` + `context/SESSION_STATE.json`.

Prompts listos: `docs/TASK_PROMPTS.md`.
