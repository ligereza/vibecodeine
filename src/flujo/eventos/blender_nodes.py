"""Composicion del flyer POR NODOS dentro de Blender: sin Photoshop.

Reemplaza al Droplet de Photoshop: en vez de esperar flyer_final.jpg, el
material de RD.blend se reconstruye EN MEMORIA para consumir directo
FRAME2.png (marco con ventana recortada por alpha) + input_ig.jpg (flyer ya
disenado que entrega la productora), recoloreando el marco al color
predominante del input. No toca ni guarda el .blend (mismo principio que
blender_gpu.py).

Geometria medida del FRAME2.png real (9898x9899, 2026-07-10, analisis PIL
del archivo en C:/rd/AUTOMATIZACION -- no adivinada): la ventana es el
rectangulo transparente interior, bbox pixel (6488,378)-(9350,4272).

NO se importa desde flujo (import bpy solo existe dentro de Blender):
    blender -b RD.blend --python blender_nodes.py -- \
        --frame FRAME2.png --input input_ig.jpg \
        [--color-png color_predominante.png] [--salida render.png]

Los helpers de matematica (cover + afin UV, hue) son python puro y se
testean sin Blender en tests/test_blender_nodes.py.
"""
import colorsys
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Ventana del marco en coordenadas UV de Blender (origen abajo-izquierda,
# eje Y invertido respecto a pixeles de imagen). Medida, no estimada.
WINDOW_UV = {
    "x0": 0.655486,
    "x1": 0.944635,
    "y0": 0.568441,  # 1 - 4272/9899
    "y1": 0.961814,  # 1 - 378/9899
}


def cover_mapping(window_uv, frame_size, input_size):
    """Escala+offset (afin) para el nodo Mapping del contenido.

    Mapea la region de ventana del UV del marco al recorte central del input
    en modo cover (llena la ventana sin distorsionar; recorta el excedente).
    Devuelve (scale_xy, location_xy) tal que uv_input = uv * scale + location.
    """
    fw_px, fh_px = frame_size
    iw_px, ih_px = input_size
    if min(fw_px, fh_px, iw_px, ih_px) <= 0:
        raise ValueError("dimensiones de imagen invalidas (<= 0)")
    win_w_uv = window_uv["x1"] - window_uv["x0"]
    win_h_uv = window_uv["y1"] - window_uv["y0"]
    if win_w_uv <= 0 or win_h_uv <= 0:
        raise ValueError("ventana UV degenerada")
    win_w_px = win_w_uv * fw_px
    win_h_px = win_h_uv * fh_px

    # cover: el input escala hasta cubrir ambos ejes; la fraccion visible
    # de cada eje queda <= 1 y el resto se recorta centrado.
    k = max(win_w_px / iw_px, win_h_px / ih_px)
    frac_w = win_w_px / (k * iw_px)
    frac_h = win_h_px / (k * ih_px)

    scale_x = frac_w / win_w_uv
    scale_y = frac_h / win_h_uv
    loc_x = (1.0 - frac_w) / 2.0 - window_uv["x0"] * scale_x
    loc_y = (1.0 - frac_h) / 2.0 - window_uv["y0"] * scale_y
    return (scale_x, scale_y), (loc_x, loc_y)


def hue_de_rgb(rgb):
    """Hue [0,1) de un color RGB 0-255 (colorsys, python puro)."""
    r, g, b = (max(0, min(255, int(c))) / 255.0 for c in rgb)
    h, _s, _v = colorsys.rgb_to_hsv(r, g, b)
    return h


def _parse_args(argv):
    """Argumentos despues de '--' (estilo blender_render.py)."""
    args = argv[argv.index("--") + 1:] if "--" in argv else []
    parsed = {"frame": None, "input": None, "color_png": None, "salida": None}
    key_map = {"--frame": "frame", "--input": "input",
               "--color-png": "color_png", "--salida": "salida"}
    i = 0
    while i < len(args):
        key = key_map.get(args[i])
        if key is None or i + 1 >= len(args):
            raise SystemExit(f"Argumento no reconocido o sin valor: {args[i]}")
        parsed[key] = args[i + 1]
        i += 2
    if not parsed["frame"] or not parsed["input"]:
        raise SystemExit("Faltan --frame y/o --input")
    return parsed


def _color_predominante_bpy(color_png_path):
    """Lee el pixel central del PNG de color predominante via bpy (RGB 0-255)."""
    import bpy

    img = bpy.data.images.load(color_png_path)
    try:
        w, h = img.size
        if w <= 0 or h <= 0 or len(img.pixels) < 4:
            raise ValueError(f"imagen de color invalida: {color_png_path}")
        idx = ((h // 2) * w + (w // 2)) * img.channels
        px = img.pixels[idx:idx + 3]
        return tuple(round(c * 255) for c in px)
    finally:
        bpy.data.images.remove(img)


def _buscar_material_flyer():
    """Material cuyo nodo de imagen usa flyer_final -- sin adivinar nombres."""
    import bpy

    for mat in bpy.data.materials:
        if not mat.use_nodes:
            continue
        for node in mat.node_tree.nodes:
            if node.type == "TEX_IMAGE" and node.image and \
                    "flyer_final" in node.image.name.lower():
                return mat, node
    raise SystemExit(
        "No encontre un material con textura flyer_final en el .blend; "
        "el rebuild de nodos espera el RD.blend real (no adivinar)."
    )


def build_flyer_nodes(mat, nodo_original, frame_path, input_path, hue_objetivo):
    """Reconstruye el material: FRAME2 recoloreado sobre el input mapeado.

    El nodo de imagen original (flyer_final.jpg) queda mudo, no se borra:
    los links que salian de su Color pasan a salir de la mezcla nueva.
    """
    import bpy

    tree = mat.node_tree
    nodes, links = tree.nodes, tree.links

    frame_img = bpy.data.images.load(frame_path)
    input_img = bpy.data.images.load(input_path)

    tex_coord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    mapping.vector_type = "POINT"
    (sx, sy), (lx, ly) = cover_mapping(
        WINDOW_UV, tuple(frame_img.size), tuple(input_img.size))
    mapping.inputs["Scale"].default_value = (sx, sy, 1.0)
    mapping.inputs["Location"].default_value = (lx, ly, 0.0)

    tex_input = nodes.new("ShaderNodeTexImage")
    tex_input.image = input_img
    tex_input.extension = "EXTEND"  # sin costuras negras fuera del recorte
    tex_frame = nodes.new("ShaderNodeTexImage")
    tex_frame.image = frame_img

    # Recolor del marco: fijar el hue al del color predominante. Los pixeles
    # neutros (marco negro, blancos) no cambian porque su saturacion es ~0;
    # los acentos verdes saltan al color del evento conservando S y V.
    sep = nodes.new("ShaderNodeSeparateColor")
    sep.mode = "HSV"
    comb = nodes.new("ShaderNodeCombineColor")
    comb.mode = "HSV"
    hue_val = nodes.new("ShaderNodeValue")
    hue_val.outputs[0].default_value = hue_objetivo
    hue_val.label = "hue predominante"

    mezcla = nodes.new("ShaderNodeMix")
    mezcla.data_type = "RGBA"
    mezcla.blend_type = "MIX"

    links.new(tex_coord.outputs["UV"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], tex_input.inputs["Vector"])
    links.new(tex_frame.outputs["Color"], sep.inputs["Color"])
    links.new(hue_val.outputs[0], comb.inputs["Red"])    # H en modo HSV
    links.new(sep.outputs["Green"], comb.inputs["Green"])  # S
    links.new(sep.outputs["Blue"], comb.inputs["Blue"])    # V
    # marco (recoloreado) SOBRE el contenido, segun el alpha del marco
    links.new(tex_frame.outputs["Alpha"], mezcla.inputs["Factor"])
    links.new(tex_input.outputs["Color"], mezcla.inputs["A"])
    links.new(comb.outputs["Color"], mezcla.inputs["B"])

    destinos = [(l.to_node, l.to_socket) for l in tree.links
                if l.from_node is nodo_original and l.from_socket.name == "Color"]
    for l in [l for l in tree.links if l.from_node is nodo_original]:
        tree.links.remove(l)
    for to_node, to_socket in destinos:
        links.new(mezcla.outputs["Result"], to_socket)
    nodo_original.mute = True
    return mezcla


def main():
    import bpy
    from blender_gpu import force_gpu  # noqa: E402 -- modulo hermano

    args = _parse_args(sys.argv)
    for ruta in ("frame", "input"):
        if not os.path.exists(args[ruta]):
            raise SystemExit(f"No existe --{ruta}: {args[ruta]}")

    if args["color_png"] and os.path.exists(args["color_png"]):
        rgb = _color_predominante_bpy(args["color_png"])
    else:
        rgb = (0, 254, 254)  # cyan de referencia del flyer_final validado
    hue = hue_de_rgb(rgb)
    print(f"Color predominante RGB={rgb} hue={hue:.4f}")

    mat, nodo = _buscar_material_flyer()
    build_flyer_nodes(mat, nodo, os.path.abspath(args["frame"]),
                      os.path.abspath(args["input"]), hue)
    print(f"Material '{mat.name}' recompuesto por nodos (sin Photoshop).")

    print(f"GPU: {force_gpu()}")
    if args["salida"]:
        bpy.context.scene.render.filepath = os.path.abspath(args["salida"])
        bpy.ops.render.render(write_still=True)
        print(f"Render guardado en: {args['salida']}")


if __name__ == "__main__":
    main()
