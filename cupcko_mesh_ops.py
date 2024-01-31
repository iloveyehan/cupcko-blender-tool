import bpy
import bmesh
from mathutils import Vector

# 确定当前对象，确保它是一个网格
obj = bpy.context.object
if obj.type != 'MESH':
    print("Selected object is not a mesh.")
else:
    # 获取网格数据
    mesh = obj.data

    # 准备字典来存储映射关系
    pos_to_neg_index = {}  # 正 x 的顶点 index 映射到负 x 的顶点 index

    # 遍历所有顶点，构建映射关系
    for vert in mesh.vertices:
        x, y, z = vert.co.x, vert.co.y, vert.co.z
        tolerance = 1e-6
        if x > tolerance:
            # 寻找对应的负 x 顶点
            for other_vert in mesh.vertices:
                # if other_vert.co.x == -x and other_vert.co.y == y and other_vert.co.z == z:

                if abs(other_vert.co.x + x) < tolerance and abs(other_vert.co.y - y) < tolerance and abs(
                        other_vert.co.z - z) < tolerance:
                    # 顶点匹配

                    # 找到映射，记录正 x 到负 x 的索引映射
                    # pos_to_neg_index[vert.index] = other_vert.index
                    pos_to_neg_index[other_vert.index] = vert.index
                    break  # 找到对应顶点后停止该轮循环

    # 用负 x 的顶点 index 获取正 x 的顶点 index
    for pos_idx, neg_idx in pos_to_neg_index.items():
        print("Positive Vertex Index:", pos_idx, "has a corresponding Negative Vertex Index:", neg_idx)
        # 在这里可以根据需要进行其他操作

    # 更新网格以反映变更
    mesh.update()
    #            corresponding_vert.co=Vector((-vert.co.x,vert.co.y,vert.co.z))

    depsgraph = bpy.context.evaluated_depsgraph_get()
    # 更新依赖图
    obj_eval = obj.evaluated_get(depsgraph)
    mesh = obj_eval.to_mesh()
    sk = obj.data.shape_keys.key_blocks['eye_まばたき'].data
    for v in mesh.vertices:
        if v.co.x < 0:
            try:
                p_index = pos_to_neg_index[v.index]
            except:

                continue
            sk[v.index].co = mesh.vertices[p_index].co
            sk[v.index].co.x = -sk[v.index].co.x

    obj_eval.to_mesh_clear()
