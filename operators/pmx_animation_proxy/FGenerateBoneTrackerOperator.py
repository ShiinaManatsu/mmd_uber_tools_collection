import bpy
import bmesh


# fk_bone_name = ["足.L", "ひざ.L", "足首.L", "足先EX.L", "足.R", "ひざ.R", "足首.R", "足先EX.R"]


def select_vertex(obj, v_i):  # 选中指定索引顶点
    # 清除现有选择
    bpy.ops.mesh.select_all(action='DESELECT')
    bm = bmesh.from_edit_mesh(obj.data)
    # 确保索引表已更新
    bm.verts.ensure_lookup_table()
    # 选择特定顶点（例如，第一个顶点）
    vertex_index_to_select = v_i

    bm.verts[vertex_index_to_select].select = True

    # 更新选择状态
    bmesh.update_edit_mesh(obj.data)


def select_vertex_groups(obj, name, vert_index):  # 为选中顶点创建顶点组
    # 创建一个新的顶点组
    bpy.ops.object.vertex_group_add()

    # 获取当前选定的顶点组
    vertex_group = obj.vertex_groups.active

    # 将选定的顶点分配到顶点组中
    bpy.ops.object.vertex_group_assign()
    # 切换回对象模式
    bpy.ops.object.mode_set(mode='OBJECT')
    # 重命名顶点组
    vertex_group.name = name  # 将顶点组重命名为您想要的名称
    # 进入编辑模式
    bpy.ops.object.mode_set(mode='EDIT')

    me = obj.data
    bm = bmesh.from_edit_mesh(me)

    name_to_index = {"p": 0, "x": 1, "y": 2, "z": 3}
    subindex = name_to_index[name]

    uv_layer = bm.loops.layers.uv.verify()

    face: bmesh.types.BMFace
    for face in bm.faces:
        loop: bmesh.types.BMLoop
        for loop in face.loops:
            if loop.vert.index == vert_index:
                loop_uv = loop[uv_layer]
                # use xy position of the vertex as a uv coordinate
                loop_uv.uv = [0, subindex]

    bmesh.update_edit_mesh(me)


def generate_basic_cube():
    # 创建一个立方体
    bpy.ops.mesh.primitive_cube_add(
        size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0))
    # 获取活动对象
    cube_obj = bpy.context.active_object

    cube_size = 0.05  # 生成物体大小

    # 进入编辑模式
    bpy.ops.object.mode_set(mode='EDIT')

    # 选择所有顶点
    bpy.ops.mesh.select_all(action='SELECT')

    # 缩放所有顶点，以世界原点为中心
    bpy.ops.transform.resize(value=(cube_size, cube_size, cube_size))

    # 选择所有顶点
    bpy.ops.mesh.select_all(action='SELECT')
    # 移动所有顶点
    bpy.ops.transform.translate(value=(cube_size, cube_size, cube_size))

    select_vertex(cube_obj, 7)

    bpy.ops.mesh.delete(type='VERT')  # 删除索引为7的顶点

    # 指定顶点组
    select_vertex(cube_obj, 0)
    select_vertex_groups(cube_obj, "p", 0)

    select_vertex(cube_obj, 4)
    select_vertex_groups(cube_obj, "x", 4)

    select_vertex(cube_obj, 2)
    select_vertex_groups(cube_obj, "y", 2)

    select_vertex(cube_obj, 1)
    select_vertex_groups(cube_obj, "z", 1)

    # 切换回对象模式
    bpy.ops.object.mode_set(mode='OBJECT')

    return cube_obj


def copy_cude_for_bone(cube_obj, bone, bone_object):
    # 复制物体引用
    copy_cube_object = cube_obj.copy()

    # 复制物体数据
    copy_cube_object.data = cube_obj.data.copy()

    # 将复制物体添加到场景中
    bpy.context.collection.objects.link(copy_cube_object)

    # 将立方体的名称设置为骨骼的名称
    copy_cube_object.name = bone.name

    # 获取骨骼的变换矩阵并将其应用于立方体的变换
    copy_cube_object.matrix_world = bone_object.matrix_world @ bone.matrix_local

    # 添加骨架修改器到物体
    modifier = copy_cube_object.modifiers.new(
        name="Armature Modifier", type='ARMATURE')

    # 遍历物体的顶点组
    for vertex_group in copy_cube_object.vertex_groups:
        # 获取原始的顶点组名称
        original_name = vertex_group.name

        # 修改顶点组名称为物体名称加上原始的顶点组名称
        new_name = bone.name + "_" + original_name
        vertex_group.name = new_name

    # 设置骨架对象
    modifier.object = bone_object
    # 新建顶点组名称为骨骼名称
    vertex_group = copy_cube_object.vertex_groups.new(name=bone.name)

    # 设置权重值
    weight_value = 1.0  # 设置为所需的权重值
    for vertex in copy_cube_object.data.vertices:
        vertex_group.add([vertex.index], weight_value, 'REPLACE')

    child_object = copy_cube_object
    parent_object = bone_object

    if child_object is not None and parent_object is not None:
        # 将子物体添加到父物体的子集中
        parent_object.select_set(True)  # 选中父物体
        bpy.context.view_layer.objects.active = parent_object
        bpy.ops.object.parent_set(type='OBJECT')  # 使用 'OBJECT' 类型的父子关系
        child_object.select_set(False)  # 取消选择子物体
        bpy.context.view_layer.update()

    return copy_cube_object


def generate_bone_trackers():
    bone_object = bpy.context.active_object
    if not bone_object or bone_object.type != 'ARMATURE':
        return False
    cube_obj = generate_basic_cube()

    bone_trackers = []
    # for bone_name in fk_bone_name:
    for bone_name in list(map(lambda x: x.name, bone_object.data.bones)):
        bone = bone_object.data.bones.get(bone_name)
        bone_trackers.append(copy_cude_for_bone(
            cube_obj, bone, bone_object))

    bpy.ops.object.select_all(action='DESELECT')  # 取消选择所有物体
    # bpy.context.view_layer.objects.active = None  # 取消活动物体

    tracker: bpy.types.Object
    for tracker in bone_trackers:
        tracker.select_set(True)
        bpy.context.view_layer.objects.active = tracker
        bone_index = bone_object.data.bones.find(tracker.name)
        print(f"{tracker.name} -> {bone_index}")
        bpy.ops.object.mode_set(mode='EDIT')
        me = tracker.data
        bm = bmesh.from_edit_mesh(me)

        uv_layer = bm.loops.layers.uv.verify()

        face: bmesh.types.BMFace
        for face in bm.faces:
            loop: bmesh.types.BMLoop
            for loop in face.loops:
                loop_uv = loop[uv_layer]
                # use xy position of the vertex as a uv coordinate
                loop_uv.uv = [bone_index, loop_uv.uv.y]

        bmesh.update_edit_mesh(me)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')

    for bone_tracker in bone_trackers:
        bone_tracker.select_set(True)
        bpy.context.view_layer.objects.active = bone_tracker

    bpy.ops.object.join()  # 合并物体

    selected_object = bpy.context.selected_objects[0]
    selected_object.name = "骨骼坐标系"
    bpy.data.objects.remove(cube_obj, do_unlink=True)
    return True


class GenerateBoneTrackerOperator(bpy.types.Operator):
    '''为选中的骨架的腿部FK骨骼生成骨骼追踪器'''
    bl_idname = "uber.generate_bone_tracker"
    bl_label = ("Generate Bone Tracker")
    bl_options = {"UNDO_GROUPED"}

    def execute(self, context):
        result = generate_bone_trackers()
        if not result:
            self.report({'ERROR'}, ("Generate Bone Tracker Failed"))
        return {'FINISHED'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        bone_object = bpy.context.active_object
        if not bone_object or bone_object.type != 'ARMATURE':
            return False

        return True
