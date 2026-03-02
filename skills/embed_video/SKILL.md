# Embed Video

Embed YouTube or Loom videos in Jekyll markdown pages.

## YouTube

```html
<iframe width="560" height="315" src="https://www.youtube.com/embed/VIDEO_ID" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
```

Extract VIDEO_ID from YouTube URLs:

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`

## Loom

```html
<div style="position: relative; padding-bottom: 56.25%; height: 0;">
  <iframe src="https://www.loom.com/embed/VIDEO_ID" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"></iframe>
</div>
```

Extract VIDEO_ID from Loom URLs:

- `https://www.loom.com/share/VIDEO_ID`

The wrapping div with `padding-bottom: 56.25%` makes the embed responsive (16:9 aspect ratio).

## Placement

Place the embed right after the page title or section heading, before the main text content.
