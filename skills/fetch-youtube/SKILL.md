---
name: fetch-youtube
description: Fetch YouTube video transcripts. Use when the user asks to get a YouTube video transcript, subtitles, or captions, or wants to analyze/summarize a YouTube video.
allowed-tools: Bash(python *), Bash(pip install *)
argument-hint: [video-url-or-id]
---

# Fetch YouTube Transcript

Fetch the transcript/subtitles of a YouTube video and return it as timestamped text.

## Requirements

Ensure `youtube-transcript-api` is installed:

```bash
pip install youtube-transcript-api
```

## Usage

Run the fetch script with a YouTube video ID or URL:

```bash
python ~/.claude/skills/fetch-youtube/youtube.py <video-id-or-url>
```

The script accepts either:
- A video ID: `dQw4w9WgXcQ`
- A full URL: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
- A short URL: `https://youtu.be/dQw4w9WgXcQ`

## Output

The script prints the transcript as timestamped subtitles to stdout:

```
0:00 Hello and welcome
0:05 Today we're going to talk about...
1:23:45 And that wraps up our discussion
```

## What to do with the output

After fetching the transcript, ask the user what they'd like to do with it. Common tasks:
- Summarize the video
- Extract key points or action items
- Answer questions about the video content
- Search for specific topics mentioned
- Create notes from the video
