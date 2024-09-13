import bpy
import pickle
import base64
import pyperclip


def apply_action_to_shape_keys(obj, action_name, fcurves_data):
    if not obj.data.shape_keys:
        print("Selected mesh has no shape keys.")
        return

    if action_name in bpy.data.actions:
        action = bpy.data.actions[action_name]
    else:
        action = bpy.data.actions.new(name=action_name)

    action.fcurves.clear()

    if not obj.data.shape_keys.animation_data:
        obj.data.shape_keys.animation_data_create()

    obj.data.shape_keys.animation_data.action = action

    for fcurve_data in fcurves_data:
        fcurve = action.fcurves.new(data_path=fcurve_data['data_path'])
        for co in fcurve_data['keyframe_data']:
            keyframe = fcurve.keyframe_points.insert(
                frame=co[0], value=co[1], options={'FAST'})
            keyframe.co = co


def apply_shape_key_values(shape_keys, shape_key_values):
    for key_name, value in shape_key_values.items():
        if key_name in shape_keys.key_blocks:
            shape_keys.key_blocks[key_name].value = value


def apply_shape_key_animations_from_clipboard(obj):
    encoded_data = pyperclip.paste()
    serialized_data = base64.b64decode(encoded_data)
    shape_key_animations = pickle.loads(serialized_data)

    if 'action_name' in shape_key_animations and 'fcurves' in shape_key_animations:
        action_name = shape_key_animations['action_name']
        fcurves_data = shape_key_animations['fcurves']
        apply_action_to_shape_keys(obj, action_name, fcurves_data)

    if 'values' in shape_key_animations:
        apply_shape_key_values(obj.data.shape_keys,
                               shape_key_animations['values'])

    print("Shape key animations and values pasted from clipboard.")


def paste_action():
    # Ensure a single object is selected
    if len(bpy.context.selected_objects) != 1:
        print("Please select a single mesh object to paste the shape key animations.")
    else:
        obj = bpy.context.selected_objects[0]
        if obj.type != 'MESH':
            print("Selected object is not a mesh.")
        elif not obj.data.shape_keys:
            print("Selected mesh has no shape keys.")
        else:
            apply_shape_key_animations_from_clipboard(obj)


class ShapeKeyHelpersPasteOperator(bpy.types.Operator):
    bl_idname = "ubertools.shape_key_helpers_paste"
    bl_label = ("Paste Shapekey Action")
    bl_options = {"UNDO_GROUPED"}

    def execute(self, context):
        paste_action()
        return {'FINISHED'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return bpy.context.active_object and bpy.context.active_object.type == "MESH"
