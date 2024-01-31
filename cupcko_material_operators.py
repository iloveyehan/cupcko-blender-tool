import bpy
class Cupcko_mt_clear_unused_material(bpy.types.Operator):
    """清除未使用的材质"""

    bl_idname = "cupcko.mt_clear_unused_material"
    bl_label = "清除未使用的材质"
    bl_options = {'UNDO'}


    @classmethod
    def poll(cls, context):
        return 1

    def execute(self, context):
        #先记录有用的，清除所有，再append
        for obj in bpy.context.selected_objects:
            if obj.type=='MESH':

                # 物体没材质的情况
                if obj.material_slots[:] == []:
                    continue
                mt_list = {}
                for face_i in obj.data.polygons:

                    name = obj.material_slots[face_i.material_index].name
                    if name not in mt_list.keys():
                        mt_list[name] = []
                    mt_list[name].append(face_i.index)
                obj.data.materials.clear()

                obj.data.materials.clear()
                if len(mt_list) !=0:
                    m_name_list=list(mt_list.keys())
                    for i in range(len(mt_list)):
                        obj.data.materials.append(bpy.data.materials[m_name_list[i]])
                        for face_id in mt_list[m_name_list[i]]:
                            print(face_id,'--',i)
                            obj.data.polygons[face_id].material_index=i
                del  mt_list
        return {'FINISHED'}
class Cupcko_mt_fix_view_material_metal(bpy.types.Operator):
    """取消掉金属视图着色"""

    bl_idname = "cupcko.mt_fix_view_material_metal"
    bl_label = "取消掉视图显示的金属1"
    bl_options = {'UNDO'}


    @classmethod
    def poll(cls, context):
        return 1

    def execute(self, context):
        for m in bpy.data.materials:
            m.metallic = 0
        return {'FINISHED'}