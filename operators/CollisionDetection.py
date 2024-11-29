import bpy
from functools import partial
import win32gui
import gc
from tqdm import tqdm


def create_overlap_detection_proxy():
    bpy.ops.mesh.primitive_circle_add(
        enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    bpy.ops.node.new_geometry_nodes_modifier()
    proxy_obj = bpy.context.object
    node_group: bpy.types.NodeGroup = proxy_obj.modifiers[0].node_group
    inputs = node_group.inputs
    inputs.new(type="NodeSocketObject", name="obj1")
    inputs.new(type="NodeSocketObject", name="obj2")

    nodes = node_group.nodes
    obj_info1: bpy.types.GeometryNodeObjectInfo = nodes.new(
        type="GeometryNodeObjectInfo")
    obj_info1.location.x = -140
    obj_info1.location.y = -140

    obj_info2: bpy.types.GeometryNodeObjectInfo = nodes.new(
        type="GeometryNodeObjectInfo")
    obj_info2.location.x = -140
    obj_info2.location.y = -180

    mesh_boolean: bpy.types.GeometryNodeMeshBoolean = nodes.new(
        type="GeometryNodeMeshBoolean")
    mesh_boolean.location.x = 0
    mesh_boolean.location.y = 50
    mesh_boolean.operation = "INTERSECT"

    store_attri: bpy.types.GeometryNodeStoreNamedAttribute = nodes.new(
        type="GeometryNodeStoreNamedAttribute")
    store_attri.location.x = 50
    store_attri.location.y = 0
    store_attri.data_type = "BOOLEAN"
    store_attri.inputs["Name"].default_value = "Intersection"

    links = node_group.links
    input = nodes["Group Input"]
    output = nodes["Group Output"]

    links.new(input.outputs["obj1"],    obj_info1.inputs["Object"])
    links.new(input.outputs["obj2"],    obj_info2.inputs["Object"])

    links.new(obj_info1.outputs["Geometry"],    mesh_boolean.inputs["Mesh 2"])
    links.new(obj_info2.outputs["Geometry"],    mesh_boolean.inputs["Mesh 2"])

    links.new(mesh_boolean.outputs["Mesh"],    store_attri.inputs["Geometry"])

    links.new(store_attri.outputs["Geometry"],    output.inputs["Geometry"])
    return proxy_obj


def get_overlapping_from_proxy(obj):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evalA = obj.evaluated_get(depsgraph)
    return ("Intersection" in evalA.data.attributes and len(evalA.data.attributes["Intersection"].data)) > 0


def enum_windows_callback(hwnd, results):
    class_name = win32gui.GetClassName(hwnd)
    if class_name == "ConsoleWindowClass":
        results.append((hwnd, win32gui.GetWindowText(hwnd)))


def show_blender_system_console():

    windows = []
    win32gui.EnumWindows(enum_windows_callback, windows)

    for hwnd, title in windows:
        if title == "":
            break

    print(f"The Blender console window is {hwnd}")

    # Check if the window is visible or hidden
    is_visible = win32gui.IsWindowVisible(hwnd)

    if is_visible:
        print("The window is visible.")
        win32gui.SetForegroundWindow(hwnd)
    else:
        print("The window is hidden.")
        bpy.ops.wm.console_toggle()


def remove_unused_meshes():
    for mesh in bpy.data.meshes:
        if mesh.users == 0 or mesh.users == None:  # If no object is using this mesh
            bpy.data.meshes.remove(mesh)


def gc_impl():
    # remove_unused_meshes()
    gc.collect()


class CollisionDetection(bpy.types.Operator):
    bl_idname = "ubertools.collision_detection"
    bl_label = "Run Collision Detection"
    bl_description = "Run Collision Detection"

    def execute(self, context):
        try:
            show_blender_system_console()
        except:
            pass

        selections = context.selected_objects
        scene = context.scene
        proxy = create_overlap_detection_proxy()
        proxy.modifiers[0]["Input_2"] = selections[0]
        proxy.modifiers[0]["Input_3"] = selections[1]
        frames = range(scene.frame_start, scene.frame_end+1)

        for v in (pbar := tqdm(frames)):
            pbar.set_description(f"Testing frame: {v}/{scene.frame_end}")
            scene.frame_set(v)
            proxy.update_tag()
            overlap = get_overlapping_from_proxy(proxy)
            # print(f"{v}/{scene.frame_end} =====>   {overlap}")
            if overlap:
                scene.timeline_markers.new(f'overlap_{v:5}', frame=v)

        gc_impl()
        bpy.data.objects.remove(proxy)
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) == 2 and context.selected_objects[0].type == "MESH" and context.selected_objects[1].type == "MESH"
