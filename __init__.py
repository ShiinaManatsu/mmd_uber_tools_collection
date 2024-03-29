import bpy
import os
import importlib
from .ui import IkFixPanel, vmd_stop_motion
from .ui.IkFixPanel import VIEW3D_PT_ikfix_panel
from .ui.vmd_stop_motion import VMDStopMotionMethods, VMDStopMotionUI
from .operators.pmx_animation_proxy import FClearConstraintOperator, FCopyVertexGroupOperator, FAddBoneConstraintOperator, FGenerateBoneTrackerOperator

bl_info = {
    "name": "MMD Uber Tools Collection",
    "author": "ShiinaManatsu",
    "description": "MMD pipline tools collection",
    "blender": (3, 3, 0),
    "version": (0, 0, 3),
    "location": "",
    "warning": "",
    "category": "Generic"
}


modules = [
    FClearConstraintOperator,
    FCopyVertexGroupOperator,
    FAddBoneConstraintOperator,
    FGenerateBoneTrackerOperator,
    IkFixPanel,
    vmd_stop_motion
]

classes = (
    VMDStopMotionUI,
    VMDStopMotionMethods,
    VIEW3D_PT_ikfix_panel,
    FClearConstraintOperator.ClearConstraintOperator,
    FCopyVertexGroupOperator.CopyVertexGroupOperator,
    FAddBoneConstraintOperator.AddBoneConstraintOperator,
    FGenerateBoneTrackerOperator.GenerateBoneTrackerOperator
)


def register():
    # reload the submodules
    if os.environ.get('Uber'):
        for module in modules:
            importlib.reload(module)

    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)

if __name__ == "__main__":
    register()
