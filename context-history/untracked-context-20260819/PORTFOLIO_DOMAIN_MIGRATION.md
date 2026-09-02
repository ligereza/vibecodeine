# Portfolio domain migration status

Read-only audit performed 2026-08-16.

Current publication connection:

- Repository: `ligereza/vibecodeine`.
- Workflow: `.github/workflows/publicar_iskvw.yml`.
- Source: `main`, GitHub Pages workflow deployment.
- Current GitHub Pages custom domain: `iskvw.cl`.
- No repository Actions variable `PUBLIC_DOMAIN` is currently defined; the
  workflow therefore falls back to `iskvw.cl`.
- Local workflow generates `_sitio/CNAME` from `PUBLIC_DOMAIN` and publishes
  only the `iskvw/` site. It does not publish MAK, RD or Cultura.
- No Cloudflare DNS/Pages configuration is present in the repository. The
  external Cloudflare dashboard cannot be inferred from local files.
- No new domain name was supplied, so no domain or DNS mutation was made.

Migration sequence when the new domain is known:

1. Confirm the exact bare domain and whether `www` should redirect or alias.
2. Set the GitHub Actions repository variable `PUBLIC_DOMAIN` to that bare
   domain; do not put it in `.env` or source files.
3. Configure the custom domain in GitHub Pages and the corresponding DNS
   records in Cloudflare.
4. Dispatch `publicar iskvw` once and verify the generated CNAME, HTTPS,
   root index and asset paths.
5. Keep `iskvw.cl` unchanged until the new domain passes the live checks.

Current state is safe: the old domain remains the active fallback and no
external DNS or hosting state was changed.
