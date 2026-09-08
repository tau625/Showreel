/**
 * 逐句字幕 —— 数据源是 TTS 生成的词级时间轴，与配音天然同步。
 * 无底色方案：同色系多层柔光描边托底，字像"印"在画面上，比贴白条高级。
 */
import React from 'react';
import { interpolate, useCurrentFrame } from 'remotion';
import { C, FONT } from '../theme';
import type { Caption } from '../timeline';

export const Captions: React.FC<{
  captions: Caption[];
  /** 显示到段内第几帧为止；传 seg.audioEndFrame 可让字幕只在配音期间出现 */
  untilFrame?: number;
  fontSize?: number;
  bottom?: number;
  color?: string;
}> = ({ captions, untilFrame, fontSize = 34, bottom = 90, color = C.ink }) => {
  const frame = useCurrentFrame();
  const limit = untilFrame ?? Number.MAX_SAFE_INTEGER;

  const active = captions.find(
    (c) => frame >= c.startFrame && frame < c.endFrame && frame < limit,
  );
  if (!active) return null;

  const appear = interpolate(
    frame,
    [active.startFrame, active.startFrame + 8],
    [0, 1],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' },
  );

  return (
    <div
      style={{
        position: 'absolute',
        left: 0,
        right: 0,
        bottom,
        display: 'flex',
        justifyContent: 'center',
        padding: '0 220px',
        pointerEvents: 'none',
      }}
    >
      <span
        style={{
          fontFamily: FONT.serif,
          fontSize,
          fontWeight: 500,
          color,
          lineHeight: 1.6,
          letterSpacing: 2.5,
          textAlign: 'center',
          opacity: appear,
          transform: `translateY(${(1 - appear) * 10}px)`,
          textShadow: [
            '0 0 2px rgba(250,248,242,.95)',
            '0 0 6px rgba(250,248,242,.9)',
            '0 1px 14px rgba(250,248,242,.8)',
            '0 2px 28px rgba(250,248,242,.6)',
          ].join(','),
        }}
      >
        {active.text}
      </span>
    </div>
  );
};
