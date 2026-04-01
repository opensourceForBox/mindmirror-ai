# MindMirror AI - 登录/注册界面原型

**版本**: v1.0  
**日期**: 2026-03-24  
**负责人**: ui-designer  
**状态**: ✅ 已完成

---

## 1. 界面概述

**功能**: 用户登录、注册、验证码获取  
**入口**: App 启动后的首个界面  
**目标**: 简化注册流程，降低用户门槛

---

## 2. 界面布局

### 2.1 登录界面

```
┌─────────────────────────────────────────────┐
│                                              │
│                                              │
│              🧠 MindMirror                   │
│              心理镜像 · AI 陪伴                │
│                                              │
│                                              │
│                                              │
│  ┌─────────────────────────────────────┐   │
│  │  手机号                              │   │
│  │  +86 ▼ _______________              │   │
│  └─────────────────────────────────────┘   │
│                                              │
│  ┌─────────────────────────────────────┐   │
│  │  验证码          获取验证码          │   │
│  │  _________                          │   │
│  └─────────────────────────────────────┘   │
│                                              │
│  ┌─────────────────────────────────────┐   │
│  │           登 录                      │   │
│  └─────────────────────────────────────┘   │
│                                              │
│  ─────────── 或 ───────────                 │
│                                              │
│  ┌─────────────────────────────────────┐   │
│  │           密码登录                   │   │
│  └─────────────────────────────────────┘   │
│                                              │
│                                              │
│  □ 我已阅读并同意《用户协议》和《隐私政策》   │
│                                              │
│  ─────────────────────────────────────────  │
│  遇到问题？           联系客服              │
│                                              │
└─────────────────────────────────────────────┘
```

**布局规格**:
- Logo 距顶部：80dp
- Logo 尺寸：120dp × 120dp
- 输入框高度：48dp
- 按钮高度：48dp
- 底部边距：32dp

### 2.2 注册界面

```
┌─────────────────────────────────────────────┐
│  ← 返回                                     │
│                                              │
│              创建账号                        │
│              开启你的心灵之旅                │
│                                              │
│  ┌─────────────────────────────────────┐   │
│  │  手机号 *                            │   │
│  │  +86 ▼ _______________              │   │
│  └─────────────────────────────────────┘   │
│                                              │
│  ┌─────────────────────────────────────┐   │
│  │  验证码 *        获取验证码          │   │
│  │  _________                          │   │
│  └─────────────────────────────────────┘   │
│                                              │
│  ┌─────────────────────────────────────┐   │
│  │  密码 *                              │   │
│  │  ●●●●●●●●              👁️          │   │
│  └─────────────────────────────────────┘   │
│  至少 8 位，包含字母和数字                    │
│                                              │
│  ┌─────────────────────────────────────┐   │
│  │  确认密码 *                          │   │
│  │  ●●●●●●●●                           │   │
│  └─────────────────────────────────────┘   │
│                                              │
│  ┌─────────────────────────────────────┐   │
│  │           创建账号                   │   │
│  └─────────────────────────────────────┘   │
│                                              │
│  已有账号？登录                              │
│                                              │
└─────────────────────────────────────────────┘
```

---

## 3. 交互说明

### 3.1 输入框交互

| 状态 | 行为 | 视觉反馈 |
|------|------|----------|
| Default | 等待输入 | Gray 300 边框 |
| Focused | 用户点击 | Primary 边框 (2dp) |
| Valid | 输入有效 | 绿色对勾图标 |
| Error | 输入无效 | Error 边框 + 错误提示 |
| Disabled | 不可用 | Gray 100 背景 |

### 3.2 验证码流程

```
用户输入手机号 → 点击"获取验证码" → 
  发送请求 → 显示倒计时 (60s) → 
  用户输入验证码 → 自动验证 → 
  成功：跳转下一步 / 失败：显示错误
```

**倒计时状态**:
```
获取验证码 (Default)
  ↓ 点击
发送中... (Loading, 按钮禁用)
  ↓ 成功
60s 后重新获取 (Gray 500, 禁用)
  ↓ 倒计时结束
获取验证码 (可再次点击)
```

### 3.3 密码可见性切换

```
密码输入框右侧显示 👁️ 图标

点击 👁️ → 显示明文密码，图标变为 👁️̸
再次点击 → 隐藏密码，图标恢复 👁️
```

### 3.4 表单验证

**实时验证**:
- 手机号格式：输入时验证
- 密码强度：输入时显示强度条
- 验证码：提交时验证

**密码强度指示器**:
```
弱    中    强    非常强
▓░░░░  ▓▓▓░░  ▓▓▓▓▓  ▓▓▓▓▓
(红)   (橙)   (绿)   (深绿)
```

**验证规则**:
| 字段 | 规则 | 错误提示 |
|------|------|----------|
| 手机号 | 11 位数字，1 开头 | "请输入有效的手机号" |
| 验证码 | 6 位数字 | "请输入 6 位验证码" |
| 密码 | 8-20 位，字母 + 数字 | "密码至少 8 位，包含字母和数字" |
| 确认密码 | 与密码一致 | "两次输入的密码不一致" |

---

## 4. 组件列表

### 4.1 核心组件

| 组件 | 数量 | 说明 |
|------|------|------|
| Logo | 1 | MindMirror 品牌标识 |
| TextInput | 3-4 | 手机号、验证码、密码 |
| Button | 2-3 | 登录、注册、获取验证码 |
| Checkbox | 1 | 协议同意 |
| TextLink | 2 | 协议链接、密码登录切换 |

### 4.2 组件代码（Jetpack Compose）

```kotlin
// 手机号输入框
@Composable
fun PhoneNumberInput(
    value: String,
    onValueChange: (String) -> Unit,
    error: String? = null
) {
    OutlinedTextField(
        value = value,
        onValueChange = onValueChange,
        label = { Text("手机号") },
        prefix = { 
            Text("+86")
            Icon(Icons.Default.ArrowDropDown, "选择区号")
        },
        placeholder = { Text("请输入手机号") },
        isError = error != null,
        supportingText = error?.let { { Text(it) } },
        modifier = Modifier.fillMaxWidth(),
        colors = OutlinedTextFieldDefaults.colors(
            focusedBorderColor = MindMirrorColors.primary,
            unfocusedBorderColor = MindMirrorColors.gray300
        )
    )
}

// 验证码输入框
@Composable
fun VerificationCodeInput(
    value: String,
    onValueChange: (String) -> Unit,
    onSendCode: () -> Unit,
    countdownSeconds: Int
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        OutlinedTextField(
            value = value,
            onValueChange = onValueChange,
            label = { Text("验证码") },
            placeholder = { Text("6 位数字") },
            maxLength = 6,
            modifier = Modifier.weight(1f)
        )
        
        Button(
            onClick = onSendCode,
            enabled = countdownSeconds == 0,
            modifier = Modifier.height(48.dp)
        ) {
            Text(
                if (countdownSeconds > 0) "${countdownSeconds}s" 
                else "获取验证码"
            )
        }
    }
}

// 密码输入框
@Composable
fun PasswordInput(
    value: String,
    onValueChange: (String) -> Unit,
    label: String,
    error: String? = null
) {
    var passwordVisible by remember { mutableStateOf(false) }
    
    OutlinedTextField(
        value = value,
        onValueChange = onValueChange,
        label = { Text(label) },
        placeholder = { Text("请输入密码") },
        visualTransformation = 
            if (passwordVisible) VisualTransformation.None 
            else PasswordVisualTransformation(),
        trailingIcon = {
            IconButton(onClick = { passwordVisible = !passwordVisible }) {
                Icon(
                    imageVector = if (passwordVisible) 
                        Icons.Default.VisibilityOff 
                    else 
                        Icons.Default.Visibility,
                    contentDescription = if (passwordVisible) 
                        "隐藏密码" 
                    else 
                        "显示密码"
                )
            }
        },
        isError = error != null,
        supportingText = error?.let { { Text(it) } },
        modifier = Modifier.fillMaxWidth()
    )
}

// 协议同意 Checkbox
@Composable
fun AgreementCheckbox(
    checked: Boolean,
    onCheckedChange: (Boolean) -> Unit
) {
    Row(
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        Checkbox(
            checked = checked,
            onCheckedChange = onCheckedChange,
            colors = CheckboxDefaults.colors(
                checkedColor = MindMirrorColors.primary
            )
        )
        Text(
            text = "我已阅读并同意",
            style = MindMirrorTypography.bodySmall,
            color = MindMirrorColors.gray700
        )
        ClickableText(
            text = AnnotatedString("《用户协议》"),
            onClick = { /* 打开协议 */ },
            style = MindMirrorTypography.bodySmall.copy(
                color = MindMirrorColors.primary
            )
        )
        Text(
            text = "和",
            style = MindMirrorTypography.bodySmall,
            color = MindMirrorColors.gray700
        )
        ClickableText(
            text = AnnotatedString("《隐私政策》"),
            onClick = { /* 打开政策 */ },
            style = MindMirrorTypography.bodySmall.copy(
                color = MindMirrorColors.primary
            )
        )
    }
}
```

---

## 5. 状态管理

### 5.1 ViewModel

```kotlin
@HiltViewModel
class LoginViewModel @Inject constructor(
    private val authRepository: AuthRepository
) : ViewModel() {
    
    // UI State
    val uiState: StateFlow<LoginUiState> = _uiState.asStateFlow()
    private val _uiState = MutableStateFlow(LoginUiState())
    
    // 事件
    private val _events = MutableSharedFlow<LoginEvent>()
    val events: SharedFlow<LoginEvent> = _events.asSharedFlow()
    
    // 输入
    fun onPhoneNumberChange(phone: String) {
        _uiState.update { it.copy(phoneNumber = phone) }
    }
    
    fun onVerificationCodeChange(code: String) {
        _uiState.update { it.copy(verificationCode = code) }
    }
    
    fun onPasswordChange(password: String) {
        _uiState.update { it.copy(password = password) }
    }
    
    // 获取验证码
    fun sendVerificationCode() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            
            try {
                authRepository.sendVerificationCode(
                    phoneNumber = uiState.value.phoneNumber
                )
                _uiState.update { 
                    it.copy(
                        isLoading = false,
                        countdownSeconds = 60
                    ) 
                }
                _events.emit(LoginEvent.CodeSent)
            } catch (e: Exception) {
                _uiState.update { 
                    it.copy(
                        isLoading = false,
                        error = e.message
                    ) 
                }
            }
        }
    }
    
    // 登录
    fun login() {
        if (!validateForm()) return
        
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            
            try {
                val result = authRepository.login(
                    phoneNumber = uiState.value.phoneNumber,
                    verificationCode = uiState.value.verificationCode
                )
                _events.emit(LoginEvent.LoginSuccess(result))
            } catch (e: Exception) {
                _uiState.update { 
                    it.copy(
                        isLoading = false,
                        error = e.message
                    ) 
                }
            }
        }
    }
    
    private fun validateForm(): Boolean {
        val state = uiState.value
        
        return when {
            !isValidPhoneNumber(state.phoneNumber) -> {
                _uiState.update { it.copy(phoneError = "请输入有效的手机号") }
                false
            }
            state.verificationCode.length != 6 -> {
                _uiState.update { it.copy(codeError = "请输入 6 位验证码") }
                false
            }
            else -> true
        }
    }
}

// UI State 数据类
data class LoginUiState(
    val phoneNumber: String = "",
    val verificationCode: String = "",
    val password: String = "",
    val isLoading: Boolean = false,
    val countdownSeconds: Int = 0,
    val phoneError: String? = null,
    val codeError: String? = null,
    val passwordError: String? = null,
    val error: String? = null,
    val agreementChecked: Boolean = false
)

// 事件
sealed class LoginEvent {
    object CodeSent : LoginEvent()
    data class LoginSuccess(val tokens: AuthTokens) : LoginEvent()
    data class Error(val message: String) : LoginEvent()
}
```

---

## 6. 错误处理

### 6.1 错误类型与提示

| 错误码 | 错误信息 | 用户提示 |
|--------|----------|----------|
| INVALID_PHONE | 手机号格式错误 | "请输入有效的手机号" |
| PHONE_NOT_REGISTERED | 手机号未注册 | "该手机号未注册，请先注册" |
| INVALID_CODE | 验证码错误 | "验证码错误，请重新输入" |
| CODE_EXPIRED | 验证码已过期 | "验证码已过期，请重新获取" |
| TOO_MANY_REQUESTS | 请求过于频繁 | "操作过于频繁，请稍后再试" |
| NETWORK_ERROR | 网络错误 | "网络连接失败，请检查网络" |
| SERVER_ERROR | 服务器错误 | "服务器繁忙，请稍后再试" |

### 6.2 错误展示

```kotlin
// Snackbar 错误提示
@Composable
fun ErrorSnackbar(
    error: String?,
    onDismiss: () -> Unit
) {
    error?.let {
        Snackbar(
            modifier = Modifier.padding(16.dp),
            backgroundColor = MindMirrorColors.error,
            contentColor = Color.White,
            action = {
                TextButton(onClick = onDismiss) {
                    Text("关闭", color = Color.White)
                }
            }
        ) {
            Text(it)
        }
    }
}
```

---

## 7. 无障碍设计

### 7.1 内容描述

```kotlin
// Logo
Icon(
    painter = painterResource(R.drawable.logo),
    contentDescription = "MindMirror AI 心理镜像"
)

// 输入框
OutlinedTextField(
    // ...
    modifier = Modifier.semantics {
        contentDescription = "手机号输入框"
    }
)

// 按钮
Button(
    // ...
    modifier = Modifier.semantics {
        contentDescription = "登录按钮"
    }
)
```

### 7.2 焦点管理

```kotlin
// 自动聚焦到第一个输入框
LaunchedEffect(Unit) {
    phoneNumberFocusRequester.requestFocus()
}

// 输入完成后自动跳转到下一个输入框
OutlinedTextField(
    // ...
    keyboardOptions = KeyboardOptions(
        imeAction = ImeAction.Next
    ),
    keyboardActions = KeyboardActions(
        onNext = { verificationCodeFocusRequester.requestFocus() }
    )
)
```

---

## 8. 响应式设计

### 8.1 横屏适配

```
横屏时，界面分为左右两部分：

┌─────────────────────────────────────────────────────────────┐
│                                                              │
│  ┌─────────────────┐    ┌─────────────────────────────────┐ │
│  │                 │    │                                  │ │
│  │     Logo        │    │         登录表单                  │ │
│  │   MindMirror    │    │                                  │ │
│  │   心理镜像       │    │   [手机号输入框]                 │ │
│  │                 │    │   [验证码输入框]                 │ │
│  │   插图          │    │   [登录按钮]                     │ │
│  │                 │    │                                  │ │
│  └─────────────────┘    └─────────────────────────────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 8.2 平板适配

- 最小宽度：600dp
- 表单最大宽度：400dp
- 居中显示

---

## 9. 动效设计

### 9.1 页面进入

```kotlin
// Fade In + Slide Up
AnimatedVisibility(
    visible = true,
    enter = fadeIn(animationSpec = tween(300)) + 
            slideInVertically(
                initialOffsetY = { it / 4 },
                animationSpec = tween(300)
            )
) {
    LoginContent()
}
```

### 9.2 按钮点击

```kotlin
// Scale Down on Press
val scale by animateFloatAsState(
    if (isPressed) 0.95f else 1f,
    animationSpec = tween(100)
)

Box(
    modifier = Modifier
        .scale(scale)
        .clickable(onClick = onClick)
) {
    ButtonContent()
}
```

### 9.3 验证码倒计时

```kotlin
// 数字滚动动画
AnimatedContent(
    targetState = countdownSeconds,
    transitionSpec = {
        slideInVertically { height -> height } + 
        fadeIn() togetherWith 
        slideOutVertically { height -> -height } + 
        fadeOut()
    }
) { seconds ->
    Text("${seconds}s")
}
```

---

## 10. 测试要点

### 10.1 功能测试

- [ ] 手机号格式验证
- [ ] 验证码发送与倒计时
- [ ] 密码可见性切换
- [ ] 表单提交验证
- [ ] 登录成功跳转
- [ ] 错误提示展示

### 10.2 无障碍测试

- [ ] TalkBack 朗读顺序
- [ ] 焦点管理
- [ ] 内容描述完整性

### 10.3 兼容性测试

- [ ] 不同屏幕尺寸
- [ ] 横竖屏切换
- [ ] 深色模式
- [ ] 字体缩放

---

*文档版本：1.0*  
*创建时间：2026-03-24*  
*负责人：ui-designer*  
*状态：✅ 已完成*
