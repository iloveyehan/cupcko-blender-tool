import bpy

from .cupcko_operators import determine_and_convert
class SyncActiveBoneNameOperator(bpy.types.Operator):
    """同步两个Armature的Active Bone名称"""
    bl_idname = "cupcko.sync_active_bone_name"
    bl_label = "同步Active Bone名称"
    bl_options = {'REGISTER', 'UNDO'}
    mirror: bpy.props.BoolProperty(
        name="镜像处理",
        description="对选中骨骼的对称骨骼执行相同操作",
        default=True
    )
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'ARMATURE'
    def execute(self, context):
        # 获取当前选中的两个Armature对象
        armatures = [obj for obj in context.selected_objects if obj.type == 'ARMATURE']
        armature = context.active_object
        active_bone = context.active_bone
        # 获取镜像骨骼名称
        mirror_active_name = determine_and_convert(active_bone.name)[2]
        # mirror_active_bone = None
        # if self.mirror and mirror_active_name:
        #     mirror_active_bone = armature.data.bones.get(mirror_active_name)

            
        if len(armatures) != 2:
            self.report({'ERROR'}, "请确保选中了两个Armature对象")
            return {'CANCELLED'}
        ac_bone_name=bpy.context.active_pose_bone.name
        for a in armatures:
            if a==bpy.context.active_object:
                continue
            mirror_name = determine_and_convert(a.data.bones.active.name)[2]
            print('mirror_name',mirror_name,'mirror_active_name',mirror_active_name)
            if self.mirror:
                print('mirror mirror_name',mirror_name,'mirror_active_name',mirror_active_name)
                mirror_bone = a.data.bones.get(mirror_name)
                print(mirror_bone)
                if mirror_bone is not None:
                    mirror_bone.name=mirror_active_name
                    
            a.data.bones.active.name=ac_bone_name
        
        self.report({'INFO'}, f"已将第二个Armature的Active Bone名字改为: {ac_bone_name}")
        return {'FINISHED'}