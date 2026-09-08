(function () {
  "use strict";

  const POLL_MS = 90;
  let pollTimer = null;
  let lastCueId = "";

  function el(id) {
    return document.getElementById(id);
  }

  function fmtCue(cue) {
    if (!cue) return "sin cue";
    const label = cue.title || cue.tema || "cue";
    return cue.n != null ? `#${cue.n} ${label}` : label;
  }

  function applySnapshot(snapshot) {
    const root = el("estudio-app");
    if (!root || !snapshot) return;
    root.dataset.liveMode = snapshot.mode || "idle";
    root.style.setProperty("--xio-amp", String(snapshot.amplitude || 0));
    root.style.setProperty("--xio-beat", String(snapshot.beat || 0));
    const cue = snapshot.cue || null;
    const layerSeed = Number(cue && (cue.layer != null ? cue.layer : cue.n)) || 0;
    root.style.setProperty("--xio-cue-hue", String((layerSeed * 47) % 360));

    const timecodeEl = el("mesa-live-timecode");
    if (timecodeEl) timecodeEl.textContent = snapshot.timecode || "00:00:00:00";

    const cueEl = el("mesa-live-cue");
    if (cueEl) cueEl.textContent = fmtCue(cue);

    const sourceEl = el("mesa-live-source");
    if (sourceEl) {
      const isExternal = snapshot.source === "external";
      sourceEl.textContent = isExternal ? "externo" : (snapshot.mode === "idle" ? "detenido" : "sintético");
      sourceEl.classList.toggle("is-external", isExternal);
    }

    const ampBar = el("mesa-live-amp-bar");
    if (ampBar) ampBar.style.width = `${Math.round((snapshot.amplitude || 0) * 100)}%`;

    const cueId = cue ? String(cue.n != null ? cue.n : cue.title || "") : "";
    if (cueId && cueId !== lastCueId) {
      const world = el("mesa-world");
      if (world) {
        world.classList.remove("mesa-cue-flash");
        void world.offsetWidth; // restart the CSS animation on repeated cues
        world.classList.add("mesa-cue-flash");
      }
    }
    lastCueId = cueId;

    const startButton = el("mesa-live-start");
    const pauseButton = el("mesa-live-pause");
    if (startButton) startButton.disabled = snapshot.mode === "running" || snapshot.mode === "external";
    if (pauseButton) pauseButton.disabled = snapshot.mode !== "running";
  }

  async function poll() {
    try {
      const response = await fetch("/api/portfolio/xio/live", { cache: "no-store" });
      const data = await response.json();
      if (data && data.ok !== false) applySnapshot(data);
    } catch {
      // network hiccup: keep the last visual state, retry next tick
    }
  }

  function startPolling() {
    if (pollTimer) return;
    poll();
    pollTimer = window.setInterval(poll, POLL_MS);
  }

  function stopPolling() {
    if (!pollTimer) return;
    window.clearInterval(pollTimer);
    pollTimer = null;
    const root = el("estudio-app");
    if (root) {
      root.style.setProperty("--xio-amp", "0");
      root.style.setProperty("--xio-beat", "0");
      delete root.dataset.liveMode;
    }
  }

  async function sendAction(action) {
    try {
      const response = await fetch("/api/portfolio/xio/live", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action }),
      });
      const data = await response.json();
      if (data && data.ok !== false) applySnapshot(data);
    } catch {
      // ignore; the next poll tick resyncs
    }
  }

  function toggleHud() {
    const hud = el("mesa-live-hud");
    const toggle = el("mesa-live-toggle");
    if (!hud) return;
    const showing = hud.hidden;
    hud.hidden = !showing;
    if (toggle) toggle.classList.toggle("is-active", showing);
    if (showing) startPolling();
    else stopPolling();
  }

  function wire() {
    const toggle = el("mesa-live-toggle");
    const hud = el("mesa-live-hud");
    if (!toggle || !hud) return false;
    toggle.addEventListener("click", (event) => {
      event.stopPropagation();
      toggleHud();
    });
    hud.addEventListener("click", (event) => {
      const button = event.target.closest("[data-live-action]");
      if (!button) return;
      event.stopPropagation();
      sendAction(button.dataset.liveAction);
    });
    return true;
  }

  if (!wire()) {
    // mesa_montaje.js mounts the shell synchronously before this script runs,
    // but guard against load-order changes rather than fail silently.
    let attempts = 0;
    const retry = window.setInterval(() => {
      attempts += 1;
      if (wire() || attempts > 40) window.clearInterval(retry);
    }, 100);
  }
}());
