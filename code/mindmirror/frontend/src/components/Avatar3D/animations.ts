/**
 * Avatar3D 动画参数与工具函数
 */

/** 表情参数接口 — 描述 3D 角色面部各部位的动画状态 */
export interface ExpressionParams {
  /** 嘴角弧度: -1(下弯/难过) ~ 1(上扬/微笑) */
  mouthCurve: number;
  /** 嘴巴开合度: 0(闭合) ~ 1(大张) */
  mouthOpenness: number;
  /** 嘴巴宽度系数: 0.7(小) ~ 1.3(宽) */
  mouthWidth: number;
  /** 眉毛角度: -1(内蹙/愤怒) ~ 1(上扬/惊讶) */
  browAngle: number;
  /** 眉毛高度偏移 */
  browHeight: number;
  /** 眼睛开合度: 0(闭眼) ~ 1(全开) */
  eyeOpenness: number;
}

/* ------------------------------------------------------------------ */
/*  Emotion → ExpressionParams 映射表                                  */
/*  同时支持任务要求的 emotion 字符串 (happy/sad/angry/neutral/anxious) */
/*  和现有 Expression 类型 (empathy/thinking/concerned/encouraging)    */
/* ------------------------------------------------------------------ */
export const EMOTION_PARAMS: Record<string, ExpressionParams> = {
  // ---- 基础情绪 ----
  happy: {
    mouthCurve: 1.0,
    mouthOpenness: 0.15,
    mouthWidth: 1.2,
    browAngle: 0.4,
    browHeight: 0.02,
    eyeOpenness: 0.75,
  },
  sad: {
    mouthCurve: -0.8,
    mouthOpenness: 0.05,
    mouthWidth: 0.85,
    browAngle: -0.3,
    browHeight: -0.03,
    eyeOpenness: 0.5,
  },
  angry: {
    mouthCurve: -0.3,
    mouthOpenness: 0.1,
    mouthWidth: 0.9,
    browAngle: -1.0,
    browHeight: -0.04,
    eyeOpenness: 0.65,
  },
  neutral: {
    mouthCurve: 0.15,
    mouthOpenness: 0.0,
    mouthWidth: 1.0,
    browAngle: 0.0,
    browHeight: 0.0,
    eyeOpenness: 0.85,
  },
  anxious: {
    mouthCurve: 0.0,
    mouthOpenness: 0.5,
    mouthWidth: 0.7,
    browAngle: 0.8,
    browHeight: 0.04,
    eyeOpenness: 0.9,
  },

  // ---- Expression 类型映射 ----
  empathy: {
    mouthCurve: 0.6,
    mouthOpenness: 0.1,
    mouthWidth: 1.05,
    browAngle: 0.2,
    browHeight: 0.0,
    eyeOpenness: 0.7,
  },
  thinking: {
    mouthCurve: 0.05,
    mouthOpenness: 0.25,
    mouthWidth: 0.85,
    browAngle: 0.3,
    browHeight: 0.01,
    eyeOpenness: 0.6,
  },
  concerned: {
    mouthCurve: -0.4,
    mouthOpenness: 0.1,
    mouthWidth: 0.9,
    browAngle: -0.2,
    browHeight: -0.02,
    eyeOpenness: 0.6,
  },
  encouraging: {
    mouthCurve: 1.0,
    mouthOpenness: 0.35,
    mouthWidth: 1.3,
    browAngle: 0.5,
    browHeight: 0.03,
    eyeOpenness: 0.8,
  },
};

/* ------------------------------------------------------------------ */
/*  动画工具函数                                                        */
/* ------------------------------------------------------------------ */

/** 线性插值 — 用于表情参数平滑过渡 */
export function lerp(current: number, target: number, factor: number): number {
  return current + (target - current) * factor;
}

/**
 * 呼吸动画偏移
 * sin 波浮动, 幅度 0.02, 周期 3 秒
 */
export function getBreathingOffset(time: number): number {
  return Math.sin((time / 3) * Math.PI * 2) * 0.02;
}

/**
 * 说话动画 — 嘴巴开合振荡
 * 频率约 1.6Hz, 模拟自然说话节奏
 * @param time  经过时间(秒)
 * @param intensity 强度 0~1
 * @returns 0~0.3 的开合量
 */
export function getSpeakingOffset(time: number, intensity = 1): number {
  return Math.abs(Math.sin(time * 10)) * intensity * 0.25;
}

/**
 * 眨眼缩放计算
 * @param time 当前时间
 * @param blinkStartTime 眨眼开始时间, <0 表示未眨眼
 * @param duration 眨眼持续时间(秒), 默认 0.15s
 * @returns 眼睛 Y 缩放: 1=全开, 0.15=几乎闭合
 */
export function getBlinkScale(
  time: number,
  blinkStartTime: number,
  duration = 0.15,
): number {
  if (blinkStartTime < 0) return 1;
  const progress = (time - blinkStartTime) / duration;
  if (progress < 0 || progress > 1) return 1;
  // 前半段闭合, 后半段睁开
  return progress < 0.5
    ? 1 - progress * 2 * 0.85
    : 0.15 + (progress - 0.5) * 2 * 0.85;
}
