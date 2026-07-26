// Entry point of the hub (all panels). See mainPlano.tsx for the standalone
// plano bundle.
//
// The service tariff is fetched from the hub BEFORE React mounts, so no panel
// ever renders a stale price. It comes from data/rd_packs.json -- the same file
// the rider and the Python quote read. Until 2026-07-26 the web carried its own
// hardcoded copy, so editing the tariff changed the PDF and left the app
// showing the old figures.
//
// If the hub is not reachable (a static build opened from disk) the code values
// stay: they are the same numbers, only frozen at build time.
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App";
import { applyPackPriceOverrides, type PackId } from "./rdBrand";

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

loadTariff().finally(() => {
  createRoot(document.getElementById("root")!).render(
    <StrictMode>
      <App />
    </StrictMode>
  );
});
