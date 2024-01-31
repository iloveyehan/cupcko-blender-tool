import bpy


def shape_key_fc_LR(objname):
    # 存储场景的激活相机
    camera = bpy.context.scene.camera
    # 存储要做驱动变化的模型
    obj = bpy.data.objects[objname]
    # 将4*4的世界坐标系变换矩阵转换成3*3，再切割出x轴向向量
    obj_left = obj.matrix_world.to_3x3().transposed()[0].normalized()
    # 求x轴向量和相机的夹角
    # 两个单位向量a*b=|a||b|cosθ=cosθ
    # 根据cos函数的图像，相机正对x轴时，应该达到1，正好对应驱动器权重1
    angle_value = obj_left.dot((camera.matrix_world.translation - obj.matrix_world.translation).normalized())

    return -angle_value


def shape_key_fc_UD(objname):
    # 存储场景的激活相机
    camera = bpy.context.scene.camera
    # 存储要做驱动变化的模型
    obj = bpy.data.objects[objname]
    # 将4*4的世界坐标系变换矩阵转换成3*3，再切割出x轴向向量
    obj_left = obj.matrix_world.to_3x3().transposed()[2].normalized()
    # 求x轴向量和相机的夹角
    # 两个单位向量a*b=|a||b|cosθ=cosθ
    # 根据cos函数的图像，相机正对z轴时，应该达到1，正好对应驱动器权重1
    angle_value = obj_left.dot((camera.matrix_world.translation - obj.matrix_world.translation).normalized())
    return angle_value


class Camera_Driver(bpy.types.Operator):
    '''自动设置相机驱动，名称格式right，left，up，down__fix'''
    # '''先拿到物体的x轴向量，跟相机对物体向量求向量积，获得夹角大小'''
    bl_idname = "cupcko.character_camera_driver"
    bl_label = "设置角度驱动"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.active_object is None:
            return 0
        return bpy.context.object.data.shape_keys != None

    def execute(self, context):
        # 把函数名放在驱动器的namespace命名空间，方便在驱动器里调用这个函数
        bpy.app.driver_namespace['shape_key_LR'] = shape_key_fc_LR
        bpy.app.driver_namespace['shape_key_UD'] = shape_key_fc_UD
        sk = context.object.data.shape_keys
        for key, keyblock in sk.key_blocks.items():
            if keyblock == sk.key_blocks[0]:
                print("忽略basis")
                continue
            # 如果形态键中有我们设置的对应的名字，就按照名字一一设置好脚本驱动
            if 'right__fix' in key:
                fcurve = sk.driver_add(f'key_blocks["{key}"].value')
                fcurve.driver.expression = f'max(0,shape_key_LR("{context.object.name}"))'
            elif 'left__fix' in key:
                fcurve = sk.driver_add(f'key_blocks["{key}"].value')
                fcurve.driver.expression = f'max(0,-shape_key_LR("{context.object.name}"))'
            elif 'up__fix' in key:
                fcurve = sk.driver_add(f'key_blocks["{key}"].value')
                fcurve.driver.expression = f'max(0,shape_key_UD("{context.object.name}"))'
            elif 'down__fix' in key:
                fcurve = sk.driver_add(f'key_blocks["{key}"].value')
                fcurve.driver.expression = f'max(0,-shape_key_UD("{context.object.name}"))'

        return {'FINISHED'}
