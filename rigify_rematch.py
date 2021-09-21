import bpy
def _rematch():
    first=bpy.context.active_object
    second=bpy.data.objects['metarig']
 
    print(first.name)
    print(second.name)
   # bpy.ops.object.editmode_toggle()

    for bone in first.data.edit_bones[:]:

        for bone2 in second.data.edit_bones[:]:
            if bone.name==bone2.name:
                bone.head=bone2.head 
                bone.tail=bone2.tail
                bone.roll=bone2.roll
_rematch()