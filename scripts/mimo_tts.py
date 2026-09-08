#!/usr/bin/env python3
"""小米 MiMo v2.5 TTS voice design —— 按文字描述生成音色。

用法：
    python mimo_tts.py "音色描述" "要朗读的文本" out/sample.mp3

接口三个坑（已封装）：
- 端点是 /v1/chat/completions（不是 /v1/audio/speech，那个 404）
- 要朗读的文本必须放 assistant 角色，音色描述放 user，否则 400
- 音频以 base64 藏在 choices[0].message.audio.data

密钥不写进本仓库（会公开到 GitHub），只从环境变量 MIMO_API_KEY 读。
没有就报错退出，让使用者自己 export。
"""
import base64
import json
import os
import pathlib
import sys
import urllib.request

URL = "https://token-plan-cn.xiaomimimo.com/v1/chat/completions"
MODEL = "mimo-v2.5-tts-voicedesign"


def load_key() -> str:
    key = os.environ.get("MIMO_API_KEY") or ""
    if not key:
        sys.exit("缺少 MiMo API 密钥：export MIMO_API_KEY=<你的密钥>")
    return key


def tts(voice_desc: str, text: str, out_path: str) -> None:
    body = {
        "model": MODEL,
        "modalities": ["text", "audio"],
        "audio": {"format": "mp3"},
        "messages": [
            {"role": "user", "content": f"请用以下音色朗读：{voice_desc}"},
            {"role": "assistant", "content": text},
        ],
    }
    req = urllib.request.Request(
        URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {load_key()}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        resp = json.loads(r.read().decode("utf-8"))
    raw = base64.b64decode(resp["choices"][0]["message"]["audio"]["data"])
    p = pathlib.Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(raw)
    print(f"OK {p}  {len(raw) / 1024:.1f} KB")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)
    tts(sys.argv[1], sys.argv[2], sys.argv[3])
