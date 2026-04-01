# MindMirror AI - 对话界面原型

**版本**: v1.0  
**日期**: 2026-03-24  
**负责人**: ui-designer  
**状态**: ✅ 已完成

---

## 1. 界面概述

**功能**: 用户与 AI 心理医生进行实时对话  
**入口**: 首页"开始对话"按钮 / 底部导航"对话"  
**目标**: 提供流畅、自然的对话体验，支持文字、语音输入

---

## 2. 界面布局

### 2.1 对话界面（竖屏）

```
┌─────────────────────────────────────────────┐
│  ←      与 AI 对话                  ⋮ 更多   │
│         今天感觉怎么样？                     │
├─────────────────────────────────────────────┤
│                                              │
│  ┌─────────────────────────────────────────┐│
│  │ 🤖 MindMirror AI                        ││
│  │                                         ││
│  │ 你好，小明。我是你的 AI 心理陪伴者。     ││
│  │                                         ││
│  │ 今天感觉怎么样？有什么想和我聊聊的吗？  ││
│  │                                         ││
│  │              11:00                      ││
│  └─────────────────────────────────────────┘│
│                                              │
│  ┌─────────────────────────────────────────┐│
│  │              你今天看起来有点焦虑       ││
│  │                                         ││
│  │                              11:01  👤 ││
│  └─────────────────────────────────────────┘│
│                                              │
│  ┌─────────────────────────────────────────┐│
│  │ 🤖 MindMirror AI                        ││
│  │                                         ││
│  │ 我理解你的感受。焦虑是一种常见的情绪... ││
│  │                                         ││
│  │ 想具体说说是什么让你感到焦虑吗？         ││
│  │                                         ││
│  │  ┌─────────────┐ ┌─────────────┐       ││
│  │  │ 💡 工作压力  │ │ 💡 人际关系 │       ││
│  │  └─────────────┘ └─────────────┘       ││
│  │  ┌─────────────┐ ┌─────────────┐       ││
│  │  │ 💡 健康问题  │ │ 💡 其他     │       ││
│  │  └─────────────┘ └─────────────┘       ││
│  │                                         ││
│  │              11:01                      ││
│  └─────────────────────────────────────────┘│
│                                              │
│  ┌─────────────────────────────────────────┐│
│  │ 🤖 MindMirror AI                        ││
│  │                                         ││
│  │ 我们可以一起分析一下...                 ││
│  │                                         ││
│  │              11:02                      ││
│  └─────────────────────────────────────────┘│
│                                              │
├─────────────────────────────────────────────┤
│  ┌─────────────────────────────────────┐ 🎤 │
│  │  输入消息...                         │    │
│  └─────────────────────────────────────┘ 📎 │
│                                              │
│  ┌─────────────────────────────────────────┐│
│  │              💬 发送                     ││
│  └─────────────────────────────────────────┘│
└─────────────────────────────────────────────┘
```

### 2.2 对话界面（横屏）

```
┌─────────────────────────────────────────────────────────────┐
│  ←  与 AI 对话                                      ⋮ 更多   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────┐  ┌───────────────────────────────────┐ │
│  │                 │  │                                   │ │
│  │   情绪状态      │  │        对话内容区                  │ │
│  │                 │  │                                   │ │
│  │   😰 焦虑       │  │  [AI 消息]                         │ │
│  │   65%           │  │  [用户消息]                        │ │
│  │                 │  │  [AI 消息 + 建议]                  │ │
│  │   ────────      │  │                                   │ │
│  │                 │  │                                   │ │
│  │   建议：        │  │                                   │ │
│  │   深呼吸练习    │  │                                   │ │
│  │                 │  │                                   │ │
│  └─────────────────┘  └───────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐ 🎤 │
│  │  输入消息...                                        │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 核心组件

### 3.1 消息气泡

**AI 消息**:
```
┌─────────────────────────────────────────────┐
│ 🤖 MindMirror AI                            │
│                                             │
│ 你好，我是你的 AI 心理陪伴者。               │
│ 今天感觉怎么样？                            │
│                                             │
│              11:00                          │
└─────────────────────────────────────────────┘
```

**用户消息**:
```
┌─────────────────────────────────────────────┐
│              我今天感觉很焦虑        👤     │
│                                             │
│                              11:01          │
└─────────────────────────────────────────────┘
```

**规格**:
- AI 消息背景：Gray 100
- 用户消息背景：Primary Light (#8AB4E4)
- 圆角：16dp（外侧）/ 4dp（内侧）
- 最大宽度：75%
- 内边距：12dp

### 3.2 建议按钮（快速回复）

```
┌─────────────┐ ┌─────────────┐
│ 💡 工作压力  │ │ 💡 人际关系 │
└─────────────┘ └─────────────┘
┌─────────────┐ ┌─────────────┐
│ 💡 健康问题  │ │ 💡 其他     │
└─────────────┘ └─────────────┘
```

**规格**:
- 高度：36dp
- 圆角：18dp（full）
- 背景：White
- 边框：Primary 1dp
- 文字：Primary，14sp

### 3.3 输入区域

```
┌─────────────────────────────────────────────┐
│  ┌─────────────────────────────────────┐ 🎤 │
│  │  输入消息...                         │    │
│  └─────────────────────────────────────┘ 📎 │
│                                             │
│  ┌─────────────────────────────────────────┐│
│  │              💬 发送                     ││
│  └─────────────────────────────────────────┘│
└─────────────────────────────────────────────┘
```

**状态**:
- Default: 输入框 + 麦克风图标
- Typing: 输入框激活，发送按钮出现
- Recording: 录音中动画

### 3.4 录音状态

```
┌─────────────────────────────────────────────┐
│                                              │
│         ┌─────────────────┐                 │
│         │                 │                 │
│         │     🎤          │                 │
│         │                 │                 │
│         │   正在听你说...  │                 │
│         │                 │                 │
│         │   ▓▓▓░░░░░░░    │                 │
│         │   00:03         │                 │
│         │                 │                 │
│         └─────────────────┘                 │
│                                              │
│              [结束录音]                      │
│                                              │
└─────────────────────────────────────────────┘
```

---

## 4. 交互说明

### 4.1 消息发送流程

```
用户输入 → 点击发送 → 
  显示"发送中"状态 → 
  收到 AI 响应 → 
  流式显示 AI 回复（逐字） → 
  显示建议按钮
```

**流式显示动画**:
```kotlin
// 逐字显示 AI 回复
@Composable
fun StreamingText(
    text: String,
    speed: Int = 30 // 每字间隔毫秒
) {
    var displayedText by remember { mutableStateOf("") }
    
    LaunchedEffect(text) {
        displayedText = ""
        text.forEach { char ->
            displayedText += char
            delay(speed)
        }
    }
    
    Text(displayedText)
}
```

### 4.2 快速回复

```
用户点击建议按钮 → 
  按钮内容自动填充到输入框 → 
  自动发送（或确认后发送）
```

### 4.3 语音输入

```
点击麦克风 → 开始录音 → 
  显示录音动画 → 
  点击结束/超时自动结束 → 
  语音转文字 → 
  显示转录结果 → 
  确认后发送
```

### 4.4 情绪检测提示

当检测到用户情绪波动时：

```
┌─────────────────────────────────────────────┐
│  ⚠️  情绪检测                               │
│                                             │
│  我们注意到你现在的情绪可能比较低落。       │
│                                             │
│  ┌─────────────┐  ┌─────────────┐         │
│  │    知道了    │  │  需要帮助   │         │
│  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────┘
```

---

## 5. 打字指示器

```
┌─────────────────────────────────────────────┐
│ 🤖 MindMirror AI                            │
│                                             │
│  ●  ●  ●                                    │
│                                             │
└─────────────────────────────────────────────┘
```

**动画**:
```kotlin
@Composable
fun TypingIndicator() {
    Row(
        horizontalArrangement = Arrangement.spacedBy(4.dp),
        modifier = Modifier.padding(16.dp)
    ) {
        repeat(3) { index ->
            Box(
                modifier = Modifier
                    .size(8.dp)
                    .background(
                        color = MindMirrorColors.gray500,
                        shape = CircleShape
                    )
                    .animate(
                        animation = infiniteRepeatable(
                            animation = tween(
                                durationMillis = 600,
                                easing = FastOutSlowInEasing
                            ),
                            repeatMode = RepeatMode.Reverse
                        ),
                        delayMillis = index * 200
                    ) { progress ->
                        scale(progress)
                    }
            )
        }
    }
}
```

---

## 6. 危机干预界面

当检测到危机信号时：

```
┌─────────────────────────────────────────────┐
│  ⚠️  重要提示                               │
│                                             │
│  我注意到你提到了一些让我担心的内容。       │
│                                             │
│  你并不孤单，我们都在这里帮助你。           │
│                                             │
│  ┌─────────────────────────────────────────┐│
│  │  📞 心理援助热线                        ││
│  │     400-161-9995 (24 小时)               ││
│  │                                         ││
│  │  💬 联系紧急联系人                      ││
│  │                                         ││
│  │  🧘 深呼吸练习                          ││
│  └─────────────────────────────────────────┘│
│                                             │
│  ┌─────────────────────────────────────────┐│
│  │         我理解了，谢谢关心              ││
│  └─────────────────────────────────────────┘│
└─────────────────────────────────────────────┘
```

---

## 7. ViewModel

```kotlin
@HiltViewModel
class ChatViewModel @Inject constructor(
    private val chatRepository: ChatRepository,
    private val emotionRepository: EmotionRepository,
    private val crisisRepository: CrisisRepository
) : ViewModel() {
    
    val uiState: StateFlow<ChatUiState> = _uiState.asStateFlow()
    private val _uiState = MutableStateFlow(ChatUiState())
    
    private val _messages = MutableStateFlow<List<Message>>(emptyList())
    val messages: StateFlow<List<Message>> = _messages.asStateFlow()
    
    fun sendMessage(content: String) {
        viewModelScope.launch {
            // 添加用户消息
            val userMessage = Message(
                id = UUID.randomUUID().toString(),
                role = "user",
                content = content,
                timestamp = System.currentTimeMillis()
            )
            _messages.value = _messages.value + userMessage
            
            // 显示打字指示器
            _uiState.update { it.copy(isAiTyping = true) }
            
            try {
                // 调用 AI 服务
                val response = chatRepository.sendMessage(
                    conversationId = getOrCreateConversationId(),
                    message = content,
                    emotionState = _uiState.value.currentEmotion
                )
                
                // 危机检测
                if (response.crisisDetected) {
                    _uiState.update { 
                        it.copy(
                            crisisAlert = response.crisisInfo,
                            isAiTyping = false
                        ) 
                    }
                    return@launch
                }
                
                // 流式显示 AI 回复
                _uiState.update { it.copy(isAiTyping = false) }
                
                val aiMessage = Message(
                    id = response.messageId,
                    role = "assistant",
                    content = response.content,
                    suggestions = response.suggestions,
                    timestamp = System.currentTimeMillis()
                )
                _messages.value = _messages.value + aiMessage
                
            } catch (e: Exception) {
                _uiState.update { 
                    it.copy(
                        isAiTyping = false,
                        error = e.message
                    ) 
                }
            }
        }
    }
    
    fun startVoiceInput() {
        _uiState.update { it.copy(isRecording = true) }
        // 开始录音...
    }
    
    fun stopVoiceInput() {
        _uiState.update { it.copy(isRecording = false) }
        // 处理录音...
    }
}

data class ChatUiState(
    val isLoading: Boolean = false,
    val isAiTyping: Boolean = false,
    val isRecording: Boolean = false,
    val currentEmotion: EmotionState? = null,
    val crisisAlert: CrisisInfo? = null,
    val error: String? = null,
    val inputValue: String = ""
)
```

---

## 8. WebSocket 流式对话

```kotlin
// WebSocket 连接管理
class ChatWebSocketManager @Inject constructor(
    private val websocketFactory: WebSocketFactory
) {
    private var webSocket: WebSocket? = null
    
    fun connect(token: String, callbacks: ChatCallbacks) {
        val request = Request.Builder()
            .url("wss://api.mindmirror.ai/api/v1/chat/stream?token=$token")
            .build()
        
        webSocket = websocketFactory.newWebSocket(request, object : WebSocketListener() {
            override fun onMessage(webSocket: WebSocket, text: String) {
                val message = Json.decodeFromString<StreamMessage>(text)
                
                when (message.type) {
                    "token" -> callbacks.onToken(message.data)
                    "complete" -> callbacks.onComplete(message.data)
                    "error" -> callbacks.onError(message.data)
                }
            }
            
            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                callbacks.onError(t.message)
            }
        })
    }
    
    fun send(message: ChatMessage) {
        webSocket?.send(Json.encodeToString(message))
    }
    
    fun disconnect() {
        webSocket?.close(1000, "Normal closure")
    }
}

interface ChatCallbacks {
    fun onToken(token: String)
    fun onComplete(data: CompleteData)
    fun onError(error: String)
}
```

---

## 9. 测试要点

### 9.1 功能测试

- [ ] 消息发送与接收
- [ ] 流式显示效果
- [ ] 建议按钮点击
- [ ] 语音输入
- [ ] 危机检测提示
- [ ] 历史记录加载

### 9.2 性能测试

- [ ] 消息列表滚动流畅
- [ ] 流式显示无卡顿
- [ ] WebSocket 重连机制

### 9.3 边界测试

- [ ] 长消息处理
- [ ] 网络断开处理
- [ ] 快速连续发送

---

*文档版本：1.0*  
*创建时间：2026-03-24*  
*负责人：ui-designer*  
*状态：✅ 已完成*
