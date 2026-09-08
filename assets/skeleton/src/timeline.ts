/**
 * 时间轴 —— 由 gen_voice.py 生成的 timeline.json 驱动，不要手改。
 * 改文案重跑 gen_voice.py，这里自动跟着变。
 */
import raw from './data/timeline.json';

export type Caption = {
  text: string;
  startFrame: number;
  endFrame: number;
};

export type Segment = {
  id: string;
  scene: string; // 对应 src/scenes/index.ts registry 的 key
  title: string;
  text: string;
  audio: string;
  audioDuration: number;
  padBefore: number;
  extra: number;
  padAfter: number;
  keyPoints: string[];
  captions: Caption[];
  /** 配音讲完的帧位置（段内相对帧），之后是纯画面演示 */
  audioEndFrame: number;
  frames: number;
  /** 段在全片中的起始帧（下面累加得出） */
  startFrame: number;
};

export const FPS = raw.fps;

export const segments: Segment[] = (() => {
  let cursor = 0;
  return (raw.segments as Omit<Segment, 'startFrame'>[]).map((s) => {
    const seg: Segment = { ...s, startFrame: cursor };
    cursor += s.frames;
    return seg;
  });
})();

export const TOTAL_FRAMES = segments.reduce((sum, s) => sum + s.frames, 0);

export const getSegment = (id: string): Segment => {
  const seg = segments.find((s) => s.id === id);
  if (!seg) throw new Error(`找不到场景段: ${id}`);
  return seg;
};
