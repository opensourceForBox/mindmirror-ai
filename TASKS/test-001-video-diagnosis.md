# 任务：录像诊断功能测试

## 基本信息
- **任务 ID**: test-001-video-diagnosis
- **功能名称**: 录像诊断界面测试
- **优先级**: P0
- **依赖**: ui-001-video-diagnosis 完成
- **推荐模型**: qwen3.5-plus

---

## 测试范围

### 功能测试
- [ ] 页面加载和渲染
- [ ] 统计卡片数据展示
- [ ] 录像丢失列表展示
- [ ] 设备信息面板展示
- [ ] 重新诊断按钮交互

### 视觉测试
- [ ] 深色主题正确应用
- [ ] 配色符合参考图
- [ ] 响应式布局适配（手机/平板/桌面）
- [ ] 卡片悬停效果

### 交互测试
- [ ] 按钮点击反馈
- [ ] 列表项点击展开
- [ ] 状态标签呼吸动画
- [ ] 加载状态显示

---

## 测试用例

### 用例 1: 页面加载测试

```python
def test_page_load():
    """测试页面正常加载"""
    # Given
    page_url = "file:///root/.openclaw/workspace/canvas/ui-001-video-diagnosis/index.html"
    
    # When
    response = requests.get(page_url)
    
    # Then
    assert response.status_code == 200
    assert "<title>录像诊断 - 监控中心</title>" in response.text
    assert 'var(--primary-bg)' in response.text  # 检查 CSS 变量
```

### 用例 2: 统计卡片数据验证

```python
def test_stat_cards():
    """测试统计卡片数据正确显示"""
    # Given
    expected_stats = {
        "存储天数": "30 天",
        "录像总数": "720 个",
        "丢失录像": "12 个",
        "完整率": "98.3%"
    }
    
    # When
    page_content = read_html_file()
    
    # Then
    for label, value in expected_stats.items():
        assert label in page_content, f"缺少统计项：{label}"
        assert value in page_content, f"统计值错误：{label}"
```

### 用例 3: 配色方案验证

```python
def test_color_scheme():
    """测试配色方案是否符合参考图"""
    # Given
    expected_colors = {
        "--primary-bg": "#1a1a2e",
        "--card-bg": "#16213e",
        "--accent-color": "#00d9ff",
        "--danger-color": "#ff4757"
    }
    
    # When
    css_content = extract_css_from_html()
    
    # Then
    for var, color in expected_colors.items():
        assert f"{var}: {color}" in css_content, f"配色错误：{var}"
```

### 用例 4: 响应式布局测试

```python
def test_responsive_layout():
    """测试响应式布局"""
    # Given
    breakpoints = {
        "mobile": 375,
        "tablet": 768,
        "desktop": 1024
    }
    
    # When & Then
    for device, width in breakpoints.items():
        screenshot = capture_screenshot(width=width)
        assert screenshot is not None, f"{device} 截图失败"
        assert check_layout_correct(screenshot), f"{device} 布局错误"
```

### 用例 5: 交互效果测试

```python
def test_interaction_effects():
    """测试交互效果"""
    # Given
    page = load_page()
    
    # When - 悬停卡片
    card = page.find_element(".stat-card")
    card.hover()
    
    # Then - 检查悬停效果
    transform = card.get_css_value("transform")
    assert "translateY" in transform, "卡片悬停无上浮效果"
    
    # When - 点击重新诊断按钮
    btn = page.find_element(".refresh-btn")
    btn.click()
    
    # Then - 检查按钮状态变化
    btn_text = btn.text
    assert "诊断中" in btn_text, "按钮点击无状态变化"
```

---

## 测试数据

### 有效数据
```json
{
  "device_name": "东门监控摄像头 #001",
  "storage_days": 30,
  "total_videos": 720,
  "lost_videos": 12,
  "completion_rate": "98.3%"
}
```

### 预期 UI 元素
```json
{
  "header": ["录像诊断监控中心", "诊断异常"],
  "stat_cards": ["存储天数", "录像总数", "丢失录像", "完整率"],
  "loss_list": ["丢失时间", "丢失原因", "丢失时长"],
  "info_panel": ["设备名称", "IP 地址", "在线状态"]
}
```

---

## 输出要求

### 文件结构
```
test-reports/video-diagnosis/
├── test_ui.py            # UI 测试用例
├── test_visual.py        # 视觉测试用例
├── test_interaction.py   # 交互测试用例
├── conftest.py           # Pytest 配置
├── test_data.json        # 测试数据
├── screenshots/          # 测试截图
│   ├── mobile.png
│   ├── tablet.png
│   └── desktop.png
└── test_report.md        # 测试报告
```

### 测试报告
`test_report.md` 必须包含：
- [ ] 测试概述（测试范围、环境）
- [ ] 测试结果汇总（通过/失败用例数）
- [ ] 失败用例详情（错误信息、截图）
- [ ] 视觉测试结果（配色、布局）
- [ ] 性能测试结果（加载时间）
- [ ] 遗留问题和建议

---

## 验收标准

- [ ] 所有 P0 测试用例通过
- [ ] 测试覆盖率 ≥ 80%
- [ ] 视觉测试通过（配色、布局符合参考图）
- [ ] 响应式测试通过（3 个断点都正常）
- [ ] 测试报告完整、清晰
- [ ] 测试代码可重复执行

---

## 注意事项

- ⚠️ 测试数据用 Mock，不要依赖真实后端
- ⚠️ 测试用例要独立，不互相依赖
- ⚠️ 截图保存清晰，标注测试场景
- ⚠️ 测试报告用 Markdown 格式，便于阅读
