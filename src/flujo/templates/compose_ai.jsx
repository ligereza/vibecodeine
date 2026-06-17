// compose_ai.jsx — Flujo v0.15
// Script para Adobe Illustrator (doble clic)
// Coloca input_ig.jpg como imagen linked + swatches

#target illustrator

function main() {
    var baseFolder = Folder.current;
    var inputFile = new File(baseFolder + "/input/input_ig.jpg");

    if (!inputFile.exists) {
        alert("No se encontró input/input_ig.jpg");
        return;
    }

    var doc = app.documents.add(DocumentColorSpace.RGB, 1080, 1920);
    doc.artboards[0].name = baseFolder.name;

    var placed = doc.placedItems.add();
    placed.file = inputFile;
    placed.name = "Imagen IG (Linked)";

    var scale = (1920 / placed.height) * 100;
    placed.resize(scale, scale);
    placed.position = [(1080 - placed.width) / 2, 1920 - placed.height];

    var palette = [
        [255, 0, 127],
        [0, 255, 200],
        [25, 25, 25],
        [255, 255, 255],
        [140, 90, 220]
    ];
    var names = ["Principal", "Acento", "Fondo", "Texto", "Secundario"];

    for (var i = 0; i < palette.length; i++) {
        var c = new RGBColor();
        c.red = palette[i][0];
        c.green = palette[i][1];
        c.blue = palette[i][2];

        var sw = doc.swatches.add();
        sw.name = names[i];
        sw.color = c;
    }

    alert("Documento listo para Illustrator");
}

main();
