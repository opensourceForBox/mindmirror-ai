# 开发任务：待办事项 API 服务

## 项目概述
创建一个简单的待办事项（Todo）REST API 服务，支持基本的 CRUD 操作。

## 技术栈
- **框架**: Flask
- **存储**: SQLite（轻量级，无需额外配置）
- **Python 版本**: 3.8+

## 功能需求

### API 端点
1. `GET /todos` - 获取所有待办事项
2. `GET /todos/<id>` - 获取单个待办事项
3. `POST /todos` - 创建新待办事项
4. `PUT /todos/<id>` - 更新待办事项
5. `DELETE /todos/<id>` - 删除待办事项

### 数据模型
```json
{
  "id": 1,
  "title": "完成任务",
  "description": "描述内容",
  "completed": false,
  "created_at": "2026-03-10T08:00:00Z"
}
```

## 开发要求

### 使用 Claude Code 模式
```bash
claude --model qwen3.5-plus "实现 Todo API 服务" --permission-mode acceptEdits
```

### 模型选择
- **推荐模型**: `qwen3.5-plus`（日常 CRUD 任务，性价比最高）

### 输出目录
```
code/todo-api/
├── app.py              # Flask 应用入口
├── models.py           # 数据模型
├── routes.py           # API 路由
├── requirements.txt    # Python 依赖
└── README.md          # 运行说明
```

## 验收标准
- [ ] 所有 API 端点正常工作
- [ ] 包含基本的错误处理
- [ ] 提供运行说明文档
- [ ] 代码有基本注释

## 通知
完成后通知 Manager。
