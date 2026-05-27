---
name: niche-bending
description: "Protocollo NICHE BENDING — Genera nicchie derivate uniche da un canale analizzato. Data una formula di successo (output di CLERK), trova content pillars alternativi, genera nomi canale, target audience, fonti di storie, e adatta il framework a nicchie inesplorate. Usa quando l'utente vuole espandere, variare, o replicare la formula di un canale in una nuova direzione."
---

# 📋 Protocollo NICHE BENDING — Generazione Niche Derivate

Il Niche Bending è il processo di prendere un **framework/formato** da un canale che funziona e applicarlo a una **nuova categoria di contenuto** mai esplorata, creando qualcosa di unico e non saturato.

> "Niche bending is basically taking a framework, a format from one niche, and then adding a content category to that, bending them together to create something unique." — Tim (Art of War)

## Quando usare

- L'utente ha già completato CLERK su un canale e vuole trovare **nuove direzioni**
- L'utente chiede di "espandere", "variare", "trovare alternative" alla nicchia originale
- L'utente vuole capire **quali altre nicchie** potrebbero usare la stessa formula
- L'utente chiede di "niche bend" dopo aver visto la formula di un canale

## Input richiesti

1. **Cartella output CLERK** — es. `output/finestexplainerr/clerk/`
   - Necessario: `sop_human.md`, `sop_ai.md`, `hook_playbook.md`
   - Opzionale: `script_blueprint.md`, `transcript_database.csv`
2. **Eventuale preferenza dell'utente** — es. "preferisco nicchie business/tech" oppure "voglio esplorare direzioni horror"

## Procedura

### FASE 1: Analisi della formula originale

Leggi i file della cartella CLERK e identifica:

#### 1.1 Elementi Estrattivi del Formato
- **Formato narrativo:** listicle, chronological, story-driven, etc.
- **Tono:** scary, educational, mysterious, inspirational, etc.
- **Struttura script:** hook tipo, durata, transizioni
- **Target emotivo:** paura, curiosità, ispirazione, nostalgia, etc.

#### 1.2 Content Pillars esistenti
- Quali sono i pilastri attuali?
- Quale performa meglio/peggio?
- C'è spazio per pilastri complementari?

#### 1.3 Formula di Successo
- Cosa rende il canale virale? (hook forti? evergreen? shareability?)
- Qual è il "filo conduttore" emotivo?
- Chi è l'audience primario?

### FASE 2: Generazione Niche Bends

Genera **3-5 Niche Bends** seguendo la matrice di compatibilità:

#### Matrice di Compatibilità

```
FORMATO (dalla formula) + NUOVA CATEGORIA = NICHE BEND
```

Ogni Niche Bend deve avere:

| Elemento | Descrizione |
|----------|-------------|
| **Nome canale** | Nome originale o nuovo, memorable |
| **Concept** | Frase che cattura l'essenza |
| **Content Pillars** | 3-4 categorie di contenuto |
| **Target Audience** | Demografica + psicografica |
| **Primary Sources** | 5-9 risorse dove trovare storie (Reddit, Wikipedia, podcast, libri, etc.) |
| **Topic Discovery Process** | Come trovare idee per quella nicchia |
| **Adaptation Framework** | Come modificare la formula originale per la nuova nicchia |
| **High-Performance Signals** | Cosa rende un video virale in quella nicchia |
| **Tonalità adattata** | Come il tono originale si adatta |

#### Criteri di Qualità

Un buon Niche Bend deve essere:
- ✅ **Unico** — non saturato da competitor
- ✅ **Sostenibile** — abbastanza contenuto per 100+ video
- ✅ **Adattabile** — formula replicabile
- ✅ **Monetizzabile** — brand deal potenziali
- ✅ **Scalabile** — evergreen o ricorrente

### FASE 3: Deep Research (per ogni Niche Bend)

Per i 2-3 Niche Bends più promettenti, fai ricerca autonoma sul web:

1. **Cerca la nicchia** — es. "scam explainer channel", "true crime mysteries YouTube"
2. **Trova competitor** — esistono canali? Sono saturi?
3. **Trova storie** — cerca fonti primarie (Reddit threads, articoli, podcast)
4. **Valuta potenziale** — è una nicchia con storia o no?

Usa il tool `web_search` per ricerche approfondite:

```bash
web_search "best [niche] YouTube channels faceless explainer"
web_search "[niche] stories for videos Reddit"
web_search "[topic] mysteries unexplained"
```

### FASE 4: Generazione Output

Genera **3 documenti** nella directory `output/{nome_canale}/niche-bending/`:

---

#### 📄 1. `niche_bends.md` — Niche Bends Completi

Documento strutturato con tutti i Niche Bends generati:

```markdown
# Niche Bending Report: {Nome Canale Originale}

## Executive Summary
[Qual è la formula originale e perché funziona]
[Quanti niche bends generati e su quale logica]

## Niche Bend 1: {Nome}
### Concept
[Frase che cattura l'essenza]

### Content Pillars
1. [Pillar] — [descrizione]
2. ...

### Target Audience
- **Età:** 18-35
- **Genere:** Male predominante
- **Psicografica:** [interessi, comportamenti]
- **Perché guardano:** [bisogno emotivo soddisfatto]

### Primary Sources
1. [Nome] — [URL/referenza] — [tipo di storie che offre]
2. ...

### Adaptation Framework
[Come modificare la formula originale per questa nicchia]

### High-Performance Signals
[Quali elementi rendono un video virale in questa nicchia]

### Tonalità Adattata
[Come il tono del canale originale si adatta qui]

---

Ripeti per Niche Bend 2, 3, etc.

## Confronto Niche Bends
| Niche Bend | Uniqueness | Sustainability | Scalability | Monetization | TOTALE |
|---|---|---|---|---|---|
| {Nome 1} | 8 | 7 | 9 | 6 | 30 |
| {Nome 2} | 9 | 8 | 7 | 8 | 32 |
```

---

#### 📄 2. `primary_sources.md` — Fonti Primarie per tutte le nicchie

Raccolta organizzata di fonti per ogni Niche Bend:

```markdown
# Primary Sources Database

## Per {Niche Bend 1}
### Forum & Community
- [Nome] — [URL] — [descrizione]
### Notizie & Articoli
- [Nome] — [URL] — [descrizione]
### Podcast & Video
- [Nome] — [URL] — [descrizione]
### Libri & Documenti
- [Nome] — [URL] — [descrizione]

## Per {Niche Bend 2}
[stessa struttura]
```

---

#### 📄 3. `topic_ideas.md` — Idee Video per ogni Niche Bend

Genera 10-15 idee video per i 2 Niche Bends più promettenti:

```markdown
# Topic Ideas: {Niche Bend Nome}

## Content Pillar 1: [Nome]
1. **[Titolo video con hook forte]** — [breve descrizione + perché funzionerebbe]
2. ...

## Content Pillar 2: [Nome]
1. ...

---

## Content Pillar 1: {Niche Bend 2 Nome}
...
```

---

### FASE 5: Merge opzionale

Se l'utente vuole, puoi proporre di **mergiare due Niche Bends** per creare qualcosa di ancora più unico.

Il merge funziona quando:
- I due Niche Bends hanno audience simile
- I content pillars sono complementari
- Il "filo conduttore" emotivo è lo stesso

Formula:
```
NICHE BEND A + NICHE BEND B = NUOVO CONCEPT IBRIDO
```

Il risultato del merge ha:
- Nome canale nuovo
- Content pillars combinati
- Fonti di entrambi
- Formula ibrida

---

### FASE 6: Summary finale

Al termine, mostra all'utente un riepilogo:

```
✅ NICHE BENDING completato per {Nome Canale Originale}

🎯 Niche Bends generati: {N}
   1. {Nome 1} — Score: {X}/40
   2. {Nome 2} — Score: {X}/40
   3. {Nome 3} — Score: {X}/40

📁 File generati in output/{nome_canale}/niche-bending/:
   1. niche_bends.md — Niche Bends completi con score
   2. primary_sources.md — Database fonti primarie
   3. topic_ideas.md — Idee video per pilastro

**Dopo il Niche Bending (per canali come finestexplainerr):**
Una volta completato il bending, promuovi la strategia e le idee in `ideas/secret_cities_strategy.md` e `ideas/evergreen_topic_ideas.md`.
La cartella `niche-bending/` diventa archivio di ricerca. La produzione futura si guida da `ideas/` (Niche Bending come driver principale).

🏆 Top Niche Bend consigliato: {Nome}

💡 Prossimi passi suggeriti:
   - Lancia /skill:script-stealing con il Niche Bend scelto
   - Usa primary_sources.md per iniziare la ricerca storie
   - Rivedi topic_ideas.md per idee video immediate
```

## Note importanti

- **Non proporre solo nicchie "ovvie"** — cerca direzioni non esplorate
- **Usa la creatività** — il valore del Niche Bending è trovare angoli non saturati
- **Valuta la sostenibilità** — chiediti: "Posso fare 100 video in questa nicchia?"
- **Chiedi conferma** prima di fare deep research estesa su tutti i Niche Bends
- **Ilmergeè potente** — a volte combinare due nicchie crea qualcosa di unico