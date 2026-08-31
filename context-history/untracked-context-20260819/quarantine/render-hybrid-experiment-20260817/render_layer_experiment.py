#!/usr/bin/env python3
"""Render one bounded static/dynamic layer experiment from a .blend copy.

The script is invoked by Blender and never saves the loaded blend. Static mode
renders the scene without the movie screen and animated cylinders. Dynamic
mode keeps the movie screen, animated cylinders, floor and reflection-heavy
objects, hides the rest, and renders with transparent film for compositing.
"""
from __future__ import annotations

import argparse
import bmesh
import os
import sys
import time
from pathlib import Path

import bpy


EVENTS_DIR = Path(__file__).resolve().parents[1] / "src" / "flujo" / "eventos"
sys.path.insert(0, str(EVENTS_DIR))
import blender_nodes as bn  # noqa: E402
import blender_nodes_video as bnv  # noqa: E402
from blender_gpu import force_gpu  # noqa: E402


DYNAMIC_OBJECTS = {"Cylinder", "Cylinder.002", "Tablet.002"}
REFLECTION_MATERIALS = {
    "Metal04 PBR", "Metal", "Rusty Metal", "Glass", "Glass.001",
    "GlassFrosty", "GlassDirty", "Decorative Glass 05", "Liquid1",
    "LiquidBlue.003", "Simple Crystal.001", "PlasticBlack",
    "Translucent Plastic", "RubberGreen", "Stylized Water.001",
    "Material.002", "Material.008",
}


def parse_args():
    values = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True, type=Path)
    parser.add_argument(
        "--mode", choices=("static", "scene_static", "dynamic", "floor", "foreground", "screen_only", "reflection", "reflection_base"),
        required=True,
    )
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--frame", type=int, default=1)
    parser.add_argument("--samples", type=int, default=128)
    parser.add_argument("--resolution-scale", type=int, default=100)
    parser.add_argument(
        "--downscale-screen", type=int, default=0,
        help="experimental max dimension for the unused static flyer image",
    )
    parser.add_argument(
        "--drop-legacy-screen-stills", action="store_true",
        help="unlink legacy flyer still nodes after the video path is selected",
    )
    return parser.parse_args(values)


def install_movie(video_path: Path) -> int:
    image = bpy.data.images.load(str(video_path), check_existing=True)
    duration = image.frame_duration
    color_path = Path("/home/mak/RD/AUTOMATIZACION/RESULTADOS/color_predominante.png")
    if color_path.exists():
        rgb = bn._color_predominante_bpy(str(color_path))
        bn._repuntar_color_predominante(str(color_path))
    else:
        rgb = (0, 254, 254)
    hue = bn.hue_de_rgb(rgb)
    frame_path = "/home/mak/RD/AUTOMATIZACION/FRAME2.png"
    try:
        flyer_materials = bn._buscar_materiales_flyer()
    except SystemExit:
        flyer_materials = []
    if flyer_materials:
        for material, node in flyer_materials:
            bnv.build_flyer_nodes_video(
                material, node, frame_path, str(video_path), hue, duration,
            )
        return len(flyer_materials)
    return bnv.swap_existing_movie_nodes(str(video_path), duration)


def downscale_unused_screen_image(max_dimension: int) -> dict | None:
    """Reduce the oversized still retained by the legacy screen material."""
    if max_dimension <= 0:
        return None
    image = bpy.data.images.get("flyer_final.jpg")
    if image is None or (image.size[0] <= max_dimension and image.size[1] <= max_dimension):
        return None
    old_size = tuple(image.size)
    scale = max_dimension / max(old_size)
    image.scale(max(1, round(old_size[0] * scale)), max(1, round(old_size[1] * scale)))
    return {"image": image.name, "old_size": old_size, "new_size": tuple(image.size)}


def drop_legacy_screen_stills(enabled: bool) -> list[str]:
    """Unlink only obsolete stills retained beside the live video nodes."""
    if not enabled:
        return []
    removed = []
    for material_name in ("Material.002", "Material.008"):
        material = bpy.data.materials.get(material_name)
        if not material or not material.use_nodes:
            continue
        for node in material.node_tree.nodes:
            image = getattr(node, "image", None)
            if image and image.name in {"flyer_final.jpg", "prueba.png"}:
                removed.append(f"{material_name}:{node.name}:{image.name}")
                node.image = None
    for image_name in ("flyer_final.jpg", "prueba.png"):
        image = bpy.data.images.get(image_name)
        if image and image.users == 0:
            bpy.data.images.remove(image)
    return removed


def create_screen_subset(scene):
    """Create an unsaved mesh containing only Tablet.002 video faces."""
    source = scene.objects.get("Tablet.002")
    if source is None or source.type != "MESH":
        raise SystemExit("SCREEN_OBJECT_NOT_FOUND: Tablet.002")
    video_material_indices = {3, 4}
    bm = bmesh.new()
    bm.from_mesh(source.data)
    delete_faces = [face for face in bm.faces if face.material_index not in video_material_indices]
    bmesh.ops.delete(bm, geom=delete_faces, context="FACES")
    mesh = bpy.data.meshes.new("__LAYER_SCREEN_ONLY_MESH")
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    screen = source.copy()
    screen.name = "__LAYER_SCREEN_ONLY"
    screen.data = mesh
    screen.matrix_world = source.matrix_world.copy()
    scene.collection.objects.link(screen)
    return screen


def uses_reflection_material(obj) -> bool:
    return any(
        slot.material and slot.material.name in REFLECTION_MATERIALS
        for slot in obj.material_slots
    )


def configure_visibility(scene, mode):
    previous = []
    if mode == "static":
        keep = DYNAMIC_OBJECTS
    elif mode == "scene_static":
        keep = {obj.name for obj in scene.objects}
    elif mode == "floor":
        keep = {"Base"}
    elif mode == "foreground":
        keep = set(DYNAMIC_OBJECTS)
    elif mode == "screen_only":
        keep = {"__LAYER_SCREEN_ONLY"}
    elif mode == "reflection":
        keep = set(DYNAMIC_OBJECTS)
        keep.add("Base")
    elif mode == "reflection_base":
        keep = {"Base"}
        keep.update(obj.name for obj in scene.objects if uses_reflection_material(obj))
        # The baseline must contain the static reflective surfaces, but none of
        # the moving/video objects.  Tablet.002 can use a reflective material,
        # so material-based inclusion alone would leak the dynamic screen into
        # this pass and invalidate the reflection delta.
        keep.difference_update(DYNAMIC_OBJECTS)
    else:
        keep = set(DYNAMIC_OBJECTS)
        keep.add("Base")
        keep.update(obj.name for obj in scene.objects if uses_reflection_material(obj))
    for obj in scene.objects:
        previous.append((obj, obj.hide_render))
        if mode == "static":
            obj.hide_render = obj.name in DYNAMIC_OBJECTS
        elif mode == "scene_static":
            obj.hide_render = obj.name in {"Cylinder", "Cylinder.002"}
        else:
            obj.hide_render = obj.name not in keep
    return previous, len(keep), sum(1 for obj in scene.objects if obj.hide_render)


def main():
    args = parse_args()
    video = args.video.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if not video.is_file():
        raise SystemExit(f"VIDEO_NOT_FOUND: {video}")
    output.parent.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    # The source blend has an identity compositor with multiple Render Layers.
    # For isolated layers it forces the transparent world to opaque RGBA, so
    # disable it only in this unsaved experiment and let Blender emit the raw
    # film alpha needed by the compositor outside this script.
    scene.use_nodes = False
    gpu = force_gpu(prefer=("CUDA", "OPTIX", "HIP"))
    if gpu.get("device") != "GPU":
        raise SystemExit(f"GPU_REQUIRED: {gpu}")
    screen_image = downscale_unused_screen_image(args.downscale_screen)
    movie_nodes = install_movie(video)
    # The video builder must see the legacy material nodes first; only then can
    # the now-unreferenced still image be unlinked safely.
    dropped_screen_stills = drop_legacy_screen_stills(args.drop_legacy_screen_stills)
    temporary_screen = create_screen_subset(scene) if args.mode == "screen_only" else None
    scene.frame_set(args.frame)
    scene.cycles.samples = args.samples
    scene.cycles.use_denoising = False
    scene.render.use_simplify = True
    scene.cycles.texture_limit_render = "2048"
    scene.cycles.use_auto_tile = True
    scene.cycles.tile_size = 512
    scene.render.use_persistent_data = False
    scene.render.image_settings.file_format = "PNG"
    scene.render.resolution_percentage = args.resolution_scale
    scene.render.filepath = str(output)
    scene.render.film_transparent = args.mode != "static"
    scene.render.image_settings.color_mode = "RGBA" if args.mode != "static" else "RGB"
    previous, keep_count, hidden_count = configure_visibility(scene, args.mode)
    started = time.monotonic()
    try:
        bpy.ops.render.render(write_still=True)
    finally:
        for obj, hidden in previous:
            obj.hide_render = hidden
        if temporary_screen is not None:
            mesh = temporary_screen.data
            bpy.data.objects.remove(temporary_screen, do_unlink=True)
            bpy.data.meshes.remove(mesh)
    elapsed = time.monotonic() - started
    print(
        "LAYER_RENDER_OK",
        {
            "mode": args.mode,
            "output": str(output),
            "seconds": round(elapsed, 3),
            "movie_nodes": movie_nodes,
            "kept_name_count": keep_count,
            "hidden_objects": hidden_count,
            "samples": scene.cycles.samples,
            "gpu": gpu,
            "film_transparent": scene.render.film_transparent,
            "resolution_scale": args.resolution_scale,
            "screen_image": screen_image,
            "dropped_screen_stills": dropped_screen_stills,
        },
        flush=True,
    )


if __name__ == "__main__":
    main()
