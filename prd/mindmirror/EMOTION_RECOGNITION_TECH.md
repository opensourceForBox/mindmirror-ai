# MindMirror AI - 情绪识别技术方案

**版本**: v1.0  
**日期**: 2026-03-24  
**负责人**: ai-engineer  
**状态**: ✅ 已完成

---

## 1. 技术概述

### 1.1 目标

构建多模态情绪识别系统，通过视频（面部表情）和音频（语音特征）实时分析用户情绪状态，为 AI 心理对话提供上下文感知能力。

### 1.2 核心指标

| 指标 | 目标值 | 测量方式 |
|------|--------|----------|
| 情绪识别准确率 | ≥75% | 标准测试集 |
| 推理延迟 | <200ms | P95 延迟 |
| 危机信号召回率 | ≥90% | 危机场景测试 |
| 系统可用性 | ≥99% | 服务监控 |

### 1.3 情绪分类体系

采用 Ekman 基本情绪 + 心理状态扩展：

| 情绪类型 | 英文 | 效价范围 | 唤醒度范围 |
|---------|------|----------|-----------|
| 快乐 | happy | 0.5 ~ 1.0 | 0.3 ~ 0.8 |
| 悲伤 | sad | -1.0 ~ -0.3 | 0.1 ~ 0.5 |
| 愤怒 | angry | -1.0 ~ -0.3 | 0.6 ~ 1.0 |
| 恐惧 | fearful | -0.8 ~ -0.2 | 0.7 ~ 1.0 |
| 惊讶 | surprised | -0.2 ~ 0.5 | 0.6 ~ 1.0 |
| 厌恶 | disgusted | -1.0 ~ -0.4 | 0.4 ~ 0.8 |
| 中性 | neutral | -0.2 ~ 0.2 | 0.1 ~ 0.4 |
| **焦虑** | anxious | -0.7 ~ -0.1 | 0.6 ~ 0.9 |
| **抑郁** | depressed | -1.0 ~ -0.4 | 0.1 ~ 0.3 |

---

## 2. 视频情绪识别方案

### 2.1 模型选型对比

#### 方案 A: Tavus Raven-1 (推荐)

**优势**:
- ✅ 专为心理场景优化，对微表情识别准确率高
- ✅ 支持边缘部署，推理延迟低（~80ms）
- ✅ 提供焦虑/抑郁等心理状态检测
- ✅ 商业授权清晰，支持私有化部署

**劣势**:
- ❌ 商业授权费用较高
- ❌ 模型较大（~500MB）

**准确率预估**: 78-82%  
**推理延迟**: 80-120ms (边缘) / 150-200ms (云端)  
**成本**: $0.002/次调用 或 $5000/月（无限）

---

#### 方案 B: GPT-4o Vision

**优势**:
- ✅ 多模态理解能力强
- ✅ 无需训练，开箱即用
- ✅ API 调用简单

**劣势**:
- ❌ 延迟较高（300-500ms）
- ❌ 成本较高（$0.01/张）
- ❌ 数据隐私问题（需上传到 OpenAI）
- ❌ 无法针对心理场景微调

**准确率预估**: 70-75%  
**推理延迟**: 300-500ms  
**成本**: $0.01/张

---

#### 方案 C: 开源模型组合 (FER + OpenFace)

**模型**:
- 面部表情识别：DeepFace (Facebook) 或 FER (PyTorch)
- 面部特征点：OpenFace 2.0
- 微表情分析：MIC 微调模型

**优势**:
- ✅ 开源免费
- ✅ 可完全私有化部署
- ✅ 可针对心理场景微调

**劣势**:
- ❌ 需要自建训练 pipeline
- ❌ 准确率略低（需大量微调）
- ❌ 维护成本高

**准确率预估**: 70-78%（微调后）  
**推理延迟**: 60-100ms (本地)  
**成本**: 开发人力 + GPU 服务器

---

#### 方案 D: 智谱 GLM-4V

**优势**:
- ✅ 国产模型，数据合规
- ✅ 支持中文场景
- ✅ 成本相对较低

**劣势**:
- ❌ 情绪识别非主打能力
- ❌ 延迟中等（200-300ms）

**准确率预估**: 72-76%  
**推理延迟**: 200-300ms  
**成本**: ¥0.005/次

---

### 2.2 推荐方案：Tavus Raven-1 + 开源降级

**主方案**: Tavus Raven-1（边缘部署）  
**降级方案**: DeepFace（本地备用）

**切换策略**:
```python
if raven1_available and latency < 200ms:
    use_raven1()
else:
    use_deepface()  # 降级方案
```

---

### 2.3 推理优化策略

#### 边缘计算架构

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  Android    │ →  │  边缘节点    │ →  │  云端备份   │
│  摄像头采集  │    │  (Raven-1)   │    │  (GLM-4V)   │
└─────────────┘    └──────────────┘    └─────────────┘
     30fps              <150ms            <300ms
```

#### 优化技术

1. **模型量化**: FP32 → INT8，减少 75% 模型体积，加速 2-3 倍
2. **帧采样**: 30fps → 5fps 分析，减少计算量 83%
3. **ROI 裁剪**: 仅处理面部区域，减少 90% 像素
4. **批处理**: 多用户请求合并批处理（云端）
5. **缓存策略**: 相同面部状态缓存 500ms

#### 性能基准

| 优化项 | 优化前 | 优化后 | 提升 |
|--------|--------|--------|------|
| 模型体积 | 500MB | 125MB | 75%↓ |
| 推理延迟 | 350ms | 120ms | 66%↓ |
| GPU 显存 | 4GB | 1GB | 75%↓ |

---

### 2.4 测试方案

#### 测试数据集

1. **公开数据集**:
   - FER2013 (35k 张)
   - AffectNet (450k 张)
   - RAF-DB (30k 张，含复合情绪)

2. **自建数据集** (心理场景):
   - 目标：10k 张标注图片
   - 标注维度：基本情绪 + 焦虑/抑郁程度
   - 来源：志愿者录制 + 专业演员

#### 评估指标

```python
metrics = {
    'accuracy': '总体准确率',
    'precision_per_class': '各类别精确率',
    'recall_per_class': '各类别召回率',
    'f1_score': 'F1 分数',
    'confusion_matrix': '混淆矩阵',
    'inference_latency_p50': 'P50 延迟',
    'inference_latency_p95': 'P95 延迟',
    'inference_latency_p99': 'P99 延迟'
}
```

---

## 3. 音频情绪识别方案

### 3.1 模型选型

#### 方案 A: OpenSMILE + 自定义分类器 (推荐)

**特征提取**: OpenSMILE (eGeMAPS 特征集)
- 88 维声学特征
- 包括：F0 基频、能量、MFCC、频谱等

**分类器**: XGBoost / LightGBM
- 输入：88 维特征
- 输出：9 类情绪 + valence/arousal

**优势**:
- ✅ 轻量级，可实时处理
- ✅ 可解释性强
- ✅ 易于部署

**准确率预估**: 72-78%

---

#### 方案 B: Wav2Vec 2.0 + 微调

**模型**: Facebook Wav2Vec 2.0
- 预训练：LibriSpeech 960 小时
- 微调：MSP-IMPROV / IEMOCAP

**优势**:
- ✅ 端到端，无需手工特征
- ✅ 准确率高

**劣势**:
- ❌ 模型大（~300MB）
- ❌ 推理延迟高

**准确率预估**: 75-80%  
**推理延迟**: 200-300ms

---

#### 方案 C: Azure Speech Emotion API

**优势**:
- ✅ 开箱即用
- ✅ 准确率高

**劣势**:
- ❌ 成本高
- ❌ 数据隐私问题
- ❌ 依赖网络

**成本**: $0.002/秒

---

### 3.2 推荐方案：OpenSMILE + XGBoost

**理由**:
- 轻量级，适合移动端/边缘部署
- 可解释性强，便于调试
- 成本低，可大规模部署

---

### 3.3 音频特征提取方案

#### 特征集：eGeMAPS (88 维)

| 特征类别 | 特征数 | 说明 |
|----------|--------|------|
| F0 (基频) | 14 | 音高相关 |
| Energy (能量) | 14 | 响度相关 |
| MFCC (1-4) | 20 | 频谱包络 |
| Spectral (频谱) | 32 | 频谱形状 |
| Voicing (发声) | 8 | 发声概率 |

#### 预处理流程

```
原始音频 → 降噪 → 预加重 → 分帧 → 特征提取 → 标准化 → 分类器
   ↓
16kHz, 16bit
   ↓
Wiener 滤波 / Spectral Subtraction
   ↓
25ms 帧长，10ms 帧移
   ↓
eGeMAPS 88 维
   ↓
Z-score 标准化
   ↓
XGBoost 分类
```

#### 降噪方案

1. **背景噪声抑制**: RNNoise (开源)
2. **回声消除**: WebRTC AEC
3. **自动增益控制**: WebRTC AGC

---

### 3.4 音频情绪识别 API

```python
POST /api/v1/emotion/audio/analyze

Request:
{
  "audio_chunk": "base64...",  # 2 秒音频片段
  "sample_rate": 16000,
  "channels": 1
}

Response:
{
  "emotion_type": "anxious",
  "confidence": 0.82,
  "valence": -0.4,
  "arousal": 0.7,
  "acoustic_features": {
    "pitch_mean": 220.5,
    "pitch_std": 45.2,
    "energy_mean": -25.3,
    "speech_rate": 5.2  # 音节/秒
  },
  "latency_ms": 85
}
```

---

## 4. 多模态融合策略

### 4.1 融合架构

采用**晚融合 (Late Fusion)** 策略：

```
视频流 → Raven-1 → 视频情绪分数 ─┐
                                 ├→ 加权融合 → 最终情绪
音频流 → OpenSMILE → 音频情绪分数 ─┘
```

**理由**:
- 视频和音频特征维度不同，早融合困难
- 晚融合允许独立优化两个模态
- 支持单模态降级（如摄像头关闭）

---

### 4.2 融合算法

#### 加权平均法

```python
def fuse_emotions(video_result, audio_result):
    # 动态权重：基于置信度
    video_weight = video_result.confidence
    audio_weight = audio_result.confidence
    
    # 归一化
    total_weight = video_weight + audio_weight
    video_weight /= total_weight
    audio_weight /= total_weight
    
    # 加权融合
    final_valence = (video_result.valence * video_weight + 
                     audio_result.valence * audio_weight)
    final_arousal = (video_result.arousal * video_weight + 
                     audio_result.arousal * audio_weight)
    
    # 情绪类型：选择高分者
    if video_result.confidence > audio_result.confidence * 1.2:
        final_emotion = video_result.emotion_type
    elif audio_result.confidence > video_result.confidence * 1.2:
        final_emotion = audio_result.emotion_type
    else:
        # 置信度接近，使用规则引擎
        final_emotion = rule_based_fusion(video_result, audio_result)
    
    return {
        'emotion_type': final_emotion,
        'valence': final_valence,
        'arousal': final_arousal,
        'confidence': (video_result.confidence + audio_result.confidence) / 2
    }
```

---

### 4.3 权重分配策略

#### 场景自适应权重

| 场景 | 视频权重 | 音频权重 | 理由 |
|------|---------|---------|------|
| 光线充足 | 0.6 | 0.4 | 视频质量高 |
| 光线昏暗 | 0.3 | 0.7 | 视频质量低 |
| 环境嘈杂 | 0.7 | 0.3 | 音频质量低 |
| 用户说话 | 0.4 | 0.6 | 音频信息丰富 |
| 用户沉默 | 0.8 | 0.2 | 依赖面部表情 |

---

### 4.4 冲突处理机制

#### 规则引擎

```python
def rule_based_fusion(video, audio):
    # 规则 1: 焦虑检测（音频优先）
    if audio.emotion_type == 'anxious' and audio.confidence > 0.7:
        return 'anxious'
    
    # 规则 2: 抑郁检测（视频优先）
    if video.emotion_type == 'depressed' and video.confidence > 0.7:
        return 'depressed'
    
    # 规则 3: 危机信号（任一高置信度）
    crisis_emotions = ['fearful', 'depressed']
    if (video.emotion_type in crisis_emotions and video.confidence > 0.8) or \
       (audio.emotion_type in crisis_emotions and audio.confidence > 0.8):
        return max([video, audio], key=lambda x: x.confidence).emotion_type
    
    # 默认：选择置信度高者
    return max([video, audio], key=lambda x: x.confidence).emotion_type
```

---

### 4.5 融合效果预估

| 融合策略 | 准确率 | 召回率 | F1 |
|----------|--------|--------|-----|
| 仅视频 | 78% | 75% | 76% |
| 仅音频 | 75% | 72% | 73% |
| 简单平均 | 80% | 77% | 78% |
| **加权融合 (推荐)** | **82%** | **79%** | **80%** |
| 规则增强融合 | 83% | 81% | 82% |

---

## 5. 部署方案

### 5.1 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                    客户端 (Android)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │
│  │ 摄像头采集 │  │ 麦克风采集 │  │  本地预处理 (降噪/裁剪) │  │
│  └────┬─────┘  └────┬─────┘  └──────────┬───────────┘  │
│       │             │                    │              │
│       └─────────────┴────────────────────┘              │
│                           │                              │
│                           ▼                              │
│                  ┌──────────────┐                        │
│                  │  WebSocket   │                        │
│                  └──────┬───────┘                        │
└─────────────────────────┼────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   边缘节点 (Edge)                        │
│  ┌──────────────────────────────────────────────────┐   │
│  │  视频推理服务 (Raven-1 INT8)                      │   │
│  │  - GPU: NVIDIA T4                                 │   │
│  │  - 延迟：<150ms                                   │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  音频推理服务 (OpenSMILE + XGBoost)               │   │
│  │  - CPU: 4 vCPU                                    │   │
│  │  - 延迟：<100ms                                   │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  融合服务                                         │   │
│  │  - 加权融合 + 规则引擎                            │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   云端备份 (Cloud)                       │
│  ┌──────────────────────────────────────────────────┐   │
│  │  GLM-4V (降级方案)                                 │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  模型训练与更新                                    │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

### 5.2 资源需求

#### 边缘节点 (单节点)

| 资源 | 配置 | 数量 | 说明 |
|------|------|------|------|
| GPU | NVIDIA T4 (16GB) | 2 | 视频推理 |
| CPU | 8 vCPU | 1 | 音频推理 + 融合 |
| 内存 | 32GB | 1 | - |
| 存储 | 100GB SSD | 1 | 模型 + 缓存 |
| 带宽 | 100Mbps | 1 | 视频流上传 |

**支持并发**: 50-100 用户/节点  
**延迟预算**: <200ms (P95)

#### 云端备份

| 资源 | 配置 | 数量 | 说明 |
|------|------|------|------|
| GPU | NVIDIA A10 | 4 | GLM-4V 推理 |
| CPU | 16 vCPU | 2 | API 网关 |
| 内存 | 64GB | 2 | - |

---

### 5.3 边缘计算 vs 云端推理

| 维度 | 边缘计算 | 云端推理 |
|------|---------|---------|
| 延迟 | <200ms | 300-500ms |
| 带宽成本 | 低 (仅上传特征) | 高 (上传视频流) |
| 数据隐私 | 高 (本地处理) | 中 (需传输) |
| 可扩展性 | 中 (需部署节点) | 高 (弹性扩容) |
| 维护成本 | 高 (分布式) | 低 (集中式) |

**决策**: 边缘计算为主，云端备份为辅

---

## 6. 技术风险与应对

### 6.1 风险矩阵

| 风险 | 概率 | 影响 | 应对策略 |
|------|------|------|----------|
| 准确率不达标 | 中 | 高 | 多模型备选 + 持续微调 |
| 延迟过高 | 中 | 高 | 边缘部署 + 模型量化 |
| 光线/噪声干扰 | 高 | 中 | 质量评估 + 降级策略 |
| 隐私合规问题 | 中 | 高 | 本地处理 + 数据脱敏 |
| 模型偏见 | 低 | 中 | 多样化测试集 + 公平性审计 |

---

### 6.2 降级方案

#### Level 1: 单模态降级

```python
if video_quality < threshold:
    # 仅使用音频
    emotion = audio_model.predict(audio_features)
elif audio_quality < threshold:
    # 仅使用视频
    emotion = video_model.predict(video_frame)
else:
    # 多模态融合
    emotion = fuse(video_result, audio_result)
```

#### Level 2: 文本情绪分析 (最后降级)

```python
if both_modalities_fail:
    # 使用文本情绪分析
    emotion = text_sentiment_analysis(message_content)
```

#### Level 3: 规则引擎

```python
if all_ai_models_fail:
    # 使用关键词匹配
    emotion = keyword_based_detection(message_content)
```

---

### 6.3 性能优化预案

1. **模型蒸馏**: 训练小模型（~50MB）替代大模型
2. **动态批处理**: 根据负载自动调整 batch size
3. **模型预热**: 启动时预加载模型到 GPU
4. **异步推理**: 非阻塞式推理，避免阻塞对话流
5. **缓存策略**: 相同用户短期缓存情绪状态

---

## 7. 实施计划

### 7.1 阶段划分

| 阶段 | 时间 | 任务 | 交付物 |
|------|------|------|--------|
| Phase 1 | 第 3-4 周 | 视频模型集成 | 视频情绪 API |
| Phase 2 | 第 5 周 | 音频模型集成 | 音频情绪 API |
| Phase 3 | 第 6 周 | 多模态融合 | 融合服务 |
| Phase 4 | 第 7 周 | 性能优化 | 延迟<200ms |
| Phase 5 | 第 8 周 | 测试与验收 | 测试报告 |

---

### 7.2 里程碑

| 里程碑 | 时间 | 验收标准 |
|--------|------|----------|
| M2: 情绪识别完成 | 第 5 周末 | 视频 + 音频 API 可用，准确率≥75% |
| M3: 融合完成 | 第 6 周末 | 多模态融合上线，延迟<200ms |

---

## 8. 参考资源

### 8.1 开源项目

- **DeepFace**: https://github.com/serengil/deepface
- **OpenFace**: https://github.com/TadasBaltrusaitis/OpenFace
- **OpenSMILE**: https://github.com/naxingyu/opensmile
- **FER**: https://github.com/OzyMisty/FER

### 8.2 数据集

- **FER2013**: https://www.kaggle.com/c/challenges-in-representation-learning-facial-expression-recognition-challenge
- **AffectNet**: http://mohammadmahoor.com/affectnet/
- **IEMOCAP**: https://sail.usc.edu/iemocap/
- **RAF-DB**: http://www.whdeng.cn/RAF/model1.html

### 8.3 商业 API

- **Tavus Raven-1**: https://www.tavus.io/
- **Azure Emotion API**: https://azure.microsoft.com/en-us/services/cognitive-services/face/
- **智谱 GLM-4V**: https://open.bigmodel.cn/

---

*文档版本：1.0*  
*创建时间：2026-03-24*  
*负责人：ai-engineer*  
*状态：✅ 已完成*
