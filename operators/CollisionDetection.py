import bpy
from functools import partial
import win32gui
import gc
from tqdm import tqdm


def create_overlap_detection_proxy():
    bpy.ops.mesh.primitive_plane_add()
    proxy_obj = bpy.context.object

    geo_modifier: bpy.types.NodesModifier = proxy_obj.modifiers.new(
        name="Geometry Nodes", type='NODES')

    node_tree = bpy.data.node_groups.new(
        name="OverlapDetectionNodeTree", type='GeometryNodeTree')

    geo_modifier.node_group = node_tree

    node_group = geo_modifier.node_group
    inputs = node_group.inputs

    inputs.new(type="NodeSocketObject", name="obj1")
    inputs.new(type="NodeSocketObject", name="obj2")
    node_group.outputs.new(type="NodeSocketGeometry", name="Geometry")

    nodes = node_group.nodes

    group_input: bpy.types.GeometryNodeObjectInfo = nodes.new(
        type="NodeGroupInput")
    group_output: bpy.types.GeometryNodeObjectInfo = nodes.new(
        type="NodeGroupOutput")

    indent = 0
    spacing = 70

    def add_indent():
        nonlocal indent
        indent += 1

    def location():
        nonlocal indent
        nonlocal spacing
        return indent*spacing

    group_input.location.x = location()
    group_input.location.y = 0

    add_indent()
    obj_info1: bpy.types.GeometryNodeObjectInfo = nodes.new(
        type="GeometryNodeObjectInfo")
    obj_info1.location.x = location()
    obj_info1.location.y = 0

    obj_info2: bpy.types.GeometryNodeObjectInfo = nodes.new(
        type="GeometryNodeObjectInfo")
    obj_info2.location.x = location()
    obj_info2.location.y = spacing

    add_indent()
    mesh_boolean: bpy.types.GeometryNodeMeshBoolean = nodes.new(
        type="GeometryNodeMeshBoolean")
    mesh_boolean.location.x = location()
    mesh_boolean.location.y = 0
    mesh_boolean.operation = "INTERSECT"

    add_indent()
    store_attri: bpy.types.GeometryNodeStoreNamedAttribute = nodes.new(
        type="GeometryNodeStoreNamedAttribute")
    store_attri.location.x = location()
    store_attri.location.y = 0
    store_attri.data_type = "BOOLEAN"
    store_attri.inputs["Name"].default_value = "Intersection"

    add_indent()
    group_output.location.x = location()
    group_output.location.y = 0

    links: bpy.types.NodeLinks = node_group.links

    links.new(group_input.outputs["obj1"],    obj_info1.inputs["Object"])
    links.new(group_input.outputs["obj2"],    obj_info2.inputs["Object"])

    links.new(obj_info1.outputs["Geometry"],    mesh_boolean.inputs["Mesh 2"])
    links.new(obj_info2.outputs["Geometry"],    mesh_boolean.inputs["Mesh 2"])

    links.new(mesh_boolean.outputs["Mesh"],    store_attri.inputs["Geometry"])

    links.new(store_attri.outputs["Geometry"],
              group_output.inputs["Geometry"])

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
        proxy.modifiers[0]["Input_0"] = selections[0]
        proxy.modifiers[0]["Input_1"] = selections[1]
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
