#!/usr/bin/env python3
"""Experimental static-diffuse bake that keeps glossy/video response live.

The source blend is never saved. For selected opaque, non-metallic static
objects, Cycles bakes direct+indirect diffuse light at frame 1 into an image.
The copied material then adds that baked diffuse radiance to the original
Principled shader with Base Color black, preserving its glossy response.

This is intentionally a bounded experiment: it does not bake the floor,
glass, liquid, runtime video screen, animated objects, or any reflection-heavy
material. A caller must provide a separate output blend.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy


SKIP_MATERIALS = {
    "Material.002", "Material.008", "Decorative Glass 05", "Glass",
    "Glass.001", "GlassFrosty", "Liquid1", "LiquidBlue.003",
    "Simple Crystal.001", "Stylized Water", "Tube", "Watte",
    "Metal04 PBR", "Metal", "Rusty Metal",
}


def parse_args():
    values = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--resolution", type=int, default=512)
    parser.add_argument("--objects", nargs="+", required=True)
    return parser.parse_args(values)


def is_static_opaque_nonmetal(obj, material):
    if obj.type != "MESH" or not obj.data.uv_layers:
        return False
    if obj.animation_data or obj.data.animation_data:
        return False
    if material.name in SKIP_MATERIALS or not material.use_nodes:
        return False
    if any(getattr(node, "image", None) and node.image.source == "MOVIE"
           for node in material.node_tree.nodes):
        return False
    principled = next((node for node in material.node_tree.nodes
                       if node.bl_idname == "ShaderNodeBsdfPrincipled"), None)
    if not principled:
        return False
    metallic = principled.inputs.get("Metallic")
    alpha = principled.inputs.get("Alpha")
    transmission = principled.inputs.get("Transmission Weight")
    if not metallic or metallic.is_linked or float(metallic.default_value) >= 0.1:
        return False
    if alpha and not alpha.is_linked and float(alpha.default_value) < 0.99:
        return False
    if transmission and not transmission.is_linked and float(transmission.default_value) > 0.01:
        return False
    return True


def active_target(tree, image):
    target = tree.nodes.new("ShaderNodeTexImage")
    target.name = "BAKED STATIC DIFFUSE"
    target.label = "BAKED STATIC DIFFUSE (frame 1)"
    target.image = image
    for node in tree.nodes:
        node.select = False
    target.select = True
    tree.nodes.active = target
    return target


def bake_one(scene, obj, slot_index, source_material, resolution):
    material = source_material.copy()
    material.name = f"{source_material.name}__HYBRID_{obj.name}"
    obj.material_slots[slot_index].material = material
    tree = material.node_tree
    principled = next(node for node in tree.nodes
                      if node.bl_idname == "ShaderNodeBsdfPrincipled")
    image = bpy.data.images.new(
        name=f"BAKE_STATIC_DIFFUSE_{obj.name}_{slot_index}",
        width=resolution, height=resolution, alpha=True, float_buffer=False,
    )
    image.colorspace_settings.name = "sRGB"
    target = active_target(tree, image)

    for other in bpy.context.selected_objects:
        other.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    obj.active_material_index = slot_index

    scene.render.bake.target = "IMAGE_TEXTURES"
    scene.render.bake.use_clear = True
    scene.render.bake.margin = 16
    scene.render.bake.margin_type = "ADJACENT_FACES"
    scene.render.bake.width = resolution
    scene.render.bake.height = resolution
    scene.render.bake.use_selected_to_active = False
    scene.render.bake.use_pass_color = True
    scene.render.bake.use_pass_direct = True
    scene.render.bake.use_pass_indirect = True
    scene.render.bake.use_pass_diffuse = True
    scene.render.bake.use_pass_glossy = False
    scene.render.bake.use_pass_transmission = False
    scene.render.bake.use_pass_emit = False
    scene.frame_set(1)
    bpy.ops.object.bake(type="DIFFUSE")

    # Keep the original Principled closure for live glossy/specular response,
    # but remove its diffuse contribution and add the baked diffuse radiance.
    base_color = principled.inputs.get("Base Color")
    if base_color:
        for link in list(tree.links):
            if link.to_socket == base_color:
                tree.links.remove(link)
        base_color.default_value = (0.0, 0.0, 0.0, 1.0)
    emission = tree.nodes.new("ShaderNodeEmission")
    emission.name = "BAKED DIFFUSE RADIANCE"
    emission.inputs["Strength"].default_value = 1.0
    tree.links.new(target.outputs["Color"], emission.inputs["Color"])
    add = tree.nodes.new("ShaderNodeAddShader")
    output = next(node for node in tree.nodes
                  if node.bl_idname == "ShaderNodeOutputMaterial")
    for link in list(tree.links):
        if link.to_node == output and link.to_socket == output.inputs["Surface"]:
            tree.links.remove(link)
    tree.links.new(principled.outputs["BSDF"], add.inputs[0])
    tree.links.new(emission.outputs[0], add.inputs[1])
    tree.links.new(add.outputs[0], output.inputs["Surface"])
    image.pack()
    return {
        "object": obj.name,
        "slot": slot_index,
        "source_material": source_material.name,
        "hybrid_material": material.name,
        "image": image.name,
        "resolution": [resolution, resolution],
        "bake": "DIFFUSE direct+indirect at frame 1",
        "glossy_preserved": True,
    }


def main():
    args = parse_args()
    output = args.output.expanduser().resolve()
    source = Path(bpy.data.filepath).resolve()
    if output == source:
        raise SystemExit("OUTPUT_MUST_DIFFER_FROM_SOURCE")
    if args.resolution < 256 or args.resolution > 2048:
        raise SystemExit("RESOLUTION_OUT_OF_BOUNDS")
    output.parent.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    hidden = []
    # Exclude known dynamic geometry and the runtime screen from the static
    # lighting contribution. Their live shaders remain in the saved copy.
    for obj in scene.objects:
        if (obj.animation_data or getattr(obj.data, "animation_data", None)
                or obj.name == "Tablet.002"):
            hidden.append((obj, obj.hide_render))
            obj.hide_render = True

    results = []
    skipped = []
    try:
        for object_name in args.objects:
            obj = scene.objects.get(object_name)
            if not obj:
                skipped.append({"object": object_name, "reason": "OBJECT_NOT_FOUND"})
                continue
            for slot_index, slot in enumerate(obj.material_slots):
                material = slot.material
                if not material or not is_static_opaque_nonmetal(obj, material):
                    skipped.append({
                        "object": obj.name, "slot": slot_index,
                        "material": material.name if material else None,
                        "reason": "NOT_STATIC_OPAQUE_NONMETAL",
                    })
                    continue
                print(f"HYBRID_BAKE_START: {obj.name} / {material.name}", flush=True)
                results.append(bake_one(scene, obj, slot_index, material, args.resolution))
                print(f"HYBRID_BAKE_OK: {obj.name} / {material.name}", flush=True)
    finally:
        for obj, previous in hidden:
            obj.hide_render = previous

    bpy.ops.wm.save_as_mainfile(filepath=str(output))
    report = {
        "source": str(source), "output": str(output), "scene": scene.name,
        "requested_objects": args.objects, "baked": results, "skipped": skipped,
        "dynamic_excluded": [obj.name for obj, _ in hidden],
        "glossy_preserved": True,
        "source_never_saved": True,
    }
    print("HYBRID_BAKE_JSON_BEGIN")
    print(json.dumps(report, indent=2, ensure_ascii=True))
    print("HYBRID_BAKE_JSON_END")
    print(f"HYBRID_BAKE_COMPLETE: {output}")


if __name__ == "__main__":
    main()
