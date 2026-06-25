/**
 * Avatar3D — 程序化生成的 3D 卡通形象
 *
 * 使用 @react-three/fiber 的 Canvas 渲染纯几何体角色 (无外部 GLB 模型)
 * 根据情绪状态实时切换表情, 支持呼吸 / 眨眼 / 说话动画
 */
import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { useAvatar } from './useAvatar';
import {
  lerp,
  getBreathingOffset,
  getSpeakingOffset,
  getBlinkScale,
  type ExpressionParams,
} from './animations';
import { EXPRESSION_LABELS, EMOTION_LABELS } from '../../utils/constants';
import type { Expression } from '../../types';

/* ================================================================== */
/*  Character — Canvas 内部的 3D 角色组件                              */
/* ================================================================== */

interface CharacterProps {
  emotion: string;
  isSpeaking: boolean;
}

const Character = React.memo(function Character({ emotion, isSpeaking }: CharacterProps) {
  // ---- Mesh refs ----
  const bodyGroupRef = useRef<THREE.Group>(null);
  const headGroupRef = useRef<THREE.Group>(null);
  const leftEyeRef = useRef<THREE.Group>(null);
  const rightEyeRef = useRef<THREE.Group>(null);
  const mouthRef = useRef<THREE.Mesh>(null);
  const oMouthRef = useRef<THREE.Mesh>(null);
  const leftBrowRef = useRef<THREE.Mesh>(null);
  const rightBrowRef = useRef<THREE.Mesh>(null);
  const leftCheekRef = useRef<THREE.Mesh>(null);
  const rightCheekRef = useRef<THREE.Mesh>(null);

  // ---- Animation state ----
  const { stateRef } = useAvatar(emotion);

  /* ---------------------------------------------------------------- */
  /*  useFrame — 每帧更新动画                                          */
  /* ---------------------------------------------------------------- */
  useFrame((state, delta) => {
    const time = state.clock.elapsedTime;
    const s = stateRef.current;
    const cur = s.currentParams;
    const tgt = s.targetParams;

    // -- 1. 表情参数平滑过渡 (lerp) --
    const f = Math.min(delta * 5, 1); // 过渡速度
    cur.mouthCurve = lerp(cur.mouthCurve, tgt.mouthCurve, f);
    cur.mouthOpenness = lerp(cur.mouthOpenness, tgt.mouthOpenness, f);
    cur.mouthWidth = lerp(cur.mouthWidth, tgt.mouthWidth, f);
    cur.browAngle = lerp(cur.browAngle, tgt.browAngle, f);
    cur.browHeight = lerp(cur.browHeight, tgt.browHeight, f);
    cur.eyeOpenness = lerp(cur.eyeOpenness, tgt.eyeOpenness, f);

    // -- 2. 呼吸动画 --
    if (bodyGroupRef.current) {
      bodyGroupRef.current.position.y = -0.1 + getBreathingOffset(time);
    }

    // -- 3. 头部轻微摆动 --
    if (headGroupRef.current) {
      headGroupRef.current.rotation.z = Math.sin(time * 0.5) * 0.03;
      headGroupRef.current.rotation.y = Math.sin(time * 0.3) * 0.05;
    }

    // -- 4. 眨眼调度 --
    if (time >= s.nextBlinkTime && s.blinkStartTime < 0) {
      s.blinkStartTime = time;
    }
    if (s.blinkStartTime >= 0 && time - s.blinkStartTime >= 0.15) {
      s.blinkStartTime = -1;
      s.nextBlinkTime = time + 3 + Math.random() * 2;
    }
    const blinkScale = getBlinkScale(time, s.blinkStartTime);
    const eyeScaleY = blinkScale * cur.eyeOpenness;
    if (leftEyeRef.current) leftEyeRef.current.scale.y = eyeScaleY;
    if (rightEyeRef.current) rightEyeRef.current.scale.y = eyeScaleY;

    // -- 5. 说话动画 --
    const speakingPulse = getSpeakingOffset(time, isSpeaking ? 1 : 0);

    // -- 6. 嘴巴形状 --
    // O 嘴透明度: mouthOpenness > 0.25 时渐显
    const oFactor = Math.max(0, Math.min(1, (cur.mouthOpenness - 0.25) / 0.25));
    const regularOpacity = 1 - oFactor;

    if (mouthRef.current) {
      const mat = mouthRef.current.material as THREE.MeshStandardMaterial;
      mat.opacity = regularOpacity;

      // 微笑弧线嘴: 正 scale = 微笑, 负 scale = 难过
      const direction = cur.mouthCurve >= 0 ? 1 : -1;
      const curveAmount = Math.abs(cur.mouthCurve);
      const baseScaleY = Math.max(0.12, curveAmount * 0.7 + 0.3);
      // 说话时嘴巴开合脉动 (仅在非 O 嘴状态下生效)
      mouthRef.current.scale.y = (baseScaleY + speakingPulse * (1 - oFactor)) * direction;
      mouthRef.current.scale.x = cur.mouthWidth;
    }

    if (oMouthRef.current) {
      const mat = oMouthRef.current.material as THREE.MeshStandardMaterial;
      mat.opacity = oFactor;
      // O 嘴说话时缩放脉动
      const oScale = 1 + speakingPulse * oFactor * 2;
      oMouthRef.current.scale.setScalar(oScale);
    }

    // -- 7. 眉毛 --
    if (leftBrowRef.current && rightBrowRef.current) {
      const rot = cur.browAngle * 0.3;
      leftBrowRef.current.rotation.z = rot;    // 正 = 内侧上扬
      rightBrowRef.current.rotation.z = -rot;   // 负 = 内侧上扬
      leftBrowRef.current.position.y = 0.22 + cur.browHeight;
      rightBrowRef.current.position.y = 0.22 + cur.browHeight;
    }

    // -- 8. 腮红 (开心时显示) --
    const blushOpacity = Math.max(0, cur.mouthCurve) * 0.45;
    if (leftCheekRef.current) {
      (leftCheekRef.current.material as THREE.MeshStandardMaterial).opacity = blushOpacity;
    }
    if (rightCheekRef.current) {
      (rightCheekRef.current.material as THREE.MeshStandardMaterial).opacity = blushOpacity;
    }
  });

  /* ---------------------------------------------------------------- */
  /*  Geometry & Material 常量                                         */
  /* ---------------------------------------------------------------- */
  const skinColor = '#FFE0C0';
  const hairColor = '#7C5CFC';
  const bodyColor = '#A78BFA';
  const eyeWhite = '#FFFFFF';
  const pupilColor = '#4A3B6B';
  const browColor = '#6B5B8D';
  const mouthColor = '#E87B9F';
  const cheekColor = '#FFB6C8';
  const noseColor = '#F5D0B0';

  return (
    <group ref={bodyGroupRef} position={[0, -0.1, 0]}>
      {/* ============ 身体 ============ */}
      <mesh position={[0, -0.45, 0]}>
        <capsuleGeometry args={[0.38, 0.4, 8, 16]} />
        <meshStandardMaterial color={bodyColor} roughness={0.65} />
      </mesh>

      {/* ============ 头部 ============ */}
      <group ref={headGroupRef} position={[0, 0.4, 0]}>
        {/* 脸 */}
        <mesh>
          <sphereGeometry args={[0.5, 32, 32]} />
          <meshStandardMaterial color={skinColor} roughness={0.5} />
        </mesh>

        {/* 头发 (顶部半圆球) */}
        <mesh position={[0, 0.12, -0.02]} rotation={[0.12, 0, 0]}>
          <sphereGeometry args={[0.52, 32, 32, 0, Math.PI * 2, 0, Math.PI * 0.55]} />
          <meshStandardMaterial color={hairColor} roughness={0.7} />
        </mesh>

        {/* 刘海 */}
        <mesh position={[0, 0.18, 0.35]} rotation={[-0.3, 0, 0]}>
          <sphereGeometry args={[0.3, 16, 16, 0, Math.PI * 2, 0, Math.PI * 0.4]} />
          <meshStandardMaterial color="#9B7DFC" roughness={0.7} />
        </mesh>

        {/* 左耳 */}
        <mesh position={[-0.5, 0, 0]}>
          <sphereGeometry args={[0.08, 16, 16]} />
          <meshStandardMaterial color={skinColor} roughness={0.5} />
        </mesh>

        {/* 右耳 */}
        <mesh position={[0.5, 0, 0]}>
          <sphereGeometry args={[0.08, 16, 16]} />
          <meshStandardMaterial color={skinColor} roughness={0.5} />
        </mesh>

        {/* ---------- 左眼 ---------- */}
        <group ref={leftEyeRef} position={[-0.18, 0.05, 0.43]}>
          {/* 眼白 */}
          <mesh>
            <sphereGeometry args={[0.1, 16, 16]} />
            <meshStandardMaterial color={eyeWhite} roughness={0.3} />
          </mesh>
          {/* 瞳孔 */}
          <mesh position={[0, 0, 0.06]}>
            <sphereGeometry args={[0.055, 16, 16]} />
            <meshStandardMaterial color={pupilColor} roughness={0.2} />
          </mesh>
          {/* 高光 */}
          <mesh position={[0.025, 0.03, 0.095]}>
            <sphereGeometry args={[0.022, 8, 8]} />
            <meshStandardMaterial
              color={eyeWhite}
              emissive={eyeWhite}
              emissiveIntensity={0.6}
            />
          </mesh>
        </group>

        {/* ---------- 右眼 ---------- */}
        <group ref={rightEyeRef} position={[0.18, 0.05, 0.43]}>
          <mesh>
            <sphereGeometry args={[0.1, 16, 16]} />
            <meshStandardMaterial color={eyeWhite} roughness={0.3} />
          </mesh>
          <mesh position={[0, 0, 0.06]}>
            <sphereGeometry args={[0.055, 16, 16]} />
            <meshStandardMaterial color={pupilColor} roughness={0.2} />
          </mesh>
          <mesh position={[0.025, 0.03, 0.095]}>
            <sphereGeometry args={[0.022, 8, 8]} />
            <meshStandardMaterial
              color={eyeWhite}
              emissive={eyeWhite}
              emissiveIntensity={0.6}
            />
          </mesh>
        </group>

        {/* ---------- 眉毛 ---------- */}
        <mesh ref={leftBrowRef} position={[-0.18, 0.22, 0.42]}>
          <boxGeometry args={[0.1, 0.022, 0.03]} />
          <meshStandardMaterial color={browColor} roughness={0.6} />
        </mesh>
        <mesh ref={rightBrowRef} position={[0.18, 0.22, 0.42]}>
          <boxGeometry args={[0.1, 0.022, 0.03]} />
          <meshStandardMaterial color={browColor} roughness={0.6} />
        </mesh>

        {/* ---------- 鼻子 ---------- */}
        <mesh position={[0, -0.06, 0.47]}>
          <sphereGeometry args={[0.035, 12, 12]} />
          <meshStandardMaterial color={noseColor} roughness={0.5} />
        </mesh>

        {/* ---------- 嘴巴 (微笑/难过弧线) ---------- */}
        <mesh ref={mouthRef} position={[0, -0.2, 0.44]}>
          {/* 半圆环, arc=π, 默认旋转 π 使弧线朝下(微笑) */}
          <torusGeometry args={[0.09, 0.022, 8, 16, Math.PI]} />
          <meshStandardMaterial color={mouthColor} roughness={0.5} transparent opacity={1} />
        </mesh>

        {/* ---------- O 型嘴 (焦虑/说话) ---------- */}
        <mesh ref={oMouthRef} position={[0, -0.2, 0.45]}>
          <torusGeometry args={[0.05, 0.02, 8, 16]} />
          <meshStandardMaterial color={mouthColor} roughness={0.5} transparent opacity={0} />
        </mesh>

        {/* ---------- 腮红 ---------- */}
        <mesh ref={leftCheekRef} position={[-0.3, -0.08, 0.38]}>
          <sphereGeometry args={[0.06, 16, 16]} />
          <meshStandardMaterial color={cheekColor} roughness={0.8} transparent opacity={0} />
        </mesh>
        <mesh ref={rightCheekRef} position={[0.3, -0.08, 0.38]}>
          <sphereGeometry args={[0.06, 16, 16]} />
          <meshStandardMaterial color={cheekColor} roughness={0.8} transparent opacity={0} />
        </mesh>
      </group>
    </group>
  );
});

/* ================================================================== */
/*  Avatar3D — 主组件 (Canvas + 容器)                                  */
/* ================================================================== */

export interface Avatar3DProps {
  /** 情绪状态字符串 (支持 happy/sad/angry/neutral/anxious 及 Expression 类型) */
  emotion: string;
  /** 是否正在说话 (嘴巴开合动画) */
  isSpeaking?: boolean;
  /** Canvas 容器尺寸 (px) */
  size?: number;
  /** 额外 className */
  className?: string;
}

export default function Avatar3D({
  emotion,
  isSpeaking = false,
  size = 200,
  className = '',
}: Avatar3DProps) {
  // 计算标签文字
  const label = useMemo(() => {
    const exprMap = EXPRESSION_LABELS as Record<string, string>;
    return exprMap[emotion] || EMOTION_LABELS[emotion] || emotion;
  }, [emotion]);

  return (
    <div className={`flex flex-col items-center gap-2 ${className}`}>
      {/* 3D 画布容器 */}
      <div
        style={{
          width: size,
          height: size,
          borderRadius: '50%',
          overflow: 'hidden',
          background:
            'linear-gradient(135deg, #E8DDFF 0%, #FFF8F0 50%, #E8F4FD 100%)',
          boxShadow:
            '0 8px 32px rgba(124, 92, 252, 0.15), 0 2px 8px rgba(0,0,0,0.06)',
        }}
      >
        <Canvas
          camera={{ position: [0, 0.05, 2.8], fov: 38 }}
          dpr={[1, 2]}
          flat
          gl={{ antialias: true, alpha: true }}
        >
          {/* 环境光 — 柔和的基底照明 */}
          <ambientLight intensity={0.7} />
          {/* 主光源 — 右上方暖光 */}
          <directionalLight position={[3, 4, 5]} intensity={0.6} />
          {/* 补光 — 左侧紫色氛围光 */}
          <directionalLight position={[-3, 1, 2]} intensity={0.3} color="#B4A7FF" />

          <Character emotion={emotion} isSpeaking={isSpeaking} />
        </Canvas>
      </div>

      {/* 表情标签 */}
      <span
        className="text-sm font-medium px-3 py-1 rounded-full"
        style={{
          background: 'rgba(124, 92, 252, 0.1)',
          color: '#7C5CFC',
          transition: 'all 0.3s ease',
        }}
      >
        {label}
      </span>
    </div>
  );
}
