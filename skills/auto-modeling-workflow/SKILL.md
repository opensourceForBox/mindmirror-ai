---
name: auto-modeling-workflow
description: >
  自动建模工作流，根据飞书消息触发，自动生成并修改 3D 模型。支持文生 3D、图生 3D，以及通过 Blender 进行后期修改。
---

# 自动建模工作流 Skill

## 功能描述

本 Skill 提供**端到端 3D 建模自动化**能力，从飞书消息触发，自动完成：
1. 解析用户意图和参数
2. 调用混元 3D 生成初始模型
3. 使用 Blender 进行后期修改（如需要）
4. 上传结果到飞书

## 工作流步骤

```
用户消息 → 参数解析 → 3D 生成 → Blender 修改 → 结果上传
```

## 触发条件

当用户消息包含以下关键词时自动触发：
- "生成模型"
- "建模"
- "3d 模型"
- "创建一个 3D"
- "帮我建模"

## 参数提取规则

| 参数 | 提取模式 | 说明 |
|------|----------|------|
| `model_description` | `生成 (.*?) 模型` | 模型描述 |
| `modification` | `修改为 (.*?)` | 修改需求 |
| `style` | `风格为 (.*?)` | 风格要求 |
| `image` | 飞书图片附件 | 参考图片（图生 3D） |

## Agent 执行指令

### 📌 步骤 1：解析飞书消息

从飞书消息中提取：
- 文本内容（用于参数提取）
- 图片附件（用于图生 3D）

### 📌 步骤 2：调用混元 3D 生成

```bash
# 文生 3D
python3 ~/.openclaw/workspace/skills/hy-3d-generation/scripts/main.py \
  --prompt "{{model_description}}，风格：{{style}}" \
  --model 3.1

# 图生 3D
python3 ~/.openclaw/workspace/skills/hy-3d-generation/scripts/main.py \
  --image-base64 "{{image_base64}}" \
  --model 3.1
```

### 📌 步骤 3：Blender 后期修改（可选）

如果用户有修改需求，调用 `blender-command-generator` 技能生成 Blender 命令：

```bash
# 生成 Blender 命令
python3 ~/.openclaw/workspace/skills/blender-command-generator/scripts/generate_command.py \
  --modification "{{modification}}" \
  --input-model "{{generated_model_path}}"

# 执行 Blender 命令
blender --background --python-expr "{{generated_command}}"
```

### 📌 步骤 4：上传结果到飞书

使用 `message` 工具上传生成的模型文件：

```yaml
action: send
media: "{{final_model_path}}"
message: "你的模型已生成完成！"
```

## 完整调用示例

### 示例 1：文生 3D

**用户消息**：
> 生成一个耳机充电盒模型，风格为简约现代

**执行流程**：
```bash
python3 ~/.openclaw/workspace/skills/auto-modeling-workflow/scripts/workflow.py \
  --prompt "耳机充电盒" \
  --style "简约现代"
```

### 示例 2：图生 3D + 修改

**用户消息**：
> 生成这个耳机的 3D 模型，修改为添加皮卡丘浮雕

**执行流程**：
```bash
python3 ~/.openclaw/workspace/skills/auto-modeling-workflow/scripts/workflow.py \
  --image-base64 "{{base64}}" \
  --modification "添加皮卡丘浮雕"
```

### 示例 3：完整参数

**用户消息**：
> 生成一个跑车模型，风格为赛博朋克，修改为低多边形风格

**执行流程**：
```bash
python3 ~/.openclaw/workspace/skills/auto-modeling-workflow/scripts/workflow.py \
  --prompt "跑车" \
  --style "赛博朋克" \
  --modification "低多边形风格"
```

## 核心脚本

- `scripts/workflow.py` — 主工作流脚本，协调各步骤
- `scripts/parse_message.py` — 解析飞书消息和参数
- `scripts/upload_feishu.py` — 上传结果到飞书

## 依赖

- Python 3.7+
- `hy-3d-generation` 技能
- `blender-command-generator` 技能
- Blender 3.0+（可选，用于后期修改）

## 环境变量

| 变量 | 说明 |
|------|------|
| `TENCENTCLOUD_SECRET_ID` | 腾讯云 API SecretId |
| `TENCENTCLOUD_SECRET_KEY` | 腾讯云 API SecretKey |
| `TENCENTCLOUD_REGION` | 腾讯云区域（国际站：ap-singapore） |
| `TENCENTCLOUD_ENDPOINT` | 腾讯云 endpoint（国际站：ai3d.ap-singapore.tencentcloudapi.com） |
| `FEISHU_APP_ID` | 飞书应用 ID |
| `FEISHU_APP_SECRET` | 飞书应用密钥 |

## 输出目录

- `/tmp/auto-modeling/` — 临时工作目录
- `/tmp/auto-modeling/generated/` — 生成的原始模型
- `/tmp/auto-modeling/modified/` — 修改后的最终模型

## 注意事项

1. **模型文件有效期**：混元 3D 生成的 URL 有效期为 24 小时，需及时下载
2. **Blender 命令安全**：生成的 Blender 命令需要审核后再执行
3. **文件大小限制**：飞书上传文件大小限制为 500MB
4. **处理时间**：3D 生成通常需要 2-5 分钟，Blender 修改视复杂度而定
