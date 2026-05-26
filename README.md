# 🎯 yt-automation

Pipeline per trovare canali YouTube breakout, analizzarli e replicarne la formula con AI.

## Flusso operativo

```
1. SCOPERTA          2. ANALISI              3. REPLICA
find_breakout_ ───→  extract_transcript ───→  Protocolli AI (CLERK,
channels.py          .py                      NICHE BENDING, SCRIPT
                                              STEALING) — vedi
breakout.txt         transcript.txt           BUSINESS_PLAN.md §4-6
```

---

## 🔍 Step 1 — Trova canali breakout

Scansiona tutto YouTube, trova canali nuovi (< 4 mesi) con pochi video e views esplosive.

```bash
python find_breakout_channels.py -o breakout.txt
```

**Come funziona** (3 fasi, ~5 min):

| Fase | Tool | API |
|------|------|-----|
| Scoperta video virali (138 ricerche × 3 sort) | scrapetube | 0 |
| Analisi canali – 8 thread paralleli | scrapetube | 0 |
| Conferma età + iscritti (1 batch) | YouTube API | **~6 unità** |

**Output** — `breakout.txt`:
```
#01 | Melty ASMR
    https://youtube.com/@melty_asmr_love
    📊 82K iscritti | 15 video | 56M views totali
    📈 3.7M views/video | Score: 62.5/100
    📅 Creato 79 giorni fa
```

**Parametri utili:**
```bash
--max-age-days 30       # solo canali < 1 mese
--max-age-days 150      # allarga a 5 mesi
--min-subs 5000         # solo canali già grossi
--search-limit 40       # ricerca più profonda (più lento)
--extra-queries "cook,fitness"  # aggiungi topic
```

---

## 📝 Step 2 — Estrai transcript dei video del canale scelto

Dopo aver scelto un canale da `breakout.txt`, estrai i transcript per darli ai protocolli AI.

```bash
python extract_transcript.py "https://www.youtube.com/watch?v=VIDEO_ID" -o transcript.txt
```

Opzioni: `--json`, `--cookies cookies.txt`, `-l it,en`.

---

## ▶️ Step 3 — Protocolli AI

Con i transcript estratti, segui la pipeline del **BUSINESS_PLAN.md** (§4-6):

1. **CLERK** — analizza struttura script del canale → genera SOP
2. **NICHE BENDING** — trova nicchie derivate uniche
3. **SCRIPT STEALING** — genera idee + script completi

---

## 🔧 Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

API key già configurata nello script. Per cambiarla: `--api-key` o `export YOUTUBE_API_KEY=...`
