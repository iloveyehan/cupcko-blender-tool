import math
import bpy
class Cupcko_vg_clean_vg(bpy.types.Operator):
    """清理激活顶点组,移除0权重"""

    bl_idname = "cupcko.vg_clean_vg"
    bl_label = "清理激活顶点组,移除0权重"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return bpy.context.object is not None

    def execute(self, context):
        # 获取当前活动对象
        obj = bpy.context.active_object
        # 检查是否为网格对象
        if not obj or obj.type != 'MESH':
            raise Exception("请先选择一个网格物体")
        # 获取当前激活的顶点组
        vertex_group = obj.vertex_groups.active
        if not vertex_group:
            raise Exception("当前没有激活的顶点组")
        # 存储需要移除的顶点索引
        to_remove = []
        # 遍历所有顶点
        for vertex in obj.data.vertices:
            # 获取该顶点在激活顶点组中的权重
            weight = 0.0
            for group in vertex.groups:
                if group.group == vertex_group.index:
                    weight = group.weight
                    break

            # 如果权重为0则标记移除
            if weight <= 0.0:
                to_remove.append(vertex.index)
        # 执行移除操作
        if to_remove:
            vertex_group.remove(to_remove)
            print(f"已从顶点组 '{vertex_group.name}' 中移除 {len(to_remove)} 个权重为0的顶点")
        else:
            print("当前顶点组中没有权重为0的顶点")
        # 刷新视图
        bpy.context.view_layer.update()
        return {'FINISHED'}
class Cupcko_vg_clean_advanced(bpy.types.Operator):
    """清理所有顶点组中的非法权重（0、负值、NaN）"""
    
    bl_idname = "cupcko.vg_clean_advanced"
    bl_label = "高级清理顶点组 (0/负值/NaN)"
    bl_options = {'UNDO'}
    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'MESH'
    def execute(self, context):
        obj = context.active_object
        report_buffer = []  # 用于存储清理报告
        
        # 优化：预先获取顶点组索引映射
        vg_index_map = {vg.index: vg for vg in obj.vertex_groups}
        
        # 并行遍历顶点数据
        for v in obj.data.vertices:
            for group in v.groups:
                vg = vg_index_map.get(group.group)
                if not vg:
                    continue
                
                weight = group.weight
                # 检测非法权重条件
                if math.isnan(weight) or weight <= 0.0:
                    # 使用顶点组自身的remove方法
                    vg.remove([v.index])
                    report_buffer.append(
                        f"顶点 {v.index} -> {vg.name}: "
                        f"非法权重 { 'NaN' if math.isnan(weight) else f'{weight:.4f}'}"
                    )
        # 生成最终报告
        if report_buffer:
            final_report = (
                f"清理完成，共发现 {len(report_buffer)} 个非法权重：\n" +
                "\n".join(report_buffer[:10]) + 
                ("\n......" if len(report_buffer)>10 else "")
            )
            self.report({'INFO'}, final_report)
        else:
            self.report({'INFO'}, "未发现需要清理的非法权重")
        context.view_layer.update()
        return {'FINISHED'}
class Cupcko_vg_metarig_to_rig(bpy.types.Operator):
    """将顶点组转换为rigifiy类型"""

    bl_idname = "cupcko.vg_metarig_to_rigify"
    bl_label = "将顶点组转换为rigifiy类型"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return bpy.context.object is not None

    def execute(self, context):
        for i in bpy.context.object.vertex_groups:
            if i.name[:4] != 'DEF-':
                i.name = 'DEF-' + i.name
        return {'FINISHED'}

class Cupcko_vg_remove_selected_wt(bpy.types.Operator):
    """将选择的顶点从权重移除"""

    bl_idname = "cupcko.vg_remove_selected_wt"
    bl_label = "将选择的顶点从权重移除"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return bpy.context.object is not None

    def execute(self, context):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.object.vertex_group_remove_from()
        bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
        return {'FINISHED'}

class Cupcko_vg_rig_to_metarig(bpy.types.Operator):
    """将顶点组转换为metarig类型，去除def前缀"""

    bl_idname = "cupcko.vg_rigify_to_metarig"
    bl_label = "去除顶点组DEF前缀"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return bpy.context.object is not None

    def execute(self, context):
        for i in bpy.context.object.vertex_groups:
            if i.name[:4] == 'DEF-':
                i.name = i.name[4:]
        return {'FINISHED'}


def sna_add_to_data_pt_vertex_groups_4A52F(self, context):
    if not (False):
        layout = self.layout
        grid_19CD5 = layout.grid_flow(columns=6, row_major=False, even_columns=False, even_rows=False, align=False)
        grid_19CD5.enabled = True
        grid_19CD5.active = True
        grid_19CD5.use_property_split = False
        grid_19CD5.use_property_decorate = False
        grid_19CD5.alignment = 'Expand'.upper()
        grid_19CD5.scale_x = 1.0
        grid_19CD5.scale_y = 1.0
        if not True: grid_19CD5.operator_context = "EXEC_DEFAULT"
        row_CC1A6 = grid_19CD5.row(heading='', align=True)
        row_CC1A6.alert = False
        row_CC1A6.enabled = True
        row_CC1A6.active = True
        row_CC1A6.use_property_split = False
        row_CC1A6.use_property_decorate = False
        row_CC1A6.scale_x = 1.0
        row_CC1A6.scale_y = 1.0
        row_CC1A6.alignment = 'Expand'.upper()
        if not True: row_CC1A6.operator_context = "EXEC_DEFAULT"
        op = row_CC1A6.operator('cupcko.vg_metarig_to_rigify', text='转rigify', icon_value=0, emboss=True,
                                depress=False)
        op = row_CC1A6.operator('cupcko.vg_rigify_to_metarig', text='转metarig', icon_value=0, emboss=True,
                                depress=False)
        op = row_CC1A6.operator('cupcko.vg_clean_vg', text='清理0权重', icon_value=0, emboss=True,
                                depress=False)
        op = row_CC1A6.operator('cupcko.vg_clean_advanced', text='清理所有组0权重new', icon_value=0, emboss=True,
                                depress=False)


class Cupcko_vg_clear_unused(bpy.types.Operator):
    """删除没有使用的顶点组（形变骨骼，修改器），不包括被其他物体使用的顶点组"""

    bl_idname = "cupcko.vg_clear_unused"
    bl_label = "删除没有使用的顶点组"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return bpy.context.object is not None

    def execute(self, context):
        '''遍历当前激活骨骼修改器中的骨骼，加入列表，遍历修改器使用的顶点组'''
        obj = bpy.context.object
        used_vg = []
        armature = []
        # 检查所有修改器
        for mod in obj.modifiers:
            # 这里我们检查几个常见的修改器属性
            if hasattr(mod, 'vertex_group') and mod.vertex_group is not None:
                used_vg.append(mod.vertex_group)
            # 需要骨骼激活状态
            if mod.type == 'ARMATURE' and mod.object is not None and mod.show_viewport:
                armature.append(mod.object)
        # 检查形变骨骼
        for a in armature:
            for b in a.data.bones:
                if b.use_deform:
                    used_vg.append(b.name)
        # 检查顶点组
        for vg in obj.vertex_groups:
            if vg.name not in used_vg:
                obj.vertex_groups.remove(vg)
        return {'FINISHED'}


class Cupcko_vg_remove_zero(bpy.types.Operator):
    """删除权重为0的顶点组"""

    bl_idname = "cupcko.vg_remove_zero"
    bl_label = "删除权重为0的顶点组"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return bpy.context.object is not None

    def execute(self, context):
        '''遍历所有顶点组，大于0的跳过'''
        obj = bpy.context.object
        unused_vg = []

        # 确保物体是一个网格
        if obj.type == 'MESH':
            # 遍历所有顶点组
            for v_group in obj.vertex_groups:
                used = False  # 假设顶点组未被使用

                # 遍历所有顶点检查是否属于当前顶点组
                for vertex in obj.data.vertices:
                    for group in vertex.groups:
                        if group.group == v_group.index and group.weight != 0:
                            used = True  # 顶点分配给顶点组
                            break

                    if used:
                        break  # 退出顶点循环

                # 输出顶点组及其使用状态
                if not used:
                    unused_vg.append(v_group.name)
            for vg_name in unused_vg:
                obj.vertex_groups.remove(obj.vertex_groups[vg_name])

        return {'FINISHED'}




import re


def determine_and_convert(vertex_group_name):
    # 定义左右边的标识符及其转换规则
    sides = [
        {"left": "_L_", "right": "_R_"},
        {"left": "_l_", "right": "_r_"},
        {"left": "_l", "right": "_r"},
        {"left": "_L", "right": "_R"},
        {"left": ".l", "right": ".r"},
        {"left": ".L", "right": ".R"},
        {"left": "Left", "right": "Right"},
        {"left": "left", "right": "right"},
    ]

    # 对每一组左右标识符进行检查和转换
    for side in sides:
        left_pattern = re.escape(side["left"])
        right_pattern = re.escape(side["right"])

        # 检查并替换左边标识符为右边标识符
        if re.search(left_pattern, vertex_group_name, ):
            return re.sub(left_pattern, side["right"], vertex_group_name, )
        # 检查并替换右边标识符为左边标识符
        elif re.search(right_pattern, vertex_group_name, ):
            return re.sub(right_pattern, side["left"], vertex_group_name, )

    # 如果没有找到任何匹配的标识符，返回原名称
    print(vertex_group_name)
    return vertex_group_name


class Cupcko_vg_mirror_weight(bpy.types.Operator):
    """镜像顶点权重"""

    bl_idname = "cupcko.vg_mirror_weight"
    bl_label = "镜像顶点权重"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return bpy.context.object is not None

    def execute(self, context):
        temp_mode=bpy.context.object.mode

        # 确保Blender处于对象模式
        bpy.ops.object.mode_set(mode='OBJECT')

        # 获取当前激活的模型A
        model_a = bpy.context.view_layer.objects.active

        # 记录模型A当前激活顶点组a_g的名称
        active_vg_name = model_a.vertex_groups.active.name

        # 创建模型B和模型C为模型A的副本
        model_b = model_a.copy()
        model_b.data = model_a.data.copy()
        model_b.name = "B"
        bpy.context.collection.objects.link(model_b)

        model_c = model_a.copy()
        model_c.data = model_a.data.copy()
        model_c.name = "C"
        bpy.context.collection.objects.link(model_c)

        # 在X轴上缩放模型B为-1，实现镜像
        model_b.scale.x *= -1

        # 确保变更生效
        bpy.context.view_layer.update()

        # 为模型C添加DataTransfer修改器，传递模型B的顶点组
        data_transfer_mod = model_c.modifiers.new(name="DataTransfer", type='DATA_TRANSFER')
        data_transfer_mod.object = model_b
        data_transfer_mod.use_vert_data = True
        data_transfer_mod.data_types_verts = {'VGROUP_WEIGHTS'}
        data_transfer_mod.vert_mapping = 'POLYINTERP_NEAREST'

        # 应用DataTransfer修改器到模型C
        bpy.context.view_layer.objects.active = model_c
        bpy.ops.object.datalayout_transfer(modifier="DataTransfer")
        bpy.ops.object.modifier_apply(modifier=data_transfer_mod.name)

        # 清理模型C的顶点组，只留下a_g
        for vg in model_c.vertex_groups:
            if vg.name != active_vg_name:
                model_c.vertex_groups.remove(vg)

        mirrored = determine_and_convert(model_c.vertex_groups.active.name)
        model_c.vertex_groups.active.name = mirrored
        # 为模型A添加DataTransfer修改器，传递模型C的a_g顶点组
        bpy.context.view_layer.objects.active = model_a
        data_transfer_mod_a = model_a.modifiers.new(name="DataTransferA", type='DATA_TRANSFER')
        data_transfer_mod_a.object = model_c
        data_transfer_mod_a.use_vert_data = True
        data_transfer_mod_a.data_types_verts = {'VGROUP_WEIGHTS'}
        data_transfer_mod.vert_mapping = 'POLYINTERP_NEAREST'
        # 应用DataTransfer修改器到模型A
        bpy.ops.object.datalayout_transfer(modifier="DataTransferA")

        model_a.vertex_groups.active_index = model_a.vertex_groups.find(mirrored)
        bpy.ops.object.modifier_apply(modifier=data_transfer_mod_a.name)
        bpy.data.meshes.remove(model_b.data)
        bpy.data.meshes.remove(model_c.data)


        bpy.ops.object.mode_set(mode=temp_mode)
        return {'FINISHED'}
class Cupcko_vg_symmetry_weight(bpy.types.Operator):
    """对称顶点权重，适用于居中的顶点组"""

    bl_idname = "cupcko.vg_symmetry_weight"
    bl_label = "对称顶点权重"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return bpy.context.object is not None

    def execute(self, context):
        temp_mode = bpy.context.object.mode
        # 确保Blender处于对象模式
        bpy.ops.object.mode_set(mode='OBJECT')

        # 获取当前激活的模型A
        model_a = bpy.context.view_layer.objects.active

        # 记录模型A当前激活顶点组a_g的名称
        active_vg_name = model_a.vertex_groups.active.name

        # 创建模型B和模型C为模型A的副本
        model_b = model_a.copy()
        model_b.data = model_a.data.copy()
        model_b.name = "B"
        bpy.context.collection.objects.link(model_b)

        model_c = model_a.copy()
        model_c.data = model_a.data.copy()
        model_c.name = "C"
        bpy.context.collection.objects.link(model_c)

        bpy.context.view_layer.objects.active = model_b  # 激活模型B
        # 添加并应用镜像修改器
        mirror_mod = model_b.modifiers.new(name="Mirror", type='MIRROR')
        bpy.context.object.modifiers["Mirror"].use_axis[0] = True
        bpy.context.object.modifiers["Mirror"].use_bisect_axis[0] = True
        bpy.context.object.modifiers["Mirror"].use_bisect_flip_axis[0] = True

        bpy.ops.object.modifier_apply(modifier=mirror_mod.name)
        # 添加并应用切分修改器

        # 为模型C添加DataTransfer修改器，传递模型B的顶点组
        data_transfer_mod = model_c.modifiers.new(name="DataTransfer", type='DATA_TRANSFER')
        data_transfer_mod.object = model_b
        data_transfer_mod.use_vert_data = True
        data_transfer_mod.data_types_verts = {'VGROUP_WEIGHTS'}
        data_transfer_mod.vert_mapping = 'POLYINTERP_NEAREST'

        # 应用DataTransfer修改器到模型C
        bpy.context.view_layer.objects.active = model_c
        bpy.ops.object.datalayout_transfer(modifier="DataTransfer")
        bpy.ops.object.modifier_apply(modifier=data_transfer_mod.name)

        # 清理模型C的顶点组，只留下a_g
        for vg in model_c.vertex_groups:
            if vg.name != active_vg_name:
                model_c.vertex_groups.remove(vg)
        mirrored = determine_and_convert(model_c.vertex_groups.active.name)
        model_c.vertex_groups.active.name = mirrored

        # 为模型A添加DataTransfer修改器，传递模型C的a_g顶点组
        bpy.context.view_layer.objects.active = model_a
        data_transfer_mod_a = model_a.modifiers.new(name="DataTransferA", type='DATA_TRANSFER')
        data_transfer_mod_a.object = model_c
        data_transfer_mod_a.use_vert_data = True
        data_transfer_mod_a.data_types_verts = {'VGROUP_WEIGHTS'}
        data_transfer_mod.vert_mapping = 'POLYINTERP_NEAREST'

        # 应用DataTransfer修改器到模型A
        bpy.ops.object.datalayout_transfer(modifier="DataTransferA")
        bpy.ops.object.modifier_apply(modifier=data_transfer_mod_a.name)
        model_a.vertex_groups.active_index = model_a.vertex_groups.find(mirrored)
        bpy.data.meshes.remove(model_b.data)
        bpy.data.meshes.remove(model_c.data)
        bpy.ops.object.mode_set(mode=temp_mode)
        return {'FINISHED'}