# 架构设计任务 - 录像诊断功能

## 任务目标
作为产品 + 架构师，为"录像诊断功能"做详细的技术架构设计。

## 输出要求

### 1. 产品需求文档
- 文件：`prd/video-diagnosis/video-diagnosis_prd.md`
- 内容：用户故事、验收标准、业务规则

### 2. 技术架构设计
- 文件：`prd/video-diagnosis/ARCHITECTURE.md`
- 内容：
  - 系统架构图
  - 模块划分（上传、分析、存储、API）
  - 数据流设计
  - 技术栈选型

### 3. Claude Code 规范
- 文件：`prd/video-diagnosis/.cloude/settings.mdc`
- 内容：开发规范、代码风格、模型推荐

### 4. 任务拆解建议
- 文件：`prd/video-diagnosis/task-dev.md`
- 内容：给 Developer Worker 的详细技术任务

## 推荐模型
- **模型**: `glm-5`
- **理由**: 复杂系统架构设计，需要高逻辑一致性

## 验收标准
- PRD 包含完整的用户故事和验收标准
- 架构设计包含清晰的模块划分和接口定义
- 技术选型合理（视频处理库、存储方案等）
- 任务拆解足够详细，Developer 可直接执行
