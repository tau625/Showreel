/**
 * 每个项目要改的参数都集中在这里。
 * BGM_FILE 为 null 时不渲染音轨（先把画面做出来，BGM 后加也行）。
 */
export const BGM_FILE: string | null = null; // 例：'bgm-classic.m4a'，文件放 public/
export const BGM_VOLUME = 0.12; // 别超过 0.15，否则盖住人声
export const BGM_FADE_SEC = 2; // 首尾各淡入淡出 2 秒
