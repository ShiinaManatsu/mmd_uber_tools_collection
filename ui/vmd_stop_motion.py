import bpy


class VMDStopMotionUI(bpy.types.Panel):
    bl_idname = 'Vmd_Stopmotion'
    bl_label = 'Vmd Stopmotion'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Vmd Stopmotion"

    def draw(self, context):
        layout = self.layout
        layout.operator(operator="opr.setupkeys", text="Setup KeyFrames")


class VMDStopMotionMethods(bpy.types.Operator):
    bl_idname = 'opr.setupkeys'
    bl_label = 'DoSetupKeyFrames'

    def execute(self, context):
        obj = bpy.context.object
        action = obj.animation_data.action
        fcurve: bpy.types.FCurve
        for fcurve in action.fcurves:
            key: bpy.types.Keyframe
            for index, key in enumerate(fcurve.keyframe_points):
                if(index == len(fcurve.keyframe_points)-2):
                    break
                next = fcurve.keyframe_points[index+1]
                if(next.co[0]-key.co[0] == 1):
                    key.interpolation = "CONSTANT"
        return {'FINISHED'}
