/* Vibo Adobe Panel - dispatcher CEP */

// ==========================================================================
// RUTA DINAMICA: leer de config.json, env var, o fallback relativo
// ==========================================================================
var cs = new CSInterface();

function getRepoToolsPath() {
  // 1) Intentar variable de entorno ADOBE_PANEL_REPO_ROOT (si CEP la expone)
  try {
    if (cs && cs.getEnvironmentVariable) {
      var envPath = cs.getEnvironmentVariable("ADOBE_PANEL_REPO_ROOT");
      if (envPath && envPath.length > 0) return envPath;
    }
  } catch(e) {}
  
  // 2) Leer desde config.json
  try {
    var configFolder = new Folder(cs.getSystemPath("userSystem") + "/Adobe/CEP/preferences/vibo_adobe_panel");
    if (!configFolder.exists) configFolder.create();
    var configFile = new File(configFolder.fsName + "/config.json");
    if (configFile.exists) {
      configFile.encoding = "UTF-8";
      configFile.open("r");
      var content = configFile.read();
      configFile.close();
      var cfg = JSON.parse(content);
      if (cfg.repo_tools_path && cfg.repo_tools_path.length > 0) {
        return cfg.repo_tools_path;
      }
    }
  } catch(e) {}
  
  // 3) Fallback: ruta relativa desde la ubicacion del panel
  var currentDir = new Folder($.fileName).parent;
  return currentDir.fsName.replace(/\\/g, "/");
}

var REPO_TOOLS = getRepoToolsPath();
var appId = cs.getApplicationID();

var TOOLS = {
  ILST: [
    { label: "Titulos -> fotos individuales", file: "illustrator/scripts/titles_to_photos.jsx" },
    { label: "Revectorizar JPEG + extrusion 3D", file: "illustrator/scripts/logo_revector_extrude.jsx" },
    { label: "Batch: carpeta de logos -> vector+PNG", file: "illustrator/scripts/logo_revector_batch.jsx" },
    { label: "Limpiar logo (nodos)", file: "illustrator/scripts/logo_clean_master.jsx" }
  ],
  PHXS: [
    { label: "Capas -> fotos individuales", file: "photoshop/scripts/layers_to_photos.jsx" }
  ],
  AEFT: [
    { label: "Auto titles + mixer (reactivo al audio)", file: "after_effects/scripts/auto_titles_mixer_ae.jsx" },
    { label: "Titulos -> composiciones", file: "after_effects/scripts/titles_to_comps.jsx" }
  ]
};
TOOLS.PHSP = TOOLS.PHXS; // alias de Photoshop

var HOST_NAMES = { ILST: "Illustrator", PHXS: "Photoshop", PHSP: "Photoshop", AEFT: "After Effects" };

function setStatus(msg, isErr) {
  var el = document.getElementById("status");
  el.textContent = msg || "";
  el.className = "status" + (isErr ? " err" : "");
}

function run(file) {
  var full = REPO_TOOLS + "/" + file;
  var jsx = '(function(){var f=new File("' + full + '");' +
            'if(!f.exists){return "NO_EXISTE:"+f.fsName;}' +
            'try{$.evalFile(f);return "OK";}catch(e){return "ERR:"+e;}})()';
  setStatus("Ejecutando...", false);
  cs.evalScript(jsx, function (res) {
    if (res === "OK") setStatus("Listo. Revisa la app.", false);
    else if (res && res.indexOf("NO_EXISTE:") === 0) setStatus("No encuentro el script:\n" + res.substring(10), true);
    else setStatus("Error: " + res, true);
  });
}

function render() {
  document.getElementById("host").textContent = HOST_NAMES[appId] || ("App: " + appId);
  var list = TOOLS[appId];
  var container = document.getElementById("buttons");
  container.innerHTML = "";

  if (!list) {
    setStatus("Esta app (" + appId + ") no tiene herramientas en el panel todavia.", true);
    return;
  }
  for (var i = 0; i < list.length; i++) {
    (function (item) {
      var btn = document.createElement("button");
      btn.className = "tool";
      btn.textContent = item.label;
      btn.onclick = function () { run(item.file); };
      container.appendChild(btn);
    })(list[i]);
  }
}

render();