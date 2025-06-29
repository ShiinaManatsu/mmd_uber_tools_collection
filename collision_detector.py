import bpy

from ..operators.CollisionDetection import CollisionDetection


class CollisionDetectionPanel(bpy.types.Panel):
    bl_label = "Collision Detection"
    bl_idname = "UBERTOOLS_PT_CollisionDetection"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MMD"  # SideBar Name

    # 2. Draw UI Function
    def draw(self, context):
        layout = self.layout

        # Buttons
        row = layout.row()
        row.operator(CollisionDetection.bl_idname,
                     icon="BOOKMARKS", text=CollisionDetection.bl_label)
