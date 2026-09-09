# Showreel · 展卷

**Videos written in code — a complete AI pipeline for making promo videos for your software.**

> 展卷 (zhǎn juàn, "unrolling a scroll"): a promo video unrolls your software's
> features like a handscroll, scene by scene, for the viewer.
> Showreel: the established English word for exactly this kind of short,
> self-introduction film.

This is an **Agent Skill**. Once installed in your AI assistant, a single
sentence — "make a promo video for my software" — takes you from storyboard all
the way to publishing. You can also skip the AI part and drive the scripts and
the project skeleton manually.

**[中文文档](README.md)** · English

## What the pipeline covers

| Stage | What you get |
|---|---|
| Storyboard | Narrative skeletons (selling points up front); an `extra` mechanism — adjust total length by changing a number, never re-recording voice-over |
| Voice-over | edge-tts free voices / MiMo voice design (describe a voice in words, get it generated); word-level captions auto-aligned to audio |
| Visuals | A Remotion starter project: theme system, scene registry, screenshot switch (no screenshots? auto-falls back to a code-rebuilt UI) |
| BGM | Fade-in/out curves, volume kept under the voice track, zero-copyright options included |
| Rendering | Studio live preview, partial renders to save time, background render-progress monitor |
| Delivery | Sped-up cut (1.5x is the promo standard), size compression, poster frame |
| Publishing | GitHub Release assets, README embedded player (the issue-attachment → CDN-link trick), copy templates for Xiaohongshu / Bilibili / WeChat Channels |

## Two modes

| | `promo` — product marketing | `generic` — general purpose |
|---|---|---|
| Use case | Promo & feature-demo videos for your software/project | Explainers, tutorials, data reports, recruitment |
| Narrative skeleton | Hook → pain points → **selling points up front** → N demos → closing (license/CTA) | Pick per topic: misconception→mechanism→evidence / goal→steps→verification / conclusion→metrics→recommendations |
| Main visuals | Real screenshots / screen recordings / rebuilt UI | Code-driven animation / data charts / diagrams |
| Publishing focus | GitHub + embedded README player + Xiaohongshu + Bilibili | Bilibili / Channels + timestamped chapters |

The mode is decided up front and only affects two things — the storyboard
skeleton and the copy templates. Everything else is shared.

## A film it made

Produced entirely by this pipeline — Remotion rendering, edge-tts voice-over,
word-level captions, 8-scene storyboard, 1.5x delivery cut (1 min 56 s):

https://github.com/user-attachments/assets/2e59032c-0cc7-4e00-802e-52b620c795b5

Source project: [tau625/ShudaoLe](https://github.com/tau625/ShudaoLe) — a
textbook downloader for China's national smart-education platform.

## Install

```bash
git clone https://github.com/tau625/showreel.git ~/.workbuddy/skills/showreel

# One-time dependencies
pip install edge-tts mutagen numpy pillow imageio-ffmpeg fonttools
```

Start a new session and it just works. Other SKILL.md-style agents (Claude
Code, etc.): drop the folder into their skills directory.

## Usage

Tell your AI:

```
Make a promo video for my project XX
Embed this video in the README / attach it to a Release
Make an explainer / tutorial video
```

The AI first locks down 5 decisions with you (aspect ratio / target length /
visual sources / audio plan / publishing platforms), then runs the 8-step
pipeline: storyboard → voice samples for approval → scene implementation →
rendering → delivery & publishing. Hard rules live in SKILL.md — selling
points must come first, new voices get sample approval before full generation,
style changes are batched before a full render, and so on.

The scripts also work standalone:

```bash
python scripts/gen_voice.py --root <project>   # storyboard JSON → voice + captions + timeline
python scripts/progress.py --root <project>    # render progress (current scene / ETA)
python scripts/ffutil.py speed in.mp4 out.mp4 1.5   # speed-up / compress / poster
MIMO_API_KEY=<key> python scripts/mimo_tts.py "voice description" "text" out.mp3
```

## Requirements

| Dependency | Notes |
|---|---|
| Node ≥ 20 | Runs Remotion (`npm install` in the starter project) |
| Python ≥ 3.10 | Scripts & TTS |
| Edge or Chrome | Remotion's render engine (China-network users: the bundled Chrome Headless Shell download stalls; the starter project is pre-configured to use your local browser) |
| gh CLI | Publishing stage only |

The China-network pitfalls (blocked raw.githubusercontent, Chrome download
hangs, bundled ffmpeg missing `setpts`, Git Bash path mangling, non-interactive
`gh` auth — 13 entries) have all been hit and solved; the fixes live in
`references/env-setup.md`. Follow them instead of re-debugging.

## Repository layout

```
├── SKILL.md                     # The skill itself: rules + 8-step workflow
├── references/                  # Deep-dive docs by topic
│   ├── env-setup.md             #   Environment + the 13-entry pitfall table
│   ├── script-and-voice.md      #   Storyboard schema / TTS / captions / BGM
│   ├── narrative.md             #   Per-topic narrative skeletons (generic mode)
│   ├── remotion-scaffold.md     #   Project structure / render iteration / delivery
│   ├── publish-github.md        #   Release assets + README embedded player
│   ├── copywriting.md           #   Copy templates: Xiaohongshu / Bilibili / Channels
│   └── example-shudaole.md      #   Full worked example (with final numbers)
├── scripts/                     # Standalone tooling
│   ├── gen_voice.py             #   Voice-over + word-level captions + timeline
│   ├── progress.py              #   Render progress monitor
│   ├── ffutil.py                #   Speed / compress / poster (full ffmpeg)
│   └── mimo_tts.py              #   MiMo voice design (key via env var)
└── assets/
    ├── script-template.json     # Storyboard template (annotated)
    └── skeleton/                # Remotion starter project — copy & go
```

## Credits

The visual system of the worked example (cinnabar / rice-paper / ink) comes
from [tau625/ShudaoLe](https://github.com/tau625/ShudaoLe).
Music ecosystem: Joakim Karud / Vlog No Copyright Music.

## License

[MIT](LICENSE)
