#!/usr/bin/env python3
"""Generate Scene 01 video via MiniMax API (image-to-video if URL works, else text-to-video)."""

import json
import os
import sys
import time
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import threading
import requests

API_KEY = os.environ.get(
    "MINIMAX_API_KEY",
    "sk-cp-4Rv9zYpYNcmoMCS8tL5FCecz9V5rs3aUWbzBOTWh_TqVPZgiGD4C_DcT9F9X-nShMw7MiiJxA2uef7tagN-NfDFtwqgWVppJT1Iv_rw0XGz_qSm2d2NYo0o",
)
BASE = "https://api.minimaxi.com/v1"
ROOT = Path(__file__).resolve().parent
IMAGE = ROOT / "images_grok_lite_1080" / "scene_01.png"
OUT_DIR = ROOT / "minimax_video_scene01"
OUT_VIDEO = OUT_DIR / "scene_01_arzamas16.mp4"
POLL_SEC = 10
MAX_WAIT = 900

MOTION_PROMPT = (
    "Cinematic investigative documentary, ultra-realistic 35mm film grain, cold war secrecy. "
    "Remote Russian forest at dawn, heavy barbed wire fence, raked sand strip, armed watchtower in mist. "
    "Slow subtle camera movement along the perimeter [推进], cold mist drifting, oppressive isolation, "
    "muted desaturated slate gray and cold blue, no text, no logos, no people walking, Soviet military secrecy atmosphere."
)

T2V_PROMPT = (
    "Cinematic investigative documentary still, ultra-realistic, 35mm film look, subtle grain, "
    "cold war secrecy, wide shot remote Russian forest at dawn, heavy barbed wire fence stretching into distance, "
    "raked sand strip along perimeter, armed watchtower in background, cold mist, oppressive total isolation, "
    "Soviet-era military secrecy, muted desaturated palette, minimal human presence. "
    "Slow documentary camera push forward [推进], mist moving gently."
)


def headers():
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }


def start_image_server(port: int) -> str:
    os.chdir(ROOT / "images_grok_lite_1080")
    server = ThreadingHTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    public_ip = requests.get("https://api.ipify.org", timeout=10).text.strip()
    return f"http://{public_ip}:{port}/scene_01.png", server


def create_task(payload: dict) -> str:
    r = requests.post(f"{BASE}/video_generation", headers=headers(), json=payload, timeout=60)
    r.raise_for_status()
    data = r.json()
    if data.get("base_resp", {}).get("status_code", 0) != 0:
        raise RuntimeError(f"create failed: {data}")
    task_id = data.get("task_id")
    if not task_id:
        raise RuntimeError(f"no task_id: {data}")
    return str(task_id)


def poll_task(task_id: str) -> str:
    url = f"{BASE}/query/video_generation"
    deadline = time.time() + MAX_WAIT
    while time.time() < deadline:
        r = requests.get(url, headers=headers(), params={"task_id": task_id}, timeout=60)
        r.raise_for_status()
        data = r.json()
        status = data.get("status") or data.get("data", {}).get("status")
        print(f"  status: {status}")
        if status in ("Success", "success"):
            file_id = data.get("file_id") or data.get("data", {}).get("file_id")
            if file_id:
                return str(file_id)
            raise RuntimeError(f"success but no file_id: {data}")
        if status in ("Fail", "fail", "Failed", "failed"):
            raise RuntimeError(f"generation failed: {data}")
        time.sleep(POLL_SEC)
    raise TimeoutError(f"task {task_id} not done in {MAX_WAIT}s")


def download_file(file_id: str, dest: Path) -> None:
    r = requests.get(
        f"{BASE}/files/retrieve",
        headers=headers(),
        params={"file_id": file_id},
        timeout=60,
    )
    r.raise_for_status()
    data = r.json()
    if data.get("base_resp", {}).get("status_code", 0) != 0:
        raise RuntimeError(f"retrieve failed: {data}")
    download_url = data["file"]["download_url"]
    print(f"  download: {download_url[:80]}...")
    vr = requests.get(download_url, timeout=300)
    vr.raise_for_status()
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(vr.content)
    print(f"  saved: {dest} ({dest.stat().st_size} bytes)")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if not IMAGE.is_file():
        print(f"Missing image: {IMAGE}", file=sys.stderr)
        sys.exit(1)

    meta = {
        "scene": "01 — Arzamas-16 Opening Hook",
        "source_image": str(IMAGE),
        "motion_prompt": MOTION_PROMPT,
    }

    payload = {
        "model": "MiniMax-Hailuo-2.3",
        "duration": 6,
        "resolution": "768P",
        "prompt_optimizer": True,
    }

    mode = "text-to-video"
    image_url = None
    try:
        print("Starting temp HTTP server for image-to-video...")
        image_url, _server = start_image_server(18765)
        print(f"  first_frame_image URL: {image_url}")
        payload_i2v = {
            **payload,
            "prompt": MOTION_PROMPT,
            "first_frame_image": image_url,
        }
        task_id = create_task(payload_i2v)
        mode = "image-to-video"
    except Exception as e:
        print(f"image-to-video failed ({e}), falling back to text-to-video...")
        payload_t2v = {**payload, "prompt": T2V_PROMPT}
        task_id = create_task(payload_t2v)
        mode = "text-to-video"

    meta["mode"] = mode
    meta["task_id"] = task_id
    meta["first_frame_url"] = image_url
    (OUT_DIR / "job.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print(f"Task {task_id} ({mode}), polling...")
    file_id = poll_task(task_id)
    meta["file_id"] = file_id
    download_file(file_id, OUT_VIDEO)
    (OUT_DIR / "job.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print("Done.")


if __name__ == "__main__":
    main()