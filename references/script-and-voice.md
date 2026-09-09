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

- 首尾各 2 秒淡入淡出
- 音量峰值 **0.12**，绝对不要超过 0.15，否则盖人声
- 曲长要 ≥ 全片时长，否则需要循环
