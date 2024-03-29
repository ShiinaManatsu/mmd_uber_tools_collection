import bpy
import math


def copy_vertex_group():

    armature: bpy.types.Armature
    mesh: bpy.types.Mesh
    mesh_obj: bpy.types.Object
    for o in bpy.context.selected_objects:
        if len(o.modifiers) > 0:
            mesh = o.data
            mesh_obj = o
        else:
            armature = o

    # Reconstruct vertex group
    # <bone_index, <subtype, vertex_index>>
    vertexset: dict[int, dict[int, int]] = {}

    uv_layer = mesh.uv_layers[0].data
    poly: bpy.types.MeshPolygon
    for poly in mesh.polygons:
        for loop_index in poly.loop_indices:
            uv = uv_layer[loop_index].uv
            if math.modf(uv.y)[0] > 0.001:
                continue
            bone_index = int(uv.x)
            type_index = int(uv.y)
            vertex_index = mesh.loops[loop_index].vertex_index
            if not bone_index in vertexset.keys():
                vertexset[bone_index] = {}
            vertexset[bone_index][type_index] = vertex_index

    for bone_index in vertexset.keys():
        bone_name = armature.pose.bones[bone_index].bone.name
        vg = mesh_obj.vertex_groups.new(name=bone_name)
        vg.add(list(vertexset[bone_index].values()), 1, 'REPLACE')
        
        vg = mesh_obj.vertex_groups.new(name=f"{bone_name}_x")
        vg.add([vertexset[bone_index][1]], 1, 'REPLACE')
        
        vg = mesh_obj.vertex_groups.new(name=f"{bone_name}_y")
        vg.add([vertexset[bone_index][2]], 1, 'REPLACE')
        
        vg = mesh_obj.vertex_groups.new(name=f"{bone_name}_z")
        vg.add([vertexset[bone_index][3]], 1, 'REPLACE')
        
        vg = mesh_obj.vertex_groups.new(name=f"{bone_name}_p")
        vg.add([vertexset[bone_index][0]], 1, 'REPLACE')

    bpy.ops.object.select_all(action="DESELECT")
    mesh_obj.select_set(True)  # 选中abc
    armature.select_set(True)
    # 更新视图以反映选择的更改
    bpy.context.view_layer.objects.active = mesh_obj
    bpy.context.view_layer.update()
    return True


class CopyVertexGroupOperator(bpy.types.Operator):
    '''为选中的骨架的腿部FK骨骼生成骨骼追踪器'''
    bl_idname = "uber.copy_vertex_group"
    bl_label = ("Copy Vertex Group")
    bl_options = {"UNDO_GROUPED"}

    def execute(self, context):
        result = copy_vertex_group()
        if not result:
            self.report({'ERROR'}, ("Copy Vertex Group Failed"))
            return {'CANCELLED'}
        return {'FINISHED'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return bpy.context.mode == 'OBJECT'
