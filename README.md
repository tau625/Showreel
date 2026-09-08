# 展卷 Showreel

**用代码写视频 —— 给软件做宣传片的完整 AI 流水线。**

> 展卷：宣传片就是把软件功能像卷轴一样徐徐展开，一段一段演示给人看。
> Showreel：英文里"用来展示自己的短片"的现成说法，正是这个品类。

这是一个 **AI 技能（Agent Skill）**。装进你的 AI 助手后，一句"给我的软件做个宣传视频"，它会带着你从分镜一路走到发布；也可以只用它仓库里的脚本和工程骨架，自己手动跑流水线。

## 流水线覆盖

| 环节 | 内容 |
|---|---|
| 分镜 | 叙事骨架（卖点前置）、`extra` 机制——调时长只改数字，不触发重录 |
| 配音 | edge-tts 免费音色 / MiMo voice design 按文字描述捏音色，词级字幕自动对齐 |
| 画面 | Remotion 起手工程：主题系统、场景注册表、截图开关（没截图自动回退代码复刻界面） |
| BGM | 淡入淡出曲线、音量压人声之下，附零版权方案 |
| 渲染 | Studio 实时预览、局部渲染省时间、后台渲染进度监控脚本 |
| 交付 | 倍速版（宣传常用 1.5x）、压体积、抽封面 |
| 发布 | GitHub Release 附件、README 内嵌播放器（issue 附件换 CDN 链接的正确姿势）、小红书 / B站 / 视频号文案模板 |

## 两种模式

| | `promo` 产品宣传 | `generic` 通用 |
|---|---|---|
| 用途 | 给软件 / 项目做宣传片、功能演示 | 科普讲解、教程演示、数据报告、活动招新 |
| 叙事骨架 | 抛问 → 痛点 → **卖点前置** → 流程演示 ×N → 收尾（许可/CTA） | 按题材查表：误解→原理→例证 / 目标→步骤→验证 / 结论→指标→建议 |
| 画面主力 | 真实截图 / 录屏 / 界面复刻 | 代码动画 / 数据图表 / 示意图 |
| 发布重心 | GitHub + README 内嵌 + 小红书 + B站 | B站 / 视频号 + 时间戳章节 |

模式在开工时判定，只有分镜骨架和文案模板两处分流，其余步骤完全共用。

## 它做出来的片子

下面这条完全由本流水线生产——Remotion 渲染、edge-tts 配音、词级字幕、程序化 BGM，8 段分镜，1.5 倍速交付（1 分 56 秒）：

https://github.com/user-attachments/assets/2e59032c-0cc7-4e00-802e-52b620c795b5

源项目：[tau625/ShudaoLe](https://github.com/tau625/ShudaoLe) —— 国家中小学智慧教育平台教材下载器。

## 安装

```bash
# WorkBuddy：克隆到用户级技能目录
git clone https://github.com/tau625/showreel.git ~/.workbuddy/skills/showreel

# 依赖（一次性）
pip install edge-tts mutagen numpy pillow imageio-ffmpeg fonttools
```

装完后新开会话即可触发，无需其他配置。同为 SKILL.md 格式的 agent（Claude Code 等）把目录放进对应的 skills 目录即可。

## 使用

对 AI 说：

```
给我的项目 XX 做个宣传视频
把这条视频嵌进 README / 发个 Release 附件
做个科普视频 / 教程视频
```

AI 会先和你拍板 5 件事（画幅 / 时长 / 画面素材 / 声音方案 / 发布平台），然后按 8 步流水线推进：分镜 → 配音样音试听 → 场景实现 → 渲染 → 交付发布。硬规则都写在 SKILL.md 里：卖点必须前置、新音色先出样音再全量、样式改动攒批渲染等。

脚本也可以脱离 AI 单独用：

```bash
python scripts/gen_voice.py --root <项目>   # 分镜 JSON → 配音 + 字幕 + 时间轴
python scripts/progress.py --root <项目>    # 渲染进度（当前段 / 估计剩余）
python scripts/ffutil.py speed in.mp4 out.mp4 1.5   # 倍速 / 压缩 / 封面
MIMO_API_KEY=<key> python scripts/mimo_tts.py "音色描述" "文本" out.mp3
```

## 环境要求

| 依赖 | 说明 |
|---|---|
| Node ≥ 20 | 跑 Remotion（起手工程 `npm install`） |
| Python ≥ 3.10 | 脚本与 TTS |
| Edge 或 Chrome | Remotion 渲染内核（国内网络拉不动 Chrome Headless Shell，工程里已配好用本机浏览器） |
| gh CLI | 仅发布环节需要 |

国内网络的坑（raw 被墙、Chrome 下载卡死、ffmpeg 缺 setpts、Git Bash 路径转换、gh 非交互登录等 13 条）都已踩过并写进 `references/env-setup.md` 的踩坑表，照解法走即可，不用重新试错。

## 目录结构

```
├── SKILL.md                     # 技能主文件：规则 + 8 步工作流
├── references/                  # 分主题深挖文档
│   ├── env-setup.md             #   环境与 13 条踩坑表
│   ├── script-and-voice.md      #   分镜 schema / TTS / 字幕 / BGM
│   ├── narrative.md             #   generic 模式按题材的叙事骨架
│   ├── remotion-scaffold.md     #   工程结构 / 渲染迭代 / 交付形态
│   ├── publish-github.md        #   Release 附件 + README 内嵌播放器
│   ├── copywriting.md           #   小红书 / B站 / 视频号文案模板
│   └── example-shudaole.md      #   完整实例（含成品参数）
├── scripts/                     # 可独立使用的工具脚本
│   ├── gen_voice.py             #   配音 + 词级字幕 + 时间轴生成
│   ├── progress.py              #   渲染进度监控
│   ├── ffutil.py                #   倍速 / 压缩 / 封面（完整 ffmpeg）
│   └── mimo_tts.py              #   MiMo voice design（密钥走环境变量）
└── assets/
    ├── script-template.json     # 分镜脚本模板（含注释说明）
    └── skeleton/                # Remotion 起手工程，复制即用
```

## 致谢

实例项目的视觉系统（朱砂 / 宣纸 / 墨）来自 [tau625/ShudaoLe](https://github.com/tau625/ShudaoLe)。
背景音乐生态：Joakim Karud / Vlog No Copyright Music。
