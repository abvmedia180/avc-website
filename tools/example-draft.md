---
slug: lawat31
number: "01"
title: Law at 31
date: April 2026
excerpt: Reflections on starting law school in my thirties.
---

This is where you write your letter. Just write naturally.

Paragraphs are separated by a blank line, like this. You don't need to think about HTML — the script handles all of that for you.

You can **bold** things you want to emphasize, or use *italics* for a lighter touch. Links work like this: [alphaventurecapital.vc](https://alphaventurecapital.vc).

> Pull quotes look beautiful. Use them for the single line you want readers to remember.

## Use section headings when the letter gets long

Headings break the letter into sections. Use them sparingly — one or two per letter is usually enough.

When you're ready to publish, just run:

```
uv run tools/new_letter.py tools/your-draft.md
```

The script will:

1. Generate the styled HTML page at `/lawat31/`
2. Add an entry to the letters index at `/letters`
3. Update `robots.txt` so Google doesn't index it
4. Print the URLs and git commands

Then you commit and push, and the letter is live.
