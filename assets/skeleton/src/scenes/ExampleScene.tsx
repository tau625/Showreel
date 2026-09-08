/**
 * 场景模板 —— 复制它改成自己的场景。
 * 演示了四件必备的事：纸底、标题入场、keyPoints 逐条浮现、字幕压在配音区间。
 */
import React from 'react';
import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';
import type { Segment } from '../timeline';
import { Paper } from '../components/Paper';
import { Captions } from '../components/Captions';
import { C, ease, FONT } from '../theme';

const TITLE_IN = 16;      // 标题入场帧数
const ITEM_STAGGER = 8;   // 每条要点之间的错开帧数

export const ExampleScene: React.FC<{ seg: Segment }> = ({ seg }) => {
  const frame = useCurrentFrame();
  const items = seg.keyPoints ?? [];

  const titleIn = ease.out(interpolate(frame, [0, TITLE_IN], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  }));

  return (
    <Paper>
      <AbsoluteFill
        style={{
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 48,
        }}
      >
        {/* 标题 */}
        <div
          style={{
            fontFamily: FONT.serif,
            fontSize: 76,
            fontWeight: 600,
            color: C.ink,
            letterSpacing: 6,
            opacity: titleIn,
            transform: `translateY(${(1 - titleIn) * 24}px)`,
          }}
        >
          {seg.title}
        </div>

        {/* 要点清单：逐条浮现 */}
        {items.length > 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 22 }}>
            {items.map((k, i) => {
              const start = TITLE_IN + i * ITEM_STAGGER;
              const p = ease.out(interpolate(frame, [start, start + 14], [0, 1], {
                extrapolateLeft: 'clamp',
                extrapolateRight: 'clamp',
              }));
              return (
                <div
                  key={k}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 18,
                    opacity: p,
                    transform: `translateX(${(1 - p) * -18}px)`,
                  }}
                >
                  <div
                    style={{
                      width: 12,
                      height: 12,
                      borderRadius: 6,
                      background: C.seal,
                      flexShrink: 0,
                    }}
                  />
                  <span
                    style={{
                      fontFamily: FONT.serif,
                      fontSize: 42,
                      color: C.ink,
                      letterSpacing: 2,
                    }}
                  >
                    {k}
                  </span>
                </div>
              );
            })}
          </div>
        )}
      </AbsoluteFill>

      {/* 字幕只在配音区间出现，之后是纯画面演示 */}
      <Captions captions={seg.captions} untilFrame={seg.audioEndFrame} fontSize={34} />
    </Paper>
  );
};
