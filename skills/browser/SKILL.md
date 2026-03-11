# Browser 技能 - Brave 浏览器自动化

智能体通过 Brave 浏览器进行网页浏览、截图、交互等操作。

## 环境配置

**浏览器路径**: `/usr/bin/brave-browser`

## 使用方法

### 1. 打开网页

```javascript
await browser.open({
    targetUrl: 'https://example.com',
    profile: 'openclaw'
});
```

### 2. 网页快照

```javascript
const snapshot = await browser.snapshot({
    action: 'snapshot',
    refs: 'aria'  // 或 'role'
});
```

### 3. 点击元素

```javascript
await browser.act({
    action: 'act',
    request: {
        kind: 'click',
        ref: 'e12'  // 从 snapshot 获取的元素引用
    }
});
```

### 4. 输入文本

```javascript
await browser.act({
    action: 'act',
    request: {
        kind: 'type',
        ref: 'e12',
        text: 'Hello World'
    }
});
```

### 5. 截图

```javascript
await browser.screenshot({
    action: 'screenshot',
    fullPage: true
});
```

### 6. 导航

```javascript
await browser.navigate({
    action: 'navigate',
    targetUrl: 'https://new-url.com'
});
```

## 完整示例

```javascript
// 1. 打开网页
await browser.open({
    targetUrl: 'https://www.example.com',
    profile: 'openclaw'
});

// 2. 获取快照
const snapshot = await browser.snapshot({
    action: 'snapshot',
    refs: 'aria'
});

// 3. 分析页面元素
console.log('页面元素:', snapshot);

// 4. 点击按钮
await browser.act({
    action: 'act',
    request: {
        kind: 'click',
        ref: 'e12'
    }
});

// 5. 输入文本
await browser.act({
    action: 'act',
    request: {
        kind: 'type',
        ref: 'e15',
        text: '搜索内容'
    }
});

// 6. 截图保存
await browser.screenshot({
    action: 'screenshot',
    fullPage: true
});
```

## Canvas 预览

配合 Canvas 使用，实现 UI 实时预览：

```javascript
// 1. 导航到 Canvas 页面
await canvas.navigate({
    action: 'navigate',
    url: 'file:///root/.openclaw/workspace/canvas/ui-001/index.html'
});

// 2. 截图查看
const snapshot = await canvas.snapshot({
    action: 'snapshot',
    outputFormat: 'png'
});
```

## 注意事项

- ✅ 使用 `profile: 'openclaw'` 使用隔离浏览器
- ✅ 使用 `refs: 'aria'` 获取稳定的元素引用
- ⚠️ 浏览器启动需要 2-3 秒
- ⚠️ 复杂页面加载可能需要 5-10 秒

## 相关文档

- [OpenClaw Browser 文档](https://docs.openclaw.ai/tools/browser)
- [Browser 工具参考](https://docs.openclaw.ai/tools/browser)
