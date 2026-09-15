/* Runtime común de las pieles de ISKVW.
 *
 * Una piel puede cambiar la forma de leer, pero no puede cambiar el archivo
 * que está mostrando. Este módulo mantiene juntas las dos partes que antes
 * estaban repetidas en campo y terminal: cargar el manifiesto/archivo y
 * ofrecer el cambio de piel conservando la lectura actual en la URL.
 */
(function (root) {
  "use strict";

  const SKINS = [
    { id: "campo", label: "campo" },
    { id: "terminal", label: "terminal" },
  ];
  const manifestPromises = new Map();

  function registryFromManifest(value) {
    if (!Array.isArray(value)) return SKINS;
    const skins = value.filter(s => s && typeof s === "object"
      && /^[a-z0-9_-]+$/i.test(String(s.id || ""))
      && typeof s.path === "string")
      .map(s => ({ id: String(s.id), label: String(s.label || s.id) }));
    return skins.length ? skins : SKINS;
  }

  function tienePiezas(data) {
    return Array.isArray(data)
      ? data.length > 0
      : !!(data && Array.isArray(data.piezas) && data.piezas.length);
  }

  function ordenarArchivo(manifest, data) {
    if (!data || Array.isArray(data) || !Array.isArray(data.piezas)) return data;
    const orden = manifest && Array.isArray(manifest.order)
      ? manifest.order : [];
    if (!orden.length) return data;
    const porId = new Map(data.piezas.map(p => [p && p.id, p]));
    const usados = new Set();
    const piezas = [];
    for (const id of orden) {
      const pieza = porId.get(id);
      if (!pieza || usados.has(id)) continue;
      piezas.push(pieza);
      usados.add(id);
    }
    // El manifiesto no puede hacer desaparecer una pieza nueva. Si el archivo
    // creció después de generarlo, se conserva al final en su orden de origen.
    for (const pieza of data.piezas) {
      if (!pieza || usados.has(pieza.id)) continue;
      piezas.push(pieza);
      usados.add(pieza.id);
    }
    return { ...data, piezas };
  }

  async function leerJson(ruta) {
    try {
      const respuesta = await root.fetch(ruta);
      if (!respuesta || !respuesta.ok) return null;
      return await respuesta.json();
    } catch (_) {
      return null;
    }
  }

  function leerManifest(paths) {
    const key = paths.join("|");
    if (manifestPromises.has(key)) return manifestPromises.get(key);
    const promise = (async () => {
      for (const ruta of paths) {
        const dato = await leerJson(ruta);
        if (dato && dato.schema === "iskvw-portfolio-manifest-v1") return dato;
      }
      return null;
    })();
    manifestPromises.set(key, promise);
    return promise;
  }

  async function loadPortfolio({
    portfolioPaths = [],
    sourcePaths = [],
    fallback = [],
  } = {}) {
    const manifest = await leerManifest(portfolioPaths);
    if (manifest) installSkinSwitcher(registryFromManifest(manifest.skins));
    for (const ruta of sourcePaths) {
      const dato = await leerJson(ruta);
      if (!tienePiezas(dato)) continue;
      const ordenado = manifest ? ordenarArchivo(manifest, dato) : dato;
      return {
        data: ordenado,
        manifest,
        kind: Array.isArray(ordenado) ? "array" : "archive",
        source: ruta,
      };
    }
    return {
      data: fallback,
      manifest,
      kind: Array.isArray(fallback) ? "array" : "archive",
      source: "inline-fallback",
    };
  }

  function rutaDePiel(id) {
    const loc = root.location || {};
    const path = String(loc.pathname || "");
    const match = path.match(/^(.*\/piel\/)[^/]+(?:\/index\.html)?\/?$/);
    let destino;
    if (match) {
      destino = match[1] + id + "/";
    } else {
      const carpeta = path.replace(/[^/]*$/, "");
      destino = carpeta + "piel/" + id + "/";
    }
    return destino + String(loc.search || "") + String(loc.hash || "");
  }

  function installSkinSwitcher(skins = SKINS) {
    if (!root.document || !root.document.body) return null;
    const body = root.document.body;
    if (!body.dataset || !body.dataset.skin) return null;
    let nav = body.querySelector && body.querySelector("[data-iskvw-skin-switcher]");
    if (!nav) nav = root.document.createElement("nav");
    nav.dataset.iskvwSkinSwitcher = "";
    nav.setAttribute("aria-label", "cambiar piel");
    if (nav.replaceChildren) nav.replaceChildren();
    for (const skin of registryFromManifest(skins)) {
      const link = root.document.createElement("a");
      link.href = rutaDePiel(skin.id);
      link.textContent = skin.label;
      link.dataset.skinTarget = skin.id;
      if (skin.id === body.dataset.skin) {
        link.setAttribute("aria-current", "page");
        link.dataset.active = "";
      }
      nav.appendChild(link);
    }
    if (!nav.parentNode) body.appendChild(nav);

    if (root.document.head) {
      const style = root.document.createElement("style");
      style.textContent = `
        [data-iskvw-skin-switcher]{position:fixed;z-index:20;top:12px;left:50%;
          transform:translateX(-50%);display:flex;gap:8px;padding:4px 7px;
          border:1px solid rgba(232,228,218,.18);background:rgba(8,8,10,.52);
          font:10px/1 ui-monospace,SFMono-Regular,Menlo,monospace;
          letter-spacing:.12em;text-transform:uppercase;backdrop-filter:blur(4px)}
        [data-iskvw-skin-switcher] a{color:rgba(232,228,218,.58);text-decoration:none}
        [data-iskvw-skin-switcher] a[data-active]{color:#e8e4da}
        [data-iskvw-skin-switcher] a:hover{color:#fff}
      `;
      root.document.head.appendChild(style);
    }
    return nav;
  }

  root.ISKVW_SKIN_RUNTIME = Object.freeze({
    skins: SKINS,
    loadPortfolio,
    orderArchive: ordenarArchivo,
    skinPath: rutaDePiel,
    installSkinSwitcher,
  });
  installSkinSwitcher();
  leerManifest(["../../datos/portafolio.json"])
    .then(manifest => {
      if (manifest) installSkinSwitcher(registryFromManifest(manifest.skins));
    });
})(window);
