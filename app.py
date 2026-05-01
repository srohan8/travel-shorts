import os
import io
import sys
import json
import base64
import subprocess
import re
import glob
import threading
import time
import webbrowser
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory, render_template
from dotenv import load_dotenv
from dotenv import set_key as dotenv_set_key
import google.generativeai as genai
from PIL import Image
import tempfile
import ollama as ollama_client
import urllib.request

# ── Paths (works both in dev and when frozen by PyInstaller) ─────────────────
if getattr(sys, 'frozen', False):
    _BUNDLE  = Path(sys._MEIPASS)           # read-only bundled assets
    _APP_DIR = Path(sys.executable).parent  # writable dir next to .exe
else:
    _BUNDLE  = Path(__file__).parent
    _APP_DIR = Path(__file__).parent

_ENV_FILE = _APP_DIR / ".env"
load_dotenv(_ENV_FILE)

# Write errors to a log file when frozen (no console window)
if getattr(sys, 'frozen', False):
    import logging
    _log_file = _APP_DIR / "travel-shorts.log"
    logging.basicConfig(filename=str(_log_file), level=logging.ERROR,
                        format="%(asctime)s %(levelname)s %(message)s")

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
AI_PROVIDER    = os.environ.get("AI_PROVIDER", "gemini")
OLLAMA_MODEL   = os.environ.get("OLLAMA_MODEL", "gemma4:31b-cloud")
OLLAMA_HOST    = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
MINNAL_API_KEY = os.environ.get("MINNAL_API_KEY", "")
MINNAL_BASE    = "https://app.minnal.io"

OUTPUT_DIR = _APP_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

_ffmpeg_bin = _BUNDLE / "ffmpeg" / "bin"
def _find_bin(name):
    for candidate in [name + ".exe", name]:
        p = _ffmpeg_bin / candidate
        if p.exists():
            return str(p)
    return name  # fall back to system PATH

FFMPEG  = _find_bin("ffmpeg")
FFPROBE = _find_bin("ffprobe")

progress_log = []
progress_lock = threading.Lock()
analyze_progress = {"current": 0, "total": 0}
stop_requested = False

def log(msg):
    with progress_lock:
        progress_log.append(msg)
    print(msg)

def get_video_metadata(video_path):
    """Extract metadata from video using ffprobe"""
    cmd = [
        FFPROBE, "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        data = json.loads(result.stdout)
        fmt = data.get("format", {})
        tags = fmt.get("tags", {})
        duration = float(fmt.get("duration", 0))
        return {
            "filename": Path(video_path).name,
            "duration": duration,
            "duration_str": f"{int(duration//60)}:{int(duration%60):02d}",
            "size_mb": round(int(fmt.get("size", 0)) / 1024 / 1024, 1),
            "creation_time": tags.get("creation_time", tags.get("date", "Unknown")),
            "location": tags.get("location", tags.get("com.apple.quicktime.location.ISO6709", "Unknown")),
            "path": video_path
        }
    return {"filename": Path(video_path).name, "duration": 0, "path": video_path}

def extract_frames(video_path, num_frames=None):
    """Extract evenly spaced frames from video, scaling count with duration"""
    meta = get_video_metadata(video_path)
    duration = meta.get("duration", 60)
    if num_frames is None:
        if duration < 30:
            num_frames = 3
        elif duration < 120:
            num_frames = 5
        elif duration < 300:
            num_frames = 8
        else:
            num_frames = 12
    frames = []
    
    with tempfile.TemporaryDirectory() as tmpdir:
        for i in range(num_frames):
            timestamp = (duration / (num_frames + 1)) * (i + 1)
            frame_path = os.path.join(tmpdir, f"frame_{i}.jpg")
            cmd = [
                FFMPEG, "-ss", str(timestamp), "-i", video_path,
                "-vframes", "1", "-q:v", "3", "-vf", "scale=640:-1",
                frame_path, "-y", "-loglevel", "quiet"
            ]
            subprocess.run(cmd, capture_output=True)
            if os.path.exists(frame_path):
                with open(frame_path, "rb") as f:
                    frames.append({
                        "timestamp": timestamp,
                        "timestamp_str": f"{int(timestamp//60)}:{int(timestamp%60):02d}",
                        "data": base64.b64encode(f.read()).decode()
                    })
    return frames

def analyze_video_with_gemini(video_path, trip_context, frames):
    """Send frames to Gemini for analysis"""
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash-lite")
    
    parts = []
    parts.append(f"""You are a travel content analyst. Analyze these frames from a travel video.

Trip context: {trip_context}
Video file: {Path(video_path).name}

For each frame, identify:
- What is happening (scene description)
- Location/setting (beach, city, restaurant, landmark, etc.)
- Mood/energy (calm, exciting, funny, scenic, etc.)
- YouTube Shorts potential (high/medium/low) and why

Then suggest 1-3 specific clips from this video for YouTube Shorts, with:
- Suggested start/end timestamps (estimate based on frame positions)
- Short title (max 6 words)
- Hook line (first sentence to grab attention)
- Caption (2-3 sentences)
- 5 hashtags

Respond in this exact JSON format:
{{
  "scenes": [
    {{"timestamp": "0:30", "description": "...", "setting": "...", "mood": "...", "shorts_potential": "high/medium/low"}}
  ],
  "suggested_clips": [
    {{
      "title": "...",
      "start_time": "0:00",
      "end_time": "0:30",
      "hook": "...",
      "caption": "...",
      "hashtags": ["#travel", "#..."],
      "why": "..."
    }}
  ]
}}""")
    
    for i, frame in enumerate(frames):
        img_data = base64.b64decode(frame["data"])
        parts.append({
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": frame["data"]
            }
        })
        parts.append(f"[Frame at {frame['timestamp_str']}]")
    
    prompt_parts = [parts[0]]
    for i, frame in enumerate(frames):
        img = Image.open(io.BytesIO(base64.b64decode(frame["data"])))
        prompt_parts.append(f"\n[Frame at {frame['timestamp_str']}]:")
        prompt_parts.append(img)
    
    for attempt in range(3):
        try:
            response = model.generate_content(prompt_parts)
            break
        except Exception as e:
            if "429" in str(e) and attempt < 2:
                wait = 30 * (attempt + 1)
                log(f"Rate limited, waiting {wait}s before retry...")
                time.sleep(wait)
            else:
                raise

    # Parse JSON from response
    text = response.text
    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match:
        return json.loads(json_match.group())
    return {"scenes": [], "suggested_clips": [], "raw": text}

def generate_shorts_plan(all_analyses, trip_context, video_metas):
    """Generate overall YouTube Shorts content plan"""
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash-lite")

    summary = json.dumps({
        "trip_context": trip_context,
        "videos_analyzed": len(all_analyses),
        "all_clips": [
            {**clip, "source_video": Path(a.get("video", "")).name}
            for a in all_analyses
            for clip in a.get("suggested_clips", [])
        ]
    }, indent=2)

    prompt = f"""Based on this travel video analysis, create a YouTube Shorts content plan.

{summary}

IMPORTANT: For source_video in each segment, you MUST copy the exact filename from the source_video field in all_clips above. Do not invent or shorten filenames.

Create a content strategy with:
1. Overall trip narrative (2-3 sentences)
2. A curated series of YouTube Shorts ordered for maximum engagement. Each Short should be a mini-montage of 2-4 segments from different moments or different source videos, stitched into one cohesive clip. Aim for a total combined duration of 30-60 seconds per Short (the ideal length for YouTube Shorts). Only use one segment if that single clip is already 30+ seconds and compelling on its own. Skip repetitive footage — quality over quantity.
3. Posting schedule suggestion (one post per day or every other day)
4. Series title and theme

Respond in JSON:
{{
  "series_title": "...",
  "narrative": "...",
  "posting_schedule": "...",
  "shorts": [
    {{
      "order": 1,
      "title": "...",
      "segments": [
        {{"source_video": "filename.mp4", "start_time": "0:10", "end_time": "0:25"}},
        {{"source_video": "filename2.mp4", "start_time": "1:05", "end_time": "1:20"}},
        {{"source_video": "filename3.mp4", "start_time": "0:45", "end_time": "1:05"}}
      ],
      "hook": "...",
      "caption": "...",
      "hashtags": ["#..."]
    }}
  ]
}}"""

    response = model.generate_content(prompt)
    text = response.text
    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match:
        return json.loads(json_match.group())
    return {"shorts": [], "raw": text}

def analyze_video_with_ollama(video_path, trip_context, frames):
    prompt = f"""You are a travel content analyst. Analyze these frames from a travel video.

Trip context: {trip_context}
Video file: {Path(video_path).name}

For each frame, identify:
- What is happening (scene description)
- Location/setting (beach, city, restaurant, landmark, etc.)
- Mood/energy (calm, exciting, funny, scenic, etc.)
- YouTube Shorts potential (high/medium/low) and why

Then suggest 1-3 specific clips from this video for YouTube Shorts, with:
- Suggested start/end timestamps (estimate based on frame positions)
- Short title (max 6 words)
- Hook line (first sentence to grab attention)
- Caption (2-3 sentences)
- 5 hashtags

Respond in this exact JSON format:
{{
  "scenes": [
    {{"timestamp": "0:30", "description": "...", "setting": "...", "mood": "...", "shorts_potential": "high/medium/low"}}
  ],
  "suggested_clips": [
    {{
      "title": "...",
      "start_time": "0:00",
      "end_time": "0:30",
      "hook": "...",
      "caption": "...",
      "hashtags": ["#travel", "#..."],
      "why": "..."
    }}
  ]
}}"""

    client = ollama_client.Client(host=OLLAMA_HOST)
    response = client.chat(
        model=OLLAMA_MODEL,
        messages=[{
            "role": "user",
            "content": prompt,
            "images": [frame["data"] for frame in frames]
        }]
    )
    text = response.message.content
    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match:
        return json.loads(json_match.group())
    return {"scenes": [], "suggested_clips": [], "raw": text}

def generate_shorts_plan_ollama(all_analyses, trip_context, video_metas):
    summary = json.dumps({
        "trip_context": trip_context,
        "videos_analyzed": len(all_analyses),
        "all_clips": [
            {**clip, "source_video": Path(a.get("video", "")).name}
            for a in all_analyses
            for clip in a.get("suggested_clips", [])
        ]
    }, indent=2)

    prompt = f"""Based on this travel video analysis, create a YouTube Shorts content plan.

{summary}

IMPORTANT: For source_video in each segment, you MUST copy the exact filename from the source_video field in all_clips above. Do not invent or shorten filenames.

Create a content strategy with:
1. Overall trip narrative (2-3 sentences)
2. A curated series of YouTube Shorts ordered for maximum engagement. Each Short should be a mini-montage of 2-4 segments from different moments or different source videos, stitched into one cohesive clip. Aim for a total combined duration of 30-60 seconds per Short (the ideal length for YouTube Shorts). Only use one segment if that single clip is already 30+ seconds and compelling on its own. Skip repetitive footage — quality over quantity.
3. Posting schedule suggestion (one post per day or every other day)
4. Series title and theme

Respond in JSON:
{{
  "series_title": "...",
  "narrative": "...",
  "posting_schedule": "...",
  "shorts": [
    {{
      "order": 1,
      "title": "...",
      "segments": [
        {{"source_video": "filename.mp4", "start_time": "0:10", "end_time": "0:25"}},
        {{"source_video": "filename2.mp4", "start_time": "1:05", "end_time": "1:20"}},
        {{"source_video": "filename3.mp4", "start_time": "0:45", "end_time": "1:05"}}
      ],
      "hook": "...",
      "caption": "...",
      "hashtags": ["#..."]
    }}
  ]
}}"""

    client = ollama_client.Client(host=OLLAMA_HOST)
    response = client.chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    text = response.message.content
    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match:
        return json.loads(json_match.group())
    return {"shorts": [], "raw": text}

def cut_and_concat(segments, output_name):
    """Cut multiple segments from source videos and concatenate into one clip."""
    output_path = OUTPUT_DIR / output_name
    with tempfile.TemporaryDirectory() as tmpdir:
        seg_files = []
        for i, seg in enumerate(segments):
            src = seg.get("source_video", "")
            if not src or not os.path.exists(src):
                log(f"  Segment source not found, skipping: {src}")
                continue
            sf = os.path.join(tmpdir, f"seg_{i:03d}.mp4")
            cmd = [
                FFMPEG,
                "-ss", str(to_seconds(seg.get("start_time", 0))),
                "-to", str(to_seconds(seg.get("end_time", 60))),
                "-i", src, "-c", "copy", sf, "-y", "-loglevel", "quiet"
            ]
            r = subprocess.run(cmd, capture_output=True)
            if r.returncode == 0 and os.path.exists(sf):
                seg_files.append(sf)

        if not seg_files:
            return False, str(output_path)

        if len(seg_files) == 1:
            import shutil
            shutil.copy2(seg_files[0], str(output_path))
            return True, str(output_path)

        # Write concat list then merge with stream copy (fast, no re-encode)
        list_path = os.path.join(tmpdir, "concat.txt")
        with open(list_path, "w") as f:
            for sf in seg_files:
                f.write(f"file '{sf}'\n")
        cmd = [
            FFMPEG, "-f", "concat", "-safe", "0",
            "-i", list_path, "-c", "copy",
            str(output_path), "-y", "-loglevel", "quiet"
        ]
        r = subprocess.run(cmd, capture_output=True)
        return r.returncode == 0, str(output_path)

# ── Routes ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    base = str(_BUNDLE) if getattr(sys, 'frozen', False) else "."
    return send_from_directory(base, "index.html")

@app.route("/api/status")
def status():
    if AI_PROVIDER == "ollama":
        key_set = True  # Ollama doesn't need an API key
        model_label = OLLAMA_MODEL
    else:
        key_set = bool(GEMINI_API_KEY)
        model_label = "Gemini"
    return jsonify({"key_set": key_set, "provider": AI_PROVIDER, "model": model_label})

@app.route("/api/set-key", methods=["POST"])
def set_api_key():
    global GEMINI_API_KEY
    data = request.json
    GEMINI_API_KEY = data.get("api_key", "")
    return jsonify({"ok": True})

@app.route("/api/scan-folder", methods=["POST"])
def scan_folder():
    data = request.json
    folder = data.get("folder", "")
    if not os.path.exists(folder):
        return jsonify({"error": "Folder not found"}), 400
    
    extensions = ["*.mp4", "*.mov", "*.avi", "*.mkv", "*.MP4", "*.MOV"]
    videos = []
    for ext in extensions:
        videos.extend(glob.glob(os.path.join(folder, ext)))
        videos.extend(glob.glob(os.path.join(folder, "**", ext), recursive=True))
    
    videos = list(set(videos))
    metas = []
    for v in videos:
        meta = get_video_metadata(v)
        metas.append(meta)
    
    metas.sort(key=lambda x: x.get("creation_time", ""))
    return jsonify({"videos": metas, "count": len(metas)})

@app.route("/api/analyze", methods=["POST"])
def analyze():
    try:
        data = request.json
        videos = data.get("videos", [])
        trip_context = data.get("trip_context", "")

        if AI_PROVIDER == "gemini" and not GEMINI_API_KEY:
            return jsonify({"error": "Gemini API key not set"}), 400

        global stop_requested
        stop_requested = False
        all_analyses = []
        video_metas = []
        analyze_progress["current"] = 0
        analyze_progress["total"] = len(videos)

        for video_path in videos:
            if stop_requested:
                log(f"Stopped early — generating plan from {len(all_analyses)} videos analysed so far...")
                break
            log(f"Extracting frames from {Path(video_path).name}...")
            frames = extract_frames(video_path)
            meta = get_video_metadata(video_path)
            video_metas.append(meta)

            if frames:
                log(f"Analyzing {Path(video_path).name} with {AI_PROVIDER}...")
                try:
                    if AI_PROVIDER == "ollama":
                        analysis = analyze_video_with_ollama(video_path, trip_context, frames)
                    else:
                        analysis = analyze_video_with_gemini(video_path, trip_context, frames)
                        time.sleep(5)  # avoid free-tier rate limits between videos
                    analysis["video"] = video_path
                    analysis["meta"] = meta
                    all_analyses.append(analysis)
                except Exception as e:
                    log(f"Error analyzing {Path(video_path).name}: {e}")
                    all_analyses.append({"video": video_path, "meta": meta, "error": str(e)})
                finally:
                    analyze_progress["current"] += 1

        log("Generating overall content plan...")
        if AI_PROVIDER == "ollama":
            plan = generate_shorts_plan_ollama(all_analyses, trip_context, video_metas)
        else:
            plan = generate_shorts_plan(all_analyses, trip_context, video_metas)

        # Resolve source_video filenames to full paths in each segment
        def _resolve_path(sv):
            for a in all_analyses:
                full_path = a.get("video", "")
                if sv == Path(full_path).name or sv in full_path or full_path.endswith(sv):
                    return full_path
            return sv  # leave as-is if not found

        for short in plan.get("shorts", []):
            if short.get("segments"):
                for seg in short["segments"]:
                    seg["source_video"] = _resolve_path(seg.get("source_video", ""))
            elif short.get("source_video"):
                # backward-compat: single-segment AI response
                resolved = _resolve_path(short["source_video"])
                short["source_video"] = resolved
                short["segments"] = [{
                    "source_video": resolved,
                    "start_time": short.get("start_time", "0:00"),
                    "end_time":   short.get("end_time",   "0:45"),
                }]

        result = {"analyses": all_analyses, "plan": plan}

        with open(OUTPUT_DIR / "analysis.json", "w") as f:
            json.dump(result, f, indent=2)

        return jsonify(result)
    except Exception as e:
        log(f"Fatal error in analyze: {e}")
        return jsonify({"error": str(e)}), 500

def to_seconds(t):
    if isinstance(t, (int, float)):
        return t
    parts = str(t).split(":")
    if len(parts) == 2:
        return int(parts[0]) * 60 + float(parts[1])
    return float(t)

@app.route("/api/cut-clip", methods=["POST"])
def cut_clip():
    try:
        data = request.json
        title = (data.get("title", "clip")).replace(" ", "_")
        output_name = f"{title}.mp4"

        # New multi-segment format
        segments = data.get("segments")
        if segments:
            success, output_path = cut_and_concat(segments, output_name)
        else:
            # Legacy single-clip format
            input_path = data.get("input_path")
            if not input_path or not os.path.exists(input_path):
                return jsonify({"error": f"Source not found: {input_path}"}), 400
            success, output_path = cut_and_concat([{
                "source_video": input_path,
                "start_time": data.get("start_time", "0"),
                "end_time":   data.get("end_time", "60"),
            }], output_name)

        if success:
            return jsonify({"ok": True, "output": output_path})
        return jsonify({"error": "FFmpeg failed — check sources exist and timestamps are valid"}), 500
    except Exception as e:
        log(f"cut-clip error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/cut-all", methods=["POST"])
def cut_all():
    try:
        data = request.json
        shorts = data.get("shorts", [])
        results = []

        for i, short in enumerate(shorts):
            title = short.get("title", f"Short_{i+1}").replace(" ", "_")[:40]
            output_name = f"Short_{i+1}_{title}.mp4"

            segments = short.get("segments") or []
            # Backward-compat: single source_video
            if not segments and short.get("source_video"):
                segments = [{
                    "source_video": short["source_video"],
                    "start_time":   short.get("start_time", "0"),
                    "end_time":     short.get("end_time", "60"),
                }]

            seg_names = ", ".join(Path(s.get("source_video","")).name for s in segments)
            log(f"Stitching Short {i+1}: {seg_names}")
            success, path = cut_and_concat(segments, output_name)
            results.append({"title": short.get("title"), "ok": success, "path": path,
                            "segments": len(segments)})

        return jsonify({"results": results})
    except Exception as e:
        log(f"cut-all error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/progress")
def get_progress():
    with progress_lock:
        logs = list(progress_log)
    return jsonify({"logs": logs, "current": analyze_progress["current"], "total": analyze_progress["total"]})

@app.route("/api/stop-analyze", methods=["POST"])
def stop_analyze():
    global stop_requested
    stop_requested = True
    log("Stop requested — will finish current video then generate plan...")
    return jsonify({"ok": True})

@app.route("/output/<path:filename>")
def serve_output(filename):
    return send_from_directory(OUTPUT_DIR, filename)

# ── Settings ─────────────────────────────────────────────────────────────────

@app.route("/api/settings")
def get_settings():
    return jsonify({
        "ai_provider":    AI_PROVIDER,
        "ollama_model":   OLLAMA_MODEL,
        "ollama_host":    OLLAMA_HOST,
        "gemini_key_set": bool(GEMINI_API_KEY),
        "minnal_key_set": bool(MINNAL_API_KEY),
    })

@app.route("/api/settings", methods=["POST"])
def save_settings():
    global GEMINI_API_KEY, AI_PROVIDER, OLLAMA_MODEL, OLLAMA_HOST, MINNAL_API_KEY, FFMPEG, FFPROBE
    data = request.json or {}

    def _set(key, val):
        if val is not None:
            dotenv_set_key(str(_ENV_FILE), key, str(val))
            os.environ[key] = str(val)

    if "ai_provider" in data:
        AI_PROVIDER = data["ai_provider"]
        _set("AI_PROVIDER", AI_PROVIDER)
    if "gemini_api_key" in data and data["gemini_api_key"]:
        GEMINI_API_KEY = data["gemini_api_key"]
        _set("GEMINI_API_KEY", GEMINI_API_KEY)
    if "ollama_model" in data:
        OLLAMA_MODEL = data["ollama_model"]
        _set("OLLAMA_MODEL", OLLAMA_MODEL)
    if "ollama_host" in data:
        OLLAMA_HOST = data["ollama_host"]
        _set("OLLAMA_HOST", OLLAMA_HOST)
    if "minnal_api_key" in data:
        MINNAL_API_KEY = data["minnal_api_key"]
        _set("MINNAL_API_KEY", MINNAL_API_KEY)

    return jsonify({"ok": True})

@app.route("/api/test-ollama", methods=["POST"])
def test_ollama():
    data = request.json or {}
    host  = data.get("host", OLLAMA_HOST)
    model = data.get("model", OLLAMA_MODEL)
    try:
        client = ollama_client.Client(host=host)
        # list() is a lightweight ping — no GPU needed
        models = client.list()
        names  = [m.model for m in (models.models or [])]
        has_model = any(model.split(":")[0] in n for n in names)
        return jsonify({"ok": True, "models": names, "model_found": has_model})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 200  # 200 so JS can read the body

# ── Minnal integration ───────────────────────────────────────────────────────

def minnal_request(method, path, body=None, api_key=None):
    key = api_key or MINNAL_API_KEY
    url = f"{MINNAL_BASE}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {key}")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

@app.route("/api/minnal/brands")
def minnal_brands():
    api_key = request.headers.get("X-Minnal-Key") or MINNAL_API_KEY
    if not api_key:
        return jsonify({"error": "Minnal API key not set"}), 400
    try:
        brands = minnal_request("GET", "/api/brands", api_key=api_key)
        return jsonify(brands)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/minnal/schedule", methods=["POST"])
def minnal_schedule():
    api_key = request.headers.get("X-Minnal-Key") or MINNAL_API_KEY
    if not api_key:
        return jsonify({"error": "Minnal API key not set"}), 400
    try:
        result = minnal_request("POST", "/api/posts/schedule", body=request.json, api_key=api_key)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = 5000
    print(f"Travel Shorts AI — http://localhost:{port}")
    threading.Timer(1.5, lambda: webbrowser.open(f"http://localhost:{port}")).start()
    app.run(debug=False, port=port)
