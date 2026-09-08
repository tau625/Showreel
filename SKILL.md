---
name: showreel
description: 展卷 Showreel —— 用 Remotion 从零生产视频并发布。主打给软件做宣传片与功能演示（showreel），也覆盖科普讲解、教程演示、数据报告。含 AI 配音与字幕、BGM、渲染迭代、倍速/封面交付、GitHub Release 附件与 README 内嵌播放器、小红书/B站/视频号文案。内置 promo（产品宣传）与 generic（科普/教程/报告）两种模式，开工时按题材切换。当用户说"给这个软件做个宣传视频/演示视频/功能展示片""做个科普视频/教程视频""把视频嵌进 README""发 Release 附件""写发布文案"时使用。
agent_created: true
---

# 展卷 Showreel

把 SKILL.md 所在目录视为 `<skill-base>`。所有 references / assets / scripts 都相对它解析，不依赖调用方当前工作目录。

**展卷**：宣传片就是把软件功能像卷轴一样徐徐展开，一段一段演示给人看。
**Showreel**：英文里"用来展示自己的短片"的现成说法，正是软件宣传片这个品类。

本 skill 生产**代码驱动的视频**：React 写画面，配音驱动时间轴，渲染成 mp4。适合界面演示、图表动画、文字动效这类可控画面；不适合真人实拍。

## 两种模式

| | `promo` 产品宣传 | `generic` 通用（科普/教程/报告/活动） |
|---|---|---|
| 用途 | 给自家产品/项目做宣传片、功能演示 | 讲原理、教操作、读数据、招新 |
| 叙事骨架 | 抛问 → 痛点 → **卖点前置** → 流程演示×N → 收尾（开源/许可/CTA） | 见 `<skill-base>/references/narrative.md`，按题材选 |
| 画面主力 | 真实截图 / 录屏 / 界面复刻 | 代码动画 / 数据图表 / 示意图 |
| 时长 | 60s–3min | 30s–8min |
| 发布重心 | GitHub Release + README 内嵌 + 小红书 + B站 | B站/视频号 + 时间戳章节（观众会跳看） |
| 文案模板 | `<skill-base>/references/copywriting.md` §1 | 同文件 §2 |

**切换规则**：用户说的是"宣传片/产品演示/功能展示/给 X 项目做视频" → `promo`；说的是"科普/讲解/教程/数据报告/招新" → `generic`；拿不准就用一句话问，不要猜——模式选错会推翻已录好的配音和整条时间轴。

模式只在两处影响执行：**Step 4 分镜骨架**和 **Step 8 文案**。其余步骤两模式完全一致，不要为模式另起一套流程。

## 规则

1. **先拍板再动手**。画幅、时长、画面素材来源、声音方案、发布平台这 5 项不问清楚就开工，中途改配音时长会让全片时间轴平移，已渲的段全部作废。Step 1 用一张表一次性问完。
2. **卖点/结论必须前置**，不埋在流程里。观众前 15 秒决定去留。
3. **时间轴由音频反推，不手写帧数**。段长 = `padBefore + 配音时长 + extra + padAfter`，由 `gen_voice.py` 算出写进 `timeline.json`，代码里不出现硬编码帧数。
4. **改时长只动 `extra`**（配音讲完后留给画面演示的秒数），不动配音文案，这样不会触发重录。
5. **样式迭代用 Studio / 局部渲染**，攒一批改动最后一次全渲。全片渲染几分钟到十几分钟，单次修改就全渲是最大的时间浪费。
6. **渲染命令不接管道**（`| tail` 会全缓冲看不到进度）。一律 `> out/render.log 2>&1`，另开终端跑 `progress.py`。
7. **视频不进 git**。`.gitignore` 加 `*.mp4`，否则几十 MB 永久留在 `.git` 历史里。
8. **发布前逐张检查截图**是否泄露本机用户名/路径/令牌。
9. 遇到报错先查 `<skill-base>/references/env-setup.md` §踩坑表，那里集中了本环境已验证的全部坑和解法，不要重新试错。

## 工作流程

### Step 1 · 判模式 + 拍板 5 项

1. 判定 `promo` 还是 `generic`（按上面的切换规则）。
2. 用一张表问用户（或替用户给默认值并明确说明）：画幅 16:9 / 9:16；目标时长；画面素材（代码复刻 / 真实截图 / 两者）；声音（AI 配音+字幕 / 纯 BGM+文字 / 无声后期配）；发布平台。
3. 把结论记在 `_src/script.json` 顶部的 `note` 字段，后续步骤以它为准。

### Step 2 · 环境与脚手架

```bash
cp -r <skill-base>/assets/skeleton <项目目录> && cd <项目目录>
```

再按 `<skill-base>/references/env-setup.md` 装 Python 依赖、`npm install`、确认浏览器路径。**环境有问题的全部解法都在那一份里**，不要自己摸索。

### Step 3 · 素材

真实截图 → `public/shots/`（宽 ≥1200px，带窗口边框）；界面源码走 jsDelivr 取 CSS 变量定配色；数据/图表用代码画，比截图清晰且可动画。BGM 优先用用户提供的可商用曲子，缺曲子时的零版权方案见 `references/script-and-voice.md` §3。

### Step 4 · 分镜脚本

写 `_src/script.json`（schema 见 `<skill-base>/references/script-and-voice.md` §1，骨架见 `<skill-base>/assets/script-template.json`）。

- `promo` 模式：抛问 → 痛点 → 卖点（单独成段，配 `keyPoints` 做视觉清单）→ 流程演示×N → 收尾。
- `generic` 模式：按题材查 `<skill-base>/references/narrative.md` 选骨架。

段落数参考：30s→2-3 段，60s→4-5 段，2-3min→7-9 段，5min+→10-16 段。

### Step 5 · 配音、字幕、BGM

```bash
<python-cmd> <skill-base>/scripts/gen_voice.py --root .
```

逐段 TTS → `public/voice/sN.mp3` + SRT → 重算 `src/data/timeline.json`（含每条字幕的进出帧）。文案未变时复用已有音频，秒出结果。音色选择、MiMo voice design 用法、BGM 接入见 `<skill-base>/references/script-and-voice.md`。

**新音色必须先出 3 个 15 秒样音给用户试听，选定后再全量生成。**

### Step 6 · 场景实现与视觉系统

改三处即可换皮：`src/theme.ts`（配色 + 字体）、`src/scenes/*`（各段画面）、`src/assets/shots.ts`（截图开关，`null` = 回退代码复刻）。场景要在 `src/scenes/index.tsx` 的 registry 里注册，漏注册会走 Fallback 而不崩。详见 `<skill-base>/references/remotion-scaffold.md`。

写完跑 `./node_modules/.bin/tsc --noEmit`。

### Step 7 · 渲染

```bash
./node_modules/.bin/remotion studio                                        # 调样式首选，零渲染
./node_modules/.bin/remotion render PromoMain out/preview.mp4 --scale=0.5  # 半分辨率粗看
./node_modules/.bin/remotion render PromoMain out/x.mp4 --frames=A-B       # 局部
./node_modules/.bin/remotion render PromoMain out/x.mp4 > out/render.log 2>&1   # 全片
<python-cmd> <skill-base>/scripts/progress.py --root .                     # 另开终端看进度
```

交付给用户前至少全渲一次，并抽查首尾与中段各一帧。

### Step 8 · 交付与发布

按需用 `<skill-base>/scripts/ffutil.py` 做倍速 / 压缩 / 抽封面。

- GitHub：Release 附件放高清版，README 内嵌播放器必须用 issue 附件换 CDN 链接（`<video>` 标签会被 GitHub 剥掉）。完整命令与铁律见 `<skill-base>/references/publish-github.md`。
- 平台文案：`<skill-base>/references/copywriting.md`，`promo` 用 §1，`generic` 用 §2。

## 索引

上下文变长或需要找回方向时，先复述 `current_step` 和下一步，再直达：

- 环境、路径、全部已验证踩坑：`<skill-base>/references/env-setup.md`
- 分镜 schema、TTS、字幕、BGM：`<skill-base>/references/script-and-voice.md`
- 叙事骨架（generic 模式分题材）：`<skill-base>/references/narrative.md`
- 工程结构、组件、渲染迭代、交付形态：`<skill-base>/references/remotion-scaffold.md`
- GitHub Release / README 内嵌 / gh 命令：`<skill-base>/references/publish-github.md`
- 小红书 / B站 / 视频号文案模板：`<skill-base>/references/copywriting.md`
- 完整实例（书到了宣传片，含真实数据与成品参数）：`<skill-base>/references/example-shudaole.md`
- 脚本：`scripts/gen_voice.py`（配音+时间轴）、`scripts/mimo_tts.py`（自定义音色）、`scripts/progress.py`（渲染进度）、`scripts/ffutil.py`（倍速/压缩/封面）
- 起手工程：`assets/skeleton/`，`assets/script-template.json`

索引只负责恢复方向，不替代上面的 Step 1–8。
