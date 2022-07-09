import bpy
import bmesh
# from .mesh_data_transfer import MeshDataTransfer
from .cupcko_mesh_data_transfer import *

class ApylyModiWithShapekey(bpy.types.Operator):
    '''传递物体形状'''
    bl_idname = "cupcko.apply_modi_with_shapekey"
    bl_label = "应用带形态键的模型的修改器"
    bl_options = {'REGISTER', 'UNDO'}
    modi_name: bpy.props.StringProperty(
        default=''
    )
    @classmethod
    def poll(cls, context):

        return 1

    def execute(self, context):
        '''
       1.应用单个
        要遍历修改器，暂时关闭其他修改器
        先get graph
        然后保存模型的每个形态键的状态
        删除所有形态键
        然后应用修改器，然后再传回去
        再开启其他修改器
        '''
        if self.modi_name=='all':
            # 生成meshdata
            apply_all = MeshData(context.active_object, deformed=True)

            # 生成形态键坐标组,形态键值 清单
            sk_array = apply_all.get_shape_keys_vert_pos()
            sk_values = apply_all.store_shape_keys_name_value()

            # 删除形态键 应用修改器
            with bpy.context.temp_override(active_object=apply_all.obj):
                bpy.ops.object.shape_key_remove(all=True)
                bpy.ops.object.convert(target='MESH')

            # 还原形态键
            for sk_name in sk_array:
                apply_all.set_position_as_shape_key(shape_key_name=sk_name, co=sk_array[sk_name],
                                                       value=sk_values[sk_name])

        else:
            modi_temp = bpy.context.active_object.modifiers
            modi_contr={}
            for modi in modi_temp:
                modi_contr[modi.name]=bpy.context.active_object.modifiers[modi.name].show_viewport
                if self.modi_name == modi.name:
                    # 跳过当前修改
                    continue
                else:
                    # 暂时关闭其他修改器
                    bpy.context.active_object.modifiers[modi.name].show_viewport = False


            #生成meshdata
            apply_single=MeshData(context.active_object,deformed=True)

            #生成形态键坐标组,形态键值 清单
            sk_array=apply_single.get_shape_keys_vert_pos()
            sk_values=apply_single.store_shape_keys_name_value()



            #删除形态键 应用修改器
            with bpy.context.temp_override(active_object=apply_single.obj):
                bpy.ops.object.shape_key_remove(all=True)
                bpy.ops.object.modifier_apply(modifier=self.modi_name)
            #还原形态键
            for sk_name in sk_array:
                apply_single.set_position_as_shape_key(shape_key_name=sk_name,co=sk_array[sk_name],value=sk_values[sk_name])

            for modi in modi_temp:
                # modi_contr[modi.name]=bpy.context.active_object.modifiers[modi.name].show_viewport
                if self.modi_name == modi.name:
                    # 跳过当前修改
                    continue
                else:
                    # 暂时关闭其他修改器
                    bpy.context.active_object.modifiers[modi.name].show_viewport = modi_contr[modi.name]
        self.report({'INFO'}, '应用完了')
        return {'FINISHED'}

class TransferShapeData(bpy.types.Operator):
    '''传递物体形状'''
    bl_idname = "cupcko.transfer_shape_data"
    bl_label = "传递形状"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        sample_space = context.object.cupcko_mesh_transfer_object.mesh_object_space
        return context.active_object is not None \
               and context.active_object.cupcko_mesh_transfer_object.mesh_shape_get_from_this is not None \
               and sample_space != "TOPOLOGY" and bpy.context.object.mode == "OBJECT"

    def execute(self, context):
        '''
        先用构建bvh树,然后取得每个顶点击中目标网格的坐标,然后通过这个坐标算出他的重心坐标,就是线性归一的值
        然后用重心坐标乘以目标物体的坐标 就是传递后的坐标
        
        '''
        a = context.active_object.cupcko_mesh_transfer_object
        source = a.mesh_shape_get_from_this
        as_shape_key = a.transfer_shape_as_key
        uv_space = True
        search_method = a.search_method
        mask_vertex_group = a.vertex_group_filter
        invert_mask = a.invert_vertex_group_filter
        world_space = False
        deformed_source = a.transfer_modified_source
        print("ops", deformed_source)
        transfer_data = MeshDataTransfer(thisobj=context.active_object, source=source, uv_space=uv_space,
                                         search_method=search_method, vertex_group=mask_vertex_group,
                                         invert_vertex_group=invert_mask,
                                         deformed_source=deformed_source, world_space=world_space)
        #   transfer_data.source.hitfaces_tri()
        #  transfer_data.thisobj.hitfaces_tri()
        transferred = transfer_data.transfer_vertex_position(as_shape_key=as_shape_key)
        transfer_data.free()
        if not transferred:
            self.report({'INFO'}, 'Unable to perform the operation')
            return {'CANCELLED'}
        self.report({'INFO'}, 'Shape transferred')
        return {'FINISHED'}


class TransferUV(bpy.types.Operator):
    '''传递uv'''
    bl_idname = "cupcko.transfer_uv_data"
    bl_label = "传递UV"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None \
               and context.active_object.cupcko_mesh_transfer_object.mesh_shape_get_from_this is not None \
               and bpy.context.object.mode == "OBJECT"

    def execute(self, context):
        source = context.object.cupcko_mesh_transfer_object.mesh_shape_get_from_this
        transfer_data = MeshDataTransfer(source=source, thisobj=context.active_object)
        transfer_data.transfer_uv()
        transfer_data.free()
        self.report({'INFO'}, 'UV transferred')
        return {'FINISHED'}

    # 弹出是否执行窗口
    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)


class Cupcko_return_selected_obj(bpy.types.Operator):
    '''多选物体,编辑模式选择一部分顶点,返回顶点所属物体'''
    bl_idname = "cupcko.return_selected_obj"
    bl_label = "选编返物"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return 1

    def execute(self, context):
        select_obj = bpy.context.selected_objects
        list = []
        bpy.ops.object.mode_set(mode='EDIT')
        for obj in select_obj:
            if obj.type == "MESH":
                # print(obj.data.total_vert_sel)
                if obj.data.total_vert_sel > 0:
                    list.append(obj)
                    print(list)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        for obj in list:
            bpy.data.objects[obj.name].select_set(state=True)
        self.report({'INFO'}, '返回编辑模式顶点所属物体')
        return {'FINISHED'}


class SNA_OT_Hide_Empty(bpy.types.Operator):
    bl_idname = "sna.hide_empty"
    bl_label = "hide_empty"
    bl_description = "隐藏所有空物体"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        try:
            pass  # Text Script Start
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.scale_clear(clear_delta=False)
            bpy.ops.object.select_all(action='DESELECT')

            for a in bpy.context.scene.objects:
                if a.type == "EMPTY":
                    a.hide_viewport = 1
                if a.type == "ARMATURE":
                    bpy.ops.object.posemode_toggle()
                    bpy.ops.pose.select_all(action='SELECT')
                    bpy.ops.pose.scale_clear()
                    bpy.ops.pose.rot_clear()
                    bpy.ops.pose.loc_clear()
                    bpy.ops.object.posemode_toggle()
            pass  # Text Script End
        except Exception as exc:
            print(str(exc) + " | Error in execute function of hide_empty")
        return {"FINISHED"}
