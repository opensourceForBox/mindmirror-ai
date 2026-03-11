# 开发任务描述 - 天气查询 API

## 任务目标
使用 Claude Code 实现 Flask 天气查询 API 服务

## 输入文档
- PRD: `prd/weather-api/weather-api_prd.md`
- 架构：`prd/weather-api/ARCHITECTURE.md`
- 规范：`prd/weather-api/.cloude/settings.mdc`

## 模型配置
- **推荐模型**: `qwen3.5-plus`
- **理由**: 日常 CRUD 任务，性价比最高
- **调用命令**: `claude --model qwen3.5-plus "根据任务实现..." --permission-mode acceptEdits`

## 输出要求
- 目录：`/root/.openclaw/workspace/code/weather-api/`
- 文件清单：
  - app.py - Flask 应用入口
  - models.py - 数据模型（Weather, Forecast）
  - routes.py - API 路由（/weather, /forecast, /cities）
  - mock_data.py - 模拟天气数据
  - requirements.txt - Python 依赖
  - README.md - 运行说明

## 验收标准
- 项目可直接运行（`python app.py`）
- 所有 API 端点可正常访问
- 返回 JSON 格式数据
- README 包含清晰的启动和测试说明
