#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Blender Command Generator - 将自然语言转换为 Blender Python 命令
"""

import argparse
import json
import re
import sys
from typing import Dict, List, Optional, Tuple

# 命令模板库
COMMAND_TEMPLATES = {
    # === 变换操作 ===
    "scale": {
        "patterns": [r"放大 (\d+(?:\.\d+)?) 倍", r"缩放 (\d+(?:\.\d+)?) 倍", r"缩小到 (\d+(?:\.\d+)?)%"],
        "template": "bpy.ops.transform.resize(value=({factor}, {factor}, {factor}), orient_type='GLOBAL')",
        "description": "缩放模型"
    },
    "rotate": {
        "patterns": [r"旋转 (\d+(?:\.\d+)?) 度", r"沿 (?:[XYZxyz]) 轴旋转 (\d+(?:\.\d+)?) 度"],
        "template": "bpy.ops.transform.rotate(value={radians}, axis={axis})",
        "description": "旋转模型"
    },
    "translate": {
        "patterns": [r"向 (?:上 | 下 | 左 | 右 | 前 | 后) 移动 ([\d\.]+) 米", r"平移 ([\d\.]+) 米"],
        "template": "bpy.ops.transform.translate(value={vector})",
        "description": "移动模型"
    },
    
    # === 修改器操作 ===
    "subdivide": {
        "patterns": [r"细分", r"增加细节", r"平滑表面", r"平滑"],
        "template": "bpy.ops.object.modifier_add(type='SUBSURF'); bpy.context.object.modifiers['Subdivision'].levels = {levels}",
        "description": "添加细分修改器"
    },
    "decimate": {
        "patterns": [r"低多边形", r"减少面数", r"减面", r"简化"],
        "template": "bpy.ops.object.modifier_add(type='DECIMATE'); bpy.context.object.modifiers['Decimate'].ratio = {ratio}",
        "description": "添加减面修改器"
    },
    "smooth": {
        "patterns": [r"平滑着色", r"平滑法线"],
        "template": "bpy.ops.object.shade_smooth()",
        "description": "平滑着色"
    },
    
    # === 材质操作 ===
    "material_color": {
        "patterns": [r"改为 (.*?) 色", r"材质改为 (.*?)", r"颜色改为 (.*?)"],
        "template": "mat = bpy.data.materials.new(name='CustomMat'); mat.use_nodes = True; bsdf = mat.node_tree.nodes['Principled BSDF']; bsdf.inputs['Base Color'].default_value = {color}; obj = bpy.context.object; obj.data.materials.append(mat)",
        "description": "更改材质颜色"
    },
    "material_metal": {
        "patterns": [r"金属质感", r"金属材质", r"改为金属"],
        "template": "mat = bpy.data.materials.new(name='MetalMat'); mat.use_nodes = True; bsdf = mat.node_tree.nodes['Principled BSDF']; bsdf.inputs['Metallic'].default_value = 1.0; bsdf.inputs['Roughness'].default_value = 0.2; obj = bpy.context.object; obj.data.materials.append(mat)",
        "description": "添加金属材质"
    },
    "material_glass": {
        "patterns": [r"玻璃质感", r"透明材质", r"改为玻璃"],
        "template": "mat = bpy.data.materials.new(name='GlassMat'); mat.use_nodes = True; bsdf = mat.node_tree.nodes['Principled BSDF']; bsdf.inputs['Transmission'].default_value = 1.0; bsdf.inputs['Roughness'].default_value = 0.0; obj = bpy.context.object; obj.data.materials.append(mat)",
        "description": "添加玻璃材质"
    },
    
    # === 添加几何体 ===
    "add_text": {
        "patterns": [r"添加文字 ['\"]?(.*?)['\"]?", r"写上 ['\"]?(.*?)['\"]?", r"刻上 ['\"]?(.*?)['\"]?"],
        "template": "bpy.ops.object.text_add(); text = bpy.context.object; text.data.body = '{text}'; text.location.z += 0.5",
        "description": "添加文字"
    },
    "add_cube": {
        "patterns": [r"添加立方体", r"添加方块"],
        "template": "bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))",
        "description": "添加立方体"
    },
    "add_sphere": {
        "patterns": [r"添加球体", r"添加圆球"],
        "template": "bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0))",
        "description": "添加球体"
    },
    
    # === 浮雕效果 ===
    "emboss": {
        "patterns": [r"添加 (.*?) 浮雕", r"(.*?) 浮雕", r"雕刻 (.*?)"],
        "template": "bpy.ops.object.modifier_add(type='DISPLACE'); displace = bpy.context.object.modifiers['Displace']; displace.strength = 0.3; displace.direction = 'NORMAL'",
        "description": "添加浮雕效果"
    },
    
    # === 布尔操作 ===
    "boolean_cut": {
        "patterns": [r"挖 (?:一个)?洞", r"切割", r"布尔切割"],
        "template": "bpy.ops.mesh.primitive_cylinder_add(radius=0.1, location=(0, 0, 0)); cutter = bpy.context.object; bpy.ops.object.mode_set(mode='OBJECT'); bpy.context.view_layer.objects.active = bpy.context.object; bpy.ops.object.modifier_add(type='BOOLEAN'); bpy.context.object.modifiers['Boolean'].object = cutter; bpy.ops.object.modifier_apply(modifier='Boolean')",
        "description": "布尔切割"
    },
}

# 颜色映射
COLOR_MAP = {
    "红色": (1, 0, 0, 1),
    "绿色": (0, 1, 0, 1),
    "蓝色": (0, 0, 1, 1),
    "黄色": (1, 1, 0, 1),
    "白色": (1, 1, 1, 1),
    "黑色": (0, 0, 0, 1),
    "灰色": (0.5, 0.5, 0.5, 1),
    "银色": (0.75, 0.75, 0.75, 1),
    "金色": (1, 0.84, 0, 1),
    "粉色": (1, 0.75, 0.8, 1),
    "紫色": (0.5, 0, 0.5, 1),
    "橙色": (1, 0.5, 0, 1),
    "青色": (0, 1, 1, 1),
}

# 轴向映射
AXIS_MAP = {
    "x": (1, 0, 0),
    "y": (0, 1, 0),
    "z": (0, 0, 1),
    "X": (1, 0, 0),
    "Y": (0, 1, 0),
    "Z": (0, 0, 1),
}

# 方向向量映射
DIRECTION_MAP = {
    "上": (0, 0, 1),
    "下": (0, 0, -1),
    "左": (-1, 0, 0),
    "右": (1, 0, 0),
    "前": (0, 1, 0),
    "后": (0, -1, 0),
}


def parse_scale(modification: str) -> Optional[Dict]:
    """解析缩放指令"""
    patterns = [
        (r"放大 ([\d\.]+) 倍", lambda m: float(m.group(1))),
        (r"缩放 ([\d\.]+) 倍", lambda m: float(m.group(1))),
        (r"缩小到 ([\d\.]+)%", lambda m: float(m.group(1)) / 100),
        (r"缩小 ([\d\.]+) 倍", lambda m: 1.0 / float(m.group(1))),
    ]
    
    for pattern, extractor in patterns:
        match = re.search(pattern, modification)
        if match:
            factor = extractor(match)
            return {
                "command": f"bpy.ops.transform.resize(value=({factor}, {factor}, {factor}), orient_type='GLOBAL')",
                "description": f"将模型缩放 {factor} 倍"
            }
    return None


def parse_rotate(modification: str) -> Optional[Dict]:
    """解析旋转指令"""
    import math
    
    # 匹配轴向和角度
    axis_match = re.search(r"沿 ([XYZxyz]) 轴旋转 ([\d\.]+) 度", modification)
    if axis_match:
        axis_char = axis_match.group(1)
        degrees = float(axis_match.group(2))
        radians = math.radians(degrees)
        
        axis_vector = AXIS_MAP.get(axis_char, (0, 0, 1))
        
        return {
            "command": f"bpy.ops.transform.rotate(value={radians:.4f}, axis={axis_vector})",
            "description": f"沿{axis_char.upper()}轴旋转{degrees}度"
        }
    
    # 仅角度，默认 Z 轴
    angle_match = re.search(r"旋转 ([\d\.]+) 度", modification)
    if angle_match:
        degrees = float(angle_match.group(1))
        radians = math.radians(degrees)
        
        return {
            "command": f"bpy.ops.transform.rotate(value={radians:.4f}, axis=(0, 0, 1))",
            "description": f"沿 Z 轴旋转{degrees}度"
        }
    
    return None


def parse_translate(modification: str) -> Optional[Dict]:
    """解析平移指令"""
    for direction, vector in DIRECTION_MAP.items():
        match = re.search(rf"向{direction} 移动 ([\d\.]+) 米", modification)
        if match:
            distance = float(match.group(1))
            vec_str = f"({vector[0]*distance}, {vector[1]*distance}, {vector[2]*distance})"
            return {
                "command": f"bpy.ops.transform.translate(value={vec_str})",
                "description": f"向{direction}移动{distance}米"
            }
    return None


def parse_material(modification: str) -> Optional[Dict]:
    """解析材质指令"""
    # 检查颜色
    for color_name, color_value in COLOR_MAP.items():
        if color_name in modification or color_name.lower() in modification.lower():
            color_str = f"{color_value}"
            return {
                "command": f"mat = bpy.data.materials.new(name='CustomMat'); mat.use_nodes = True; bsdf = mat.node_tree.nodes['Principled BSDF']; bsdf.inputs['Base Color'].default_value = {color_str}; obj = bpy.context.object; obj.data.materials.append(mat)",
                "description": f"将材质改为{color_name}"
            }
    
    # 检查特殊材质
    if "金属" in modification:
        return {
            "command": "mat = bpy.data.materials.new(name='MetalMat'); mat.use_nodes = True; bsdf = mat.node_tree.nodes['Principled BSDF']; bsdf.inputs['Metallic'].default_value = 1.0; bsdf.inputs['Roughness'].default_value = 0.2; obj = bpy.context.object; obj.data.materials.append(mat)",
            "description": "添加金属材质"
        }
    
    if "玻璃" in modification or "透明" in modification:
        return {
            "command": "mat = bpy.data.materials.new(name='GlassMat'); mat.use_nodes = True; bsdf = mat.node_tree.nodes['Principled BSDF']; bsdf.inputs['Transmission'].default_value = 1.0; bsdf.inputs['Roughness'].default_value = 0.0; obj = bpy.context.object; obj.data.materials.append(mat)",
            "description": "添加玻璃/透明材质"
        }
    
    return None


def parse_add_text(modification: str) -> Optional[Dict]:
    """解析添加文字指令"""
    match = re.search(r"添加文字 ['\"]?(.*?)['\"]?$|写上 ['\"]?(.*?)['\"]?$|刻上 ['\"]?(.*?)['\"]?$", modification)
    if match:
        text = match.group(1) or match.group(2) or match.group(3)
        return {
            "command": f"bpy.ops.object.text_add(); text = bpy.context.object; text.data.body = '{text}'; text.location.z += 0.5",
            "description": f"添加文字'{text}'"
        }
    return None


def parse_emboss(modification: str) -> Optional[Dict]:
    """解析浮雕指令"""
    # 检查是否包含"浮雕"关键词
    if "浮雕" in modification:
        # 尝试提取浮雕主题
        match = re.search(r"添加 (.*?) 浮雕 | (.*?) 浮雕 | 雕刻 (.*?) 浮雕", modification)
        subject = "图案"
        if match:
            subject = match.group(1) or match.group(2) or match.group(3) or "图案"
        else:
            # 简单提取"浮雕"前的内容
            parts = modification.split("浮雕")
            if len(parts) > 0 and parts[0]:
                subject = parts[0].replace("添加", "").replace("的", "").strip()
        
        return {
            "command": f"bpy.ops.object.modifier_add(type='DISPLACE'); displace = bpy.context.object.modifiers['Displace']; displace.strength = 0.3; displace.direction = 'NORMAL'",
            "description": f"添加{subject}浮雕效果",
            "warnings": ["建议使用纹理贴图以获得更好的浮雕效果"]
        }
    return None


def parse_decimate(modification: str) -> Optional[Dict]:
    """解析减面指令"""
    if any(kw in modification for kw in ["低多边形", "减少面数", "减面", "简化"]):
        # 检查是否有具体比例
        ratio_match = re.search(r"减少到 (\d+(?:\.\d+)?)%|保留 (\d+(?:\.\d+)?)%", modification)
        ratio = float(ratio_match.group(1) or ratio_match.group(2)) / 100 if ratio_match else 0.1
        
        return {
            "command": f"bpy.ops.object.modifier_add(type='DECIMATE'); bpy.context.object.modifiers['Decimate'].ratio = {ratio}",
            "description": f"添加减面修改器，保留{ratio*100:.0f}%的面"
        }
    return None


def parse_subdivide(modification: str) -> Optional[Dict]:
    """解析细分指令"""
    if any(kw in modification for kw in ["细分", "增加细节", "平滑表面", "平滑"]):
        levels = 2  # 默认细分级别
        levels_match = re.search(r"(\d+) 级|(\d+) 层", modification)
        if levels_match:
            levels = int(levels_match.group(1) or levels_match.group(2))
        
        return {
            "command": f"bpy.ops.object.modifier_add(type='SUBSURF'); bpy.context.object.modifiers['Subdivision'].levels = {levels}",
            "description": f"添加细分修改器（{levels}级）"
        }
    return None


def generate_blender_command(modification: str, input_model: Optional[str] = None) -> Dict:
    """
    根据自然语言描述生成 Blender 命令
    
    Args:
        modification: 修改描述
        input_model: 输入模型路径（可选）
    
    Returns:
        包含命令和说明的字典
    """
    
    # 按顺序尝试各种解析器
    parsers = [
        parse_scale,
        parse_rotate,
        parse_translate,
        parse_material,
        parse_add_text,
        parse_emboss,
        parse_decimate,
        parse_subdivide,
    ]
    
    for parser in parsers:
        result = parser(modification)
        if result:
            response = {
                "blender_command": result["command"],
                "description": result["description"],
                "input_model": input_model
            }
            if "warnings" in result:
                response["warnings"] = result["warnings"]
            return response
    
    # 如果没有匹配的解析器，返回通用响应
    return {
        "blender_command": f"# 无法解析修改指令：{modification}\n# 请提供更具体的描述，如'放大 2 倍'、'改为红色'、'添加文字 Hello'等",
        "description": f"未识别的修改类型：{modification}",
        "suggestions": [
            "放大/缩小 X 倍",
            "旋转 X 度",
            "改为 X 色",
            "添加文字'XXX'",
            "添加 X 浮雕",
            "低多边形风格",
            "细分表面"
        ]
    }


def main():
    parser = argparse.ArgumentParser(description="Blender 命令生成器")
    parser.add_argument("--modification", type=str, required=True, help="修改描述")
    parser.add_argument("--input-model", type=str, default=None, help="输入模型路径")
    parser.add_argument("--output", type=str, default=None, help="输出文件路径")
    
    args = parser.parse_args()
    
    # 生成命令
    result = generate_blender_command(args.modification, args.input_model)
    
    # 输出 JSON
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
