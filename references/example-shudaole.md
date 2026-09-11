# 实例：书到了（ShudaoLe）宣传片

`promo` 模式的完整落地案例。2026-09-08 全流程跑通，是本 skill 各步骤的验收参照。

## 项目参数

| 项 | 值 |
|---|---|
| 题材 | 开源教材下载器宣传片 |
| 模式 | `promo` |
| 画幅 / fps | 1920×1080 / 30fps |
| 段数 | 8 |
| 母版 | 2:54，5257 帧，17.2 MB |
| 交付版 | 1.5 倍速，1:56，11.7 MB |
| 发布 | Release v1.2.0 附件 + README 内嵌播放器（7.31MB 压缩版走 issue #2） |
| 仓库 | `tau625/ShudaoLe` |

## 八段结构（promo 骨架的标准展开）

| 段 | scene | 内容 | extra |
|---|---|---|---|
| s1 | intro | 抛问："找齐一整套教材 PDF 要花多长时间？" | 0.5 |
| s2 | pain | 两条传统路的痛点：网盘限速 / 合集几个 G 且版本存疑 | 0.5 |
| s3 | promise | **卖点前置**，5 条 `keyPoints` 做视觉清单 | 1.0 |
| s4 | platform | 界面亮相 + 四步流程 + 三平台 | 1.0 |
| s5 | token | 一键登录取令牌 | 2.0 |
| s6 | filter | 五级级联筛选 + chips + 命中数 | 2.0 |
| s7 | download | 批量勾选 + 实时进度 | 2.5 |
| s8 | outro | 开源 + PolyForm Noncommercial 1.0.0 + 版权声明 | 1.0 |

卖点 5 条（用户指定必须前置，一条不能少）：无需网盘及其会员 / 无需克隆整个项目内容 / 教材更新与国家官方平台一致 / 下载速度快不限速 / 占用小。

## 视觉系统

从产品 `smartedu_webui.html` 的 `:root` CSS 变量里取色，保证宣传片与软件本体同一套语言：

```
seal  #b23a2e 朱砂（印章 / 主色）
paper #f5f2ea 宣纸（背景）
ink   #2c2820 墨（正文）
```

字体：思源宋体 `Noto Serif SC`（标题与字幕，`fontWeight: 500`），楷体（印章），黑体（正文）。
自定义组件：`Seal.tsx` 朱砂落印动画作 logo、`AppUI.tsx` 代码复刻界面（截图缺失时的回退）。

## 声音

- 配音：edge-tts `zh-CN-XiaoxiaoNeural`，`rate=-10%`。中途试过 MiMo voice design 捏音色，最终还是选了晓晓。
- BGM：Joakim Karud - Classic。音量 0.12，淡入 2s / 淡出 4s。
  v1.2.0 里只写了「首尾 2s」且没注意曲长——曲子 3:50 < 成片 5:00，
  **末尾 70 秒是静音的**；v1.5.0 用 `extend_bgm.py` 交叉淡化接长到 302s 才补上
  （详见 `script-and-voice.md` §4 的「哑巴坑」）。
- 字幕：思源宋体 34px，无底色，四层宣纸色 `textShadow` 柔光托底。

## 关键决策记录

- 卖点单独成段（s3）而非散在流程里——用户明确要求前置。
- 截图先上 4 张真实截图（`platform/token/filter/download`），`download` 那张露出本机路径 `C:\Users\SAKE\...`，重截打码版替换后才发布。
- 全片 1.5 倍速作为发布规格，母版仍保留。
- 视频只进 Release 附件与 README 引用，不进 git。

## 复用时的注意

这个实例的 8 个 `scenes/*.tsx` 是**与书到了强绑定**的，不要直接复制到新项目。要复用的是：骨架结构、`theme.ts` 的配色取值方式、`Caption`/`UIShot`/`Paper` 三个通用组件、以及 Step 1–8 的执行顺序。
