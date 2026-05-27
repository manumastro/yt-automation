---
name: ai-news
description: "Protocollo AI NEWS — Ricerca trend/notizie real-time per alimentare la pipeline topic di un canale YouTube. Usa web_search/web_fetch per trovare eventi recenti, valutare potenziale e produrre shortlist operativa."
---

# 📰 Protocollo AI NEWS — Trend & Notizie per Topic Pipeline

Protocollo per trovare topic attuali (news/trend/eventi) compatibili con la formula del canale.

## Quando usare

- Dopo CLERK/NICHE BENDING per aggiornare le idee con trend real-time
- Quando l'utente chiede "cosa sta esplodendo ora" in una nicchia
- Prima di SCRIPT STEALING per scegliere topic più freschi

## Input richiesti

1. Cartella canale: `output/<canale>/`
2. File CLERK disponibili: preferibilmente `clerk/script_blueprint.md`, `clerk/hook_playbook.md`
3. (Opzionale) `niche-bending/niche_bends.md` e `niche-bending/topic_ideas.md`
4. Finestra temporale trend (default: ultimi 30 giorni)
5. Numero topic finali (default: 10)

## Procedura

### FASE 1 — Definisci criteri trend-fit

Deriva dai file CLERK i criteri per accettare/scartare news:
- coerenza con tono e format
- potenziale hook nei primi 3 secondi
- presenza di specificity spikes (date, numeri, nomi)
- disponibilità fonti verificabili

### FASE 2 — Web discovery (obbligatoria)

Usa `web_search` per trovare:
- breaking news della nicchia
- discussioni ad alta trazione (forum/community)
- eventi ricorrenti o anniversari utili

Query tipiche:
- `"<niche> breaking news"`
- `"<niche> latest incident"`
- `"site:reddit.com <niche>"`
- `"<topic> timeline explained"`

### FASE 3 — Verifica rapida fonti

Per i candidati top, usa `web_fetch` su 2-3 URL chiave per topic:
- valida fatti principali
- estrai dettagli narrativi utili (nomi, date, numeri, conseguenze)
- scarta rumor non corroborati

### FASE 4 — Scoring e shortlist

Assegna score 1-10 per ogni topic su:
1. Hook strength
2. Format fit
3. Novelty
4. Source confidence
5. Viral potential

Seleziona top topic (default: 10).

### FASE 5 — Output file

Crea snapshot datati in `output/<canale>/ideas/` (o in una sottocartella `ai-news-runs/` se preferisci):

1. `topic_shortlist_YYYY-MM-DD.md`
   - Top topic con score + rationale
   - Hook suggestion per ciascuno

2. `trend_sources_YYYY-MM-DD.md`
   - Elenco fonti/URL usati
   - Stato verifica (verified / partial / weak)

3. `news_angles_YYYY-MM-DD.md`
   - 2-3 angoli narrativi per ogni topic top
   - Nota su quale angolo è migliore per SCRIPT STEALING

**Nota per canali maturi con Niche Bending già eseguito** (es. finestexplainerr):
Questi file sono **supporto secondario**. La direzione principale viene da `ideas/secret_cities_strategy.md` + `ideas/evergreen_topic_ideas.md`. I topic AI NEWS devono passare il filtro dei pillar prima di entrare in production queue.

## Output attesi (esempio)

- `output/<canale>/ideas/topic_shortlist_2026-05-24.md`
- `output/<canale>/ideas/trend_sources_2026-05-24.md`
- `output/<canale>/ideas/news_angles_2026-05-24.md`

## Regole operative

- Usa sempre `web_search` (obbligatorio)
- Usa `web_fetch` per validare i topic principali
- Evita claim non verificabili o solo rumor
- Mantieni allineamento con la formula CLERK del canale
- Salva sempre gli output su file
