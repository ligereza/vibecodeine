/*
  poblar_contraportadas.jsx  -  Adobe Illustrator ExtendScript

  Lee el master  svg/suplementos_rd/_master_contraportadas.json  y rellena el
  documento ACTIVO con CAPAS nombradas y BLOQUES de texto de AREA (area type),
  editables y REFLOWABLES: editas un parrafo y se re-justifica dentro de
  Illustrator (no hay que regenerar el SVG).

  Capas que crea (o reutiliza si ya existen):
    - titulo        : kicker (PRODUCTO/LINEA) + titulo, centrados
    - descripcion   : encabezado "Descripcion" + un bloque de area con los parrafos
    - nutrientes    : encabezado (Nutrientes/Productos/...) + un bloque con los bullets

  USO
    1) Abre en Illustrator la contraportada del producto (artboard 2000x2800 px).
    2) Fija abajo JSON_PATH (ruta a _master_contraportadas.json) y FLYER_ID.
    3) Archivo > Scripts > Otro script...  (o arrastra este .jsx a Illustrator).

  NOTA: no puedo probarlo aqui; si el texto sale corrido en Y, ajusta Y_SIGN
  (1 <-> -1) o SCALE. Todo lo demas es parametrico abajo.
*/

#target illustrator

(function () {
  // ------------------------------------------------------------------ CONFIG
  var JSON_PATH = "C:/IA/flujo/svg/suplementos_rd/_master_contraportadas.json";
  var FLYER_ID  = "02_impulso";   // id del master; "ALL" = intenta todos por artboard

  var CANVAS_W = 2000, CANVAS_H = 2800;
  var SCALE  = 1;    // px del canvas -> unidades del documento (1 si el doc esta en px)
  var Y_SIGN = -1;   // Illustrator suele medir Y hacia arriba; -1 = "y desde arriba"

  var MARGIN_X = 185, CONTENT_W = CANVAS_W - MARGIN_X * 2;   // ancho de los bloques

  // Coordenadas (px desde arriba) calibradas al mismo layout del generador Python.
  var LY = {
    kicker: 300, title: 403,
    descHeader: 603, descBody: 675,
    itemsHeader: 1205, itemsBody: 1265
  };
  var FS = { kicker: 27, title: 92, header: 48, desc: 44, item: 34 };
  var BODY_H = { desc: 480, items: 780 };  // alto inicial de las cajas (reflow luego)

  var COL = {
    blanco: [242, 242, 242], amarillo: [255, 210, 31], muted: [167, 159, 168]
  };
  var ACCENT = {
    green: [46,204,113], yellow: [255,210,31], purple: [139,77,255],
    blue: [42,141,255], orange: [230,126,34], red: [240,82,75], magenta: [200,0,200]
  };
  var PID_ACCENT = { "04_pre_fiesta": [200,0,200] };

  // ------------------------------------------------------------------ HELPERS
  function readTextFile(path) {
    var f = new File(path);
    if (!f.exists) throw new Error("No existe el JSON: " + path);
    f.encoding = "UTF-8";
    f.open("r");
    var s = f.read();
    f.close();
    return s;
  }

  function parseJSON(str) {
    // ExtendScript no siempre trae JSON.parse; el JSON es JS valido, asi que
    // lo evaluamos (archivo local de confianza).
    if (typeof JSON !== "undefined" && JSON.parse) return JSON.parse(str);
    return eval("(" + str + ")");
  }

  function rgb(arr) {
    var c = new RGBColor();
    c.red = arr[0]; c.green = arr[1]; c.blue = arr[2];
    return c;
  }

  function fontOr(names) {
    for (var i = 0; i < names.length; i++) {
      try { return app.textFonts.getByName(names[i]); } catch (e) {}
    }
    return null;
  }
  var FONT_REG  = fontOr(["ArialMT", "Helvetica", "Arial"]);
  var FONT_BOLD = fontOr(["Arial-BoldMT", "Helvetica-Bold", "Arial-Bold"]);

  function ptTop(yFromTop) { return Y_SIGN * yFromTop * SCALE; }

  function getLayer(doc, name) {
    for (var i = 0; i < doc.layers.length; i++)
      if (doc.layers[i].name === name) return doc.layers[i];
    var l = doc.layers.add();
    l.name = name;
    return l;
  }

  function pointText(layer, xPx, yFromTop, content, sizePx, color, bold, centered) {
    var tf = layer.textFrames.pointText([xPx * SCALE, ptTop(yFromTop)]);
    tf.contents = content;
    var attr = tf.textRange.characterAttributes;
    attr.size = sizePx * SCALE;
    attr.fillColor = rgb(color);
    if ((bold ? FONT_BOLD : FONT_REG)) attr.textFont = bold ? FONT_BOLD : FONT_REG;
    if (centered) tf.paragraphs[0].paragraphAttributes.justification = Justification.CENTER;
    return tf;
  }

  function areaBlock(layer, xPx, yFromTop, widthPx, heightPx, lines, sizePx, color, accentColor) {
    // rectangle(top, left, width, height) -> caja de area type reflowable
    var rect = layer.pathItems.rectangle(
      ptTop(yFromTop), xPx * SCALE, widthPx * SCALE, heightPx * SCALE
    );
    var tf = layer.textFrames.areaText(rect);
    tf.contents = lines.join("\r");           // 1 parrafo por \r -> reflowea
    var attr = tf.textRange.characterAttributes;
    attr.size = sizePx * SCALE;
    attr.fillColor = rgb(color);
    if (FONT_REG) attr.textFont = FONT_REG;
    // interlineado y espacio entre parrafos, para que respire como el SVG
    tf.textRange.characterAttributes.leading = sizePx * 1.25 * SCALE;
    try { tf.textRange.paragraphAttributes.spaceAfter = sizePx * 0.5 * SCALE; } catch (e) {}
    // colorear el bullet inicial de cada parrafo con el acento
    if (accentColor) {
      for (var p = 0; p < tf.paragraphs.length; p++) {
        var par = tf.paragraphs[p];
        if (par.characters.length && par.characters[0].contents === "•")
          par.characters[0].characterAttributes.fillColor = rgb(accentColor);
      }
    }
    return tf;
  }

  // ------------------------------------------------------------------ CONTENIDO
  function buildFlyer(doc, fl) {
    var gen = (fl.type === "general");
    var acc = PID_ACCENT[fl.id] || ACCENT[fl.accent] || ACCENT.magenta;
    var title = gen ? (fl.title || "") : (fl.title || "").toUpperCase();

    // --- capa titulo ---
    var Lt = getLayer(doc, "titulo");
    pointText(Lt, CANVAS_W / 2, LY.kicker, gen ? "LINEA" : "PRODUCTO", FS.kicker, COL.amarillo, true, true);
    pointText(Lt, CANVAS_W / 2, LY.title, title, FS.title, COL.blanco, true, true);

    // --- capa descripcion ---
    var Ld = getLayer(doc, "descripcion");
    pointText(Ld, MARGIN_X, LY.descHeader, "Descripcion", FS.header, COL.amarillo, true, false);
    var desc = fl.description || [];
    if (desc.length)
      areaBlock(Ld, MARGIN_X, LY.descBody, CONTENT_W, BODY_H.desc, desc, FS.desc, COL.blanco, null);

    // --- capa nutrientes ---
    var items = (fl.items || []).length ? fl.items.slice(0) : [];
    if (!items.length) {                       // proteina: versions + usage
      var vs = fl.versions || [];
      for (var i = 0; i < vs.length; i++) {
        var b = vs[i].body || vs[i].desc || vs[i].text || "";
        items.push(((vs[i].title || "") + ": " + b).replace(/^:\s*|\s*:$/g, ""));
      }
      var us = fl.usage;
      if (us) {
        if (us instanceof Array) { for (var u = 0; u < us.length; u++) items.push(String(us[u])); }
        else items.push(String(us));
      }
    }
    var bullets = [];
    for (var k = 0; k < items.length; k++) bullets.push("•  " + items[k]);

    var Ln = getLayer(doc, "nutrientes");
    pointText(Ln, MARGIN_X, LY.itemsHeader, fl.section_title || "Nutrientes", FS.header, COL.amarillo, true, false);
    if (bullets.length)
      areaBlock(Ln, MARGIN_X, LY.itemsBody, CONTENT_W, BODY_H.items, bullets, FS.item, COL.blanco, acc);
  }

  // ------------------------------------------------------------------ MAIN
  if (!app.documents.length) { alert("Abre primero la contraportada en Illustrator."); return; }
  var doc = app.activeDocument;
  try { app.coordinateSystem = CoordinateSystem.ARTBOARDCOORDINATESYSTEM; } catch (e) {}

  var data = parseJSON(readTextFile(JSON_PATH));
  var flyers = data.flyers || [];

  var target = null;
  for (var i = 0; i < flyers.length; i++) if (flyers[i].id === FLYER_ID) target = flyers[i];
  if (FLYER_ID !== "ALL" && !target) { alert("No encontre el flyer id: " + FLYER_ID); return; }

  if (FLYER_ID === "ALL") {
    for (var j = 0; j < flyers.length; j++) buildFlyer(doc, flyers[j]);
    alert("Listo: " + flyers.length + " flyers poblados (revisa capas por artboard).");
  } else {
    buildFlyer(doc, target);
    alert("Listo: '" + FLYER_ID + "' poblado en capas titulo / descripcion / nutrientes.");
  }
})();
