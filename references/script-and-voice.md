# 分镜、配音、字幕、BGM

## 1. `_src/script.json` schema

```jsonc
{
  "voice": "zh-CN-XiaoxiaoNeural",   // TTS 音色
  "rate": "-10%",                     // 语速（负号值必须写成 --rate=-10%，见踩坑 #6）
  "note": "本片决策：16:9 / 2-3min / 截图+代码 / 配音+字幕 / 发 GitHub+小红书",
  "segments": [
    {
      "id": "s1",           // 段 id，决定 public/voice/{id}.mp3 文件名
      "scene": "intro",     // 对应 src/scenes/index.tsx registry 的 key
      "title": "抛问",      // 仅用于日志与进度显示
      "extra": 0.5,         // 配音讲完后留给画面演示的秒数 ★调总时长就动它
      "keyPoints": ["..."], // 可选：本段要点清单，场景里做视觉列表
      "text": "配音文案"    // 也是字幕内容
    }
  ]
}
```

`extra` 建议值：纯文字段 0.5，要点清单段 1.0，演示动画段 2.0–2.5。

**改文案 = 重录该段音频；只改 `extra` = 秒出，不重录。** 这就是为什么调时长优先动 `extra`。

### 改一段文案后，总长会变——要重新分配 `extra` 收回目标

改一段旁白，配音时长就变了（v1.5.0 结尾段从 79 字扩到 110 字，配音 21.5s → 31.75s，
总长从 300.0s 涨到 310.2s）。按铁律不能动旁白，只能在 `extra` 上找回来：

```
所需 extra 总和 = 目标总长 - 配音净长 - 段数 × 0.9(pad 前后)
```

拿这个数跟当前总和一比，按比例削下去即可（v1.5.0 是把 13 段从合计 30.5s 压到 20.2s）。
**注意帧是整段 `round()` 出来的**，总帧数会有 1~3 帧的零头，最后微调某一段的
`extra` 0.1s 就能精确命中（例：目标 9000 帧，算出来 9003 → 某段 −0.1s 即可）。
`extra` 压到多小算过分？演示动画段低于 1.2s 就会「话没说完画面就切了」，别再往下压。

### 场景组件里的时点一律按 `seg.frames` 的比例写

**不要写死帧号。** 文案一变、`extra` 一调，段长就变，写死的帧号全部错位。
正确姿势：

```tsx
const F = seg.frames;
const fr = (p: number) => Math.round(F * p);   // p = 0~1
const fade = (a: number, b: number) => interpolate(frame, [a, b], [0, 1], { ... });
// 用 fr(0.24) 这类比例值，别用 210
```

多段「一层讲一件事」的场景用**多层绝对定位 + 交叉溶解**（相邻两层重叠 ~40 帧），
`opacity` 控制进出，布局不用 flex 重排，就不会出现元素跳动。

### 分镜脚本的表格不要手抄

`timeline.json` 是唯一事实来源。手抄时间码必然过时（v1.5.0 改一次结尾，14 行表格 +
14 处「节奏」说明全废）。写个同步脚本按 `timeline.json` 重新生成表格与每段的节奏行，
改完重跑一次；**记得保留原文的行尾（CRLF）**，否则 diff 会因换行符全红，看不出真实改动。
参考实现：`video/promo-1.5.0/_src/sync_storyboard.py`。

## 2. 生成配音与时间轴

```bash
<python-cmd> <skill-base>/scripts/gen_voice.py --root . [--force]
```

做的事（按段）：

1. 调 edge-tts 生成 `public/voice/sN.mp3` + `_src/_tmp/sN.srt`
2. **复用判断**：mp3 与 srt 都在、`_tmp/manifest.json` 里记录的文案与当前一致 → 跳过重录
3. 用 `mutagen` 读音频真实时长（读不到就回退到字幕最后时间戳 +0.2s）
4. 段长 = `PAD_BEFORE(0.35s) + 时长 + extra + PAD_AFTER(0.55s)`，按 30fps 折算帧数
5. 解析 SRT 成字幕数组（每条带 `startFrame` / `endFrame`，已加上 padBefore 偏移）
6. 累加出每段的 `startFrame`，写 `src/data/timeline.json`

输出的 `timeline.json` 顶层：`{ "fps": 30, "segments": [...] }`。Remotion 侧只读这个文件，代码里不出现帧数。

### 音色

edge-tts 免费中文女声实测可用只有两个：

- `zh-CN-XiaoxiaoNeural` 晓晓 — 亲和自然，通用首选（书到了最终选它）
- `zh-CN-XiaoyiNeural` 晓伊 — 略年轻

知性的晓墨已下架。列全部音色：`edge-tts --list-voices | grep zh-CN`。

### MiMo voice design（要按描述捏音色时用）

```bash
export MIMO_API_KEY=<你的密钥>     # 密钥不进仓库，只从环境变量读
<python-cmd> <skill-base>/scripts/mimo_tts.py "音色描述" "要朗读的文本" out/sample.mp3
```

接口的三个坑（已封装进脚本）：

- 端点是 `/v1/chat/completions`，**不是** `/v1/audio/speech`（后者 404）
- **朗读文本必须放 `assistant` 角色**，音色描述放 `user`
- 音频以 base64 藏在 `choices[0].message.audio.data`

音色描述模板（书卷气旁白，可直接改）：

> 25–35 岁成年女声，音色温润偏暖、中低音区，气息饱满不刻意；语速中速偏慢，有呼吸留白；语调起伏小而稳，句尾平收不上扬。整体气质是纪录片旁白 + 图书馆导读——安静、可信、有文化感。

**流程硬要求**：先生成 3 个候选 15 秒样音给用户试听，选定后再全量生成，别直接全片生成。

## 3. 字幕

字幕由 SRT 自动生成，与配音天然同步，不需要手调。`Captions.tsx` 的关键参数：

- `fontSize`：默认 34（1080p 下偏小的雅致尺寸；科普/教程可到 40）
- 无底色方案：用同色系多层 `textShadow` 柔光托底，字像"印"在画面上，比贴白条高级

字幕只在 `audioEndFrame` 之前出现（`untilFrame`），之后是纯画面演示时间，不再压字。

## 4. BGM

三选一：

1. **用户提供曲子**（首选）：`cp 曲子 public/bgm-xxx.m4a`，在 `src/config.ts` 里把 `BGM_FILE` 指过去。发布时按曲子要求署名。
2. **零版权曲库**：Joakim Karud / Vlog No Copyright Music 生态，简介署名 `Music: Joakim Karud - Classic`。
3. **程序合成**（`numpy` 生成中式五声音阶拨弦，零版权风险）：需要时按这个思路现写，别用有版权的流行曲。

接入要点（`src/Promo.tsx` 骨架已实现，改 `src/config.ts` 即可）：

- 淡入 2 秒、淡出 4 秒（淡出别给 2 秒，音乐收尾太短会「啪」地断）
- 音量峰值 **0.12**，绝对不要超过 0.15，否则盖人声
- **曲长必须 ≥ 全片时长**，否则末尾一段是**完全静音**的

### ⚠️ 曲长不够是个「哑巴坑」（2026-09-11 踩到）

`<Audio>` 不会自动循环，曲子放完就静音。**Remotion 不报错，渲染日志里也看不出来**，
只有量音频电平才发现。实战：Joakim Karud - Classic 只有 3:50 = 229.7s，
而成片 5:00 —— **末尾 70 秒没有任何音乐**，全片看下来才会觉得「后半段好安静」。

**自检（渲染后必做一次，别靠耳朵）**——量「段间留白」（那 0.9s 既无配音）或片尾 extra 段的电平：

```bash
ffmpeg -ss 297 -t 3 -i out/成片.mp4 -af volumedetect -f null -
# 有 BGM 时应有 ~-28 dB（= 曲子约 -10 dB × 0.12）；-70 dB 以下就是没音乐
```

更稳的做法：整轨解码后逐秒算 RMS，一眼就能看出从第几秒开始掉下去。

**接长方法**：交叉淡化（等功率 cos/sin 权重）把中段循环一遍：

```
head[0:S] →xfade→ 原曲[S:S+K] →xfade→ 原曲[S:body_end]
总长 = body_end + K - 2×xfade
S 用 RMS 自动挑「能量最低的 1s 窗口」，避免硬接在乐句中间
```

**最容易搞砸的一点**：免版权曲子几乎都自带 10 秒左右的淡出收尾（本曲从 217s 就开始
−28 → −35 → −49 → −82 dB）。照原样保留的话，接长版的末尾同样渐弱，**等于白接**。
所以必须自动定位淡出起点（相对中位电平掉 8 dB 即视为淡出）、**把淡出段整段丢掉**，
让床保持满电平到末尾，收尾交给上面那条音量曲线。

参考实现：`video/promo-1.5.0/extend_bgm.py`（含 `body_end()` 淡出定位、
`pick_loop_start()` 挑接缝、接缝跃变与末尾电平双重自检）。
`ffmpeg` 变速/滤镜要用 `imageio-ffmpeg` 的完整版，Remotion 自带的缺 `setpts`。
