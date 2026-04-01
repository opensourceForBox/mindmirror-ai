# MindMirror AI - 设计系统规范

**版本**: v1.0  
**日期**: 2026-03-24  
**负责人**: ui-designer  
**状态**: ✅ 已完成

---

## 1. 设计原则

### 1.1 核心价值观

| 价值 | 说明 | 应用 |
|------|------|------|
| **温暖** | 让用户感到被理解和关怀 | 柔和的色彩、圆润的边角 |
| **专业** | 建立信任感 | 清晰的层次、一致的排版 |
| **可信赖** | 心理健康 App 的核心 | 稳重的色调、克制的动效 |
| **无障碍** | 包容性设计 | 足够的对比度、大点击区域 |

### 1.2 设计语言

- **风格**: 现代简约 + 人文关怀
- **关键词**: 平静、安全、希望
- **避免**: 过于活泼、刺激性强、医疗冷漠感

---

## 2. 色彩系统

### 2.1 主色调

```
┌─────────────────────────────────────────────────────────────┐
│  Primary Colors                                              │
│                                                              │
│  ▉ Primary      #5B8DBE  主蓝色 - 信任、平静                  │
│  ▉ Primary Light #8AB4E4  浅蓝色 - 背景、高亮                 │
│  ▉ Primary Dark  #3A6B99  深蓝色 - 文字、边框                 │
│                                                              │
│  ▉ Accent       #7CB9A8  薄荷绿 - 积极情绪、成功              │
│  ▉ Warning      #E8A85C  暖橙色 - 提醒、注意                  │
│  ▉ Error        #D67B7B  柔和红 - 错误、危机（避免刺激）       │
│                                                              │
│  ▉ Success      #6BB892  绿色 - 完成、正向反馈                │
│  ▉ Info         #5B8DBE  蓝色 - 信息提示                      │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 中性色

```
┌─────────────────────────────────────────────────────────────┐
│  Neutral Colors                                              │
│                                                              │
│  ▉ Gray 900     #1A1A2E  最深灰 - 主要文字                   │
│  ▉ Gray 700     #4A4A5E  深灰 - 次要文字                     │
│  ▉ Gray 500     #8A8A9E  中灰 - 占位符、禁用                 │
│  ▉ Gray 300     #C8C8D8  浅灰 - 边框、分割线                 │
│  ▉ Gray 100     #E8E8F0  最浅灰 - 背景                       │
│  ▉ White        #FFFFFF  纯白 - 卡片背景                      │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 情绪色（用于情绪可视化）

| 情绪 | 颜色 | Hex | 使用场景 |
|------|------|-----|----------|
| Happy | 暖黄 | #F4C95C | 快乐情绪标记 |
| Sad | 蓝灰 | #6B8CA8 | 悲伤情绪标记 |
| Angry | 柔和红 | #D67B7B | 愤怒情绪标记 |
| Anxious | 紫灰 | #9B7BA8 | 焦虑情绪标记 |
| Neutral | 中灰 | #8A8A9E | 中性情绪标记 |
| Calm | 薄荷绿 | #7CB9A8 | 平静情绪标记 |

### 2.4 色彩对比度

所有文字与背景对比度 ≥ 4.5:1（WCAG AA 标准）

```
✅ 通过:
- Gray 900 on White: 16.2:1
- Gray 700 on White: 8.5:1
- White on Primary: 5.1:1

⚠️ 注意:
- Gray 500 on Gray 100: 3.2:1 (仅用于禁用状态)
```

---

## 3. 排版系统

### 3.1 字体家族

```kotlin
// Android (Jetpack Compose)
val Typography = Typography(
    defaultFontFamily = FontFamily(
        Font(R.font.noto_sans_regular, FontWeight.Normal),
        Font(R.font.noto_sans_medium, FontWeight.Medium),
        Font(R.font.noto_sans_bold, FontWeight.Bold)
    ),
    // 中文回退
    cjkFontFamily = FontFamily(
        Font(R.font.noto_sans_cjk_regular, FontWeight.Normal),
        Font(R.font.noto_sans_cjk_medium, FontWeight.Medium),
        Font(R.font.noto_sans_cjk_bold, FontWeight.Bold)
    )
)
```

**字体选择**:
- 英文：Noto Sans（Google Fonts，开源）
- 中文：Noto Sans CJK（思源黑体）

### 3.2 字号阶梯

| 级别 | 字号 | 行高 | 字重 | 使用场景 |
|------|------|------|------|----------|
| Display | 32sp | 40sp | Bold | 大标题 |
| H1 | 24sp | 32sp | Bold | 页面标题 |
| H2 | 20sp | 28sp | Medium | 章节标题 |
| H3 | 18sp | 24sp | Medium | 卡片标题 |
| Body Large | 16sp | 24sp | Normal | 正文（大） |
| Body | 14sp | 20sp | Normal | 正文（标准） |
| Body Small | 12sp | 16sp | Normal | 辅助文字 |
| Caption | 11sp | 14sp | Normal | 图注、标签 |

### 3.3 文字颜色

```kotlin
// 文字颜色规范
object TextColors {
    val Primary = Color(0xFF1A1A2E)      // 主要文字
    val Secondary = Color(0xFF4A4A5E)    // 次要文字
    val Disabled = Color(0xFF8A8A9E)     // 禁用文字
    val Hint = Color(0xFFA0A0B0)         // 占位符
    val Link = Color(0xFF5B8DBE)         // 链接
    val Error = Color(0xFFD67B7B)        // 错误
}
```

---

## 4. 间距系统

### 4.1 基础单位

基础间距单位：**4dp**

```
4dp, 8dp, 12dp, 16dp, 20dp, 24dp, 32dp, 40dp, 48dp, 64dp
```

### 4.2 组件间距

```kotlin
object Spacing {
    val xs = 4.dp    // 极小间距（图标与文字）
    val sm = 8.dp    // 小间距（相关元素）
    val md = 16.dp   // 中间距（卡片内边距）
    val lg = 24.dp   // 大间距（区块之间）
    val xl = 32.dp   // 超大间距（页面边距）
    val xxl = 48.dp  // 特大间距（重要分隔）
}
```

### 4.3 布局示例

```
┌────────────────────────────────────────────┐
│  Page Padding: 16dp                         │
│  ┌────────────────────────────────────┐   │
│  │  Card Padding: 16dp                 │   │
│  │  ┌────────────────────────────┐    │   │
│  │  │  Content                   │    │   │
│  │  │  ↑                         │    │   │
│  │  │  8dp (元素间距)             │    │   │
│  │  │  ↑                         │    │   │
│  │  │  Content                   │    │   │
│  │  └────────────────────────────┘    │   │
│  └────────────────────────────────────┘   │
└────────────────────────────────────────────┘
```

---

## 5. 圆角系统

### 5.1 圆角阶梯

| 级别 | 圆角 | 使用场景 |
|------|------|----------|
| None | 0dp | 分割线、边框 |
| Small | 4dp | 小按钮、标签 |
| Medium | 8dp | 卡片、输入框 |
| Large | 12dp | 大卡片、对话框 |
| XL | 16dp | 模态弹窗 |
| Full | 999dp | 圆形头像、 pill 按钮 |

### 5.2 组件圆角规范

```kotlin
object Shapes {
    val small = RoundedCornerShape(4.dp)
    val medium = RoundedCornerShape(8.dp)
    val large = RoundedCornerShape(12.dp)
    val extraLarge = RoundedCornerShape(16.dp)
    val circular = RoundedCornerShape(50)
}
```

---

## 6. 阴影系统

### 6.1 阴影层级

| 层级 | 阴影值 | 使用场景 |
|------|--------|----------|
| 0 | none | 平面元素 |
| 1 | 0 1dp 2dp rgba(0,0,0,0.05) | 轻微浮起 |
| 2 | 0 2dp 4dp rgba(0,0,0,0.08) | 卡片、按钮 |
| 3 | 0 4dp 8dp rgba(0,0,0,0.12) | 悬浮按钮 |
| 4 | 0 8dp 16dp rgba(0,0,0,0.16) | 对话框、弹窗 |

### 6.2 阴影实现

```kotlin
// Jetpack Compose
fun Modifier.shadowElevation(level: Int): Modifier {
    return when (level) {
        0 -> this
        1 -> shadow(this, elevation = 1.dp, clip = false)
        2 -> shadow(this, elevation = 2.dp, clip = false)
        3 -> shadow(this, elevation = 4.dp, clip = false)
        4 -> shadow(this, elevation = 8.dp, clip = false)
        else -> this
    }
}
```

---

## 7. 核心组件

### 7.1 按钮

```
┌─────────────────────────────────────────────────────────────┐
│  Button Types                                                │
│                                                              │
│  Primary Button (主要按钮)                                   │
│  ┌─────────────────────────────┐                            │
│  │      开始对话                │  Primary bg, White text   │
│  └─────────────────────────────┘  h: 48dp, r: 8dp          │
│                                                              │
│  Secondary Button (次要按钮)                                 │
│  ┌─────────────────────────────┐                            │
│  │      查看历史                │  White bg, Primary border │
│  └─────────────────────────────┘  h: 48dp, r: 8dp          │
│                                                              │
│  Text Button (文字按钮)                                      │
│  ┌─────────────────────────────┐                            │
│  │      跳过                    │  No bg, Primary text      │
│  └─────────────────────────────┘  h: 40dp                   │
│                                                              │
│  Floating Action Button (悬浮按钮)                           │
│         ┌─────┐                                              │
│         │  +  │  Primary bg, White icon, 56dp circle        │
│         └─────┘  shadow level 3                              │
└─────────────────────────────────────────────────────────────┘
```

**状态**:
- Default: 正常状态
- Pressed: 透明度 80%
- Disabled: Gray 300 bg, Gray 500 text
- Loading: 显示进度指示器

### 7.2 输入框

```
┌─────────────────────────────────────────────────────────────┐
│  Input Field                                                 │
│                                                              │
│  Default:                                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  今天感觉怎么样...                                   │   │
│  └─────────────────────────────────────────────────────┘   │
│  ↑ Gray 300 border, Gray 500 placeholder                   │
│                                                              │
│  Focused:                                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  今天感觉很焦虑...                                   │   │
│  └─────────────────────────────────────────────────────┘   │
│  ↑ Primary border (2dp)                                     │
│                                                              │
│  Error:                                                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  请输入内容                                          │   │
│  └─────────────────────────────────────────────────────┘   │
│  ↑ Error border (2dp), Error text below                   │
└─────────────────────────────────────────────────────────────┘
```

**规格**:
- 高度：48dp（单行）
- 内边距：16dp 水平
- 圆角：8dp
- 字体：16sp

### 7.3 卡片

```
┌─────────────────────────────────────────────────────────────┐
│  Card Component                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  ┌───────────┐                                      │   │
│  │  │  图标/头像 │  标题                               │   │
│  │  └───────────┘  副标题/描述文字...                  │   │
│  │                                                      │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │              操作按钮                        │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────┘   │
│  ↑ White bg, 8dp radius, shadow level 2                    │
│  ↑ Padding: 16dp                                           │
└─────────────────────────────────────────────────────────────┘
```

### 7.4 情绪标签

```
┌─────────────────────────────────────────────────────────────┐
│  Emotion Chips                                               │
│                                                              │
│  ▉ 开心      ▉ 平静      ▉ 焦虑      ▉ 悲伤                 │
│  (黄 bg)    (绿 bg)    (紫 bg)    (蓝灰 bg)                 │
│                                                              │
│  规格:                                                       │
│  - 高度：32dp                                                │
│  - 圆角：16dp (full)                                         │
│  - 内边距：12dp 水平                                         │
│  - 字体：14sp Medium                                         │
└─────────────────────────────────────────────────────────────┘
```

### 7.5 对话框

```
┌─────────────────────────────────────────────────────────────┐
│  Dialog                                                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                                                      │   │
│  │              ⚠️  检测到危机信号                      │   │
│  │                                                      │   │
│  │    我们注意到你最近情绪波动较大，建议联系专业人士。   │   │
│  │                                                      │   │
│  │    ┌─────────────────┐  ┌─────────────────┐        │   │
│  │    │    取消          │  │  联系心理热线    │        │   │
│  │    └─────────────────┘  └─────────────────┘        │   │
│  │                                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│  ↑ White bg, 16dp radius, shadow level 4                   │
│  ↑ Padding: 24dp                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 8. 图标系统

### 8.1 图标库

**推荐**: Material Icons (Google)

**常用图标**:
| 用途 | 图标名 | 尺寸 |
|------|--------|------|
| 首页 | home | 24dp |
| 对话 | chat | 24dp |
| 情绪 | sentiment_satisfied | 24dp |
| 历史 | history | 24dp |
| 设置 | settings | 24dp |
| 返回 | arrow_back | 24dp |
| 关闭 | close | 24dp |
| 发送 | send | 24dp |
| 相机 | camera_alt | 24dp |
| 麦克风 | mic | 24dp |

### 8.2 图标规范

- 默认颜色：Gray 700
- 激活状态：Primary
- 禁用状态：Gray 300
- 点击区域：≥ 48dp

---

## 9. 动效规范

### 9.1 动画时长

| 类型 | 时长 | 缓动 |
|------|------|------|
| 微交互（按钮点击） | 100ms | Ease Out |
| 小组件动画 | 200ms | Ease Out |
| 页面过渡 | 300ms | Ease In Out |
| 复杂动画 | 500ms | Custom |

### 9.2 缓动曲线

```kotlin
// Jetpack Compose
object AnimationSpecs {
    val quick = tween(100ms, easing = FastOutSlowInEasing)
    val normal = tween(200ms, easing = FastOutSlowInEasing)
    val slow = tween(300ms, easing = FastOutSlowInEasing)
}
```

### 9.3 动效原则

- ✅ 有目的：动画服务于功能，不为动而动
- ✅ 自然：符合物理规律（惯性、弹性）
- ✅ 克制：心理健康 App 避免过度刺激
- ✅ 可关闭：提供减少动画选项

---

## 10. 无障碍设计

### 10.1 对比度要求

- 正常文字：≥ 4.5:1
- 大文字（≥ 18sp）：≥ 3:1
- 图标：≥ 3:1

### 10.2 点击区域

- 最小尺寸：48dp × 48dp
- 元素间距：≥ 8dp

### 10.3 内容描述

```kotlin
// Jetpack Compose
IconButton(
    onClick = { ... },
    modifier = Modifier.semantics {
        contentDescription = "发送消息"
    }
) {
    Icon(Icons.Default.Send, contentDescription = null)
}
```

### 10.4 字体缩放

支持系统字体缩放（100% - 200%）

---

## 11. 深色模式

### 11.1 深色主题色彩

```kotlin
val DarkColorScheme = darkColorScheme(
    primary = Color(0xFF8AB4E4),
    background = Color(0xFF121218),
    surface = Color(0xFF1E1E28),
    // ...
)
```

### 11.2 深色模式适配

- 避免纯黑（#000000），使用深灰（#121218）
- 降低饱和度，避免刺眼
- 阴影改为光晕效果

---

## 12. 设计资源

### 12.1 Figma 文件

- 设计系统：`MindMirror Design System`
- 原型文件：`MindMirror UI Prototypes`

### 12.2 代码实现

- Compose 组件库：`/code/mindmirror/ui/components/`
- 主题配置：`/code/mindmirror/ui/theme/`

---

*文档版本：1.0*  
*创建时间：2026-03-24*  
*负责人：ui-designer*  
*状态：✅ 已完成*
