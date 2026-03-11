# 开发任务描述 - Todo API

## 任务目标
使用 Claude Code 实现 Flask Todo API 服务

## 输入文档
- PRD: `prd/todo-api/todo-api_prd.md`
- 架构：`prd/todo-api/ARCHITECTURE.md`
- 规范：`prd/todo-api/.cloude/settings.mdc`

## 执行方式
使用 Claude Code CLI 执行开发：
```bash
claude "根据任务描述实现 Todo API" --permission-mode acceptEdits
```

## 输出要求
- 目录：`/root/.openclaw/workspace/code/todo-api/`
- 文件：app.py, models.py, routes.py, requirements.txt, README.md

## 验收标准
- 项目可直接运行
- API 端点正常工作
- 代码有注释
