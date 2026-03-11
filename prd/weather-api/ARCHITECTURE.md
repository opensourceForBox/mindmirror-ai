# 系统架构设计 - 天气查询 API

## 技术栈选型
- **后端框架**: Flask 3.x
- **数据存储**: 内存字典（模拟数据）
- **API 风格**: RESTful JSON

## 系统架构图
```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Client    │────▶│  Flask App   │────▶│  Mock Data  │
│  (HTTP)     │     │  (REST API)  │     │  (In-Memory)│
└─────────────┘     └──────────────┘     └─────────────┘
```

## 模块划分

### 目录结构
```
code/weather-api/
├── app.py              # Flask 应用入口
├── models.py           # 数据模型（Weather, Forecast）
├── routes.py           # API 路由
├── mock_data.py        # 模拟天气数据
├── requirements.txt    # Python 依赖
└── README.md           # 运行说明
```

### API 端点
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /weather?city=xxx | 查询当前天气 |
| GET | /forecast?city=xxx | 查询 3 天预报 |
| GET | /cities | 获取支持的城市列表 |

## 数据模型

### Weather（当前天气）
| 字段 | 类型 | 说明 |
|------|------|------|
| city | String | 城市名 |
| temperature | Float | 温度（摄氏度） |
| condition | String | 天气状况（晴/雨/云等） |
| humidity | Integer | 湿度（%） |
| updated_at | DateTime | 更新时间 |

### Forecast（天气预报）
| 字段 | 类型 | 说明 |
|------|------|------|
| city | String | 城市名 |
| forecasts | Array | 3 天预报列表 |

## 部署方案
- 本地开发：`python app.py`

## 版本
v1.0.0 - 初始版本
