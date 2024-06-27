import bpy

from ..operators.CreateClothForBreast import CreateClothForBreast, UpdateBreastProperty

from bpy.props import *


def update_breast(self, context):
    if bpy.context.scene.breast.current_breast_obj is not None:
        bpy.ops.ubertools.update_breast_property()


class CreateClothForBreastProperty(bpy.types.PropertyGroup):
    total_vertices: IntProperty(
        default=400, name="Proxy Mesh Vertex Count")  # type: ignore

    mass: FloatProperty(default=3, name="Mass(重量)",
                        unit="MASS", update=update_breast)  # type: ignore
    softness: FloatProperty(default=0, name="Softness(柔软)",
                            min=0, max=2, update=update_breast)  # type: ignore
    springy: FloatProperty(default=100, name="Springy(弹性)",
                           min=0, max=100, update=update_breast)  # type: ignore
    fullness: FloatProperty(
        default=400, name="Fullness(干瘪-丰满)", min=200, max=600, update=update_breast)  # type: ignore

    # brest config
    left_breast_bone_name: bpy.props.StringProperty(
        default="胸上2.L", name="Left Breast Bone")  # type: ignore
    right_breast_bone_name: bpy.props.StringProperty(
        default="胸上2.R", name="Right Breast Bone")  # type: ignore

    current_breast_obj: PointerProperty(
        name="Cloth Object", type=bpy.types.Object)  # type: ignore


class CreateClothForBreastPanel(bpy.types.Panel):
    bl_idname = 'UBERTOOLS_PT_CreateClothForBreast'
    bl_label = 'Cloth For Breast'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MMD"

    def draw(self, context):
        breast_props = bpy.context.scene.breast
        layout = self.layout

        layout.prop(breast_props, "left_breast_bone_name")
        layout.prop(breast_props, "right_breast_bone_name")
        layout.operator(CreateClothForBreast.bl_idname)

        layout.separator()

        layout.prop(breast_props, "mass")
        layout.prop(breast_props, "softness")
        layout.prop(breast_props, "springy")
        layout.prop(breast_props, "fullness")
        
        layout.separator()

        layout.prop(breast_props, "current_breast_obj")


def register():
    bpy.types.Scene.breast = bpy.props.PointerProperty(
        type=CreateClothForBreastProperty)


def unregister():
    del bpy.types.Scene.breast
