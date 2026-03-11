# 用户确认流程

## 设计原则

**前期设计必须让用户确认后再动手** ✅

## 确认点

### 确认点 1：架构设计完成后

**时机**: product-manager 完成 PRD 和架构设计

**Manager 输出**:
```
📋 请确认架构设计

## PRD 摘要
- 功能：录像诊断功能
- 用户故事：3 个
- 验收标准：5 个

## 技术架构
- 后端：Flask 3.x + ffmpeg-python
- 前端：HTML/CSS/JS（响应式）
- 存储：本地临时目录

## 文件位置
- PRD: prd/video-diagnosis/video-diagnosis_prd.md
- 架构：prd/video-diagnosis/ARCHITECTURE.md

请回复"确认"开始任务拆解，或提出修改意见。
```

**用户操作**:
- ✅ 回复"确认" → 进入下一阶段
- ❌ 提出修改 → product-manager 重新设计

---

### 确认点 2：任务拆解后

**时机**: Manager 创建完 Worker 任务文件

**Manager 输出**:
```
📋 请确认任务拆解

## UI 任务
- 页面：上传页、结果页、历史页
- 模型：kimi-k2.5
- 交付：designs/video-diagnosis/

## 开发任务
- API：4 个端点
- 诊断规则：5 种问题检测
- 模型：glm-5
- 交付：code/video-diagnosis/

## 测试任务
- API 测试 + 边界用例
- 模型：qwen3.5-plus
- 交付：test-reports/video-diagnosis/

请回复"确认"开始执行，或提出修改意见。
```

**用户操作**:
- ✅ 回复"确认" → spawn Workers
- ❌ 提出修改 → Manager 调整任务

---

### 确认点 3：交付物确认（可选）

**时机**: 所有 Worker 完成

**Manager 输出**:
```
📋 请确认交付物

## UI 设计
- ✅ upload.html, result.html, history.html
- ✅ style.css, app.js

## 后端代码
- ✅ app.py, models.py, routes.py, analyzer.py
- ✅ requirements.txt, README.md

## 测试报告
- ✅ test_api.py, test_report.md

请回复"确认"完成项目，或提出修改意见。
```

**用户操作**:
- ✅ 回复"确认" → 项目完成
- ❌ 提出修改 → 进入下一轮迭代（v1.1）

---

## 完整流程图

```
用户："开发录像诊断功能"
    ↓
📋 Manager spawn 📝 product-manager（架构设计）
    ↓
📝 product-manager 输出 PRD + 架构
    ↓
【确认点 1】📋 Manager 汇总，等待用户确认
    ├─ 用户"确认" → 继续
    └─ 用户"修改" → 📝 重新设计
    ↓
📋 Manager 创建 Worker 任务
    ↓
【确认点 2】📋 Manager 汇总，等待用户确认
    ├─ 用户"确认" → spawn Workers
    └─ 用户"修改" → 📋 调整任务
    ↓
🔧 UI Worker 执行 → designs/
    ↓
🔧 Developer Worker 执行 → code/
    ↓
🔧 Tester Worker 执行 → test-reports/
    ↓
【确认点 3】📋 Manager 汇总交付物，等待用户确认
    ├─ 用户"确认" → ✅ 项目完成
    └─ 用户"修改" → 🔄 进入 v1.1 迭代
```

---

## 确认记录

所有用户确认记录保存在：
```
iterations/v1.0/APPROVALS/
├── architecture-approval.md    # 架构设计确认
├── tasks-approval.md           # 任务拆解确认
└── deliverables-approval.md    # 交付物确认（可选）
```

**示例** (`architecture-approval.md`):
```markdown
# 架构设计确认记录

## 确认时间
2026-03-09 21:45

## 确认内容
- PRD: prd/video-diagnosis/video-diagnosis_prd.md
- 架构：prd/video-diagnosis/ARCHITECTURE.md

## 用户反馈
"确认，可以开始任务拆解"

## 状态
✅ 已确认
```

---

## 简单项目 vs 复杂项目

### 简单项目（如 Todo API）
```
用户："做一个 Todo API"
    ↓
📋 Manager 直接拆解任务
    ↓
【确认点】📋 Manager 汇总任务，等待用户确认
    ├─ 用户"确认" → spawn developer
    └─ 用户"修改" → 📋 调整任务
    ↓
🔧 Developer 执行 → code/
    ↓
✅ 完成
```

### 复杂项目（如录像诊断）
```
完整流程（3 个确认点）
```

---

## 好处

1. **避免返工**: 前期设计确认后再执行，减少后期修改
2. **用户掌控**: 每个关键节点用户都可以提出意见
3. **透明度高**: 用户清楚知道项目进展
4. **质量保证**: 多层确认保证交付质量

---

## 用户操作指南

**当 Manager 发送确认请求时**:

### 选项 A：确认
```
确认
```
或
```
没问题，开始执行
```

### 选项 B：提出修改
```
PRD 中需要增加批量上传功能
```
或
```
开发任务的 API 端点需要增加 DELETE 操作
```

### 选项 C：要求更多信息
```
想看一下详细的架构设计文档
```
Manager 会提供完整文档链接

---

## 总结

**核心原则**: 前期设计必须让用户确认后再动手

**确认点**:
1. 架构设计完成后
2. 任务拆解后
3. 交付物确认（可选）

**用户权利**:
- ✅ 确认通过
- ✅ 提出修改
- ✅ 要求更多信息
