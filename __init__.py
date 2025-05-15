'''
mesh transfer部分参考了Maurizio Memoli的meshdatatransfer
'''
import bpy
from bpy import context
from bpy.props import PointerProperty
# from numpy import inf
import bpy.utils
import sys
import os
from .cupcko_operators import *
from .cupcko_uv_operators import *
from .cupcko_material_operators import *
from .cupcko_vg_ops import *
from . import flatten_uv
from . import cupcko_camera_driver
from . import edge_length
from .cupcko_mesh_data_transfer import *
from .cupcko_bone_ops import *
from .update import CheckUpdateOperator
# if sys.platform == 'win32': os.system('chcp 65001')

# import importlib

# importlib.reload(flatten_uv)
# importlib.reload(cupcko_mesh_data_transfer)
# importlib.reload(cupcko_operators)
# importlib.reload(cupcko_camera_driver)

bl_info = {
    "name": "cupcko",
    "author": "cupcko",
    "version": (1, 0, 6),
    "blender": (2, 93, 0),
    "location": "到处都是",
    "description": "快速编辑,镜像,整理自定义骨骼形状",
    "tracker_url": "123",
    # "category": "用户"
}
#
#
from bpy.types import Operator, AddonPreferences
from bpy.props import StringProperty, IntProperty, BoolProperty


class ExampleAddonPreferences(AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __name__
    luanguage_switch: BoolProperty(name="语言切换", default=False)
    mouse_deps_switch: BoolProperty(name="鼠标深度", default=False)
    surface_paint_switch: BoolProperty(name="表面绘制", default=False)
    emulate_3_button_mouse: BoolProperty(name="三键鼠标", default=False)
    sculpt_rotate_switch: BoolProperty(name="旋转切换", default=False)

    def draw(self, context):
        layout = self.layout
        layout.label(text="预设")
        row = layout.row(align=True)
        row.prop(self, "luanguage_switch", toggle=True)
        row.prop(self, "mouse_deps_switch", toggle=True)
        row.prop(self, "surface_paint_switch", toggle=True)
        row.prop(self, "emulate_3_button_mouse", toggle=True)
        row.prop(self, "sculpt_rotate_switch", toggle=True)
        row2 = layout.row(align=True)
        row2.operator("cupcko.check_update", text="检查更新")

class Cupcko_Panel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Item"
    @classmethod
    def poll(cls, context):
        return (context.object is not None)

    bl_idname = "VIEW3D_PT_test_1"
    bl_label = "CupckoTool"

    def draw(self, context):
        layout = self.layout
        layout.label(text="反馈群:536440291")
        box_4A26D = layout.box()
        box_4A26D.alert = False
        box_4A26D.enabled = True
        box_4A26D.active = True
        box_4A26D.use_property_split = False
        box_4A26D.use_property_decorate = False
        box_4A26D.alignment = 'Right'.upper()
        box_4A26D.scale_x = 1.0
        box_4A26D.scale_y = 1.1380000114440918
        box_4A26D.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        col_125D6 = box_4A26D.column(heading='', align=True)
        col_125D6.alert = False
        col_125D6.enabled = True
        col_125D6.active = True
        col_125D6.use_property_split = False
        col_125D6.use_property_decorate = False
        col_125D6.scale_x = 1.0
        col_125D6.scale_y = 1.399999976158142
        col_125D6.alignment = 'Expand'.upper()
        col_125D6.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        row_B24E1 = col_125D6.row(heading='', align=True)
        row_B24E1.alert = False
        row_B24E1.enabled = True
        row_B24E1.active = True
        row_B24E1.use_property_split = False
        row_B24E1.use_property_decorate = False
        row_B24E1.scale_x = 1.0
        row_B24E1.scale_y = 1.0
        row_B24E1.alignment = 'Expand'.upper()
        row_B24E1.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        if bpy.context.preferences.inputs.use_mouse_depth_navigate:
            op = row_B24E1.operator(Cupcko_rotate_center_switch.bl_idname, text='鼠标深度', icon_value=256, emboss=True,
                                    depress=False)
        else:
            op = row_B24E1.operator(Cupcko_rotate_center_switch.bl_idname, text='屏幕深度', icon_value=256, emboss=True,
                                    depress=False)
        op = row_B24E1.operator('cup.annotate_surface', text='表面绘制', icon_value=197, emboss=True, depress=False)
        if bpy.context.preferences.inputs.use_mouse_emulate_3_button:
            op = row_B24E1.operator(Cupcko_3button_mouse_switch.bl_idname, text='三键已开启', icon_value=209, emboss=True,
                                    depress=False)
        else:
            op = row_B24E1.operator(Cupcko_3button_mouse_switch.bl_idname, text='三键已关闭', icon_value=209, emboss=True,
                                    depress=False)

        if bpy.context.preferences.inputs.view_rotate_method == 'TRACKBALL':
            op = row_B24E1.operator(Cupcko_rotate_method_switch.bl_idname, text='当前:轨迹球', icon_value=238, emboss=True,
                                    depress=False)
        else:
            op = row_B24E1.operator(Cupcko_rotate_method_switch.bl_idname, text='当前:转盘', icon_value=238, emboss=True,
                                    depress=False)
        row_23868 = col_125D6.row(heading='', align=True)
        row_23868.alert = False
        row_23868.enabled = True
        row_23868.active = True
        row_23868.use_property_split = False
        row_23868.use_property_decorate = False
        row_23868.scale_x = 1.0
        row_23868.scale_y = 1.0
        row_23868.alignment = 'Expand'.upper()
        row_23868.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        if bpy.context.mode != 'EDIT_MESH':
            op = row_23868.operator('cup.edit_custom_shape', text='编辑', icon_value=548, emboss=True, depress=False)
            op = row_23868.operator('cup.mirror_custom_shape', text='镜像', icon_value=446, emboss=True, depress=False)
            op = row_23868.operator('cup.cs_group_orgnize', text='整理', icon_value=179, emboss=True, depress=False)
        else:
            op = row_23868.operator(Cupcko_exit_edit_shape.bl_idname)
        row_AF6DF = col_125D6.row(heading='', align=True)
        row_AF6DF.alert = False
        row_AF6DF.enabled = True
        row_AF6DF.active = True
        row_AF6DF.use_property_split = True
        row_AF6DF.use_property_decorate = False
        row_AF6DF.scale_x = 1.0
        row_AF6DF.scale_y = 1.0
        row_AF6DF.alignment = 'Expand'.upper()
        row_AF6DF.operator_context = "INVOKE_DEFAULT" if False else "EXEC_DEFAULT"
        obj = context.active_object
        if obj and obj.type == 'MESH' and obj.data.shape_keys and obj.data.shape_keys.key_blocks.get('uv_flat') and \
                obj.data.shape_keys.key_blocks['uv_flat'].value > 0.99:
            op = row_AF6DF.operator(flatten_uv.Create_flat_mesh.bl_idname, text='UV>Mesh', icon_value=582, emboss=True,
                                    depress=False)
        else:
            op = row_AF6DF.operator('cup.create_flat_mesh', text='MESH>UV', icon_value=582, emboss=True, depress=False)
        op = row_AF6DF.operator(flatten_uv.Dupulicate_mesh_aply_key.bl_idname, text='应用', icon_value=583, emboss=True,
                                depress=False)
        if obj and obj.type == 'MESH':
            col_BA204 = box_4A26D.column(heading='', align=True)
            col_BA204.alert = False
            col_BA204.enabled = True
            col_BA204.active = True
            col_BA204.use_property_split = False
            col_BA204.use_property_decorate = False
            col_BA204.scale_x = 1.0
            col_BA204.scale_y = 1.4
            col_BA204.alignment = 'Expand'.upper()
            col_BA204.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
            row_A164F = col_BA204.row(heading='', align=True)
            row_A164F.alert = False
            row_A164F.enabled = True
            row_A164F.active = True
            row_A164F.use_property_split = False
            row_A164F.use_property_decorate = False
            row_A164F.scale_x = 1.2
            row_A164F.scale_y = 1
            row_A164F.alignment = 'Expand'.upper()
            row_A164F.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"

            obj_prop = context.object.cupcko_mesh_transfer_object

            op = row_A164F.prop(obj_prop, 'transfer_modified_source', text='', toggle=True, icon_value=94)
            row_A164F.prop_search(obj_prop, "mesh_shape_get_from_this", context.scene, "objects", text='', icon='NONE')
            row_A164F.prop_search(obj_prop, "vertex_group_filter", bpy.context.active_object, "vertex_groups", text='',
                                  icon='GROUP_VERTEX')
            op = row_A164F.prop(obj_prop, 'invert_vertex_group_filter', text='', toggle=True, icon_value=8)
            row_DCBDC = col_BA204.row(heading='', align=True)
            row_DCBDC.alert = False
            row_DCBDC.enabled = True
            row_DCBDC.active = True
            row_DCBDC.use_property_split = False
            row_DCBDC.use_property_decorate = False
            row_DCBDC.scale_x = 1.0
            row_DCBDC.scale_y = 1.0
            row_DCBDC.alignment = 'Expand'.upper()
            row_DCBDC.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
            row_86263 = col_BA204.row(heading='', align=True)
            row_86263.alert = False
            row_86263.enabled = True
            row_86263.active = True
            row_86263.use_property_split = False
            row_86263.use_property_decorate = False
            row_86263.scale_x = 1.3
            row_86263.scale_y = 1.0
            row_86263.alignment = 'Expand'.upper()
            row_86263.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
            row_86263.prop(obj_prop, 'search_method', text='', icon_value=30, emboss=True, expand=False, slider=True,
                           toggle=False, invert_checkbox=False,
                           index=0)
            op = row_86263.operator('cupcko.transfer_uv_data', text='传递UV', icon_value=493, emboss=True, depress=False)
            op = row_86263.operator('cupcko.transfer_shape_data', text='传递形状', icon_value=452, emboss=True, depress=False)
            row_86263.prop(obj_prop, 'transfer_shape_as_key', text='', icon_value=176)
            op = row_86263.operator(Cupcko_fix_vertex_mirroring.bl_idname, text='修复对称', icon_value=737, emboss=True,
                                    depress=False)


def sna_add_to_data_pt_modifiers_E5089(self, context):
    if bpy.context.active_object.type == 'MESH' and bpy.context.active_object.modifiers and bpy.context.active_object.data.shape_keys:
        layout = self.layout
        box_89ACB = layout.box()
        box_89ACB.alert = False
        box_89ACB.enabled = True
        box_89ACB.active = True
        box_89ACB.use_property_split = False
        box_89ACB.use_property_decorate = False
        box_89ACB.alignment = 'Expand'.upper()
        box_89ACB.scale_x = 1.0
        box_89ACB.scale_y = 1.0
        row_2AF10 = box_89ACB.row(heading='', align=False)
        row_2AF10.alert = False
        row_2AF10.enabled = True
        row_2AF10.active = True
        row_2AF10.use_property_split = False
        row_2AF10.use_property_decorate = False
        row_2AF10.scale_x = 1.0
        row_2AF10.scale_y = 1.0
        row_2AF10.alignment = 'Expand'.upper()
        op = row_2AF10.operator('cupcko.apply_modi_with_shapekey', text='强制应用全部', icon_value=0, emboss=True,
                                depress=False)
        op.mod_name = 'all'
        row_33EA9 = box_89ACB.row(heading='', align=False)
        row_33EA9.alert = False
        row_33EA9.enabled = True
        row_33EA9.active = True
        row_33EA9.use_property_split = False
        row_33EA9.use_property_decorate = False
        row_33EA9.scale_x = 1.0
        row_33EA9.scale_y = 1.0
        row_33EA9.alignment = 'Expand'.upper()
        for mod in bpy.context.active_object.modifiers:
            op = row_33EA9.operator('cupcko.apply_modi_with_shapekey', text=f'{mod.name}', icon_value=0, emboss=True,
                                    depress=False)
            op.mod_name = mod.name


class VIEW3D_HT_Language(bpy.types.Header):
    # Panel
    bl_space_type = 'VIEW_3D'
    bl_region_type = "HEADER"
    bl_options = {'REGISTER', 'UNDO'}

    bl_label = "Cupcko"

    def draw(self, context):
        if context.region.alignment != 'RIGHT':
            layout = self.layout
            row1 = layout.row(align=True)
            row1.scale_x = 0.8
            if bpy.context.preferences.addons[__name__].preferences.luanguage_switch:
                row1.operator("cup.language_switch")
            # row1 = layout.row()
            if bpy.context.preferences.addons[__name__].preferences.mouse_deps_switch:
                if bpy.context.preferences.inputs.use_mouse_depth_navigate:
                    row1.operator(Cupcko_rotate_center_switch.bl_idname, text='鼠标深度')

                else:
                    row1.operator(Cupcko_rotate_center_switch.bl_idname, text='屏幕深度')
            if bpy.context.preferences.addons[__name__].preferences.surface_paint_switch:
                row1.operator("cup.annotate_surface")
            if bpy.context.preferences.addons[__name__].preferences.emulate_3_button_mouse:
                if bpy.context.preferences.inputs.use_mouse_emulate_3_button:
                    op = row1.operator(Cupcko_3button_mouse_switch.bl_idname, text='三键已开启')
                else:
                    op = row1.operator(Cupcko_3button_mouse_switch.bl_idname, text='三键已关闭')
            if bpy.context.preferences.addons[__name__].preferences.sculpt_rotate_switch:
                if bpy.context.preferences.inputs.view_rotate_method == 'TRACKBALL':
                    row1.operator(Cupcko_rotate_method_switch.bl_idname, text='当前:轨迹球')
                else:
                    row1.operator(Cupcko_rotate_method_switch.bl_idname, text='当前:转盘')
            row1.operator(Cupcko_Switch_High.bl_idname, text='高模')
            row1.operator(Cupcko_Switch_Low.bl_idname, text='低模')

# class Init_settings():
#     def __init__(self):
#         self.zh_CN=self.detect_language()
#     def detect_language(self):
#         if bpy.app.version[0]==3:
#             return 'zh_CN'
#         elif bpy.app.version[0]>3:
#             return 'zh_HANS'
# setting=Init_settings()
def _language_switch():
    context_language = bpy.context.preferences.view.use_translate_interface
    view_l = bpy.context.preferences.view.language
    if view_l not in ['zh_CN','zh_HANS']:
        #如果当前不是中文
        try:
            bpy.context.preferences.view.language = 'zh_CN'
        except:
            bpy.context.preferences.view.language = 'zh_HANS'
        bpy.context.preferences.view.use_translate_new_dataname = False
    else:
        try:
            bpy.context.preferences.view.language='en_US'
        except:
            pass
        if context_language:
            bpy.context.preferences.view.use_translate_interface = False
        elif context_language == False:
            bpy.context.preferences.view.use_translate_interface = True
    # elif view_l != 'DEFAULT':
    bpy.context.preferences.view.use_translate_new_dataname = False


def do_not_pick_oneself(self, object):
    if bpy.context.active_object == object:
        return False
    return object.type == 'MESH'


def only_pick_mesh(self, object):
    return object.type == 'MESH'


class Meshdata_Settings(bpy.types.PropertyGroup):
    mesh_shape_get_from_this: bpy.props.PointerProperty(name="source mesh", description="采样此模型", type=bpy.types.Object,
                                                        poll=do_not_pick_oneself)
    mesh_object_space: bpy.props.EnumProperty(
        items=[('WORLD_SPACE', 'World', '', 1), ('LOCAL_SPACE', 'Local', '', 2), ('UV_SPACE', 'active uv', '', 3),
               ('TOPOLOGY_SPACE', 'Topology', '', 4)],
        name="Object Space", default='LOCAL_SPACE')
    search_method: bpy.props.EnumProperty(
        items=[('CLOSEST', 'Closest', '', 1), ('RAYCAST', 'Raycast', '', 2), ('-X', 'Left', '', 3),
               ('+X', 'Right', '', 4)],
        name="Search method", default='CLOSEST')
    transfer_shape_as_key: bpy.props.BoolProperty(name='transfer as shape key',
                                                  description="做成形态键")
    vertex_group_filter: bpy.props.StringProperty(name="Vertex Group", description="仅传递顶点组中的顶点")
    # vertex_group_filter: bpy.props.PointerProperty(name="Vertex Group", description="仅传递顶点组中的顶点",
    #                                                type=bpy.types.VertexGroups, poll=only_pick_mesh)
    invert_vertex_group_filter: bpy.props.BoolProperty(name="Invert vertex group", description="反转顶点组")
    transfer_modified_source: bpy.props.BoolProperty()


class Cupcko_rotate_center_switch(bpy.types.Operator):
    bl_idname = "cup.depth_on"
    bl_label = "鼠标深度"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if 1:
            return True

    def execute(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False
        try:
            if bpy.context.preferences.inputs.use_mouse_depth_navigate:
                bpy.context.preferences.inputs.use_mouse_depth_navigate = 0
            else:
                bpy.context.preferences.inputs.use_mouse_depth_navigate = 1
        finally:
            context.preferences.edit.use_global_undo = use_global_undo
            print('Cupcko_rotate_center_switch',bpy.context.preferences.inputs.use_mouse_depth_navigate)
        return {'FINISHED'}


class Cupcko_3button_mouse_switch(bpy.types.Operator):
    bl_idname = "cup.3button_mouse_switch"
    bl_label = "切换模拟三键鼠标"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if 1:
            return True

    def execute(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False
        try:
            if bpy.context.preferences.inputs.use_mouse_emulate_3_button:
                bpy.context.preferences.inputs.use_mouse_emulate_3_button = 0
            else:
                bpy.context.preferences.inputs.use_mouse_emulate_3_button = 1
        finally:
            context.preferences.edit.use_global_undo = use_global_undo

        return {'FINISHED'}


class Cupcko_annotate_surface(bpy.types.Operator):
    bl_idname = "cup.annotate_surface"
    bl_label = "表面绘制"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if 1:
            return True

    def execute(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False
        try:
            _annotate_surface()
        finally:
            context.preferences.edit.use_global_undo = use_global_undo
        self.report({'INFO'}, '画笔设置为表面绘制')
        return {'FINISHED'}


def _annotate_surface():
    bpy.context.scene.tool_settings.annotation_stroke_placement_view3d = 'SURFACE'


def _rotate_method_switch():
    method = bpy.context.preferences.inputs.view_rotate_method
    if method == 'TRACKBALL':
        bpy.context.preferences.inputs.view_rotate_method = 'TURNTABLE'
    elif method == 'TURNTABLE':
        bpy.context.preferences.inputs.view_rotate_method = 'TRACKBALL'


class Cupcko_rotate_method_switch(bpy.types.Operator):
    bl_idname = "cup.rotate_method_switch"
    bl_label = "切换旋转"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # context.mode == 'OBJECT' 
        if 1:
            return True

    def execute(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False
        try:
            _rotate_method_switch()
        finally:
            context.preferences.edit.use_global_undo = use_global_undo
        return {'FINISHED'}


class Cupcko_Language_switch(bpy.types.Operator):
    bl_idname = "cup.language_switch"
    bl_label = "语言切换"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # context.mode == 'OBJECT' 
        if 1:
            return True

    def execute(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False
        try:
            _language_switch()
        finally:
            context.preferences.edit.use_global_undo = use_global_undo
        return {'FINISHED'}
class Cupcko_Switch_High(bpy.types.Operator):
    bl_idname = "cup.switch_high"
    bl_label = "高模"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):

        return context.mode == 'OBJECT'

    def execute(self, context):
        # 遍历场景中的所有物体
        for obj in context.scene.objects:
            # 检查物体名称是否包含 "_high"
            if "_high" in obj.name:
                # 切换物体的可见性
                if obj.hide:
                    obj.hide_set(0)
                else:
                    obj.hide_set(1)

        return {'FINISHED'}
class Cupcko_Switch_Low(bpy.types.Operator):
    bl_idname = "cup.switch_low"
    bl_label = "低模"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):

        return context.mode == 'OBJECT'

    def execute(self, context):
        # 遍历场景中的所有物体
        for obj in context.scene.objects:
            # 检查物体名称是否包含 "low"
            if "_low" in obj.name:
                # 切换物体的可见性
                if obj.hide:
                    obj.hide_set(0)
                else:
                    obj.hide_set(1)

        return {'FINISHED'}
class Cupcko_exit_edit_shape(bpy.types.Operator):
    bl_idname = "cup.exit_edit_shape"
    bl_label = "应用形状"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.active_object:
            if context.mode == 'EDIT_MESH':
                if 'cs_' in context.active_object.name:
                    return True

    def execute(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False

        try:
            _exit_edit_shape()
        finally:
            context.preferences.edit.use_global_undo = use_global_undo
        return {'FINISHED'}


class Cupcko_edit_custom_shape(bpy.types.Operator):
    # tooltip
    '编辑自定义骨骼形状'

    bl_idname = "cup.edit_custom_shape"
    bl_label = "编辑形状"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.mode == 'POSE':
            if bpy.context.active_pose_bone:
                return True

    def execute(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False

        try:
            # if bpy.context.active_pose_bone.custom_shape:
            _edit_custom_shape()
            # else:
            #     self.report({"ERROR"}, "No custom shapes set for this bone. Create one first.")

        finally:
            context.preferences.edit.use_global_undo = use_global_undo
        return {'FINISHED'}


class Cupcko_mirror_custom_shape(bpy.types.Operator):
    # tooltip
    '镜像自定义骨骼形状'

    bl_idname = "cup.mirror_custom_shape"
    bl_label = "镜像形状"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.mode == 'POSE':
            if bpy.context.active_pose_bone:
                return True

    def execute(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False

        try:
            # if bpy.context.active_pose_bone.custom_shape:
            _mirror_custom_shape(self)
            # else:
            #     self.report({"ERROR"}, "No custom shapes set for this bone. Create one first.")

        finally:
            context.preferences.edit.use_global_undo = use_global_undo
        return {'FINISHED'}


class Cupcko_cs_group_orgnize(bpy.types.Operator):
    # tooltip
    '整合所有自定义形状物体到custom_group_master空物体下'

    bl_idname = "cup.cs_group_orgnize"
    bl_label = "整理"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # context.mode == 'OBJECT'
        if context.active_object is None:
            return 0
        if bpy.context.object.type == 'ARMATURE':
            return True

    def execute(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False

        try:

            cs_group_orgnize()


        finally:
            context.preferences.edit.use_global_undo = use_global_undo
        self.report({'INFO'}, '整理完了,查看cs_group_orgnize')
        return {'FINISHED'}


def _edit_custom_shape():
    bone = bpy.context.active_pose_bone
    bone.custom_shape_scale_xyz[0]=1
    object_rig = bpy.context.active_object

    print('1+' + bpy.context.active_object.name)
    # 确定物体是否有自定义骨骼,没有就新建,然后统一自定义骨骼名称
    if not bpy.context.active_pose_bone.custom_shape:
        bpy.ops.mesh.primitive_plane_add(size=2, calc_uvs=True, enter_editmode=False, align='WORLD', location=(0, 0, 0),
                                         rotation=(0, 0, 0), scale=(0, 0, 0))
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.delete(type='ONLY_FACE')
        bpy.ops.object.mode_set(mode='OBJECT')
        bone.custom_shape = bpy.context.active_object
    # 如果不小心删掉了自定义骨骼
    try:
        bpy.context.collection.objects.link(bone.custom_shape)

    except:
        pass

    mesh_custom_shape = bone.custom_shape

    mesh_custom_shape['object_rig'] = object_rig.name
    bone_custom_shape_transform = bone.custom_shape_transform
    print('2+' + bpy.context.active_object.name)
    if bone_custom_shape_transform:

        print(object_rig.matrix_world)
        print(bone_custom_shape_transform.matrix)
        mesh_custom_shape.matrix_world = object_rig.matrix_world @ bone_custom_shape_transform.matrix
        # 将物体模式的位移旋转缩放当成增量，进行矩阵乘法，得到最终骨骼所在位置角度，传给自定义骨骼
        # print (mesh_custom_shape.matrix_world)

    else:
        mesh_custom_shape.matrix_world = object_rig.matrix_world @ bone.matrix

    mesh_custom_shape.scale *= bone.custom_shape_scale_xyz
    mesh_custom_shape.scale *= bone.length
    print('3+' + bpy.context.active_object.name)
    bpy.ops.object.posemode_toggle()
    bpy.data.objects[object_rig.name].select_set(False)

    unhide_object(mesh_custom_shape)
    bpy.context.view_layer.objects.active = mesh_custom_shape
    bpy.data.objects[mesh_custom_shape.name].select_set(1)
    bpy.ops.object.make_single_user(object=True, obdata=True, material=False, animation=False, obdata_animation=False)
    mesh_custom_shape.name = '_cs_' + bone.name
    mesh_custom_shape.data.name = '_cs_' + bone.name
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')


def set_active_object(object_name):
    bpy.context.view_layer.objects.active = bpy.data.objects[object_name]
    bpy.data.objects[object_name].select_set(state=True)


def hide_object(obj_to_set):
    obj_to_set.hide_set(True)
    obj_to_set.hide_viewport = True


def unhide_object(obj_to_set):
    obj_to_set.hide_set(False)
    obj_to_set.hide_viewport = False


def hide_object_render(obj_to_set):
    obj_to_set.hide_set(True)
    obj_to_set.hide_render = True


def unlink_object(ob):
    for col in bpy.data.collections:
        if ob.name in col.objects:
            col.objects.unlink(ob)


def cs_group_orgnize():
    # 判断是否有自定义骨骼合集cs_group_master，若没有 创建一个
    bone_grp = bpy.context.object.pose.bones
    rig = bpy.context.active_object
    cs_group_master = None
    if not bpy.data.objects.get('custom_group_master'):
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        cs_group_master = bpy.context.active_object
        cs_group_master.name = 'custom_group_master'
        set_active_object(rig.name)
        bpy.ops.object.mode_set(mode='POSE')

    else:
        cs_group_master = bpy.data.objects['custom_group_master']
    set_active_object(rig.name)

    # hide_object(bpy.data.objects['custom_group_master'])
    for bone in bone_grp:
        if bone.custom_shape:
            bone.custom_shape.parent = bpy.data.objects['custom_group_master']
    for child in cs_group_master.children:
        unlink_object(child)
        try:
            cs_group_master.users_collection[0].objects.link(child)
        except:
            pass
        hide_object(child)
        hide_object_render(child)
    hide_object(cs_group_master)
    hide_object_render(cs_group_master)


def _exit_edit_shape():
    # 去掉所有面 完成后回到姿态模式
    cs_shape = bpy.context.active_object
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.delete(type='ONLY_FACE')
    bpy.ops.object.mode_set(mode='OBJECT')

    # object_rig=None
    object_rig_name = None
    for key in cs_shape.keys():
        if 'object_rig' in key:
            object_rig_name = cs_shape['object_rig']
            # object_rig=bpy.data.objects.get(object_rig_name)
    set_active_object(object_rig_name)
    bpy.ops.object.mode_set(mode='POSE')

    hide_object(cs_shape)


def get_bone_side(bone_name):
    mirror_char_in = ['l.', 'L.', 'l_', 'L_', 'r_', 'R_', 'R.', 'r.', '.l', '_l', '.L', '_l', '.r', '.R', '_R', '_r']
    mirror_char_ot = ['r.', 'R.', 'r_', 'R_', 'l_', 'L_', 'L.', 'l.', '.r', '_r', '.R', '_r', '.l', '.L', '_L', '_l']
    mirror_bone_name = 'None'
    for bone_side in mirror_char_in:
        # print('骨骼是左边还是右边='+bone_side)

        if bone_side in bone_name:
            n = bone_name.index(bone_side)
            length = len(bone_name)
            # print('长度=', length)
            # print('name序号=', n)
            i = mirror_char_in.index(bone_side)
            bone_side_mir = mirror_char_ot[i]
            # print(bone_name[n:])

            # if n+2<length and n-1>0:

            if n == 0:
                # 名称前置型骨骼
                mirror_bone_name = "".join((bone_side, bone_name))
                # print('名称前置型骨骼=' + mirror_bone_name)

            if n + 2 < length:
                if bone_name[n + 2] == '.' or bone_name[n + 2] == '_' or bone_name[n - 1] == '.' or bone_name[
                    n - 1] == '_':
                    # 名称中间型骨骼

                    split = bone_name.split(bone_side)
                    mirror_bone_name = "".join((split[0], bone_side_mir, split[1]))
                    # mirror_bone_name=split[0]+bone_side_mir+split[1]
                    # print('名称中间型骨骼=' + mirror_bone_name)
            # return(mirror_bone_name)

            elif bone_side == bone_name[-2:]:
                # 名称后置型骨骼
                mirror_bone_name = "".join((bone_name[:-2], bone_side_mir))
                # mirror_bone_name=bone_name[:-2]+bone_side_mir
                # print('名称后置型骨骼=' + mirror_bone_name)
                # print('bone_name=' + bone_name[-2:])
            # return(mirror_bone_name)
    return (mirror_bone_name)


def get_selected_pose_bones():
    return bpy.context.selected_pose_bones


def _mirror_custom_shape(self):
    cs_group_orgnize()
    # 先拿到骨骼物体名字，存起来，用列表查找镜像骨存起来，再判断有没有镜像骨
    rig_name = bpy.context.active_object.name
    rig = bpy.data.objects[rig_name]
    # selected_bone=get_selected_pose_bones()[0]

    for bone in get_selected_pose_bones():
        bone_name = bone.name
        try:
            bone.custom_shape.name = '_cs_' + bone_name
            bone.custom_shape.data.name = '_cs_' + bone_name
        except:
            pass
        split = []
        mirror_bone_name = ''
        mirror_cs_obj = None
        mirror_bone_name = get_bone_side(bone.name)

        if mirror_bone_name == 'None':
            self.report({'INFO'}, '无法镜像,你镜像个锤子')
        # print('选中骨骼无左右标识符,先加上.l或者.r后缀')
        else:
            mirror_bone = rig.pose.bones.get(mirror_bone_name)

            #  print('骨骼='+mirror_bone_name)
            # 选中骨骼无自定义骨骼形状
            if not bone.custom_shape:
                print('选中骨骼无自定义骨骼形状,先给自身创建一个,点击编辑')
            else:
                if mirror_bone.custom_shape:
                    # 有自定义骨骼
                    if not mirror_bone.custom_shape.name == '_cs_' + mirror_bone_name:
                        # 自定义骨骼名字不对
                        mirror_cs_obj = mirror_bone.custom_shape
                        mirror_cs_obj.name = '_cs_' + mirror_bone_name
                        # mirror_cs_obj.data=bone.custom_shape.data.copy()
                        # mirror_cs_obj.data.name='_cs_'+mirror_bone_name
                    # print('自定义骨骼名字不对,已自动更改为_cs_+骨骼名')
                    else:
                        # 自定义骨骼名字正确
                        #  print('自定义骨骼名字正确')
                        mirror_cs_obj = mirror_bone.custom_shape

                else:
                    # 没有自定义骨骼
                    # print('没有自定义骨骼,已自动补全')
                    bpy.ops.object.mode_set(mode='OBJECT')
                    bpy.ops.mesh.primitive_plane_add(size=2, calc_uvs=True, enter_editmode=False, align='WORLD',
                                                     location=(0, 0, 0), rotation=(0, 0, 0), scale=(0, 0, 0))
                    mirror_bone.custom_shape = bpy.context.active_object
                    mirror_cs_obj = mirror_bone.custom_shape
                    mirror_cs_obj.name = '_cs_' + mirror_bone_name
                mirror_cs_obj.data = bone.custom_shape.data.copy()
                mirror_cs_obj.data.name = '_cs_' + mirror_bone_name
                unhide_object(mirror_cs_obj)

                bpy.ops.object.mode_set(mode='OBJECT')

                set_active_object(mirror_cs_obj.name)
                # 设置变换中心为游标，将物体移动到游标
                bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'
                bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')

                bpy.ops.transform.mirror(constraint_axis=(True, False, False), orient_type='LOCAL')
                bpy.ops.object.mode_set(mode='OBJECT')
                hide_object(mirror_cs_obj)
                hide_object(bone.custom_shape)
                set_active_object(rig_name)
                bpy.ops.object.location_clear(clear_delta=False)

                bpy.ops.object.mode_set(mode='POSE')
                mirror_bone.custom_shape_scale_xyz = (1, 1, 1)

                bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'


class Cupcko_shape_keys_driver(bpy.types.Panel):
    bl_label = "Shape Keys"
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'}

    def draw(self, context):
        layout = self.layout
        add_lab = layout.row()
        add_lab.operator(cupcko_camera_driver.Camera_Driver.bl_idname)


from . import cupcko_node_add

classes = [
SNA_OT_Hide_Empty,
cupcko_node_add.Cupcko_add_NdotL,
flatten_uv.Create_flat_mesh,
Cupcko_Panel,
Cupcko_edit_custom_shape,
Cupcko_mirror_custom_shape,
Cupcko_exit_edit_shape,
Cupcko_cs_group_orgnize,

Cupcko_Language_switch,
Cupcko_3button_mouse_switch,
Cupcko_rotate_center_switch,
Cupcko_Switch_High,
Cupcko_Switch_Low,

Cupcko_annotate_surface,
Cupcko_rotate_method_switch,
flatten_uv.Dupulicate_mesh_aply_key,
Cupcko_return_selected_obj,
Meshdata_Settings,
TransferUV,
TransferShapeData,
ExampleAddonPreferences,
cupcko_camera_driver.Camera_Driver,
ApylyModiWithShapekey,
Cupcko_fix_vertex_mirroring,
Cupcko_combine_selected_bone_weights,
TransferMultiShapeData,
Cupcko_uv_unify_uv_name,
Cupcko_uv_unify_uv_name_for_bake,
Cupcko_uv_set_bake_active,
Cupcko_uv_set_bake_uv,
Cupcko_mt_clear_unused_material,
Cupcko_mt_fix_view_material_metal,
Cupcko_turn_off_allshapekeys,
Cupcko_unify_objdata_name,
Cupcko_vg_metarig_to_rig,
Cupcko_vg_rig_to_metarig,
Cupcko_vg_clear_unused,
Cupcko_vg_remove_zero,
Cupcko_vg_clean_vg,
Cupcko_vg_clean_advanced,
Cupcko_vg_remove_selected_wt,
Cupcko_vg_mirror_weight,
Cupcko_vg_symmetry_weight,
SyncActiveBoneNameOperator,
CheckUpdateOperator,
]


class SNA_AddonPreferences_6C2B8(bpy.types.AddonPreferences):
    bl_idname = 'Cupcko'

    def draw(self, context):
        if not (False):
            layout = self.layout
            box_4B933 = layout.box()
            box_4B933.alert = False
            box_4B933.enabled = True
            box_4B933.active = True
            box_4B933.use_property_split = False
            box_4B933.use_property_decorate = False
            box_4B933.alignment = 'Right'.upper()
            box_4B933.scale_x = 1.0
            box_4B933.scale_y = 1.1380000114440918
            box_4B933.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
            grid_7B5B9 = box_4B933.grid_flow(columns=6, row_major=False, even_columns=False, even_rows=False,
                                             align=True)
            grid_7B5B9.enabled = True
            grid_7B5B9.active = True
            grid_7B5B9.use_property_split = False
            grid_7B5B9.use_property_decorate = False
            grid_7B5B9.alignment = 'Expand'.upper()
            grid_7B5B9.scale_x = 1.0
            grid_7B5B9.scale_y = 1.0
            grid_7B5B9.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
            op = grid_7B5B9.operator('sn.dummy_button_operator', text='深度', icon_value=0, emboss=True, depress=False)
            op = grid_7B5B9.operator('sn.dummy_button_operator', text='深度', icon_value=0, emboss=True, depress=False)
            op = grid_7B5B9.operator('sn.dummy_button_operator', text='深度', icon_value=0, emboss=True, depress=False)
            op = grid_7B5B9.operator('sn.dummy_button_operator', text='深度', icon_value=0, emboss=True, depress=False)
def show_console(self, context):
    if not (False):
        layout = self.layout
        op = layout.operator('wm.console_toggle', text='输出', icon_value=0, emboss=True, depress=False)
#插入rigify
def sna_add_to_data_pt_rigify_0066A(self, context):
    if not (False):
        layout = self.layout
        op = layout.operator('pose.rigify_generate_with_weightbone', text='生成rigify显示权重骨', icon_value=0, emboss=True, depress=False)
def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)
    edge_length.edge_length_register()
    bpy.types.TOPBAR_HT_upper_bar.append(VIEW3D_HT_Language.draw)
    bpy.types.DATA_PT_shape_keys.append(Cupcko_shape_keys_driver.draw)
    bpy.types.DATA_PT_modifiers.append(sna_add_to_data_pt_modifiers_E5089)
    bpy.types.Object.cupcko_mesh_transfer_object = PointerProperty(type=Meshdata_Settings)
    if "rigify" in bpy.context.preferences.addons:
        bpy.utils.register_class(Generate_Rigify_With_WeightBone)
        bpy.types.DATA_PT_rigify.append(sna_add_to_data_pt_rigify_0066A)
    bpy.utils.register_class(SNA_AddonPreferences_6C2B8)
    bpy.types.TOPBAR_MT_editor_menus.append(show_console)
    bpy.types.DATA_PT_vertex_groups.append(sna_add_to_data_pt_vertex_groups_4A52F)


def unregister():
    from bpy.utils import unregister_class
    for c in reversed(classes):
        unregister_class(c)
    edge_length.edge_length_unregister()
    bpy.types.TOPBAR_HT_upper_bar.remove(VIEW3D_HT_Language.draw)
    bpy.types.DATA_PT_shape_keys.remove(Cupcko_shape_keys_driver.draw)
    bpy.types.DATA_PT_modifiers.remove(sna_add_to_data_pt_modifiers_E5089)
    del bpy.types.Object.cupcko_mesh_transfer_object
    if "rigify" in bpy.context.preferences.addons:
        bpy.utils.unregister_class(Generate_Rigify_With_WeightBone)
        bpy.types.DATA_PT_rigify.remove(sna_add_to_data_pt_rigify_0066A)
    bpy.utils.unregister_class(SNA_AddonPreferences_6C2B8)
    bpy.types.TOPBAR_MT_editor_menus.remove(show_console)
    bpy.types.DATA_PT_vertex_groups.remove(sna_add_to_data_pt_vertex_groups_4A52F)


if __name__ == "__main__":
    register()
