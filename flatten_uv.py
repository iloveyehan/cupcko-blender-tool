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
        return context.active_object and context.active_object.type == 'MESH' and len(context.active_object.data.uv_layers) > 0 and bpy.context.mode=="OBJECT"
    def execute(self,context):
        #obj=context.active_object
        me=bpy.context.object
        bm=bmesh.new()
        bm.from_mesh(me.data)
        # active_uv=bm.loops.layers.uv.active 
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
                create_flat_mesh(bm)

                bm.to_mesh(me.data)
                shapekey=me.data.shape_keys.key_blocks.get("uv_flat")
                shapekey.value = 1 
                print("uv flat key,try to create")
                
                    
        except:
            #pass
            a=time.time()           
        
           
            create_flat_mesh(bm)

            bm.to_mesh(me.data)
            print((time.time()-a),'s') 
            shapekey=me.data.shape_keys.key_blocks.get("uv_flat")
            shapekey.value = 1
            #me=bpy.context.object
            #bm=bmesh.new()
            #bm.from_mesh(me.data) 
            #dupulicate_mesh_apply_key() 
        bm.free()   
        return {"FINISHED"}          
def create_flat_mesh(bm):
    new_flatten_uv=bm.verts.layers.shape.get("uv_flat")
    me=bpy.context.object
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
        return context.active_object and context.active_object.type == 'MESH' and context.active_object.data.shape_keys and bpy.context.mode=="OBJECT"
    def execute(self,context):
        #obj=context.active_object
        me=bpy.context.object
      #  bm=bmesh.new()
      #  bm.from_mesh(me.data) 
        dupulicate_mesh_apply_key()
        return {"FINISHED"}  
def dupulicate_mesh_apply_key():
    name=bpy.context.active_object.name
    #如果是已经复制过后的对象,就不再重复复制
    if ".00" not in name:
        bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "orient_type":'GLOBAL', "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":True, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})
        bpy.data.objects[name].hide=True
        me=bpy.context.object
        shapekey=me.data.shape_keys.key_blocks.get("uv_flat")
    #将平面uv移到最顶上,保证应用的是它
        shapekey.value = 1
        index=me.data.shape_keys.key_blocks[:].index(shapekey)
        bpy.context.object.active_shape_key_index = index
        print("key index=",index)
        if index!=1:    
            bpy.ops.object.shape_key_move(type='TOP')
        Basis=me.data.shape_keys.key_blocks.get("Basis")
        me.shape_key_remove(Basis)
        bpy.ops.object.shape_key_remove(all=True)
    
    if ".00" in name:
        me=bpy.context.object
        if me.data.shape_keys:
            shapekey=me.data.shape_keys.key_blocks.get("uv_flat")
            if shapekey:
                shapekey.value = 1
            Basis=me.data.shape_keys.key_blocks.get("Basis")
            index=me.data.shape_keys.key_blocks[:].index(shapekey)
            bpy.context.object.active_shape_key_index = index
            print("key index2=",index)
            if index!=1:  
                bpy.ops.object.shape_key_move(type='TOP')
            me.shape_key_remove(Basis)
            
            try:

                bpy.ops.object.shape_key_remove(all=True)
            except:
                pass    
        else:
            print("do not click twice")
def test():
    me=bpy.context.object
    bm=bmesh.new()
    bm.from_mesh(me.data)
    #dupulicate_mesh_aply_key(bm)
    for f in bm.faces:
        lp=f.loops.link_loops[:]
        for l in lp:    
            print(l)
