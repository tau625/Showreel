/**
 * 主合成 —— 通用件，通常不需要改。
 * 每段 = 一段配音 + 一个场景，段首段尾各做一点透明度转场。
 */
import React from 'react';
import { Audio } from '@remotion/media';
import { AbsoluteFill, interpolate, Sequence, staticFile, useCurrentFrame } from 'remotion';
import { FPS, segments, TOTAL_FRAMES } from './timeline';
import type { Segment } from './timeline';
import { resolveScene } from './scenes';
import { BGM_FADE_SEC, BGM_FILE, BGM_VOLUME } from './config';
import { C } from './theme';

const FADE = 14;

const SegWrapper: React.FC<{ seg: Segment }> = ({ seg }) => {
  const frame = useCurrentFrame();
  const Scene = resolveScene(seg.scene);
  const opacity = interpolate(
    frame,
    [0, FADE, seg.frames - FADE, seg.frames],
    [0, 1, 1, 0],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' },
  );
  return (
    <AbsoluteFill style={{ opacity }}>
      <Scene seg={seg} />
    </AbsoluteFill>
  );
};

export const Promo: React.FC = () => {
  const fadeFrames = BGM_FADE_SEC * FPS;
  const bgmVolume = (f: number) =>
    BGM_VOLUME * Math.max(0, Math.min(f / fadeFrames, (TOTAL_FRAMES - f) / fadeFrames, 1));

  return (
    <AbsoluteFill style={{ backgroundColor: C.paper }}>
      {BGM_FILE ? <Audio src={staticFile(BGM_FILE)} volume={bgmVolume} /> : null}

      {segments.map((seg) => (
        <Sequence
          key={seg.id}
          from={seg.startFrame}
          durationInFrames={seg.frames}
          premountFor={FPS}
        >
          {/* 配音在段内延迟 padBefore 起播，前后留白给转场 */}
          <Sequence from={Math.round(seg.padBefore * FPS)}>
            <Audio src={staticFile(seg.audio)} />
          </Sequence>
          <SegWrapper seg={seg} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
