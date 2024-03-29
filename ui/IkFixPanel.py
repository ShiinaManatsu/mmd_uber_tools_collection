import bpy

from ..operators.FClearConstraintOperator import ClearConstraintOperator
from ..operators.FCopyVertexGroupOperator import CopyVertexGroupOperator
from ..operators.FAddBoneConstraintOperator import AddBoneConstraintOperator
from ..operators.FGenerateBoneTrackerOperator import GenerateBoneTrackerOperator




class VIEW3D_PT_ikfix_panel(bpy.types.Panel):
    bl_label = "PMX IK Correction"
    bl_idname = "VIEW3D_PT_ikfix_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MMD"  # SideBar Name

    # 2. Draw UI Function
    def draw(self, context):
        layout = self.layout

        # Buttons
        row = layout.row()
        row.operator(GenerateBoneTrackerOperator.bl_idname,
                     icon="BONE_DATA", text="生成骨骼物体")

        row = layout.row()
        row.operator(CopyVertexGroupOperator.bl_idname,
                     icon="VERTEXSEL", text="传递顶点组")

        row = layout.row()
        row.operator(AddBoneConstraintOperator.bl_idname,
                     icon="CONSTRAINT_BONE", text="生成骨骼约束")

        row = layout.row()
        row.operator(ClearConstraintOperator.bl_idname,
                     icon="LOOP_BACK", text="清除约束")

        # Text Show
        row = layout.row()  # Create a new row
        row.label(text='by SFY And YCYXZ', icon='FUND')
