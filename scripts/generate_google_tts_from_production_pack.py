#!/usr/bin/env python3
import argparse
import base64
import json
import mimetypes
import os
import re
import struct
import urllib.request
from pathlib import Path


def load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def parse_scenes(markdown: str) -> list[dict]:
    scene_sections = re.finditer(r"(?ms)^## Scene\s+(\d+)\s+—.*?(?=^## Scene\s+\d+\s+—|\Z)", markdown)
    scenes = []
    for match in scene_sections:
        scene_number = int(match.group(1))
        section = match.group(0)
        audio_match = re.search(
            r"(?ms)^### (?:C\) Audio scena|D\) Prompt audio — Gemini TTS)\nScene\n(.*?)\n\nSample Context\n(.*?)\n\nText\n(.*?)(?:\n\n---|\Z)",
            section,
        )
        if not audio_match:
            continue
        scenes.append(
            {
                "scene_number": scene_number,
                "scene": audio_match.group(1).strip(),
                "sample_context": audio_match.group(2).strip(),
                "text": audio_match.group(3).strip(),
            }
        )
    return scenes


def parse_audio_mime_type(mime_type: str) -> dict[str, int]:
    bits_per_sample = 16
    rate = 24000
    for param in mime_type.split(";"):
        param = param.strip()
        if param.lower().startswith("rate="):
            try:
                rate = int(param.split("=", 1)[1])
            except (ValueError, IndexError):
                pass
        elif param.startswith("audio/L"):
            try:
                bits_per_sample = int(param.split("L", 1)[1])
            except (ValueError, IndexError):
                pass
    return {"bits_per_sample": bits_per_sample, "rate": rate}


def convert_to_wav(audio_data: bytes, mime_type: str) -> bytes:
    p = parse_audio_mime_type(mime_type)
    bits_per_sample, sample_rate = p["bits_per_sample"], p["rate"]
    num_channels = 1
    data_size = len(audio_data)
    bytes_per_sample = bits_per_sample // 8
    block_align = num_channels * bytes_per_sample
    byte_rate = sample_rate * block_align
    chunk_size = 36 + data_size
    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",
        chunk_size,
        b"WAVE",
        b"fmt ",
        16,
        1,
        num_channels,
        sample_rate,
        byte_rate,
        block_align,
        bits_per_sample,
        b"data",
        data_size,
    )
    return header + audio_data


def build_gemini_prompt(scene: dict, style: str, pace: str) -> str:
    return (
        "Read the following transcript based on the director's note.\n\n"
        "# Director's note\n"
        f"Style: {style}\n"
        f"Pace: {pace}.\n\n"
        "## Scene:\n"
        f"{scene['scene']}\n\n"
        "## Sample Context:\n"
        f"{scene['sample_context']}\n\n"
        "## Transcript:\n"
        f"{scene['text']}"
    )


def generate_cloud_tts_audio(
    api_key: str,
    text: str,
    output_base_path: Path,
    language_code: str,
    voice_name: str,
    speaking_rate: float,
    pitch: float,
    audio_encoding: str,
) -> list[str]:
    url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={api_key}"
    payload = {
        "input": {"text": text},
        "voice": {"languageCode": language_code, "name": voice_name},
        "audioConfig": {
            "audioEncoding": audio_encoding,
            "speakingRate": speaking_rate,
            "pitch": pitch,
        },
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as response:
        data = json.loads(response.read().decode("utf-8"))

    audio_content = data.get("audioContent")
    if not audio_content:
        raise RuntimeError(f"Cloud TTS response missing audioContent: {data}")

    binary = base64.b64decode(audio_content)
    extension = {
        "MP3": ".mp3",
        "LINEAR16": ".wav",
        "OGG_OPUS": ".ogg",
    }.get(audio_encoding, ".bin")

    output_path = output_base_path.with_suffix(extension)
    output_path.write_bytes(binary)
    return [str(output_path)]


def generate_gemini_tts_audio(
    api_key: str,
    model: str,
    voice_name: str,
    prompt: str,
    output_base_path: Path,
) -> list[str]:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    config = types.GenerateContentConfig(
        temperature=1,
        response_modalities=["audio"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice_name)
            )
        ),
    )

    saved = []
    file_index = 0
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=[types.Content(role="user", parts=[types.Part.from_text(text=prompt)])],
        config=config,
    ):
        if not chunk.parts:
            continue
        part = chunk.parts[0]
        if not (part.inline_data and part.inline_data.data):
            continue

        inline_data = part.inline_data
        data_buffer = inline_data.data
        ext = mimetypes.guess_extension(inline_data.mime_type)
        if ext is None:
            ext = ".wav"
            data_buffer = convert_to_wav(inline_data.data, inline_data.mime_type)

        suffix = f"_{file_index}" if file_index > 0 else ""
        out = output_base_path.with_name(output_base_path.name + suffix).with_suffix(ext)
        out.write_bytes(data_buffer)
        saved.append(str(out))
        file_index += 1
    return saved


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate TTS from production_pack_it.md scenes")
    parser.add_argument("--pack", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--start-scene", type=int, default=1)
    parser.add_argument("--end-scene", type=int, default=None)
    parser.add_argument("--backend", choices=["cloud", "gemini"], default="gemini")
    parser.add_argument("--api-key-env", default="GEMINI_API_KEY")
    parser.add_argument("--env-file", default=".env")

    parser.add_argument("--model", default="gemini-3.1-flash-tts-preview")
    parser.add_argument("--voice", default="Sadachbia")
    parser.add_argument(
        "--style",
        default="Professional, authoritative, clear articulation with standard broadcast cadence.",
    )
    parser.add_argument("--pace", default="Natural conversational pace")

    parser.add_argument("--language-code", default="en-US")
    parser.add_argument("--cloud-voice", default="en-US-Neural2-D")
    parser.add_argument("--speaking-rate", type=float, default=0.94)
    parser.add_argument("--pitch", type=float, default=0.0)
    parser.add_argument("--audio-encoding", choices=["MP3", "LINEAR16", "OGG_OPUS"], default="MP3")

    args = parser.parse_args()

    load_env_file(Path(args.env_file))
    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        raise RuntimeError(f"Missing API key in {args.api_key_env} (or {args.env_file}).")

    pack_path = Path(args.pack)
    if not pack_path.exists():
        raise FileNotFoundError(f"Pack not found: {pack_path}")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    scenes = parse_scenes(pack_path.read_text(encoding="utf-8"))
    selected = [s for s in scenes if s["scene_number"] >= args.start_scene]
    if args.end_scene is not None:
        selected = [s for s in selected if s["scene_number"] <= args.end_scene]

    if not selected:
        print("No scenes selected.")
        return

    manifest = {
        "pack": str(pack_path),
        "backend": args.backend,
        "output_dir": str(output_dir),
        "start_scene": args.start_scene,
        "end_scene": args.end_scene,
        "files": [],
    }

    for scene in selected:
        n = scene["scene_number"]
        base_file = output_dir / f"scene_{n:02d}"

        if args.backend == "cloud":
            saved_files = generate_cloud_tts_audio(
                api_key=api_key,
                text=scene["text"],
                output_base_path=base_file,
                language_code=args.language_code,
                voice_name=args.cloud_voice,
                speaking_rate=args.speaking_rate,
                pitch=args.pitch,
                audio_encoding=args.audio_encoding,
            )
        else:
            prompt = build_gemini_prompt(scene, args.style, args.pace)
            saved_files = generate_gemini_tts_audio(
                api_key=api_key,
                model=args.model,
                voice_name=args.voice,
                prompt=prompt,
                output_base_path=base_file,
            )

        print(f"Scene {n}: generated {len(saved_files)} file(s)")
        for p in saved_files:
            print(f"  - {p}")
            manifest["files"].append({"scene": n, "path": p, "text": scene["text"]})

    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Manifest saved: {manifest_path}")


if __name__ == "__main__":
    main()
