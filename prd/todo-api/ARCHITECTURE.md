# 系统架构设计 - Todo API 服务

## 技术栈选型
- **后端框架**: Flask 3.x
- **数据库**: SQLite
- **ORM**: Flask-SQLAlchemy
- **API 风格**: RESTful JSON

## 系统架构图
```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Client    │────▶│  Flask App   │────▶│   SQLite    │
│  (HTTP)     │     │  (REST API)  │     │  (Database) │
└─────────────┘     └──────────────┘     └─────────────┘
```

## 模块划分

### 目录结构
```
code/todo-api/
├── app.py              # Flask 应用入口
├── models.py           # 数据模型（Todo）
├── routes.py           # API 路由
├── requirements.txt    # Python 依赖
└── README.md           # 运行说明
```

### 数据模型 - Todo
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键，自增 |
| title | String(200) | 待办事项标题 |
| completed | Boolean | 是否完成（默认 false） |
| created_at | DateTime | 创建时间 |

### API 端点
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /todos | 创建待办事项 |
| GET | /todos | 获取列表 |
| GET | /todos/<id> | 获取单个 |
| PUT | /todos/<id> | 更新待办事项 |
| DELETE | /todos/<id> | 删除待办事项 |

## 部署方案
- 本地开发：`python app.py`
- 生产环境：Gunicorn + Nginx（后续迭代）

## 版本
v1.0.0 - 初始版本
