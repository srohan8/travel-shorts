# 🎬 Travel Shorts AI

Turn your raw travel footage into a YouTube Shorts content plan — automatically.

## What it does
1. Scans your video folder locally
2. Extracts key frames (no full upload — just JPGs)
3. Sends frames to Gemini (free tier) for scene analysis
4. Generates a full YouTube Shorts story plan with timestamps
5. Cuts the clips automatically using FFmpeg

---

## Setup

### 1. Install FFmpeg
**Windows:** Download from https://ffmpeg.org/download.html → add to PATH
**Linux:** `sudo apt install ffmpeg`

### 2. Install Python dependencies
```bash
pip install flask google-generativeai Pillow
```

### 3. Get a free Gemini API key
Go to: https://aistudio.google.com/app/apikey
Create a free key (no credit card needed for free tier)

### 4. Run the app
```bash
python app.py
```

Then open your browser at: **http://localhost:5000**

---

## How to use

1. Paste your Gemini API key → Save
2. Enter your video folder path (e.g. `C:\Videos\Bali` or `/home/user/videos/bali`)
3. Click **Scan Folder** — it finds all .mp4 .mov .avi .mkv files
4. Select which videos to include
5. Write a short trip description (location, vibe, days, activities)
6. Click **Analyze & Generate Plan**
7. Review the YouTube Shorts plan
8. Click **Cut All Clips** — trimmed videos saved to `output/` folder

---

## Privacy
- Your full videos NEVER leave your machine
- Only small JPEG frames (640px wide) are sent to Gemini for analysis
- All cutting/processing happens locally via FFmpeg

## Output
Cut clips are saved to the `output/` folder next to `app.py`
Named like: `Short_1_Sunset_in_Ubud.mp4`
