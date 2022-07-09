'''选中animationRig再运行'''

import bpy
import re
# for a in bpy.context.scene.objects:
#     print(a.name)
#     if re.search(r'rigref', a.name, re.I | re.M):
#         searchObj1 = re.search(r'(.*)rigref(.*)', a.name, re.I | re.M).group(1)
#         searchObj2 = re.search(r'rigref', a.name, re.I | re.M).group()
#         namespace = searchObj1 + searchObj2
#         print(namespace)
#         break
namespace=''
dict1 = {
    '_M_neckTop':['_M_head',],
    '_M_neckRoot': [ ],
    '_M_chest': ['_shoulder.l', '_shoulder.r','_capBRoot.l', '_capFRoot.l', '_capBRoot.r', '_capFRoot.r', '_M_capFRoot', '_M_capBRoot', ],
    '_shoulder.l': ['_armRoot.l'],
    '_shoulder.r': ['_armRoot.r'],
    '_elbow.l': ['_elbowAUX.l'],
    '_elbow.r': ['_elbowAUX.r'],
    '_hand.l': ['_handTip.l', '_handThumb.l'],
    '_hand.r': ['_handTip.r', '_handThumb.r'],
    '_M_hip': ['_legRoot.l', '_legRoot.r'],
    '_legRoot.l':['_legAUX.l'],
    '_legRoot.r':['_legAUX.r'],
    '_knee.l': ['_kneeAUX.l'],
    '_knee.r': ['_kneeAUX.r'],
}
parentDict=dict1

bpy.ops.object.mode_set(mode='OBJECT')
if ('gameRig_' + bpy.context.object.name) not in bpy.context.scene.objects:

    if bpy.context.object.type == 'ARMATURE':
        aniRigBone = bpy.context.object

        gameRigBone = bpy.data.objects.new('gameRig_' + bpy.context.object.name,
                                           bpy.data.armatures[bpy.context.object.name].copy())
        gameRigBone.name = 'gameRig_' + aniRigBone.name
        bpy.context.scene.collection.objects.link(gameRigBone)
    deformBoneLst = []
    nodeformBoneLst = []
    bpy.ops.object.select_all(action='DESELECT')
    gameRigBone.select_set(1)
    bpy.context.view_layer.objects.active = gameRigBone
    gameRigBone.animation_data_clear()
    gameRigBone.data.layers = (
        True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True,
        True, True, True, True, True, True, True, True, True, True, True, True, True, True)
    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.reveal()
    for b in gameRigBone.pose.bones:
        if b.name == 'root':
            b.bone.use_deform = 1
            deformBoneLst.append(b.name)
            continue
        if b.bone.use_deform == True:
            deformBoneLst.append(b.name)
        else:
            nodeformBoneLst.append(b.name)
    print(deformBoneLst)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.armature.select_all(action='DESELECT')
    for b in nodeformBoneLst:
        gameRigBone.data.edit_bones.remove(gameRigBone.data.edit_bones[b])

    for b in gameRigBone.data.edit_bones:
        for a in parentDict:
            for c in parentDict[a]:
                gameRigBone.data.edit_bones[namespace+c].parent=gameRigBone.data.edit_bones[namespace+a]
    bpy.ops.object.mode_set(mode='POSE')
    for b in gameRigBone.pose.bones:
        constraint = b.constraints.new(type='COPY_TRANSFORMS')
        constraint.target = aniRigBone
        constraint.subtarget = aniRigBone.pose.bones[b.name].name
    bpy.ops.object.mode_set(mode='OBJECT')