# Remotion 工程结构、渲染与交付

起手工程在 `<skill-base>/assets/skeleton/`，Step 2 直接复制。

## 1. 结构

```
src/
├── config.ts          # ★ BGM 文件名与音量、淡入淡出秒数
├── theme.ts           # ★ 配色 + 字体（换皮只改这里）
├── timeline.ts        # 通用：读 timeline.json 编排，勿改
├── Promo.tsx          # 通用：BGM 曲线 + 段 Sequence + 转场淡入淡出，勿改
├── Root.tsx           # Composition 尺寸 / fps，画幅在这里改
├── components/
│   ├── Paper.tsx      # 纸质背景（vignette + 纹理）
│   ├── Captions.tsx   # 无底色字幕（字号/字体/描边可调）
│   └── UIShot.tsx     # 截图容器，null 时回退到代码复刻
├── assets/shots.ts    # ★ 截图开关
├── scenes/
│   ├── index.tsx      # ★ 场景注册表，新增场景在这里登记
│   └── *.tsx          # ★ 各段画面，每个项目重写
└── data/timeline.json # gen_voice.py 产出，勿手改
```

**每个项目只需要改打 ★ 的文件**，其余是通用件。

## 2. 换皮三处

**`theme.ts`** — 配色常量 + 字体族。从被演示产品的 CSS 变量里取值最稳（宣传片与产品本体同一套视觉语言）。参考取值：

```ts
export const C = {
  seal: '#b23a2e',   // 主色（印章 / 强调）
  paper: '#f5f2ea',  // 背景
  ink: '#2c2820',    // 正文
  muted: '#8d8370',  // 次要文字
  line: '#e7e1d3',   // 描边
} as const;
```

**`scenes/*.tsx`** — 每段一个组件，签名 `{ seg: Segment }`。可用数据：`seg.frames`、`seg.audioEndFrame`、`seg.captions`、`seg.keyPoints`、`seg.text`。
用 `useCurrentFrame()` 做动画，用 `interpolate` + `ease.out`（theme 里已给缓动）。

**`assets/shots.ts`** — 有真实截图就填路径，没有填 `null` 回退到代码复刻：

```ts
export const shots: Record<string, string | null> = {
  platform: 'shots/platform.png',
  token: null,   // 还没截，先用代码复刻
};
```

场景组件里用 `<UIShot scene="platform" width={1200}>{回退内容}</UIShot>` 包起来，截图到位后改一行即可切换。

新增场景要在 `scenes/index.tsx` 的 registry 登记；漏登记会渲染 FallbackScene（显示段标题）而不崩溃。

## 3. 画幅与时长

`Root.tsx` 里改 `width` / `height` / `fps`。总时长由 `TOTAL_FRAMES` 自动算，不要手填。

竖版（9:16）不要只改尺寸——构图会崩。要么新建 Composition 让场景用 `useVideoConfig()` 自适应，要么单独调一版构图。

## 4. 渲染与迭代

```bash
./node_modules/.bin/remotion studio                                        # 实时预览，调样式首选，零渲染
./node_modules/.bin/remotion still PromoMain out/f.png --frame=N           # 单帧抽查
./node_modules/.bin/remotion render PromoMain out/x.mp4 --frames=A-B       # 只渲某段，改场景时用它
./node_modules/.bin/remotion render PromoMain out/preview.mp4 --scale=0.5  # 半分辨率粗看
./node_modules/.bin/remotion render PromoMain out/x.mp4 > out/render.log 2>&1  # 全片
<python-cmd> <skill-base>/scripts/progress.py --root .                     # 另开终端看进度
```

`out/` 必须存在，不存在时渲染会直接失败（骨架里已带 `out/.gitkeep`）。

`progress.py` 优先解析 `out/render.log` 里的 `Rendered N/M, time remaining: Xs`，并显示当前处在哪个分镜段。

**迭代原则**：Studio 和局部渲染是免费的，全渲是贵的。样式改动攒一批，最后只全渲一次交付。改文案重跑 `gen_voice.py` 后必须全渲（时间轴变了）。

## 5. 交付形态

| 需求 | 命令 |
|---|---|
| 倍速版 | `<python-cmd> <skill-base>/scripts/ffutil.py speed in.mp4 out.mp4 1.5` |
| 压到 10MB 内 | `... ffutil.py compress in.mp4 out.mp4 24` |
| 封面图 | `... ffutil.py poster in.mp4 poster.jpg 00:00:40` |
| 透明通道（叠实拍） | `remotion render --sequence --image-format=png`，别渲 mp4 |
| 竖版 | 见上面 §3 |

1.5 倍速是宣传片的常用交付规格：2:54 母版 → 1:56，节奏更紧。**母版和倍速版都留着**，发布页放倍速版、附件放高清版。
