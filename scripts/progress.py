#!/usr/bin/env python3
"""查询 Remotion 渲染进度。

优先解析 out/render.log 里的 `Rendered N/M, time remaining: Xs`，
读不到再数帧缓存目录（%TEMP%/react-motion-render*/element-*.jpeg），
渲染结束后报产物路径与体积。

用法：
    python progress.py --root <项目目录>          # 默认当前目录
    python progress.py --root . --out out/x.mp4   # 指定产物，用于判断是否已完成
"""
import argparse
import glob
import json
import os
import pathlib
import re
import sys
import time

FPS = 30


def load_total(root: pathlib.Path):
    tl = root / "src" / "data" / "timeline.json"
    if not tl.exists():
        return None, []
    d = json.loads(tl.read_text(encoding="utf-8"))
    segs, cur = [], 0
    for s in d["segments"]:
        segs.append((s["id"], s.get("title", ""), cur, cur + s["frames"]))
        cur += s["frames"]
    return cur, segs


def seg_name_at(segs, frame):
    for sid, title, a, b in segs:
        if a <= frame < b:
            return f"{sid} {title}（{a}–{b}）"
    return "编码收尾中（帧已渲完，正在封装 mp4）"


def bar(done, total, width=32):
    r = max(0.0, min(1.0, done / total))
    n = int(r * width)
    return "[" + "#" * n + "." * (width - n) + f"] {r*100:5.1f}%"


def read_log_progress(log: pathlib.Path):
    if not log.exists():
        return None
    text = log.read_text(encoding="utf-8", errors="ignore")
    m = re.findall(r"Rendered (\d+)/(\d+)(?:, time remaining: (\d+)s)?", text)
    if not m:
        return None
    last_n, last_t, remain = m[-1]
    enc = re.findall(r"Encoded (\d+)/(\d+)", text)
    finished = ("out/" in text and ".mp4" in text) or (enc and enc[-1][0] == enc[-1][1])
    return int(last_n), int(last_t), int(remain) if remain else None, finished


def find_render_dir():
    tmp = os.environ.get("TEMP") or os.environ.get("TMP") or "/tmp"
    cands = glob.glob(os.path.join(tmp, "react-motion-render*"))
    return max(cands, key=lambda p: os.path.getmtime(p)) if cands else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default=None, help="产物路径；不传就取 out/ 下最新 mp4")
    args = ap.parse_args()

    root = pathlib.Path(args.root).resolve()
    total, segs = load_total(root)
    if total is None:
        print(f"找不到 {root / 'src/data/timeline.json'}，先跑 gen_voice.py")
        sys.exit(1)

    if args.out:
        out = pathlib.Path(args.out)
    else:
        mps = sorted((root / "out").glob("*.mp4"), key=lambda p: p.stat().st_mtime) if (root / "out").exists() else []
        out = mps[-1] if mps else root / "out" / "unnamed.mp4"

    log = read_log_progress(root / "out" / "render.log")
    if log is not None:
        done, total_log, remain, finished = log
        if not finished and done < total_log:
            print(f"进度 {bar(done, total_log)}   {done}/{total_log} 帧  "
                  f"≈ {done/FPS:.0f}s / {total_log/FPS:.0f}s")
            print(f"当前段落：{seg_name_at(segs, done)}")
            if remain:
                print(f"Remotion 估计剩余：{remain} 秒")
            return

    if out.exists() and out.stat().st_size > 0:
        print(f"渲染已完成\n产物：{out}  {out.stat().st_size/1024/1024:.1f} MB")
        return

    rd = find_render_dir()
    if rd is None:
        print("没在渲染，也没找到产物。先跑：")
        print("  ./node_modules/.bin/remotion render PromoMain out/x.mp4 > out/render.log 2>&1")
        return

    def count():
        return len(list(pathlib.Path(rd).glob("element-*.jpeg")))

    done = count()
    print(f"帧缓存目录：{rd}")
    print(f"进度 {bar(done, total)}   {done}/{total} 帧  ≈ {done/FPS:.0f}s / {total/FPS:.0f}s")
    print(f"当前段落：{seg_name_at(segs, done)}")

    t0, c0 = time.time(), done
    time.sleep(5)
    c1 = count()
    dt = time.time() - t0
    if dt > 0 and c1 > c0:
        spd = (c1 - c0) / dt
        print(f"速度 ≈ {spd:.1f} 帧/秒   剩余 {total - c1} 帧 ≈ {(total - c1)/spd/60:.1f} 分钟")


if __name__ == "__main__":
    main()
