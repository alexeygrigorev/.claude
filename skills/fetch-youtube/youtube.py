#!/usr/bin/env python3
"""Fetch YouTube video transcripts as timestamped subtitles."""

import re
import sys
from pathlib import Path

from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url_or_id: str) -> str:
    """Extract YouTube video ID from a URL or return as-is if already an ID."""
    patterns = [
        r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})",
        r"^([a-zA-Z0-9_-]{11})$",
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    return url_or_id


def format_timestamp(seconds: float) -> str:
    """Convert seconds to H:MM:SS if > 1 hour, else M:SS."""
    total_seconds = int(seconds)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)

    if hours > 0:
        return f"{hours}:{minutes:02}:{secs:02}"
    else:
        return f"{minutes}:{secs:02}"


def make_subtitles(transcript) -> str:
    """Format transcript entries into timestamped subtitle text."""
    lines = []
    for entry in transcript:
        ts = format_timestamp(entry.start)
        text = entry.text.replace("\n", " ")
        lines.append(ts + " " + text)
    return "\n".join(lines)


def fetch_transcript_raw(video_id):
    """Fetch raw transcript data from YouTube."""
    ytt_api = YouTubeTranscriptApi()
    transcript = ytt_api.fetch(video_id)
    return transcript


def fetch_transcript_text(video_id):
    """Fetch transcript and return as formatted subtitle text."""
    transcript = fetch_transcript_raw(video_id)
    subtitles = make_subtitles(transcript)
    return subtitles


def fetch_transcript_cached(video_id, cache_dir=None):
    """Fetch transcript with local file caching."""
    if cache_dir is None:
        cache_dir = Path.home() / ".cache" / "youtube_transcripts"
    else:
        cache_dir = Path(cache_dir)

    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / f"{video_id}.txt"

    if cache_file.exists():
        return cache_file.read_text(encoding="utf-8")

    subtitles = fetch_transcript_text(video_id)
    cache_file.write_text(subtitles, encoding="utf-8")

    return subtitles


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python youtube.py <video-url-or-id>", file=sys.stderr)
        sys.exit(1)

    video_id = extract_video_id(sys.argv[1])
    print(fetch_transcript_cached(video_id))
