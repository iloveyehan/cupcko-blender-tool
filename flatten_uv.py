from bmesh.types import BMEditSelSeq
import bpy
import bmesh
from mathutils import Vector
import time
# from numpy.core.fromnumeric import shape
# from numpy.lib.function_base import append
#bpy.ops.object.editmode_toggle()
class Create_flat_mesh(bpy.types.Operator):
    bl_idname = "cup.create_flat_mesh"
    bl_label = "Mesh>UV"
    bl_options = {'REGISTER','UNDO'}
    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'MESH' and len(context.active_object.data.uv_layers) > 0 and bpy.context.mode=="OBJECT"              and bpy.context.object.hide_set(0)
    def execute(self,context):
        #obj=context.active_object
      
        
        # active_uv=bm.loops.layers.uv.active 
        if len(bpy.context.selected_objects)>=1:
                for obj in bpy.context.selected_objects:
                    
                    if obj.type=='MESH':
                        me=obj
                        bm=bmesh.new()
                        bm.from_mesh(me.data)
                        try:
                            print("try")
                            shapekey=me.data.shape_keys.key_blocks.get("uv_flat")
                            if shapekey:
                                print("uv flat key")  
                                if shapekey.value==1:

                                    shapekey.value = 0
                                else:
                                    shapekey.value=1
                            #print("no uv flat key in pannel")

                            if not shapekey:
                                
                                create_flat_mesh(bm,obj)

                                bm.to_mesh(me.data)
                                
                                shapekey=me.data.shape_keys.key_blocks.get("uv_flat")
                                shapekey.value = 1 
                                print("uv flat key,try to create")
                                
                                    
                        except:
                            #pass
                            a=time.time()           
                            

                            create_flat_mesh(bm,obj)

                            bm.to_mesh(me.data)
                            bm.free()
                            print((time.time()-a),'s') 
                            shapekey=me.data.shape_keys.key_blocks.get("uv_flat")
                            shapekey.value = 1
                            #me=bpy.context.object
                            #bm=bmesh.new()
                            #bm.from_mesh(me.data) 
                            #dupulicate_mesh_apply_key() 
                        bm.free()  
        return {"FINISHED"}          
def create_flat_mesh(bm,obj):
    new_flatten_uv=bm.verts.layers.shape.get("uv_flat")
    me=obj
    if not me.data.shape_keys:
        print("no shape_key")
        me.shape_key_add(name="Basis") 
        print("create basis")
    if not new_flatten_uv:
        print("no new_flatten_uv")
        new_flatten_uv=bm.verts.layers.shape.new("uv_flat")
        print("create flat uv shape key")
    seam_edges=get_Seam_edges(bm)
    if seam_edges:
        bmesh.ops.split_edges(bm,edges=seam_edges)
    active_uv=bm.loops.layers.uv.active
    bm.verts.ensure_lookup_table()
    scale=me.scale[0] 
    for vert in bm.verts:
        #if vert.link_loops:
        location=vert.link_loops[0][active_uv].uv
        vert[new_flatten_uv]=Vector((3*location[0]/scale,3*location[1]/scale,0))
    

    #shapekey.value=1
def get_Seam_edges(bm):
    seam_edges=[]
    active_uv=bm.loops.layers.uv.active 
    for edge in bm.edges:
        if len(edge.link_faces)==2:
            uv_point=edge.link_loops[0]             
            uv_point2=edge.link_loops[1]
            if uv_point2[active_uv].uv!= uv_point.link_loop_next[active_uv].uv or uv_point[active_uv].uv!= uv_point2.link_loop_next[active_uv].uv:   
                seam_edges.append(edge)
    return seam_edges            
class Dupulicate_mesh_aply_key(bpy.types.Operator):
    bl_idname = "cup.dupulicate_mesh_aply_key"
    bl_label = "应用"
    bl_options = {'REGISTER','UNDO'}
    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'MESH' and context.active_object.data.shape_keys and bpy.context.mode=="OBJECT" \
     
    def execute(self,context):
        a=bpy.context.selected_objects
        if len(a)>=1:
            
            for obj in a:
                if obj.type=='MESH':
                    dupulicate_mesh_apply_key(obj)
        return {"FINISHED"}  
def dupulicate_mesh_apply_key(obj):
    if obj.data.shape_keys.key_blocks['uv_flat']:
        set_active_object(obj.name)
        bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
        temp_obj=bpy.context.object
        shapekey=temp_obj.data.shape_keys.key_blocks.get("uv_flat")
        #将平面uv移到最顶上,保证应用的是它
        shapekey.value = 1
        index=temp_obj.data.shape_keys.key_blocks[:].index(shapekey)
        temp_obj.active_shape_key_index = index
        print("key index=",index)
        if index!=1:    
            bpy.ops.object.shape_key_move(type='TOP')
        Basis=temp_obj.data.shape_keys.key_blocks.get("Basis")
        temp_obj.shape_key_remove(Basis)
        bpy.ops.object.shape_key_remove(all=True)

        temp_obj.name='{}_001'.format(obj.name)
        temp_obj.data.name='{}_001'.format(obj.name)
        bpy.data.objects[obj.name].hide_set(1)


def set_active_object(object_name):
    bpy.ops.object.select_all(action='DESELECT')

    bpy.context.view_layer.objects.active = bpy.data.objects[object_name]
    bpy.data.objects[object_name].select_set(state=True)    
def test():
    me=bpy.context.object
    bm=bmesh.new()
    bm.from_mesh(me.data)
    #dupulicate_mesh_aply_key(bm)
    for f in bm.faces:
        lp=f.loops.link_loops[:]
        for l in lp:    
            print(l)
