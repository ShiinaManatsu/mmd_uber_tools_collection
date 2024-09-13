import bpy
import pickle
import base64
import pyperclip


def save_action(action):
    fcurves_data = []
    for fcurve in action.fcurves:
        if fcurve.data_path.startswith('key_blocks'):
            keyframe_data = [(keyframe.co[0], keyframe.co[1])
                             for keyframe in fcurve.keyframe_points]
            fcurves_data.append({
                'data_path': fcurve.data_path,
                'keyframe_data': keyframe_data
            })
    return fcurves_data


def save_shape_key_values(shape_keys):
    shape_key_values = {}
    for key_block in shape_keys.key_blocks:
        shape_key_values[key_block.name] = key_block.value
    return shape_key_values


def save_shape_key_animations(obj):
    shape_key_animations = {}
    if obj.data.shape_keys.animation_data and obj.data.shape_keys.animation_data.action:
        action = obj.data.shape_keys.animation_data.action
        shape_key_animations['action_name'] = action.name
        shape_key_animations['fcurves'] = save_action(action)
    shape_key_animations['values'] = save_shape_key_values(obj.data.shape_keys)
    return shape_key_animations


def copy_shape_key_animations_to_clipboard(obj):
    shape_key_animations = save_shape_key_animations(obj)

    serialized_data = pickle.dumps(shape_key_animations)
    encoded_data = base64.b64encode(serialized_data).decode('utf-8')

    pyperclip.copy(encoded_data)
    print("Shape key animations and values copied to clipboard.")


def paste_action():
    # Ensure a single object is selected
    if len(bpy.context.selected_objects) != 1:
        print("Please select a single mesh object with shape key animations.")
    else:
        obj = bpy.context.selected_objects[0]
        if obj.type != 'MESH':
            print("Selected object is not a mesh.")
        elif not obj.data.shape_keys:
            print("Selected mesh has no shape keys.")
        else:
            copy_shape_key_animations_to_clipboard(obj)


class ShapeKeyHelpersCopyOperator(bpy.types.Operator):
    bl_idname = "ubertools.shape_key_helpers_copy"
    bl_label = ("Copy Shapekey Action")

    def execute(self, context):
        paste_action()
        return {'FINISHED'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return bpy.context.active_object and bpy.context.active_object.type == "MESH"
