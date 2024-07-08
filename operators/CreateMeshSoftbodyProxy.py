import bpy

expand_selection_times = 2
remesh_times = 0
TOTAL_REMESH_TIME = 2
remeshed_mesh = []


separated_mesh: bpy.types.Object = None
armatureObj: bpy.types.Object = None


class CreateClothForBreast(bpy.types.Operator):
    bl_idname = "ubertools.create_mesh_softbody_proxy"
    bl_label = "Create Softbody"
    bl_description = "Create softbody proxy mesh, then assign to mesh softbody."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        breast_props = bpy.context.scene.softbody_mesh
        total_vertices = breast_props.total_vertices
        vertex_group_0 = breast_props.vertex_group_0
        vertex_group_1 = breast_props.vertex_group_1

        global separated_mesh
        global armatureObj
        global remesh_times
        remesh_times = 0

        mesh_obj = bpy.context.active_object
        armatureObj = mesh_obj.parent

        def excute_remesh_loop():
            global remesh_times
            global remeshed_mesh
            print(f"remeshing: {bpy.context.active_object}")
            if remesh_times > 0:
                print(f"remesh append: {bpy.context.active_object}")
                remeshed_mesh.append(bpy.context.active_object)
            if remesh_times < TOTAL_REMESH_TIME:
                remesh_times += 1
                bpy.types.Scene.remesh_callback = excute_remesh_loop
                bpy.ops.qremesher.remesh()
            else:
                del bpy.types.Scene.remesh_callback
                after_remesh()

        def create_softbody_goal(obj: bpy.types.Object):
            #   Add deform bind vertex group
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')

            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj

            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.region_to_loop()

            for i in range(expand_selection_times):
                bpy.ops.mesh.select_more()

            obj.vertex_groups.new(
                name="BreastGoal").name
            bpy.ops.object.vertex_group_assign()

            bpy.ops.object.mode_set(mode='OBJECT')

        def mix_weight(obj: bpy.types.Object, a, b):
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj

            bpy.ops.object.modifier_add(type='VERTEX_WEIGHT_MIX')
            weight_mix: bpy.types.VertexWeightMixModifier = bpy.context.object.modifiers[-1]
            weight_mix.vertex_group_a = a
            weight_mix.vertex_group_b = b
            weight_mix.mix_set = 'B'
            weight_mix.mix_mode = 'ADD'
            bpy.ops.object.modifier_apply(modifier=weight_mix.name)

        def after_remesh():
            global separated_mesh
            global armatureObj

            fine_remeshed_mesh = bpy.context.active_object

            for m in remeshed_mesh[:-1]:
                bpy.data.objects.remove(m, do_unlink=True)

            #   Transfer data from source mesh
            fine_remeshed_mesh.select_set(True)
            bpy.context.view_layer.objects.active = fine_remeshed_mesh
            bpy.ops.object.modifier_add(type='DATA_TRANSFER')
            data_transfer: bpy.types.DataTransferModifier = bpy.context.object.modifiers[-1]
            data_transfer.data_types_verts = {'VGROUP_WEIGHTS'}
            data_transfer.object = separated_mesh
            bpy.ops.object.datalayout_transfer(modifier="DataTransfer")
            bpy.ops.object.modifier_apply(modifier=data_transfer.name)

            bpy.ops.object.modifier_add(type='ARMATURE')
            armature: bpy.types.ArmatureModifier = bpy.context.object.modifiers[-1]
            armature.object = armatureObj

            fine_remeshed_mesh.vertex_groups.remove(
                fine_remeshed_mesh.vertex_groups[vertex_group_0])
            fine_remeshed_mesh.vertex_groups.remove(
                fine_remeshed_mesh.vertex_groups[vertex_group_1])

            #   Config softbody
            create_softbody_goal(fine_remeshed_mesh)
            bpy.ops.object.modifier_add(type='SOFT_BODY')
            softbody: bpy.types.SoftBodyModifier = bpy.context.object.modifiers[-1]
            softbody.settings.vertex_group_goal = "BreastGoal"
            softbody.settings.goal_min = 0.9
            softbody.settings.goal_default = 1
            softbody.settings.goal_friction = 30
            softbody.settings.goal_spring = 0.5
            softbody.point_cache.frame_end = 9999

            bpy.ops.object.modifier_add(type='SMOOTH')
            smooth: bpy.types.SmoothModifier = bpy.context.object.modifiers[-1]
            smooth.factor = 1
            smooth.iterations = 2
            fine_remeshed_mesh.hide_render = True
            fine_remeshed_mesh.hide_viewport = True

            #   Config source mesh
            # bpy.ops.mesh.select_all(action='DESELECT')
            for o in bpy.context.selected_objects:
                o.select_set(False)
            separated_mesh.select_set(True)
            bpy.context.view_layer.objects.active = separated_mesh

            bpy.ops.object.modifier_add(type='SURFACE_DEFORM')
            deform: bpy.types.SurfaceDeformModifier = bpy.context.object.modifiers[-1]
            deform.target = fine_remeshed_mesh
            deform.vertex_group = "BreastWeightCombined"
            deform.use_sparse_bind = True
            bpy.ops.object.surfacedeform_bind(modifier=deform.name)
            separated_mesh.hide_set(False)

        #   Separete softbody mesh
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type="VERT")
        bpy.ops.mesh.select_all(action='DESELECT')

        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles()

        bpy.ops.mesh.select_all(action='DESELECT')

        mesh_obj.vertex_groups.active_index = mesh_obj.vertex_groups[vertex_group_0].index
        bpy.ops.object.vertex_group_select()
        mesh_obj.vertex_groups.active_index = mesh_obj.vertex_groups[vertex_group_1].index
        bpy.ops.object.vertex_group_select()
        # bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')

        #   expand select to hide deform artifacts
        for i in range(expand_selection_times):
            bpy.ops.mesh.select_more()

        bpy.ops.mesh.separate(type='SELECTED')
        bpy.ops.object.mode_set(mode='OBJECT')

        separated_mesh = bpy.context.selected_objects[1]
        print(f"separated_mesh------------------:{separated_mesh}")

        #   Add deform vertex group
        create_softbody_goal(separated_mesh)

        breast_combined_name = separated_mesh.vertex_groups.new(
            name="BreastWeightCombined").name
        mix_weight(separated_mesh, breast_combined_name, vertex_group_0)
        mix_weight(separated_mesh, breast_combined_name, vertex_group_1)

        #   Start remeshing
        bpy.context.scene.qremesher.target_count = total_vertices
        bpy.context.scene.qremesher.adaptive_size = 0
        bpy.context.scene.qremesher.symmetry_x = True

        excute_remesh_loop()
        return {'FINISHED'}
