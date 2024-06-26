import bpy

from ..operators.CreateClothForBreast import CreateClothForBreast, UpdateBreastProperty

from bpy.props import *


class CreateClothForBreastProperty(bpy.types.PropertyGroup):
    total_vertices: IntProperty(
        default=400, name="Proxy Mesh Vertex Count")
    mass: FloatProperty(default=3, name="Mass", unit="MASS")
    sagginess: FloatProperty(default=0, name="Sagginess", min=0, max=2)
    springy: FloatProperty(default=100, name="Springy", min=0, max=100)
    fullness: FloatProperty(default=400, name="Fullness", min=200, max=600)

    # brest config
    left_breast_bone_name: bpy.props.StringProperty(
        default="胸上2.L", name="Left Breast Bone")
    right_breast_bone_name: bpy.props.StringProperty(
        default="胸上2.R", name="Right Breast Bone")

    current_breast_obj: PointerProperty(
        name="Cloth Object", type=bpy.types.Object)


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
        layout.prop(breast_props, "sagginess")
        layout.prop(breast_props, "springy")
        layout.prop(breast_props, "fullness")
        layout.prop(breast_props, "current_breast_obj")
        layout.operator(UpdateBreastProperty.bl_idname)


def register():
    bpy.types.Scene.breast = bpy.props.PointerProperty(
        type=CreateClothForBreastProperty)


def unregister():
    del bpy.types.Scene.breast
