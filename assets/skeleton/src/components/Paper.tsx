/** 纸质感背景 —— 全片统一，四角压暗让中心聚光 */
import React from 'react';
import { AbsoluteFill } from 'remotion';
import { C } from '../theme';

export const Paper: React.FC<{ children?: React.ReactNode; vignette?: boolean }> = ({
  children,
  vignette = true,
}) => (
  <AbsoluteFill style={{ background: C.paper }}>
    {vignette ? (
      <AbsoluteFill
        style={{
          background:
            'radial-gradient(ellipse at 50% 45%, rgba(255,255,255,0.55) 0%, rgba(255,255,255,0) 45%, rgba(120,105,80,0.10) 100%)',
        }}
      />
    ) : null}
    <AbsoluteFill
      style={{
        backgroundImage:
          'repeating-linear-gradient(0deg, rgba(140,120,90,0.030) 0px, rgba(140,120,90,0.030) 1px, transparent 1px, transparent 4px)',
      }}
    />
    {children}
  </AbsoluteFill>
);
