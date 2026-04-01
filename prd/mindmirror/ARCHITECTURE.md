# MindMirror AI - 系统架构设计文档

## 1. 技术栈选型

### 1.1 前端 (Android)
| 组件 | 技术选择 | 理由 |
|------|----------|------|
| 开发语言 | Kotlin | Android 官方推荐 |
| UI 框架 | Jetpack Compose | 声明式 UI，开发效率高 |
| 摄像头 | CameraX | 官方支持，兼容性好 |
| 音频处理 | Android AudioRecord | 低延迟音频采集 |
| 本地存储 | Room + DataStore | 结构化数据 + 配置存储 |

### 1.2 后端
| 组件 | 技术选择 | 理由 |
|------|----------|------|
| 运行时 | Node.js 20+ | 高并发，生态丰富 |
| Web 框架 | NestJS | TypeScript，模块化，易于维护 |
| 数据库 | PostgreSQL 15+ | 关系型，JSONB 支持，扩展性好 |
| 缓存 | Redis 7+ | 会话缓存，高频数据 |
| 消息队列 | Bull (Redis-based) | 异步任务处理 |
| API 文档 | Swagger/OpenAPI | 自动生成，便于协作 |

### 1.3 AI 服务
| 组件 | 技术选择 | 理由 |
|------|----------|------|
| 对话模型 | 智谱 GLM-4 / GPT-4o | 中文能力强，支持 function call |
| 情绪识别 | Tavus Raven-1 / 自研模型 | 多模态，低延迟 |
| 语音识别 | Whisper (OpenAI) | 开源，准确率高 |
| 语音合成 | Azure TTS | 自然度高，情感丰富 |
| 模型部署 | Triton Inference Server | 高性能，支持多框架 |

### 1.4 基础设施
| 组件 | 技术选择 | 理由 |
|------|----------|------|
| 容器化 | Docker | 标准化部署 |
| 编排 | Kubernetes | 自动扩缩容，高可用 |
| CI/CD | GitHub Actions | 与代码仓库集成 |
| 监控 | Prometheus + Grafana | 指标采集与可视化 |
| 日志 | ELK Stack | 集中日志管理 |

## 2. 系统架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      Client (Android)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  视频采集 │  │  音频采集 │  │   UI 层   │  │ 本地存储 │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼────────────┼────────────┼────────────┼────────────┘
        │            │            │            │
        │ HTTPS/WSS  │            │            │
        ▼            ▼            ▼            ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway (Nginx)                     │
│                   负载均衡 / SSL 终止 / 限流                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│  User Service │  │  Chat Service │  │ Emotion Service│
│  (NestJS)     │  │  (NestJS)     │  │   (NestJS)    │
└───────┬───────┘  └───────┬───────┘  └───────┬───────┘
        │                  │                  │
        ▼                  ▼                  ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│  PostgreSQL   │  │    Redis      │  │  AI Model API │
│  (Users,      │  │  (Sessions,   │  │  (Raven-1,    │
│   Sessions)   │  │   Cache)      │  │   GLM-4)      │
└───────────────┘  └───────────────┘  └───────────────┘
```

### 2.2 微服务划分

| 服务 | 职责 | 端口 |
|------|------|------|
| api-gateway | 路由、认证、限流 | 80/443 |
| user-service | 用户管理、认证 | 3001 |
| chat-service | 对话管理、消息存储 | 3002 |
| emotion-service | 情绪分析、记录 | 3003 |
| cbt-service | CBT 练习管理 | 3004 |
| crisis-service | 危机检测、预警 | 3005 |
| notification-service | 推送通知 | 3006 |

## 3. 数据库设计

### 3.1 核心表

```sql
-- 用户表
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(255),
    password_hash VARCHAR(255),
    nickname VARCHAR(100),
    age_range VARCHAR(20),
    gender VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- 对话会话表
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active'
);

-- 消息表
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- user/assistant/system
    content TEXT NOT NULL,
    emotion_state JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 情绪记录表
CREATE TABLE emotion_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    emotion_type VARCHAR(50) NOT NULL,
    confidence FLOAT NOT NULL,
    video_snapshot_url VARCHAR(500),
    audio_features JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CBT 练习记录
CREATE TABLE cbt_exercises (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    exercise_type VARCHAR(50) NOT NULL,
    content JSONB NOT NULL,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 危机预警记录
CREATE TABLE crisis_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL, -- low/medium/high/critical
    resolved BOOLEAN DEFAULT false,
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_emotion_records_user ON emotion_records(user_id, created_at);
CREATE INDEX idx_crisis_alerts_user ON crisis_alerts(user_id, resolved);
```

## 4. API 设计

### 4.1 认证接口

```yaml
POST /api/v1/auth/register
  body: { phone, code, password }
  response: { token, user }

POST /api/v1/auth/login
  body: { phone, password }
  response: { token, user }

POST /api/v1/auth/refresh
  body: { refresh_token }
  response: { token }
```

### 4.2 对话接口

```yaml
POST /api/v1/chat/message
  body: { content, emotion_state }
  response: { message_id, reply, suggestions }

WS  /api/v1/chat/stream
  send: { content, emotion_state }
  recv: { type: 'token'|'complete', data: string }
```

### 4.3 情绪接口

```yaml
POST /api/v1/emotion/analyze
  body: { video_frame_base64, audio_features }
  response: { emotion_type, confidence, valence, arousal }

GET  /api/v1/emotion/history
  query: { start_date, end_date, limit }
  response: { records: [...] }
```

### 4.4 CBT 接口

```yaml
GET  /api/v1/cbt/exercises
  response: { exercises: [...] }

POST /api/v1/cbt/exercises
  body: { exercise_id, responses }
  response: { completed, feedback }
```

### 4.5 危机接口

```yaml
POST /api/v1/crisis/check
  body: { message, emotion_state }
  response: { is_crisis, severity, suggestions }

POST /api/v1/crisis/alert
  body: { user_id, alert_type, severity }
  response: { alert_id, notifications_sent }
```

## 5. 安全设计

### 5.1 认证与授权
- JWT Token 认证 (Access Token 15 分钟，Refresh Token 7 天)
- RBAC 权限模型 (user/admin/superadmin)
- API 速率限制 (每用户 100 请求/分钟)

### 5.2 数据加密
- 传输层：TLS 1.3
- 存储层：AES-256 加密敏感字段
- 生物特征：本地处理，不上传不存储

### 5.3 隐私保护
- 数据最小化原则
- 用户数据导出/删除功能
- 匿名化数据分析

## 6. 部署架构

### 6.1 开发环境
- Docker Compose 本地运行
- 热重载开发模式

### 6.2 生产环境
```
┌─────────────────────────────────────────┐
│           Kubernetes Cluster            │
│  ┌─────────────────────────────────┐   │
│  │         Ingress Controller      │   │
│  └─────────────────────────────────┘   │
│                    │                    │
│  ┌─────────────────┼─────────────────┐ │
│  │    Service Mesh (Istio)           │ │
│  └─────────────────┼─────────────────┘ │
│                    │                    │
│  ┌───────┐  ┌───────┐  ┌───────┐      │
│  │ Pod   │  │ Pod   │  │ Pod   │ ...  │
│  │ svc A │  │ svc B │  │ svc C │      │
│  └───────┘  └───────┘  └───────┘      │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │    StatefulSet (PostgreSQL)     │   │
│  │    StatefulSet (Redis)          │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### 6.3 CI/CD 流程
```
Code Push → GitHub Actions → 
  Build & Test → 
  Docker Build → 
  Push to Registry → 
  Deploy to Staging → 
  Integration Test → 
  Deploy to Production (Blue-Green)
```

## 7. 监控与告警

### 7.1 关键指标
- API 响应时间 (P95 < 500ms)
- 错误率 (< 1%)
- 系统可用性 (> 99%)
- 数据库连接池使用率

### 7.2 告警规则
- 错误率 > 5% 持续 5 分钟 → P1 告警
- 响应时间 P95 > 1s 持续 10 分钟 → P2 告警
- 服务宕机 → P0 告警

---
*文档版本：1.0*  
*创建时间：2026-03-24*  
*负责人：backend-architect*
