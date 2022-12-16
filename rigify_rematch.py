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

bpy.ops.object.mode_set(mode='EDIT')
for  a in bpy.context.selectable_objects:
    if a==bpy.context.view_layer.objects.active:
        active=a
        continue
        obj=a
for b in a.data.edit_bones:
    for obj_b in obj.data.edit_bones:
        if b.name==obj_b.name:
            obj_b.head=b.head
            obj_b.tail=b.head
            obj_b.roll=b.roll
