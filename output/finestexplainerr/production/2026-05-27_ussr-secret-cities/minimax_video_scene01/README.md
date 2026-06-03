# Scene 01 — tentativo video (2026-06-02)

## Sorgente produzione

- **Pack:** `production_pack_it.md` → Scene 01 Arzamas-16 Opening Hook
- **Immagine:** `../images_grok_lite_1080/scene_01.png` (Grok Imagine via MicuAPI)
- **Motion prompt:** slow push along barbed wire, cold mist, documentary cold war tone

## MiniMax Hailuo (api.minimaxi.com)

**Stato:** bloccato — non è un problema di prompt.

```json
{
  "status_code": 2056,
  "status_msg": "usage limit exceeded, weekly usage limit reached for Token Plan Plus (0/0 used), resets at 2026-06-08T00:00:00+08:00"
}
```

Interpretazione: sul piano **Token Plan Plus** la quota **video settimanale è 0/0** (nessun slot video incluso o esaurito). L’endpoint `remains` mostra `video` al 100% ma l’API di generazione rifiuta con 2056.

**Script:** `../generate_minimax_scene01_video.py` (image-to-video con URL pubblico temporaneo).

## MicuAPI `grok-imagine-video`

**Stato:** modello listato, ma `POST /v1/video/generations` non inoltra correttamente il campo `model` verso upstream (errore `Field required` / param `model`).

## Output locale (fallback)

| File | Descrizione |
|------|-------------|
| `scene_01_arzamas16_kenburns.mp4` | 6s, 1920×1080, pan lento + zoom leggero da `scene_01.png` (ffmpeg) |

Per **video AI vero** (movimento nebbia, luci torre, ecc.):

1. Upgrade MiniMax (Max/Ultra) o crediti pay-as-you-go + API key 按量计费 su [platform.minimaxi.com](https://platform.minimaxi.com)
2. Riprovare dopo **2026-06-08** se la quota video Plus si resetta con slot > 0
3. **Google Flow / Veo** (`flow_automation_tool`) con `scene_01.png` + motion prompt
4. Fix canale MicuAPI per `grok-imagine-video`