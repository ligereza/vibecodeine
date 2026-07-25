"""Como blender_nodes_video.py pero renderiza PNG por frame (no FFMPEG mux),
con resume: salta frames ya escritos con tamano sano. Reusa el mismo grafo
de nodos probado (blender_nodes.py) via blender_nodes_video.py.

Uso:
    blender -b RD_video.blend --python blender_nodes_video_seq.py -- \
        --input input_ig_video.mp4 --frame FRAME2.png \
        --color-png color_predominante.png --out-dir RESULTADOS/frames_x \
        --frame-start 1 --frame-end 600 --min-size 20000
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import blender_nodes as bn  # noqa: E402
import blender_nodes_video as bnv  # noqa: E402


def _parse_args(argv):
    args = argv[argv.index("--") + 1:] if "--" in argv else []
    parsed = {
        "frame": None, "input": None, "color_png": None, "out_dir": None,
        "frame_start": 1, "frame_end": None, "min_size": 20000,
    }
    key_map = {
        "--frame": "frame", "--input": "input", "--color-png": "color_png",
        "--out-dir": "out_dir", "--frame-start": "frame_start",
        "--frame-end": "frame_end", "--min-size": "min_size",
    }
    i = 0
    while i < len(args):
        key = key_map.get(args[i])
        if key is None or i + 1 >= len(args):
            raise SystemExit(f"Argumento no reconocido o sin valor: {args[i]}")
        val = args[i + 1]
        if key in ("frame_start", "frame_end", "min_size"):
            val = int(val)
        parsed[key] = val
        i += 2
    if not parsed["input"] or not parsed["out_dir"]:
        raise SystemExit("Faltan --input y/o --out-dir (obligatorios)")
    return parsed


def main():
    import bpy
    from blender_gpu import force_gpu  # noqa: E402

    args = _parse_args(sys.argv)
    base_blend = os.path.dirname(bpy.data.filepath) if bpy.data.filepath else ""
    if not args["frame"] and base_blend:
        args["frame"] = os.path.join(base_blend, "FRAME2.png")
    if not args["color_png"] and base_blend:
        args["color_png"] = os.path.join(base_blend, "RESULTADOS", "color_predominante.png")
    for clave in ("frame", "input", "color_png"):
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
        print(f"Aviso: --frame-end {frame_end} > duracion real {frame_duration}; recortando.")
        frame_end = frame_duration

    for mat, nodo in bn._buscar_materiales_flyer():
        modo = bnv.build_flyer_nodes_video(
            mat, nodo, os.path.abspath(args["frame"]), video_path, hue, frame_duration)
        print(f"Material '{mat.name}' {modo} por nodos VIDEO (sin Photoshop).")

    print(f"GPU: {force_gpu()}")

    scene = bpy.context.scene
    scene.cycles.samples = 128
    scene.cycles.use_denoising = False
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"

    out_dir = args["out_dir"]
    os.makedirs(out_dir, exist_ok=True)
    min_size = args["min_size"]

    rendered = 0
    skipped = 0
    for f in range(frame_start, frame_end + 1):
        out_path = os.path.join(out_dir, f"frame_{f:04d}.png")
        if os.path.exists(out_path) and os.path.getsize(out_path) >= min_size:
            skipped += 1
            continue
        scene.frame_set(f)
        scene.render.filepath = out_path
        bpy.ops.render.render(write_still=True)
        rendered += 1
        print(f"OK frame {f}/{frame_end} -> {out_path} "
              f"({os.path.getsize(out_path)} bytes)")

    print(f"Listo: {rendered} renderizados, {skipped} saltados (ya existian).")


if __name__ == "__main__":
    main()
