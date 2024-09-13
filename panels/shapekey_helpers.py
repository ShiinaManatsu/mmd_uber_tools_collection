import bpy

from ..operators.ShapeKeyHelpersCopy import ShapeKeyHelpersCopyOperator
from ..operators.ShapeKeyHelpersPaste import ShapeKeyHelpersPasteOperator


class ShapeKeyHelpersPanel(bpy.types.Panel):
    bl_label = "Shape Key Helpers"
    bl_idname = "UBERTOOLS_PT_ShapeKeyHelpers"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MMD"  # SideBar Name

    # 2. Draw UI Function
    def draw(self, context):
        layout = self.layout

        # Buttons
        row = layout.row()
        row.operator(ShapeKeyHelpersCopyOperator.bl_idname,
                     icon="COPYDOWN", text=ShapeKeyHelpersCopyOperator.bl_label)
        row.operator(ShapeKeyHelpersPasteOperator.bl_idname,
                     icon="PASTEDOWN", text=ShapeKeyHelpersPasteOperator.bl_label)
