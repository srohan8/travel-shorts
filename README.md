# Travel Shorts AI

![Travel Shorts AI](banner.png)

Turn your raw travel footage into a ready-to-post Shorts series — automatically.

---

## What it does

Travel Shorts AI analyses your travel videos with a vision AI model, identifies the best moments, and generates a complete content plan — series title, posting schedule, hooks, captions, and hashtags. It then cuts the clips and exports portrait 9:16 MP4s ready to upload.

Works fully **offline with Ollama**, or via the cloud using Gemini, OpenAI, or Anthropic APIs.

---

## Quick start (self-hosted)

**Requirements:** Python 3.11+, [FFmpeg](https://ffmpeg.org/download.html) on your PATH

```bash
git clone https://github.com/srohan8/travel-shorts.git
cd travel-shorts

pip install -r requirements.txt

cp .env.example .env
# Edit .env — add your Gemini or Ollama settings

python app.py
# → Opens http://localhost:5000 automatically
```

### Setup steps in the app

1. **Settings** (⚙️) — choose your AI provider and paste your API key
2. **Video Folder** — enter the absolute path to your footage folder
3. **Select Videos** — pick which clips to analyse
4. **Output** — choose format (Shorts / Reels / TikTok), look preset, and smart crop
5. **Trip Context** — describe your trip in a sentence; pick a **Vibe** (Cinematic, Funny, Storytelling…)
6. **Analyze & Generate Plan** — sit back while the AI works
7. **Cut All Clips** — exports stitched, cropped, colour-graded MP4s to `output/`

---

## AI Providers

| Provider | Model | Notes |
|----------|-------|-------|
| **Gemini** (default) | `gemini-2.0-flash` | Free tier available — get key at [aistudio.google.com](https://aistudio.google.com/app/apikey) |
| **Ollama** | any vision model | 100% local, no API key needed — [ollama.com](https://ollama.com) |
| **OpenAI** | `gpt-4o-mini` | Fast + cheap vision analysis |
| **Anthropic** | `claude-haiku-4-5` | Low latency, excellent instruction-following |

---

## Features

- **Smart crop** — face detection → motion fallback → centre crop (OpenCV)
- **Colour grading** — presets (Natural, Vivid, Cinematic, Warm, Cool, B&W HDR) + fine-tune sliders
- **Multi-segment Shorts** — AI stitches 2–4 clips from different videos into one cohesive Short
- **Travel Score** — per-Short virality scoring (Hook, Arc, Diversity, Pacing, Visual) with coaching notes
- **Vibe selector** — Cinematic / Funny / Storytelling / Informative / Raw & Real tone injection
- **Run History** — reload any previous analysis instantly, no re-processing needed
- **Minnal integration** — schedule posts directly from the app via [Minnal](https://app.minnal.io)
- **Format support** — YouTube Shorts (60s), Reels (90s), TikTok (10 min)

---

## Free vs Cloud

| | Self-hosted (this repo) | Cloud (coming soon) |
|--|--|--|
| Cost | Free forever | Paid subscription |
| Setup | Python + FFmpeg required | Zero setup |
| AI key | Your own | Managed |
| Privacy | Stays on your machine | Processed server-side |
| Updates | Manual | Automatic |

---

## Environment variables

Copy `.env.example` to `.env` and fill in what you need:

```
GEMINI_API_KEY=        # Get free key at aistudio.google.com
AI_PROVIDER=gemini     # gemini | ollama | openai | anthropic
OLLAMA_MODEL=gemma4:31b-cloud
OLLAMA_HOST=http://localhost:11434
OUTPUT_FORMAT=shorts   # shorts | reels | tiktok
SMART_CROP=true
```

See `.env.example` for all options with inline comments.

---

## Licence

**AGPL v3** — free to self-host, fork, and modify.

If you distribute a modified version or run it as a network service, your modifications must also be open-sourced under AGPL v3.

A managed cloud version (zero-setup, subscription) is coming — [moonga.studio](https://moonga.studio).
