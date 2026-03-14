---
name: jina-reader
description: Fetch clean, readable content from any URL using Jina Reader. Use when the user wants to read, summarize, or analyze a web page, article, or blog post.
allowed-tools: Bash(curl *)
argument-hint: <url>
---

# Jina Reader

Fetch clean, readable content from any URL using [Jina Reader](https://r.jina.ai/).

## Usage

```bash
curl -sL "https://r.jina.ai/<url>"
```

For example:

```bash
curl -sL "https://r.jina.ai/https://example.com/article"
```

## Notes

- Works with most web pages, articles, and blog posts
- Returns clean markdown-formatted content stripped of navigation, ads, and other clutter
- Do NOT use for GitHub URLs — use `gh` CLI or raw.githubusercontent.com instead
- If Jina Reader fails for a specific URL, fall back to WebFetch

## What to do with the output

After fetching the content, ask the user what they'd like to do with it. Common tasks:
- Summarize the article
- Extract key points or action items
- Answer questions about the content
- Compare with other articles
