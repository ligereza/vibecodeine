# =============================================================================
#  THE TRILOGY, FUSED - one Geometry Nodes animation
#  Blender 4.5 LTS · single script · 450 frames = 15 modes x 30 frames · 15 s @ 30 fps
#
#  The three ideas run SIMULTANEOUSLY, one blend mode per 30-frame segment:
#    MEZCLA  : a Simulation Zone iterates b <- b (+)k l once per frame -- each
#              segment is literally 30 iterations toward that mode's fixed point.
#    MAPA    : the address IS the inherited layer: l = u (the point's x-address
#              in [0,1]). The fixed-point structure of each operator becomes a
#              terrain profile over the map; u->R, v->G colors the atlas.
#    RELIEVE : twin objects share the tree. The STRUCTURE twin really displaces
#              (Set Position by b); the GAZE twin stays flat and only carries b
#              into the shader as bump. An orbiting light tells them apart.
#
#  Run in the Scripting tab (Alt+P). Re-run friendly: rebuilds its own
#  collection "TRILOGY_GN" and every node group prefixed "TGN_".
# =============================================================================

import bpy, math

CONFIG = {
    "fps": 30,
    "frames_per_mode": 30,
    "grid_size": 8.0,        # world size of the terrain
    "grid_verts": 128,       # resolution per side
    "b0": 0.15,              # initial base value (same as blend-math-lab)
    "max_height": 2.2,       # world z that b = 1.0 maps to
    "twin_gap": 10.0,        # distance between structure twin and gaze twin
}

# the 15 operators, in the canonical order of blend-math-lab.html
MODE_NAMES = ["normal", "multiply", "screen", "overlay", "hardlight",
              "softlight", "darken", "lighten", "colordodge", "colorburn",
              "difference", "exclusion", "linearburn", "add", "subtract"]

F1 = 1
F_END = len(MODE_NAMES) * CONFIG["frames_per_mode"]     # 450

# ----------------------------------------------------------------------------
# scene reset (re-run friendly)
# ----------------------------------------------------------------------------
scn = bpy.context.scene
scn.frame_start, scn.frame_end = F1, F_END
scn.render.fps = CONFIG["fps"]

if "TRILOGY_GN" in bpy.data.collections:
    col = bpy.data.collections["TRILOGY_GN"]
    for o in list(col.objects):
        bpy.data.objects.remove(o, do_unlink=True)
else:
    col = bpy.data.collections.new("TRILOGY_GN")
    scn.collection.children.link(col)

for ng in [g for g in bpy.data.node_groups if g.name.startswith("TGN_")]:
    bpy.data.node_groups.remove(ng)

# --factory-startup leaves the default Cube/Light/Camera in the scene -- none of
# them belong to TRILOGY_GN, so the Cube renders as a stray white box at the
# world origin. Clear them explicitly (guarded: re-runs may have none left).
for _default_name in ("Cube", "Light", "Camera"):
    _default_obj = bpy.data.objects.get(_default_name)
    if _default_obj is not None:
        bpy.data.objects.remove(_default_obj, do_unlink=True)

def link_obj(obj):
    for c in obj.users_collection:
        c.objects.unlink(obj)
    col.objects.link(obj)
    return obj

# ----------------------------------------------------------------------------
# tiny node-building helpers (every mode group is plain Math/Compare/Switch)
# ----------------------------------------------------------------------------
def _out(sockish):
    """Accept a node (first output), an output socket, or a python float."""
    return sockish

def _plug(nt, dst_input, src):
    if isinstance(src, (int, float)):
        dst_input.default_value = float(src)
    elif hasattr(src, "outputs"):                       # a node -> first output
        nt.links.new(src.outputs[0], dst_input)
    else:                                               # a socket
        nt.links.new(src, dst_input)

def M(nt, op, a, b=None, clamp=False):
    """ShaderNodeMath works inside Geometry Nodes trees."""
    n = nt.nodes.new("ShaderNodeMath")
    n.operation = op
    n.use_clamp = clamp
    _plug(nt, n.inputs[0], a)
    if b is not None:
        _plug(nt, n.inputs[1], b)
    return n

def CMP(nt, op, a, b):
    n = nt.nodes.new("FunctionNodeCompare")
    n.data_type = 'FLOAT'
    n.operation = op                                     # e.g. 'LESS_EQUAL'
    _plug(nt, n.inputs[0], a)
    _plug(nt, n.inputs[1], b)
    return n

def PICK(nt, cond, if_false, if_true):
    """Boolean float switch (avoids ShaderNodeMix socket-index gotchas)."""
    n = nt.nodes.new("GeometryNodeSwitch")
    n.input_type = 'FLOAT'
    _plug(nt, n.inputs["Switch"], cond)
    _plug(nt, n.inputs["False"], if_false)
    _plug(nt, n.inputs["True"], if_true)
    return n

# ----------------------------------------------------------------------------
# one small node group per operator:  (b, l) -> out, all fields
# ----------------------------------------------------------------------------
def new_mode_group(name):
    ng = bpy.data.node_groups.new("TGN_op_" + name, 'GeometryNodeTree')
    ng.interface.new_socket(name="b", in_out='INPUT', socket_type='NodeSocketFloat')
    ng.interface.new_socket(name="l", in_out='INPUT', socket_type='NodeSocketFloat')
    ng.interface.new_socket(name="out", in_out='OUTPUT', socket_type='NodeSocketFloat')
    n_in = ng.nodes.new("NodeGroupInput")
    n_out = ng.nodes.new("NodeGroupOutput")
    return ng, n_in, n_out

def build_mode(name):
    ng, gi, go = new_mode_group(name)
    b, l = gi.outputs["b"], gi.outputs["l"]
    EPS = 1e-4

    if name == "normal":
        res = l
    elif name == "multiply":
        res = M(ng, 'MULTIPLY', b, l).outputs[0]
    elif name == "screen":
        # 1-(1-b)(1-l) = b + l - b*l
        bl = M(ng, 'MULTIPLY', b, l)
        s = M(ng, 'ADD', b, l)
        res = M(ng, 'SUBTRACT', s.outputs[0], bl.outputs[0]).outputs[0]
    elif name in ("overlay", "hardlight"):
        # 2bl                      if pivot <= .5
        # 1 - 2(1-b)(1-l)          else        (pivot: b overlay / l hardlight)
        pivot = b if name == "overlay" else l
        lo = M(ng, 'MULTIPLY', M(ng, 'MULTIPLY', b, l).outputs[0], 2.0)
        ib = M(ng, 'SUBTRACT', 1.0, b)
        il = M(ng, 'SUBTRACT', 1.0, l)
        hi = M(ng, 'SUBTRACT', 1.0,
               M(ng, 'MULTIPLY', M(ng, 'MULTIPLY', ib.outputs[0], il.outputs[0]).outputs[0], 2.0).outputs[0])
        cond = CMP(ng, 'LESS_EQUAL', pivot, 0.5)
        res = PICK(ng, cond.outputs[0], hi.outputs[0], lo.outputs[0]).outputs[0]
    elif name == "softlight":
        # W3C: l<=.5 : b - (1-2l) b (1-b)
        #      else  : b + (2l-1)(d-b),  d = b<=.25 ? ((16b-12)b+4)b : sqrt(b)
        one_m_2l = M(ng, 'SUBTRACT', 1.0, M(ng, 'MULTIPLY', l, 2.0).outputs[0])
        b_1mb = M(ng, 'MULTIPLY', b, M(ng, 'SUBTRACT', 1.0, b).outputs[0])
        lo = M(ng, 'SUBTRACT', b,
               M(ng, 'MULTIPLY', one_m_2l.outputs[0], b_1mb.outputs[0]).outputs[0])
        d_in = M(ng, 'MULTIPLY',
                 M(ng, 'ADD',
                   M(ng, 'MULTIPLY',
                     M(ng, 'SUBTRACT', M(ng, 'MULTIPLY', b, 16.0).outputs[0], 12.0).outputs[0],
                     b).outputs[0],
                   4.0).outputs[0],
                 b)
        d_sq = M(ng, 'SQRT', b)
        d = PICK(ng, CMP(ng, 'LESS_EQUAL', b, 0.25).outputs[0],
                 d_sq.outputs[0], d_in.outputs[0])
        two_l_m1 = M(ng, 'SUBTRACT', M(ng, 'MULTIPLY', l, 2.0).outputs[0], 1.0)
        hi = M(ng, 'ADD', b,
               M(ng, 'MULTIPLY', two_l_m1.outputs[0],
                 M(ng, 'SUBTRACT', d.outputs[0], b).outputs[0]).outputs[0])
        res = PICK(ng, CMP(ng, 'LESS_EQUAL', l, 0.5).outputs[0],
                   hi.outputs[0], lo.outputs[0]).outputs[0]
    elif name == "darken":
        res = M(ng, 'MINIMUM', b, l).outputs[0]
    elif name == "lighten":
        res = M(ng, 'MAXIMUM', b, l).outputs[0]
    elif name == "colordodge":
        # min(1, b / max(1-l, eps))
        den = M(ng, 'MAXIMUM', M(ng, 'SUBTRACT', 1.0, l).outputs[0], EPS)
        res = M(ng, 'MINIMUM', M(ng, 'DIVIDE', b, den.outputs[0]).outputs[0], 1.0).outputs[0]
    elif name == "colorburn":
        # l<=0 -> 0 exactly (reference); else 1 - min(1, (1-b) / l)
        den = M(ng, 'MAXIMUM', l, EPS)
        frac = M(ng, 'DIVIDE', M(ng, 'SUBTRACT', 1.0, b).outputs[0], den.outputs[0])
        burn = M(ng, 'SUBTRACT', 1.0, M(ng, 'MINIMUM', frac.outputs[0], 1.0).outputs[0])
        res = PICK(ng, CMP(ng, 'LESS_EQUAL', l, 0.0).outputs[0],
                   burn.outputs[0], 0.0).outputs[0]
    elif name == "difference":
        res = M(ng, 'ABSOLUTE', M(ng, 'SUBTRACT', b, l).outputs[0]).outputs[0]
    elif name == "exclusion":
        # b + l - 2bl
        s = M(ng, 'ADD', b, l)
        bl2 = M(ng, 'MULTIPLY', M(ng, 'MULTIPLY', b, l).outputs[0], 2.0)
        res = M(ng, 'SUBTRACT', s.outputs[0], bl2.outputs[0]).outputs[0]
    elif name == "linearburn":
        res = M(ng, 'MAXIMUM', M(ng, 'SUBTRACT', M(ng, 'ADD', b, l).outputs[0], 1.0).outputs[0], 0.0).outputs[0]
    elif name == "add":
        res = M(ng, 'MINIMUM', M(ng, 'ADD', b, l).outputs[0], 1.0).outputs[0]
    elif name == "subtract":
        res = M(ng, 'MAXIMUM', M(ng, 'SUBTRACT', b, l).outputs[0], 0.0).outputs[0]
    else:
        raise ValueError("unknown mode %s" % name)

    # final clamp to [0,1] keeps every operator honest (like clamp() in the JS lab)
    clamped = M(ng, 'MINIMUM', M(ng, 'MAXIMUM', res, 0.0).outputs[0], 1.0)
    ng.links.new(clamped.outputs[0], go.inputs["out"])
    return ng

MODE_GROUPS = [build_mode(nm) for nm in MODE_NAMES]

# ----------------------------------------------------------------------------
# the main tree: grid -> address -> simulation-zone iteration -> twins
# ----------------------------------------------------------------------------
main = bpy.data.node_groups.new("TGN_trilogy", 'GeometryNodeTree')
main.interface.new_socket(name="Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
main.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
real_sock = main.interface.new_socket(name="Real Displacement", in_out='INPUT',
                                      socket_type='NodeSocketBool')
real_sock.default_value = True

g_in = main.nodes.new("NodeGroupInput")
g_out = main.nodes.new("NodeGroupOutput")

grid = main.nodes.new("GeometryNodeMeshGrid")
grid.inputs["Size X"].default_value = CONFIG["grid_size"]
grid.inputs["Size Y"].default_value = CONFIG["grid_size"]
grid.inputs["Vertices X"].default_value = CONFIG["grid_verts"]
grid.inputs["Vertices Y"].default_value = CONFIG["grid_verts"]

# address u,v in [0,1] from position (grid is centered at origin)
pos = main.nodes.new("GeometryNodeInputPosition")
sep = main.nodes.new("ShaderNodeSeparateXYZ")
main.links.new(pos.outputs["Position"], sep.inputs["Vector"])
inv = 1.0 / CONFIG["grid_size"]
u = M(main, 'ADD', M(main, 'MULTIPLY', sep.outputs["X"], inv).outputs[0], 0.5)
v = M(main, 'ADD', M(main, 'MULTIPLY', sep.outputs["Y"], inv).outputs[0], 0.5)

# timeline: segment id + local reset flag
stime = main.nodes.new("GeometryNodeInputSceneTime")
f0 = M(main, 'SUBTRACT', stime.outputs["Frame"], float(F1))       # 0-based frame
seg_raw = M(main, 'FLOOR', M(main, 'DIVIDE', f0.outputs[0], float(CONFIG["frames_per_mode"])).outputs[0])
seg = M(main, 'MINIMUM', M(main, 'MAXIMUM', seg_raw.outputs[0], 0.0).outputs[0],
        float(len(MODE_NAMES) - 1))
local = M(main, 'MODULO', f0.outputs[0], float(CONFIG["frames_per_mode"]))
is_reset = CMP(main, 'LESS_THAN', local.outputs[0], 0.5)          # frame 0 of segment

# ── simulation zone: state lives as attribute "b" on the geometry ──────────
sim_in = main.nodes.new("GeometryNodeSimulationInput")
sim_out = main.nodes.new("GeometryNodeSimulationOutput")
sim_in.pair_with_output(sim_out)

main.links.new(grid.outputs["Mesh"], sim_in.inputs["Geometry"])

b_prev_n = main.nodes.new("GeometryNodeInputNamedAttribute")
b_prev_n.data_type = 'FLOAT'
b_prev_n.inputs["Name"].default_value = "b"
b_prev = b_prev_n.outputs["Attribute"]

# all 15 operators evaluate on (b_prev, l=u); IndexSwitch picks the segment's one
idx_switch = main.nodes.new("GeometryNodeIndexSwitch")
idx_switch.data_type = 'FLOAT'
while len(idx_switch.index_switch_items) < len(MODE_NAMES):
    idx_switch.index_switch_items.new()
main.links.new(seg.outputs[0], idx_switch.inputs["Index"])
for i, mg in enumerate(MODE_GROUPS):
    gnode = main.nodes.new("GeometryNodeGroup")
    gnode.node_tree = mg
    main.links.new(b_prev, gnode.inputs["b"])
    main.links.new(u.outputs[0], gnode.inputs["l"])
    main.links.new(gnode.outputs["out"], idx_switch.inputs[i + 1])  # [0] is Index

# reset to b0 on each segment's first frame (also covers frame 1: attr missing -> 0)
b_next = PICK(main, is_reset.outputs[0], idx_switch.outputs[0], CONFIG["b0"])

store_b = main.nodes.new("GeometryNodeStoreNamedAttribute")
store_b.data_type = 'FLOAT'
store_b.domain = 'POINT'
store_b.inputs["Name"].default_value = "b"
main.links.new(sim_in.outputs["Geometry"], store_b.inputs["Geometry"])
main.links.new(b_next.outputs[0], store_b.inputs["Value"])
main.links.new(store_b.outputs["Geometry"], sim_out.inputs["Geometry"])

# ── after the zone: store the address for the shader, then the twin split ──
store_u = main.nodes.new("GeometryNodeStoreNamedAttribute")
store_u.data_type = 'FLOAT'; store_u.domain = 'POINT'
store_u.inputs["Name"].default_value = "addr_u"
main.links.new(sim_out.outputs["Geometry"], store_u.inputs["Geometry"])
main.links.new(u.outputs[0], store_u.inputs["Value"])

store_v = main.nodes.new("GeometryNodeStoreNamedAttribute")
store_v.data_type = 'FLOAT'; store_v.domain = 'POINT'
store_v.inputs["Name"].default_value = "addr_v"
main.links.new(store_u.outputs["Geometry"], store_v.inputs["Geometry"])
main.links.new(v.outputs[0], store_v.inputs["Value"])

# structure twin: really move the points up by b * H; gaze twin: height 0
b_now_n = main.nodes.new("GeometryNodeInputNamedAttribute")
b_now_n.data_type = 'FLOAT'
b_now_n.inputs["Name"].default_value = "b"
height = M(main, 'MULTIPLY', b_now_n.outputs["Attribute"], CONFIG["max_height"])
height_or_0 = PICK(main, g_in.outputs["Real Displacement"], 0.0, height.outputs[0])

off = main.nodes.new("ShaderNodeCombineXYZ")
main.links.new(height_or_0.outputs[0], off.inputs["Z"])
setpos = main.nodes.new("GeometryNodeSetPosition")
main.links.new(store_v.outputs["Geometry"], setpos.inputs["Geometry"])
main.links.new(off.outputs["Vector"], setpos.inputs["Offset"])
# NOTE: the tree is closed with a Set Material node AFTER the material exists
# below -- geometry generated inside GN ignores the object's material slots.

# ----------------------------------------------------------------------------
# material: MAPA address gradient + MEZCLA emission by b + bump for the gaze twin
# ----------------------------------------------------------------------------
mat = bpy.data.materials.get("m_TGN") or bpy.data.materials.new("m_TGN")
mat.use_nodes = True
nt = mat.node_tree
nt.nodes.clear()
bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
out_n = nt.nodes.new("ShaderNodeOutputMaterial")
nt.links.new(bsdf.outputs["BSDF"], out_n.inputs["Surface"])

a_u = nt.nodes.new("ShaderNodeAttribute"); a_u.attribute_name = "addr_u"
a_v = nt.nodes.new("ShaderNodeAttribute"); a_v.attribute_name = "addr_v"
a_b = nt.nodes.new("ShaderNodeAttribute"); a_b.attribute_name = "b"
comb = nt.nodes.new("ShaderNodeCombineColor")
nt.links.new(a_u.outputs["Fac"], comb.inputs["Red"])
nt.links.new(a_v.outputs["Fac"], comb.inputs["Green"])
comb.inputs["Blue"].default_value = 0.15
nt.links.new(comb.outputs["Color"], bsdf.inputs["Base Color"])
bsdf.inputs["Roughness"].default_value = 0.5

# emission pulse = the iteration value itself (2.5*b, like Act I's columns)
emit = nt.nodes.new("ShaderNodeMath"); emit.operation = 'MULTIPLY'
nt.links.new(a_b.outputs["Fac"], emit.inputs[0])
emit.inputs[1].default_value = 2.5
nt.links.new(comb.outputs["Color"], bsdf.inputs["Emission Color"])
nt.links.new(emit.outputs[0], bsdf.inputs["Emission Strength"])

# bump from b: on the flat twin this is the ONLY relief (the gaze)
bump = nt.nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = 0.9
nt.links.new(a_b.outputs["Fac"], bump.inputs["Height"])
nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

# close the GN tree: assign the material to the GENERATED geometry
setmat = main.nodes.new("GeometryNodeSetMaterial")
setmat.inputs["Material"].default_value = mat
main.links.new(setpos.outputs["Geometry"], setmat.inputs["Geometry"])
main.links.new(setmat.outputs["Geometry"], g_out.inputs["Geometry"])

# ----------------------------------------------------------------------------
# the twins + floor + light + camera + markers
# ----------------------------------------------------------------------------
def make_twin(name, x, real):
    mesh = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, mesh)
    link_obj(ob)
    ob.location = (x, 0, 0)
    mod = ob.modifiers.new("Trilogy", 'NODES')
    mod.node_group = main
    mod[real_sock.identifier] = real
    ob.data.materials.append(mat)
    return ob

gap = CONFIG["twin_gap"] / 2.0
make_twin("TWIN_structure", -gap, True)
make_twin("TWIN_gaze", gap, False)

floor_mesh = bpy.data.meshes.new("floor")
floor = bpy.data.objects.new("floor", floor_mesh)
link_obj(floor)
import bmesh
bm = bmesh.new()
bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=25)
bm.to_mesh(floor_mesh); bm.free()
floor.location = (0, 0, -0.01)
fmat = bpy.data.materials.get("m_TGN_floor") or bpy.data.materials.new("m_TGN_floor")
fmat.use_nodes = True
_floor_bsdf = fmat.node_tree.nodes["Principled BSDF"]
_floor_bsdf.inputs["Base Color"].default_value = (.03, .03, .04, 1)
_floor_bsdf.inputs["Roughness"].default_value = 0.35
floor.data.materials.append(fmat)

# orbiting spot: 3 laps over the 450 -- grazing angles change inside every segment
piv = bpy.data.objects.new("light_pivot", None); link_obj(piv)
piv.location = (0, 0, 3.0)
ld = bpy.data.lights.new("orbiter", 'SPOT')
ld.energy = 24000; ld.spot_size = math.radians(85)
ld.spot_blend = 0.35                            # soften the hard spot edge
ld.shadow_soft_size = 0.4
lo = bpy.data.objects.new("orbiter", ld); link_obj(lo)
lo.parent = piv
lo.location = (0, -14, 3.5)
lo.rotation_euler = (math.radians(72), 0, 0)
piv.rotation_euler.z = 0.0
piv.keyframe_insert("rotation_euler", frame=F1)
piv.rotation_euler.z = math.tau * 3
piv.keyframe_insert("rotation_euler", frame=F_END)
try:    # keep the orbit linear (legacy fcurves view, still fine on 4.4/4.5)
    for fc in piv.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = 'LINEAR'
except AttributeError:
    pass

kd = bpy.data.lights.new("fill", 'AREA'); kd.energy = 900; kd.size = 14
ko = bpy.data.objects.new("fill", kd); link_obj(ko)
ko.location = (0, -12, 14); ko.rotation_euler = (math.radians(32), 0, 0)

def cam_pitch_to(cam_loc, target):
    """Euler-X pitch (radians) for a camera on the x=0, yaw=0 axis (this rig's
    camera and CAM_TARGET both sit at world x=0) so it looks at `target`.
    Blender's camera looks down local -Z at rest; rotating by angle a about X
    gives world view-dir (0, sin a, -cos a), so a = atan2(dy, -dz)."""
    dy = target[1] - cam_loc[1]
    dz = target[2] - cam_loc[2]
    return math.atan2(dy, -dz)

CAM_TARGET = (0.0, 0.0, 1.7)  # world-origin track, raised to the twins' visual midline
cam_loc_a = (0, -24, 15)
cam_loc_b = (0, -21, 13.5)                      # slow push-in across the 15 s

cd = bpy.data.cameras.new("CAM")
cd.lens = 35                                    # wide enough for both twins
cam = bpy.data.objects.new("CAM", cd); link_obj(cam)
cam.location = cam_loc_a
cam.rotation_euler = (cam_pitch_to(cam_loc_a, CAM_TARGET), 0, 0)
cam.keyframe_insert("location", frame=F1)
cam.keyframe_insert("rotation_euler", frame=F1)
cam.location = cam_loc_b
cam.rotation_euler = (cam_pitch_to(cam_loc_b, CAM_TARGET), 0, 0)
cam.keyframe_insert("location", frame=F_END)
cam.keyframe_insert("rotation_euler", frame=F_END)
scn.camera = cam

scn.timeline_markers.clear()
for i, nm in enumerate(MODE_NAMES):
    scn.timeline_markers.new(nm.upper(), frame=F1 + i * CONFIG["frames_per_mode"])

scn.world = scn.world or bpy.data.worlds.new("W")
scn.world.use_nodes = True
scn.world.node_tree.nodes["Background"].inputs["Color"].default_value = (.012, .013, .018, 1)
try:
    scn.render.engine = 'BLENDER_EEVEE_NEXT'
except TypeError:
    scn.render.engine = 'BLENDER_EEVEE'

print("TRILOGY_GN ready · %d frames = %d modes x %d · twins: structure vs gaze"
      % (F_END, len(MODE_NAMES), CONFIG["frames_per_mode"]))
print("NOTE: simulation zones evaluate frame by frame -- play from frame 1")
