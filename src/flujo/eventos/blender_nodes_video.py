"""Variante VIDEO de blender_nodes.py: mismo grafo de nodos probado
(MARCO/HUE/FADE/MEZCLA), pero el CONTENIDO es un video (source='MOVIE')
en vez de un JPG estatico.

NO reemplaza a blender_nodes.py (el camino de imagen estatica sigue
intacto, sin tocar). Reutiliza sus helpers puros (fitwidth_mapping,
hue_de_rgb, labels, _buscar_materiales_flyer, _nodo_por_label,
_color_predominante_bpy, _repuntar_color_predominante, _resolver_ruta)
importandolos como modulo hermano.

Uso (mismo patron que blender_nodes.py):
    blender -b RD_video.blend --python blender_nodes_video.py -- \
        --input input_ig_video.mp4 --frame FRAME2.png \
        --color-png color_predominante.png --salida render_video.mp4 \
        --frame-start 1 --frame-end 600 --fps 30

Solo --input es obligatorio (mismos defaults derivados de la carpeta
del .blend que blender_nodes.py). --frame-end por defecto = duracion
real del clip (leida via bpy.data.images con source MOVIE), asi que un
smoke test se pide explicito con --frame-end 24.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import blender_nodes as bn  # noqa: E402 -- modulo hermano, reusa el grafo probado


def _parse_args(argv):
    args = argv[argv.index("--") + 1:] if "--" in argv else []
    parsed = {
        "frame": None, "input": None, "color_png": None, "salida": None,
        "frame_start": 1, "frame_end": None, "fps": None,
    }
    key_map = {
        "--frame": "frame", "--input": "input", "--color-png": "color_png",
        "--salida": "salida", "--frame-start": "frame_start",
        "--frame-end": "frame_end", "--fps": "fps",
    }
    i = 0
    while i < len(args):
        key = key_map.get(args[i])
        if key is None or i + 1 >= len(args):
            raise SystemExit(f"Argumento no reconocido o sin valor: {args[i]}")
        val = args[i + 1]
        if key in ("frame_start", "frame_end"):
            val = int(val)
        elif key == "fps":
            val = float(val)
        parsed[key] = val
        i += 2
    if not parsed["input"]:
        raise SystemExit("Falta --input (unico argumento obligatorio)")
    return parsed


def build_flyer_nodes_video(mat, nodo_original, frame_path, video_path,
                             hue_objetivo, frame_duration):
    """Como bn.build_flyer_nodes, pero CONTENIDO = video (source MOVIE).

    Reusa el mismo grafo (MARCO/HUE/FADE/MEZCLA); solo el nodo de
    imagen del contenido pasa a ser un ShaderNodeTexImage cuya .image
    tiene source='MOVIE' con image_user configurado para animar.
    """
    import bpy

    ya_existe = bn._nodo_por_label(mat, bn.LBL_MEZCLA) is not None
    tree = mat.node_tree

    video_img = bpy.data.images.load(video_path, check_existing=True)
    if video_img.source != "MOVIE":
        raise SystemExit(
            f"{video_path} no cargo como MOVIE (source={video_img.source}); "
            "revisa el archivo/codec."
        )

    if ya_existe:
        ti = bn._nodo_por_label(mat, bn.LBL_CONTENIDO)
        tf = bn._nodo_por_label(mat, bn.LBL_MARCO)
        hv = bn._nodo_por_label(mat, bn.LBL_HUE)
        mapping = next(n for n in tree.nodes if n.type == "MAPPING" and any(
            l.to_node == ti for l in tree.links if l.from_node == n))
        tf.image = bpy.data.images.load(frame_path, check_existing=True)
        ti.image = video_img
        frame_size = tuple(tf.image.size)
        video_size = tuple(video_img.size)
        (sx, sy), (lx, ly) = bn.fitwidth_mapping(bn.WINDOW_UV, frame_size, video_size)
        mapping.inputs["Scale"].default_value = (sx, sy, 1.0)
        mapping.inputs["Location"].default_value = (lx, ly, 0.0)
        hv.outputs[0].default_value = hue_objetivo
    else:
        # Sin grafo previo: construir con el helper probado usando el
        # video como si fuera la imagen del contenido (mismo tipo de
        # nodo, ShaderNodeTexImage acepta .image con source MOVIE).
        bn.build_flyer_nodes(mat, nodo_original, frame_path, video_path, hue_objetivo)
        ti = bn._nodo_por_label(mat, bn.LBL_CONTENIDO)
        ti.image = video_img  # el helper cargo un STILL; lo reemplazamos por el MOVIE

    ti.image_user.frame_duration = frame_duration
    ti.image_user.frame_start = 1
    ti.image_user.frame_offset = 0
    ti.image_user.use_auto_refresh = True
    return "update" if ya_existe else "build"


def main():
    import bpy
    from blender_gpu import force_gpu  # noqa: E402 -- modulo hermano

    args = _parse_args(sys.argv)
    base_blend = os.path.dirname(bpy.data.filepath) if bpy.data.filepath else ""
    if not args["frame"] and base_blend:
        args["frame"] = os.path.join(base_blend, "FRAME2.png")
    if not args["color_png"] and base_blend:
        args["color_png"] = os.path.join(base_blend, "RESULTADOS",
                                          "color_predominante.png")
    for clave in ("frame", "input", "color_png", "salida"):
        args[clave] = bn._resolver_ruta(args[clave], base_blend)
    for ruta in ("frame", "input"):
        if not args[ruta] or not os.path.exists(args[ruta]):
            raise SystemExit(f"No existe --{ruta}: {args[ruta]}")

    if args["color_png"] and os.path.exists(args["color_png"]):
        color_png = os.path.abspath(args["color_png"])
        rgb = bn._color_predominante_bpy(color_png)
        bn._repuntar_color_predominante(color_png)
    else:
        rgb = (0, 254, 254)
    hue = bn.hue_de_rgb(rgb)
    print(f"Color predominante RGB={rgb} hue={hue:.4f}")

    video_path = os.path.abspath(args["input"])
    probe = bpy.data.images.load(video_path, check_existing=True)
    frame_duration = probe.frame_duration
    print(f"Video: {video_path} frame_duration={frame_duration}")

    frame_start = args["frame_start"] or 1
    frame_end = args["frame_end"] or frame_duration
    if frame_end > frame_duration:
        print(f"Aviso: --frame-end {frame_end} > duracion real {frame_duration}; "
              f"recortando a {frame_duration}.")
        frame_end = frame_duration

    for mat, nodo in bn._buscar_materiales_flyer():
        modo = build_flyer_nodes_video(
            mat, nodo, os.path.abspath(args["frame"]), video_path, hue, frame_duration)
        print(f"Material '{mat.name}' {modo} por nodos VIDEO (sin Photoshop).")

    print(f"GPU: {force_gpu()}")

    scene = bpy.context.scene
    scene.frame_start = frame_start
    scene.frame_end = frame_end
    if args["fps"]:
        scene.render.fps = int(args["fps"])
    # Politica video (LAST_HANDOFF): 128 samples adaptive, SIN denoise.
    scene.cycles.samples = 128
    scene.cycles.use_denoising = False

    if args["salida"]:
        out = os.path.abspath(args["salida"])
        scene.render.filepath = out
        scene.render.image_settings.file_format = "FFMPEG"
        scene.render.ffmpeg.format = "MPEG4"
        scene.render.ffmpeg.codec = "H264"
        scene.render.ffmpeg.constant_rate_factor = "MEDIUM"
        scene.render.ffmpeg.ffmpeg_preset = "GOOD"
        scene.render.ffmpeg.audio_codec = "NONE"
        bpy.ops.render.render(animation=True)
        print(f"Render de video guardado en: {out}")


if __name__ == "__main__":
    main()
