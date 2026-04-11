# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "markdown>=3.5",
#   "python-frontmatter>=1.1",
# ]
# ///
"""
Generate a new Alpha Venture Capital letter from a markdown file.

Usage:
    uv run tools/new_letter.py path/to/draft.md

Markdown frontmatter format (YAML):
---
slug: lawat31
number: "01"
title: Law at 31
date: April 2026
excerpt: A short one-line teaser for the index page.
---

# Your letter content here

Write in normal markdown. Bold, italic, links, blockquotes, headings all work.
"""

import sys
import re
from pathlib import Path

import frontmatter
import markdown as md

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = REPO_ROOT / "tools" / "letter-template.html"
INDEX = REPO_ROOT / "letters" / "index.html"
ROBOTS = REPO_ROOT / "robots.txt"


def render_letter(draft_path: Path) -> dict:
    post = frontmatter.load(draft_path)
    required = ["slug", "number", "title", "date", "excerpt"]
    missing = [k for k in required if k not in post.metadata]
    if missing:
        sys.exit(f"ERROR: missing frontmatter keys: {missing}")

    meta = post.metadata
    body_html = md.markdown(
        post.content,
        extensions=["extra", "sane_lists", "smarty"],
    )

    template = TEMPLATE.read_text()
    page = (
        template.replace("{{TITLE}}", meta["title"])
        .replace("{{NUMBER}}", str(meta["number"]))
        .replace("{{DATE}}", meta["date"])
        .replace("{{DESCRIPTION}}", meta.get("excerpt", ""))
        .replace("{{BODY}}", body_html)
    )

    out_dir = REPO_ROOT / meta["slug"]
    out_dir.mkdir(exist_ok=True)
    (out_dir / "index.html").write_text(page)
    print(f"  wrote {out_dir.relative_to(REPO_ROOT)}/index.html")

    return meta


def update_index(meta: dict) -> None:
    """Insert or replace this letter's entry in /letters/index.html (newest first)."""
    index_html = INDEX.read_text()
    start = "<!-- LETTERS-LIST-START -->"
    end = "<!-- LETTERS-LIST-END -->"
    assert start in index_html and end in index_html, "index markers not found"

    i = index_html.index(start) + len(start)
    j = index_html.index(end)
    block = index_html[i:j]

    entry_html = (
        f'    <a href="/{meta["slug"]}" class="letter-entry">\n'
        f'      <div class="letter-entry-meta">Letter {meta["number"]} · {meta["date"]}</div>\n'
        f'      <div class="letter-entry-title">{meta["title"]}</div>\n'
        f'      <div class="letter-entry-excerpt">{meta["excerpt"]}</div>\n'
        f'    </a>'
    )

    existing_pattern = re.compile(
        rf'\s*<a href="/{re.escape(meta["slug"])}"[^>]*class="letter-entry">.*?</a>',
        re.DOTALL,
    )

    if existing_pattern.search(block):
        new_block = existing_pattern.sub(f"\n{entry_html}", block)
    else:
        list_open = '<div class="letters-list">'
        if list_open in block:
            new_block = block.replace(list_open, f"{list_open}\n{entry_html}")
        else:
            new_block = f'\n  <div class="letters-list">\n{entry_html}\n  </div>\n  '

    new_index = index_html[: i] + new_block + index_html[j:]
    INDEX.write_text(new_index)
    print(f"  updated letters/index.html")


def update_robots(slug: str) -> None:
    """Ensure the slug is listed in robots.txt."""
    line = f"Disallow: /{slug}/"
    content = ROBOTS.read_text()
    if line in content:
        return
    content = content.rstrip() + f"\n{line}\n"
    ROBOTS.write_text(content)
    print(f"  updated robots.txt")


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Usage: uv run tools/new_letter.py path/to/draft.md")
    draft = Path(sys.argv[1])
    if not draft.exists():
        sys.exit(f"ERROR: {draft} not found")

    print(f"Publishing letter from {draft}...")
    meta = render_letter(draft)
    update_index(meta)
    update_robots(meta["slug"])
    print(f"\n✓ Letter '{meta['title']}' published at /{meta['slug']}")
    print(f"  View at: https://alphaventurecapital.vc/{meta['slug']}")
    print(f"  Archive: https://alphaventurecapital.vc/letters")
    print(f"\nNext: git add -A && git commit -m 'Add letter: {meta['title']}' && git push")


if __name__ == "__main__":
    main()
