import bpy
import re
namespace=''
for a in bpy.context.object.data.bones:
    # print(a.name)
    if re.search(r'rigref', a.name, re.I | re.M):
        searchObj1 = re.search(r'(.*)rigref(.*)', a.name, re.I | re.M).group(1)
        searchObj2 = re.search(r'rigref', a.name, re.I | re.M).group()
        namespace = searchObj1 + searchObj2
        print(namespace)
        break
for i in bpy.context.object.data.bones:
    if re.search(namespace, i.name, re.I | re.M) and '_L_' in i.name:
        # re.search(namespace, i.name, re.I | re.M):
        i.name = re.search(f'(.*){namespace}_L(.*)', i.name, re.I | re.M).group(1) + re.search(f'(.*){namespace}_L(.*)',
                                                                                               i.name,
                                                                                               re.I | re.M).group(
            2)+'.l'
        print(i.name)
    elif re.search(namespace, i.name, re.I | re.M) and '_R_' in i.name:
        # re.search(namespace, i.name, re.I | re.M):
        i.name = re.search(f'(.*){namespace}_R(.*)', i.name, re.I | re.M).group(1) + re.search(f'(.*){namespace}_R(.*)',
                                                                                               i.name,
                                                                                               re.I | re.M).group(
            2)+'.r'
    elif re.search(namespace, i.name, re.I | re.M):
        i.name = re.search(f'(.*){namespace}(.*)', i.name, re.I | re.M).group(1) + re.search(f'(.*){namespace}(.*)',
                                                                                             i.name, re.I | re.M).group(
            2)
# for a in bpy.context.scene.objects:
#     if len(a.modifiers) > 0 and a.modifiers[0].type == 'ARMATURE':
#         a.modifiers[0].object = bpy.data.objects['gameRig_RIG-Armature']


