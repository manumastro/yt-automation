#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import requests
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)

YOUTUBE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")


def extract_video_id(value: str) -> str:
    value = value.strip()
    if YOUTUBE_ID_RE.fullmatch(value):
        return value

    parsed = urlparse(value)
    host = parsed.netloc.lower()

    if host.startswith("www."):
        host = host[4:]

    if host in {"youtube.com", "m.youtube.com"}:
        # https://www.youtube.com/watch?v=VIDEO_ID
        if parsed.path == "/watch":
            qs = parse_qs(parsed.query)
            if "v" in qs and qs["v"]:
                return qs["v"][0]
        # https://www.youtube.com/shorts/VIDEO_ID
        m = re.match(r"^/shorts/([A-Za-z0-9_-]{11})", parsed.path)
        if m:
            return m.group(1)
        # https://www.youtube.com/embed/VIDEO_ID
        m = re.match(r"^/embed/([A-Za-z0-9_-]{11})", parsed.path)
        if m:
            return m.group(1)

    if host == "youtu.be":
        m = re.match(r"^/([A-Za-z0-9_-]{11})", parsed.path)
        if m:
            return m.group(1)

    raise ValueError(f"Impossibile estrarre il video_id da: {value}")


def format_timestamp(seconds: float) -> str:
    total = int(seconds)
    hours, rem = divmod(total, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def choose_transcript(transcript_list, preferred_languages: list[str] | None):
    available = list(transcript_list)
    if not available:
        return None

    if preferred_languages:
        preferred = [lang.strip().lower() for lang in preferred_languages if lang.strip()]
        for lang in preferred:
            for transcript in available:
                code = (transcript.language_code or "").lower()
                name = (transcript.language or "").lower()
                if code == lang or code.startswith(lang) or name.startswith(lang):
                    return transcript

    return available[0]


def build_output_text(items: list[dict]) -> str:
    lines = []
    for item in items:
        text = str(item.get("text", "")).replace("\n", " ").strip()
        start = format_timestamp(float(item.get("start", 0.0)))
        lines.append(f"[{start}] {text}")
    return "\n".join(lines)


def parse_vtt_to_items(vtt_content: str) -> list[dict]:
    """Converte contenuto VTT in formato items compatibile."""
    items = []
    lines = vtt_content.split("\n")
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Cerca timestamp (formato: 00:00:00.000 --> 00:00:02.000)
        if "-->" in line:
            parts = line.split("-->")
            start_str = parts[0].strip().split(".")[0]  # Rimuovi millisecondi per parsing
            
            # Converti timestamp in secondi
            time_parts = start_str.replace(",", ".").split(":")
            if len(time_parts) == 3:
                hours, minutes, seconds = time_parts
                start_seconds = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
            elif len(time_parts) == 2:
                minutes, seconds = time_parts
                start_seconds = int(minutes) * 60 + float(seconds)
            else:
                start_seconds = float(time_parts[0])
            
            # Raccogli il testo (può essere su più righe)
            text_lines = []
            i += 1
            while i < len(lines):
                current_line = lines[i].strip()
                # Fine del blocco: riga vuota, numero, o nuovo timestamp
                if not current_line or current_line.isdigit() or "-->" in current_line:
                    break
                # Rimuovi tag VTT/HTML (<c>, </c>, <00:00:00.000>, ecc.)
                cleaned = re.sub(r'<[^>]+>', '', current_line)
                cleaned = cleaned.strip()
                if cleaned and cleaned != "":
                    text_lines.append(cleaned)
                i += 1
            
            if text_lines:
                # Prendi solo l'ultima riga che contiene il testo completo
                # (nei VTT automatici YouTube, le righe precedenti sono parziali)
                full_text = text_lines[-1]
                # Rimuovi spazi multipli
                full_text = re.sub(r'\s+', ' ', full_text).strip()
                if full_text:
                    items.append({
                        "start": start_seconds,
                        "text": full_text
                    })
        else:
            i += 1
    
    # Rimuovi duplicati consecutivi con lo stesso testo
    cleaned_items = []
    prev_text = ""
    for item in items:
        if item["text"] != prev_text:
            cleaned_items.append(item)
            prev_text = item["text"]
    
    return cleaned_items


def fetch_with_ytdlp(video_id: str, args) -> int:
    """Usa yt-dlp per scaricare i sottotitoli quando si usano cookies."""
    import tempfile
    
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_template = str(Path(tmpdir) / "subtitle")
        
        # Trova yt-dlp nello stesso virtual environment
        ytdlp_path = str(Path(sys.executable).parent / "yt-dlp")
        if not Path(ytdlp_path).exists():
            ytdlp_path = "yt-dlp"  # Fallback al PATH
        
        # Aggiungi Deno al PATH per risolvere le sfide JS di YouTube
        env = os.environ.copy()
        deno_bin = str(Path.home() / ".deno" / "bin")
        if deno_bin not in env.get("PATH", ""):
            env["PATH"] = f"{deno_bin}:{env.get('PATH', '')}"
        
        cmd = [
            ytdlp_path,
            "--cookies", args.cookies,
            "--write-auto-sub",
            "--sub-lang", "en",
            "--sub-format", "vtt",
            "--skip-download",
            "--sleep-requests", "2",
            "-o", output_template,
            url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        
        if result.returncode != 0:
            print(f"yt-dlp error: {result.stderr}", file=sys.stderr)
            return 1
        
        # Cerca il file VTT scaricato
        vtt_files = list(Path(tmpdir).glob("*.vtt"))
        if not vtt_files:
            print("Nessun sottotitolo trovato.", file=sys.stderr)
            return 2
        
        # Leggi il primo VTT trovato
        vtt_content = vtt_files[0].read_text(encoding="utf-8")
        items = parse_vtt_to_items(vtt_content)
        
        if args.json:
            payload = {
                "video_id": video_id,
                "language": "auto",
                "language_code": "it",
                "is_generated": True,
                "items": items,
            }
            output = json.dumps(payload, ensure_ascii=False, indent=2)
        else:
            output = build_output_text(items)
        
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(output, encoding="utf-8")
            print(f"Transcript salvato in: {output_path}")
        else:
            print(output)
        
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Estrae il transcript di un video YouTube usando youtube-transcript-api."
    )
    parser.add_argument("url_or_id", help="URL YouTube o video_id")
    parser.add_argument(
        "-l",
        "--languages",
        help="Lista di lingue preferite, separate da virgola (es. it,en).",
        default="it,en",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="File di output .txt o .json. Se omesso, stampa su stdout.",
        default=None,
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Salva/mostra il transcript in JSON invece che in testo semplice.",
    )
    parser.add_argument(
        "--proxy",
        help="Proxy HTTP/HTTPS da usare, es. http://user:pass@host:port",
        default=None,
    )
    parser.add_argument(
        "--cookies",
        help='File cookies.txt in formato Netscape (es. da "Get cookies.txt LOCALLY")',
        default=None,
    )

    args = parser.parse_args()

    try:
        video_id = extract_video_id(args.url_or_id)
        
        # Se vengono forniti i cookies, usa yt-dlp (più affidabile)
        if args.cookies:
            return fetch_with_ytdlp(video_id, args)
        
        if args.proxy:
            session = requests.Session()
            session.proxies.update({"http": args.proxy, "https": args.proxy})
            api = YouTubeTranscriptApi(http_client=session)
        else:
            api = YouTubeTranscriptApi()
        transcript_list = api.list(video_id)
        preferred_languages = [x.strip() for x in args.languages.split(",")] if args.languages else []
        transcript = None
        if preferred_languages:
            try:
                transcript = transcript_list.find_transcript(preferred_languages)
            except NoTranscriptFound:
                transcript = None
        if transcript is None:
            transcript = choose_transcript(transcript_list, None)

        if transcript is None:
            print("Nessun transcript trovato per le lingue richieste.", file=sys.stderr)
            return 2

        items = transcript.fetch()
        if args.json:
            payload = {
                "video_id": video_id,
                "language": getattr(transcript, "language", None),
                "language_code": getattr(transcript, "language_code", None),
                "is_generated": getattr(transcript, "is_generated", None),
                "items": items,
            }
            output = json.dumps(payload, ensure_ascii=False, indent=2)
        else:
            output = build_output_text(items)

        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(output, encoding="utf-8")
            print(f"Transcript salvato in: {output_path}")
        else:
            print(output)

        return 0

    except (TranscriptsDisabled, NoTranscriptFound) as exc:
        print(f"Nessun transcript disponibile: {exc}", file=sys.stderr)
        return 2
    except VideoUnavailable as exc:
        print(f"Video non disponibile: {exc}", file=sys.stderr)
        return 3
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 4
    except Exception as exc:  # pragma: no cover - best effort CLI
        print(f"Errore imprevisto: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
