# Todo API 服务

简单的待办事项 REST API 服务，基于 Flask 和 SQLite。

## 技术栈

- **框架**: Flask 2.3.3
- **数据库**: SQLite
- **Python**: 3.8+

## 项目结构

```
code/todo-api/
├── app.py              # Flask 应用入口
├── models.py           # 数据模型和数据库操作
├── routes.py           # API 路由定义
├── requirements.txt    # Python 依赖
└── README.md          # 本文档
```

## 快速开始

### 1. 安装依赖

```bash
cd code/todo-api
pip install -r requirements.txt
```

### 2. 运行服务

```bash
python app.py
```

服务将在 `http://localhost:5000` 启动。

## API 端点

### 获取所有待办事项
```bash
GET /todos
```

### 获取单个待办事项
```bash
GET /todos/<id>
```

### 创建待办事项
```bash
POST /todos
Content-Type: application/json

{
  "title": "完成任务",
  "description": "描述内容",
  "completed": false
}
```

### 更新待办事项
```bash
PUT /todos/<id>
Content-Type: application/json

{
  "title": "新标题",
  "completed": true
}
```

### 删除待办事项
```bash
DELETE /todos/<id>
```

## 数据模型

```json
{
  "id": 1,
  "title": "完成任务",
  "description": "描述内容",
  "completed": false,
  "created_at": "2026-03-10T08:00:00Z"
}
```

## 测试示例

使用 curl 测试：

```bash
# 创建待办事项
curl -X POST http://localhost:5000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "学习 Flask", "description": "完成教程"}'

# 获取所有
curl http://localhost:5000/todos

# 获取单个
curl http://localhost:5000/todos/1

# 更新
curl -X PUT http://localhost:5000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'

# 删除
curl -X DELETE http://localhost:5000/todos/1
```
