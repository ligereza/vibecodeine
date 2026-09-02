# Phase 447 — Tapiz renderer contract gate

## Alcance

Se auditó el siguiente consumidor HTML independiente encontrado desde
`/home/mak/*`: `tools/tapiz_renderer.html`. Se verificó el dueño de datos, el
contrato estructural, el decodificador de payloads, el polling y la copia de
despliegue. El renderer local se mantuvo separado de `tapiz_three.html`, que
usa un CDN de Three.js.

## Dueño y contrato

```text
tools/compete_engine.py --demo
  -> tools/dist/system_status.json  (input demo clasificado)
  -> tools/tapiz_renderer.html      (renderer local, file/http fallback)
tools/system_map.py                 (schema validator)
```

El HTML consume las cuatro secciones del contrato: malla luminosa, máscara
cromática, colisiones cronológicas y payloads codificados. Renderiza el sigilo
del metadata, respeta `prefers-reduced-motion`, hace polling cada 30 segundos y
solo decodifica payloads al interactuar con una espora. Si `fetch` falla en
`file://`, ofrece un selector local de JSON.

## Validación foreground

Ejecutado desde `/home/mak/flujo`:

```text
py_compile system_map.py + compete_engine.py         -> exit 0
system_map.py validate tools/dist/system_status.json  -> exit 0
compete_engine.py --help                             -> exit 0
Node new Function sobre el script inline             -> exit 0
JSON schema/payload assertions                        -> exit 0
cmp contra flujo-deploy/tools/tapiz_renderer.html    -> exit 0
```

El estado demo tiene 28,784 bytes, dos payloads (`Psicosis`, `Fungi`) y todas
las claves requeridas por `API_CONTRACT_SCHEMA`. La comprobación independiente
decodificó ambos payloads con Base64+Shift42 y produjo texto UTF-8 no vacío.
El HTML tiene 12,662 bytes, 51 tags, un script inline, cero `src` externos y
SHA-256 `0845bbd13489ead7fdb8e81ee01dabe7adca8638af22a8603b8a4b8036028602`;
la copia de `flujo-deploy` es idéntica.

## Dictamen

```text
TAPIZ_RENDERER_OWNER_GREEN
TAPIZ_SYSTEM_SCHEMA_GREEN
TAPIZ_PAYLOAD_DECODER_GREEN
TAPIZ_DEMO_INPUT_VALID
TAPIZ_DEPLOY_COPY_EXACT
TAPIZ_THREE_EXTERNAL_CDN_SEPARATE
```

Este slice está integrado como renderer local de evidencia/demo. No se debe
confundir con telemetría viva: `--live` existe en el generador, pero no se
ejecutó porque lee estado real del repo y podría producir una proyección
operativa diferente. Tampoco se inició servidor.

## Riesgos y rollback

- El input actual es demo y debe conservar esa etiqueta; no es diagnóstico
  clínico ni estado operativo de MAK.
- El renderer 3D `tapiz_three.html` queda aparte por su dependencia externa
  `https://unpkg.com/three@0.160.0/...`; no se convirtió en dependencia del
  renderer local.
- No hubo cambios en fuente, JSON, HTML o despliegue; rollback: no-op.

## Siguiente acción

Continuar con el siguiente HTML de herramienta o piel independiente desde
`/home/mak/*`, priorizando `tools/tapiz_three.html` únicamente como gate de
dependencia externa estática, sin CDN request, y luego las superficies cultura
restantes. Mantener separados el bundle RD bloqueado por Node/Vite, Sala3D,
venue, laser, Plano/Rider y la tabla oficial RD.
