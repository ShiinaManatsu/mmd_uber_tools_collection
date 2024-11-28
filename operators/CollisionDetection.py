import bpy
from functools import partial
import win32gui


def apply_shape_keys(obj):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.shape_key_remove(all=True, apply_mix=True)


def apply_all_modifiers(obj):
    """Apply all modifiers to the object except the Boolean modifier."""
    bpy.context.view_layer.objects.active = obj
    for mod in obj.modifiers:
        if mod.type != 'BOOLEAN':
            bpy.ops.object.modifier_apply(modifier=mod.name)


def check_boolean_intersection_with_modifiers(obj1, obj2):
    """Check for intersection using the Boolean modifier, with modifiers applied."""

    # Copy the objects to avoid modifying the originals
    obj1_copy = obj1.copy()
    obj1_copy.data = obj1.data.copy()  # Copy the mesh data
    bpy.context.collection.objects.link(obj1_copy)

    obj2_copy = obj2.copy()
    obj2_copy.data = obj2.data.copy()  # Copy the mesh data
    bpy.context.collection.objects.link(obj2_copy)

    # Apply shape keys to the copied objects (fully apply them to the geometry)
    apply_shape_keys(obj1_copy)
    apply_shape_keys(obj2_copy)

    # Apply all modifiers to the copied objects (except the Boolean modifier)
    apply_all_modifiers(obj1_copy)
    apply_all_modifiers(obj2_copy)

    # Add the Boolean modifier to obj1_copy for intersection check
    bool_modifier = obj1_copy.modifiers.new(name="Boolean", type='BOOLEAN')
    bool_modifier.operation = 'INTERSECT'  # Check for intersection
    bool_modifier.use_self = False
    bool_modifier.object = obj2_copy

    # Apply the Boolean modifier
    bpy.context.view_layer.objects.active = obj1_copy
    bpy.ops.object.modifier_apply(modifier=bool_modifier.name)

    # Check if the geometry after applying the Boolean modifier is empty or has faces
    if obj1_copy.data.polygons:
        print("Meshes intersect.")
        bpy.data.objects.remove(obj1_copy)  # Clean up the copy
        bpy.data.objects.remove(obj2_copy)  # Clean up the copy
        return True
    else:
        print("Meshes do not intersect.")
        bpy.data.objects.remove(obj1_copy)  # Clean up the copy
        bpy.data.objects.remove(obj2_copy)  # Clean up the copy
        return False


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


def remove_unused_shapekeys():
    for sk in bpy.data.shape_keys:
        if sk.users == 0 or sk.users == None:  # If no object is using this mesh
            bpy.data.shape_keys.key_blocks.remove(sk)


def gc_impl():
    remove_unused_meshes()
    remove_unused_shapekeys()


class CollisionDetection(bpy.types.Operator):
    bl_idname = "ubertools.collision_detection"
    bl_label = "Run Collision Detection"
    bl_description = "Run Collision Detection"

    def execute(self, context):
        show_blender_system_console()
        selections = context.selected_objects
        scene = context.scene

        frames = range(scene.frame_start, scene.frame_end+1)
        frame_count = len(frames)
        for i, v in enumerate(frames):
            self.progress = i/frame_count
            scene.frame_set(v)
            if v == scene.frame_end:
                self.progress = 1
            overlap = check_boolean_intersection_with_modifiers(
                selections[0], selections[1])
            gc_impl()
            print(f"{v}/{scene.frame_end} =====>   {overlap}")
            if overlap:
                scene.timeline_markers.new(f'overlap_{v:5}', frame=v)
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) == 2 and context.selected_objects[0].type == "MESH" and context.selected_objects[1].type == "MESH"
