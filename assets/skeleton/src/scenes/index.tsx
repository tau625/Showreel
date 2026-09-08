/**
 * 场景注册表 —— 新增场景在这里登记，key 对应 script.json 里的 seg.scene。
 * 漏登记不会崩，会渲染 FallbackScene（显示段标题），方便边做边补。
 */
import React from 'react';
import { AbsoluteFill } from 'remotion';
import type { Segment } from '../timeline';
import { ExampleScene } from './ExampleScene';
import { C, FONT } from '../theme';

export type SceneProps = { seg: Segment };

export const scenes: Record<string, React.FC<SceneProps>> = {
  example: ExampleScene,
  // intro: IntroScene,
  // pain: PainScene,
};

export const FallbackScene: React.FC<SceneProps> = ({ seg }) => (
  <AbsoluteFill
    style={{
      background: C.paper,
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: FONT.serif,
    }}
  >
    <div style={{ fontSize: 72, color: C.ink, letterSpacing: 4 }}>{seg.title}</div>
    <div style={{ fontSize: 28, color: C.muted, marginTop: 20 }}>
      未注册场景：{seg.scene}
    </div>
  </AbsoluteFill>
);

export const resolveScene = (name: string): React.FC<SceneProps> => scenes[name] ?? FallbackScene;
