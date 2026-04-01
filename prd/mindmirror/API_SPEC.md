# MindMirror AI - API 规范文档 (OpenAPI 3.0)

**版本**: v1.0  
**日期**: 2026-03-24  
**负责人**: backend-architect  
**状态**: ✅ 已完成

---

## 1. API 概述

### 1.1 基础信息

- **Base URL**: `https://api.mindmirror.ai/v1`
- **认证方式**: JWT Bearer Token
- **数据格式**: JSON (UTF-8)
- **API 版本**: v1

### 1.2 认证机制

#### JWT Token 结构
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
{
  "sub": "user_uuid",
  "iat": 1234567890,
  "exp": 1234571490,
  "type": "access"
}
```

#### Token 获取流程
1. 用户登录 → 获取 `access_token` (15 分钟) + `refresh_token` (7 天)
2. access_token 过期 → 使用 refresh_token 刷新
3. refresh_token 过期 → 重新登录

#### 请求头示例
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

### 1.3 通用响应格式

#### 成功响应
```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "request_id": "req_xxx",
    "timestamp": "2026-03-24T11:00:00Z"
  }
}
```

#### 错误响应
```json
{
  "success": false,
  "error": {
    "code": "INVALID_REQUEST",
    "message": "请求参数无效",
    "details": [
      {
        "field": "phone",
        "message": "手机号格式不正确"
      }
    ]
  },
  "meta": {
    "request_id": "req_xxx",
    "timestamp": "2026-03-24T11:00:00Z"
  }
}
```

### 1.4 通用错误码

| 错误码 | HTTP 状态码 | 说明 |
|--------|-----------|------|
| SUCCESS | 200 | 成功 |
| INVALID_REQUEST | 400 | 请求参数无效 |
| UNAUTHORIZED | 401 | 未认证或 Token 过期 |
| FORBIDDEN | 403 | 无权限访问 |
| NOT_FOUND | 404 | 资源不存在 |
| CONFLICT | 409 | 资源冲突（如手机号已注册） |
| RATE_LIMITED | 429 | 请求频率超限 |
| INTERNAL_ERROR | 500 | 服务器内部错误 |
| SERVICE_UNAVAILABLE | 503 | 服务不可用 |

---

## 2. 认证模块 (Authentication)

### 2.1 发送验证码

**POST** `/auth/send-code`

发送手机验证码

**请求参数**:
```json
{
  "phone": "+8613800138000"
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "expire_in": 300,
    "retry_after": 60
  }
}
```

**错误码**:
- `INVALID_PHONE`: 手机号格式错误
- `RATE_LIMITED`: 发送频率过高

---

### 2.2 用户注册

**POST** `/auth/register`

新用户注册

**请求参数**:
```json
{
  "phone": "+8613800138000",
  "code": "123456",
  "password": "SecurePass123!",
  "nickname": "小明",
  "age_range": "25-34",
  "gender": "male"
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "user_id": "usr_abc123",
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_in": 900,
    "token_type": "Bearer"
  }
}
```

**错误码**:
- `CODE_EXPIRED`: 验证码已过期
- `CODE_INVALID`: 验证码错误
- `PHONE_REGISTERED`: 手机号已注册

---

### 2.3 用户登录

**POST** `/auth/login`

用户登录

**请求参数**:
```json
{
  "phone": "+8613800138000",
  "code": "123456"
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "user_id": "usr_abc123",
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_in": 900,
    "token_type": "Bearer"
  }
}
```

**错误码**:
- `USER_NOT_FOUND`: 用户不存在
- `CODE_EXPIRED`: 验证码已过期
- `CODE_INVALID`: 验证码错误

---

### 2.4 刷新 Token

**POST** `/auth/refresh`

使用 refresh_token 刷新 access_token

**请求参数**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_in": 900,
    "token_type": "Bearer"
  }
}
```

**错误码**:
- `TOKEN_EXPIRED`: refresh_token 已过期
- `TOKEN_INVALID`: refresh_token 无效
- `TOKEN_REVOKED`: refresh_token 已撤销

---

### 2.5 登出

**POST** `/auth/logout`

用户登出（撤销 token）

**请求头**: `Authorization: Bearer ...`

**请求参数**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**响应示例**:
```json
{
  "success": true,
  "data": null
}
```

---

## 3. 情绪识别模块 (Emotion)

### 3.1 情绪分析

**POST** `/emotion/analyze`

分析用户上传的视频/音频帧的情绪状态

**请求头**: `Authorization: Bearer ...`

**请求参数** (multipart/form-data):
```
video_frame: [binary] (可选)
audio_chunk: [binary] (可选)
timestamp: 1234567890 (可选)
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "analysis_id": "emo_xyz789",
    "emotion_type": "anxious",
    "confidence": 0.87,
    "valence": -0.4,
    "arousal": 0.7,
    "emotions": [
      { "type": "anxious", "score": 0.87 },
      { "type": "sad", "score": 0.45 },
      { "type": "neutral", "score": 0.23 }
    ],
    "video_analysis": {
      "facial_expression": "tensed",
      "eye_contact": "avoidant"
    },
    "audio_analysis": {
      "pitch_variance": 0.6,
      "speech_rate": "fast",
      "volume_level": "high"
    },
    "timestamp": "2026-03-24T11:00:00Z"
  }
}
```

**错误码**:
- `INVALID_MEDIA`: 媒体格式不支持
- `MEDIA_TOO_LARGE`: 文件过大

---

### 3.2 获取情绪历史

**GET** `/emotion/history`

获取用户情绪历史记录

**请求头**: `Authorization: Bearer ...`

**查询参数**:
```
start_date: 2026-03-01 (可选)
end_date: 2026-03-24 (可选)
limit: 50 (可选，默认 50，最大 200)
cursor: xxx (分页游标，可选)
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "records": [
      {
        "analysis_id": "emo_xyz789",
        "emotion_type": "anxious",
        "confidence": 0.87,
        "valence": -0.4,
        "arousal": 0.7,
        "timestamp": "2026-03-24T11:00:00Z"
      }
    ],
    "pagination": {
      "next_cursor": "abc123",
      "has_more": true
    },
    "summary": {
      "dominant_emotion": "anxious",
      "average_valence": -0.3,
      "average_arousal": 0.6,
      "total_records": 150
    }
  }
}
```

---

### 3.3 获取情绪趋势

**GET** `/emotion/trend`

获取用户情绪趋势统计

**请求头**: `Authorization: Bearer ...`

**查询参数**:
```
period: day|week|month (默认 week)
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "period": "week",
    "trend": [
      {
        "date": "2026-03-18",
        "dominant_emotion": "neutral",
        "average_valence": 0.1,
        "average_arousal": 0.4
      },
      {
        "date": "2026-03-19",
        "dominant_emotion": "happy",
        "average_valence": 0.5,
        "average_arousal": 0.6
      }
    ],
    "insights": [
      "本周情绪整体较为平稳",
      "周三情绪最为积极"
    ]
  }
}
```

---

## 4. 对话模块 (Chat)

### 4.1 发送消息

**POST** `/chat/message`

发送一条消息并获取回复

**请求头**: `Authorization: Bearer ...`

**请求参数**:
```json
{
  "conversation_id": "conv_abc123", (可选，新建会话时不传)
  "content": "我今天感觉不太好...",
  "emotion_state": {
    "emotion_type": "sad",
    "confidence": 0.8
  } (可选)
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "conversation_id": "conv_abc123",
    "message_id": "msg_xyz789",
    "response": {
      "role": "assistant",
      "content": "我听到你说感觉不太好，能具体说说是什么让你有这种感觉吗？",
      "emotion_detected": "sad",
      "suggested_action": "active_listening"
    },
    "metadata": {
      "model_used": "glm-5",
      "tokens_used": 150,
      "latency_ms": 320
    }
  }
}
```

**错误码**:
- `INVALID_CONTENT`: 消息内容无效
- `CONVERSATION_NOT_FOUND`: 会话不存在

---

### 4.2 创建会话

**POST** `/chat/conversation`

创建新的对话会话

**请求头**: `Authorization: Bearer ...`

**请求参数**:
```json
{
  "title": "晚间倾诉", (可选)
  "tags": ["mood", "anxiety"] (可选)
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "conversation_id": "conv_abc123",
    "title": "晚间倾诉",
    "created_at": "2026-03-24T11:00:00Z"
  }
}
```

---

### 4.3 获取会话列表

**GET** `/chat/conversations`

获取用户的对话会话列表

**请求头**: `Authorization: Bearer ...`

**查询参数**:
```
limit: 20 (可选)
cursor: xxx (可选)
status: active|archived (可选)
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "conversations": [
      {
        "conversation_id": "conv_abc123",
        "title": "晚间倾诉",
        "message_count": 15,
        "last_message_at": "2026-03-24T11:00:00Z",
        "status": "active"
      }
    ],
    "pagination": {
      "next_cursor": "abc123",
      "has_more": true
    }
  }
}
```

---

### 4.4 流式对话 (WebSocket)

**WS** `/chat/stream`

建立 WebSocket 连接进行流式对话

**连接参数**:
```
?token=eyJhbGciOiJIUzI1NiIs...
&conversation_id=conv_abc123 (可选)
```

**客户端发送消息**:
```json
{
  "type": "message",
  "content": "我今天感觉不太好..."
}
```

**服务端响应** (流式):
```json
{
  "type": "chunk",
  "content": "我听到",
  "is_final": false
}
{
  "type": "chunk",
  "content": "你说感觉不太好",
  "is_final": false
}
{
  "type": "complete",
  "content": "能具体说说是什么让你有这种感觉吗？",
  "message_id": "msg_xyz789",
  "metadata": {
    "model_used": "glm-5",
    "tokens_used": 150,
    "latency_ms": 320
  }
}
```

**服务端推送** (情绪检测):
```json
{
  "type": "emotion_update",
  "emotion_type": "sad",
  "confidence": 0.8
}
```

**错误响应**:
```json
{
  "type": "error",
  "code": "INVALID_MESSAGE",
  "message": "消息格式错误"
}
```

---

## 5. CBT 模块 (CBT Exercises)

### 5.1 获取练习列表

**GET** `/cbt/exercises`

获取可用的 CBT 练习列表

**请求头**: `Authorization: Bearer ...`

**查询参数**:
```
type: thought_record|behavioral_activation|... (可选)
recommended: true (可选，只获取推荐的)
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "exercises": [
      {
        "exercise_id": "cbt_001",
        "type": "thought_record",
        "title": "思维记录表",
        "description": "识别并记录自动负性思维",
        "estimated_duration": 600,
        "difficulty": "beginner",
        "completion_count": 5,
        "last_completed_at": "2026-03-20T10:00:00Z"
      }
    ],
    "recommended": ["cbt_001", "cbt_003"]
  }
}
```

---

### 5.2 获取练习详情

**GET** `/cbt/exercises/{exercise_id}`

获取单个练习的详细内容

**请求头**: `Authorization: Bearer ...`

**响应示例**:
```json
{
  "success": true,
  "data": {
    "exercise_id": "cbt_001",
    "type": "thought_record",
    "title": "思维记录表",
    "description": "识别并记录自动负性思维",
    "instructions": [
      "1. 描述触发情绪的情境",
      "2. 记录当时的自动思维",
      "3. 识别情绪类型和强度",
      "4. 寻找支持和不支持思维的证据",
      "5. 生成替代性思维"
    ],
    "questions": [
      {
        "id": "q1",
        "type": "text",
        "label": "情境描述",
        "placeholder": "发生了什么？"
      },
      {
        "id": "q2",
        "type": "text",
        "label": "自动思维",
        "placeholder": "你当时想到了什么？"
      }
    ],
    "estimated_duration": 600
  }
}
```

---

### 5.3 提交练习

**POST** `/cbt/exercises/{exercise_id}/submit`

提交完成的练习

**请求头**: `Authorization: Bearer ...`

**请求参数**:
```json
{
  "answers": {
    "q1": "今天开会时我的建议被否定了",
    "q2": "我觉得自己的能力不够，永远做不好",
    "q3": "悲伤 (8/10)",
    "q4": "证据：过去有成功的项目经验...",
    "q5": "这次建议被否定不代表我能力不行"
  },
  "mood_before": "sad",
  "mood_after": "neutral",
  "duration_seconds": 480
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "record_id": "cbt_rec_xyz",
    "feedback": {
      "summary": "你很好地识别了自动负性思维，并找到了替代性思维",
      "suggestions": [
        "继续练习认知重构技巧",
        "记录每天的小成就"
      ]
    },
    "progress": {
      "total_completed": 6,
      "this_week": 2,
      "streak_days": 3
    }
  }
}
```

---

### 5.4 获取练习进度

**GET** `/cbt/progress`

获取用户的 CBT 练习进度

**请求头**: `Authorization: Bearer ...`

**响应示例**:
```json
{
  "success": true,
  "data": {
    "total_completed": 15,
    "by_type": {
      "thought_record": 5,
      "behavioral_activation": 4,
      "cognitive_restructuring": 3,
      "mindfulness": 3
    },
    "this_week": 3,
    "streak_days": 5,
    "mood_improvement": {
      "average_before": -0.4,
      "average_after": -0.1,
      "improvement_rate": 0.75
    },
    "achievements": [
      {
        "id": "first_exercise",
        "title": "第一次练习",
        "unlocked_at": "2026-03-15T10:00:00Z"
      }
    ]
  }
}
```

---

## 6. 危机预警模块 (Crisis)

### 6.1 危机检测

**POST** `/crisis/check`

检测当前消息/状态是否存在危机风险

**请求头**: `Authorization: Bearer ...`

**请求参数**:
```json
{
  "content": "我觉得活着没意思...",
  "emotion_state": {
    "emotion_type": "depressed",
    "confidence": 0.9
  },
  "context": "conversation" (可选)
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "risk_level": "high",
    "alert_type": "suicide_risk",
    "confidence": 0.85,
    "triggered_by": ["keyword", "emotion_threshold"],
    "recommended_actions": [
      "show_crisis_resources",
      "notify_emergency_contact",
      "suggest_professional_help"
    ],
    "resources": {
      "hotline": "400-161-9995",
      "text": "希望 24 热线"
    }
  }
}
```

---

### 6.2 获取危机资源

**GET** `/crisis/resources`

获取危机干预资源

**请求头**: `Authorization: Bearer ...`

**响应示例**:
```json
{
  "success": true,
  "data": {
    "hotlines": [
      {
        "name": "希望 24 热线",
        "phone": "400-161-9995",
        "hours": "24 小时",
        "type": "suicide_prevention"
      },
      {
        "name": "北京心理危机研究与干预中心",
        "phone": "010-82951332",
        "hours": "24 小时",
        "type": "crisis_intervention"
      }
    ],
    "emergency_contacts": [
      {
        "name": "张三",
        "relationship": "家人",
        "phone": "138****0000"
      }
    ],
    "self_help": [
      {
        "title": "深呼吸练习",
        "duration": 180,
        "url": "/exercises/breathing"
      }
    ]
  }
}
```

---

### 6.3 设置紧急联系人

**POST** `/crisis/emergency-contact`

设置紧急联系人

**请求头**: `Authorization: Bearer ...`

**请求参数**:
```json
{
  "name": "张三",
  "relationship": "家人",
  "phone": "+8613800138000",
  "notify_on_high_risk": true
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "contact_id": "contact_abc",
    "created_at": "2026-03-24T11:00:00Z"
  }
}
```

---

### 6.4 获取预警历史

**GET** `/crisis/alerts`

获取用户的危机预警历史

**请求头**: `Authorization: Bearer ...`

**查询参数**:
```
limit: 20 (可选)
severity: low|medium|high|critical (可选)
resolved: true|false (可选)
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "alerts": [
      {
        "alert_id": "alert_xyz",
        "alert_type": "suicide_risk",
        "severity": "high",
        "trigger_reason": "检测到关键词'不想活了'",
        "created_at": "2026-03-20T15:00:00Z",
        "resolved": true,
        "resolved_at": "2026-03-20T15:30:00Z",
        "action_taken": "用户使用了深呼吸练习"
      }
    ],
    "pagination": {
      "next_cursor": "abc123",
      "has_more": false
    }
  }
}
```

---

## 7. 用户模块 (User)

### 7.1 获取个人信息

**GET** `/user/profile`

获取当前用户个人信息

**请求头**: `Authorization: Bearer ...`

**响应示例**:
```json
{
  "success": true,
  "data": {
    "user_id": "usr_abc123",
    "phone": "+86138****8000",
    "email": "user@example.com",
    "nickname": "小明",
    "age_range": "25-34",
    "gender": "male",
    "avatar_url": "https://...",
    "timezone": "Asia/Shanghai",
    "language": "zh-CN",
    "created_at": "2026-01-01T00:00:00Z"
  }
}
```

---

### 7.2 更新个人信息

**PATCH** `/user/profile`

更新用户个人信息

**请求头**: `Authorization: Bearer ...`

**请求参数**:
```json
{
  "nickname": "小明 updated",
  "avatar_url": "https://...",
  "timezone": "Asia/Shanghai"
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "user_id": "usr_abc123",
    "updated_fields": ["nickname", "avatar_url"]
  }
}
```

---

### 7.3 获取用户设置

**GET** `/user/settings`

获取用户设置

**请求头**: `Authorization: Bearer ...`

**响应示例**:
```json
{
  "success": true,
  "data": {
    "notifications": {
      "push_enabled": true,
      "email_enabled": false,
      "reminder_time": "09:00"
    },
    "privacy": {
      "data_sharing": false,
      "analytics": true
    },
    "preferences": {
      "theme": "light",
      "font_size": "medium"
    }
  }
}
```

---

### 7.4 更新用户设置

**PATCH** `/user/settings`

更新用户设置

**请求头**: `Authorization: Bearer ...`

**请求参数**:
```json
{
  "notifications": {
    "push_enabled": false
  },
  "preferences": {
    "theme": "dark"
  }
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "updated_fields": ["notifications.push_enabled", "preferences.theme"]
  }
}
```

---

### 7.5 删除账号

**DELETE** `/user/account`

删除用户账号（软删除，30 天后硬删除）

**请求头**: `Authorization: Bearer ...`

**请求参数**:
```json
{
  "confirmation": "DELETE_MY_ACCOUNT",
  "reason": "不再需要服务"
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "deletion_scheduled_at": "2026-04-23T11:00:00Z",
    "grace_period_days": 30,
    "recovery_instructions": "30 天内登录可恢复账号"
  }
}
```

---

## 8. 限流策略

| 接口类别 | 限流规则 |
|----------|----------|
| 认证接口 | 5 次/分钟 (按手机号) |
| 情绪分析 | 30 次/分钟 (按用户) |
| 对话接口 | 60 次/分钟 (按用户) |
| CBT 练习 | 100 次/分钟 (按用户) |
| 危机检测 | 不限 (安全优先) |

**限流响应头**:
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1234567890
Retry-After: 60
```

---

## 9. WebSocket 事件类型

### 客户端 → 服务端

| 事件类型 | 说明 | 载荷 |
|----------|------|------|
| `message` | 发送消息 | `{ content: string }` |
| `emotion_update` | 上报情绪 | `{ emotion_type, confidence }` |
| `typing` | 正在输入 | `{ is_typing: boolean }` |
| `ping` | 心跳 | `{ timestamp: number }` |

### 服务端 → 客户端

| 事件类型 | 说明 | 载荷 |
|----------|------|------|
| `chunk` | 流式响应片段 | `{ content, is_final }` |
| `complete` | 响应完成 | `{ content, message_id, metadata }` |
| `emotion_update` | 情绪检测更新 | `{ emotion_type, confidence }` |
| `crisis_alert` | 危机预警 | `{ risk_level, actions }` |
| `error` | 错误 | `{ code, message }` |
| `pong` | 心跳响应 | `{ timestamp }` |

---

## 10. 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| v1.0 | 2026-03-24 | 初始版本，覆盖所有核心接口 |

---

*文档版本：1.0*  
*创建时间：2026-03-24*  
*负责人：backend-architect*  
*状态：✅ 已完成*
