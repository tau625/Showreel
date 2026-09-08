# 环境与踩坑（Windows / 国内网络已验证）

`<python-cmd>` = 当前环境可用的 Python（Windows 上通常 `py -3` 或 `python`；若用隔离 venv 就写 venv 里的绝对路径）。

## 1. 依赖

| 工具 | 要求 | 用途 |
|---|---|---|
| Node | ≥ 20（跑 Remotion） | 渲染引擎 |
| Python | ≥ 3.10 | edge-tts / MiMo TTS / ffmpeg 封装 |
| ffmpeg | `imageio-ffmpeg` 自带（pip 装） | 倍速、压缩、抽封面 |
| 浏览器 | 本机已装的 Edge 或 Chrome | Remotion 渲染内核（国内拉不动 Chrome Headless Shell） |
| gh CLI | ≥ 2.50，已 `gh auth login` | Release / issue 附件 |

```bash
<python-cmd> -m pip install edge-tts mutagen numpy pillow imageio-ffmpeg fonttools
npm install
```

Remotion 版本 4.0.522（`@remotion/cli` / `remotion` / `@remotion/media` / `@remotion/transitions`）。

## 2. `remotion.config.ts` 必配

不配这两项会卡在下载 Chrome Headless Shell（国内拉不动，静默卡 10+ 分钟无输出）：

```ts
import { Config } from '@remotion/cli/config';
Config.setEntryPoint('src/index.ts');
Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
Config.setBrowserExecutable('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe');
Config.setChromiumOpenGlRenderer('angle');   // 部分显卡下不设会黑屏
Config.setConcurrency(4);
```

找本机 Edge / Chrome 路径：Windows 常见 `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`；没有就 `ls "/c/Program Files/Google/Chrome/Application/chrome.exe"`。

## 3. 踩坑表

| # | 坑 | 现象 | 解法 |
|---|---|---|---|
| 1 | `raw.githubusercontent.com` 被墙 | SSL 握手失败 | 换 `https://cdn.jsdelivr.net/gh/{user}/{repo}@{branch}/{file}` |
| 2 | Remotion 自动下载 Chrome Headless Shell | 卡十几分钟无输出 | `Config.setBrowserExecutable` 指向本机 Edge |
| 3 | 渲染命令接 `\| tail` | 输出全缓冲，看不到进度 | 改 `> out/render.log 2>&1`，用 `progress.py` |
| 4 | Remotion 自带 ffmpeg 缺 `setpts` | 变速报 filter not found | 用 `imageio-ffmpeg` 的完整 ffmpeg（ffutil.py 已封装） |
| 5 | Git Bash 把 `PTS/1.5` 当路径转换 | 参数被改写成 Windows 路径 | 用 Python `subprocess` 传参，绕开 shell |
| 6 | `edge-tts --rate -10%` | 负号被解析成新参数 | 写成 `--rate=-10%` |
| 7 | 大体积可变字体（思源宋体 20MB） | 渲染耗时翻倍 | 可接受就留；赶时间只给标题用，正文换黑体 |
| 8 | 非交互 shell 里 `gh` 报未登录 | `please run gh auth login` | `export GH_TOKEN=$(gh auth token)` |
| 9 | curl 调 GitHub 报证书吊销 | `CRYPT_E_NO_REVOCATION_CHECK` | 加 `--ssl-no-revoke` |
| 10 | GitHub 附件上传 API 一律失败 | 任何大小都 `Bad Size` | 别用 curl 打 `uploads.github.com`，改用 `gh --attach` |
| 11 | issue 附件传视频失败 | `Failed to upload` | 免费账号 **10 MB** 上限，压到 7 MB 再传 |
| 12 | 截图泄露本机路径 | 视频里出现 `C:\Users\...` | 重截打码版，发布前逐张检查 |
| 13 | `/tmp` 不可写 | Remotion 报 cannot write | 设 `TMP`/`TEMP` 到项目内 `.tmp`，或直接依赖系统 TEMP |

## 4. 目录约定

```
<项目>/
├── _src/
│   ├── script.json        # 分镜与文案（唯一真相源）
│   └── _tmp/              # SRT 缓存 + 复用 manifest
├── public/
│   ├── voice/             # gen_voice.py 产出的 sN.mp3
│   ├── shots/             # 真实截图
│   └── bgm-*.m4a          # BGM
├── src/                   # Remotion 工程
└── out/                   # 渲染产物 + render.log（不进 git）
```
