# 需求拆解标准模板

> **原则**: 每个子智能体拿到的任务文件都能**直接执行**，无需额外澄清

---

## 使用说明

当 Manager/架构师 收到需求后，按照以下模板为每个智能体生成任务文件，确保：
- ✅ 任务边界清晰
- ✅ 执行步骤明确
- ✅ 输出格式具体
- ✅ 验收标准可量化

---

## 1. UI 设计师任务模板

**设计师配置**:
- **代号**: 画师
- **模型**: kimi-k2.5（默认）/ qwen3.5-vl（备用）
- **特点**: 纯大模型驱动，不依赖外部设计工具
- **核心功能**: 样例模仿生成 + Canvas 实时预览

```markdown
# 任务：[功能名称] UI 设计

## 基本信息
- **任务 ID**: ui-[序号]-[功能缩写]
- **功能名称**: [如：用户登录页面]
- **优先级**: P0/P1/P2
- **依赖**: [如：无 / 等待 PRD 确认]
- **推荐模型**: kimi-k2.5（多模态 UI 生成）
- **参考样例**: [如：sample-A / 无]

---

## 视觉描述

### 整体风格
[如：Airbnb 风格、圆角元素、极简主义、商务风]

### 配色建议
- **主色**: #4F46E5（用于按钮、链接）
- **辅色**: 灰色系（#6B7280、#9CA3AF）
- **背景**: #FFFFFF / #F9FAFB
- **文字**: #111827（主）/ #6B7280（次）

### 字体要求
[如：系统默认无衬线字体 -apple-system, BlinkMacSystemFont, "Segoe UI"]

### 参考图
[如有，提供路径或描述：类似微信登录页、参考 Dribbble #12345]

---

## 关键组件清单

请确保生成的界面包含以下组件：

- [ ] [组件 1：手机号输入框 - 带国家代码选择器]
- [ ] [组件 2：密码输入框 - 带显示/隐藏切换]
- [ ] [组件 3：登录按钮 - 主色、大尺寸]
- [ ] [组件 4：忘记密码链接]
- [ ] [组件 5：社交登录选项（微信/苹果/Google）]
- [ ] [组件 6：注册账号链接]
- [ ] [组件 7：隐私政策同意复选框]

---

## 布局要求

### 页面结构
[如：上下结构]
- 顶部：Logo + 标题
- 中间：登录表单
- 底部：社交登录 + 注册链接

### 响应式要求

| 设备 | 断点 | 要求 |
|------|------|------|
| 手机 | <768px | 表单宽度 90%，按钮全宽，大而易于点击 |
| 平板 | 768-1024px | 表单宽度 60%，居中显示 |
| 桌面 | >1024px | 表单宽度 400px，固定在右侧或居中 |

---

## 交互要求

- [ ] [输入框聚焦时边框高亮（主色，2px）]
- [ ] [登录按钮悬停时颜色变深（10%）]
- [ ] [点击按钮时有加载状态（CSS 动画模拟）]
- [ ] [表单提交前做简单验证（非空提示，红色文字）]
- [ ] [密码输入框右侧有显示/隐藏切换图标]
- [ ] [错误状态：输入框边框变红，下方显示错误信息]

---

## 输出要求

### 文件格式
- **主文件**: `login.html`（完整 HTML，包含内联样式或 `<style>` 标签）
- **样式文件**: `login.css`（如样式复杂，可单独拆分）
- **资源文件**: `assets/` 目录（图标、图片等）

### 预览
- 写入 Canvas 目录实现实时预览
- 或在 HTML 中提供可直接打开的完整代码

### 交付路径
`deliverables/ui/ui-[序号]-[功能缩写]/`

---

## 验收标准

- [ ] 所有组件清单中的组件都已实现
- [ ] 响应式布局在 3 个断点下都正常显示
- [ ] 交互效果（悬停、聚焦、加载）都能正常工作
- [ ] 代码无语法错误，可直接在浏览器打开
- [ ] 使用 CSS 变量定义颜色（方便开发替换）
- [ ] 所有交互用纯 CSS 实现（不依赖 JavaScript，除非特别要求）

---

## 注意事项

- ⚠️ 图片用占位符（如 Unsplash Source 或 Font Awesome 图标）
- ⚠️ 颜色用 CSS 变量定义（--primary-color, --text-color 等）
- ⚠️ 不要依赖外部 CDN（除非必要），优先使用本地资源
- ⚠️ 代码要有注释，关键样式说明用途
```

---

## 2. 开发架构师任务模板

```markdown
# 任务：[功能名称] 后端开发

## 基本信息
- **任务 ID**: dev-[序号]-[功能缩写]
- **功能名称**: [如：用户认证 API]
- **优先级**: P0/P1/P2
- **依赖**: [如：ui-[序号] 完成 / PRD 确认]
- **推荐模型**: glm-5（复杂后端）/ qwen3.5-plus（日常 CRUD）

---

## 功能概述

[用 1-2 句话描述功能：实现用户登录、注册、Token 管理等认证功能]

---

## 技术栈要求

### 语言/框架
- **语言**: [如：Python 3.11+]
- **框架**: [如：FastAPI 0.100+]
- **数据库**: [如：PostgreSQL 15 / SQLite]
- **ORM**: [如：SQLAlchemy 2.0 / Prisma]

### 依赖管理
- **包管理**: `requirements.txt` / `package.json`
- **环境**: `.env` 文件管理配置

---

## API 接口清单

请实现以下 API 端点：

### 1. POST /api/auth/register
**功能**: 用户注册

**请求体**:
```json
{
  "phone": "+8613800138000",
  "password": "securePassword123",
  "code": "123456"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "userId": "usr_xxx",
    "token": "eyJhbGc..."
  }
}
```

**错误处理**:
- 400: 手机号格式错误 / 密码强度不足 / 验证码错误
- 409: 手机号已注册

---

### 2. POST /api/auth/login
**功能**: 用户登录

**请求体**:
```json
{
  "phone": "+8613800138000",
  "password": "securePassword123"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "userId": "usr_xxx",
    "token": "eyJhbGc...",
    "expiresIn": 86400
  }
}
```

---

### 3. POST /api/auth/logout
**功能**: 用户登出

**请求头**: `Authorization: Bearer <token>`

**响应**:
```json
{
  "success": true,
  "message": "已登出"
}
```

---

## 数据模型

### User 表
```sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    phone VARCHAR(20) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

---

## 业务逻辑要求

### 密码处理
- [ ] 使用 bcrypt 或 argon2 哈希（不要明文存储）
- [ ] 密码强度验证：至少 8 位，包含大小写字母和数字

### Token 管理
- [ ] 使用 JWT 格式
- [ ] 有效期 24 小时
- [ ] 实现 Token 黑名单（登出后失效）

### 验证码
- [ ] 发送短信验证码（用 Mock 实现）
- [ ] 验证码有效期 5 分钟
- [ ] 验证码尝试次数限制（5 次/小时）

---

## 输出要求

### 文件结构
```
code/[项目名]/
├── app.py              # FastAPI 主应用
├── models.py           # 数据模型
├── routes.py           # API 路由
├── utils.py            # 工具函数（密码哈希、JWT 等）
├── requirements.txt    # 依赖列表
├── .env.example        # 环境变量示例
└── README.md           # 运行说明
```

### 代码规范
- [ ] 遵循 PEP 8（Python）或对应语言规范
- [ ] 关键函数有 docstring 注释
- [ ] 错误处理完整（try-except）
- [ ] 日志记录（用 logging 模块）

### 运行说明
README.md 必须包含：
- [ ] 环境要求（Python 版本等）
- [ ] 安装步骤（pip install -r requirements.txt）
- [ ] 配置说明（.env 文件）
- [ ] 启动命令（python app.py）
- [ ] API 测试方法（curl 示例或 Postman 集合）

---

## 验收标准

- [ ] 所有 API 端点都能正常工作
- [ ] 请求/响应格式符合要求
- [ ] 错误处理完整（返回标准错误格式）
- [ ] 代码无语法错误，可直接运行
- [ ] 有完整的 README 运行说明
- [ ] 通过基本测试（手动或自动化）

---

## 注意事项

- ⚠️ 敏感信息（密码、密钥）不要硬编码，用环境变量
- ⚠️ 数据库连接用连接池
- ⚠️ API 响应时间控制在 200ms 以内
- ⚠️ 实现 CORS（允许前端跨域访问）
```

---

## 3. 测试工程师任务模板

```markdown
# 任务：[功能名称] 测试

## 基本信息
- **任务 ID**: test-[序号]-[功能缩写]
- **功能名称**: [如：用户认证 API 测试]
- **优先级**: P0/P1/P2
- **依赖**: [如：dev-[序号] 完成]
- **推荐模型**: qwen3.5-plus

---

## 测试范围

### 功能测试
- [ ] [功能点 1：用户注册]
- [ ] [功能点 2：用户登录]
- [ ] [功能点 3：用户登出]
- [ ] [功能点 4：Token 刷新]

### 边界测试
- [ ] [边界 1：手机号格式验证]
- [ ] [边界 2：密码强度验证]
- [ ] [边界 3：验证码有效期]

### 异常测试
- [ ] [异常 1：网络超时]
- [ ] [异常 2：数据库连接失败]
- [ ] [异常 3：无效 Token]

---

## 测试用例清单

### 用例 1: 用户注册 - 成功
```python
def test_register_success():
    """测试用户注册成功场景"""
    payload = {
        "phone": "+8613800138000",
        "password": "SecurePass123",
        "code": "123456"
    }
    response = requests.post("/api/auth/register", json=payload)
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert "token" in response.json()["data"]
```

### 用例 2: 用户注册 - 手机号已存在
```python
def test_register_duplicate():
    """测试手机号已注册"""
    payload = {
        "phone": "+8613800138000",  # 已存在的手机号
        "password": "SecurePass123",
        "code": "123456"
    }
    response = requests.post("/api/auth/register", json=payload)
    assert response.status_code == 409
    assert "已注册" in response.json()["message"]
```

### 用例 3: 用户登录 - 密码错误
```python
def test_login_wrong_password():
    """测试密码错误"""
    payload = {
        "phone": "+8613800138000",
        "password": "WrongPassword"
    }
    response = requests.post("/api/auth/login", json=payload)
    assert response.status_code == 401
    assert "密码错误" in response.json()["message"]
```

---

## 测试数据

### 有效数据
```json
{
  "valid_phone": "+8613800138000",
  "valid_password": "SecurePass123",
  "valid_code": "123456"
}
```

### 无效数据
```json
{
  "invalid_phone": "13800138000",  // 缺少国家代码
  "weak_password": "123",  // 密码太短
  "expired_code": "000000"  // 过期验证码
}
```

---

## 输出要求

### 文件结构
```
test-reports/[项目名]/
├── test_auth.py        # 测试用例
├── conftest.py         # Pytest 配置
├── test_data.json      # 测试数据
├── test_report.md      # 测试报告
└── requirements.txt    # 测试依赖
```

### 测试报告
`test_report.md` 必须包含：
- [ ] 测试概述（测试范围、环境）
- [ ] 测试结果汇总（通过/失败用例数）
- [ ] 失败用例详情（错误信息、截图）
- [ ] 性能测试结果（响应时间、并发数）
- [ ] 遗留问题和建议

---

## 验收标准

- [ ] 测试覆盖率 ≥ 80%（核心功能）
- [ ] 所有 P0 用例通过
- [ ] 测试报告完整、清晰
- [ ] 测试代码可重复执行
- [ ] 发现问题有详细记录

---

## 注意事项

- ⚠️ 测试数据用 Mock，不要依赖真实数据库
- ⚠️ 测试用例要独立，不互相依赖
- ⚠️ 敏感信息（密码、Token）用环境变量
- ⚠️ 测试报告用 Markdown 格式，便于阅读
```

---

## 4. 产品架构师任务模板（复杂项目用）

```markdown
# 任务：[项目名称] 产品架构设计

## 基本信息
- **任务 ID**: pm-[序号]-[项目缩写]
- **项目名称**: [如：录像诊断功能]
- **优先级**: P0
- **推荐模型**: glm-5

---

## 需求背景

[描述需求的业务背景、目标用户、解决的问题]

---

## 产品需求文档 (PRD)

### 用户故事
```
作为 [用户角色]
我希望 [完成什么任务]
以便 [获得什么价值]
```

### 功能清单
- [ ] [功能 1：录像上传]
- [ ] [功能 2：AI 分析]
- [ ] [功能 3：报告生成]

### 验收标准
[每个功能的验收标准，用 Given-When-Then 格式]

---

## 系统架构设计

### 技术选型
- **前端**: [如：React 18 + TypeScript]
- **后端**: [如：Python FastAPI]
- **数据库**: [如：PostgreSQL + Redis]
- **AI 服务**: [如：自研模型 / 第三方 API]

### 架构图
```
[用文字或 ASCII 描述系统架构]
用户 → 前端 → API Gateway → 后端服务 → 数据库
                              ↓
                          AI 服务
```

### 数据流
```
[描述关键数据流]
1. 用户上传录像 → 2. 后端存储 → 3. 调用 AI 分析 → 4. 生成报告 → 5. 返回用户
```

---

## 输出要求

### 交付物
- [ ] `prd/[项目名]/[项目名]_prd.md` - 产品需求文档
- [ ] `prd/[项目名]/ARCHITECTURE.md` - 系统架构设计
- [ ] `prd/[项目名]/.cloude/settings.mdc` - Claude Code 规范
- [ ] `prd/[项目名]/task-dev.md` - 开发任务描述

### 文档规范
- [ ] PRD 包含用户故事、功能清单、验收标准
- [ ] 架构设计包含技术选型、架构图、数据流
- [ ] .mdc 文件包含代码规范、项目配置
- [ ] task-dev.md 包含开发任务拆解、推荐模型

---

## 注意事项

- ⚠️ 架构设计要考虑扩展性
- ⚠️ 技术选型要说明理由
- ⚠️ 风险评估（技术风险、时间风险）
```

---

## 使用示例

### 场景：开发一个用户登录功能

**Manager 创建的任务文件**:

1. `TASKS/ui-login.md` - 使用 UI 设计师模板
2. `TASKS/dev-login.md` - 使用开发架构师模板
3. `TASKS/test-login.md` - 使用测试工程师模板

每个任务文件都包含：
- ✅ 清晰的任务边界
- ✅ 详细的执行步骤
- ✅ 具体的输出格式
- ✅ 可量化的验收标准

---

*模板版本：v1.0 | 最后更新：2026-03-11*
