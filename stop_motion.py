import bpy


class VMDStopMotionPanel(bpy.types.Panel):
    bl_idname = 'UBERTOOLS_PT_StopMotion'
    bl_label = 'Vmd Stopmotion'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MMD"

    def draw(self, context):
        layout = self.layout
        layout.operator(operator=VMDStopMotionMethods.bl_idname,
                        text="Setup KeyFrames")


class VMDStopMotionMethods(bpy.types.Operator):
    bl_idname = 'ubertools.apply_stop_motion'
    bl_label = 'DoSetupKeyFrames'

    def execute(self, context):
        obj = bpy.context.object
        action = obj.animation_data.action
        fcurve: bpy.types.FCurve
        for fcurve in action.fcurves:
            last = len(fcurve.keyframe_points)-1
            key: bpy.types.Keyframe
            for index, key in enumerate(fcurve.keyframe_points):
                if (index == last):
                    break
                next = fcurve.keyframe_points[index+1]
                if (next.co[0]-key.co[0] < 1.1):
                    key.interpolation = "CONSTANT"
        return {'FINISHED'}
