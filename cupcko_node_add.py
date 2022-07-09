from hashlib import new
import bpy


class Cupcko_add_NdotL(bpy.types.Operator):
    '''在鼠标位置创建节点'''
    bl_idname = "cupcko.add_ndotl"
    bl_label = "在鼠标位置添加NdotL"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return 1

    def invoke(self, context, event):
        # 读取鼠标位置，传给操作符
        region = context.region.view2d
        ui_scale = context.preferences.system.ui_scale
        x, y = region.region_to_view(event.mouse_region_x, event.mouse_region_y)
        self.x, self.y = x / ui_scale, y / ui_scale
        return self.execute(context)

    def execute(self, context):
        active_obj_name = context.active_object.name
        # 判断下有没有主光
        main_light = 'MainLightDirection'
        main_light_empty = 'MainLightEmpty'
        # 如果没有主光就应该是第一次创建灯光向量
        if bpy.data.objects.get('MainLightDirection') is None or bpy.data.objects['MainLightDirection'].type != 'LIGHT':
            bpy.ops.object.light_add(type='SUN', radius=1, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
            context.object.name = 'MainLightDirection'
            loc = bpy.context.object.matrix_world.translation
            if bpy.data.objects.get('MainLightEmpty') is None:
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = bpy.data.objects[main_light]
                bpy.data.objects[main_light].select_set(state=True)
                bpy.ops.object.rotation_clear(clear_delta=False)

                bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(loc[0], loc[1], loc[2] - 1),
                                         scale=(1, 1, 1))
                bpy.context.object.scale *= 0.01
                context.object.name = 'MainLightEmpty'
                bpy.context.view_layer.objects.active = bpy.data.objects['MainLightDirection']
                bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
                bpy.data.objects[main_light_empty].hide_select = 1
                bpy.data.objects[main_light_empty].hide_viewport = 1



            else:
                # 把已经存在的空物体挪到灯光下面
                bpy.data.objects[main_light_empty].matrix_world.translation = (loc[0], loc[1], loc[2] - 1)
                bpy.data.objects[main_light_empty].select_set(state=True)
                bpy.context.view_layer.objects.active = bpy.data.objects[main_light]
                bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
                bpy.data.objects[main_light_empty].hide_select = 1
                bpy.data.objects[main_light_empty].hide_viewport = 1
        else:
            # 如果有主光就清空下旋转，判断是否有空物体，没有就创建(有就意味着已经做过灯光向量，就不用管)
            if bpy.data.objects.get('MainLightEmpty') is None:
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = bpy.data.objects[main_light]
                bpy.data.objects[main_light].select_set(state=True)
                bpy.ops.object.rotation_clear(clear_delta=False)

                loc = bpy.context.object.matrix_world.translation
                bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(loc[0], loc[1], loc[2] - 1),
                                         scale=(1, 1, 1))
                bpy.context.object.scale *= 0.01
                context.object.name = 'MainLightEmpty'
                bpy.context.view_layer.objects.active = bpy.data.objects['MainLightDirection']
                bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
                bpy.data.objects[main_light_empty].hide_select = 1
                bpy.data.objects[main_light_empty].hide_viewport = 1
            else:
                # 有可能手滑 动了空物体的位置
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = bpy.data.objects[main_light]
                bpy.data.objects[main_light].select_set(state=True)
                bpy.ops.object.rotation_clear(clear_delta=False)

                loc = bpy.data.objects[main_light].matrix_world.translation
                bpy.data.objects[main_light_empty].matrix_world.translation = (loc[0], loc[1], loc[2] - 1)
                bpy.data.objects[main_light_empty].hide_select = 1
                bpy.data.objects[main_light_empty].hide_viewport = 1

        # 重新设置激活物体为模型
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = bpy.data.objects[active_obj_name]
        bpy.data.objects[active_obj_name].select_set(state=True)
        # 创建灯光位置节点，上驱动
        active_m_name = context.object.active_material.name
        n_light = bpy.data.materials[active_m_name].node_tree.nodes.new('ShaderNodeCombineXYZ')
        n_light.location.x = self.x
        n_light.location.y = self.y
        n_light.label = '灯光位置'
        n_light.name = '灯光位置'
        # 给xyz轴都加上驱动
        for axis in n_light.inputs:
            fcurve = n_light.inputs[axis.name].driver_add('default_value')
            fcurve.driver.expression = 'var'
            fcurve.driver.variables.new()
            fcurve.driver.variables['var'].type = 'TRANSFORMS'
            fcurve.driver.variables['var'].targets[0].id = bpy.data.objects[main_light]
            fcurve.driver.variables['var'].targets[0].transform_space = 'WORLD_SPACE'
            fcurve.driver.variables['var'].targets[0].transform_type = f'LOC_{axis.name}'
        # 创建空物体节点
        n_light_em = bpy.data.materials[active_m_name].node_tree.nodes.new('ShaderNodeCombineXYZ')
        n_light_em.location.x = self.x
        n_light_em.location.y = self.y - 250
        n_light_em.label = '空物体位置'
        n_light_em.name = '空物体位置'
        # 给xyz轴都加上驱动
        for axis in n_light_em.inputs:
            fcurve = n_light_em.inputs[axis.name].driver_add('default_value')
            fcurve.driver.expression = 'var'
            fcurve.driver.variables.new()
            fcurve.driver.variables['var'].type = 'TRANSFORMS'
            fcurve.driver.variables['var'].targets[0].id = bpy.data.objects[main_light_empty]
            fcurve.driver.variables['var'].targets[0].transform_space = 'WORLD_SPACE'
            fcurve.driver.variables['var'].targets[0].transform_type = f'LOC_{axis.name}'

        n_sub1 = bpy.data.materials[active_m_name].node_tree.nodes.new('ShaderNodeVectorMath')
        n_sub1.location.x = self.x + 200
        n_sub1.location.y = self.y - 125
        n_sub1.operation = 'SUBTRACT'
        n_sub1.label = '相减'
        n_sub1.name = '相减'
        # 把灯光向量计算出来
        bpy.data.materials[active_m_name].node_tree.links.new(n_light.outputs[0], n_sub1.inputs[0])
        bpy.data.materials[active_m_name].node_tree.links.new(n_light_em.outputs[0], n_sub1.inputs[1])
        # 归一化灯光向量
        n_normalize1 = bpy.data.materials[active_m_name].node_tree.nodes.new('ShaderNodeVectorMath')
        n_normalize1.location.x = self.x + 400
        n_normalize1.location.y = self.y - 125
        n_normalize1.operation = 'NORMALIZE'
        n_normalize1.label = '归一化'
        n_normalize1.name = '归一化'
        bpy.data.materials[active_m_name].node_tree.links.new(n_sub1.outputs[0], n_normalize1.inputs[0])

        # 添加法线
        n_normal1 = bpy.data.materials[active_m_name].node_tree.nodes.new('ShaderNodeNewGeometry')
        n_normal1.location.x = self.x
        n_normal1.location.y = self.y + 250
        # new_node.operation='DOT_PRODUCT'
        n_normal1.label = '法线'
        n_normal1.name = '法线'

        n_normalize2 = bpy.data.materials[active_m_name].node_tree.nodes.new('ShaderNodeVectorMath')
        n_normalize2.location.x = self.x + 400
        n_normalize2.location.y = self.y + 250
        n_normalize2.operation = 'NORMALIZE'
        n_normalize2.label = '归一化'
        n_normalize2.name = '归一化'
        bpy.data.materials[active_m_name].node_tree.links.new(n_normal1.outputs[1], n_normalize2.inputs[0])
        # 添加点乘
        n_ndot1 = bpy.data.materials[active_m_name].node_tree.nodes.new('ShaderNodeVectorMath')
        n_ndot1.location.x = self.x + 600
        n_ndot1.location.y = self.y
        n_ndot1.operation = 'DOT_PRODUCT'
        n_ndot1.label = '点乘'
        n_ndot1.name = '点乘'

        # 连接点乘
        bpy.data.materials[active_m_name].node_tree.links.new(n_normalize2.outputs[0], n_ndot1.inputs[0])
        bpy.data.materials[active_m_name].node_tree.links.new(n_normalize1.outputs[0], n_ndot1.inputs[1])
        return {'FINISHED'}
