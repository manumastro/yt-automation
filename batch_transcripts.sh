#!/usr/bin/env bash
# batch_transcripts.sh — Estrae transcript di più video YouTube in batch
# Uso: ./batch_transcripts.sh <output_dir> <video_url_1> [video_url_2] ...
# Oppure: cat video_urls.txt | ./batch_transcripts.sh <output_dir>
#
# Richiede: .venv attivo con extract_transcript.py funzionante

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
EXTRACT="$PROJECT_DIR/extract_transcript.py"
COOKIES="$PROJECT_DIR/cookies.txt"

if [ $# -lt 1 ]; then
    echo "Uso: $0 <output_dir> [video_url ...]"
    echo "Oppure: cat urls.txt | $0 <output_dir>"
    exit 1
fi

OUTPUT_DIR="$1"
shift
mkdir -p "$OUTPUT_DIR"

# Raccogli URL: da argomenti o da stdin
URLS=()
if [ $# -gt 0 ]; then
    URLS=("$@")
elif [ ! -t 0 ]; then
    while IFS= read -r line; do
        line="$(echo "$line" | xargs)"  # trim
        [ -n "$line" ] && [[ ! "$line" =~ ^# ]] && URLS+=("$line")
    done
fi

if [ ${#URLS[@]} -eq 0 ]; then
    echo "Nessun URL fornito."
    exit 1
fi

TOTAL=${#URLS[@]}
OK=0
FAIL=0
FAILED_URLS=()

echo "📝 Estrazione batch: $TOTAL video → $OUTPUT_DIR"
echo "=================================================="

for i in "${!URLS[@]}"; do
    URL="${URLS[$i]}"
    N=$((i + 1))

    # Estrai video ID per il filename
    VIDEO_ID=$(echo "$URL" | grep -oP '(?:v=|youtu\.be/|shorts/)([A-Za-z0-9_-]{11})' | head -1 | sed 's/.*\///' | sed 's/v=//')
    if [ -z "$VIDEO_ID" ]; then
        VIDEO_ID=$(echo "$URL" | grep -oP '[A-Za-z0-9_-]{11}' | head -1)
    fi

    OUTFILE="$OUTPUT_DIR/${VIDEO_ID}.txt"

    printf "[%d/%d] %s ... " "$N" "$TOTAL" "$VIDEO_ID"

    # Prova con cookies, poi senza
    if python3 "$EXTRACT" "$URL" --cookies "$COOKIES" -o "$OUTFILE" 2>/dev/null; then
        OK=$((OK + 1))
        SIZE=$(wc -c < "$OUTFILE")
        echo "✅ (${SIZE} bytes)"
    elif python3 "$EXTRACT" "$URL" -o "$OUTFILE" 2>/dev/null; then
        OK=$((OK + 1))
        SIZE=$(wc -c < "$OUTFILE")
        echo "✅ senza cookies (${SIZE} bytes)"
    else
        FAIL=$((FAIL + 1))
        FAILED_URLS+=("$URL")
        echo "❌ FALLITO"
        rm -f "$OUTFILE"
    fi
done

echo "=================================================="
echo "✅ Estratti: $OK/$TOTAL"
if [ $FAIL -gt 0 ]; then
    echo "❌ Falliti: $FAIL"
    for u in "${FAILED_URLS[@]}"; do
        echo "   - $u"
    done
fi
