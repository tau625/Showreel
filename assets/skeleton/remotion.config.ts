import { Config } from '@remotion/cli/config';

Config.setEntryPoint('src/index.ts');
Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);

// 不走 Remotion 自带的 Chrome Headless Shell 下载（国内拉不动），直接用系统 Edge/Chrome。
// 找不到浏览器就先确认路径：
//   ls "/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
//   ls "/c/Program Files/Google/Chrome/Application/chrome.exe"
Config.setBrowserExecutable(
  'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
);

// 部分显卡下不设会黑屏
Config.setChromiumOpenGlRenderer('angle');
Config.setConcurrency(4);
