---
name: script-stealing
description: "Protocollo SCRIPT STEALING — Ideazione + scrittura script da un canale analizzato (output CLERK). Converte blueprint/hook/SOP in topic shortlist, outline e script pronti produzione. Usa quando l'utente vuole passare da analisi a script operativi."
---

# ✍️ Protocollo SCRIPT STEALING — Ideazione + Scrittura Script

Trasforma l'analisi CLERK in output editoriali pronti per produzione.

## Quando usare

- L'utente ha già `output/<canale>/clerk/` e vuole "scrivere i video"
- L'utente chiede di replicare la formula di un competitor
- L'utente vuole topic + outline + script pronti

## Input richiesti

1. Cartella CLERK: `output/<canale>/clerk/`
   - obbligatori: `script_blueprint.md`, `hook_playbook.md`, `sop_ai.md`
   - utili: `transcript_database.csv`, `video_list.md`
2. (Opzionale) cartella NICHE BENDING: `output/<canale>/niche-bending/`
3. Numero script da produrre (default: 1)
4. Lingua output script (default: EN, se non specificata)

## Procedura

### FASE 1 — Setup produzione

Crea directory:

`output/<canale>/production/<YYYY-MM-DD>_<slug>/`

File target:
- `outline.md`
- `script.md`
- `title_options.md`
- `qa_checklist.md`

### FASE 2 — Topic selection

- Estrai 3-5 topic coerenti con blueprint + hook patterns
- Se presente `niche-bending/topic_ideas.md`, preferisci topic con doppio fit (formula + niche bend)
- Seleziona 1 topic principale con motivazione

### FASE 3 — Research rapida web (obbligatoria)

Usa `web_search` (e `web_fetch` se serve) per:
- verificare che il topic abbia materiale sufficiente
- raccogliere 5-10 fatti/source points affidabili
- trovare eventuali angoli trend/news recenti da integrare nello script

Salva un mini recap fonti/fatti in `outline.md` prima della scaletta.

### FASE 4 — Outline strutturato

Crea outline completo con:
- Hook iniziale (cold open)
- Sezioni/entry con progressione narrativa
- Specificity spikes previsti (numeri, date, nomi)
- Open loops e payoff finale

### FASE 5 — Script completo

Scrivi script finale seguendo rigorosamente:
- struttura e ritmo da `script_blueprint.md`
- pattern hook da `hook_playbook.md`
- regole operative da `sop_ai.md`

### FASE 6 — Packaging editoriale

In `title_options.md` genera:
- 10 titoli in stile canale
- 3 varianti thumbnail angle (testuale/concept)

### FASE 7 — QA finale

In `qa_checklist.md` verifica:
- hook forte nei primi secondi
- assenza filler
- ritmo e chiarezza
- presenza open loops + payoff
- coerenza con formula competitor

## Output attesi

- `output/<canale>/production/<YYYY-MM-DD>_<slug>/outline.md` (include mini research fonti)
- `output/<canale>/production/<YYYY-MM-DD>_<slug>/script.md`
- `output/<canale>/production/<YYYY-MM-DD>_<slug>/title_options.md`
- `output/<canale>/production/<YYYY-MM-DD>_<slug>/qa_checklist.md`

## Regole operative

- Non inventare format estranei alla formula CLERK
- Mantieni il tono coerente col canale target
- Verifica fatti principali con `web_search`/`web_fetch` prima della stesura finale
- Se mancano file CLERK obbligatori, fermati e chiedi integrazione
- Salva sempre su file (non solo in chat)
