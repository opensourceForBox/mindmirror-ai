/**
 * useAvatar — 管理 3D 角色的动画状态
 *
 * 职责:
 *  1. emotion → 表情参数映射 (通过 EMOTION_PARAMS)
 *  2. 眨眼调度 (每 3~5 秒随机眨眼, 由 useFrame 驱动, 不使用 setInterval)
 *  3. 表情平滑过渡 (current → target, 在 useFrame 中 lerp)
 */
import { useRef, useMemo } from 'react';
import { EMOTION_PARAMS, type ExpressionParams } from './animations';

/** 动画运行时状态 — 全部存在 ref 中, 避免 re-render */
export interface AvatarAnimState {
  /** 目标表情参数 (由当前 emotion 决定) */
  targetParams: ExpressionParams;
  /** 当前表情参数 (逐帧 lerp 向 target 靠拢) */
  currentParams: ExpressionParams;
  /** 下一次眨眼的时间 (秒) */
  nextBlinkTime: number;
  /** 当前眨眼开始时间, -1 表示未眨眼 */
  blinkStartTime: number;
}

/** 随机生成下次眨眼时间 (3~5 秒后) */
function randomBlinkDelay(): number {
  return 3 + Math.random() * 2;
}

export function useAvatar(emotion: string) {
  // emotion → target params (memoized)
  const targetParams = useMemo<ExpressionParams>(
    () => EMOTION_PARAMS[emotion] ?? EMOTION_PARAMS.neutral,
    [emotion],
  );

  // 运行时状态 — 初始化为与 target 一致, 避免首帧跳变
  const stateRef = useRef<AvatarAnimState>({
    targetParams,
    currentParams: { ...targetParams },
    nextBlinkTime: randomBlinkDelay(),
    blinkStartTime: -1,
  });

  // emotion 变化时同步 target (ref 可安全变更, 不触发 re-render)
  stateRef.current.targetParams = targetParams;

  return { stateRef };
}
