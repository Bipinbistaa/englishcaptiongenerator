# AI-Powered Automatic English Video Caption Generator

## 1. Project Overview

Streamlit web app. Take English-speaking video, auto-generate English
subtitles, burn them into video. Output: playable captioned MP4 plus
optional SRT file.

## 2. Problem Statement

Manual captioning slow, tedious, needs listening + typing + timing
every line by hand. Accessibility and content reach suffer when
captions missing.

## 3. Proposed Solution

AI pipeline: speech recognition (Faster-Whisper) converts speech to
timestamped text. NLP cleans and segments text into readable caption
lines. Subtitle generator builds valid SRT. FFmpeg burns captions
directly into video frames — no external subtitle file needed to
view captions.

## 4. Objectives

- Automatic speech recognition (English)
- NLP-based text cleaning and caption segmentation
- Automatic timestamped subtitle (SRT) generation
- Automatic caption burning into video (FFmpeg)
- Final captioned MP4 as primary deliverable

## 5. AI Technologies

**Speech Recognition** — Faster-Whisper transcribes English speech to
text with segment-level timestamps.

**NLP** — Cleans whitespace/punctuation, splits transcript into
caption-sized lines (≤ ~42 chars/line, ≤ 2 lines/caption) without
rewriting meaning.

**Subtitle Generation** — Converts processed segments into valid,
correctly numbered, non-overlapping `.srt` (optionally `.vtt`).

**Video Processing** — FFmpeg burns subtitles into video via the
`subtitles` filter, re-encoding video (H.264) while preserving audio,
duration, and aspect ratio.

## 6. System Architecture

```text
English Video
      |
      v
Video Validation (extension, size, audio track check)
      |
      v
Audio Extraction (FFmpeg -> 16kHz mono WAV)
      |
      v
Speech Recognition (Faster-Whisper -> timestamped segments)
      |
      v
NLP Processing (clean + segment into caption lines)
      |
      v
Subtitle Generation (.srt)
      |
      v
Caption Burning (FFmpeg subtitles filter)
      |
      v
captioned_video.mp4  (primary output)
captions.srt          (secondary output)
```

## 7. Installation

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

## 8. FFmpeg Installation

**macOS**
```bash
brew install ffmpeg
```

**Windows**
1. Download build from https://www.gyan.dev/ffmpeg/builds/
2. Extract, add the `bin` folder to your `PATH`.
3. Verify: `ffmpeg -version`

**Ubuntu / Linux**
```bash
sudo apt update
sudo apt install ffmpeg
```

## 9. Running the Application

```bash
streamlit run app.py
```

## 10. Usage

```text
Upload Video
   -> Generate Captions
      -> Speech Recognition
         -> NLP Processing
            -> Subtitle Generation
               -> FFmpeg Caption Burning
                  -> Preview Final Video
                     -> Download Captioned MP4 / SRT
```

## 11. Supported Input

English-speaking videos: `.mp4`, `.mov`, `.mkv`, `.avi`, `.webm`.

## 12. Output

English-captioned MP4 video (captions burned into frames), plus
optional `.srt` file.

## 13. Limitations

- Background noise reduces transcription accuracy.
- Multiple overlapping speakers hard to distinguish (no diarization).
- Strong accents can affect transcription quality.
- Long videos take longer to process (CPU-bound by default).
- Whisper timestamps are segment-level, not exact word-level alignment.

## 14. Future Improvements

- Speaker diarization
- Word-level timestamps
- Real-time captioning
- Multiple language support
- YouTube URL input
- Better punctuation restoration
- Custom caption styles (fonts/colors from UI)
- Cloud deployment
- GPU acceleration

## Project Structure

```text
english-caption-generator/
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
├── config/settings.py
├── services/
│   ├── video_service.py
│   ├── audio_service.py
│   ├── transcription_service.py
│   ├── nlp_service.py
│   ├── subtitle_service.py
│   └── caption_video_service.py
├── utils/
│   ├── file_utils.py
│   ├── time_utils.py
│   └── cleanup.py
├── models/schemas.py
├── outputs/
├── temp/
└── tests/
    ├── test_subtitles.py
    ├── test_time_utils.py
    └── test_nlp.py
```

## Configuration (.env)

```env
WHISPER_MODEL=small     # tiny | base | small | medium
DEVICE=cpu
COMPUTE_TYPE=int8
MAX_VIDEO_SIZE_MB=200
```

Whisper model auto-caches via `@st.cache_resource` — loaded once per
app session, not per video.

## Testing

```bash
pytest tests/ -v
```

Covers: time conversion, SRT generation (numbering, timestamps,
empty/long segments), NLP cleanup + line splitting, and caption
segment ordering.

## Scope Note

English-caption-only project. No translation, no Nepali language
support, no database, no auth — kept simple and runnable on a normal
laptop, as intended for a capstone submission.

## Demo Workflow (for presentation)

1. Upload short English video (30–60s works well for a live demo).
2. Click "Generate English Captions" — watch progress indicators.
3. Show transcript + SRT preview panels.
4. Play final captioned video — captions visible burned into frame.
5. Download both captioned MP4 and SRT.
6. Explain each pipeline stage using the architecture diagram above.
