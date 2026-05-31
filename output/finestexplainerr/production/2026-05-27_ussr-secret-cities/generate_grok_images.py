#!/usr/bin/env python3
"""
Batch image generation for USSR Secret Cities production pack
using grok-imagine-image-lite via micuapi.ai
"""

import os
import sys
import time
import json
import requests
from pathlib import Path

# ===================== CONFIG =====================
API_KEY = "sk-kYI6yasrYFV5v8gj84TS5s43aVTc8RntuEnUMje58r8eFxYC"
BASE_URL = "https://www.micuapi.ai/v1/images/generations"
MODEL = "grok-imagine-image-lite"
SIZE = "1920x1080"          # 1080p 16:9
DELAY_SECONDS = 5           # polite delay between calls
OUTPUT_DIR = Path("images_grok_lite_1080")
PROMPTS_FILE = Path("image_prompts_scene21_plus.txt")
# ==================================================


def load_prompts(path: Path) -> list[str]:
    prompts = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                prompts.append(line)
    return prompts


def generate_image(prompt: str) -> str | None:
    """Call the API and return the image URL or None on failure."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "n": 1,
        "size": SIZE,
        "response_format": "url",
    }

    try:
        resp = requests.post(BASE_URL, headers=headers, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        if "data" in data and len(data["data"]) > 0:
            return data["data"][0]["url"]
        else:
            print(f"  [!] Unexpected response: {data}")
            return None
    except Exception as e:
        print(f"  [!] API error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"      Response: {e.response.text[:300]}")
        return None


def download_image(url: str, dest: Path) -> bool:
    """Download image from URL and save to dest."""
    try:
        r = requests.get(url, timeout=120, stream=True)
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"  [!] Download failed: {e}")
        return False


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Loading prompts from {PROMPTS_FILE}...")
    prompts = load_prompts(PROMPTS_FILE)
    print(f"Found {len(prompts)} prompts.\n")

    success = 0
    failed = 0

    for idx, prompt in enumerate(prompts, 1):
        filename = f"scene_{idx:02d}.png"
        filepath = OUTPUT_DIR / filename

        print(f"[{idx:02d}/{len(prompts)}] Generating {filename} ...")

        url = generate_image(prompt)
        if not url:
            print("  → Failed to get URL from API")
            failed += 1
            time.sleep(DELAY_SECONDS)
            continue

        if download_image(url, filepath):
            size_kb = filepath.stat().st_size // 1024
            print(f"  → Saved {filename} ({size_kb} KB)")
            success += 1
        else:
            failed += 1

        # Be nice to the API
        if idx < len(prompts):
            print(f"  (sleeping {DELAY_SECONDS}s)\n")
            time.sleep(DELAY_SECONDS)

    print("\n" + "=" * 50)
    print(f"Done. Success: {success} | Failed: {failed}")
    print(f"Images saved in: {OUTPUT_DIR.resolve()}")
    print("=" * 50)


if __name__ == "__main__":
    main()
