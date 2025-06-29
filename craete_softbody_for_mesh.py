import bpy
from ..operators.CreateMeshSoftbodyProxy import CreateClothForBreast
from bpy.props import *

vertex_group_count = 0
delimiter = ",,,"


def array_to_string(arr, delimiter=''):
    return delimiter.join(arr)


def string_to_array(s, delimiter=None):
    if delimiter is None:
        return s.split()
    else:
        return s.split(delimiter)


class SoftbodyForMeshProperty(bpy.types.PropertyGroup):
    total_vertices: IntProperty(default=800, name="Proxy Mesh Vertex Count")

    vertex_group: StringProperty(default="", name="Vertex Group")
    vertex_group_0: StringProperty(default="胸上2.L", name="Vertex Group_0")
    vertex_group_1: StringProperty(default="胸上2.R", name="Vertex Group_1")

    target_count: bpy.props.IntProperty(
        name="target_count", default=5000, soft_min=100, soft_max=10000, step=20, min=1)
    adaptive_size: bpy.props.FloatProperty(
        name="adaptive_size", default=50, min=0, max=100, step=0.5, precision=0, subtype='PERCENTAGE')

    deform_name: StringProperty(default="", name="Deform Name")

    compensate_softbody_drop: BoolProperty(
        default=True, name="CompensateSoftbodyDrop")

    compensate_softbody_drop_weight: FloatProperty(
        default=0.5, min=0, max=1, name="CompensateSoftbodyDropWeight")

    compensate_softbody_drop_weight: FloatProperty(
        default=0.5, min=0, max=1, name="CompensateSoftbodyDropWeight")

    is_compensate_called: BoolProperty(
        default=False, name="IsCompensateCalled")


# class AddVertexGroupSlot(bpy.types.Operator):
#     bl_idname = "ubertools.add_vertex_group_slot"
#     bl_label = "Add Vertex Group Slot"
#     bl_description = "Config cloth for breast."
#     bl_options = {'REGISTER', 'UNDO'}


#     def execute(self, context):
#         pass


class CreateClothForBreastPanel(bpy.types.Panel):
    bl_idname = 'UBERTOOLS_PT_SoftbodyForMesh'
    bl_label = 'Softbody'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MMD"

    def draw(self, context):
        breast_props: SoftbodyForMeshProperty = bpy.context.scene.softbody_mesh

        vertex_group = string_to_array(breast_props.vertex_group)
        vertex_group_count = len(vertex_group)

        layout = self.layout

        layout.prop(breast_props, "total_vertices")

        layout.separator()

        layout.label(text="Vertex Group:")
        # for x in range(vertex_group_count):
        #     layout.
        layout.prop(breast_props, "vertex_group_0")
        layout.prop(breast_props, "vertex_group_1")

        layout.prop(breast_props, "compensate_softbody_drop")
        layout.prop(breast_props, "compensate_softbody_drop_weight")
        layout.separator()

        layout.operator(CreateClothForBreast.bl_idname)


def register():
    bpy.types.Scene.softbody_mesh = bpy.props.PointerProperty(
        type=SoftbodyForMeshProperty)


def unregister():
    del bpy.types.Scene.softbody_mesh
