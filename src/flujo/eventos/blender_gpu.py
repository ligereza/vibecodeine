"""Force Cycles to render on GPU (OptiX/CUDA/HIP), never CPU.

Non-destructive: sets device in-memory for this Blender session only, does
NOT modify/save the .blend file. Import and call force_gpu() from any bpy
script BEFORE bpy.ops.render.render(), or run standalone via:
    blender -b file.blend --python blender_gpu.py -f 1
"""


def force_gpu(prefer=("OPTIX", "CUDA", "HIP", "METAL")):
    """Enable the first available GPU compute backend and select all its
    devices. Returns a dict report (backend, devices enabled) for logging.
    Falls back to CPU only if truly no GPU backend is available (never
    silently renders on CPU when a GPU exists)."""
    import bpy

    scene = bpy.context.scene
    if scene.render.engine != "CYCLES":
        return {"engine": scene.render.engine, "note": "not Cycles, GPU device N/A"}

    cprefs = bpy.context.preferences.addons["cycles"].preferences
    chosen = None
    for backend in prefer:
        try:
            cprefs.compute_device_type = backend
            cprefs.get_devices()
            if any(d.type == backend for d in cprefs.devices):
                chosen = backend
                break
        except Exception:
            continue

    if chosen is None:
        scene.cycles.device = "CPU"
        return {"engine": "CYCLES", "device": "CPU", "reason": "no GPU backend detected"}

    enabled = []
    for d in cprefs.devices:
        if d.type == chosen:
            d.use = True
            enabled.append(d.name)
        elif d.type == "CPU":
            d.use = False  # GPU only, CPU stays idle so it doesn't bottleneck

    scene.cycles.device = "GPU"
    return {"engine": "CYCLES", "device": "GPU", "backend": chosen, "devices_enabled": enabled}


if __name__ == "__main__":
    import json
    print("=== GPU_FORCE_JSON_START ===")
    print(json.dumps(force_gpu(), indent=2))
    print("=== GPU_FORCE_JSON_END ===")
