import bpy
#from .mesh_data_transfer import MeshDataTransfer 
from .cupcko_mesh_data_transfer import *
class TransferShapeData(bpy.types.Operator):
    '''传递物体形状'''
    bl_idname="cupcko.transfer_shape_data"
    bl_label="传递形状"
    bl_options = {'REGISTER','UNDO'}
    @classmethod
    def poll(cls, context):
        sample_space = context.object.cupcko_mesh_transfer_object.mesh_object_space
        return context.active_object is not None \
               and context.active_object.cupcko_mesh_transfer_object.mesh_shape_get_from_this is not None\
               and sample_space != "TOPOLOGY" and bpy.context.object.mode == "OBJECT"
    def execute(self,context):
        '''
        先用构建bvh树,然后取得每个顶点击中目标网格的坐标,然后通过这个坐标算出他的重心坐标,就是线性归一的值
        然后用重心坐标乘以目标物体的坐标 就是传递后的坐标
        
        '''
        a=context.active_object.cupcko_mesh_transfer_object
        source=a.mesh_shape_get_from_this
        as_shape_key=a.transfer_shape_as_key
        uv_space=True
        search_method=a.search_method
        mask_vertex_group = a.vertex_group_filter
        invert_mask = a.invert_vertex_group_filter
        search_method=a.search_method
        
        transfer_data=MeshDataTransfer(thisobj=context.active_object,source=source,uv_space=uv_space,
                                        search_method=search_method,vertex_group=mask_vertex_group,invert_vertex_group=invert_mask)
     #   transfer_data.source.hitfaces_tri() 
      #  transfer_data.thisobj.hitfaces_tri()                               
        transferred=transfer_data.transfer_vertex_position(as_shape_key=as_shape_key)
        transfer_data.free()
        if not transferred:
            self.report({'INFO'},'Unable to perform the operation')
            return{'CANCELLED'}
        self.report({'INFO'},'Shape transferred')
        return {'FINISHED'}
        
class TransferUV(bpy.types.Operator):
    '''传递uv'''
    bl_idname = "cupcko.transfer_uv_data"
    bl_label = "传递UV"
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None \
               and context.active_object.cupcko_mesh_transfer_object.mesh_shape_get_from_this is not None \
               and bpy.context.object.mode == "OBJECT"
    
    def execute(self, context):
        source=context.object.cupcko_mesh_transfer_object.mesh_shape_get_from_this
        transfer_data=MeshDataTransfer(source=source,thisobj=context.active_object)
        transfer_data.transfer_uv()
        transfer_data.free()
        self.report({'INFO'},'UV transferred')
        return {'FINISHED'}
    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)