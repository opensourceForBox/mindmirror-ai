# Flask 天气 API

简单的天气查询 API 服务，提供中国主要城市的当前天气和 3 天天气预报数据。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行服务

```bash
python app.py
```

服务将在 http://127.0.0.1:5000 启动

## API 端点

### 获取城市列表

```bash
GET /api/cities
```

**响应示例:**
```json
{
    "success": true,
    "data": {
        "cities": ["北京", "上海", "广州", "深圳", "杭州"],
        "count": 5
    }
}
```

### 获取当前天气

```bash
GET /api/weather?city=北京
```

**参数:**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| city | string | 是 | 城市名称 |

**响应示例:**
```json
{
    "success": true,
    "data": {
        "city": "北京",
        "temperature": 15,
        "condition": "晴",
        "humidity": 45,
        "wind_speed": 12,
        "wind_direction": "西北",
        "aqi": 85
    }
}
```

### 获取天气预报

```bash
GET /api/forecast?city=上海
```

**参数:**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| city | string | 是 | 城市名称 |

**响应示例:**
```json
{
    "success": true,
    "data": [
        {
            "date": "2026-03-10",
            "high": 14,
            "low": 8,
            "condition": "多云"
        },
        {
            "date": "2026-03-11",
            "high": 16,
            "low": 10,
            "condition": "阴"
        },
        {
            "date": "2026-03-12",
            "high": 18,
            "low": 11,
            "condition": "小雨"
        }
    ]
}
```

## 使用 curl 测试

```bash
# 获取城市列表
curl http://127.0.0.1:5000/api/cities

# 查询北京天气
curl "http://127.0.0.1:5000/api/weather?city=北京"

# 查询上海预报
curl "http://127.0.0.1:5000/api/forecast?city=上海"

# 查询广州天气
curl "http://127.0.0.1:5000/api/weather?city=广州"

# 查询深圳预报
curl "http://127.0.0.1:5000/api/forecast?city=深圳"

# 查询杭州天气
curl "http://127.0.0.1:5000/api/weather?city=杭州"
```

## 错误响应

### 缺少城市参数 (400)
```json
{
    "success": false,
    "error": "缺少必要参数：city"
}
```

### 城市不存在 (404)
```json
{
    "success": false,
    "error": "未找到城市 'xxx' 的天气数据"
}
```

## 支持的城市

- 北京
- 上海
- 广州
- 深圳
- 杭州

## 项目结构

```
weather-api/
├── app.py          # Flask 应用入口
├── routes.py       # API 路由定义
├── models.py       # 数据模型类
├── mock_data.py    # 模拟天气数据
├── requirements.txt # Python 依赖
└── README.md       # 本文档
```

## 技术栈

- Python 3.10+
- Flask 3.x
