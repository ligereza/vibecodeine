# Phase 410 — Portfolio hosting connection audit

Date: 2026-08-15
Agent: LUNA principal
Scope: read-only inspection of the active portfolio publishing path. No DNS,
Cloudflare, GitHub, domain or source mutation was performed.

## Evidence inspected

- Canonical authoring root: `/home/mak/flujo`.
- Portfolio source published by the workflow: `/home/mak/flujo/iskvw/`.
- Publisher: `/home/mak/flujo/.github/workflows/publicar_iskvw.yml`.
- Deployment copy: `/home/mak/flujo-deploy/.github/workflows/publicar_iskvw.yml`.
- Portfolio owner gate: `/home/mak/flujo/context/PHASE408_PORTFOLIO_WEB_OWNER_GATE.md`.

The two workflow files have identical SHA-256:

`d3a1fbede3a2e6d7d471f71f1e380ee8b368e84b873f05ebfddd5309e4b0301d`

## Current connection

1. The workflow is triggered only by `workflow_dispatch`; it does not publish
   on every push and it does not run a permanent local service.
2. It builds a temporary `_sitio/` from `iskvw/`, generates
   `iskvw/datos/archivo.json`, validates the data/SVG contract, and publishes
   the artifact with `actions/configure-pages`,
   `actions/upload-pages-artifact` and `actions/deploy-pages`.
3. Therefore the repository-proven publishing platform is GitHub Pages, not
   Cloudflare Pages or Cloudflare Workers.
4. The custom-domain file is generated at deploy time:
   `PUBLIC_DOMAIN: ${{ vars.PUBLIC_DOMAIN || 'iskvw.cl' }}` followed by
   `_sitio/CNAME`. If the repository variable is absent, the old hostname
   `iskvw.cl` remains the default.
5. The workflow publishes the portfolio surface only. It does not publish RD,
   the MAK tree, XIO or the protected original `portfolio_media` archive.

## DNS / Cloudflare boundary

Read-only local checks on 2026-08-15:

```text
dig +short CNAME iskvw.cl  -> exit 0, no answer
dig +short A iskvw.cl      -> exit 0, no answer
dig +short AAAA iskvw.cl   -> exit 0, no answer
getent ahosts iskvw.cl     -> exit 2, no answer
```

No active `wrangler.toml`, Wrangler config, `pages.dev`, `workers.dev` or
Cloudflare deployment configuration was found in the bounded active tree. The
repository contains a Cloudflare-named research document, but it is not an
operational DNS/deployment configuration. These facts do not prove what is in
the Cloudflare dashboard, nor whether Cloudflare is currently acting as DNS,
proxy or certificate layer. That remains an external-state check.

## Safe future domain migration

When the new domain is ready, the smallest expected change is:

1. Set the GitHub repository variable `PUBLIC_DOMAIN` to the new bare domain.
2. Dispatch `publicar iskvw` manually and verify the generated `CNAME` and
   deployed Pages URL.
3. Configure the new domain's DNS/custom-domain binding at the provider.
4. Verify HTTPS and the portfolio before retiring the old domain.

No step above was executed in this phase. The critical guard is to avoid
deploying while `PUBLIC_DOMAIN` is absent, because that writes `iskvw.cl` into
the new artifact by default.

## Result

The portfolio is locally wired to GitHub Pages with a generated custom-domain
binding. Cloudflare is not currently evidenced as the publisher from local
files. No files were modified outside this report and the handoff update.

## Next action

Keep domain renewal/migration deferred. Continue the MAK integration gates;
when the user authorizes the domain change, inspect the external GitHub Pages
custom-domain and Cloudflare DNS state as one read-only bounded check before
changing `PUBLIC_DOMAIN`.
