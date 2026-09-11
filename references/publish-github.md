# GitHub 发布：Release 附件 + README 内嵌播放器

```bash
export GH_TOKEN=$(gh auth token)   # 非交互 shell 必加，否则 gh 报未登录
```

## 1. Release 附件（高清母版）

```bash
gh release upload v1.2.0 ./demo-1.5x.mp4
gh release upload v1.2.0 ./demo.mp4        # 可多次追加
```

- 附件名**必须用 ASCII**，中文名直链会被百分号转义，难看且不好引用。
- 误删后重传：再跑一次 `gh release upload`，直链不变、README 不用改。

## 2. README 内嵌播放器（关键）

**铁律：Release 附件的 mp4 在 README 里永远只渲染成下载链接。** GitHub 的 HTML 过滤器会把 `<video>` 整个剥成空 `<p>`；只有自家 CDN（`user-images.githubusercontent.com` / `github.com/user-attachments`）上的视频才会渲染成内嵌播放器。

**别想着换 CDN 绕过附件上传**（2026-09-11 逐一实测，`gh api markdown` 验证）：把 mp4 传到自己仓库再用
`raw.githubusercontent.com` / `media.githubusercontent.com`（LFS）/ `cdn.jsdelivr.net`（jsDelivr）/
`objects.githubusercontent.com` 当 `<video src>` —— **这四种全部被剥成空 `<p>`**，白费功夫。
另外 `raw.githubusercontent.com` 在国内本来就被墙，就算能渲染也是给海外用户看的。
**唯一可行路径就是走 issue 附件换 `user-attachments` 直链。**

正确做法：

```bash
# 1) 压到 10MB 以内（免费账号视频上限，付费 100MB）
<python-cmd> <skill-base>/scripts/ffutil.py compress in.mp4 out-web.mp4 24
# 参考：11.67MB → 7.31MB（crf 24 + slow preset），1080p 观感无损

# 2) 作为附件发到 issue，换 user-attachments 直链
gh issue comment <N> -R <owner>/<repo> --body "演示视频" --attach ./out-web.mp4
# 视频不能带 #alt 后缀，会报 cannot set alt text on video
```

拿到的 `https://github.com/user-attachments/assets/<uuid>` **裸链接写进 README 即可**，GitHub 自动渲染成播放器：

```markdown
## 功能演示

https://github.com/user-attachments/assets/2e59032c-0cc7-4e00-802e-52b620c795b5

> 演示内容：……（1 分 56 秒，1.5 倍速）。
> 更高画质见 [Release 附件](https://github.com/<owner>/<repo>/releases/download/<tag>/<file>.mp4)。
```

推送前预演渲染结果（不用真推送）：

```bash
GH_TOKEN=$(gh auth token) gh api markdown -f text='<粘贴你的 user-attachments 链接>' \
  -f mode=gfm -f context=<owner>/<repo>
```

返回的 HTML 里出现 `<video` 才算能渲染成播放器，否则就是被剥掉了。

用 issue 承载附件时，建议专门开一个"演示视频"issue 并置顶说明，避免被误关（关掉不影响链接有效性）。

## 3. 不把视频提交进 git

```
# .gitignore
out/
video/
*.mp4
*.mov
```

41MB 的 mp4 一旦 `git add` 就永久留在 `.git` 历史里（书到了项目 `.git` 原本才 29MB）。已经误提交了才需要 `git filter-repo`，很麻烦，防住即可。

## 4. 发布检查清单

- [ ] 截图里没有本机用户名 / 绝对路径 / 令牌
- [ ] 开源许可标注准确（如 PolyForm Noncommercial 1.0.0）
- [ ] BGM 已按曲子要求署名
- [ ] README 播放器链接是 `user-attachments` 域名（不是 release download 域名）
- [ ] 附件名全 ASCII
- [ ] `git status` 里没有 mp4
