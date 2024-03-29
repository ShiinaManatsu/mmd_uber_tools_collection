import bpy


def clear_constraint():
    bone_object = bpy.context.active_object
    if not bone_object or bone_object.type != 'ARMATURE':
        return False

    # 遍历目标骨骼
    for bone_name in list(map(lambda x: x.name, bone_object.data.bones)):
        if bone_name not in bone_object.data.bones:
            continue
        bone = bone_object.data.bones[bone_name]

        # 切换到姿态模式
        bpy.ops.object.mode_set(mode='POSE')

        # 选中当前骨骼
        bone_object.data.bones.active = bone_object.data.bones[bone.name]
        bpy.ops.pose.select_all(action='SELECT')

        # 获取骨骼的所有约束
        bone_constraints = bone_object.pose.bones[bone.name].constraints
        # 要删除的约束名称列表
        constraints_to_delete = ["Copy Location_P", "Damped Track_X", "Damped Track_Z"]

        # 遍历并删除指定名称的约束
        for constraint_name in constraints_to_delete:
            for constraint in bone_constraints:
                if constraint.name == constraint_name or constraint.name.startswith(constraint_name + "."):
                    bone_constraints.remove(constraint)
        # 切换回对象模式
        bpy.ops.object.mode_set(mode='OBJECT')

        print(f"'{bone.name}' constraints cleared.")
    return True


class ClearConstraintOperator(bpy.types.Operator):
    '''清除腿部FK骨骼的约束'''
    bl_idname = "uber.clear_constraint"
    bl_label = ("Clear Constraint")
    bl_options = {"UNDO_GROUPED"}

    def execute(self, context):
        result = clear_constraint()
        if not result:
            self.report({'ERROR'}, ("Clear Constraint Failed"))
        return {'FINISHED'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return bpy.context.mode == 'OBJECT'
