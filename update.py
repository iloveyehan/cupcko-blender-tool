import json, bpy, urllib.request
from pathlib import Path
import shutil
import zipfile,  tempfile
import importlib
def ignore_git(dir, names):
    return ['.git'] if '.git' in names else []
def download_and_install(remote):
    # 创建临时目录
    tmp = Path(tempfile.mkdtemp())
    
    # 下载 ZIP 文件
    zip_path = tmp / "addon.zip"
    urllib.request.urlretrieve(remote["download_url"], zip_path)
    
    # 解压 ZIP 文件
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(path=tmp)
    # addon_name = Path(__file__).parent.name+'-'
    addon_path = Path(__file__).parent
    # 4. 找到解压后真实的子文件夹
    extracted = [d for d in tmp.iterdir() if d.is_dir()]
    if not extracted:
        raise RuntimeError("解压后未发现目录")
    source_dir = extracted[0]
    # print('addon_name',addon_name,source_dir)
    # 获取 Blender 插件目录
    # scripts_path = Path(bpy.utils.user_resource('SCRIPTS', "addons"))
    
    # # 使用当前文件的父目录名作为插件文件夹名
    # addon_name = Path(__file__).parent.name
    # target = scripts_path / addon_name
    
    # 直接覆盖目标目录中的文件
    shutil.copytree(source_dir, addon_path, dirs_exist_ok=True,ignore=ignore_git)
def get_remote_version():
    url = "https://raw.githubusercontent.com/iloveyehan/cupcko-blender-tool/refs/heads/main/version.json"
    with urllib.request.urlopen(url) as resp:
        data = json.load(resp)
    return data  # 返回 dict，包含 version、download_url 等

def get_local_version():
    addon_module = importlib.import_module('cupcko-blender-tool')
    version = addon_module.bl_info.get("version", (0, 0, 0))
    return str(version)
class CheckUpdateOperator(bpy.types.Operator):
    bl_idname = "cupcko.check_update"
    bl_label = "检查更新"

    def execute(self, context):
        remote = get_remote_version()
        local = get_local_version()
        remote_str = remote["version"].replace(" ", "")
        local = local.replace(" ", "")
        # print(str(remote),str(local),str(remote)==str(local))
        if remote_str != local:
            self.report({'INFO'}, f"检测到新版本 {remote_str}，开始下载")
            download_and_install(remote)
            self.report({'INFO'}, "插件已更新，请重启 Blender")
        else:
            self.report({'INFO'}, "已是最新版本")
        return {'FINISHED'}