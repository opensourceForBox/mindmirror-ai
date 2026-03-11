# 任务看板 - 录像诊断功能 v1.0

## 阶段 1：架构设计（等待用户确认）

| 任务 | Worker | 状态 | 交付物 | 推荐模型 | 备注 |
|------|--------|------|--------|---------|------|
| 架构设计 | product-manager | ✅ 完成 | prd/video-diagnosis/ | glm-5 | 等待用户确认 |

**【确认点 1】**: 请确认架构设计
- PRD: `prd/video-diagnosis/video-diagnosis_prd.md`
- 架构：`prd/video-diagnosis/ARCHITECTURE.md`
- 状态：⏳ 等待用户回复"确认"

---

## 阶段 2：Worker 执行（待确认）

| 任务 | Worker | 状态 | 交付物 | 推荐模型 | 依赖 |
|------|--------|------|--------|---------|------|
| UI 设计 | ui-designer | ⏳ 待确认 | designs/video-diagnosis/ | kimi-k2.5 | - |
| 后端 API | developer | ⏳ 待确认 | code/video-diagnosis/ | glm-5 | UI 设计 |
| 测试用例 | tester | ⏳ 待确认 | test-reports/video-diagnosis/ | qwen3.5-plus | 代码完成 |

**【确认点 2】**: 任务拆解待确认（架构确认后显示）

---

## 阶段 3：交付物确认（可选）

**【确认点 3】**: 交付物待确认（所有 Worker 完成后显示）

---

## 迭代信息
- **创建时间**: 2026-03-09
- **Manager**: 项目经理
- **当前阶段**: 阶段 1 - 等待用户确认
- **状态**: ⏳ 架构设计完成，等待用户确认

---

## 流程说明

```
阶段 1: product-manager 架构设计 ✅
  ├─ PRD（用户故事、验收标准）
  ├─ ARCHITECTURE.md（技术架构）
  ├─ .mdc 规范文件
  └─ task-dev.md（开发任务）
        ↓
【确认点 1】⏳ 用户确认中...
        ↓
阶段 2: Manager 拆解 Worker 任务
        ↓
【确认点 2】⏳ 用户确认
        ↓
阶段 3: Worker 执行（UI → Dev → Test）
        ↓
【确认点 3】⏳ 交付物确认（可选）
        ↓
阶段 4: 汇总交付物 → 用户
```

---

## 用户操作

**请回复**:
- "确认" → 开始任务拆解
- "需要修改 XX" → product-manager 重新设计
- "想看详细文档" → Manager 提供完整文档链接
