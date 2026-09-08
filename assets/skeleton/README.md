# Remotion 视频起手工程

## 开工顺序

```bash
npm install
# 1) 写分镜：_src/script.json（参考 <skill-base>/assets/script-template.json）
# 2) 定视觉：src/theme.ts（配色 + 字体）
# 3) 写场景：src/scenes/*.tsx，并在 src/scenes/index.tsx 登记
# 4) 配音 + 时间轴
python <skill-base>/scripts/gen_voice.py --root .
# 5) 类型检查 + 预览
./node_modules/.bin/tsc --noEmit
npm run dev
# 6) 渲染
npm run render              # 全片
```

## 要改的文件

| 文件 | 改什么 |
|---|---|
| `_src/script.json` | 分镜与文案（唯一真相源） |
| `src/theme.ts` | 配色 + 字体 |
| `src/scenes/*` + `src/scenes/index.tsx` | 各段画面与注册 |
| `src/assets/shots.ts` | 真实截图开关 |
| `src/config.ts` | BGM 文件名与音量 |
| `src/Root.tsx` | 画幅 / fps（改竖版动这里） |

`timeline.ts`、`Promo.tsx`、`components/*` 是通用件，一般不用动。

## 目录

- `public/shots/` 真实截图
- `public/voice/` gen_voice.py 产出的配音
- `out/` 渲染产物（不进 git）
