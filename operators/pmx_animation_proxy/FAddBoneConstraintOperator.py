import bpy


def add_constraint():
    # 获取当前的活动物体
    # active_object = bpy.context.active_object

    # 获取当前激活的对象（骨架和物体）
    selected_objects = bpy.context.selected_objects

    # 获取选中的非骨骼物体，即为abc物体
    for obj in selected_objects:
        if obj.type != 'ARMATURE':
            first_selected_object = obj
        else:
            active_object = obj
    # first_selected_object = selected_objects[1]

    print(first_selected_object)
    print(active_object)
    # 检查当前激活的对象是否是骨架类型
    if not active_object or active_object.type != 'ARMATURE':
        return False

    # 遍历FK骨骼
    for bone_name in list(map(lambda x: x.name, active_object.data.bones)):
        bone = active_object.data.bones[bone_name]
        print(bone)
        bpy.context.view_layer.objects.active = active_object
        bpy.ops.object.mode_set(mode='POSE')

        # 选中当前骨骼
        active_object.data.bones.active = active_object.data.bones[bone.name]
        bpy.ops.pose.select_all(action='SELECT')

        # 添加复制位置约束
        constraint_copy_location = active_object.pose.bones[bone.name].constraints.new(type='COPY_LOCATION')
        constraint_copy_location.name = "Copy Location_P"  # 设置约束的名称
        # 设置目标和顶点组
        target_object = first_selected_object
        if target_object:
            constraint_copy_location.target = target_object  # 设置约束的目标为目标物体
            vertex_group_name = f"{bone.name}_p"  # 替换为顶点组的名称
            constraint_copy_location.subtarget = vertex_group_name  # 设置约束的顶点组为指定名称

        # 添加阻尼追踪约束
        constraint_damped_track = active_object.pose.bones[bone.name].constraints.new(type='DAMPED_TRACK')
        constraint_damped_track.name = "Damped Track_X"  # 设置约束的名称
        # 设置约束的目标为目标物体（例如，目标是名为 "TargetObject" 的物体）
        if target_object:
            constraint_damped_track.target = target_object  # 设置约束的目标为目标物体

            # 构建顶点组名称为骨骼名称 + "_x"
            vertex_group_name = f"{bone.name}_x"
            constraint_damped_track.subtarget = vertex_group_name  # 设置约束的顶点组

            # 设置跟随轴（例如，'TRACK_X'、'TRACK_Y'、'TRACK_Z'）
            follow_axis = 'TRACK_X'  # 替换为所需的轴
            constraint_damped_track.track_axis = follow_axis

        # 添加阻尼追踪约束
        constraint_damped_track_1 = active_object.pose.bones[bone.name].constraints.new(type='DAMPED_TRACK')
        constraint_damped_track_1.name = "Damped Track_Z"  # 设置约束的名称
        # 设置约束的目标为目标物体（例如，目标是名为 "TargetObject" 的物体）
        if target_object:
            constraint_damped_track_1.target = target_object  # 设置约束的目标为目标物体

            # 构建顶点组名称为骨骼名称 + "_z"
            vertex_group_name = f"{bone.name}_z"
            constraint_damped_track_1.subtarget = vertex_group_name  # 设置约束的顶点组

            # 设置跟随轴（例如，'TRACK_X'、'TRACK_Y'、'TRACK_Z'）
            follow_axis = 'TRACK_Z'  # 替换为所需的轴
            constraint_damped_track_1.track_axis = follow_axis

        # 切换回对象模式
        bpy.ops.object.mode_set(mode='OBJECT')

        print(f"为骨骼 '{bone.name}' 添加复制位置约束")

    return True


class AddBoneConstraintOperator(bpy.types.Operator):
    '''添加腿部FK骨骼的约束'''
    bl_idname = "uber.add_constraint"
    bl_label = "Add Bone Constraint"
    bl_options = {"UNDO_GROUPED"}

    def execute(self, context):
        result = add_constraint()
        if not result:
            self.report({'ERROR'}, ("Add Constraint Failed"))
        return {'FINISHED'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return bpy.context.mode == 'OBJECT'
