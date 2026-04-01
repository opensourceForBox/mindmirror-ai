# 🧠 MindMirror AI - 项目记忆

**记录时间**: 2026-03-24  
**项目文档**: `/root/.openclaw/workspace/MindMirror-AI-Development-Plan.md`

---

## 📌 项目核心信息

### 产品定位
- **名称**: MindMirror AI（心理镜像）
- **核心价值**: 多模态 AI 实时情绪理解 + 个性化心理支持
- **目标用户**: 轻度至中度焦虑/抑郁人群、需要情绪疏导的普通人
- **硬件**: Android 盒子（USB 摄像头）或手机

### 核心功能
1. 多模态情绪识别（视频 + 音频）
2. 实时心理对话
3. CBT 心理干预
4. 危机预警系统

### 开发周期
- **12 周 MVP**
- **当前阶段**: 待启动

---

## 🚀 项目启动流程（标准）

```
✅ 总协调器 (agents-orchestrator) 初始化
   ↓
✅ week1-planner 会话启动
   ↓
✅ 创建 4 个任务文件
   ↓
✅ 生成第 1 周周报
   ↓
✅ 更新总协调器汇总报告
```

---

## 👥 推荐参与 Agent

### 核心层
| Agent | 职责 |
|-------|------|
| `agents-orchestrator` | 总协调器 |
| `product-manager` | 产品规划与优先级 |
| `backend-architect` | 后端系统架构 |
| `ai-engineer` | AI 模型集成 |

### 支持层
| Agent | 职责 |
|-------|------|
| `ui-designer` | 界面视觉设计 |
| `ux-researcher` | 用户体验研究 |
| `security-engineer` | 安全与合规 |
| `technical-writer` | 文档与知识管理 |

---

## 📂 关键目录结构

```
/root/.openclaw/workspace/
├── MindMirror-AI-Development-Plan.md    # 完整开发计划
├── memory/
│   └── MindMirror-AI-Project.md         # 本文件（项目记忆）
├── code/
│   └── mindmirror/                      # 代码产出（待创建）
├── prd/
│   └── mindmirror/                      # 产品文档（待创建）
└── designs/
    └── mindmirror/                      # 设计稿（待创建）
```

---

## 📋 第 1 周任务概览

| 任务 | 负责人 | 交付物 |
|------|--------|--------|
| 需求评审与用户故事定义 | product-manager | PRD 文档 v1.0 |
| 技术栈选型与架构设计 | backend-architect | 架构设计文档 |
| 合规要求梳理（医疗数据） | security-engineer | 合规检查清单 |
| CBT 干预内容框架设计 | psychology-advisor | 干预内容大纲 |
| 项目环境初始化 | devops-automator | Git 仓库、CI/CD 流水线 |

---

## 🎯 关键里程碑

| 里程碑 | 时间 | 验收标准 |
|--------|------|----------|
| M1: 架构冻结 | 第 3 周末 | 技术方案评审通过 |
| M2: 情绪识别完成 | 第 5 周末 | 准确率≥75% |
| M3: 对话系统完成 | 第 6 周末 | 响应延迟<500ms |
| M4: CBT 模块完成 | 第 7 周末 | 心理学专家验收 |
| M5: 危机预警完成 | 第 8 周末 | 召回率≥90% |
| M6: MVP 发布 | 第 12 周末 | 通过安全审计、性能达标 |

---

## ⚠️ 重要注意事项

### 合规风险（极高优先级）
- 医疗数据合规问题
- 隐私保护要求
- 危机干预责任边界

### 技术风险
- 情绪识别准确率不达标 → 预留 2 周优化时间
- 实时对话延迟过高 → 边缘计算 + 模型蒸馏
- 12 周时间紧张 → 严格优先级管理

---

## 🔗 相关配置

### 推荐模型
- **日常任务**: `qwencode/qwen3.5-plus`
- **复杂后端**: `qwencode/glm-5`
- **UI/前端**: `qwencode/kimi-k2.5`

### 会话目标
- 使用 `sessions_spawn` 创建独立会话
- 会话记录保存在 `memory/` 目录

---

*此文件用于快速回忆项目上下文，避免每次重新阅读完整开发计划*
