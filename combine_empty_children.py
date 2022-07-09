import bpy


def set_active_object(object_name):
    bpy.context.view_layer.objects.active = bpy.data.objects[object_name]
    bpy.data.objects[object_name].select_set(state=True)


parent_list = []
index = 0
for x in bpy.context.scene.objects:
    if x.parent:
        if x.parent.type == 'EMPTY':
            if x.type == 'MESH':
                if not x.parent.name in parent_list:
                    parent_list.append(x.parent.name)
for a in parent_list:
    bpy.ops.object.select_all(action='DESELECT')
    a_children = bpy.data.objects[a].children
    for child in a_children:

        if child.type == 'MESH':
            index = a_children.index(child)
            set_active_object(bpy.data.objects[a].children[index].name)
            print(child.name)
    try:
        bpy.ops.object.join()
    except:
        pass
