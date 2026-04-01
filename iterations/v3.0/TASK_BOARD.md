# 第 3 周任务看板 - 基础设施搭建阶段

**更新时间**: 2026-04-01  
**阶段**: 第一阶段（基础搭建）- 第 3 周  
**状态**: 🟡 待启动

---

## 任务概览

| 任务 | 负责人 | 模型 | 状态 | 交付物 | 截止时间 |
|------|--------|------|------|--------|---------|
| 01-后端微服务框架搭建 | backend-architect | qwencode/glm-5 | ⚪ 待启动 | 基础服务代码 | 第 3 周末 |
| 02-Android 项目初始化 | frontend-developer | qwencode/kimi-k2.5 | ⚪ 待启动 | 项目骨架、基础组件 | 第 3 周末 |
| 03-模型训练环境准备 | ml-ops-engineer | qwencode/glm-5 | ⚪ 待启动 | GPU 集群、训练管道 | 第 3 周末 |
| 04-数据采集方案设计 | data-engineer | qwencode/qwen3.5-plus | ⚪ 待启动 | 数据标注规范 | 第 3 周末 |
| 05-测试框架搭建 | qa-automation-engineer | qwencode/qwen3.5-plus | ⚪ 待启动 | 自动化测试框架 | 第 3 周末 |

---

## 任务详情

### 任务 01: 后端微服务框架搭建
**负责人**: backend-architect  
**模型**: `qwencode/glm-5` (复杂后端)  
**输入**: ARCHITECTURE.md, DATABASE_DESIGN.md, API_SPEC.md  
**输出**: `/root/.openclaw/workspace/code/mindmirror/backend/`  
**验收标准**: 
- [ ] NestJS 项目骨架
- [ ] 7 个微服务模块（auth, emotion, chat, cbt, crisis, user, notification）
- [ ] PostgreSQL 连接配置 + TypeORM/Prisma 集成
- [ ] Redis 缓存集成
- [ ] JWT 认证中间件
- [ ] 基础 CRUD 服务

---

### 任务 02: Android 项目初始化
**负责人**: frontend-developer  
**模型**: `qwencode/kimi-k2.5` (UI/前端)  
**输入**: ARCHITECTURE.md, UI_PROTOTYPES/  
**输出**: `/root/.openclaw/workspace/code/mindmirror/android/`  
**验收标准**: 
- [ ] Android Studio 项目骨架（Kotlin + Jetpack Compose）
- [ ] CameraX 集成
- [ ] 基础 UI 组件库（Button, Card, TextField 等）
- [ ] 导航框架（Navigation Compose）
- [ ] 网络层（Retrofit + WebSocket）
- [ ] 本地存储（Room + DataStore）

---

### 任务 03: 模型训练环境准备
**负责人**: ml-ops-engineer  
**模型**: `qwencode/glm-5` (复杂后端)  
**输入**: EMOTION_RECOGNITION_TECH.md  
**输出**: `/root/.openclaw/workspace/code/mindmirror/ml-pipeline/`  
**验收标准**: 
- [ ] GPU 服务器配置文档
- [ ] Docker 镜像（PyTorch + CUDA）
- [ ] 训练脚本骨架
- [ ] 数据加载管道
- [ ] 模型评估脚本
- [ ] 模型导出脚本（ONNX/TensorRT）

---

### 任务 04: 数据采集方案设计
**负责人**: data-engineer  
**模型**: `qwencode/qwen3.5-plus` (日常任务)  
**输入**: EMOTION_RECOGNITION_TECH.md, PRD_v1.0.md  
**输出**: `/root/.openclaw/workspace/prd/mindmirror/DATA_COLLECTION_PLAN.md`  
**验收标准**: 
- [ ] 数据标注规范文档
- [ ] 标注工具选型（CVAT / Label Studio）
- [ ] 数据质量控制流程
- [ ] 隐私保护方案（脱敏、匿名化）
- [ ] 数据集版本管理策略

---

### 任务 05: 测试框架搭建
**负责人**: qa-automation-engineer  
**模型**: `qwencode/qwen3.5-plus` (日常任务)  
**输入**: API_SPEC.md, ARCHITECTURE.md  
**输出**: `/root/.openclaw/workspace/code/mindmirror/tests/`  
**验收标准**: 
- [ ] 单元测试框架（Jest + Supertest）
- [ ] E2E 测试框架（Playwright）
- [ ] 性能测试框架（k6）
- [ ] CI/CD 集成配置
- [ ] 测试覆盖率报告模板

---

## 里程碑

| 里程碑 | 计划时间 | 状态 |
|--------|----------|------|
| M1: 架构冻结 | 第 3 周末 | 🟡 本周验收 |

---

## 依赖关系

```
任务 01 (后端) ← 依赖 → 任务 05 (测试)
       ↓
任务 02 (Android) ← 依赖 → 任务 01 (API)
       ↓
任务 03 (ML) ← 依赖 → 任务 04 (数据)
```

---

## 风险与应对

| 风险 | 影响 | 应对 |
|------|------|------|
| GPU 服务器采购延迟 | 高 | 先用云端 GPU（AutoDL/阿里云） |
| Android 开发人力不足 | 中 | 调整优先级，先完成核心界面 |
| 数据标注进度慢 | 中 | 使用公开数据集 + 众包标注 |

---

*创建时间：2026-04-01*
