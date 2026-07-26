// Entry point of the hub (all panels). See mainPlano.tsx for the standalone
// plano bundle.
//
// Two sets of editable values are fetched from the hub BEFORE React mounts, so
// no panel ever renders a stale price:
//   - the field-service tariff, data/rd_packs.json, the same file the rider and
//     the Python quote read. Until 2026-07-26 the web carried its own hardcoded
//     copy, so editing it changed the PDF and left the app on the old figures.
//   - the quote tool's line items, data/cotizacion_servicios.json. Design and
//     printing services, which change per job (the user, 2026-07-26: "cada
//     archivo de illustrator es distinto y los valores igual").
//
// If the hub is not reachable (a static build opened from disk) the code values
// stay: they are the same numbers, only frozen at build time.
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App";
import { applyPackPriceOverrides, type PackId } from "./rdBrand";
import { loadCotizacionServicios } from "./data/cotizacionServicios";

async function loadTariff(): Promise<void> {
  try {
    const res = await fetch("/api/rd-packs");
    if (!res.ok) return;
    const data = await res.json();
    const packs = data?.packs;
    if (!packs || typeof packs !== "object") return;
    const overrides: Partial<Record<PackId, number>> = {};
    for (const [id, pack] of Object.entries(packs)) {
      const precio = (pack as { precio?: unknown })?.precio;
      if (typeof precio === "number") overrides[id as PackId] = precio;
    }
    applyPackPriceOverrides(overrides);
  } catch {
    // Hub not reachable: keep the code values rather than blocking the app.
  }
}

Promise.all([loadTariff(), loadCotizacionServicios()]).finally(() => {
  createRoot(document.getElementById("root")!).render(
    <StrictMode>
      <App />
    </StrictMode>
  );
});
