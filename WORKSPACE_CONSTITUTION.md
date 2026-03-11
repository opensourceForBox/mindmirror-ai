# 工作区宪法 - AI 开发团队

## 团队成员

### 1. 产品经理 (product-manager)
- **技能**: `product-manager` (位于 `/root/.openclaw/agents/product-manager/`)
- **触发条件**:
  - `on_message`: 当飞书消息包含 ["需求", "做一个", "开发", "产品", "帮我"] 等关键词时
- **输出目录**: `prd/`
- **通知**: ui-designer, developer

### 2. UI设计师 (ui-designer)
- **技能**: `ui-designer` (位于 `/root/.openclaw/agents/ui-designer/`)
- **触发条件**:
  - `on_file_change`: 监听 `prd/` 目录下的新文件
- **输出目录**: `designs/`
- **通知**: developer

### 3. 开发架构师 (developer)
- **技能**: `developer` (位于 `/root/.openclaw/agents/developer/`)
- **触发条件**:
  - `on_file_change`: 监听 `designs/` 目录下的新文件
- **输出目录**: `code/`
- **通知**: tester

### 4. 测试工程师 (tester)
- **技能**: `tester` (位于 `/root/.openclaw/agents/tester/`)
- **触发条件**:
  - `on_file_change`: 监听 `code/` 目录下的新文件
- **输出目录**: `test-reports/`
- **通知**: (测试完成后，可由飞书主动反馈结果)

## 记忆与共享

- 所有输出目录均为 `/root/.openclaw/workspace/` 下的子目录。
- 环境变量从 `/root/.openclaw/.env` 读取。
- 每日会话记录自动保存在 `memory/`。

---
*这是AI开发团队的工作流程宪法，定义了团队成员角色、协作机制和共享规范*