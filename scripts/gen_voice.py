#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 _src/script.json 的文案逐段转成配音 mp3 + 词级字幕，并生成时间轴。

用法：
    python gen_voice.py --root <项目目录>          # 默认当前目录
    python gen_voice.py --root . --force            # 忽略复用，全部重录

产出：
    public/voice/<id>.mp3      每段配音
    _src/_tmp/<id>.srt         edge-tts 词级字幕
    _src/_tmp/manifest.json    复用判断用的文案指纹
    src/data/timeline.json     Remotion 时间轴（唯一真相源）

段长 = PAD_BEFORE + 音频时长 + extra + PAD_AFTER，按 FPS 折算帧数。
改文案 = 重录该段；只改 extra = 复用音频，秒出。
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

FPS = 30
PAD_BEFORE = 0.35   # 段前留白（秒）
PAD_AFTER = 0.55    # 段后留白，给转场和呼吸


def srt_time_to_sec(t: str) -> float:
    """00:00:01,234 -> 1.234"""
    h, m, rest = t.split(":")
    s, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def parse_srt(path: Path):
    """返回 [{'text','start','end'}, ...]"""
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    blocks = [b for b in re.split(r"\n\s*\n", text.strip()) if b.strip()]
    out = []
    for b in blocks:
        lines = [l for l in b.splitlines() if l.strip()]
        if len(lines) < 2:
            continue
        timing = next((l for l in lines if "-->" in l), None)
        if not timing:
            continue
        start_s, end_s = timing.split("-->")
        body = [l for l in lines if "-->" not in l and not l.strip().isdigit()]
        caption = " ".join(body).strip()
        if not caption:
            continue
        out.append({
            "text": caption,
            "start": srt_time_to_sec(start_s.strip()),
            "end": srt_time_to_sec(end_s.strip()),
        })
    return out


def mp3_duration(path: Path) -> float:
    try:
        from mutagen.mp3 import MP3
        return MP3(path).info.length
    except Exception:
        return 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="项目根目录（含 _src/script.json）")
    ap.add_argument("--force", action="store_true", help="忽略复用，全部重录")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    src = root / "_src"
    if not (src / "script.json").exists():
        print(f"找不到 {(src / 'script.json')}，--root 指错了吗？")
        sys.exit(1)

    voice_dir = root / "public" / "voice"
    tmp_dir = src / "_tmp"
    out_json = root / "src" / "data" / "timeline.json"
    for d in (voice_dir, tmp_dir, out_json.parent):
        d.mkdir(parents=True, exist_ok=True)

    cfg = json.loads((src / "script.json").read_text(encoding="utf-8"))
    voice = cfg.get("voice", "zh-CN-XiaoxiaoNeural")
    rate = cfg.get("rate", "-10%")
    segments = cfg["segments"]

    manifest_path = tmp_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}

    timeline = []
    for seg in segments:
        sid = seg["id"]
        mp3 = voice_dir / f"{sid}.mp3"
        srt = tmp_dir / f"{sid}.srt"

        reuse = (
            not args.force
            and mp3.exists() and mp3.stat().st_size > 0
            and srt.exists() and srt.stat().st_size > 0
            and manifest.get(sid) == seg["text"]
        )
        if reuse:
            print(f"[{sid}] 复用已有音频（文案未变）")
        else:
            cmd = [
                sys.executable, "-m", "edge_tts",
                "-v", voice,
                "-t", seg["text"],
                f"--rate={rate}",          # 必须 --rate= 形式，否则负号被当新参数
                "--write-media", str(mp3),
                "--write-subtitles", str(srt),
            ]
            r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
            if r.returncode != 0 or not mp3.exists():
                print(f"[{sid}] 配音失败:\n{r.stderr[:800]}")
                sys.exit(1)

        manifest[sid] = seg["text"]
        captions = parse_srt(srt)
        dur = mp3_duration(mp3)
        if not dur and captions:
            dur = captions[-1]["end"] + 0.2

        extra = float(seg.get("extra", 0))
        total = PAD_BEFORE + dur + extra + PAD_AFTER
        timeline.append({
            "id": sid,
            "scene": seg["scene"],
            "title": seg["title"],
            "text": seg["text"],
            "audio": f"voice/{sid}.mp3",
            "audioDuration": round(dur, 3),
            "padBefore": PAD_BEFORE,
            "extra": extra,
            "padAfter": PAD_AFTER,
            "keyPoints": seg.get("keyPoints", []),
            "audioEndFrame": int(round((PAD_BEFORE + dur) * FPS)),
            "frames": int(round(total * FPS)),
            "captions": [
                {
                    "text": c["text"],
                    "startFrame": int(round((PAD_BEFORE + c["start"]) * FPS)),
                    "endFrame": int(round((PAD_BEFORE + c["end"]) * FPS)),
                }
                for c in captions
            ],
        })
        print(f"[{sid}] {seg['title']:<8} 音频 {dur:6.2f}s  字幕 {len(captions):2d} 条")

    out_json.write_text(
        json.dumps({"fps": FPS, "segments": timeline}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    total_sec = sum(t["audioDuration"] + t["padBefore"] + t["extra"] + t["padAfter"] for t in timeline)
    voice_sec = sum(t["audioDuration"] for t in timeline)
    print(f"\n配音净时长 {voice_sec:.1f}s，成片 {total_sec:.1f}s = "
          f"{int(total_sec // 60)}分{int(total_sec % 60):02d}秒 / "
          f"{sum(t['frames'] for t in timeline)} 帧 @{FPS}fps")
    print(f"时间轴已写入 {out_json}")


if __name__ == "__main__":
    main()
