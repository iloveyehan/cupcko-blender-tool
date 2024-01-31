import bpy
class Cupcko_uv_unify_uv_name(bpy.types.Operator):
    """统一uv名称"""

    bl_idname = "cupcko.unify_uv_name"
    bl_label = "uv_规范当前激活uv名称为UVMap"
    bl_options = {'UNDO'}


    @classmethod
    def poll(cls, context):
        return 1

    def execute(self, context):
        for i in bpy.context.selected_objects:
            if i.type=='MESH':
                if not len(i.data.uv_layers):
                    i.data.uv_layers.new(name='UVMap')
                i.data.uv_layers.active.name='UVMap'

        return {'FINISHED'}
class Cupcko_uv_unify_uv_name_for_bake(bpy.types.Operator):
    """统一uv名称，创建烘焙uv，删除其他uv"""

    bl_idname = "cupcko.unify_uv_name_for_bake"
    bl_label = "uv_创建烘焙uv，删除其他uv"
    bl_options = {'UNDO'}


    @classmethod
    def poll(cls, context):
        return 1

    def execute(self, context):
        for i in bpy.context.selected_objects:
            if i.type=='MESH':
                #没有uv创建uv
                list = []
                if not len(i.data.uv_layers):
                    i.data.uv_layers.new(name='UVMap')
                else:
                    i.data.uv_layers.active.name='UVMap'
                    #删掉其他的

                    for n in i.data.uv_layers:
                        list.append(n.name)
                    for u in list:
                        if u!='UVMap' and u!='bake':
                            i.data.uv_layers.remove(i.data.uv_layers[u])
                #新建bake uv
                if 'bake' in list:
                    i.data.uv_layers['bake'].active=1
                    continue
                bake=i.data.uv_layers.new(name='bake')
                bake.active=1
        return {'FINISHED'}
class Cupcko_uv_set_bake_active(bpy.types.Operator):
    """设置烘焙uv为激活uv"""

    bl_idname = "cupcko.set_bake_active"
    bl_label = "uv_设置烘焙uv为激活uv"
    bl_options = {'UNDO'}


    @classmethod
    def poll(cls, context):
        return 1

    def execute(self, context):
        for i in bpy.context.selected_objects:
            if i.type=='MESH':
                if i.data.uv_layers[:]==[]:
                    i.data.uv_layers.new(name='UVMap')
                else:
                    for v in i.data.uv_layers:
                        if v.name=='bake':
                            v.active=1
        return {'FINISHED'}
class Cupcko_uv_set_bake_uv(bpy.types.Operator):
    """清理uv，设置bake为uvmap"""

    bl_idname = "cupcko.set_bake_uv"
    bl_label = "uv_删除其他uv，设置bake为uvmap"
    bl_options = {'UNDO'}


    @classmethod
    def poll(cls, context):
        return 1

    def execute(self, context):
        for i in bpy.context.selected_objects:
            if i.type=='MESH':
                if not len(i.data.uv_layers):
                    i.data.uv_layers.new(name='UVMap')
                elif len(i.data.uv_layers)==1:
                    i.data.uv_layers[0].name = 'UVMap'
                else:
                    list=[]
                    for n in i.data.uv_layers:
                        list.append(n.name)
                    if 'bake' in list:
                        for u in list:
                            if u != 'bake':
                                i.data.uv_layers.remove(i.data.uv_layers[u])
                        i.data.uv_layers[0].name='UVMap'


        return {'FINISHED'}