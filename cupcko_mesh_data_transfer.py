import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import numpy as np
import mathutils


# from numpy.core.defchararray import count
# from numpy.core.records import array


class MeshData:
    def __init__(self, obj, deformed=False, world_space=False, uv_space=False, triangulate=True, symmetry_axis=None):
        self.obj = obj
        self.mesh = obj.data
        self.deformed = deformed
        self.world_space = world_space
        self.uv_space = uv_space
        self.symmetry_axis=symmetry_axis
        self.triangulate = triangulate
        self.bvhtree = None  # bvhtree for point casting
        self.kdtree = None
        self.transfer_bmesh = None  # 用做临时mesh,适时释放内存

        self.vertex_map = {}
        # uv_vertices到mesh vert id的对应映射

    # def free(self):
    # shapekey方法返回传入物体的shapekey属性块
    @property
    def shape_keys(self):
        if self.mesh.shape_keys:
            return self.mesh.shape_keys.key_blocks
            # vertex_groups返回传入物体的顶点组属性

    @property
    def vertex_groups(self):
        return self.obj.vertex_groups

    # vertex|_count方法返回顶点数量
    @property
    def vertex_count(self):
        return len(self.mesh.vertices)

    def get_locked_vertex_groups_array(self):
        # 返回顶点组的反转锁定列表
        locked_groups = self.obj.vertex_groups
        if not locked_groups:
            return
        array = []
        for g in locked_groups:
            array.append(not g.lock_weight)

        return array

    def free_memory(self):
        if self.transfer_bmesh:
            self.transfer_bmesh.free()
            # 释放内存
        if self.bvhtree:
            self.bvhtree = None
        if self.kdtree:
            self.kdtree = None

    def get_vertex_groups_name(self, ignore_locked=False):
        # 方法返回顶点组名
        if not self.vertex_groups:
            return
        # list类实例化,若无传入参数,返回一个空列表
        group_names = list()
        for group in self.vertex_groups:
            group_names.append(group.name)
        if ignore_locked:
            # 过滤的顶点组
            filter_array = self.get_locked_vertex_groups_array()
            for i in range(len(filter_array)):
                if not filter_array[i]:
                    # 删除该项
                    group_names.pop(i)
        return group_names

    @property
    def shape_key_drivers(self):
        return self.mesh.shape_keys.animation_data.drivers

    @property
    def shape_key_names(self):
        if self.shape_keys:
            return [i.name for i in self.shape_keys]

    def get_vertex_group_weights(self, vertex_group_name):
        '''返回顶点组中顶点的权重 列表类型,一维数组'''
        v_groups = self.vertex_groups
        v_group = None
        for group in v_groups:
            if group.name == vertex_group_name:
                v_group = group.index
        if v_group is None:
            return
        v_count = len(self.mesh.vertices)
        weights = np.zeros(v_count, dtype=np.float32)
        for v in self.mesh.vertices:
            groups = v.groups
            # 遍历顶点
            # 拿到每个顶点所在的顶点组
            # 在所有顶点组中 寻找目标顶点组
            for group in groups:
                # group.group==group的index
                i = group.group
                if i == v_group:
                    # 找到目标顶点组时,存储
                    v_index = v.index
                    # 顶点的索引
                    weight = group.weight
                    weights[v_index] = weight
                    # 存储顶点权重
        weights.shape = (v_count, 1)
        return weights

    def get_vertex_groups_weights(self, ignore_locked=False):
        '''取得所有顶点组的权重

        先存储顶点组,顶点数量
        初始化权重
        遍历顶点,读取每个组对应的顶点权重'''
        v_groups = self.vertex_groups
        if not v_groups:
            return
        v_count = len(self.mesh.vertices)
        v_groups_count = len(v_groups)
        weights = np.zeros((v_count * v_groups_count), dtype=np.float32)
        weights.shape = (v_groups_count, v_count)
        for v in self.mesh.vertices:
            groups = v.groups
            for group in groups:
                group_index = group.group
                v_index = v.index
                weight = group.weight
                weights[group_index, v_index] = weight
        if ignore_locked:
            array = self.get_locked_vertex_groups_array()  # 获取非 锁定的顶点组
            return weights[array]
        return weights

    def set_vertex_groups_weights(self, weights, group_names):
        # 清除所有大小为0的权重
        for i in range(weights.shape[0]):
            # remove existing vertex group
            group_name = group_names[i]
            v_group = self.vertex_groups.get(group_name)
            if v_group:
                self.vertex_groups.remove(v_group)
            group_weights = weights[i]
            # 取得第一组顶点组的所有顶点权重
            v_ids = np.nonzero(group_weights)[0]
            # 拿到第一组顶点组的所有顶点权重的非0权重的索引
            v_group = self.obj.vertex_groups.new(name=group_name)
            # 实现 一个 清除顶点组内0权重的顶点  方法
            for v_id in v_ids:
                value = group_weights[v_id]
                # 取得 每个顶点的权重
                v_group.add(int(v_id), value, "REPLACE")
                # add()
                # VertexGroup.add(index, weight, type)  type: SUBTRACT ADD REPLACE
                # Add vertices to the group

    def store_shape_keys_value(self):
        if self.shape_keys is None:
            print('no shapekey')
            return
        values = []
        for sk in self.shape_keys:
            values.append(sk.value)
        return values

    def store_shape_keys_name_value(self):
        if self.shape_keys is None:
            print('no shapekey')
            return
        values = {}
        for sk in self.shape_keys:
            values[sk.name] = sk.value
        return values

    def set_shape_keys_values(self, values):
        for i in range(len(values)):
            self.shape_keys[i].value = values[i]

    def reset_shape_keys_values(self):
        for sk in self.shape_keys:
            if sk.name != "Basis":
                sk.value = 0

    def set_verts_position(self, co):
        self.mesh.vertices.foreach_set("co", co.ravel())
        self.mesh.update()

    def set_position_as_shape_key(self, shape_key_name="Data_transfer", co=None, activate=False, value=0):
        '''传入形态键名字,形变顶点组,value'''
        # 先判断是否有形态键
        if not self.shape_keys:
            self.obj.shape_key_add(name="Basis")

        # 新建接收形变的形态键
        sk = self.obj.shape_key_add(name=shape_key_name)

        # 传入新形态键的顶点数据
        sk.data.foreach_set("co", co.ravel())  # 传入(属性,序列)
        # 检测初始状态
        sk.value = value
        if activate:
            sk.value = 1

    def generate_bmesh(self, deformed=True, world_space=True):
        '''获取物体的bmesh
        如果采集修改器,返回应用修改器后的bmesh'''
        if self.symmetry_axis is None:
            bm = bmesh.new()
            # 读取初始化状态
            if deformed:
                depsgraph = bpy.context.evaluated_depsgraph_get()
                # 更新依赖图
                obj_eval = self.obj.evaluated_get(depsgraph)
                mesh = obj_eval.to_mesh()
                # 获取修改器啥的数据
                bm.from_mesh(mesh)
                obj_eval.to_mesh_clear()
            else:
                mesh = self.obj.to_mesh()
                bm.from_mesh(mesh)
            if world_space:
                print(world_space)
                bm.transform(self.obj.matrix_world)
            bm.verts.ensure_lookup_table()
            return bm
        else:
            mesh = None
            # 读取初始化状态
            if deformed:
                depsgraph = bpy.context.evaluated_depsgraph_get()
                # 更新依赖图
                obj_eval = self.obj.evaluated_get(depsgraph)
                mesh = obj_eval.to_mesh()
                # 获取修改器啥的数据
                # obj_eval.to_mesh_clear()
            else:
                mesh = self.obj.to_mesh()
            # if world_space:
            # print(world_space)
            # bm.transform(self.obj.matrix_world)

            return mesh

    def get_mesh_data(self):
        """用网格的三角形版本构建BVHTree  
        参数变形:将采样变形的网格。  
        参数位移:将在世界空间中采样网格。  
        参数uv_space:将在UVspace中采样网格,并返回平面网格,包含面循环uv的顶点id map
        返回vertex_map属性:顶点id列表
        返回transformmesh属性:uv采样就返回uv平面网格,否则返回bmtransformmesh属性
        构建bvhtree"""
        if self.symmetry_axis is None:
            # 读取初始化参数
            bm = self.generate_bmesh(self.deformed, self.world_space)

            if self.uv_space:
                self.vertex_map = {}
                uv_layer_name = self.mesh.uv_layers.active.name
                uv_id = 0
                for i, uv in enumerate(self.mesh.uv_layers):
                    # enumerate:传入一个列表,返回索引+列表
                    if uv.name == uv_layer_name:
                        uv_id = i
                # 获取bm的uv
                uv_layer = bm.loops.layers.uv[uv_id]
                bm.faces.ensure_lookup_table()
                count_faces = len(bm.faces)
                vert_coord_list = []
                face_per_vert_idlist = []
                for faceid in range(count_faces):
                    # faceid为面索引
                    face_per_vert_id = []
                    for id, vert in enumerate(bm.faces[faceid].verts):
                        vert_id = len(vert_coord_list)
                        # list初始为0,刚好对应初始id=0
                        uv_coord_temp = bm.faces[faceid].loops[id][uv_layer].uv
                        # 获取这个面的顶点的uv坐标
                        verts_coord_temp = Vector((uv_coord_temp.x, uv_coord_temp.y, 0.0))
                        vert_coord_list.append(verts_coord_temp)
                        # 总体不断增加
                        if vert_id not in self.vertex_map.keys():
                            self.vertex_map[vert_id] = vert.index
                            # 将顶点索引存入自定义索引里面,这两个索引不相同
                            # 自定义索引是每个面都有数个顶点  所以一定比顶点索引多
                        # else:
                        #     if vert.index not in self.vertex_map[vert_id]:
                        #        #同一个顶点,但是不是同一个面循环
                        #        # 所以会出现同一个顶点,但是id不同的情况
                        #         self.vertex_map[vert_id].append(vert.index)

                        face_per_vert_id.append(vert_id)
                    face_per_vert_idlist.append(face_per_vert_id)
                mesh_temp = bpy.data.meshes.new(name="temp_mesh")
                # 新建临时平面 用来传递信息  包含顶点坐标和顶点id
                mesh_temp.from_pydata(vert_coord_list, [], face_per_vert_idlist)
                # 面都是分开的,有很多重叠点  几乎每个点都会有3个重复 除了边界
                self.transfer_bmesh = bmesh.new()
                self.transfer_bmesh.from_mesh(mesh_temp)
                bpy.data.meshes.remove(mesh_temp)

            else:
                for v in bm.verts:
                    self.vertex_map[v.index] = v.index
                    self.transfer_bmesh = bm
            if self.triangulate:
                bmesh.ops.triangulate(self.transfer_bmesh, faces=self.transfer_bmesh.faces)
                # 构建bvhtree
            # 用于几何体上的邻近搜索和光线投射的 BVH 树结构
            self.bvhtree = BVHTree.FromBMesh(self.transfer_bmesh)
        else:
            # 读取初始化参数
            mesh = self.generate_bmesh(self.deformed, self.world_space)
            size = len(mesh.vertices)
            kd = mathutils.kdtree.KDTree(size)

            for i, v in enumerate(mesh.vertices):
                kd.insert(v.co, i)

            kd.balance()
            self.kdtree = kd

    def get_shape_keys_vert_pos(self, exclude_muted=False):
        if not self.shape_keys:
            return
        # if self.deformed:
        #     pass
        stored_values = self.store_shape_keys_value()
        self.reset_shape_keys_values()
        shape_arrays = {}
        basis = ['Basis', 'basis', '基型']
        temp_show_only_shape_key = self.obj.show_only_shape_key
        if temp_show_only_shape_key:
            self.obj.show_only_shape_key = 0

        for sk in self.shape_keys:
            if sk.name in basis:
                continue
            if sk.mute:
                continue
            array = self.convert_shape_key_to_array(sk)
            shape_arrays[sk.name] = array
        self.set_shape_keys_values(stored_values)
        self.obj.show_only_shape_key = temp_show_only_shape_key

        return shape_arrays

    def convert_shape_key_to_array(self, shape_key):
        '''转换shapekey为1时的顶点位置'''
        if self.deformed:
            shape_key.value = 1
            temp_mesh = bpy.data.meshes.new('mesh')
            temp_bm = self.generate_bmesh(deformed=True, world_space=False)
            temp_bm.to_mesh(temp_mesh)
            verts = temp_mesh.vertices
            v_count = len(verts)
            co = np.zeros(v_count * 3, dtype=np.float32)
            verts.foreach_get("co", co)
            # co=co.reshape(-1,3)
            co.shape = (v_count, 3)
            temp_bm.free()
            bpy.data.meshes.remove(temp_mesh)
            shape_key.value = 0
            return co

    def get_verts_position(self):
        '''获取模型顶点坐标,返回坐标矩阵'''
        if self.deformed:
            temp_bm = self.generate_bmesh(deformed=self.deformed, world_space=self.world_space)
            temp_mesh = bpy.data.meshes.new('temp_mesh')
            temp_bm.to_mesh(temp_mesh)
            verts = temp_mesh.vertices
            v_count = len(verts)
            co = np.zeros(v_count * 3, dtype=np.float32)
            verts.foreach_get("co", co)
            co.shape = (v_count, 3)
            # 拿到顶点列*xyz坐标矩阵
            bpy.data.meshes.remove(temp_mesh)
            temp_bm.free()
            print(self.obj.name)
            print(co)
            return co
        v_count = len(self.mesh.vertices)
        co = np.zeros(v_count * 3, dtype=np.float32)
        self.mesh.vertices.foreach_get("co", co)
        co.shape = (v_count, 3)
        # print(co[0])
        # print(co)
        return co


class MeshDataTransfer:
    def __init__(self, source, thisobj, uv_space=False, deformed_source=False,
                 deformed_target=False, world_space=False, search_method="RAYCAST",
                 topolpgy=False, vertex_group=None, invert_vertex_group=False,
                 exclude_locked_groups=False, exclude_muted_shapekeys=False,
                 snap_to_closest=False, tranfer_divers=False, symmetry_axis=None):
        self.deformed_source = deformed_source
        self.search_method = search_method
        self.world_space = world_space
        self.uv_space = uv_space
        self.source = MeshData(source, uv_space=uv_space, deformed=deformed_source, world_space=world_space,
                               symmetry_axis=symmetry_axis)
        self.source.get_mesh_data()
        self.thisobj = MeshData(thisobj, uv_space=uv_space, world_space=world_space, symmetry_axis=symmetry_axis)
        self.thisobj.get_mesh_data()
        print('MeshDataTransfer self.world_space', self.world_space)
        self.vertex_group = vertex_group
        self.invert_vertex_group = invert_vertex_group
        self.symmetry_axis=symmetry_axis
        self.ray_casted = None
        self.related_ids = None
        self.hit_faces = None
        self.missed_projections = None
        self.cast_verts()  # 返回投射相关
        self.tranfer_divers = tranfer_divers

    @staticmethod
    def get_barycentric_coords(ray_casted, hit_faces):
        '''计算重心坐标'''
        barycentric_coords = ray_casted.copy()
        vert_to_corners = np.copy(hit_faces)
        vert_to_corners[:, 0] -= ray_casted
        vert_to_corners[:, 1] -= ray_casted
        vert_to_corners[:, 2] -= ray_casted
        # 当前面的垂直向量
        main_triangle_areas = np.cross((hit_faces[:, 0] - hit_faces[:, 1]),
                                       (hit_faces[:, 0] - hit_faces[:, 2]))  # va
        va1 = np.cross(vert_to_corners[:, 1], vert_to_corners[:, 2])  # va1
        va2 = np.cross(vert_to_corners[:, 2], vert_to_corners[:, 0])  # va2
        va3 = np.cross(vert_to_corners[:, 0], vert_to_corners[:, 1])  # va2
        '''计算整体面积'''
        a = np.sqrt((main_triangle_areas * main_triangle_areas).sum(axis=1))
        barycentric_coords[:, 0] = np.sqrt((va1 * va1).sum(axis=1)) / a * np.sign((va1 * main_triangle_areas).sum(1))
        barycentric_coords[:, 1] = np.sqrt((va2 * va2).sum(axis=1)) / a * np.sign((va2 * main_triangle_areas).sum(1))
        barycentric_coords[:, 2] = np.sqrt((va3 * va3).sum(axis=1)) / a * np.sign((va3 * main_triangle_areas).sum(1))
        # print(barycentric_coords)
        return barycentric_coords

    def cast_verts(self):
        '''
        投射追踪
        返回
        self.ray_casted:自身到目标面 最近目标面的顶点坐标
        self.hit_faces:自身投射到目标面 目标面的顶点坐标
        self.related_ids: 目标面的顶点坐标id
        '''
        # 传形状用bvh树
        if self.symmetry_axis is None:
            # 操作顶点顺序时先初始化
            self.thisobj.transfer_bmesh.verts.ensure_lookup_table()

            v_count = len(self.thisobj.mesh.vertices)
            self.ray_casted = np.zeros(v_count * 3, dtype=np.float32)
            self.ray_casted.shape = (v_count, 3)
            # 自身投影到采样物体上,投影所在面的顶点
            self.related_ids = np.zeros(v_count * 3, dtype=np.int)
            '''自身投影到采样物体上,投影所在面的顶点id'''
            self.related_ids.shape = (v_count, 3)

            self.missed_projections = np.ones(v_count * 3, dtype=np.bool)
            self.missed_projections.shape = (v_count, 3)
            # 自身投影到采样物体上,投影所在面的顶点
            self.hit_faces = np.zeros(v_count * 9, dtype=np.float32)
            self.hit_faces.shape = (v_count, 3, 3)

            v_normal = Vector((0, 0, 1))
            self.source.transfer_bmesh.faces.ensure_lookup_table()
            # 遍历索引前先初始化
            for v in self.thisobj.transfer_bmesh.verts:

                v_id = self.thisobj.vertex_map[v.index]
                # v_ids接收此顶点的字典索引内容,里面可能包含多个面循环uv顶点索引
                if self.search_method == "CLOSEST":
                    projection = self.source.bvhtree.find_nearest(v.co)
                    print('projection', projection, '|', 'this', v.co)
                    for v in self.source.transfer_bmesh.faces[projection[2]].verts:
                        print('v', v.co)
                    # Vector location, Vector normal, int index, float distance
                    # 返回的是最近的面上的顶点坐标+xxx
                else:
                    if not self.uv_space:
                        v_normal = v.normal
                        # 返回顶点的法线向量
                    projection = self.source.bvhtree.ray_cast(v.co, v_normal)
                    # 返回的是投影面上的顶点的坐标
                    # 正面没击中,就反向投射
                    if not projection[0]:
                        projection = self.source.bvhtree.ray_cast(v.co, -1 * v_normal)
                '''
                总结:遍历自身顶点,通过bvhtree传入顶点,返回击中的面,取得面的三个顶点(面已经三角化,不用考虑四边面的情况)
                '''
                if projection[0]:
                    #    for v_id in v_ids:
                    self.ray_casted[v_id] = projection[0]
                    # 接收投影的面中的一个顶点坐标
                    self.missed_projections[v_id] = False
                    # 接收采样物体的面(投影上去的)
                    face = self.source.transfer_bmesh.faces[projection[2]]
                    self.hit_faces[v_id] = (face.verts[0].co, face.verts[1].co, face.verts[2].co)
                    #
                    v1_id = self.source.vertex_map[face.verts[0].index]
                    v2_id = self.source.vertex_map[face.verts[1].index]
                    v3_id = self.source.vertex_map[face.verts[2].index]
                    v_arry = np.array([v1_id, v2_id, v3_id])
                    # 拿到自身物体投影到采集物体身上的面的顶点的id
                    self.related_ids[v_id] = v_arry
                else:
                    # 搜索最近的面
                    # 搜锤子  就把自己传进去
                    # for v_id in v_ids:
                    self.ray_casted[v_id] = v.co
            print('toushe', self.ray_casted)
            return self.ray_casted, self.hit_faces, self.related_ids
        else:
            pass
            # self.vertex_map={}
            for v in self.thisobj.mesh.vertices:
                self.thisobj.vertex_map[v.index]=self.source.kdtree.find(v.co)[0]


    def free(self):
        '''释放内存.清空bmesh'''
        if self.thisobj:
            self.thisobj.free_memory()
        if self.source:
            self.source.free_memory()

    def get_transferred_vert_coords(self, transfer_coord):
        indexes = self.related_ids.ravel()
        '''顶点数*3的id组,展平'''
        # 顶点矩阵transfer_coord
        sorted_coords = transfer_coord[indexes]
        '''按照自定义的id顺序,给顶点重新排序'''
        sorted_coords.shape = self.hit_faces.shape
        '''顶点*坐标的二维矩阵,转为序号,关联顶点,坐标'''
        self.barycentric_coords = self.get_barycentric_coords(self.ray_casted, self.hit_faces)
        transferred_position = self.calculate_barycentric_location(sorted_coords, self.barycentric_coords)

        return transferred_position

    @staticmethod
    def calculate_barycentric_location(uv_coords, coords):
        """
        Calculate the vertex position based on the coords
        :param uv_coords:
        :param coords:
        :return:
        """
        # print("UV_coords[0,0] is: ", uv_coords[0, 0])
        # print ("Coords[0,0] is: " , coords[0, 0])
        location = uv_coords[:, 0] * coords[:, 0, None] + \
                   uv_coords[:, 1] * coords[:, 1, None] + \
                   uv_coords[:, 2] * coords[:, 2, None]
        return location

    def get_projected_vertices_on_source(self):
        '''返回投影在采样网格上的顶点坐标'''
        transferred_position=None
        if self.symmetry_axis is None:
        # 取得采样网格顶点矩阵
            transfer_coord = self.source.get_verts_position()
            transferred_position = self.get_transferred_vert_coords(transfer_coord)
        else:
            # co=np.zeros(len(self.thisobj.vertex_map)*3,dtype=np.float32)
            # co.shape=(len(self.thisobj.vertex_map),3)
            transferred_position=np.array([self.thisobj.vertex_map[i] for i in self.thisobj.vertex_map])
        undeformed_verts = self.thisobj.get_verts_position()

        transferred_position = np.where(self.missed_projections, undeformed_verts, transferred_position)
        # filtering through vertex
        masked_vertices = self.get_vertices_mask()
        #  print(self.vertex_group)
        if isinstance(masked_vertices, np.ndarray):
            transferred_position = undeformed_verts + (transferred_position - undeformed_verts) * masked_vertices
        return transferred_position

    def get_vertices_mask(self):
        """
        get the vertex group weights for the filter
        :return:
        """
        if self.vertex_group:
            v_group = self.thisobj.get_vertex_group_weights(self.vertex_group)
            if self.invert_vertex_group:
                v_group = 1.0 - v_group
            return v_group

    def transfer_vertex_position(self, as_shape_key=False):
        #
        transferred_positon = self.get_projected_vertices_on_source()
        shape_key_basis = ['Basis', 'basis', '基型']
        if as_shape_key:
            shape_key_name = "{}.transferred".format(self.source.obj.name)
            self.thisobj.set_position_as_shape_key(shape_key_name=shape_key_name, co=transferred_positon, activate=1)
        else:
            # print(self.thisobj.name)
            # 有时候物体有形态键了，但是想传形状给basis
            if not hasattr(self.thisobj.mesh.shape_keys, 'key_blocks'):

                self.thisobj.set_verts_position(transferred_positon)
            else:
                for i in shape_key_basis:

                    try:
                        self.thisobj.mesh.shape_keys.key_blocks[i].data.foreach_set('co', transferred_positon.ravel())
                    except:
                        pass
        # 刷新视图
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.editmode_toggle()

        return 1
    def fix_mirror_transfer_vertex_position(self,as_shape_key=False):

        transferred_positon = self.get_projected_vertices_on_source()
        shape_key_basis = ['Basis', 'basis', '基型']

            # 有时候物体有形态键了，但是想传形状给basis
        if not hasattr(self.thisobj.mesh.shape_keys, 'key_blocks'):

            self.thisobj.set_verts_position(transferred_positon)
        else:
            for s in shape_key_basis:

                try:
                    self.thisobj.mesh.shape_keys.key_blocks[s].data.foreach_set('co', transferred_positon.ravel())
                except:
                    pass
        # 刷新视图
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.editmode_toggle()

        return 1
    def transfer_uv(self):
        '''
        传递uv
        
        '''
        current_object = bpy.context.object
        current_mode = bpy.context.object.mode
        if not current_mode == "OBJECT":
            bpy.ops.object.mode_set(nide="OBJECT")
        if not current_object == self.thisobj.obj:  # 由meshdata类传入
            bpy.context.active_object = self.thisobj.obj
        loop_mapping = 'POLYINTERP_NEAREST'
        poly_mapping = 'POLYINTERP_PNORPROJ'
        transfer_source = self.source.obj
        transfer_thisobj = self.thisobj.obj
        data_transfer_mo = self.thisobj.obj.modifiers.new(name="Data Transfer", type='DATA_TRANSFER')
        data_transfer_mo.use_object_transform = self.world_space
        data_transfer_mo.object = transfer_source
        data_transfer_mo.use_loop_data = True
        data_transfer_mo.data_types_loops = {'UV'}
        data_transfer_mo.use_poly_data = True
        data_transfer_mo.loop_mapping = loop_mapping
        # 修改器预设完成
        source_active_uv = transfer_source.data.uv_layers.active
        data_transfer_mo.layers_uv_select_src = source_active_uv.name
        thisobj_uv = transfer_thisobj.data.uv_layers.active
        if not thisobj_uv:
            thisobj_uv = transfer_thisobj.data.uv_layers.new()
        data_transfer_mo.layers_uv_select_dst = thisobj_uv.name

        if self.vertex_group:
            data_transfer_mo.vertex_group = self.vertex_group
            data_transfer_mo.invert_vertex_group = self.invert_vertex_group

        data_transfer_mo.poly_mapping = poly_mapping
        bpy.ops.object.datalayout_transfer(modifier=data_transfer_mo.name)
        bpy.ops.object.modifier_apply(modifier=data_transfer_mo.name)

    def transfer_vertex_group(self):

        pass
