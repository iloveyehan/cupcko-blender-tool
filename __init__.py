'''
mesh transfer部分参考了Maurizio Memoli的meshdatatransfer
'''
from .cupcko_operators import *
import bpy
from bpy import context
from bpy.props import PointerProperty
import bpy.utils
import sys
import os
#from .cupcko_operators import *
from . import flatten_uv
from . import cupcko_camera_driver
#from .flatten_uv import set_active_object
from .cupcko_mesh_data_transfer import *
if sys.platform == 'win32':os.system('chcp 65001')
from bpy.types import AddonPreferences as AP
import importlib
importlib.reload(flatten_uv)
importlib.reload(cupcko_mesh_data_transfer)
importlib.reload(cupcko_operators)
importlib.reload(cupcko_camera_driver)
bl_info = {
    "name": "cupcko",
    "author": "cupcko",
    "version": (1, 0, 3),
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
    luanguage_switch:BoolProperty(name="语言切换顶部开关", default=False)
    mouse_deps_switch:BoolProperty(name="鼠标深度顶部开关", default=False)
    surface_paint_switch:BoolProperty(name="表面绘制顶部开关", default=False)
    sculpt_rotate_switch:BoolProperty(name="旋转切换顶部开关", default=False)
    # filepath: StringProperty(
    #     name="Example File Path",
    #     subtype='FILE_PATH',
    # )
    # number: IntProperty(
    #     name="Example Number",
    #     default=4,
    # )
    # boolean: BoolProperty(
    #     name="Example Boolean",
    #     default=False,
    # )

    def draw(self, context):
        layout = self.layout
        layout.label(text="预设")
        layout.prop(self,"luanguage_switch",toggle=True)
        layout.prop(self,"mouse_deps_switch",toggle=True)
        layout.prop(self,"surface_paint_switch",toggle=True)
        layout.prop(self,"sculpt_rotate_switch",toggle=True)

# class OBJECT_OT_addon_prefs_example(Operator):
#     """Display example preferences"""
#     bl_idname = "object.addon_prefs_example"
#     bl_label = "Add-on Preferences Example"
#     bl_options = {'REGISTER', 'UNDO'}

#     def execute(self, context):
#         preferences = context.preferences
#         addon_prefs = preferences.addons[__name__].preferences

#         # info = ("Path: %s, Number: %d, Boolean %r" %
#         #         (addon_prefs.filepath, addon_prefs.number, addon_prefs.boolean))

#         # self.report({'INFO'}, info)
#         # print(info)

#         return {'FINISHED'}
# #
# class Cupcko_AddonPreferences(AP):
#     language_switch0: bpy.props.BoolProperty(name="语言切换顶部开关", default=True)
#      def update_activate_switch_translate(self, context):       
#         keymaps(self, register=self.activate_switch_translate, tool="switch_translate")
class Cupcko_Panel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Item"

    @classmethod
    def poll(cls, context):
        return (context.object is not None)
    bl_idname = "VIEW3D_PT_test_1"
    bl_label = "Cupcko:反馈群536440291"
    
    def draw(self, context):
        layout = self.layout
        #v =  bpy.context.preferences.view.use_translate_interface
 
        row = layout.row(align=True)
       # language_switch=layout.row(align=True)
        row1=layout.row()
        if bpy.context.mode !='EDIT_MESH':
            row.operator("cup.edit_custom_shape")
            row.operator(Cupcko_mirror_custom_shape.bl_idname,text="镜像", icon="MOD_MIRROR")
            row.operator(Cupcko_cs_group_orgnize.bl_idname)
           
        else:
            row.operator(Cupcko_exit_edit_shape.bl_idname)
        

        if bpy.context.preferences.inputs.use_mouse_depth_navigate==True:
            row1.operator(Cupcko_rotate_center_switch2.bl_idname)
            row1.operator(Cupcko_annotate_surface.bl_idname)
        else:
            row1.operator(Cupcko_rotate_center_switch.bl_idname)
            row1.operator(Cupcko_annotate_surface.bl_idname)  
        if bpy.context.preferences.inputs.view_rotate_method=='TRACKBALL':
            row1.operator(Cupcko_rotate_method_switch.bl_idname,text='当前:轨迹球')
        else:
            row1.operator(Cupcko_rotate_method_switch.bl_idname,text='当前:转盘')  
        flat_mesh= layout.row()
        obj=context.active_object
        if obj and obj.type == 'MESH' and obj.data.shape_keys and obj.data.shape_keys.key_blocks.get('uv_flat') and obj.data.shape_keys.key_blocks['uv_flat'].value > 0.99:
            flat_mesh.operator(flatten_uv.Create_flat_mesh.bl_idname, text="UV>Mesh")
        else:
            flat_mesh.operator(flatten_uv.Create_flat_mesh.bl_idname)
        #flat_mesh.operator(flatten_uv.Create_flat_mesh.bl_idname) 
        
        flat_mesh.operator(flatten_uv.Dupulicate_mesh_aply_key.bl_idname)
        obj_prop=context.object.cupcko_mesh_transfer_object 
        pickobj= layout.row()
        pickobj.prop_search(obj_prop,"mesh_shape_get_from_this",context.scene,"objects",text="目标")
        vertex_groups=layout.row(align=True)
        vertex_groups.prop_search(obj_prop,"vertex_group_filter",bpy.context.active_object,"vertex_groups")
        vertex_groups.prop(obj_prop,'invert_vertex_group_filter',text='',toggle=True,icon='ARROW_LEFTRIGHT')
        modifi=layout.row()
        modifi.prop(obj_prop,'transfer_modified_source',text='采样形变')
        search=layout.row(align=True)
        search.prop(obj_prop, 'search_method', expand=True, text="Search method")
        transferbox=layout.row()
        transfer_uv_row=transferbox.row()
        transfer_uv=transfer_uv_row.row()
        transfer_uv.operator(TransferUV.bl_idname)
        transfer_shape_row=transferbox.row()
        transfer_shape=transfer_shape_row.row(align=True)
        transfer_shape.operator(TransferShapeData.bl_idname)
        transfer_shape.prop(obj_prop,'transfer_shape_as_key',text='',toggle=True,icon='SHAPEKEY_DATA')
class VIEW3D_HT_Language(bpy.types.Header):
    # Panel
    bl_space_type = 'VIEW_3D'
    bl_region_type = "HEADER"
    bl_options = {'REGISTER','UNDO'}
    # bl_category = "Item"

    # @classmethod
    # def poll(cls, context):
    #     return (context.object is not None)

    bl_label = "Cupcko"
    
    def draw(self, context):
        if context.region.alignment != 'RIGHT':
            layout = self.layout
            language_switch=layout.row(align=True)
            if bpy.context.preferences.addons[__name__].preferences.luanguage_switch:
                language_switch.operator("cup.language_switch")
            row1=layout.row()
            if bpy.context.preferences.addons[__name__].preferences.mouse_deps_switch:
                if bpy.context.preferences.inputs.use_mouse_depth_navigate==True:
                    row1.operator("cup.depth_off")
                    
                else:
                    row1.operator("cup.depth_on")
            if bpy.context.preferences.addons[__name__].preferences.surface_paint_switch:    
                row1.operator("cup.annotate_surface")
            if bpy.context.preferences.addons[__name__].preferences.sculpt_rotate_switch:
                if bpy.context.preferences.inputs.view_rotate_method=='TRACKBALL':
                    row1.operator(Cupcko_rotate_method_switch.bl_idname,text='当前:轨迹球')
                else:
                    row1.operator(Cupcko_rotate_method_switch.bl_idname,text='当前:转盘')                         
def _language_switch():
    context_language=bpy.context.preferences.view.use_translate_interface
    view_l=bpy.context.preferences.view.language
    if view_l=='zh_CN' :
        if context_language:
            bpy.context.preferences.view.use_translate_interface=False
        elif context_language==False:
            bpy.context.preferences.view.use_translate_interface=True
    bpy.context.preferences.view.use_translate_new_dataname=False
def do_not_pick_oneself(self,object):
    if bpy.context.active_object==object:
        return False
    return object.type=='MESH'
class Meshdata_Settings(bpy.types.PropertyGroup):
    mesh_shape_get_from_this:bpy.props.PointerProperty(name="source mesh",description="采样此模型",type=bpy.types.Object,poll=do_not_pick_oneself)
    mesh_object_space:bpy.props.EnumProperty(
        items=[('WORLD_SPACE','World','',1),('LOCAL_SPACE','Local','',2),('UV_SPACE','active uv','',3),('TOPOLOGY_SPACE','Topology','',4)],
        name="Object Space",default='LOCAL_SPACE')
    search_method: bpy.props.EnumProperty(
        items=[('CLOSEST', 'Closest', '', 1),('RAYCAST', 'Raycast', '', 2)],
        name="Search method",default='CLOSEST')
    transfer_shape_as_key:bpy.props.BoolProperty(name='transfer as shape key',
                                                description="做成形态键")
    vertex_group_filter:bpy.props.StringProperty(name="Vertex Group",description="仅传递顶点组中的顶点")
    invert_vertex_group_filter:bpy.props.BoolProperty(name="Invert vertex group", description="反转顶点组")
    transfer_modified_source : bpy.props.BoolProperty ()
class Cupcko_rotate_center_switch(bpy.types.Operator):
    bl_idname = "cup.depth_on"
    bl_label = "鼠标深度"
    bl_options = {'REGISTER','UNDO'}
    @classmethod
    def poll(cls, context):
        if 1:
            return True
    def execute(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False 
        try:
            _rotate_center_on()
        finally:
            context.preferences.edit.use_global_undo = use_global_undo
            print(bpy.context.preferences.inputs.use_mouse_depth_navigate)
        return {'FINISHED'}
def _rotate_center_on():
    bpy.context.preferences.inputs.use_mouse_depth_navigate=True

class Cupcko_rotate_center_switch2(bpy.types.Operator):
    bl_idname = "cup.depth_off"
    bl_label = "取消深度"
    bl_options = {'REGISTER','UNDO'}
    @classmethod
    def poll(cls, context):
        if 1:
            return True
    def execute(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False 
        try:
            _rotate_center_off()
        finally:
            context.preferences.edit.use_global_undo = use_global_undo
            print(bpy.context.preferences.inputs.use_mouse_depth_navigate)
        return {'FINISHED'}
        
def _rotate_center_off():
    bpy.context.preferences.inputs.use_mouse_depth_navigate=False 
class Cupcko_annotate_surface(bpy.types.Operator):
    bl_idname = "cup.annotate_surface"
    bl_label = "表面绘制"
    bl_options = {'REGISTER','UNDO'}
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
        self.report({'INFO'},'画笔设置为表面绘制')
        return {'FINISHED'}       
def _annotate_surface():
    bpy.context.scene.tool_settings.annotation_stroke_placement_view3d = 'SURFACE'
def _rotate_method_switch():
    method=bpy.context.preferences.inputs.view_rotate_method
    if method=='TRACKBALL':
        bpy.context.preferences.inputs.view_rotate_method='TURNTABLE'
    elif method=='TURNTABLE':
        bpy.context.preferences.inputs.view_rotate_method='TRACKBALL'
class Cupcko_rotate_method_switch(bpy.types.Operator):
    bl_idname = "cup.rotate_method_switch"
    bl_label = "切换旋转"
    bl_options = {'REGISTER','UNDO'}
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
    bl_label = "中英切换"
    bl_options = {'REGISTER','UNDO'}
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

class Cupcko_exit_edit_shape(bpy.types.Operator):
    bl_idname="cup.exit_edit_shape"
    bl_label="应用形状"
    bl_options = {'REGISTER','UNDO'}
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
    bl_options = {'REGISTER','UNDO'}

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
    bl_options = {'REGISTER','UNDO'}

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
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(cls, context):
        # context.mode == 'OBJECT' 
        if bpy.context.object.type=='ARMATURE':
            return True

    def execute(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False
        
        try:
            
            cs_group_orgnize()
            

        finally:
            context.preferences.edit.use_global_undo = use_global_undo
        self.report({'INFO'},'整理完了,查看cs_group_orgnize')
        return {'FINISHED'}

def _edit_custom_shape():

    bone = bpy.context.active_pose_bone
    object_rig=bpy.context.active_object

    print('1+'+bpy.context.active_object.name)
    #确定物体是否有自定义骨骼,没有就新建,然后统一自定义骨骼名称
    if not bpy.context.active_pose_bone.custom_shape:
        bpy.ops.mesh.primitive_plane_add(size=2, calc_uvs=True, enter_editmode=False, align='WORLD', location=(0, 0, 0), rotation=(0, 0, 0), scale=(0, 0, 0))
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.delete(type='ONLY_FACE')
        bpy.ops.object.mode_set(mode='OBJECT')
        bone.custom_shape=bpy.context.active_object
    #如果不小心删掉了自定义骨骼
    try:    
        bpy.context.collection.objects.link(bone.custom_shape)
    
    except:
        pass
    
    mesh_custom_shape=bone.custom_shape
    

    mesh_custom_shape['object_rig']=object_rig.name
    bone_custom_shape_transform=bone.custom_shape_transform
    print('2+'+bpy.context.active_object.name)
    if bone_custom_shape_transform:
        
        print (object_rig.matrix_world)
        print (bone_custom_shape_transform.matrix)
        mesh_custom_shape.matrix_world=object_rig.matrix_world @ bone_custom_shape_transform.matrix
        #将物体模式的位移旋转缩放当成增量，进行矩阵乘法，得到最终骨骼所在位置角度，传给自定义骨骼
        #print (mesh_custom_shape.matrix_world)
        
    else:
        mesh_custom_shape.matrix_world=object_rig.matrix_world @ bone.matrix
    
    mesh_custom_shape.scale *= bone.custom_shape_scale_xyz
    mesh_custom_shape.scale *= bone.length
    print('3+'+bpy.context.active_object.name)
    bpy.ops.object.posemode_toggle()
    bpy.data.objects[object_rig.name].select_set(False)
    
    unhide_object(mesh_custom_shape)
    bpy.context.view_layer.objects.active=mesh_custom_shape
    bpy.data.objects[mesh_custom_shape.name].select_set(1)
    bpy.ops.object.make_single_user(object=True, obdata=True, material=False, animation=False, obdata_animation=False)
    mesh_custom_shape.name= '_cs_'+bone.name
    mesh_custom_shape.data.name= '_cs_'+bone.name
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
    #判断是否有自定义骨骼合集cs_group_master，若没有 创建一个
    bone_grp=bpy.context.object.pose.bones
    rig=bpy.context.active_object
    cs_group_master=None
    if not bpy.data.objects.get('custom_group_master'):
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        cs_group_master=bpy.context.active_object
        cs_group_master.name='custom_group_master'
        set_active_object(rig.name)
        bpy.ops.object.mode_set(mode='POSE')

    else:
        cs_group_master=bpy.data.objects['custom_group_master']
    set_active_object(rig.name)

    #hide_object(bpy.data.objects['custom_group_master'])
    for bone in bone_grp:
        if bone.custom_shape:
            bone.custom_shape.parent=bpy.data.objects['custom_group_master']
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
    #去掉所有面 完成后回到姿态模式
    cs_shape = bpy.context.active_object
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.delete(type='ONLY_FACE')
    bpy.ops.object.mode_set(mode='OBJECT')
   
    
    # object_rig=None
    object_rig_name=None
    for key in cs_shape.keys():
        if 'object_rig' in key:
            object_rig_name=cs_shape['object_rig']
            # object_rig=bpy.data.objects.get(object_rig_name)
    set_active_object(object_rig_name)
    bpy.ops.object.mode_set(mode='POSE')
    
    hide_object(cs_shape)
 
    
def get_bone_side(bone_name):
    mirror_char_in=['l.','L.','l_','L_','r_','R_','R.','r.','.l','_l','.L','_l','.r','.R','_R','_r']
    mirror_char_ot=['r.','R.','r_','R_','l_','L_','L.','l.','.r','_r','.R','_r','.l','.L','_L','_l']
    mirror_bone_name='None'
    for bone_side in mirror_char_in:
        #print('骨骼是左边还是右边='+bone_side)
    
        
        
        if bone_side in bone_name:
            n=bone_name.index(bone_side)
            length=len(bone_name)
            print('长度=',length)
            print('name序号=',n)
            i=mirror_char_in.index(bone_side)
            bone_side_mir=mirror_char_ot[i]
            print(bone_name[n:])
            
            # if n+2<length and n-1>0:

            if n==0:
            #名称前置型骨骼
                mirror_bone_name="".join((bone_side,bone_name))
                print('名称前置型骨骼='+mirror_bone_name)    

            if  n+2<length:
                if bone_name[n+2]=='.' or bone_name[n+2]=='_' or bone_name[n-1]=='.' or bone_name[n-1]=='_':
                
            #名称中间型骨骼
                    
                    
                    split=bone_name.split(bone_side)
                    mirror_bone_name="".join((split[0],bone_side_mir,split[1]))
                   # mirror_bone_name=split[0]+bone_side_mir+split[1]
                    print('名称中间型骨骼='+mirror_bone_name)
                    #return(mirror_bone_name)

            elif bone_side==bone_name[-2:]:
            #名称后置型骨骼
                mirror_bone_name="".join((bone_name[:-2],bone_side_mir))
                #mirror_bone_name=bone_name[:-2]+bone_side_mir
                print('名称后置型骨骼='+mirror_bone_name)
                print('bone_name='+bone_name[-2:])
                #return(mirror_bone_name)
    return(mirror_bone_name)            

def get_selected_pose_bones():
       return bpy.context.selected_pose_bones
def _mirror_custom_shape(self):
    cs_group_orgnize()
    #先拿到骨骼物体名字，存起来，用列表查找镜像骨存起来，再判断有没有镜像骨
    rig_name=bpy.context.active_object.name
    rig=bpy.data.objects[rig_name]
    #selected_bone=get_selected_pose_bones()[0]

    for bone in get_selected_pose_bones():
        bone_name=bone.name
        try:
            bone.custom_shape.name='_cs_'+bone_name
            bone.custom_shape.data.name='_cs_'+bone_name
        except:
            pass
        split=[]
        mirror_bone_name=''
        mirror_cs_obj=None
        mirror_bone_name=get_bone_side(bone.name)

        if mirror_bone_name=='None':
            self.report({'INFO'},'无法镜像,你镜像个锤子')
           # print('选中骨骼无左右标识符,先加上.l或者.r后缀')
        else:
            mirror_bone= rig.pose.bones.get(mirror_bone_name)
            
          #  print('骨骼='+mirror_bone_name)
            #选中骨骼无自定义骨骼形状
            if  not bone.custom_shape:
                print('选中骨骼无自定义骨骼形状,先给自身创建一个,点击编辑')
            else:    
                if mirror_bone.custom_shape:
        #有自定义骨骼
                    if not mirror_bone.custom_shape.name=='_cs_'+mirror_bone_name:
                        #自定义骨骼名字不对
                        mirror_cs_obj=mirror_bone.custom_shape
                        mirror_cs_obj.name='_cs_'+mirror_bone_name
                        # mirror_cs_obj.data=bone.custom_shape.data.copy()
                        # mirror_cs_obj.data.name='_cs_'+mirror_bone_name
                       # print('自定义骨骼名字不对,已自动更改为_cs_+骨骼名')
                    else:
                        #自定义骨骼名字正确
                      #  print('自定义骨骼名字正确')
                        mirror_cs_obj=mirror_bone.custom_shape

                else:
        #没有自定义骨骼
                   # print('没有自定义骨骼,已自动补全')
                    bpy.ops.object.mode_set(mode='OBJECT')
                    bpy.ops.mesh.primitive_plane_add(size=2, calc_uvs=True, enter_editmode=False, align='WORLD', location=(0, 0, 0), rotation=(0, 0, 0), scale=(0, 0, 0))
                    mirror_bone.custom_shape=bpy.context.active_object
                    mirror_cs_obj=mirror_bone.custom_shape
                    mirror_cs_obj.name='_cs_'+mirror_bone_name
                mirror_cs_obj.data=bone.custom_shape.data.copy()
                mirror_cs_obj.data.name='_cs_'+mirror_bone_name
                unhide_object(mirror_cs_obj)
                
                bpy.ops.object.mode_set(mode='OBJECT')
                
                set_active_object(mirror_cs_obj.name)
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
                mirror_bone.custom_shape_scale_xyz=(1,1,1)

                bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
        # else:
        #     print('选中骨骼无左右标识符,先加上.l或者.r后缀')
class Cupcko_shape_keys_driver(bpy.types.Panel):
    # Panel
    # bl_space_type = 'VIEW_3D'
    # bl_region_type = "HEADER"
    # bl_options = {'REGISTER','UNDO'}
    # bl_category = "Item"

    # @classmethod
    # def poll(cls, context):
    #     return (context.object is not None)
    bl_label = "Shape Keys"
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'}
    
    def draw(self, context):
        layout = self.layout
        add_lab=layout.row()
        add_lab.operator(cupcko_camera_driver.Camera_Driver.bl_idname)
        
from . import cupcko_node_add 
classes=(
    SNA_OT_Hide_Empty,
    cupcko_node_add.Cupcko_add_NdotL,
    flatten_uv.Create_flat_mesh,
    Cupcko_Panel,
    Cupcko_edit_custom_shape,
    Cupcko_mirror_custom_shape,
    Cupcko_exit_edit_shape,
    Cupcko_cs_group_orgnize,
 #   VIEW3D_PT_Language,
    Cupcko_Language_switch,
    Cupcko_rotate_center_switch,
    Cupcko_rotate_center_switch2,
    Cupcko_annotate_surface,
    Cupcko_rotate_method_switch,
    flatten_uv.Dupulicate_mesh_aply_key,
    Cupcko_return_selected_obj,
    Meshdata_Settings,
    TransferUV,
    TransferShapeData,
    #OBJECT_OT_addon_prefs_example,
    ExampleAddonPreferences,
    cupcko_camera_driver.Camera_Driver,
    
)

def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)	
    bpy.types.TOPBAR_HT_upper_bar.append(VIEW3D_HT_Language.draw)
    bpy.types.DATA_PT_shape_keys.append(Cupcko_shape_keys_driver.draw)
    
    bpy.types.Object.cupcko_mesh_transfer_object=PointerProperty(type=Meshdata_Settings)
    
def unregister():

    from bpy.utils import unregister_class
    for c in reversed(classes):
        unregister_class(c)
    bpy.types.TOPBAR_HT_upper_bar.remove(VIEW3D_HT_Language.draw)  
    bpy.types.DATA_PT_shape_keys.remove(Cupcko_shape_keys_driver.draw)
    del bpy.types.Object.cupcko_mesh_transfer_object
  
if __name__ == "__main__":
	register()
