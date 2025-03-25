import bpy
import bmesh
import re
# from .mesh_data_transfer import MeshDataTransfer
from .cupcko_mesh_data_transfer import *

#
class ApylyModiWithShapekey(bpy.types.Operator):
    '''应用带形态键的模型的修改器'''
    bl_idname = "cupcko.apply_modi_with_shapekey"
    bl_label = "应用带形态键的模型的修改器"
    bl_options = {'REGISTER', 'UNDO'}
    mod_name: bpy.props.StringProperty(
        default=''
    )

    @classmethod
    def poll(cls, context):

        return 1

    def execute(self, context):
        '''

        要遍历修改器，暂时关闭其他修改器
        先get graph
        然后保存模型的每个形态键的状态
        删除所有形态键
        然后应用修改器，然后再传回去
        再开启其他修改器
        有可能会报错
        镜像修改器：
        应用镜像修改器时，有的形态键左右交叉了，造成顶点数不匹配
        '''
        if self.mod_name == 'all':

            print('ApylyModiWithShapekey',self.mod_name)

            # print(self.mod_name)

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
            # a=0
            for sk in sk_array:

                apply_all.set_position_as_shape_key(shape_key_name=sk, co=sk_array[sk],
                                                    value=sk_values[sk])


        else:
            # print(self.mod_name)
            mod_temp = bpy.context.active_object.modifiers
            mod_off = {}
            for modi in mod_temp:
                # 记录修改器状态
                mod_off[modi.name] = bpy.context.active_object.modifiers[modi.name].show_viewport
                if self.mod_name == modi.name:
                    # 跳过当前修改
                    continue
                else:
                    # 暂时关闭其他修改器
                    bpy.context.active_object.modifiers[modi.name].show_viewport = False

            # 生成meshdata
            obj=bpy.context.active_object
            apply_single = MeshData(context.active_object, deformed=True)
            # apply_single = MeshDataTransfer(source=obj, thisobj=obj,
            #                                  deformed_source=True)
            # 生成形态键坐标组,形态键值 清单
            sk_array = apply_single.get_shape_keys_vert_pos()
            sk_values = apply_single.store_shape_keys_name_value()

            # 删除形态键 应用修改器
            with bpy.context.temp_override(active_object=obj):
                bpy.ops.object.shape_key_remove(all=True)
                bpy.ops.object.modifier_apply(modifier=self.mod_name)
            # 还原形态键
            for sk in sk_array:
                apply_single.set_position_as_shape_key(shape_key_name=sk, co=sk_array[sk], value=sk_values[sk])

            for modi in mod_temp:
                # modi_contr[modi.name]=bpy.context.active_object.modifiers[modi.name].show_viewport
                if self.mod_name == modi.name:
                    # 跳过当前修改
                    continue
                else:
                    # 暂时关闭其他修改器
                    bpy.context.active_object.modifiers[modi.name].show_viewport = mod_off[modi.name]
        self.report({'INFO'}, '应用完了')
        return {'FINISHED'}


class TransferShapeData(bpy.types.Operator):
    '''传递物体形状'''
    bl_idname = "cupcko.transfer_shape_data"
    bl_label = "传递形状"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.active_object is None:
            return 0
        sample_space = context.object.cupcko_mesh_transfer_object.mesh_object_space
        return context.active_object is not None \
               and context.active_object.cupcko_mesh_transfer_object.mesh_shape_get_from_this is not None \
               and sample_space != "TOPOLOGY" and (bpy.context.object.mode == "OBJECT" or bpy.context.object.mode == "SCULPT" ) \
               and context.active_object.cupcko_mesh_transfer_object.search_method[-1:]!='X'

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
        print("TransferShapeData ops", deformed_source)
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
class TransferMultiShapeData(bpy.types.Operator):
    '''传递物体形状 多个形态键'''
    bl_idname = "cupcko.transfer_multi_shape_data"
    bl_label = "传递形状"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.active_object is None:
            return 0
        sample_space = context.object.cupcko_mesh_transfer_object.mesh_object_space
        return context.active_object is not None \
               and context.active_object.cupcko_mesh_transfer_object.mesh_shape_get_from_this is not None \
               and sample_space != "TOPOLOGY" and (bpy.context.object.mode == "OBJECT" or bpy.context.object.mode == "SCULPT" ) \
               and context.active_object.cupcko_mesh_transfer_object.search_method[-1:]!='X'

    def execute(self, context):
        '''
        先用构建bvh树,然后取得每个顶点击中目标网格的坐标,然后通过这个坐标算出他的重心坐标,就是线性归一的值
        然后用重心坐标乘以目标物体的坐标 就是传递后的坐标

        '''
        a = context.active_object.cupcko_mesh_transfer_object

        source = a.mesh_shape_get_from_this
        k_v={}
        if hasattr(source.data.shape_keys, 'key_blocks'):
            #记录k v
            for s in source.data.shape_keys.key_blocks:
                k_v[s.name]=s.value
                if s.name in ['basis’,‘Basis’,‘基型']:
                    continue
                s.value=1
                as_shape_key = a.transfer_shape_as_key
                uv_space = True
                search_method = a.search_method
                mask_vertex_group = a.vertex_group_filter
                invert_mask = a.invert_vertex_group_filter
                world_space = False
                deformed_source = a.transfer_modified_source
                print("TransferShapeData ops", deformed_source)
                transfer_data = MeshDataTransfer(thisobj=context.active_object, source=source, uv_space=uv_space,
                                                 search_method=search_method, vertex_group=mask_vertex_group,
                                                 invert_vertex_group=invert_mask,
                                                 deformed_source=deformed_source, world_space=world_space,sk_name=s.name)
                #   transfer_data.source.hitfaces_tri()
                #  transfer_data.thisobj.hitfaces_tri()

                transferred = transfer_data.transfer_vertex_position(as_shape_key=as_shape_key)

                transfer_data.free()
                if not transferred:
                    self.report({'INFO'}, 'Unable to perform the operation')
                    return {'CANCELLED'}
                context.active_object.data.shape_keys.key_blocks[s.name].value=k_v[s.name]
                s.value=k_v[s.name]
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
               and bpy.context.object.mode == "OBJECT" \
               and context.active_object.cupcko_mesh_transfer_object.search_method[-1:]!='X'

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
                    print('Cupcko_return_selected_obj',list)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        for obj in list:
            bpy.data.objects[obj.name].select_set(state=True)
        self.report({'INFO'}, '返回编辑模式顶点所属物体')
        return {'FINISHED'}

sides = [
    {"left": "_L_", "right": "_R_"},
    {"left": "_l_", "right": "_r_"},
    {"left": "_l", "right": "_r"},
    {"left": "_L", "right": "_R"},
    {"left": ".l", "right": ".r"},
    {"left": ".L", "right": ".R"},
]


def determine_and_convert(vertex_group_name, LR=None):
    '''参数：顶点组名，顶点组位置
        只有顶点组名时，返回左右转换后的顶点组名，中间顶点组不变
        传入顶点组位置时，返回 顶点组位置是否匹配
        [True, last_match, replaced_string]'''
    # 定义左右边的标识符及其转换规则

    # 根据LR参数选择匹配左边还是右边的标识符，并准备替换的映射
    pattern = ''
    replace_map = {}
    if LR == '-x':
        pattern = "|".join([re.escape(side["left"]) for side in sides])
        replace_map = {side["left"]: side["right"] for side in sides}
    elif LR == '+x':
        pattern = "|".join([re.escape(side["right"]) for side in sides])
        replace_map = {side["right"]: side["left"] for side in sides}
    elif LR == 'center':
        # 创建正则表达式模式，将所有左右标识符组合成一个正则表达式
        pattern = "|".join([re.escape(side["left"]) + "|" + re.escape(side["right"]) for side in sides])

        # 使用正则表达式查找左右标识符
        matches = re.findall(pattern, vertex_group_name)

        # 如果没有找到任何匹配项，返回True；否则返回False
        return [not bool(matches), None, vertex_group_name]
    elif LR == None:
        # 构建匹配左边标识符的正则表达式，并准备替换的映射

        pattern = "|".join([re.escape(side["left"]) + "|" + re.escape(side["right"]) for side in sides])

        replace_map = {**{side["left"]: side["right"] for side in sides},
                       **{side["right"]: side["left"] for side in sides}}

    # 查找所有匹配项
    matches = re.findall(pattern, vertex_group_name)
    if not matches:
        return [False, None, vertex_group_name]

    # 仅替换最后一个匹配项
    last_match = matches[-1]
    replaced_string = re.sub(re.escape(last_match), replace_map[last_match], vertex_group_name, count=1)

    # 返回结果
    return [True, last_match, replaced_string]
class Cupcko_combine_selected_bone_weights(bpy.types.Operator):
    """多选骨骼，合并权重到激活骨骼，删除其他骨骼（支持镜像处理）"""
    bl_idname = "cupcko.combine_selected_bone_weights"
    bl_label = "合并骨骼权重，删除其他骨骼"
    bl_options = {'REGISTER', 'UNDO'}
    mirror: bpy.props.BoolProperty(
        name="镜像处理",
        description="对选中骨骼的对称骨骼执行相同操作",
        default=False
    )
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'ARMATURE'
    def execute(self, context):
        armature = context.active_object
        active_bone = context.active_bone
        child_objs = [obj for obj in armature.children if obj.type == 'MESH']
        # 获取镜像骨骼名称
        mirror_active_name = determine_and_convert(active_bone.name)[2]
        mirror_active_bone = None
        if self.mirror and mirror_active_name:
            mirror_active_bone = armature.data.bones.get(mirror_active_name)
        # 切换到姿态模式获取选中骨骼
        bpy.ops.object.mode_set(mode='POSE')
        pose_bones = context.selected_pose_bones
        # 处理所有子网格对象
        for obj in child_objs:
            mesh_data = MeshData(obj)
            v_count = len(obj.data.vertices)
            # 初始化权重数组
            weights_active = np.zeros(v_count, dtype=np.float32)
            weights_active.shape = (v_count, 1)
            weights_mirror = np.zeros_like(weights_active) if mirror_active_bone else None
            # 遍历所有选中骨骼
            for pose_bone in pose_bones:
                bone_name = pose_bone.name
                # 处理原始骨骼权重
                if (wgts := mesh_data.get_vertex_group_weights(bone_name)) is not None:
                    weights_active += wgts
                # 处理镜像骨骼权重
                if self.mirror:
                    if mirror_name := determine_and_convert(bone_name)[2]:
                        if (mirror_wgts := mesh_data.get_vertex_group_weights(mirror_name)) is not None:
                            weights_mirror += mirror_wgts
            # 写入权重数据
            mesh_data.set_vertex_group_weights(weights_active, active_bone.name)
            if mirror_active_bone and weights_mirror is not None:
                mesh_data.set_vertex_group_weights(weights_mirror, mirror_active_bone.name)
            # 清理顶点组
            self.cleanup_vertex_groups(obj, pose_bones, active_bone, mirror_active_bone)
            mesh_data.free_memory()
        # 删除骨骼
        self.remove_bones(context, armature, active_bone, mirror_active_bone)
        self.report({'INFO'}, '合并完成（镜像已启用）' if self.mirror else '合并完成')
        return {'FINISHED'}

    def cleanup_vertex_groups(self, obj, pose_bones, active_bone, mirror_active_bone):
        """清理原始和镜像顶点组"""
        vg_names_to_keep = {active_bone.name}
        if mirror_active_bone:
            vg_names_to_keep.add(mirror_active_bone.name)
        for bone in pose_bones:
            # 删除原始顶点组
            if bone.name in obj.vertex_groups and bone.name not in vg_names_to_keep:
                obj.vertex_groups.remove(obj.vertex_groups[bone.name])

            # 删除镜像顶点组
            if self.mirror:
                if mirror_name := determine_and_convert(bone.name)[2]:
                    if mirror_name in obj.vertex_groups and mirror_name not in vg_names_to_keep:
                        obj.vertex_groups.remove(obj.vertex_groups[mirror_name])

    def remove_bones(self, context, armature, active_bone, mirror_active_bone):
        """删除骨骼逻辑"""
        bpy.ops.object.mode_set(mode='EDIT')
        edit_bones = armature.data.edit_bones
        # 收集需要删除的骨骼
        to_remove = []
        for bone in context.selected_editable_bones:
            if bone.name == active_bone.name or \
                    (mirror_active_bone and bone.name == mirror_active_bone.name):
                continue

            to_remove.append(bone)

            # 添加镜像骨骼到删除列表
            if self.mirror:
                if mirror_name := determine_and_convert(bone.name)[2]:
                    if mirror_name in edit_bones:
                        to_remove.append(edit_bones[mirror_name])
        # 去重并删除
        seen = set()
        for bone in to_remove:
            if bone.name not in seen and bone.name in edit_bones:
                seen.add(bone.name)
                edit_bones.remove(bone)
        bpy.ops.object.mode_set(mode='POSE')

# class Cupcko_combine_selected_bone_weights(bpy.types.Operator):
#     '''多选骨骼，合并权重到激活骨骼，删除其他骨骼'''
#     bl_idname = "cupcko.combine_selected_bone_weights"
#     bl_label = "合并骨骼权重，删除其他骨骼"
#     bl_options = {'REGISTER', 'UNDO'}
#
#     @classmethod
#     def poll(cls, context):
#         if context.active_object is None:
#             return 0
#         return bpy.context.object.type=='ARMATURE'
#
#     def execute(self, context):
#         armature = bpy.context.active_object
#         child_obj=armature.children
#         bpy.ops.object.mode_set(mode='POSE')
#         posebone=bpy.context.selected_pose_bones
#
#         active_bone=bpy.context.active_bone
#         #做权重
#         for obj in child_obj:
#             if obj.type=='MESH':
#                 meshdata=MeshData(obj)
#                 #传入骨骼名称
#                 v_count = len(obj.data.vertices)
#                 weights = np.zeros(v_count, dtype=np.float32)
#                 weights.shape=(v_count, 1)
#                 for b in posebone:
#                     print('weight',b.name,type(weights))
#                     if meshdata.get_vertex_group_weights(b.name) is not None:
#
#                         weights +=meshdata.get_vertex_group_weights(b.name)
#                     if b.name==active_bone.name:
#                         continue
#                     if meshdata.vertex_groups.get(b.name):
#                         obj.vertex_groups.remove(obj.vertex_groups[b.name])
#                 #拿到最终权重，传入active bone
#                 meshdata.set_vertex_group_weights(weights,active_bone.name)
#                 meshdata.free_memory()
#         #删骨骼
#         bpy.ops.object.mode_set(mode='EDIT')
#         editbone = bpy.context.selected_editable_bones
#         for b in editbone:
#             if b.name==active_bone.name:
#                 continue
#             bpy.context.object.data.edit_bones.remove(b)
#             # with bpy.context.temp_override(active_object=armature,selected_editable_bones=b,active_bone=b):
#             #     bpy.ops.armature.dissolve()
#
#         bpy.ops.object.mode_set(mode='POSE')
#
#         self.report({'INFO'}, '合并完成')
#         return {'FINISHED'}
# #
#
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


class Cupcko_fix_vertex_mirroring(bpy.types.Operator):
    '''修复看起来镜像但是不对称的顶点'''
    bl_idname = "cupcko.fix_vertex_mirroring"
    bl_label = "修复看起来镜像但是不对称的顶点"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.active_object is None:
            return 0
        return context.active_object.cupcko_mesh_transfer_object.search_method[-1:] == 'X'

    def execute(self, context):
        a = context.active_object.cupcko_mesh_transfer_object
        mask_vertex_group = a.vertex_group_filter
        invert_mask = a.invert_vertex_group_filter
        world_space = False
        search_method = a.search_method
        transfer_modified_source = a.transfer_modified_source

        thisobj = context.active_object
        mode_t=thisobj.mode
        if mode_t!='OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        #记录修改器
        modi={}
        for m in thisobj.modifiers:
            if m.type == 'MASK':
                modi[m.name]=m.show_viewport
                m.show_viewport=0

        #记录形态键value
        sk_temp=0
        if hasattr(thisobj.data.shape_keys, 'key_blocks'):
            show_sk_only=thisobj.show_only_shape_key
            if thisobj.show_only_shape_key:
                show_sk_only=thisobj.show_only_shape_key
                thisobj.show_only_shape_key=0


            sk={}
            for k in thisobj.data.shape_keys.key_blocks:
                sk[k.name]=k.value
                if k.name==thisobj.active_shape_key.name:
                    k.value=1
                    continue
                k.value=0
            sk_temp=1


        source = bpy.data.objects.new('temp_mirror_mesh', thisobj.data.copy())
        bpy.context.collection.objects.link(source)
        mod = source.modifiers.new('temp_mirror', 'MIRROR')
        mod.use_bisect_axis[0] = True
        print('Cupcko_fix_vertex_mirroring',search_method[-2:])
        if  search_method[-2:]=='-X':
            mod.use_bisect_flip_axis[0] = True
        mod.merge_threshold = 0.00001
        mod.bisect_threshold = 0.00001

        transfer_data = MeshDataTransfer(source=source, thisobj=thisobj, search_method=search_method,
                                         vertex_group=mask_vertex_group,
                                         invert_vertex_group=invert_mask,
                                         deformed_source=True, world_space=world_space, symmetry_axis=search_method)
        # sk_values=transfer_data.thisobj.store_shape_keys_name_value()
        # transfer_data.thisobj.reset_shape_keys_values()
        transferred = transfer_data.fix_mirror_transfer_vertex_position()
        # transfer_data.thisobj.set_shape_keys_values(sk_values)
        transfer_data.free()
        bpy.data.objects.remove(source)
        #还原修改器
        for m in thisobj.modifiers:
            if m.type == 'MASK':
                m.show_viewport=modi[m.name]
        #还原形态键
        if sk_temp:
            for k in thisobj.data.shape_keys.key_blocks:
                k.value=sk[k.name]
            thisobj.show_only_shape_key = show_sk_only

        bpy.ops.object.mode_set(mode=mode_t)
        self.report({'INFO'}, 'Shape transferred')
        return {'FINISHED'}
def is_metarig(obj):
    if not (obj and obj.data and obj.type == 'ARMATURE'):
        return False
    if 'rig_id' in obj.data:
        return False
    for b in obj.pose.bones:
        if b.rigify_type != "":
            return True
    return False
class Generate_Rigify_With_WeightBone(bpy.types.Operator):
    """Generates a rig from the active metarig armature"""

    bl_idname = "pose.rigify_generate_with_weightbone"
    bl_label = "Rigify Generate Rig"
    bl_options = {'UNDO'}
    bl_description = 'Generates a rig from the active metarig armature'

    @classmethod
    def poll(cls, context):
        return is_metarig(context.object)

    def execute(self, context):
        bpy.ops.pose.rigify_generate()

        bpy.ops.object.mode_set(mode='OBJECT')
        print(context.selected_objects)
        print(context.object)
        context.selected_objects[0].data.layers[29] = True


        return {'FINISHED'}
class Cupcko_turn_off_allshapekeys(bpy.types.Operator):
    """关闭所有形态键"""

    bl_idname = "cupcko.turn_off_allshapekeys"
    bl_label = "关闭所有形态键"
    bl_options = {'UNDO'}
    bl_description = '关闭所有形态键'

    @classmethod
    def poll(cls, context):
        return 1

    def execute(self, context):
        for obj in context.selected_objects:
            if obj.type=="MESH":
                if obj.data.shape_keys:
                    for sk in obj.data.shape_keys.key_blocks:
                        sk.value=0

        return {'FINISHED'}
class Cupcko_unify_objdata_name(bpy.types.Operator):
    """整理模型场景，重命名obj.data与模型保持一致，为模型和材质添加obj前缀"""

    bl_idname = "cupcko.unify_objdata_name"
    bl_label = "统一所有obj和data的名字,为材质添加obj前缀,清理未使用的图片"
    bl_options = {'UNDO'}
    bl_description = '整理模型场景，重命名obj.data与模型保持一致，为模型和材质添加obj前缀,清理未使用的图片'

    @classmethod
    def poll(cls, context):
        return 1

    def execute(self, context):
        active_obj=bpy.context.active_object
        for obj in context.scene.objects:
            if obj.type=="MESH":
                if obj.name[:4]!='obj_':
                    obj.name='obj_'+obj.name
                obj.data.name=obj.name
                #材质
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.material_slot_remove_unused()

                for m in obj.material_slots:
                    if m.material is None:
                        continue
                    if m.material.name[:4] != 'obj_':
                        m.material.name='obj_'+m.material.name
                obj.select_set(False)
        mat_names=[]
        for mat in bpy.data.materials:
            mat_names.append(mat.name)

        material=bpy.data.materials
        for name in mat_names:
            if mat.name[:4]!='obj_':
                bpy.data.materials.remove(material[name])
                continue
            if material[name].use_nodes:
                nodes = material[name].node_tree.nodes
                for node in nodes:
                    if node.type == 'TEX_IMAGE' and not node.outputs[0].links:
                        nodes.remove(node)
                    elif node.type=='TEX_IMAGE' and node.image:
                        node.image.name='obj_'+node.image.name
            material[name].name=material[name].name[4:]
        if active_obj:
            bpy.context.view_layer.objects.active = active_obj
        return {'FINISHED'}

