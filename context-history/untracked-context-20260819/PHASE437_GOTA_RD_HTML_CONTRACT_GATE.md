# Phase 437: La Gota HTML contract gate

## Owner and provenance

The active tool is `tools/gota_rd/index.html`; its `flujo-deploy` projection is
byte-identical (SHA-256
`a688cef757c2343de341f4736c9c863781b2c58c1d5f303a534e4258b2a17a4f`). The
consolidated cultural memory identifies this as the La Gota v2 visual
experience: generative reagent drop, camera sampling, installation mode and
downloadable night canvas.

## Runtime boundary

The HTML visibly marks its reaction table as demo data and states that
colorimetric testing is orientative, never confirmatory. `ENDPOINT` is read
only from a URL parameter or localStorage and defaults to empty. With no
endpoint, the tool stays local and exports observations/PNG. If an endpoint is
configured, it can GET the table and POST observations; no endpoint was
configured or called in this phase.

The active Hub exposes `/api/rd-datos-summary`, but the Gota page does not
hard-code that route and the privacy-first `rd_datos.db` remains a separate
field store. Therefore Gota is not falsely classified as integrated with the
official RD reaction table.

## Validation

- deploy parity: `cmp` exit 0;
- HTML static markers: exit 0;
- both inline JavaScript blocks: `node --check` exit 0;
- no network, camera, POST, database or service execution.

## Disposition

`GOTA_RD_ACTIVE_DEMO; DEPLOY_COPY_EXACT; OFFICIAL_TABLE_UNWIRED; NO_EXTERNAL_CALL`.

The HTML is consolidated by ownership, not merged with official RD data. Its
demo boundary is a safety feature and remains open until RD supplies the
validated chart and a deliberate endpoint contract.

## Next action

Continue the HTML owner audit on the next independent active consumer. Keep the
official reaction table and privacy database as explicit integration gates.
