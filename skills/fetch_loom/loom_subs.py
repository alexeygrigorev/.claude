#!/usr/bin/env python3
"""Download subtitles from a Loom video and save to .tmp/ folder."""

import os
import re
import sys
import urllib.request


def fetch_page(video_url: str) -> str:
    """Fetch the Loom share page HTML."""
    req = urllib.request.Request(video_url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req).read().decode()


def get_title(html: str) -> str | None:
    """Extract video title from page HTML."""
    match = re.search(r'<title>([^<]+)</title>', html)
    if not match:
        return None
    title = match.group(1)
    title = re.sub(r"\s*\|\s*Loom\s*$", "", title)
    return title.strip()


def get_video_id(url: str) -> str:
    """Extract video ID from a Loom URL."""
    match = re.search(r'([0-9a-f]{32})', url)
    if match:
        return match.group(1)
    return url.rstrip('/').split('/')[-1]


def get_vtt_url(html: str) -> str:
    """Extract signed VTT captions URL from page HTML."""
    match = re.search(r'https://cdn\.loom\.com/mediametadata/captions/[^"]+', html)
    if not match:
        raise ValueError("No captions URL found. The video may not have subtitles.")
    return match.group(0).replace("&amp;", "&")


def parse_vtt(vtt_text: str) -> list[tuple[str, str]]:
    """Parse VTT into list of (timestamp, text) tuples."""
    vtt_text = vtt_text.replace("\r\n", "\n")
    cues = []
    for block in re.split(r"\n\n+", vtt_text):
        ts_match = re.search(r"(\d+):(\d+):(\d+)\.\d+\s+-->", block)
        if not ts_match:
            continue
        h, m, s = int(ts_match.group(1)), int(ts_match.group(2)), int(ts_match.group(3))
        timestamp = f"{h * 60 + m:02d}:{s:02d}"
        lines = block.strip().split("\n")
        text_lines = [l for l in lines if "-->" not in l and not l.strip().isdigit()]
        text = " ".join(text_lines)
        text = re.sub(r"<[^>]+>", "", text)
        cues.append((timestamp, text))
    return cues


def clean_fillers(text: str) -> str:
    """Remove filler words (uh, um) and clean up punctuation/spacing."""
    text = re.sub(r"\b[Uu][hm]\b,?\s*", "", text)
    text = re.sub(r"\s{2,}", " ", text)
    text = re.sub(r"\s+([.,!?])", r"\1", text)
    text = re.sub(r"^[,.\s]+", "", text)
    return text.strip()


def to_share_url(arg: str) -> str:
    """Accept a full Loom URL or just a video ID."""
    if arg.startswith("http"):
        return arg
    return f"https://www.loom.com/share/{arg}"


def slugify(title: str) -> str:
    """Convert title to a filesystem-safe slug."""
    slug = title.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <loom-url-or-video-id>")
        sys.exit(1)

    video_url = to_share_url(sys.argv[1])
    video_id = get_video_id(video_url)
    html = fetch_page(video_url)

    title = get_title(html)

    vtt_url = get_vtt_url(html)
    req = urllib.request.Request(vtt_url, headers={"User-Agent": "Mozilla/5.0"})
    vtt_text = urllib.request.urlopen(req).read().decode()

    lines = []
    if title:
        lines.append(title)
        lines.append("")

    for timestamp, text in parse_vtt(vtt_text):
        cleaned = clean_fillers(text)
        if cleaned:
            lines.append(f"{timestamp} {cleaned}")

    transcript = "\n".join(lines) + "\n"

    # Save to .tmp/ folder
    os.makedirs(".tmp", exist_ok=True)
    if title:
        filename = f"{slugify(title)}.txt"
    else:
        filename = f"{video_id}.txt"
    output_path = os.path.join(".tmp", filename)

    with open(output_path, "w") as f:
        f.write(transcript)

    print(f"Saved transcript to {output_path}")
    # Also print to stdout for piping
    print()
    print(transcript, end="")


if __name__ == "__main__":
    main()
