---
name: blender-command-generator
description: >
  通过自然语言生成 Blender Python 命令，用于 3D 模型的后期修改和处理。支持材质调整、几何体编辑、动画添加等操作。
---

# Blender 命令生成 Skill

## 功能描述

本 Skill 将**自然语言描述转换为 Blender Python 命令**，用于：
- 几何体编辑（缩放、旋转、位移、细分）
- 材质调整（颜色、纹理、透明度）
- 添加几何体（文字、形状、浮雕）
- 模型优化（减面、平滑、法线）
- 渲染设置（相机、灯光、背景）

## 支持的修改类型

| 类型 | 示例描述 | 生成的命令 |
|------|----------|-----------|
| **缩放** | "放大 2 倍"、"缩小到 50%" | `bpy.ops.transform.resize(value=(2, 2, 2))` |
| **旋转** | "旋转 90 度"、"沿 Z 轴旋转" | `bpy.ops.transform.rotate(value=1.57, axis=(0, 0, 1))` |
| **位移** | "向上移动 1 米"、"向左平移" | `bpy.ops.transform.translate(value=(0, 0, 1))` |
| **细分** | "增加细节"、"平滑表面" | `bpy.ops.object.modifier_add(type='SUBSURF')` |
| **减面** | "低多边形"、"减少面数" | `bpy.ops.object.modifier_add(type='DECIMATE')` |
| **材质** | "改为红色"、"添加金属质感" | `mat.diffuse_color = (1, 0, 0, 1)` |
| **文字** | "添加文字'Hello'" | `bpy.ops.object.text_add()` |
| **浮雕** | "添加皮卡丘浮雕" | 使用雕刻或置换修改器 |
| **布尔** | "挖一个洞"、"切割" | `bpy.ops.object.boolean_operation()` |

## Agent 执行指令

### 📌 步骤 1：解析修改需求

从用户输入中提取：
- 修改类型（缩放/旋转/材质/添加等）
- 参数值（倍数、角度、颜色等）
- 目标对象（整体/特定部分）

### 📌 步骤 2：生成 Blender Python 命令

根据修改类型生成对应的 Blender API 调用：

```python
# 示例：添加文字
bpy.ops.object.text_add()
text_obj = bpy.context.object
text_obj.data.body = "Hello"

# 示例：添加材质
mat = bpy.data.materials.new(name="RedMaterial")
mat.diffuse_color = (1, 0, 0, 1)
obj.data.materials.append(mat)

# 示例：细分
bpy.ops.object.modifier_add(type='SUBSURF')
bpy.context.object.modifiers["Subdivision"].levels = 2
```

### 📌 步骤 3：输出可执行命令

输出格式：
```json
{
  "blender_command": "Python 代码字符串",
  "description": "命令说明",
  "warnings": ["注意事项"]
}
```

## 调用示例

### 示例 1：缩放模型

**输入**：
```bash
python3 scripts/generate_command.py --modification "放大 2 倍"
```

**输出**：
```json
{
  "blender_command": "bpy.ops.transform.resize(value=(2, 2, 2), orient_type='GLOBAL')",
  "description": "将模型在所有轴向上放大 2 倍"
}
```

### 示例 2：添加文字

**输入**：
```bash
python3 scripts/generate_command.py --modification "在顶部添加文字'Custom'"
```

**输出**：
```json
{
  "blender_command": "bpy.ops.object.text_add(); text = bpy.context.object; text.data.body = 'Custom'; text.location.z += 1",
  "description": "添加文字对象并定位到模型顶部"
}
```

### 示例 3：添加浮雕

**输入**：
```bash
python3 scripts/generate_command.py --modification "添加皮卡丘浮雕" --input-model "/path/to/model.glb"
```

**输出**：
```json
{
  "blender_command": "# 使用置换修改器添加浮雕效果\nbpy.ops.object.modifier_add(type='DISPLACE'); displace = bpy.context.object.modifiers['Displace']; displace.strength = 0.5; displace.direction = 'NORMAL'",
  "description": "使用置换修改器创建浮雕效果",
  "warnings": ["需要纹理贴图以获得最佳效果"]
}
```

### 示例 4：低多边形风格

**输入**：
```bash
python3 scripts/generate_command.py --modification "改为低多边形风格"
```

**输出**：
```json
{
  "blender_command": "bpy.ops.object.modifier_add(type='DECIMATE'); decimate = bpy.context.object.modifiers['Decimate']; decimate.ratio = 0.1",
  "description": "使用减面修改器创建低多边形效果，保留 10% 的面"
}
```

### 示例 5：更改材质颜色

**输入**：
```bash
python3 scripts/generate_command.py --modification "改为红色金属材质"
```

**输出**：
```json
{
  "blender_command": "mat = bpy.data.materials.new(name='RedMetal'); mat.use_nodes = True; bsdf = mat.node_tree.nodes['Principled BSDF']; bsdf.inputs['Base Color'].default_value = (1, 0, 0, 1); bsdf.inputs['Metallic'].default_value = 1.0; bsdf.inputs['Roughness'].default_value = 0.2; obj = bpy.context.object; obj.data.materials.append(mat)",
  "description": "创建红色金属材质并应用到模型"
}
```

## 核心脚本

- `scripts/generate_command.py` — 主脚本，解析输入并生成 Blender 命令
- `scripts/command_templates.py` — 命令模板库
- `scripts/execute_blender.py` — 执行 Blender 命令（可选）

## 依赖

- Python 3.7+
- Blender 3.0+（执行命令时需要）

## 环境变量

| 变量 | 说明 |
|------|------|
| `BLENDER_PATH` | Blender 可执行路径（默认：blender） |

## 安全注意事项

⚠️ **重要**：生成的 Blender 命令应在沙箱环境中执行

1. **代码审查**：执行前审查生成的 Python 代码
2. **文件访问限制**：限制 Blender 脚本的文件访问权限
3. **超时限制**：设置合理的执行超时时间
4. **资源限制**：限制内存和 CPU 使用

## 与自动建模工作流集成

```bash
# 1. 生成 3D 模型
python3 ~/.openclaw/workspace/skills/auto-modeling-workflow/scripts/workflow.py \
  --prompt "耳机充电盒" \
  --output /tmp/model.glb

# 2. 生成修改命令
python3 ~/.openclaw/workspace/skills/blender-command-generator/scripts/generate_command.py \
  --modification "添加皮卡丘浮雕" \
  --input-model /tmp/model.glb

# 3. 执行修改
blender --background --python-expr "{{generated_command}}"
```
