# 开发任务 - 录像诊断 API

## 功能描述
实现录像诊断功能的后端 API，分析上传的视频文件并返回质量问题诊断结果。

## API 端点

### 1. 上传视频
```
POST /api/video/upload
Content-Type: multipart/form-data
Response: { video_id, filename, status }
```

### 2. 开始诊断
```
POST /api/video/{video_id}/diagnose
Response: { task_id, status: "processing" }
```

### 3. 查询诊断结果
```
GET /api/video/{video_id}/result
Response: {
  score,
  issues: [{ type, severity, description }],
  suggestions: []
}
```

### 4. 历史记录
```
GET /api/videos
Response: [{ video_id, filename, score, created_at }]
```

## 诊断规则（简化版）

| 问题类型 | 检测逻辑 |
|---------|---------|
| 画面模糊 | 分析帧的清晰度（拉普拉斯方差） |
| 音频不同步 | 检测音画时间差 |
| 帧率过低 | 分析视频 FPS |
| 分辨率过低 | 检查视频宽高 |
| 编码问题 | 检查编解码器兼容性 |

## 输出要求
- **目录**: `code/video-diagnosis/`
- **文件**:
  - `app.py` - Flask 应用入口
  - `models.py` - 数据模型（Video, DiagnosisResult）
  - `routes.py` - API 路由
  - `analyzer.py` - 视频分析核心逻辑
  - `requirements.txt` - Python 依赖
  - `README.md` - 运行说明

## 依赖
- UI 设计：`designs/video-diagnosis/`（用于理解前端需求）

## 推荐模型
- **模型**: `glm-5`
- **理由**: 复杂后端逻辑，涉及视频处理算法，需要高逻辑一致性

## 技术建议
- 使用 Flask 3.x
- 视频处理：使用 `ffmpeg-python` 或 `opencv-python`
- 文件存储：本地临时目录（生产环境可改为云存储）
- 异步处理：使用 Celery 或后台线程（诊断可能耗时）

## 验收标准
- 所有 API 端点可正常访问
- 能够上传视频文件并返回诊断结果
- 诊断逻辑合理（至少能检测帧率、分辨率）
- 代码有必要的注释
- README 包含清晰的启动和测试说明
