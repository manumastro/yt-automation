# 🎯 yt-automation — Protocolli + Discovery Canali

## Scopo
Queste istruzioni sono **globali** e si concentrano solo su:
1. protocolli AI del progetto
2. script/workflow di discovery canali YouTube

## Riferimento strategico obbligatorio
- `BUSINESS_PLAN.md` (sezione: **I 5 Protocolli AI (Tutti)**)

## Protocolli (allineamento 1:1 con BUSINESS_PLAN)

| Protocollo | Stato skill nel progetto | Attivazione |
|---|---|---|
| **CLERK** | ✅ Disponibile | `/skill:clerk` |
| **NICHE BENDING** | ✅ Disponibile | `/skill:niche-bending` |
| **SCRIPT STEALING** | ✅ Disponibile | `/skill:script-stealing` |
| **AI NEWS** | ✅ Disponibile | `/skill:ai-news` |
| **POET** | ✅ Disponibile | `/skill:poet` |
| **PRODUCTION PACK** | ✅ Disponibile | `/skill:production-pack` |

### Skills realmente presenti
- `.pi/skills/clerk/SKILL.md`
- `.pi/skills/niche-bending/SKILL.md`
- `.pi/skills/script-stealing/SKILL.md`
- `.pi/skills/ai-news/SKILL.md`
- `.pi/skills/poet/SKILL.md`
- `.pi/skills/production-pack/SKILL.md`

## Script discovery canali

### Regola base
Prima di ogni script Python:
```bash
source .venv/bin/activate
```

### 1) Scanner breakout (principale)
Script: `find_breakout_channels.py`

Esempi:
```bash
python find_breakout_channels.py -o breakout.txt
python find_breakout_channels.py --max-age-days 60 --min-subs 1000 -o breakout.txt
```

Input opzionale nicchie:
- `niches.txt`

Output principale:
- `breakout.txt`

### 2) Validazione rapida canali (browser)
Usa `browser` per controllare i candidati:
- tab video
- ordine per popolarità
- coerenza format
- segnali di posting consistency

## Script TTS Google (production pack)

Script template:
- `scripts/generate_google_tts_from_production_pack.py`

Regola base (sempre):
```bash
source .venv/bin/activate
```

Template uso per qualsiasi video (Gemini TTS):
```bash
python scripts/generate_google_tts_from_production_pack.py \
  --pack output/<canale>/production/<data_slug>/production_pack_it.md \
  --output-dir output/<canale>/production/<data_slug>/tts_gemini_sceneXX_plus \
  --start-scene 4 \
  --backend gemini \
  --api-key-env GEMINI_API_KEY
```

Note:
- Backend `gemini` segue il formato originale (`gemini-3.1-flash-tts-preview`, voice `Sadachbia`).
- Serve API key abilitata a `generativelanguage.googleapis.com`.
- Quota tipica: 10 richieste/min sul modello TTS, quindi conviene batch da 8–10 scene.
- Backend `cloud` resta disponibile come fallback (`texttospeech.googleapis.com`).

## Workflow globale: Discovery → Protocols

1. **Discovery batch**
   - Esegui `find_breakout_channels.py`
   - Crea shortlist candidati da `breakout.txt`

2. **Validazione shortlist**
   - Verifica i top candidati via browser
   - Seleziona 1 canale target

3. **Esecuzione protocolli (ordine standard)**
   - `CLERK` → `/skill:clerk`
   - `NICHE BENDING` → `/skill:niche-bending`
   - `SCRIPT STEALING` → `/skill:script-stealing`
   - `AI NEWS` → `/skill:ai-news`
   - `POET` → `/skill:poet`

4. **Packaging produzione**
   - `PRODUCTION PACK` → `/skill:production-pack`
   - Genera `production_pack_it.md` con soli prompt immagine + audio e `image_prompts_sceneXX_plus.txt`

5. **Gap tracking protocolli mancanti**
   - I 5 protocolli core hanno skill dedicata.
   - È disponibile anche la skill operativa extra `production-pack` per il packaging scena-per-scena.

## Convenzioni minime output
- Discovery: `breakout.txt`
- Analisi per canale: `output/<canale>/...`
- Produzioni: `output/<canale>/production/<data_slug>/...`
- Dashboard canale: `output/<canale>/resoconto_completo_it.txt`
- Resoconto per produzione: `output/<canale>/production/<data_slug>/resoconto_produzione_it.txt`
- Lingua di risposta: italiano (default)

## Regola resoconti produzione
- `output/<canale>/resoconto_completo_it.txt` **non** deve essere uno storico monolitico.
- Deve riflettere solo lo **stato attuale** delle produzioni presenti per quel canale.
- I dettagli operativi e lo storico breve vanno separati nei file `resoconto_produzione_it.txt` dentro ogni cartella di produzione.
- Se un canale ha più produzioni, il file root del canale funge da dashboard corrente e rimanda ai resoconti per-singola-produzione.
