#!/usr/bin/env python3
"""
🚀 YouTube Breakout Channel Scanner v2 — No-Niche Mode
========================================================
Trova canali breakout come Next Lev: senza keyword di nicchia.
L'algoritmo di YouTube fa il lavoro sporco.

Pipeline:
  Fase 0 → Seed: API Most Popular + canali seed noti
  Fase 1 → BFS Expansion: da ogni canale virale trovo canali correlati
  Fase 2 → Analisi: video count, avg views, trend, faceless detection
  Fase 3 → Scoring: RPM geography + virality + growth trend + breakout score

Consumo API minimo:
  - Fase 0: ~3 unità (videos.list chart=mostPopular)
  - Fase 2: ~3-6 unità (batch channels.list per dettagli)
  - Tutto il resto: scrapetube (0 API)

Uso:
  python find_breakout_channels.py -o breakout.txt
  python find_breakout_channels.py --max-age-days 90 --min-subs 1000 -o breakout.txt
  python find_breakout_channels.py --seed-channels "UCxxx,UCyyy" -o breakout.txt
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import json
import time
import urllib.request
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import scrapetube
from dateutil import parser as dateutil_parser

# ─── Config ──────────────────────────────────────────────────────────
API_KEY = os.environ.get(
    "YOUTUBE_API_KEY", "AIzaSyCajbRbkAVbi9r977jkMNcrukTs6hww-JM"
)

DEFAULT_MAX_AGE_DAYS = 365
DEFAULT_MAX_VIDEOS = 80
DEFAULT_MIN_SUBS = 100
DEFAULT_MIN_AVG_VIEWS = 5_000

# Canali seed manuali — i 12 canali faceless individuati dall'utente
KNOWN_SEED_CHANNELS = [
    "UC2RkPC-fzVCAdOEwc11Eesw",  # @finestexplainerr
    "UCqXlPGw_s8Mr7YOSVZYjWOg",  # @msimplifiedx
    "UCTEcNrd4VLL673VN0Fo_M-g",  # @theinspirepath7
    "UCoZDwCMYMTz7BAYSl4Jxpfw",  # @catnectar
    "UCGuuB2pO4o0Vt-wDwUYhjtg",  # @felineeus
    "UCKHscI7mEuM5LjEVtNqd9LQ",  # @midnightoracie
    "UCcA2aJFGGbSHVuqVp23rJlw",  # @MoneyChuck
    "UCYJ5QMtzbQbahCuPCulrlhw",  # @20minuteuniversity
    "UCv4Wnct9tQkgqNyQdhEYY3Q",  # @pathohubb
    "UCsUwLHyw-5OpRRg4QEjUwrw",  # @The-Brainster
    "UCYvXwKfLAXuo2NFhpoLkKmg",  # @explaineur
    "UCGxfwkwyrpiMOnQhM8MxqwA",  # @asknigel
]

# Paesi Tier-1 per RPM (advertisers pagano di più)
TIER1_COUNTRIES = {
    "US", "GB", "CA", "AU", "DE", "FR", "JP", "KR", "NL", "SE",
    "NO", "DK", "FI", "CH", "NZ", "IE", "SG", "HK", "LU", "AE",
}

# Parole che suggeriscono pubblico USA/UK nei titoli
US_UK_TITLE_SIGNALS = [
    "america", "united states", "usa ", "us ", "uk ", "britain",
    "england", "london", "washington", "california", "texas",
    "florida", "new york", "chicago", "tornado", "hurricane",
    "midwest", "mid-west", "appalachia", "tornadoes",
    "american", "canadian", "australian", "british",
    "missouri", "alabama", "oklahoma", "kansas",
]

# ─── Faceless detection ──────────────────────────────────────────────
FACELESS_POSITIVE_KEYWORDS = [
    "animat", "voiceover", "voice over", "voice-over", "narrat",
    "explain", "fact", "documentary", "document",
    "ai generat", "ai tool", "ai technolog", "ai visual",
    "text to speech", "tts", "faceless", "no face", "no-face",
    "recap", "breakdown", "compil",
    "restor", "asmr", "satisfy", "ambient",
    "lofi", "lo-fi", "synthwave", "sleep", "relax", "meditat",
    "stori", "myster", "psycholog", "scienc",
    "histor", "mytholog", "crime", "cold case",
    "engineer", "how it's made", "megaproject",
    "civiliz", "empire", "ancient", "geopolitic",
    "recreat", "visual",
    "motion graphic", "infographic", "whiteboard",
    "stock footage", "b-roll", "3d", "low poly",
    "cinematic", "timelapse", "time lapse", "time-lapse",
    "top 10", "top 5", "comparison", "vs ",
]

FACELESS_NEGATIVE_KEYWORDS = [
    "vlog", "grwm", "get ready with me",
    "unboxing haul", "mukbang", "day in my life",
    "storytime", "q&a", "meet my", "family vlog",
    "podcast", "interview", "live stream",
    "face reveal", "my face", "camera",
]


def faceless_score(name: str, description: str, titles: list[str]) -> int:
    """Stima faceless 0-100."""
    text = f"{name} {description} {' '.join(titles)}".lower()
    score = 0
    matched_pos = 0
    for kw in FACELESS_POSITIVE_KEYWORDS:
        if kw in text:
            score += 5
            matched_pos += 1
    for kw in FACELESS_NEGATIVE_KEYWORDS:
        if kw in text:
            score -= 20
    faceless_title_patterns = [
        "explained", "the truth", "you didn't know", "you don't know",
        "what if", "how ", "why ", "the rise", "the fall",
        "the entire", "the real", "the history", "the story",
        "top ", "facts about", " vs ", "comparison",
        "recap", "breakdown", "full story",
        "in minutes", "in 10", "in 20", "in 30",
    ]
    title_text = " ".join(titles).lower()
    for pat in faceless_title_patterns:
        if pat in title_text:
            score += 3
    if matched_pos >= 3:
        score += 10
    return max(0, min(100, score))


# ─── Helpers ─────────────────────────────────────────────────────────
def fmt(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def parse_view_count(text: str) -> int:
    if not text:
        return 0
    text = text.lower().replace(",", "").replace("views", "").strip()
    text = text.replace("\xa0", "")
    try:
        if "m" in text:
            return int(float(text.replace("m", "")) * 1_000_000)
        if "k" in text:
            return int(float(text.replace("k", "")) * 1_000)
        if "b" in text:
            return int(float(text.replace("b", "")) * 1_000_000_000)
        return int(float(text))
    except ValueError:
        return 0


def extract_channel_from_video(v: dict) -> tuple[str, str]:
    runs = v.get("ownerText", {}).get("runs", [{}])
    if not runs:
        runs = v.get("shortBylineText", {}).get("runs", [{}])
    ch_name = runs[0].get("text", "") if runs else ""
    ch_id = (
        runs[0]
        .get("navigationEndpoint", {})
        .get("browseEndpoint", {})
        .get("browseId", "")
        if runs
        else ""
    )
    return ch_id, ch_name


def extract_title(v: dict) -> str:
    runs = v.get("title", {}).get("runs", [{}])
    return runs[0].get("text", "") if runs else v.get("title", {}).get("simpleText", "")


def calc_trend(views_list: list[int]) -> str:
    """
    Analizza trend delle views in ordine cronologico (vecchio → nuovo).
    Ritorna: 'up', 'stable', 'down'
    """
    if len(views_list) < 3:
        return "stable"
    # Dividi in prima e seconda metà
    mid = len(views_list) // 2
    first_half = views_list[:mid]
    second_half = views_list[mid:]

    avg_first = sum(first_half) / len(first_half)
    avg_second = sum(second_half) / len(second_half)

    if avg_first == 0:
        return "stable"

    ratio = avg_second / avg_first
    if ratio >= 1.3:
        return "up"
    elif ratio <= 0.5:
        return "down"
    return "stable"


def estimate_rpm(country: str, titles: list[str]) -> float:
    """
    Stima RPM (Revenue Per Mille views) basata su:
    - Paese del canale (Tier-1 vs altri)
    - Segnali di pubblico USA/UK nei titoli
    """
    base_rpm = 1.5  # Baseline globale

    if country in TIER1_COUNTRIES:
        base_rpm = 4.0

    # Controlla titoli per segnali geografici USA/UK
    title_text = " ".join(titles).lower()
    us_signals = sum(1 for sig in US_UK_TITLE_SIGNALS if sig in title_text)
    if us_signals >= 2:
        base_rpm = max(base_rpm, 5.0)  # Pubblico prevalentemente US → RPM alto
    elif us_signals >= 1:
        base_rpm = max(base_rpm, 3.5)

    return round(base_rpm, 1)


# ─── Data ────────────────────────────────────────────────────────────
@dataclass
class Channel:
    channel_id: str
    name: str = ""
    handle: str = ""
    subs: int = 0
    video_count: int = 0
    total_views: int = 0
    created_at: Optional[datetime] = None
    age_days: int = 0
    description: str = ""
    country: str = ""
    score: float = 0.0
    breakout_score: float = 0.0
    avg_views: float = 0.0
    faceless: int = 0
    sample_videos: list = field(default_factory=list)
    all_video_views: list = field(default_factory=list)  # Views in ordine cronologico
    trend: str = "stable"
    has_viral: bool = False
    max_views_single: int = 0
    estimated_rpm: float = 0.0
    estimated_monthly_revenue: float = 0.0
    source: str = ""  # Tracciamento provenienza (seed o BFS)

    def calc_metrics(self):
        """Calcola tutte le metriche derivate."""
        if self.video_count > 0:
            self.avg_views = self.total_views / self.video_count

        # Trend
        if len(self.all_video_views) >= 3:
            self.trend = calc_trend(self.all_video_views)

        # Virality check
        self.max_views_single = max(self.all_video_views) if self.all_video_views else 0
        self.has_viral = self.max_views_single >= 500_000

        # RPM estimation
        titles = [v.get("title", "") for v in self.sample_videos]
        self.estimated_rpm = estimate_rpm(self.country, titles)

        # Revenue stima mensile
        if self.total_views > 0 and self.age_days > 0:
            daily_views = self.total_views / self.age_days
            monthly_views = daily_views * 30
            self.estimated_monthly_revenue = round(monthly_views / 1000 * self.estimated_rpm, 0)

    def calc_breakout_score(self, cfg: dict) -> float:
        """
        Breakout Score 0-100 — ispirato a Next Lev.
        Peso: canali con poche subs, tante views, crescita rapida, RPM alto.
        """
        s = 0.0

        # 1. Sub-to-view ratio (MAX 25pt) — Il segnale #1 di Next Lev
        # Poche subs + tante views = nicchia aperta
        if self.subs > 0 and self.total_views > 0:
            ratio = self.total_views / self.subs
            # 50:1 = ottimo, 20:1 = buono, 5:1 = normale
            s += min(ratio / 50, 1.0) * 25

        # 2. Avg views per video (MAX 20pt)
        if self.avg_views > 0:
            s += min(self.avg_views / 200_000, 1.0) * 20

        # 3. Growth velocity — subs per giorno (MAX 15pt)
        if self.age_days > 0:
            subs_per_day = self.subs / self.age_days
            s += min(subs_per_day / 500, 1.0) * 15

        # 4. Trend direction (MAX 10pt)
        if self.trend == "up":
            s += 10
        elif self.trend == "stable":
            s += 5

        # 5. Virality bonus (MAX 10pt) — come il video: 800K+ = virale
        if self.has_viral:
            s += 10
        elif self.max_views_single >= 100_000:
            s += 5

        # 6. RPM tier (MAX 10pt) — geografia del pubblico
        s += min(self.estimated_rpm / 6, 1.0) * 10

        # 7. Fewer videos = more breakout (MAX 10pt)
        if self.video_count > 0:
            s += max(0, 1 - self.video_count / 40) * 10

        # BONUS: Faceless replicability (MAX 5pt extra, sopra 100)
        bonus = min(self.faceless / 100, 1.0) * 5

        self.score = round(s, 1)
        self.breakout_score = round(s + bonus, 1)
        return self.breakout_score


# ─── FASE 0: Seed — Most Popular API + canali seed ───────────────────
def phase0_seed(api_key: str, region_codes: list[str], seed_channels: list[str]) -> dict[str, str]:
    """
    Costruisce il pool iniziale di canali da cui partire.

    1. 12 canali seed dell'utente → info API + video virali
    2. Categorie derivate dai seed → query mirate per canali simili
       - "Every X Explained" (Brainster, Explaineur, Ask Nigel, PathoHub)
       - Medical/Health (PathoHub)
       - Finance/Money (Money Chuck, M Simplified)
       - Cats/Animals (CatNectar, Felinee)
       - Mystery/Spiritual (Midnight Oracle, Inspire Path)
    3. Video virali → BFS expansion (2 livelli)

    Ritorna: (all_channels, vids_for_bfs)
    """
    print("🌱 Fase 0: Seed + categorie derivate dai seed...", file=sys.stderr)

    all_channels = {}
    vids_for_bfs = []
    api_calls = 0

    # API call per info canali seed
    for cid in seed_channels:
        try:
            url = (
                f"https://www.googleapis.com/youtube/v3/channels"
                f"?part=snippet,statistics,brandingSettings"
                f"&id={cid}&key={api_key}"
            )
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())
            api_calls += 1

            items = data.get("items", [])
            if not items:
                continue

            item = items[0]
            sn = item["snippet"]
            st = item["statistics"]
            subs = int(st.get("subscriberCount", 0))

            all_channels[cid] = {
                "name": sn.get("title", ""),
                "description": (sn.get("description") or "")[:500],
                "country": item.get("brandingSettings", {}).get("channel", {}).get("country", ""),
                "handle": sn.get("customUrl", ""),
                "subs": subs,
                "total_views": int(st.get("viewCount", 0)),
                "video_count": int(st.get("videoCount", 0)),
                "source": f"seed|{sn.get('title', '')}",
                "videos": [],
            }
            print(f"  ✅ {sn.get('title', '')} ({fmt(subs)} subs, {st.get('videoCount', '?')} video)", file=sys.stderr)
        except Exception as e:
            print(f"  ⚠️ Errore seed {cid}: {e}", file=sys.stderr)

    # 1c) Categorie derivate dai 12 seed channels dell'utente
    #     Analizzando i format dei seed, emergono queste 5 categorie:
    #     - "Every X Explained" (Brainster, Explaineur, Ask Nigel, PathoHub)
    #     - Medical/Health (PathoHub)
    #     - Finance/Money (Money Chuck, M Simplified)
    #     - Cats/Animals (CatNectar, Felinee)
    #     - Mystery/Spiritual (Midnight Oracle, Inspire Path)
    CATEGORY_QUERIES = [
        "every explained in minutes",
        "disease explained",
        "money explained",
        "cat facts animated",
        "mystery explained",
    ]
    print("  🔍 Categorie dai seed channels (scrapetube, 0 API)...", file=sys.stderr)
    for q in CATEGORY_QUERIES:
        try:
            results = list(scrapetube.get_search(q, limit=25, sort_by="relevance"))
            found = 0
            for r in results:
                vid_id = r.get("videoId", "")
                if not vid_id:
                    continue
                views = parse_view_count(r.get("viewCountText", {}).get("simpleText", ""))
                title = extract_title(r)
                pub = r.get("publishedTimeText", {}).get("simpleText", "")
                ch_id, ch_name = extract_channel_from_video(r)
                if not ch_id or ch_id in all_channels:
                    continue

                all_channels[ch_id] = {
                    "name": ch_name,
                    "description": "",
                    "country": "",
                    "handle": "",
                    "subs": 0,
                    "total_views": 0,
                    "video_count": 0,
                    "source": f"category|{q}",
                    "videos": [{"id": vid_id, "title": title, "views": views, "pub": pub}],
                }
                if views >= 100_000:
                    vids_for_bfs.append({"id": vid_id, "title": title, "views": views, "channel_id": ch_id, "seed_origin": f"cat:{q}"})
                found += 1
                if found >= 20:
                    break
            time.sleep(1)
            print(f"  ✅ '{q}' → +{found} canali", file=sys.stderr)
        except Exception as e:
            print(f"  ⚠️ '{q}': {e}", file=sys.stderr)
    for cid in list(all_channels.keys()):
        # Solo i seed originali hanno i video da raccogliere via scrapetube
        # I canali dalle categorie hanno già 1 video dalla search
        if not all_channels[cid]["source"].startswith("seed|"):
            continue
        try:
            vids = list(scrapetube.get_channel(cid, limit=15, sleep=0))
            for v in vids[:15]:
                vid_id = v.get("videoId", "")
                if not vid_id:
                    continue
                views = parse_view_count(v.get("viewCountText", {}).get("simpleText", ""))
                title = extract_title(v)
                pub = v.get("publishedTimeText", {}).get("simpleText", "")
                all_channels[cid]["videos"].append({
                    "id": vid_id, "title": title, "views": views, "pub": pub,
                })
                # Video con 100K+ views → BFS seed (propaga il nome del seed per tracking)
                if views >= 100_000:
                    vids_for_bfs.append({"id": vid_id, "title": title, "views": views, "channel_id": cid, "seed_origin": sn.get("title", cid)})
            time.sleep(1)
        except Exception as e:
            print(f"  ⚠️ Errore scrapetube {cid}: {e}", file=sys.stderr)

    seed_count = sum(1 for c in all_channels.values() if c["source"].startswith("seed|"))
    cat_count = sum(1 for c in all_channels.values() if c["source"].startswith("category|"))
    print(f"\n  💰 API usate Fase 0: ~{api_calls} (solo channels.list)")
    print(f"  ✅ {len(all_channels)} canali totali ({seed_count} seed + {cat_count} categorie) → {len(vids_for_bfs)} video virali per BFS\n", file=sys.stderr)

    return all_channels, vids_for_bfs


# ─── FASE 1: BFS Expansion — "Allena l'algoritmo" ────────────────────
def phase1_bfs(
    viral_videos: list[dict],
    max_bfs_expansion: int,
    max_months: int,
) -> dict[str, dict]:
    """
    Per ogni video virale dai seed channels, cerca il titolo su scrapetube.
    YouTube nei risultati mostra canali SIMILI → espansione algorithmica.
    Questo è l'equivalente automatizzato di: "guarda faceless → YouTube ti mostra più faceless".

    Dopo il primo livello, BFS di livello 2:
    dai canali trovati con >100K views, ripeti l'espansione.
    """
    print(f"🔍 Fase 1: BFS Expansion ({len(viral_videos)} video virali seed, max {max_bfs_expansion} espansioni per livello)...", file=sys.stderr)

    all_channels: dict[str, dict] = {}
    seen_vids: set[str] = set()

    def _expand(videos_to_expand: list[dict], label: str) -> list[dict]:
        """Un livello di BFS. Ritorna nuovi video virali per il livello successivo."""
        expanded = 0
        new_viral_vids = []

        for i, video in enumerate(videos_to_expand):
            vid_title = video.get("title", "")
            if len(vid_title) < 10:
                continue

            try:
                results = list(scrapetube.get_search(vid_title[:100], limit=25, sort_by="view_count"))
            except Exception:
                continue

            for r in results:
                vid_id = r.get("videoId", "")
                if not vid_id or vid_id in seen_vids:
                    continue
                seen_vids.add(vid_id)

                pub = r.get("publishedTimeText", {}).get("simpleText", "")
                # Filtro: video recenti
                t = pub.lower()
                is_recent = any(w in t for w in ["hour", "day", "week"])
                if "month" in t:
                    m = re.search(r"(\d+)\s*month", t)
                    if m and int(m.group(1)) <= max_months:
                        is_recent = True

                if not is_recent:
                    continue

                views = parse_view_count(r.get("viewCountText", {}).get("simpleText", ""))
                if views < 25_000:
                    continue

                ch_id, ch_name = extract_channel_from_video(r)
                if not ch_id:
                    continue

                title = extract_title(r)

                if ch_id not in all_channels:
                    # Per L2: seed_origin viene dal video dict, altrimenti dal channel_id
                    seed_origin = video.get("seed_origin", video.get("channel_id", "?"))
                    all_channels[ch_id] = {
                        "name": ch_name,
                        "videos": [],
                        "source": f"{label}|{seed_origin}",
                    }
                # Se il canale esiste già (es. è un seed), NON sovrascrivere il source

                all_channels[ch_id]["videos"].append({
                    "id": vid_id, "title": title, "views": views, "pub": pub,
                })

                # Se questo video è virale → candidato per BFS livello 2
                if views >= 100_000:
                    # Propaga il seed originale per il tracking
                    seed_origin = video.get("channel_id", "?")
                    new_viral_vids.append({"id": vid_id, "title": title, "views": views, "channel_id": ch_id, "seed_origin": seed_origin})

            expanded += 1
            if expanded % 10 == 0:
                print(f"  [{label}] [{expanded}/{len(videos_to_expand)}] canali: {len(all_channels)}", file=sys.stderr)

        print(f"  ✅ {label}: {len(all_channels)} canali, {len(new_viral_vids)} nuovi video virali", file=sys.stderr)
        return new_viral_vids

    # Livello 1: dai video dei seed channels
    viral_videos.sort(key=lambda v: v.get("views", 0), reverse=True)
    level1_vids = viral_videos[:max_bfs_expansion]
    new_viral = _expand(level1_vids, "BFS-L1")

    # Livello 2: dai video virali trovati al livello 1
    if new_viral:
        level2_vids = sorted(new_viral, key=lambda v: v.get("views", 0), reverse=True)[:max_bfs_expansion]
        _expand(level2_vids, "BFS-L2")

    print(f"  ✅ BFS totale: {len(all_channels)} canali unici\n", file=sys.stderr)
    return all_channels


# ─── FASE 2: Analisi canali ──────────────────────────────────────────
def phase2_analyze(
    channels: dict[str, dict],
    max_videos: int,
) -> dict[str, dict]:
    """
    Per ogni canale scoperto: conta video, raccoglie TUTTE le views in ordine cronologico.
    Skip se video_count > max_videos.
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    print(f"📊 Fase 2: Analisi {len(channels)} canali (scrapetube)...", file=sys.stderr)
    limit = max_videos + 1
    passed: dict[str, dict] = {}
    done = 0
    total = len(channels)

    def _check_channel(item):
        cid, info = item
        import threading
        result = [None]
        error = [None]

        def _fetch():
            try:
                result[0] = list(scrapetube.get_channel(cid, limit=limit, sleep=0))
            except Exception as e:
                error[0] = e

        t = threading.Thread(target=_fetch, daemon=True)
        t.start()
        t.join(timeout=20)  # 20s timeout per canale
        if t.is_alive() or error[0] is not None:
            return None
        vids = result[0]
        if vids is None:
            return None
        if len(vids) >= limit:
            return None

        # Raccogli tutte le views in ordine cronologico (scrapetube dà dal più recente al più vecchio)
        all_views_reversed = []
        total_views = 0
        samples = []
        for v in vids:
            vc = parse_view_count(v.get("viewCountText", {}).get("simpleText", ""))
            total_views += vc
            all_views_reversed.append(vc)
            if len(samples) < 5:
                samples.append({
                    "id": v.get("videoId", ""),
                    "title": extract_title(v),
                    "views": vc,
                    "pub": v.get("publishedTimeText", {}).get("simpleText", ""),
                })

        # Inverti per avere ordine cronologico (vecchio → nuovo) per il trend
        all_views_chrono = list(reversed(all_views_reversed))

        info["video_count"] = len(vids)
        info["total_views"] = total_views
        info["samples"] = samples
        info["all_video_views"] = all_views_chrono
        return (cid, info)

    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(_check_channel, item): item for item in channels.items()}
        for fut in as_completed(futures):
            done += 1
            if done % 20 == 0 or done == total:
                print(f"  [{done}/{total}] passati: {len(passed)}", file=sys.stderr)
            result = fut.result()
            if result:
                passed[result[0]] = result[1]

    print(f"  ✅ {len(passed)} canali con ≤{max_videos} video\n", file=sys.stderr)
    return passed


# ─── FASE 3: Dettagli API + Scoring ──────────────────────────────────
def phase3_scoring(channels: dict[str, dict], api_key: str, cfg: dict) -> list[Channel]:
    """
    Batch API per iscritti + data creazione + country.
    Poi calcola breakout score completo.
    """
    from googleapiclient.discovery import build

    ids = list(channels.keys())
    if not ids:
        return []

    print(f"🔑 Fase 3: Dettagli API per {len(ids)} canali...", file=sys.stderr)

    yt = build("youtube", "v3", developerKey=api_key)
    cutoff = datetime.now(timezone.utc) - timedelta(days=cfg["max_age_days"])
    result: list[Channel] = []
    skip_old = 0
    skip_subs = 0

    for i in range(0, len(ids), 50):
        batch = ids[i : i + 50]
        try:
            r = yt.channels().list(
                part="snippet,statistics,brandingSettings",
                id=",".join(batch)
            ).execute()
        except Exception as e:
            print(f"  ⚠️ Errore API: {e}", file=sys.stderr)
            continue

        for item in r.get("items", []):
            cid = item["id"]
            sn = item["snippet"]
            st = item["statistics"]
            branding = item.get("brandingSettings", {}).get("channel", {})

            try:
                created = dateutil_parser.parse(sn["publishedAt"])
                if created.tzinfo is None:
                    created = created.replace(tzinfo=timezone.utc)
            except Exception:
                continue

            if created < cutoff:
                skip_old += 1
                continue

            subs = int(st.get("subscriberCount", 0))
            if st.get("hiddenSubscriberCount"):
                subs = 0
            if subs < cfg["min_subs"]:
                skip_subs += 1
                continue

            age_days = (datetime.now(timezone.utc) - created).days
            info = channels.get(cid, {})

            ch = Channel(
                channel_id=cid,
                name=sn.get("title", info.get("name", "")),
                handle=sn.get("customUrl", ""),
                subs=subs,
                video_count=info.get("video_count", int(st.get("videoCount", 0))),
                total_views=info.get("total_views", int(st.get("viewCount", 0))),
                created_at=created,
                age_days=age_days,
                description=(sn.get("description") or "")[:500].replace("\n", " "),
                country=branding.get("country", ""),
                sample_videos=info.get("samples", [])[:5],
                all_video_views=info.get("all_video_views", []),
                source=info.get("source", "unknown"),
            )
            ch.calc_metrics()
            ch.calc_breakout_score(cfg)

            # Faceless score
            titles = [v.get("title", "") for v in ch.sample_videos]
            ch.faceless = faceless_score(ch.name, ch.description, titles)

            result.append(ch)

    # Ordina: breakout_score desc (puro, senza priorità faceless)
    result.sort(key=lambda c: c.breakout_score, reverse=True)

    # Post-filtri: skip India + min $100/mese
    skip_india = sum(1 for c in result if c.country == "IN")
    skip_low_income = sum(1 for c in result if c.country != "IN" and c.estimated_monthly_revenue < 100)
    result = [
        c for c in result
        if c.country != "IN"
        and c.estimated_monthly_revenue >= 100
    ]

    units = (len(ids) // 50 + 1) * 3
    print(f"  ✅ {len(result)} canali breakout confermati (API: ~{units} unità)")
    print(f"  ❌ Scartati: {skip_old} troppo vecchi | {skip_subs} pochi iscritti | {skip_india} India 🇮🇳 | {skip_low_income} income <$100/m\n", file=sys.stderr)
    return result


# ─── Output ──────────────────────────────────────────────────────────
def write_json(channels: list[Channel], path: str):
    """Output JSON per analisi successiva."""
    data = []
    for ch in channels:
        data.append({
            "channel_id": ch.channel_id,
            "name": ch.name,
            "handle": ch.handle,
            "url": f"https://youtube.com/{ch.handle}" if ch.handle else f"https://youtube.com/channel/{ch.channel_id}",
            "subs": ch.subs,
            "video_count": ch.video_count,
            "total_views": ch.total_views,
            "avg_views": int(ch.avg_views),
            "max_views_single": ch.max_views_single,
            "has_viral": ch.has_viral,
            "created_at": ch.created_at.isoformat() if ch.created_at else None,
            "age_days": ch.age_days,
            "country": ch.country,
            "trend": ch.trend,
            "faceless_score": ch.faceless,
            "breakout_score": ch.breakout_score,
            "estimated_rpm": ch.estimated_rpm,
            "estimated_monthly_revenue": ch.estimated_monthly_revenue,
            "description": ch.description[:200],
            "source": ch.source,  # Track provenienza
            "sample_videos": ch.sample_videos[:5],
        })
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"📄 JSON: {path}", file=sys.stderr)


def write_txt(channels: list[Channel], path: str):
    lines = []
    faceless_count = sum(1 for c in channels if c.faceless >= 15)
    viral_count = sum(1 for c in channels if c.has_viral)
    lines.append(
        f"🚀 YOUTUBE BREAKOUT CHANNELS — {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    lines.append("   No-Niche Mode — Scoperti algorithmicamente come Next Lev")
    lines.append(f"   Totale: {len(channels)} | Faceless: {faceless_count} | Virali: {viral_count}")
    lines.append("=" * 90)
    lines.append("")

    # Tabella comparativa (stile Google Sheet del video)
    lines.append("📊 COMPARISON TABLE")
    lines.append(f"{'#':<4} {'Channel':<28} {'Subs':>7} {'Videos':>6} {'Avg Views':>9} {'Max':>7} {'RPM':>5} {'$/mo':>8} {'Trend':>6} {'Score':>6}")
    lines.append("-" * 90)

    for i, ch in enumerate(channels[:30], 1):
        trend_arrow = {"up": "📈", "stable": "➡️", "down": "📉"}[ch.trend]
        lines.append(
            f"{i:<4} {ch.name[:27]:<28} {fmt(ch.subs):>7} {ch.video_count:>6} "
            f"{fmt(int(ch.avg_views)):>9} {fmt(ch.max_views_single):>7} "
            f"${ch.estimated_rpm:<4} ${fmt(int(ch.estimated_monthly_revenue)):>7} "
            f"{trend_arrow} {ch.breakout_score:>6.0f}"
        )

    lines.append("")
    lines.append("=" * 90)
    lines.append("")

    # Detail section
    for i, ch in enumerate(channels[:30], 1):
        url = f"https://youtube.com/{ch.handle}" if ch.handle else f"https://youtube.com/channel/{ch.channel_id}"
        trend_emoji = {"up": "📈", "stable": "➡️", "down": "📉"}[ch.trend]

        lines.append(f"#{i:02d} | {ch.name}")
        lines.append(f"    {url}")
        lines.append(
            f"    📊 {fmt(ch.subs)} iscritti | {ch.video_count} video | "
            f"{fmt(ch.total_views)} views totali"
        )
        lines.append(f"    📈 {fmt(int(ch.avg_views))} avg/video | "
                      f"Max: {fmt(ch.max_views_single)} | "
                      f"Virale: {'✅' if ch.has_viral else '❌'}")
        lines.append(f"    💰 RPM stimato: ${ch.estimated_rpm} | "
                      f"Revenue stimata: ${fmt(int(ch.estimated_monthly_revenue))}/mese")
        lines.append(f"    {trend_emoji} Trend: {ch.trend.upper()}")
        lines.append(f"    ⭐ Breakout Score: {ch.breakout_score}/100")
        # Tag faceless
        if ch.faceless >= 40:
            lines.append(f"    🤖 FACELESS (score: {ch.faceless})")
        elif ch.faceless >= 15:
            lines.append(f"    🤖 Probabilmente faceless (score: {ch.faceless})")
        # Country
        if ch.country:
            rpm_badge = "🔥 Tier-1" if ch.country in TIER1_COUNTRIES else ""
            lines.append(f"    🌍 {ch.country} {rpm_badge}")
        lines.append(f"    📅 Creato {ch.age_days} giorni fa ({ch.created_at.strftime('%Y-%m-%d') if ch.created_at else '?'})")
        # Trend per video
        if ch.all_video_views:
            trend_str = " → ".join(fmt(v) for v in ch.all_video_views[-6:])  # ultimi 6
            lines.append(f"    📉 Trend views: {trend_str}")
        if ch.description:
            lines.append(f"    📝 {ch.description[:150]}...")
        if ch.sample_videos:
            for v in ch.sample_videos[:3]:
                vw = fmt(v["views"]) if v.get("views") else "?"
                lines.append(f"    🎬 {v['title'][:65]} ({vw} views)")
        lines.append("")

    Path(path).write_text("\n".join(lines), encoding="utf-8")
    print(f"💾 TXT: {path}", file=sys.stderr)


# ─── Main ────────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(
        description="🚀 YouTube Breakout Channel Scanner v2 — No-Niche Mode (Next Lev style)"
    )
    p.add_argument("-o", "--output", default="breakout.txt", help="File output .txt")
    p.add_argument("--json", help="Salva anche output JSON")
    p.add_argument(
        "--max-age-days", type=int, default=DEFAULT_MAX_AGE_DAYS,
        help=f"Età max canale in giorni (default: {DEFAULT_MAX_AGE_DAYS})"
    )
    p.add_argument(
        "--max-videos", type=int, default=DEFAULT_MAX_VIDEOS,
        help=f"Max video del canale (default: {DEFAULT_MAX_VIDEOS})"
    )
    p.add_argument(
        "--min-subs", type=int, default=DEFAULT_MIN_SUBS,
        help=f"Min iscritti (default: {DEFAULT_MIN_SUBS})"
    )
    p.add_argument(
        "--min-avg-views", type=int, default=DEFAULT_MIN_AVG_VIEWS,
        help=f"Min avg views per video (default: {DEFAULT_MIN_AVG_VIEWS})"
    )
    p.add_argument("--api-key", default=API_KEY, help="YouTube API key")
    p.add_argument(
        "--regions", default="US",
        help="Regioni (legacy, non più usato - solo compatibilità)"
    )
    p.add_argument(
        "--seed-channels", default="",
        help="Canali seed extra (comma-separated channel IDs)"
    )
    p.add_argument(
        "--max-bfs", type=int, default=50,
        help="Max espansioni BFS (default: 50)"
    )

    args = p.parse_args()

    cfg = {
        "max_age_days": args.max_age_days,
        "max_videos": args.max_videos,
        "min_subs": args.min_subs,
        "min_avg_views": args.min_avg_views,
    }

    # Setup seed channels
    seed_channels = list(KNOWN_SEED_CHANNELS)
    if args.seed_channels:
        seed_channels.extend([c.strip() for c in args.seed_channels.split(",") if c.strip()])

    print("🚀 YouTube Breakout Channel Scanner v2 — Seed + Categorie", file=sys.stderr)
    print(f"   {len(seed_channels)} seed + 5 categorie derivate → BFS → breakout", file=sys.stderr)
    print("─" * 60, file=sys.stderr)
    print(f"  Max età: {cfg['max_age_days']}gg | Max video: {cfg['max_videos']}", file=sys.stderr)
    print(f"  Min iscritti: {fmt(cfg['min_subs'])} | Min avg views: {fmt(cfg['min_avg_views'])}", file=sys.stderr)
    print(f"  BFS expansion: {args.max_bfs} per livello (2 livelli)", file=sys.stderr)
    print("─" * 60 + "\n", file=sys.stderr)

    regions = [r.strip() for r in args.regions.split(",") if r.strip()]

    # ═══ FASE 0: Seed ═══
    seed_pool, viral_vids = phase0_seed(args.api_key, regions, seed_channels)

    # ═══ FASE 1: BFS Expansion ═══
    bfs_channels = phase1_bfs(viral_vids, args.max_bfs, (cfg['max_age_days'] // 30) + 1)

    # ═══ FASE 2: Analisi ═══
    analyzed = phase2_analyze(bfs_channels, cfg['max_videos'])

    # Pre-filtro: avg views
    promising = {}
    for cid, info in analyzed.items():
        vc = info.get("video_count", 0)
        tv = info.get("total_views", 0)
        if vc > 0:
            avg = tv / vc
            if avg >= cfg['min_avg_views'] * 0.3:  # Soglia leggermente più bassa per non perdere
                promising[cid] = info
    print(f"🎯 Pre-filtro avg views: {len(promising)}/{len(analyzed)} canali\n", file=sys.stderr)

    if not promising:
        print("⚠️ Nessun canale superato i filtri.", file=sys.stderr)
        return

    # ═══ FASE 3: Scoring ═══
    breakout = phase3_scoring(promising, args.api_key, cfg)

    # Post-filtro: min avg views stretto
    breakout = [ch for ch in breakout if ch.avg_views >= cfg['min_avg_views']]

    # ═══ Output ═══
    if breakout:
        print(f"✅ Trovati {len(breakout)} canali breakout!\n", file=sys.stderr)
        for i, ch in enumerate(breakout[:15], 1):
            fl = " 🤖" if ch.faceless >= 15 else ""
            trend_e = {"up": "📈", "stable": "➡️", "down": "📉"}[ch.trend]
            vir = "🔥" if ch.has_viral else ""
            print(
                f"  #{i:02d} {ch.name:<30} {fmt(ch.subs):>7} sub | "
                f"{ch.video_count:>2} vid | avg {fmt(int(ch.avg_views)):>6} | "
                f"${ch.estimated_rpm:<4}rpm | Score {ch.breakout_score:>5.0f} "
                f"{trend_e}{vir}{fl}",
                file=sys.stderr,
            )
    else:
        print("⚠️ Nessun canale breakout trovato. Prova filtri meno restrittivi.", file=sys.stderr)

    write_txt(breakout, args.output)
    if args.json:
        write_json(breakout, args.json)


if __name__ == "__main__":
    main()