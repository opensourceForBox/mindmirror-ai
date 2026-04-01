#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Modeling Workflow - 自动建模工作流
根据用户输入自动生成 3D 模型，并支持后期 Blender 修改
"""

import argparse
import base64
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# 工作目录
WORK_DIR = Path("/tmp/auto-modeling")
GENERATED_DIR = WORK_DIR / "generated"
MODIFIED_DIR = WORK_DIR / "modified"

def ensure_dirs():
    """确保工作目录存在"""
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    MODIFIED_DIR.mkdir(parents=True, exist_ok=True)

def parse_args():
    parser = argparse.ArgumentParser(description="自动建模工作流")
    
    # 输入参数（二选一）
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument("--prompt", type=str, help="文本描述（文生 3D）")
    input_group.add_argument("--image-base64", type=str, help="图片 Base64（图生 3D）")
    input_group.add_argument("--image-path", type=str, help="图片本地路径（图生 3D）")
    
    # 可选参数
    parser.add_argument("--style", type=str, default="", help="风格要求")
    parser.add_argument("--modification", type=str, default="", help="修改需求")
    parser.add_argument("--model-version", type=str, default="3.1", choices=["3.0", "3.1"], help="混元 3D 版本")
    parser.add_argument("--face-count", type=int, default=500000, help="面数")
    parser.add_argument("--output", type=str, default=None, help="输出文件路径")
    
    return parser.parse_args()

def load_image_as_base64(image_path):
    """将本地图片转换为 Base64"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def generate_3d_model(prompt=None, image_base64=None, model_version="3.1", face_count=500000):
    """调用混元 3D 生成模型"""
    print(f"\n🚀 开始生成 3D 模型...")
    
    # 构建参数
    params = {
        "model": model_version,
        "face_count": face_count
    }
    
    if prompt:
        params["prompt"] = prompt
        print(f"   描述：{prompt}")
    elif image_base64:
        params["image_base64"] = image_base64[:50] + "..." if len(image_base64) > 50 else image_base64
        print(f"   图片 Base64 长度：{len(image_base64)}")
    
    # 通过 stdin 传入参数
    json_input = json.dumps(params)
    
    # 执行混元 3D 脚本
    script_path = Path.home() / ".openclaw/workspace/skills/hy-3d-generation/scripts/main.py"
    
    result = subprocess.run(
        ["python3", str(script_path), "--stdin"],
        input=json_input,
        capture_output=True,
        text=True
    )
    
    # 解析结果
    try:
        output = json.loads(result.stdout)
        if "error" in output:
            print(f"❌ 生成失败：{output['error']} - {output.get('message', '')}")
            return None
        
        # 提取 GLB 下载链接
        for file_info in output.get("result_files", []):
            if file_info.get("type") == "GLB":
                glb_url = file_info.get("url")
                print(f"✅ 模型生成成功：{glb_url[:80]}...")
                return glb_url
        
        # 如果没有 GLB，返回第一个文件
        if output.get("result_files"):
            return output["result_files"][0].get("url")
            
    except json.JSONDecodeError:
        print(f"❌ 解析输出失败：{result.stdout}")
        print(f"   错误：{result.stderr}")
    
    return None

def download_model(url, output_path):
    """下载 3D 模型文件"""
    print(f"\n📥 下载模型：{url[:80]}...")
    
    import urllib.request
    urllib.request.urlretrieve(url, output_path)
    
    file_size = os.path.getsize(output_path) / 1024 / 1024  # MB
    print(f"✅ 下载完成：{output_path} ({file_size:.2f} MB)")
    return output_path

def generate_blender_command(modification, input_model):
    """调用 Blender 命令生成技能"""
    print(f"\n🔧 生成 Blender 修改命令...")
    
    script_path = Path.home() / ".openclaw/workspace/skills/blender-command-generator/scripts/generate_command.py"
    
    if not script_path.exists():
        print(f"⚠️  Blender 命令生成脚本不存在，跳过修改步骤")
        return None
    
    result = subprocess.run(
        ["python3", str(script_path), "--modification", modification, "--input-model", input_model],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        try:
            output = json.loads(result.stdout)
            command = output.get("blender_command")
            print(f"✅ Blender 命令已生成")
            return command
        except json.JSONDecodeError:
            print(f"⚠️  解析 Blender 命令失败：{result.stdout}")
    
    print(f"❌ Blender 命令生成失败：{result.stderr}")
    return None

def execute_blender_command(command, input_model, output_path):
    """执行 Blender 命令"""
    print(f"\n🎨 执行 Blender 修改...")
    
    # 创建 Blender Python 脚本
    script_content = f"""
import bpy
import sys

# 清除默认场景
bpy.ops.wm.read_factory_settings(use_empty=True)

# 导入模型
input_path = "{input_model}"
output_path = "{output_path}"

# 根据文件扩展名选择导入方式
if input_path.endswith('.glb'):
    bpy.ops.import_scene.gltf(filepath=input_path)
elif input_path.endswith('.obj'):
    bpy.ops.import_mesh.obj(filepath=input_path)
elif input_path.endswith('.fbx'):
    bpy.ops.import_scene.fbx(filepath=input_path)

# 执行修改命令
{command}

# 导出修改后的模型
if output_path.endswith('.glb'):
    bpy.ops.export_scene.gltf(filepath=output_path, export_format='GLB')
elif output_path.endswith('.obj'):
    bpy.ops.export.mesh.obj(filepath=output_path)
elif output_path.endswith('.fbx'):
    bpy.ops.export.scene.fbx(filepath=output_path)

print(f"修改完成：{{output_path}}")
"""
    
    # 写入临时脚本
    temp_script = WORK_DIR / "temp_blender_script.py"
    with open(temp_script, "w") as f:
        f.write(script_content)
    
    # 执行 Blender
    result = subprocess.run(
        ["blender", "--background", "--python", str(temp_script)],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"✅ Blender 修改完成：{output_path}")
        return output_path
    else:
        print(f"❌ Blender 执行失败：{result.stderr}")
        return None

def upload_to_feishu(file_path, message, chat_id=None):
    """上传文件到飞书"""
    print(f"\n📤 上传到飞书...")
    
    # 检查是否有飞书 message 工具可用
    # 这里简化处理，实际应该调用 message 工具
    print(f"   文件：{file_path}")
    print(f"   消息：{message}")
    print(f"   聊天 ID: {chat_id or '当前会话'}")
    print(f"✅ 上传逻辑需通过 message 工具实现")
    
    return True

def main():
    args = parse_args()
    ensure_dirs()
    
    print("=" * 60)
    print("🎯 自动建模工作流")
    print("=" * 60)
    
    # 步骤 1：生成 3D 模型
    if args.prompt:
        full_prompt = args.prompt
        if args.style:
            full_prompt += f"，风格：{args.style}"
        model_url = generate_3d_model(prompt=full_prompt, model_version=args.model_version, face_count=args.face_count)
    elif args.image_base64 or args.image_path:
        image_b64 = args.image_base64
        if not image_b64 and args.image_path:
            image_b64 = load_image_as_base64(args.image_path)
        model_url = generate_3d_model(image_base64=image_b64, model_version=args.model_version, face_count=args.face_count)
    else:
        print("❌ 错误：需要提供 --prompt 或 --image-base64/--image-path")
        sys.exit(1)
    
    if not model_url:
        print("❌ 3D 模型生成失败")
        sys.exit(1)
    
    # 步骤 2：下载模型
    timestamp = int(time.time())
    generated_path = GENERATED_DIR / f"model_{timestamp}.glb"
    downloaded_path = download_model(model_url, generated_path)
    
    # 步骤 3：Blender 修改（如果有修改需求）
    final_path = downloaded_path
    if args.modification:
        print(f"\n📝 修改需求：{args.modification}")
        
        blender_command = generate_blender_command(args.modification, str(downloaded_path))
        
        if blender_command:
            final_path = MODIFIED_DIR / f"model_{timestamp}_modified.glb"
            modified_result = execute_blender_command(blender_command, str(downloaded_path), str(final_path))
            if modified_result:
                final_path = Path(modified_result)
    
    # 步骤 4：输出结果
    print("\n" + "=" * 60)
    print("✅ 工作流完成！")
    print("=" * 60)
    print(f"最终模型：{final_path}")
    print(f"文件大小：{os.path.getsize(final_path) / 1024 / 1024:.2f} MB")
    
    # 输出 JSON 结果（供后续步骤使用）
    result = {
        "status": "success",
        "model_path": str(final_path),
        "original_path": str(downloaded_path),
        "modified": args.modification != ""
    }
    
    print(f"\n{json.dumps(result, ensure_ascii=False, indent=2)}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
