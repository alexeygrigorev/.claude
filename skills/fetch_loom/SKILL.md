---
name: fetch-loom
description: Download Loom video transcripts and video files. Use when the user shares a Loom URL and wants to get the transcript or download the video.
---

# Fetch Loom

Download transcripts and videos from Loom URLs.

## Subtitles / Transcript

```bash
python3 ~/.claude/skills/fetch_loom/loom_subs.py <loom-url-or-video-id>
```

Outputs a timestamped transcript (mm:ss format) with filler words removed. Saves to `.tmp/` in the current directory.

## Video Download

```bash
python3 ~/.claude/skills/fetch_loom/loom_download.py <loom-url-or-video-id>
```

Downloads the video as mp4 using yt-dlp. Saves to `.tmp/` in the current directory.

Requires `yt-dlp` to be installed.

## Notes

- Both scripts accept a full Loom URL or just the video ID
- Files are saved to `.tmp/` in the current working directory
- Filenames are derived from the video title (slugified)
