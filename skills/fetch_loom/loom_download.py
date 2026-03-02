#!/usr/bin/env python3
"""Download a Loom video to .tmp/ folder using yt-dlp."""

import os
import re
import shutil
import subprocess
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


def slugify(title: str) -> str:
    """Convert title to a filesystem-safe slug."""
    slug = title.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')


def to_share_url(arg: str) -> str:
    """Accept a full Loom URL or just a video ID."""
    if arg.startswith("http"):
        return arg
    return f"https://www.loom.com/share/{arg}"


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <loom-url-or-video-id>")
        sys.exit(1)

    yt_dlp = shutil.which("yt-dlp")
    if not yt_dlp:
        print("Error: yt-dlp is required but not found. Install it with: pip install yt-dlp")
        sys.exit(1)

    video_url = to_share_url(sys.argv[1])
    video_id = get_video_id(video_url)

    # Get title for filename
    try:
        html = fetch_page(video_url)
        title = get_title(html)
    except Exception:
        title = None

    os.makedirs(".tmp", exist_ok=True)

    if title:
        filename = f"{slugify(title)}.mp4"
    else:
        filename = f"{video_id}.mp4"

    output_path = os.path.join(".tmp", filename)

    print(f"Downloading: {title or video_id}")
    print(f"Saving to: {output_path}")

    result = subprocess.run(
        [
            yt_dlp,
            "--no-warnings",
            "-o", output_path,
            video_url,
        ],
        capture_output=False,
    )

    if result.returncode != 0:
        print(f"Error: yt-dlp exited with code {result.returncode}")
        sys.exit(1)

    if os.path.exists(output_path):
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"Done: {output_path} ({size_mb:.1f} MB)")
    else:
        print(f"Warning: Expected file {output_path} not found")
        # yt-dlp might have added an extension
        for f in os.listdir(".tmp"):
            if f.startswith(slugify(title) if title else video_id):
                actual_path = os.path.join(".tmp", f)
                size_mb = os.path.getsize(actual_path) / (1024 * 1024)
                print(f"Found: {actual_path} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
