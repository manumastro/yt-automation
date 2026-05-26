---
name: clerk
description: "Protocollo CLERK — Analisi completa di un canale YouTube competitor. Reverse-engineering della formula del canale: estrae tutti i transcript, analizza la struttura degli script, genera SOP per umani e per AI, crea un database dei transcript con key takeaways. Usa quando l'utente vuole analizzare, copiare, o capire perché un canale YouTube funziona."
---

# 📋 Protocollo CLERK — Analisi Canale Competitor

Protocollo di reverse-engineering per canali YouTube. Analizza un canale competitor e produce una suite completa di documenti strategici.

## Quando usare

- L'utente fornisce un link a un canale YouTube e vuole analizzarlo
- L'utente chiede di "copiare", "analizzare", "fare reverse engineering" di un canale
- L'utente vuole capire perché un canale funziona
- L'utente chiede una SOP basata su un canale esistente

## Input richiesti

Prima di iniziare, chiedi all'utente:

1. **Link del canale YouTube** (es. `https://youtube.com/@NomeCanale`)
2. **Tipo di contenuto da analizzare:** shorts, long form, o entrambi?
   - Shorts = video < 60 secondi
   - Long form = video > 1 minuto
3. **Quanti video analizzare?** (default: tutti, oppure "top 10/20/50 per views")
4. **Lingua preferita transcript:** (default: inglese, oppure specifica)

## Procedura

### FASE 1: Raccolta dati canale

Usa il tool `browser` per visitare il canale YouTube e raccogliere:

```
browser open https://youtube.com/@NomeCanale
browser screenshot
```

Raccogli:
- Nome canale, iscritti, data creazione (se visibile)
- Numero totale di video
- Descrizione canale (about page)
- Link social e sito web

Poi visita la tab "Videos" ordinata per "Most popular":

```
browser open https://youtube.com/@NomeCanale/videos?view=0&sort=p
browser snapshot -i
browser screenshot
```

Raccogli per ogni video visibile:
- Titolo
- Views
- Data di pubblicazione (approssimativa)
- Durata (se visibile)

Salva questa lista in un file:

```bash
mkdir -p output/{nome_canale}/clerk
```

Crea il file `output/{nome_canale}/clerk/video_list.md` con la tabella dei video.

### FASE 2: Estrazione transcript

Per ogni video della lista (o quelli selezionati dall'utente), estrai il transcript.

```bash
source .venv/bin/activate
mkdir -p output/{nome_canale}/transcripts
```

Per ogni video:
```bash
python extract_transcript.py "VIDEO_URL" --cookies cookies.txt -o "output/{nome_canale}/transcripts/{titolo_pulito}.txt"
```

**Regole:**
- Pulisci il titolo per il filename (no spazi, no caratteri speciali)
- Se un transcript fallisce, prova senza cookies, poi con `--languages en,it`
- Se fallisce ancora, annotalo come "transcript non disponibile" e prosegui
- Mostra progresso: "Estratto 3/12 transcript..."

### FASE 3: Analisi degli script

Leggi TUTTI i transcript estratti e analizza in profondità. Per ogni video, identifica:

#### 3.1 Struttura Hook (primi 5-10 secondi)
- Tipo di hook usato (domanda, statistica, storia, shock, mistero, sfida)
- Testo esatto dell'hook
- Perché funziona

#### 3.2 Struttura Script
- Schema narrativo (es. setup → escalation → climax → resolution)
- Durata media segmenti
- Transizioni tra sezioni
- Uso di cliffhanger interni (open loops)

#### 3.3 Tecniche di Retention
- Pattern interrupts (cambi improvvisi di tono, ritmo, argomento)
- Open loops (promesse non ancora soddisfatte che tengono lo spettatore)
- Specificity spikes (numeri precisi, nomi, date, dettagli concreti)
- Call to action mid-roll (subscribe, like, comment)
- Emotional triggers (paura, curiosità, sorpresa, empatia)

#### 3.4 Pattern ricorrenti
- Formule di titolo ripetute
- Strutture di thumbnail (se osservabili)
- Temi/content pillars del canale
- Tono di voce e stile narrativo

### FASE 4: Generazione output

Genera **5 documenti** nella directory `output/{nome_canale}/clerk/`:

---

#### 📄 1. `sop_human.md` — SOP per Umani

Documento leggibile che spiega PERCHÉ il canale funziona. Struttura:

```markdown
# SOP Analisi: {Nome Canale}
## Panoramica canale
## Perché questo canale funziona (executive summary)
## Analisi Hook — I {N} framework di hook usati
  ### Hook Framework 1: [nome]
  - Descrizione
  - Esempio dal canale (testo esatto)
  - Quando usarlo
  ### Hook Framework 2: [nome]
  ...
## Struttura Script — Blueprint
  - Schema narrativo standard del canale
  - Variazioni osservate
  - Durate tipiche per sezione
## Storytelling Framework
  - Come costruiscono la tensione narrativa
  - Uso di personaggi, conflitto, risoluzione
  - Tecniche emotive ricorrenti
## Tecniche di Retention
  - Pattern interrupts usati
  - Open loops (con esempi)
  - Specificity spikes (con esempi)
## Content Pillars
  - Categorie di contenuto
  - Distribuzione video per pillar
## Raccomandazioni
  - Cosa copiare
  - Cosa migliorare
  - Errori da evitare
```

---

#### 📄 2. `sop_ai.md` — SOP per AI (Machine-Readable)

File ottimizzato per essere dato come input ad altri agenti AI (Script Stealing, Poet, ecc.).
Formato strutturato, conciso, con istruzioni dirette:

```markdown
# CHANNEL REPLICATION SOP: {Nome Canale}

## CHANNEL PROFILE
- Name: ...
- Niche: ...
- Avg views: ...
- Video count: ...
- Style: ...

## SCRIPT FORMULA
### Structure
[Step-by-step della struttura script da replicare]

### Hook Templates
1. [HOOK_TYPE]: "[Template con variabili]"
2. ...

### Retention Rules
- MUST: [regola obbligatoria]
- MUST: ...
- AVOID: [cosa non fare]
- AVOID: ...

### Tone & Voice
- [descrizione precisa del tono]
- [vocabolario tipo]
- [livello di complessità]

### Content Pillars
1. [Pillar] — [descrizione + % video]
2. ...

## TITLE FORMULAS
1. "[Formula con variabili]"
2. ...

## EXAMPLE SCRIPTS
[2-3 script riassunti come riferimento strutturale]
```

---

#### 📄 3. `hook_playbook.md` — Playbook degli Hook

Catalogo completo di tutti gli hook framework identificati con:
- Nome del framework
- Pattern/formula
- 3+ esempi dal canale
- Varianti suggerite per altri topic
- Quando funziona meglio (tipo di video, audience)

---

#### 📄 4. `transcript_database.csv` — Database Transcript

File CSV con tutti i transcript e metadata:

```csv
video_id,title,url,views,duration,publish_date,hook_type,hook_text,structure_type,key_takeaways,transcript_file
```

Per ogni video includi:
- Metadata base (id, titolo, url, views, durata)
- Hook type e testo dell'hook
- Tipo di struttura script
- 3-5 key takeaways (cosa rende questo video efficace)
- Path al file transcript

---

#### 📄 5. `script_blueprint.md` — Script Structure Blueprint

Template step-by-step per scrivere uno script nello stile del canale:

```markdown
# Script Blueprint: {Nome Canale} Style

## Parametri
- Durata target: X minuti
- Struttura: [nome pattern]
- Tono: [descrizione]

## Template

### [0:00-0:05] HOOK
[Istruzioni precise + template]

### [0:05-0:30] SETUP
[Istruzioni precise + template]

### [0:30-X:XX] BODY
[Istruzioni precise + template per ogni segmento]

### [ultimi 10-15 sec] PAYOFF + CTA
[Istruzioni precise + template]

## Checklist pre-pubblicazione
- [ ] Hook cattura in < 3 secondi?
- [ ] Almeno 2 open loops nei primi 30 sec?
- [ ] Pattern interrupt ogni 30-45 sec?
- [ ] Specificity spike ogni 2-3 frasi?
- [ ] CTA naturale (non forzato)?
- [ ] Ending pulito (taglio dopo payoff)?
```

---

### FASE 5: Summary finale

Al termine, mostra all'utente un riepilogo:

```
✅ CLERK completato per {Nome Canale}

📊 Statistiche:
   - Video analizzati: X
   - Transcript estratti: X/Y
   - Hook framework identificati: X
   - Content pillars: X

📁 File generati in output/{nome_canale}/clerk/:
   1. sop_human.md — SOP leggibile
   2. sop_ai.md — SOP per altri agenti AI
   3. hook_playbook.md — Catalogo hook
   4. transcript_database.csv — Database completo
   5. script_blueprint.md — Template script

💡 Prossimi passi suggeriti:
   - Lancia /skill:niche-bending con la SOP per trovare niche bends
   - Usa sop_ai.md come input per Script Stealing
   - Rivedi hook_playbook.md per le tue prime idee video
```

## Note importanti

- **Tempo stimato:** 10-20 minuti a seconda del numero di video
- **Se l'estrazione transcript è lenta**, proponi all'utente di analizzare solo i top 10-15 video per views
- **Se il browser è lento**, usa `extract_transcript.py` direttamente senza navigare YouTube
- **Qualità > quantità:** meglio analizzare bene 10 video che male 50
- **Chiedi sempre conferma** prima di procedere con l'estrazione massiva dei transcript
