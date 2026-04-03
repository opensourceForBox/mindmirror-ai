# 第 4 周任务看板 - 情绪识别模块（视频）

**更新时间**: 2026-04-01  
**阶段**: 第二阶段（核心功能开发）- 第 4 周  
**状态**: 🟡 待启动

---

## 任务概览

| 任务 | 负责人 | 模型 | 状态 | 交付物 | 截止时间 |
|------|--------|------|------|--------|---------|
| 01-面部表情识别模型集成 | ai-engineer | qwencode/glm-5 | ⚪ 待启动 | 表情识别 API | 第 4 周末 |
| 02-视频采集与预处理 | frontend-developer | qwencode/kimi-k2.5 | ⚪ 待启动 | 视频采集模块 | 第 4 周末 |
| 03-微表情特征提取 | data-engineer | qwencode/qwen3.5-plus | ⚪ 待启动 | 特征工程代码 | 第 4 周末 |
| 04-模型推理服务部署 | ml-ops-engineer | qwencode/glm-5 | ⚪ 待启动 | 推理服务 v1 | 第 4 周末 |

---

## 任务详情

### 任务 01: 面部表情识别模型集成
**负责人**: ai-engineer  
**模型**: `qwencode/glm-5` (复杂 AI 任务)  
**输入**: EMOTION_RECOGNITION_TECH.md  
**输出**: `/root/.openclaw/workspace/code/mindmirror/backend/src/modules/emotion/`  
**验收标准**: 
- [ ] 集成 Tavus Raven-1 或 DeepFace 模型
- [ ] 实现 POST /emotion/analyze 接口
- [ ] 支持 9 类情绪分类
- [ ] 置信度 ≥75%
- [ ] 推理延迟 <200ms

---

### 任务 02: 视频采集与预处理
**负责人**: frontend-developer  
**模型**: `qwencode/kimi-k2.5` (UI/前端)  
**输入**: CameraX 文档，UI_PROTOTYPES/  
**输出**: `/root/.openclaw/workspace/code/mindmirror/android/app/src/main/java/com/mindmirror/android/data/`  
**验收标准**: 
- [ ] CameraX 视频采集功能
- [ ] 帧采样（30fps → 5fps）
- [ ] ROI 裁剪（面部区域）
- [ ] 图像预处理（亮度、对比度）
- [ ] 上传到后端 API

---

### 任务 03: 微表情特征提取
**负责人**: data-engineer  
**模型**: `qwencode/qwen3.5-plus` (日常任务)  
**输入**: EMOTION_RECOGNITION_TECH.md  
**输出**: `/root/.openclaw/workspace/code/mindmirror/ml-pipeline/features/`  
**验收标准**: 
- [ ] 面部特征点提取（68 个关键点）
- [ ] 微表情特征（AU 动作单元）
- [ ] 特征工程代码
- [ ] 特征可视化脚本

---

### 任务 04: 模型推理服务部署
**负责人**: ml-ops-engineer  
**模型**: `qwencode/glm-5` (复杂技术)  
**输入**: EMOTION_RECOGNITION_TECH.md  
**输出**: `/root/.openclaw/workspace/code/mindmirror/ml-pipeline/infer/`  
**验收标准**: 
- [ ] FastAPI 推理服务
- [ ] 模型加载（ResNet3D-18）
- [ ] 批量推理支持
- [ ] 性能监控
- [ ] Docker 部署配置

---

## 里程碑

| 里程碑 | 计划时间 | 状态 |
|--------|----------|------|
| M2: 情绪识别完成 | 第 5 周末 | 🟡 进行中 |

---

## 依赖关系

```
任务 01 (后端 API) ← 依赖 → 任务 04 (推理服务)
       ↑
任务 02 (视频采集) ← 依赖 → 任务 03 (特征提取)
```

---

*创建时间：2026-04-01*
