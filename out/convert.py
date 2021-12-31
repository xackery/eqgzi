import bpy
import os

from bpy.types import ViewLayer

class NpcType:
    def __init__(self, npcid, npcname):
        self.id = npcid
        self.name = npcname
npcs = []

class SpawnGroup:
    def __init__(self, id, spawngroupid):
        self.id = 0
        self.name = ""
        self.spawngroupid = 0
        self.spawn_limit = 0
        self.dist = 0
        self.max_x = 0
        self.min_x = 0
        self.max_y = 0
        self.min_y = 0
        self.delay = 0
        self.mindelay = 15000
        self.despawn = 0
        self.despawn_timer = 0
        self.wp_spawns = 0
spawngroups = {}

class Writer:
    def __init__(self, path):
        self.isCreated = False
        self.path = path
        #self.isLightHeader = False
        #self.isRegionHeader = False
        #self.isMaterialHeader = False
        #self.isSpawn2Header = False
        #self.isSpawnGroupHeader = False
        #self.isModHeader = False
        #self.isEmitHeader = False
        #self.isSndHeader = False
        #fmod = open(out_path + "/" + base_name + "_mod.txt", "w+")
    def write(self, text):
        if not self.isCreated:
            self.w = open(self.path, "w+")
            self.isCreated = True
            if self.path.endswith("_EnvironmentEmitters.txt"):
                fe.write("Name^EmitterDefIdx^X^Y^Z^Lifespan\n")
        self.w.write(text)
    



blend_file_path = bpy.data.filepath
directory = os.path.dirname(blend_file_path)
base_name = os.path.basename(blend_file_path).removesuffix(".blend")
out_path = directory + "/out"
cache_path = directory + "/cache"
sql_path = directory + "/sql"

fe = Writer(out_path + "/" + base_name + "_EnvironmentEmitters.txt")
fsnd = Writer(out_path + "/" + base_name + ".emt")
fl = Writer(cache_path + "/" + base_name + "_light.txt")
fr = Writer(cache_path + "/" + base_name + "_region.txt")
fm = Writer(cache_path + "/" + base_name + "_material.txt")
fsg = Writer(sql_path + "/" + base_name + "_spawngroup.sql")
fs2 = Writer(sql_path + "/" + base_name + "_spawn2.sql")

# Delete contents of out path
if not os.path.exists(out_path):
    os.makedirs(out_path)
print("out path: " + out_path)
for f in os.listdir(out_path):
    print("removing old file in out dir: "+f)
    os.remove(os.path.join(out_path, f))


# Delete contents of cache path
if not os.path.exists(cache_path):
    os.makedirs(cache_path)
print("cache path: " + cache_path)
for f in os.listdir(cache_path):
    print("removing old file in cache dir: "+f)
    os.remove(os.path.join(cache_path, f))

modDefs = {}

def roundFloatStr(value):
    return str(round(value, 4))

def process(o):
    # check for any emitter definitions, any object can contain them
    if o.get("emit_id", 0) != 0:
        print("writing out emit_id "+str(o.get("emit_id", "1"))+" from object "+ o.name)
        fe.write(o.name + "^" + str(o.get("emit_id", "1")) + "^" + roundFloatStr(-o.location.y*2) + "^" + roundFloatStr(o.location.x*2) +"^" + roundFloatStr(o.location.z*2) + "^" + o.get("emit_duration", "90000000") + "\n")   
    if o.get("sound", 0) != 0:
        print("writing out sound "+str(o.get("sound", "1"))+" from object "+ o.name)
        fsnd.write("2,"+o.get("sound", "none.wav")+",0,")
        fsnd.write(str(o.get("sound_active", "0"))+",")
        fsnd.write(roundFloatStr(o.get("sound_volume", 1.0))+",")
        fsnd.write(str(o.get("sound_fade_in", "0"))+",")
        fsnd.write(str(o.get("sound_fade_out", "0"))+",")
        fsnd.write(str(o.get("sound_type", "0"))+",")
        fsnd.write(roundFloatStr(-o.location.y*2)+ ",")
        fsnd.write(roundFloatStr(o.location.x*2)+",")
        fsnd.write(roundFloatStr(o.location.z*2)+",")
        fsnd.write(roundFloatStr(o.get("sound_radius", 15.0))+",")
        fsnd.write(roundFloatStr(o.get("sound_distance", 50.0))+",")
        fsnd.write(str(o.get("sound_rand_distance", "0"))+",")
        fsnd.write(roundFloatStr(o.get("sound_trigger_range", 50.0))+",")
        fsnd.write(str(o.get("sound_min_repeat_delay", "0"))+",")
        fsnd.write(str(o.get("sound_max_repeat_delay", "0"))+",")
        fsnd.write(str(o.get("sound_max_repeat_delay", "0"))+",")
        fsnd.write(str(o.get("sound_xmi_index", "0"))+",")
        fsnd.write(str(o.get("sound_echo", "0"))+",")
        fsnd.write(str(o.get("sound_env_toggle", "1"))+"\n")

    if o.type == 'LIGHT':
        li = o.data
        if li.type == 'POINT':
            lightName = o.name.replace(" ", "-")
            if not lightName.startswith("LIB_") and not lightName.startswith("LIT_"):
                lightName = "LIB_" + lightName
            fl.write(lightName + " " + roundFloatStr(o.location.x*2) + " " + roundFloatStr(-o.location.y*2) + " " + roundFloatStr(o.location.z*2) + " " + roundFloatStr(li.color[0]) + " " + roundFloatStr(li.color[2]) + " " + roundFloatStr(li.color[1]) + " " + roundFloatStr(li.energy/10) + "\n")

    if o.type == 'EMPTY':
        if o.empty_display_type == 'CUBE':
            fr.write(o.name.replace(" ", "-") + " " + roundFloatStr(-o.location.y*2) + " " + roundFloatStr(o.location.x*2) + " " + roundFloatStr(o.location.z*2) + " " + roundFloatStr(o.scale.y*2) + " " + roundFloatStr(-o.scale.x*2) + " " + roundFloatStr((o.scale.z)*2) + " " + roundFloatStr(o.get("unknowna", 0)) + " " + roundFloatStr(o.get("unknownb", 0)) + " " + roundFloatStr(o.get("unknownc", 0)) + "\n")


# apply all modifiers
bpy.ops.object.mode_set(mode = 'OBJECT')
for o in bpy.data.objects:
    bpy.context.view_layer.objects.active = o
    for mod in o.modifiers:
        print("applying modifier " + mod.name + " for " + o.name)
        bpy.ops.object.modifier_apply(modifier=mod.name)

# delete any objects not seen in viewport

for o in bpy.data.objects:
    if not o.visible_get(view_layer=bpy.context.view_layer): 
        print("removing " + o.name + " (not active view)")
        bpy.data.objects.remove(o, do_unlink=True)
        continue

for m in bpy.data.materials:
    fm.write("m " + m.name.replace(" ", "-") + " " + str(m.get("flag", 65536)) + " " + str(m.get("fx", "Opaque_MaxCB1.fx")) + "\n")
    for tree in m.texture_paint_slots:
        print("tree " +tree)
        for node in tree:
            print(node.name)

    for prop in m.items():
        for k in prop:
            if not isinstance(k, str):
                continue
            if k.startswith("e_"):
                eValue = str(m[k])
                if eValue.find(" ") == -1:
                    eValue = "0 "+eValue
                fm.write("e " + m.name.replace(" ", "-") + " " +  k + " " + eValue +"\n")


exportedMods = []
 #bpy.data.objects[0].asset_data
for o in bpy.data.objects:
    if "obj_" in o.name:
        print(o.name + " found as type " + o.type)
        mi = o.data
        print(o.asset_data)
        if o.library:
            print("has lib")
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
    print(o.name + " found as a type " + o.type)
    if o.type == 'EMPTY':
        print("library type?")
        print(o.users_collection)
        if o.library:
            print(o.library)
    process(o)
    if o.type != 'MESH':
        bpy.data.objects.remove(o, do_unlink=True)
        continue
    if o.type == 'MESH' and o.get("id", "0") != "0" and o.get("spawngroupid", "0") != "0":
        id = o.get("id", 0)
        spawngroupid = o.get("spawngroupid", 0)
        if not spawngroupid in spawngroups:
            spawngroups[spawngroupid] = SpawnGroup(id, spawngroupid)
        if o.get("spawngroup.name", "0") != "0":
            spawngroups[spawngroupid].name = o["spawngroup.name"]
        if o.get("spawngroup.spawn_limit", "0") != "0":
            spawngroups[spawngroupid].spawn_limit = o["spawngroup.spawn_limit"]
        if o.get("spawngroup.dist", "0") != "0":
            spawngroups[spawngroupid].dist = o["spawngroup.dist"]
        if o.get("spawngroup.max_x", "0") != "0":
            spawngroups[spawngroupid].dist = o["spawngroup.max_x"]
        if o.get("spawngroup.max_y", "0") != "0":
            spawngroups[spawngroupid].dist = o["spawngroup.max_y"]
        if o.get("spawngroup.min_x", "0") != "0":
            spawngroups[spawngroupid].dist = o["spawngroup.min_x"]
        if o.get("spawngroup.min_y", "0") != "0":
            spawngroups[spawngroupid].dist = o["spawngroup.min_y"]
        if o.get("spawngroup.delay", "0") != "0":
            spawngroups[spawngroupid].dist = o["spawngroup.delay"]
        if o.get("spawngroup.mindelay", "0") != "0":
            spawngroups[spawngroupid].dist = o["spawngroup.mindelay"]
        if o.get("spawngroup.despawn", "0") != "0":
            spawngroups[spawngroupid].dist = o["spawngroup.despawn"]
        if o.get("spawngroup.despawn_timer", "0") != "0":
            spawngroups[spawngroupid].dist = o["spawngroup.despawn_timer"]
        if o.get("spawngroup.wp_spawns", "0") != "0":
            spawngroups[spawngroupid].dist = o["spawngroup.wp_spawns"]
        fs2.write("REPLACE INTO spawn2 (id, spawngroupid, x, y, z, heading, respawntime, variance, pathgrid, version) VALUES("+str(o.get("id", "0")) + ", " +str(o.get("spawngroupid", "0"))+ ", "+str(o.location.x*2)+", "+str(o.location.y*2)+", "+str(o.location.z*2)+", "+str(o.rotation_euler.z)+ ", "+str(o.get("respawntime", "0"))+ ", "+str(o.get("variance", "0"))+ ", "+str(o.get("pathgrid", "0"))+ ", "+str(o.get("version", "0"))+");\r\n")
        bpy.data.objects.remove(o, do_unlink=True)
        continue

for sp in spawngroups:
    fsg.write("REPLACE INTO spawngroup (id, name, spawn_limit, dist, max_x, min_x, max_x, min_y, delay, mindelay, despawn, despawn_timer, wp_spawns) VALUES ("+str(spawngroups[sp].id)+", "+str(spawngroups[sp].name)+", "+str(spawngroups[sp].spawn_limit)+", "+str(spawngroups[sp].dist)+", "+str(spawngroups[sp].max_x)+", "+str(spawngroups[sp].min_x)+", "+str(spawngroups[sp].max_x)+", "+str(spawngroups[sp].min_y)+", "+str(spawngroups[sp].delay)+", "+str(spawngroups[sp].mindelay)+", "+str(spawngroups[sp].despawn)+", "+str(spawngroups[sp].despawn_timer)+", "+str(spawngroups[sp].wp_spawns)+");\r\n")
    
bpy.ops.export_scene.obj(filepath=cache_path + "/" + base_name + '.obj', check_existing=True, axis_forward='-X', axis_up='Z', filter_glob="*.obj;*.mtl", use_selection=False, use_animation=False, use_mesh_modifiers=True, use_edges=True, use_smooth_groups=False, use_smooth_groups_bitflags=False, use_normals=True, use_uvs=True, use_materials=True, use_triangles=True, use_nurbs=False, use_vertex_groups=False, use_blen_objects=True, group_by_object=False, group_by_material=False, keep_vertex_order=False, global_scale=2, path_mode='AUTO')