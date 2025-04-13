import bpy
import os
import shutil
from math import pi

# Setup logging to a file
blend_file_path = bpy.data.filepath
if not blend_file_path:
    raise RuntimeError("Script must be run from a saved .blend file")
directory = os.path.dirname(blend_file_path)
log_file = os.path.join(directory, "eqgzi_conversion_log.txt")

# Delete existing log file to start fresh
if os.path.exists(log_file):
    try:
        os.remove(log_file)
        print(f"Deleted existing log file: {log_file}")
    except Exception as e:
        print(f"Failed to delete log file {log_file}: {e}")

def log(message):
    with open(log_file, "a") as f:
        f.write(f"{message}\n")
    print(message)

log("eqgzi v1.9.3 converter (full version with flag fix) starting...")

class npcType:
    def __init__(self, npcid, npcname):
        self.id = npcid
        self.name = npcname
npcs = []

class SpawnGroup:
    def __init__(self, id):
        self.id = id
        self.name = ""
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
        self.w = None
    def IsCreated(self):
        return self.isCreated
    def write(self, text):
        try:
            if not self.isCreated:
                if self.path.find("sql") != -1 and not os.path.exists(sql_path):
                    os.makedirs(sql_path)
                self.w = open(self.path, "w+")
                self.isCreated = True
                if self.path.endswith("_EnvironmentEmitters.txt"):
                    self.w.write("Name^EmitterDefIdx^X^Y^Z^Lifespan\n")
                elif self.path.endswith("_doors.sql"):
                    self.w.write("DELETE FROM doors WHERE zone = '" + base_name + "';\n")
                    self.w.write("INSERT INTO doors (doorid, zone, `name`, pos_x, pos_y, pos_z, heading, opentype, guild, lockpick, keyitem, nokeyring, triggerdoor, triggertype, disable_timer, doorisopen, door_param, dest_zone, dest_instance, dest_x, dest_y, dest_z, dest_heading, invert_state, incline, size, buffer, client_version_mask, is_ldon_door, min_expansion, max_expansion) VALUES\n")
                elif self.path.endswith("_object.sql"):
                    self.w.write("DELETE FROM object WHERE zoneid = " + zoneid + ";\n")
                    self.w.write("INSERT INTO object (zoneid, `version`, xpos, ypos, zpos, heading, itemid, charges, objectname, `type`, icon, unknown08, unknown10, unknown20, unknown24, unknown60, unknown64, unknown68, unknown72, unknown76, unknown84, size, tilt_x, tilt_y, min_expansion, max_expansion) VALUES\n")
            self.w.write(text)
            self.w.flush()  # Ensure data is written to disk immediately
        except Exception as e:
            log(f"Error writing to {self.path}: {e}")
    def close(self):
        if self.isCreated and self.w:
            self.w.close()
            self.isCreated = False

def eulerToHeading(value):
    return round(180 / pi * value / 360 * 512)

def roundFloatStr(value):
    return str(round(value, 4))

base_name = os.path.basename(blend_file_path).replace(".blend", "")
out_path = directory + "/out"
cache_path = directory + "/cache"
sql_path = directory + "/sql"
zoneid = "32"

fe = Writer(out_path + "/" + base_name + "_EnvironmentEmitters.txt")
fsnd = Writer(out_path + "/" + base_name + ".emt")
fl = Writer(cache_path + "/" + base_name + "_light.txt")
fr = Writer(cache_path + "/" + base_name + "_region.txt")
fm = Writer(cache_path + "/" + base_name + "_material.txt")
fmod = Writer(cache_path + "/" + base_name + "_mod.txt")
fsg = Writer(sql_path + "/" + base_name + "_spawngroup_sql")
fs2 = Writer(sql_path + "/" + base_name + "_spawn2.sql")
fdoor = Writer(cache_path + "/" + base_name + "_doors.txt")
fdoorsql = Writer(sql_path + "/" + base_name + "_doors.sql")
fobjectsql = Writer(sql_path + "/" + base_name + "_object.sql")

log("Step 1) Deleting cache / out paths...")
try:
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    log("out path: " + out_path)
    for f in os.listdir(out_path):
        if not os.path.isdir(os.path.join(out_path, f)):
            log("removing old file in out dir: " + f)
            os.remove(os.path.join(out_path, f))

    if not os.path.exists(cache_path):
        os.makedirs(cache_path)
    log("cache path: " + cache_path)
    for f in os.listdir(cache_path):
        if not os.path.isdir(os.path.join(cache_path, f)):
            log("removing old file in cache dir: " + f)
            os.remove(os.path.join(cache_path, f))
except Exception as e:
    log(f"Error in Step 1: {e}")
    raise

modDefs = {}
exported_models = set()
processed_materials = set()

def isImageFile(name):
    for ext in {".dds", ".png", ".jpg"}:
        if name.find(ext) != -1:
            return True
    return False

def process(name, location, o) -> bool:
    try:
        if o.get("emit_id", 0) != 0:
            log("writing out emit_id " + str(o.get("emit_id", "1")) + " from object " + name)
            fe.write(name + "^" + str(o.get("emit_id", "1")) + "^" + roundFloatStr(-location.y*2) + "^" + roundFloatStr(location.x*2) + "^" + roundFloatStr(location.z*2) + "^" + o.get("emit_duration", "90000000") + "\n")
        if o.get("sound", 0) != 0:
            log("writing out sound " + str(o.get("sound", "1")) + " from object " + name)
            fsnd.write("2," + o.get("sound", "none.wav") + ",0,")
            fsnd.write(str(o.get("sound_active", "0")) + ",")
            fsnd.write(roundFloatStr(o.get("sound_volume", 1.0)) + ",")
            fsnd.write(str(o.get("sound_fade_in", "0")) + ",")
            fsnd.write(str(o.get("sound_fade_out", "0")) + ",")
            fsnd.write(str(o.get("sound_type", "0")) + ",")
            fsnd.write(roundFloatStr(-location.y*2) + ",")
            fsnd.write(roundFloatStr(location.x*2) + ",")
            fsnd.write(roundFloatStr(location.z*2) + ",")
            fsnd.write(roundFloatStr(o.get("sound_radius", 15.0)) + ",")
            fsnd.write(roundFloatStr(o.get("sound_distance", 50.0)) + ",")
            fsnd.write(str(o.get("sound_rand_distance", "0")) + ",")
            fsnd.write(roundFloatStr(o.get("sound_trigger_range", 50.0)) + ",")
            fsnd.write(str(o.get("sound_min_repeat_delay", "0")) + ",")
            fsnd.write(str(o.get("sound_max_repeat_delay", "0")) + ",")
            fsnd.write(str(o.get("sound_max_repeat_delay", "0")) + ",")
            fsnd.write(str(o.get("sound_xmi_index", "0")) + ",")
            fsnd.write(str(o.get("sound_echo", "0")) + ",")
            fsnd.write(str(o.get("sound_env_toggle", "1")) + "\n")
        if o.get("object_objectname", 0) != 0:
            log("writing out object " + str(o.get("object_objectname", "0")) + " from object " + name)
            if fobjectsql.IsCreated():
                fobjectsql.write(", \n")
            fobjectsql.write("(" + str(o.get("object_zoneid", zoneid)) + ", ")
            fobjectsql.write(str(o.get("object_version", "0")) + ", ")
            fobjectsql.write(roundFloatStr(-o.location.y*2) + ", " + roundFloatStr(o.location.x*2) + ", " + roundFloatStr(o.location.z*2) + ", ")
            fobjectsql.write(str(eulerToHeading(o.rotation_euler.z)) + ", ")
            fobjectsql.write(str(o.get("object_itemid", "0")) + ", ")
            fobjectsql.write(str(o.get("object_charges", "0")) + ", ")
            fobjectsql.write("'" + str(o.get("object_objectname", "0")) + "', ")
            fobjectsql.write(str(o.get("object_type", "0")) + ", ")
            fobjectsql.write(str(o.get("object_icon", "0")) + ", ")
            fobjectsql.write(str(o.get("object_unknown08", "0")) + ", ")
            fobjectsql.write(str(o.get("object_unknown10", "0")) + ", ")
            fobjectsql.write(str(o.get("object_unknown20", "0")) + ", ")
            fobjectsql.write(str(o.get("object_unknown24", "0")) + ", ")
            fobjectsql.write(str(o.get("object_unknown60", "0")) + ", ")
            fobjectsql.write(str(o.get("object_unknown64", "0")) + ", ")
            fobjectsql.write(str(o.get("object_unknown68", "0")) + ", ")
            fobjectsql.write(str(o.get("object_unknown72", "0")) + ", ")
            fobjectsql.write(str(o.get("object_unknown76", "0")) + ", ")
            fobjectsql.write(str(o.get("object_unknown84", "0")) + ", ")
            fobjectsql.write(str(o.get("object_size", "100")) + ", ")
            fobjectsql.write(str(o.get("object_tilt_x", "0")) + ", ")
            fobjectsql.write(str(o.get("object_tilt_y", "0")) + ", ")
            fobjectsql.write(str(o.get("object_min_expansion", "0")) + ", ")
            fobjectsql.write(str(o.get("object_max_expansion", "0")) + ")")

        if o.get("spawngroup_id", "0") != "0":
            id = o.get("spawn2_id", 0)
            if id == 0 and "_" in o.name and o.name.split("_")[1].isdigit():
                id = o.name.split("_")[1]

            spawngroupid = o.get("spawngroup_id", 0)
            if spawngroupid == 0:
                log("Warning: spawngroup_id is 0 for object " + o.name)
                return False
            if spawngroupid not in spawngroups:
                spawngroups[spawngroupid] = SpawnGroup(spawngroupid)
            if o.get("spawngroup_name", "0") != "0":
                spawngroups[spawngroupid].name = o["spawngroup_name"]
            if o.get("spawngroup_spawn_limit", "0") != "0":
                spawngroups[spawngroupid].spawn_limit = o["spawngroup_spawn_limit"]
            if o.get("spawngroup_dist", "0") != "0":
                spawngroups[spawngroupid].dist = o["spawngroup_dist"]
            if o.get("spawngroup_max_x", "0") != "0":
                spawngroups[spawngroupid].max_x = o["spawngroup_max_x"]
            if o.get("spawngroup_max_y", "0") != "0":
                spawngroups[spawngroupid].max_y = o["spawngroup_max_y"]
            if o.get("spawngroup_min_x", "0") != "0":
                spawngroups[spawngroupid].min_x = o["spawngroup_min_x"]
            if o.get("spawngroup_min_y", "0") != "0":
                spawngroups[spawngroupid].min_y = o["spawngroup_min_y"]
            if o.get("spawngroup_delay", "0") != "0":
                spawngroups[spawngroupid].delay = o["spawngroup_delay"]
            if o.get("spawngroup_mindelay", "0") != "0":
                spawngroups[spawngroupid].mindelay = o["spawngroup_mindelay"]
            if o.get("spawngroup_despawn", "0") != "0":
                spawngroups[spawngroupid].despawn = o["spawngroup_despawn"]
            if o.get("spawngroup_despawn_timer", "0") != "0":
                spawngroups[spawngroupid].despawn_timer = o["spawngroup_despawn_timer"]
            if o.get("spawngroup_wp_spawns", "0") != "0":
                spawngroups[spawngroupid].wp_spawns = o["spawngroup_wp_spawns"]
            fs2.write("REPLACE INTO spawn2 (id, spawngroupid, x, y, z, heading, respawntime, variance, pathgrid, version) VALUES(")
            fs2.write(str(o.get("spawn2_id", "0")) + ", " + str(o.get("spawngroup_id", "0")) + ", ")
            fs2.write(str(location.x*2) + ", " + str(-location.y*2) + ", " + str(location.z*2) + ", ")
            fs2.write(str(eulerToHeading(o.rotation_euler.z)) + ", " + str(o.get("spawn2_respawntime", "0")) + ", ")
            fs2.write(str(o.get("spawn2_variance", "0")) + ", " + str(o.get("spawn2_pathgrid", "0")) + ", ")
            fs2.write(str(o.get("spawn2_version", "0")) + ");\n")
            return False

        if o.type == 'LIGHT':
            li = o.data
            log(f"Processing light {o.name} (type: {li.type}, visible: {o.visible_get()})")
            if li.type == 'POINT':
                lightName = name.replace(" ", "-")
                if not lightName.startswith("LIB_") and not lightName.startswith("LIT_"):
                    lightName = "LIB_" + lightName
                light_data = (lightName + " " + roundFloatStr(-location.x*2) + " " + 
                              roundFloatStr(-location.y*2) + " " + roundFloatStr(location.z*2) + " " + 
                              roundFloatStr(li.color[0]) + " " + roundFloatStr(li.color[2]) + " " + 
                              roundFloatStr(li.color[1]) + " " + roundFloatStr(li.energy/10) + "\n")
                log(f"Attempting to write light data: {light_data.strip()} to {fl.path}")
                try:
                    fl.write(light_data)
                    log(f"Successfully wrote {lightName} to {fl.path}")
                except Exception as e:
                    log(f"Error writing {lightName} to {fl.path}: {e}")
            else:
                log(f"Skipping {o.name} - not a POINT light, type is {li.type}")
            return False

        if o.type == 'EMPTY':
            if o.empty_display_type == 'CUBE':
                fr.write(name.replace(" ", "-") + " " + roundFloatStr(-location.y*2) + " " + roundFloatStr(location.x*2) + " " + roundFloatStr(location.z*2) + " " + roundFloatStr(o.scale.y*2) + " " + roundFloatStr(-o.scale.x*2) + " " + roundFloatStr((o.scale.z)*2) + " " + roundFloatStr(o.get("unknowna", 0)) + " " + roundFloatStr(o.get("unknownb", 0)) + " " + roundFloatStr(o.get("unknownc", 0)) + "\n")
            return False

        if o.name.endswith("_hide"):
            log("Removing " + o.name + " from terrain export (hide suffix)")
            return False
        return True
    except Exception as e:
        log(f"Error processing object {name}: {e}")
        return False

log("Step 2) Applying modifiers...")
try:
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    for o in bpy.data.objects:
        if not o.visible_get():
            continue
        bpy.context.view_layer.objects.active = o
        for mod in o.modifiers:
            log("applying modifier " + mod.name + " for " + o.name)
            bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.ops.object.mode_set(mode='OBJECT')
except Exception as e:
    log(f"Error in Step 2: {e}")
    raise

log("Step 3) Writing material properties for main scene...")
try:
    for m in bpy.data.materials:
        if m.name not in processed_materials:
            flag = m.get("flag", 65536)  # Get custom flag property or default
            fx = m.get("fx", "Opaque_MaxC1.fx")
            fm.write(f"m {m.name.replace(' ', '-')} {flag} {fx}\n")
            processed_materials.add(m.name)
            log(f"Added main scene material {m.name} with flag={flag}, fx={fx}")
        if not m.node_tree or 'Image Texture' not in m.node_tree.nodes:
            continue
        img_node = m.node_tree.nodes['Image Texture']
        if not img_node.image:
            continue
        name = img_node.image.name
        if "." in name:
            name = name.split(".")[0]
        if os.path.isfile(name + ".txt"):
            with open(name + ".txt") as mats:
                for line in mats:
                    line = line.strip()
                    if not isImageFile(line):
                        continue
                    if not os.path.isfile(os.path.join(directory, line)):
                        log(name + ".txt: could not find animated texture " + os.path.join(directory, line))
                        raise FileNotFoundError("Texture file missing")
                    log("copying animated texture to cache: " + line)
                    shutil.copyfile(line, os.path.join("cache", line))
            shutil.copyfile(name + ".txt", os.path.join("cache", name + ".txt"))

        for k, v in m.items():
            if not isinstance(k, str) or not k.startswith("e_"):
                continue
            eValue = str(v)
            if " " not in eValue:
                eValue = "0 " + eValue
            fm.write("e " + m.name.replace(" ", "-") + " " + k + " " + eValue + "\n")
            for entry in eValue.split(" "):
                if ".dds" not in entry:
                    continue
                if not os.path.exists(entry):
                    log("failed to find " + entry + " in current path, defined on material " + m.name)
                    raise FileNotFoundError("DDS file missing")
                log("copying " + entry + " to cache")
                shutil.copyfile(entry, os.path.join("cache", entry))
except Exception as e:
    log(f"Error in Step 3: {e}")
    raise

log("Step 4) Removing any hidden objects...")
try:
    for o in list(bpy.data.objects):
        if not o.visible_get():
            log("removing " + o.name + " (not active view)")
            bpy.data.objects.remove(o, do_unlink=True)
except Exception as e:
    log(f"Error in Step 4: {e}")
    raise

log("Step 5) Exporting any linked objects and their material properties...")
exportedMods = []
try:
    for o in list(bpy.data.objects):
        if not o.visible_get():
            log(o.name + " skipped, it is not visible for export")
            continue
        col = o.instance_collection
        if not col:
            continue
        log(col.name + " has a link instance as " + o.name)

        col.library.reload()
        col = o.instance_collection
        for co in col.objects:
            log(co.name + " found and processed")
            process(o.name, o.location + co.location, co)
            if co.type == 'MESH':
                for mat_slot in co.material_slots:
                    if mat_slot.material and mat_slot.material.name not in processed_materials:
                        m = mat_slot.material
                        flag = m.get("flag", 65536)
                        fx = m.get("fx", "Opaque_MaxC1.fx")
                        mat_name = f"{col.name}-material"
                        fm.write(f"m {mat_name} {flag} {fx}\n")
                        processed_materials.add(m.name)
                        log(f"Added linked material {mat_name} with flag={flag}, fx={fx} for {col.name}")
        
        if not col.library:
            log(col.name + " has no library data, skipping export")
            continue
        
        bpy.ops.object.select_all(action='DESELECT')
        isExported = col.name in exportedMods
        if not isExported:
            log(col.name + " is going to be exported from " + col.library.name)
            exportedMods.append(col.name)
            exported_models.add(col.name)

        objName = col.library.name.replace(".blend", ".obj")

        if o.get("door_id", "0") != "0":
            log(col.name + " has door data")
            fdoor.write(objName + "\n")
            if fdoorsql.IsCreated():
                fdoorsql.write(", \n")
            fdoorsql.write("(" + str(o.get("door_id", "0")) + ", ")
            fdoorsql.write("'" + base_name + "', ")
            fdoorsql.write("'" + objName.replace(" ", "-").replace(".obj", "").upper() + "', ")
            fdoorsql.write(roundFloatStr(o.location.x*2) + ", " + roundFloatStr(-o.location.y*2) + ", " + roundFloatStr(o.location.z*2) + ", ")
            fdoorsql.write(str(eulerToHeading(o.rotation_euler.z)) + ", ")
            fdoorsql.write(str(o.get("door_opentype", "0")) + ", ")
            fdoorsql.write(str(o.get("door_guild", "0")) + ", ")
            fdoorsql.write(str(o.get("door_lockpick", "0")) + ", ")
            fdoorsql.write(str(o.get("door_keyitem", "0")) + ", ")
            fdoorsql.write(str(o.get("door_nokeyring", "0")) + ", ")
            fdoorsql.write(str(o.get("door_door_triggerdoor", "0")) + ", ")
            fdoorsql.write(str(o.get("door_door_triggertype", "0")) + ", ")
            fdoorsql.write(str(o.get("door_disable_timer", "0")) + ", ")
            fdoorsql.write(str(o.get("door_doorisopen", "0")) + ", ")
            fdoorsql.write(str(o.get("door_param", "0")) + ", ")
            fdoorsql.write("'" + str(o.get("door_dest_zone", "NONE")) + "', ")
            fdoorsql.write(str(o.get("door_dest_instance", "0")) + ", ")
            fdoorsql.write(str(o.get("door_dest_x", "0")) + ", ")
            fdoorsql.write(str(o.get("door_dest_y", "0")) + ", ")
            fdoorsql.write(str(o.get("door_dest_z", "0")) + ", ")
            fdoorsql.write(str(o.get("door_dest_heading", "0")) + ", ")
            fdoorsql.write(str(o.get("door_invert_state", "0")) + ", ")
            fdoorsql.write(str(o.get("door_incline", "0")) + ", ")
            fdoorsql.write(str(o.get("door_size", "100")) + ", ")
            fdoorsql.write(str(o.get("door_buffer", "0")) + ", ")
            fdoorsql.write(str(o.get("door_client_version_mask", "4294967295")) + ", ")
            fdoorsql.write(str(o.get("door_is_ldon_door", "0")) + ", ")
            fdoorsql.write(str(o.get("door_min_expansion", "0")) + ", ")
            fdoorsql.write(str(o.get("door_max_expansion", "0")) + ")")
        else:
            fmod.write(objName + " " + o.name.replace(" ", "-") + " " + roundFloatStr(-o.location.y*2) + " " + roundFloatStr(o.location.x*2) + " " + roundFloatStr(o.location.z*2) + " " + roundFloatStr(-o.rotation_euler.y) + " " + roundFloatStr(o.rotation_euler.x) + " " + roundFloatStr(o.rotation_euler.z) + " " + roundFloatStr(o.scale.z) + "\n")

        if isExported:
            log(col.name + " is already exported, only adding placement instance data")
            continue

        obj_file = os.path.join(cache_path, objName)
        for co in col.objects:
            bpy.context.scene.collection.objects.link(co)
            bpy.context.view_layer.objects.active = co
            co.select_set(True)
        log(f"Exporting linked object {objName}")
        bpy.ops.export_scene.obj(filepath=obj_file, check_existing=True, axis_forward='-X', axis_up='Z', filter_glob="*.obj;*.mtl", use_selection=True, use_animation=False, use_mesh_modifiers=True, use_edges=True, use_smooth_groups=False, use_smooth_groups_bitflags=False, use_normals=True, use_uvs=True, use_materials=True, use_triangles=True, use_nurbs=False, use_vertex_groups=False, use_blen_objects=True, group_by_object=False, group_by_material=False, keep_vertex_order=False, global_scale=2, path_mode='COPY')
        
        # Check if Step 5 is removing lights
        log(f"Before removal: Checking instance object {o.name}, type={o.type}")
        if o.get("door_id", "0") == "0":
            for co in col.objects:
                log(f"Checking collection object {co.name}, type={co.type}")
                if co.type == 'MESH':
                    log(f"Removing linked mesh object {co.name} from scene after export")
                    bpy.data.objects.remove(co, do_unlink=True)
                else:
                    log(f"Preserving non-mesh object {co.name} (type={co.type}) in collection")
        else:
            log(f"Preserving all objects in {col.name} as it has door data")

        # Preserve lights at the instance level
        if o.type != 'LIGHT':
            log(f"Removing instance object {o.name}, type={o.type}")
            bpy.data.objects.remove(o, do_unlink=True)
        else:
            log(f"Preserving instance object {o.name} as it is a light")
except Exception as e:
    log(f"Error in Step 5: {e}")
    raise

log("Step 6) Processing zone objects and exporting _mod objects to .mod...")
bpy.ops.object.select_all(action='DESELECT')
try:
    for o in list(bpy.data.objects):
        log(f"Step 6: Processing object {o.name}, type={o.type}")
        if not process(o.name, o.location, o):
            log(f"Step 6: Removing processed object {o.name}, type={o.type}")
            bpy.data.objects.remove(o, do_unlink=True)
            continue
        if "_mdl" in o.name.lower():
            base_obj_name = o.name.lower().replace("_mdl", "").replace(" ", "-")
            objName = base_obj_name + ".obj"
            obj_file = os.path.join(cache_path, objName)
            bpy.ops.object.select_all(action='DESELECT')
            o.select_set(True)
            bpy.context.view_layer.objects.active = o
            log(f"Step 6: Exporting {o.name} as {objName}")
            bpy.ops.export_scene.obj(filepath=obj_file, check_existing=True, axis_forward='-X', axis_up='Z', filter_glob="*.obj;*.mtl", use_selection=True, use_animation=False, use_mesh_modifiers=True, use_edges=True, use_smooth_groups=False, use_smooth_groups_bitflags=False, use_normals=True, use_uvs=True, use_materials=True, use_triangles=True, use_nurbs=False, use_vertex_groups=False, use_blen_objects=True, group_by_object=False, group_by_material=False, keep_vertex_order=False, global_scale=2, path_mode='COPY')
            fmod.write(objName + " " + o.name.replace(" ", "-") + " " + roundFloatStr(0) + " " + roundFloatStr(0) + " " + roundFloatStr(0) + " " + roundFloatStr(0) + " " + roundFloatStr(0) + " " + roundFloatStr(0) + " " + roundFloatStr(0) + "\n")
            log(f"Step 6: Removing exported _mod object {o.name}")
            bpy.data.objects.remove(o, do_unlink=True)
except Exception as e:
    log(f"Error in Step 6: {e}")
    raise

if fobjectsql.IsCreated():
    fobjectsql.write(";\n")

for sp in spawngroups:
    fsg.write("REPLACE INTO spawngroup (id, name, spawn_limit, dist, max_x, min_x, max_y, min_y, delay, mindelay, despawn, despawn_timer, wp_spawns) VALUES (" + str(spawngroups[sp].id) + ", '" + str(spawngroups[sp].name) + "', " + str(spawngroups[sp].spawn_limit) + ", " + str(spawngroups[sp].dist) + ", " + str(spawngroups[sp].max_x) + ", " + str(spawngroups[sp].min_x) + ", " + str(spawngroups[sp].max_y) + ", " + str(spawngroups[sp].min_y) + ", " + str(spawngroups[sp].delay) + ", " + str(spawngroups[sp].mindelay) + ", " + str(spawngroups[sp].despawn) + ", " + str(spawngroups[sp].despawn_timer) + ", " + str(spawngroups[sp].wp_spawns) + ");\n")

log("Step 7) Exporting remaining objects to zone .obj")
try:
    remaining_objects = [o.name for o in bpy.data.objects if o.type == 'MESH']
    if remaining_objects:
        log("Objects exported to terrain .obj: " + ", ".join(remaining_objects))
        bpy.ops.export_scene.obj(filepath=cache_path + "/" + base_name + ".obj", check_existing=True, axis_forward='-X', axis_up='Z', filter_glob="*.obj;*.mtl", use_selection=False, use_animation=False, use_mesh_modifiers=True, use_edges=True, use_smooth_groups=False, use_smooth_groups_bitflags=False, use_normals=True, use_uvs=True, use_materials=True, use_triangles=True, use_nurbs=False, use_vertex_groups=False, use_blen_objects=True, group_by_object=False, group_by_material=False, keep_vertex_order=False, global_scale=2, path_mode='COPY')
    else:
        log("No remaining objects to export to terrain .obj")
except Exception as e:
    log(f"Error in Step 7: {e}")
    raise

log("Closing all output files...")
fe.close()
fsnd.close()
fl.close()
fr.close()
fm.close()
fmod.close()
fsg.close()
fs2.close()
fdoor.close()
fdoorsql.close()
fobjectsql.close()

log("Script completed successfully")