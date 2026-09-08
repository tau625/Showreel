#!/usr/bin/env python3
"""视频后处理：倍速 / 压缩 / 抽封面。

用 imageio-ffmpeg 自带的完整 ffmpeg —— Remotion 捆绑的 ffmpeg 裁掉了 setpts，
做不了变速。参数全部走 subprocess 列表传，避免 Git Bash 把 PTS/1.5 当路径转换。

用法：
    python ffutil.py speed    in.mp4 out.mp4 1.5
    python ffutil.py compress in.mp4 out.mp4 [crf]        # 默认 crf 24
    python ffutil.py poster   in.mp4 poster.jpg [00:00:40]
    python ffutil.py probe    in.mp4                      # 时长/码率/体积
"""
import pathlib
import re
import subprocess
import sys

import imageio_ffmpeg


def ff():
    return imageio_ffmpeg.get_ffmpeg_exe()


def run(args):
    r = subprocess.run([ff(), "-y", "-loglevel", "error", *args])
    if r.returncode != 0:
        sys.exit(f"ffmpeg 失败（exit {r.returncode}）")


def speed(src, dst, factor):
    factor = float(factor)
    if not 0.5 <= factor <= 2.0:
        sys.exit("倍速超出 atempo 支持范围（0.5–2.0）；要更慢/更快请串联多个 atempo")
    run(["-i", src, "-vf", f"setpts=PTS/{factor}", "-af", f"atempo={factor}",
         "-c:v", "libx264", "-crf", "18", "-preset", "medium",
         "-c:a", "aac", "-b:a", "192k", dst])


def compress(src, dst, crf="24"):
    """压体积，用于 GitHub 附件（免费账号 10MB 上限）。
    crf 24 + slow 实测 11.67MB → 7.31MB，1080p 观感基本无损。"""
    run(["-i", src, "-c:v", "libx264", "-crf", str(crf), "-preset", "slow",
         "-pix_fmt", "yuv420p", "-movflags", "+faststart",
         "-c:a", "aac", "-b:a", "128k", dst])


def poster(src, dst, ts="00:00:40"):
    run(["-ss", ts, "-i", src, "-frames:v", "1", "-q:v", "3", dst])


def probe(src):
    """读时长与码率。imageio-ffmpeg 不带 ffprobe，所以解析 ffmpeg -i 的 stderr。
    注意：只有 -i 没有输出文件时 ffmpeg 返回非 0，这是正常的。"""
    r = subprocess.run(
        [ff(), "-hide_banner", "-i", src],
        capture_output=True, text=True, encoding="utf-8", errors="ignore",
    )
    text = r.stderr or ""
    dur = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", text)
    br = re.search(r"bitrate: (\d+) kb/s", text)
    p = pathlib.Path(src)
    if dur:
        h, m, s = dur.groups()
        total = int(h) * 3600 + int(m) * 60 + float(s)
        print(f"duration={total:.2f}s  ({int(total // 60)}:{total % 60:05.2f})")
    if br:
        print(f"bitrate={br.group(1)} kb/s")
    if not dur and not br:
        print(text[-800:] or "(读不到信息)")
    print(f"size_mb={p.stat().st_size / 1024 / 1024:.2f}")


CMDS = {
    "speed": (3, 4, lambda a: speed(*a[:2], a[2])),
    "compress": (2, 3, lambda a: compress(*a[:2], a[2] if len(a) > 2 else "24")),
    "poster": (2, 3, lambda a: poster(*a[:2], a[2] if len(a) > 2 else "00:00:40")),
    "probe": (1, 1, lambda a: probe(a[0])),
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in CMDS:
        print(__doc__)
        sys.exit(1)
    name = sys.argv[1]
    args = sys.argv[2:]
    nmin, nmax, fn = CMDS[name]
    if not nmin <= len(args) <= nmax:
        print(__doc__)
        sys.exit(1)
    fn(args)
    print(f"OK {name} -> {args[1] if name != 'probe' else args[0]}")


if __name__ == "__main__":
    main()
