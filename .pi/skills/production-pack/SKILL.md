---
name: production-pack
description: "Protocollo PRODUCTION PACK — Converte uno script finale in un pack operativo scena-per-scena con soli prompt immagine per ChatGPT e prompt audio per Gemini TTS. Genera anche un file .txt con soli prompt immagine, uno per riga."
---

# 🧩 Protocollo PRODUCTION PACK — Prompt Immagine + Audio

Trasforma uno script già finalizzato in un pack di produzione minimale e operativo.

## Quando usare

- Dopo `SCRIPT STEALING` o `POET`
- Quando esiste già `script_final.md` oppure almeno `script.md`
- Quando serve preparare asset scena-per-scena per immagini + TTS

## Input richiesti

1. Cartella produzione:
   - `output/<canale>/production/<YYYY-MM-DD>_<slug>/`
2. Script sorgente:
   - preferito: `script_final.md`
   - fallback: `script.md`
3. File formula canale consigliati:
   - `output/<canale>/clerk/script_blueprint.md`
   - `output/<canale>/clerk/sop_ai.md`
4. Lingua pack:
   - default: italiano per istruzioni/meta
   - prompt immagine e prompt audio possono restare in inglese se più adatti agli strumenti

## Obiettivo

Generare un `production_pack_it.md` che contenga **solo**:
1. prompt immagine per ChatGPT
2. prompt audio Gemini TTS per ogni scena

**Non includere prompt video.**

In aggiunta, generare un `.txt` con i soli prompt immagine, **uno per riga**.

## Procedura

### FASE 1 — Lettura e segmentazione scene

- Leggi lo script finale e segmentalo in scene brevi e producibili
- Mantieni ordine narrativo e timing naturale
- Ogni scena deve avere:
  - nome scena
  - numerazione scena
  - testo voiceover della scena
  - prompt immagine specifico della scena

### FASE 2 — Prompt immagine globale

Definisci un **prompt generale globale** coerente con:
- tone of channel
- tema del video
- realism level
- palette / lighting / camera feel
- esclusioni visive importanti

Questo prompt generale deve comparire nel `.md` e deve essere riusato come base per tutte le scene.

### FASE 3 — Prompt immagine scena-specifici

Per ogni scena crea:
- un blocco `Prompt generale`
- un blocco `Prompt scena specifico`
- un blocco `Prompt finale combinato per ChatGPT`

Il `Prompt finale combinato` deve essere semplicemente:
- prompt generale
- + prompt scena specifico

Struttura desiderata per scena nel `.md`:

```md
## Scene 01 — <nome scena>

### A) Prompt immagine generale
<global prompt identico per tutte le scene>

### B) Prompt immagine scena specifico
<scene-specific visual prompt>

### C) Prompt finale immagine — ChatGPT
<general prompt + scene-specific prompt in un unico blocco>

### D) Prompt audio — Gemini TTS
Scene
<descrizione breve scena>

Sample Context
<contesto vocale breve>

Text
<testo voiceover esatto della scena>
```

### FASE 4 — Prompt audio Gemini TTS

Per ogni scena crea un prompt audio con struttura stabile:

```text
Scene
...

Sample Context
...

Text
...
```

Regole:
- `Text` deve contenere solo il testo da pronunciare in quella scena
- `Sample Context` deve guidare tono, continuità e delivery
- tono coerente con il canale
- niente note video
- niente timing SMPTE nel testo TTS

### FASE 5 — File TXT prompt immagini

Genera anche:
- `image_prompts_sceneXX_plus.txt`

Formato:
- una scena per riga
- ogni riga contiene **solo** il prompt finale combinato immagine della scena
- nessuna label, nessun prefisso, nessun metadata inline

Formato riga:

```text
<prompt finale combinato immagine>
```

### FASE 6 — QA pack

Verifica che:
- il `.md` contenga solo immagine + audio
- nessuna sezione video sia presente
- il prompt generale sia coerente e ripetuto correttamente
- i prompt scena-specifici siano visivi, concreti e non ridondanti
- il file `.txt` abbia una sola riga per scena
- il `Text` del prompt audio corrisponda esattamente al voiceover scelto

## Output attesi

- `output/<canale>/production/<YYYY-MM-DD>_<slug>/production_pack_it.md`
- `output/<canale>/production/<YYYY-MM-DD>_<slug>/image_prompts_sceneXX_plus.txt`

## Regole operative

- Se esiste `script_final.md`, usa quello come fonte primaria
- Se manca `script_final.md`, usa `script.md`
- Non inventare scene fuori script
- Non aggiungere prompt video
- Il `.md` deve restare operativo e minimale
- I prompt immagine devono essere pensati per modelli text-to-image tipo ChatGPT
- Salva sempre i file su disco
