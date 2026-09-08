/**
 * 设计系统 —— 换皮只改这个文件。
 * 建议从被演示产品的 CSS 变量里取色，保证视频与产品是同一套视觉语言。
 */
export const C = {
  seal: '#b23a2e',      // 主色（印章 / 强调）
  sealDark: '#992e23',  // 主色深
  sealSoft: '#d9a8a1',  // 主色浅
  paper: '#f5f2ea',     // 背景
  paperDeep: '#efe9db', // 背景暗部
  card: '#fffefb',      // 卡面
  ink: '#2c2820',       // 正文
  muted: '#8d8370',     // 次要文字
  indigo: '#2f5d8a',    // 链接 / 进行中
  green: '#1c7a44',     // 完成
  line: '#e7e1d3',      // 描边
  note: '#fdf6e4',      // 提示底色
  noteStrong: '#a86a00',
} as const;

export const FONT = {
  serif: '"Noto Serif SC","Source Han Serif SC","STSong","STZhongsong","SimSun",serif',
  kai: '"KaiTi","STKaiti","楷体",serif',
  sans: '"Microsoft YaHei","PingFang SC","Segoe UI",system-ui,sans-serif',
  mono: '"Cascadia Mono","Consolas","Menlo",monospace',
} as const;

export const W = 1920;
export const H = 1080;

/** 缓动：慢出，收得稳 */
export const ease = {
  out: (t: number) => 1 - Math.pow(1 - t, 3),
  inOut: (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),
} as const;
