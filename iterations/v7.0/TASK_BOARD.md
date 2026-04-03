# 第 7 周任务看板 - CBT 干预模块

**更新时间**: 2026-04-01  
**阶段**: 第二阶段（核心功能开发）- 第 7 周 - CBT 干预模块  
**状态**: 🟡 进行中

---

## 任务概览

| 任务 | 负责人 | 模型 | 状态 | 交付物 | 截止时间 |
|------|--------|------|------|--------|---------|
| 01-CBT 练习内容开发 | psychology-advisor | qwencode/qwen3.5-plus | ⚪ 进行中 | 10 个核心练习 | 第 7 周末 |
| 02-干预流程引擎 | backend-architect | qwencode/glm-5 | ⚪ 进行中 | 流程引擎代码 | 第 7 周末 |
| 03-练习 UI 组件 | frontend-developer | qwencode/kimi-k2.5 | ⚪ 进行中 | 交互组件库 | 第 7 周末 |
| 04-进度跟踪系统 | data-engineer | qwencode/qwen3.5-plus | ⚪ 进行中 | 用户进度数据模型 | 第 7 周末 |

---

## 任务详情

### 任务 01: CBT 练习内容开发
**负责人**: psychology-advisor  
**模型**: `qwencode/qwen3.5-plus` (日常任务)  
**输入**: CBT_FRAMEWORK.md, THERAPY_TECHNIQUES.md  
**输出**: `/root/.openclaw/workspace/prd/mindmirror/CBT_EXERCISES.md`  
**验收标准**: 
- [ ] 10 个核心 CBT 练习完整内容
- [ ] 每个练习包含：目标、步骤、指导语、示例、时长
- [ ] 练习难度分级（初级/中级/高级）
- [ ] 与情绪状态映射关系
- [ ] 练习效果评估问题

---

### 任务 02: 干预流程引擎
**负责人**: backend-architect  
**模型**: `qwencode/glm-5` (复杂后端)  
**输入**: ARCHITECTURE.md, API_SPEC.md  
**输出**: `/root/.openclaw/workspace/code/mindmirror/backend/src/modules/cbt/`  
**验收标准**: 
- [ ] CBT 练习流程引擎（状态机）
- [ ] 练习推荐算法（基于情绪 + 历史）
- [ ] 进度跟踪 API（开始/完成/评分）
- [ ] 练习数据持久化
- [ ] 效果评估指标计算
- [ ] 完整的错误处理和日志

---

### 任务 03: 练习 UI 组件
**负责人**: frontend-developer  
**模型**: `qwencode/kimi-k2.5` (UI/前端)  
**输入**: UI_PROTOTYPES/CBT_EXERCISE_SCREEN.md  
**输出**: `/root/.openclaw/workspace/code/mindmirror/android/app/src/main/java/com/mindmirror/android/cbt/`  
**验收标准**: 
- [ ] 练习列表界面（卡片式展示）
- [ ] 练习详情界面（步骤引导）
- [ ] 练习进行界面（交互组件）
- [ ] 练习完成界面（反馈 + 评分）
- [ ] 进度统计界面（图表展示）
- [ ] 本地缓存（Room Database）
- [ ] 错误处理和重试机制

---

### 任务 04: 进度跟踪系统
**负责人**: data-engineer  
**模型**: `qwencode/qwen3.5-plus` (日常任务)  
**输入**: DATABASE_DESIGN.md  
**输出**: `/root/.openclaw/workspace/code/mindmirror/backend/src/modules/cbt/analytics/`  
**验收标准**: 
- [ ] 用户练习进度数据模型
- [ ] 练习完成率统计
- [ ] 情绪改善效果分析（练习前后对比）
- [ ] 连续练习天数统计
- [ ] 成就系统（徽章、里程碑）
- [ ] 数据可视化（图表数据接口）
- [ ] 隐私保护（数据脱敏）

---

## 里程碑

| 里程碑 | 计划时间 | 状态 |
|--------|----------|------|
| M4: CBT 模块完成 | 第 7 周末 | 🟡 本周验收 |

---

## 依赖关系

```
任务 01 (CBT 内容) → 被任务 02 和任务 03 依赖
       ↓
任务 02 (流程引擎) ← 依赖 → 任务 04 (进度跟踪)
       ↓
任务 03 (练习 UI) ← 依赖 → 任务 02 (API)
```

---

*创建时间：2026-04-01*
