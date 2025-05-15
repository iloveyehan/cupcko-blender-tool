import json, bpy, urllib.request
import zipfile, os, tempfile

def download_and_install(download_url):
    tmp = tempfile.mkdtemp()
    zip_path = os.path.join(tmp, "addon.zip")
    urllib.request.urlretrieve(download_url, zip_path)  # 下载 ZIP
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(path=tmp)                      # 解压到临时目录
    # 将解压后的目录覆盖到 Blender 的脚本目录
    scripts_path = bpy.utils.user_resource('SCRIPTS', "addons")
    addon_name = "你的插件文件夹名"
    target = os.path.join(scripts_path, addon_name)
    # 先删除旧文件，再移动新文件
    import shutil
    if os.path.exists(target):
        shutil.rmtree(target)
    shutil.move(os.path.join(tmp, addon_name), target)
def get_remote_version():
    url = "https://raw.githubusercontent.com/你的仓库/main/version.json"
    with urllib.request.urlopen(url) as resp:
        data = json.load(resp)
    return data  # 返回 dict，包含 version、download_url 等

def get_local_version():
    return bpy.context.preferences.addons[__name__].preferences.version  # 假设在插件偏好里存了 version
class CheckUpdateOperator(bpy.types.Operator):
    bl_idname = "cupcko.check_update"
    bl_label = "检查更新"

    def execute(self, context):
        remote = get_remote_version()
        local = get_local_version()
        if remote["version"] != local:
            self.report({'INFO'}, f"检测到新版本 {remote['version']}，开始下载")
            download_and_install(remote["download_url"])
            self.report({'INFO'}, "插件已更新，请重启 Blender")
        else:
            self.report({'INFO'}, "已是最新版本")
        return {'FINISHED'}