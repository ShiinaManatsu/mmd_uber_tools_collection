import bpy
# --------------- Main Operator called when <<Remesh It>> is pressed! -------

MASS_TO_STRUCTUAL = 100


class CreateClothForBreast(bpy.types.Operator):
    bl_idname = "ubertools.config_breast"
    bl_label = "Config Breast"
    bl_description = "Config cloth for breast."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        breast_props = bpy.context.scene.breast

        meshObj = bpy.context.active_object
        armatureObj = meshObj.parent

        left_breast_bone_name = breast_props.left_breast_bone_name
        right_breast_bone_name = breast_props.right_breast_bone_name
        breast_bind_vertex_group = ""

        temp_object = []

        def remesh_again():
            obj = bpy.context.active_object
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)

            temp_object.append(obj)

            bpy.ops.object.delete
            bpy.types.Scene.remesh_callback = remesh_last
            bpy.ops.qremesher.remesh()

        def remesh_last():
            obj = bpy.context.active_object
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)

            temp_object.append(obj)
            bpy.types.Scene.remesh_callback = after_remesh
            bpy.ops.qremesher.remesh()

        def clean_up():
            print(f"Begin clean up")
            bpy.ops.object.select_all(action='DESELECT')
            o: bpy.types.Object
            for o in temp_object:
                print(f"Delete {o.name}")
                bpy.data.objects.remove(o, do_unlink=True)

        def after_remesh():
            remeshedObj = bpy.context.active_object
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.region_to_loop()

            remeshedObj.vertex_groups.new(name="上半身2")
            bpy.ops.object.vertex_group_assign()
            bpy.ops.object.mode_set(mode='OBJECT')

            bpy.ops.object.select_all(action='DESELECT')
            armatureObj.select_set(True)
            remeshedObj.select_set(True)
            bpy.context.view_layer.objects.active = armatureObj
            bpy.ops.object.mode_set(mode='POSE')
            armature: bpy.types.Armature = armatureObj.data
            armature.bones["上半身2"].select = True
            bpy.ops.object.parent_set(type='ARMATURE_NAME')
            bpy.ops.object.mode_set(mode='OBJECT')

            bpy.ops.object.select_all(action='DESELECT')
            remeshedObj.select_set(True)
            bpy.context.view_layer.objects.active = remeshedObj

            #   Add mirror modifier to remeshed breast
            # bpy.ops.object.modifier_add(type='MIRROR')
            # bpy.ops.object.modifier_move_to_index(modifier="Mirror", index=0)

            #   Add cloth modifier to remeshed breast
            bpy.ops.object.modifier_add(type='CLOTH')
            cloth: bpy.types.ClothModifier = remeshedObj.modifiers["Cloth"]
            cloth.settings.vertex_group_mass = "上半身2"
            cloth.settings.quality = 5
            cloth.settings.mass = breast_props.mass
            cloth.settings.bending_model = 'LINEAR'

            cloth.settings.tension_stiffness = breast_props.mass * 100
            cloth.settings.shear_stiffness = 2 - breast_props.sagginess
            cloth.settings.bending_stiffness = 100 - breast_props.springy

            cloth.settings.tension_damping = 1
            cloth.settings.shear_damping = 0
            cloth.settings.bending_damping = 0

            cloth.settings.use_pressure = True
            cloth.settings.uniform_pressure_force = breast_props.mass * breast_props.fullness

            cloth.collision_settings.collision_quality = 5
            cloth.collision_settings.distance_min = 0.001

            cloth.point_cache.frame_end = 99999

            #   Add smooth modifier to remeshed breast
            bpy.ops.object.modifier_add(type='SMOOTH')
            remeshedObj.modifiers["Smooth"].factor = 0.7

            bpy.ops.object.select_all(action='DESELECT')
            meshObj.select_set(True)
            bpy.context.view_layer.objects.active = meshObj
            bpy.ops.object.modifier_add(type='SURFACE_DEFORM')
            meshObj.modifiers["SurfaceDeform"].vertex_group = breast_bind_vertex_group
            meshObj.modifiers["SurfaceDeform"].target = remeshedObj
            bpy.ops.object.surfacedeform_bind(modifier="SurfaceDeform")

            remeshedObj.hide_render = True
            remeshedObj.hide_viewport = True
            remeshedObj.name = "BreastClothProxy"
            breast_props.current_breast_obj = remeshedObj
            clean_up()

            del bpy.types.Scene.remesh_callback

        # bpy.types.Scene.remesh_callback = after_remesh

        #   Create vertex group for deform binding
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type="VERT")
        bpy.ops.mesh.select_all(action='DESELECT')

        meshObj.vertex_groups.active_index = meshObj.vertex_groups[right_breast_bone_name].index
        bpy.ops.object.vertex_group_select()
        meshObj.vertex_groups.active_index = meshObj.vertex_groups[left_breast_bone_name].index
        bpy.ops.object.vertex_group_select()
        breast_bind_vertex_group = meshObj.vertex_groups.new(
            name="BreastBind").name
        bpy.ops.object.vertex_group_assign()

        #    Select half breast for remesh
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type="VERT")
        bpy.ops.mesh.select_all(action='DESELECT')

        meshObj.vertex_groups.active_index = meshObj.vertex_groups[right_breast_bone_name].index
        bpy.ops.object.vertex_group_select()
        meshObj.vertex_groups.active_index = meshObj.vertex_groups[left_breast_bone_name].index
        bpy.ops.object.vertex_group_select()

        # bpy.ops.mesh.duplicate_move(MESH_OT_duplicate={"mode": 1}, TRANSFORM_OT_translate={"value": (0, 0, 0), "orient_axis_ortho": 'X', "orient_type": 'GLOBAL', "orient_matrix": ((0, 0, 0), (0, 0, 0), (0, 0, 0)), "orient_matrix_type": 'GLOBAL', "constraint_axis": (False, False, False), "mirror": False, "use_proportional_edit": False, "proportional_edit_falloff": 'SMOOTH', "proportional_size": 1, "use_proportional_connected": False, "use_proportional_projected": False, "snap": False, "snap_elements": {
        #                             'INCREMENT'}, "use_snap_project": False, "snap_target": 'CLOSEST', "use_snap_self": True, "use_snap_edit": True, "use_snap_nonedit": True, "use_snap_selectable": False, "snap_point": (0, 0, 0), "snap_align": False, "snap_normal": (0, 0, 0), "gpencil_strokes": False, "cursor_transform": False, "texture_space": False, "remove_on_cancel": False, "view2d_edge_pan": False, "release_confirm": False, "use_accurate": False, "use_automerge_and_split": False})
        bpy.ops.mesh.duplicate_move(MESH_OT_duplicate={"mode": 1}, TRANSFORM_OT_translate={"value": (0, 0, 0), "orient_type": 'GLOBAL', "orient_matrix": ((0, 0, 0), (0, 0, 0), (0, 0, 0)), "orient_matrix_type": 'GLOBAL', "constraint_axis": (False, False, False), "mirror": False, "use_proportional_edit": False, "proportional_edit_falloff": 'SMOOTH', "proportional_size": 1, "use_proportional_connected": False, "use_proportional_projected": False, "snap": False, "snap_elements": {
                                    'INCREMENT'}, "use_snap_project": False, "snap_target": 'CLOSEST', "use_snap_self": True, "use_snap_edit": True, "use_snap_nonedit": True, "use_snap_selectable": False, "snap_point": (0, 0, 0), "snap_align": False, "snap_normal": (0, 0, 0), "gpencil_strokes": False, "cursor_transform": False, "texture_space": False, "remove_on_cancel": False, "view2d_edge_pan": False, "release_confirm": False, "use_accurate": False, "use_automerge_and_split": False})

        bpy.ops.mesh.separate(type='SELECTED')
        bpy.ops.object.mode_set(mode='OBJECT')
        temp_object.append(bpy.context.selected_objects[1])
        bpy.context.selected_objects[0].select_set(False)

        bpy.context.scene.qremesher.target_count = breast_props.total_vertices
        bpy.context.scene.qremesher.adaptive_size = 0
        bpy.types.Scene.remesh_callback = remesh_again
        bpy.ops.qremesher.remesh()
        return {'FINISHED'}


class UpdateBreastProperty(bpy.types.Operator):
    bl_idname = "ubertools.update_breast_property"
    bl_label = "Update Breast Property"
    bl_description = "Config cloth for breast."
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        breast_props = bpy.context.scene.breast
        return breast_props.current_breast_obj is not None

    def execute(self, context):
        breast_props = bpy.context.scene.breast
        obj = breast_props.current_breast_obj

        hide_render = obj.hide_render
        hide_viewport = obj.hide_viewport
        obj.hide_render = False
        obj.hide_viewport = False

        cloth: bpy.types.ClothModifier = obj.modifiers["Cloth"]

        cloth.settings.mass = breast_props.mass
        cloth.settings.bending_model = 'LINEAR'

        cloth.settings.tension_stiffness = breast_props.mass * 100
        cloth.settings.shear_stiffness = 2 - breast_props.sagginess
        cloth.settings.bending_stiffness = 100 - breast_props.springy

        cloth.settings.use_pressure = True
        cloth.settings.uniform_pressure_force = breast_props.mass * breast_props.fullness

        obj.hide_render = hide_render
        obj.hide_viewport = hide_viewport
        return {'FINISHED'}
