# 🧠 MindMirror AI - 完整开发计划文档

**版本**: v1.0  
**日期**: 2026-03-17  
**项目**: AI 心理医生 App (MindMirror AI)

---

## 📋 一、项目概述

### 产品定位
- **产品名称**: MindMirror AI（心理镜像）
- **核心价值**: 通过多模态 AI 实时理解用户情绪，提供个性化心理支持
- **目标用户**: 轻度至中度焦虑/抑郁人群、需要情绪疏导的普通人、心理咨询师辅助工具
- **硬件环境**: Android 盒子（需外接 USB 摄像头）或手机

### 核心功能
1. 多模态情绪识别（视频 + 音频）
2. 实时心理对话
3. CBT 心理干预
4. 危机预警系统

---

## 👥 二、团队组建（12 人核心小组）

### 核心管理层
| Agent | 职责 | 关键任务 |
|-------|------|----------|
| **product-manager** | 产品规划与优先级 | 需求定义、里程碑跟踪、资源协调 |
| **technical-writer** | 文档与知识管理 | 技术文档、API 文档、用户手册 |

### 技术架构组
| Agent | 职责 | 关键任务 |
|-------|------|----------|
| **backend-architect** | 后端系统架构 | 微服务设计、数据库选型、API 规范 |
| **frontend-developer** | Android 客户端开发 | UI 实现、本地存储、音视频采集 |
| **devops-automator** | 部署与运维 | CI/CD、云基础设施、监控告警 |

### AI 核心组
| Agent | 职责 | 关键任务 |
|-------|------|----------|
| **ai-engineer** | AI 模型集成 | 情绪识别模型、对话系统、危机检测 |
| **ml-ops-engineer** | 模型部署优化 | 模型服务化、推理优化、A/B 测试 |
| **data-engineer** | 数据管道 | 数据采集、标注流程、特征工程 |

### 设计与体验组
| Agent | 职责 | 关键任务 |
|-------|------|----------|
| **ui-designer** | 界面视觉设计 | 设计系统、组件库、动效设计 |
| **ux-researcher** | 用户体验研究 | 用户访谈、可用性测试、流程优化 |

### 质量与合规组
| Agent | 职责 | 关键任务 |
|-------|------|----------|
| **security-engineer** | 安全与合规 | 数据加密、隐私保护、医疗合规 |
| **code-reviewer** | 代码质量审查 | PR 审查、代码规范、技术债务 |
| **qa-automation-engineer** | 自动化测试 | 单元测试、E2E 测试、性能测试 |

### 专家顾问组
| Agent | 职责 | 关键任务 |
|-------|------|----------|
| **psychology-advisor** | 心理学专业指导 | CBT 内容设计、危机干预协议 |

---

## 📅 三、12 周 MVP 开发计划

### 🎯 第一阶段：基础搭建（第 1-3 周）

#### 第 1 周：项目启动与需求细化
| 任务 | 负责人 | 交付物 |
|------|--------|--------|
| 需求评审与用户故事定义 | product-manager | PRD 文档 v1.0 |
| 技术栈选型与架构设计 | backend-architect | 架构设计文档 |
| 合规要求梳理（医疗数据） | security-engineer | 合规检查清单 |
| CBT 干预内容框架设计 | psychology-advisor | 干预内容大纲 |
| 项目环境初始化 | devops-automator | Git 仓库、CI/CD 流水线 |

#### 第 2 周：系统设计
| 任务 | 负责人 | 交付物 |
|------|--------|--------|
| 数据库设计与 API 规范 | backend-architect | ER 图、API Swagger |
| 情绪识别技术方案确定 | ai-engineer | 模型选型报告 |
| 界面原型设计 | ui-designer | Figma 高保真原型 |
| 用户体验流程设计 | ux-researcher | 用户旅程地图 |
| 安全架构设计 | security-engineer | 加密方案、权限设计 |

#### 第 3 周：基础设施搭建
| 任务 | 负责人 | 交付物 |
|------|--------|--------|
| 后端微服务框架搭建 | backend-architect | 基础服务代码 |
| Android 项目初始化 | frontend-developer | 项目骨架、基础组件 |
| 模型训练环境准备 | ml-ops-engineer | GPU 集群、训练管道 |
| 数据采集方案设计 | data-engineer | 数据标注规范 |
| 测试框架搭建 | qa-automation-engineer | 自动化测试框架 |

---

### 🚀 第二阶段：核心功能开发（第 4-8 周）

#### 第 4 周：情绪识别模块（视频）
| 任务 | 负责人 | 交付物 |
|------|--------|--------|
| 面部表情识别模型集成 | ai-engineer | 表情识别 API |
| 视频采集与预处理 | frontend-developer | 视频采集模块 |
| 微表情特征提取 | data-engineer | 特征工程代码 |
| 模型推理服务部署 | ml-ops-engineer | 推理服务 v1 |

#### 第 5 周：情绪识别模块（音频）
| 任务 | 负责人 | 交付物 |
|------|--------|--------|
| 语音情感识别模型集成 | ai-engineer | 语音情感 API |
| 音频采集与降噪处理 | frontend-developer | 音频处理模块 |
| 多模态融合策略设计 | ai-engineer | 融合算法 v1 |
| 情绪状态输出标准化 | backend-architect | 情绪数据结构 |

#### 第 6 周：实时对话系统
| 任务 | 负责人 | 交付物 |
|------|--------|--------|
| 对话引擎集成（LLM） | ai-engineer | 对话 API |
| 上下文管理模块 | backend-architect | 会话状态管理 |
| 心理话术库设计 | psychology-advisor | 话术模板库 |
| 对话 UI 实现 | frontend-developer | 聊天界面 v1 |

#### 第 7 周：CBT 干预模块
| 任务 | 负责人 | 交付物 |
|------|--------|--------|
| CBT 练习内容开发 | psychology-advisor | 10 个核心练习 |
| 干预流程引擎 | backend-architect | 流程引擎代码 |
| 练习 UI 组件 | ui-designer + frontend-developer | 交互组件库 |
| 进度跟踪系统 | data-engineer | 用户进度数据模型 |

#### 第 8 周：危机预警系统
| 任务 | 负责人 | 交付物 |
|------|--------|--------|
| 危机信号识别模型 | ai-engineer | 危机检测 API |
| 预警阈值与规则 | psychology-advisor | 预警协议文档 |
| 紧急联系人功能 | frontend-developer | 联系人管理 UI |
| 危机干预流程 | security-engineer | 应急响应 SOP |

---

### 🔧 第三阶段：集成与优化（第 9-12 周）

#### 第 9 周：系统集成
| 任务 | 负责人 | 交付物 |
|------|--------|--------|
| 模块集成与联调 | backend-architect | 集成测试报告 |
| 端到端流程测试 | qa-automation-engineer | E2E 测试用例 |
| 性能优化（延迟<200ms） | ml-ops-engineer | 性能基准报告 |
| 安全渗透测试 | security-engineer | 安全审计报告 |

#### 第 10 周：用户体验优化
| 任务 | 负责人 | 交付物 |
|------|--------|--------|
| 可用性测试（5-8 用户） | ux-researcher | 可用性测试报告 |
| UI 细节优化 | ui-designer | 设计迭代 v2 |
| 交互流畅度优化 | frontend-developer | 性能优化报告 |
| 无障碍适配 | frontend-developer | 无障碍检查清单 |

#### 第 11 周：稳定性与合规
| 任务 | 负责人 | 交付物 |
|------|--------|--------|
| 压力测试（1000 并发） | qa-automation-engineer | 压力测试报告 |
| 数据隐私合规审计 | security-engineer | 合规认证准备 |
| 错误处理与日志完善 | devops-automator | 监控告警系统 |
| 文档完善 | technical-writer | 完整文档包 |

#### 第 12 周：MVP 发布准备
| 任务 | 负责人 | 交付物 |
|------|--------|--------|
| 代码冻结与最终审查 | code-reviewer | 发布候选版本 |
| 生产环境部署 | devops-automator | 生产环境就绪 |
| 灰度发布计划 | product-manager | 发布计划文档 |
| MVP 演示准备 | 全员 | 演示视频 + Demo |

---

## 🎯 四、里程碑定义

| 里程碑 | 时间 | 关键交付物 | 验收标准 |
|--------|------|------------|----------|
| **M1: 架构冻结** | 第 3 周末 | 架构文档、API 规范、原型设计 | 技术方案评审通过 |
| **M2: 情绪识别完成** | 第 5 周末 | 视频 + 音频情绪识别 API | 准确率≥75%（测试集） |
| **M3: 对话系统完成** | 第 6 周末 | 实时对话功能 | 响应延迟<500ms |
| **M4: CBT 模块完成** | 第 7 周末 | 10 个 CBT 练习可用 | 心理学专家验收 |
| **M5: 危机预警完成** | 第 8 周末 | 危机检测与预警系统 | 召回率≥90% |
| **M6: MVP 发布** | 第 12 周末 | 可上线版本 | 通过安全审计、性能达标 |

---

## ⚠️ 五、风险管理

### 技术风险
| 风险 | 概率 | 影响 | 应对策略 |
|------|------|------|----------|
| 情绪识别准确率不达标 | 中 | 高 | 预留 2 周优化时间；准备多模型备选方案 |
| 实时对话延迟过高 | 中 | 高 | 采用边缘计算；模型蒸馏优化；缓存策略 |
| 多模态融合效果不佳 | 低 | 中 | 早期验证融合策略；保留单模态降级方案 |

### 合规风险
| 风险 | 概率 | 影响 | 应对策略 |
|------|------|------|----------|
| 医疗数据合规问题 | 中 | 极高 | 第 1 周即引入法律顾问；采用端到端加密；数据本地化存储 |
| 隐私保护不足 | 中 | 高 | 匿名化处理；用户数据导出/删除功能；定期安全审计 |
| 危机干预责任边界 | 高 | 极高 | 明确免责声明；建立专业心理咨询转介机制 |

### 项目风险
| 风险 | 概率 | 影响 | 应对策略 |
|------|------|------|----------|
| 12 周时间紧张 | 高 | 中 | 严格优先级管理；MVP 功能范围控制；预留 1 周缓冲 |
| 关键人员依赖 | 中 | 中 | 代码审查强制双人；文档实时更新；知识共享会议 |
| 模型训练数据不足 | 中 | 中 | 使用公开数据集；数据增强；主动学习策略 |

### 应急预案
1. **技术降级方案**：如情绪识别未达标，先上线文本对话 + CBT 核心功能
2. **分阶段发布**：先内部测试→小范围灰度→公开发布
3. **危机干预兜底**：集成专业心理热线 API，确保用户安全

---

## 📊 六、关键指标（MVP 验收标准）

| 指标类别 | 具体指标 | 目标值 |
|----------|----------|--------|
| **性能** | 对话响应延迟 | <500ms |
| **性能** | 情绪识别推理时间 | <200ms |
| **准确率** | 情绪识别准确率 | ≥75% |
| **准确率** | 危机信号召回率 | ≥90% |
| **可用性** | 用户任务完成率 | ≥85% |
| **稳定性** | 系统可用性 | ≥99% |
| **安全** | 安全漏洞数（高危） | 0 |

---

## 🛠️ 七、技术栈汇总

| 层级 | 技术选择 |
|------|----------|
| **前端** | Kotlin + Jetpack Compose + CameraX |
| **后端** | Node.js + NestJS + PostgreSQL + Redis |
| **AI** | Tavus Raven-1 / GPT-4o / 智谱 GLM-4 |
| **语音** | Whisper + Azure TTS |
| **部署** | Docker + Kubernetes + GitHub Actions |
| **监控** | Prometheus + Grafana |

---

## 📁 八、MVP 功能列表

### P0 - 必须有
1. 用户注册/登录（手机号验证码）
2. 视频情绪识别（摄像头采集 + AI 分析）
3. 实时 AI 对话（基于大模型）
4. 基础 CBT 练习（10 个核心练习）
5. 危机预警提示（关键词 + 情绪阈值）

### P1 - 应该有
1. 情绪历史记录与趋势图
2. 语音输入/输出
3. 练习推荐
4. 用户报告生成

### P2 - 可以有
1. 心理咨询师入口
2. 社区功能
3. 个性化推荐

---

## 🔐 九、合规与安全要求

### 数据分类
| 数据类型 | 敏感级别 | 存储要求 | 传输要求 |
|----------|----------|----------|----------|
| 用户基本信息 | 中 | 加密 | HTTPS |
| 情绪数据 | 高 | 加密+脱敏 | HTTPS+签名 |
| 对话记录 | 高 | 加密 | HTTPS+签名 |
| 生物特征(面部) | 极高 | 本地处理 | 不存储 |
| 危机信号 | 极高 | 加密 | 即时通知 |

### 合规标准
- [ ] GDPR 个人信息保护
- [ ] 中华人民共和国个人信息保护法
- [ ] 国家卫健委远程医疗规范
- [ ] 医疗器械网络安全注册要求（如适用）

---

## 📅 九、详细周任务（第一周示例）

### 第 1 周任务详表

| 日期 | 任务 | 负责人 | 交付物 |
|------|------|--------|--------|
| Day 1 | 需求评审会议 | product-manager | PRD 文档 v1.0 初稿 |
| Day 2 | 技术栈选型 | backend-architect | 技术选型报告 |
| Day 3 | 合规要求梳理 | security-engineer | 合规检查清单 |
| Day 4 | CBT 框架设计 | psychology-advisor | 干预内容大纲 |
| Day 5 | Git 仓库初始化 | devops-automator | 代码仓库 |
| Day 6 | CI/CD 基础配置 | devops-automator | 流水线配置 |
| Day 7 | 第一周复盘 | product-manager | 周报 + 第二周计划 |

---

## 📝 十、数据库设计摘要

### 核心表结构

```sql
-- 用户表
CREATE TABLE users (
    id UUID PRIMARY KEY,
    phone VARCHAR(20) UNIQUE,
    email VARCHAR(255),
    password_hash VARCHAR(255),
    nickname VARCHAR(100),
    age_range VARCHAR(20),
    gender VARCHAR(20),
    created_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- 对话会话表
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    title VARCHAR(255),
    started_at TIMESTAMP,
    status VARCHAR(20)
);

-- 消息表
CREATE TABLE messages (
    id UUID PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(id),
    role VARCHAR(20),
    content TEXT,
    emotion_state JSONB,
    created_at TIMESTAMP
);

-- 情绪记录表
CREATE TABLE emotion_records (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    emotion_type VARCHAR(50),
    confidence FLOAT,
    video_snapshot_url VARCHAR(500),
    audio_features JSONB,
    created_at TIMESTAMP
);

-- CBT 练习记录
CREATE TABLE cbt_exercises (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    exercise_type VARCHAR(50),
    content JSONB,
    completed_at TIMESTAMP
);

-- 危机预警记录
CREATE TABLE crisis_alerts (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    alert_type VARCHAR(50),
    severity VARCHAR(20),
    resolved BOOLEAN DEFAULT false,
    created_at TIMESTAMP
);
```

---

## 📖 十一、API 规范摘要

### 核心接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/v1/auth/register` | POST | 用户注册 |
| `/api/v1/auth/login` | POST | 用户登录 |
| `/api/v1/emotion/analyze` | POST | 情绪分析 |
| `/api/v1/chat/message` | POST | 发送消息 |
| `/api/v1/chat/stream` | WebSocket | 流式对话 |
| `/api/v1/cbt/exercises` | GET | 获取练习列表 |
| `/api/v1/cbt/exercises` | POST | 提交练习 |
| `/api/v1/crisis/check` | POST | 危机检测 |

---

## 🎯 十二、下一步行动

1. **技术验证**: 用 Python 快速搭建原型，调用 Raven-1 或 OpenAI Realtime API
2. **设计 MVP 原型**: 画出主要界面流程图，明确用户交互
3. **搭建开发环境**: 配置安卓开发环境，申请必要的 API 密钥
4. **分模块开发**: 按上述阶段推进

---

*文档版本：1.0*  
*创建时间：2026-03-17*  
*最后更新：2026-03-17*