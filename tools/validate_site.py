#!/usr/bin/env python3
"""Validate the assembled static site."""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote


ROOT = Path(__file__).resolve().parents[1]
SITE_ROOT = ROOT / "_site"
ARTICLE_INDEX = ROOT / "interactive" / "article-index.json"
REDIRECT_OVERRIDES = ROOT / "redirects" / "legacy-overrides.json"


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        for attr in ("href", "src"):
            if attr in values and values[attr]:
                self.links.append((attr, values[attr] or ""))


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def normalize_path(value: str) -> str:
    if not value.startswith("/"):
        value = "/" + value
    return value if value.endswith("/") else value + "/"


def article_entries() -> list[dict[str, object]]:
    raw = json.loads(ARTICLE_INDEX.read_text(encoding="utf-8"))
    return list(raw["articles"])


def redirect_overrides() -> dict[str, str]:
    raw = json.loads(REDIRECT_OVERRIDES.read_text(encoding="utf-8"))
    return {normalize_path(source): normalize_path(target) for source, target in raw.items()}


def resolve_target(link: str, page: Path) -> Path | None:
    if not link or link.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
        return None
    parsed = urlsplit(link)
    if parsed.scheme or parsed.netloc:
        return None
    path = unquote(parsed.path)
    if not path:
        return None
    if path.startswith("/"):
        candidate = SITE_ROOT / path.lstrip("/")
    else:
        candidate = page.parent / path
    if path.endswith("/") or candidate.is_dir():
        return candidate / "index.html"
    return candidate


def validate_internal_links(errors: list[str]) -> None:
    for page in SITE_ROOT.rglob("*.html"):
        if not page.is_file():
            continue
        if "classic" in page.relative_to(SITE_ROOT).parts:
            continue
        parser = LinkParser()
        parser.feed(page.read_text(encoding="utf-8", errors="ignore"))
        for attr, link in parser.links:
            target = resolve_target(link, page)
            if target is not None and not target.exists():
                errors.append(f"{page.relative_to(SITE_ROOT)} has broken {attr}: {link}")


def validate_site() -> list[str]:
    errors: list[str] = []
    root_index = SITE_ROOT / "index.html"
    classic_index = SITE_ROOT / "classic" / "index.html"
    require(root_index.is_file(), "Root index.html is missing.", errors)
    require(classic_index.is_file(), "Classic index.html is missing.", errors)
    require((SITE_ROOT / "assets" / "interactive-article.css").is_file(), "Interactive CSS is missing.", errors)
    require((SITE_ROOT / "assets" / "interactive-article.js").is_file(), "Interactive JS is missing.", errors)
    if (SITE_ROOT / "classic" / "feed.xml").is_file():
        require((SITE_ROOT / "feed.xml").is_file(), "Legacy root feed.xml is missing.", errors)
    if root_index.is_file():
        root_html = root_index.read_text(encoding="utf-8")
        require("ia-index-page" in root_html, "Root index is not the interactive index.", errors)
        require("/new/" not in root_html, "Root index still links to /new/.", errors)

    for article in article_entries():
        year = str(article["year"])
        slug = str(article["slug"])
        expected_url = f"/{year}/{slug}/"
        require(article["url"] == expected_url, f"{slug}: article-index URL must be {expected_url}.", errors)
        article_dir = SITE_ROOT / year / slug
        for filename in ("index.html", "source.md", "caveman.md"):
            file_path = article_dir / filename
            require(file_path.is_file(), f"{slug}: {filename} is missing.", errors)
            if file_path.is_file():
                require("/new/" not in file_path.read_text(encoding="utf-8"), f"{slug}: {filename} still contains /new/.", errors)

    overrides = redirect_overrides()
    for source, target in overrides.items():
        redirect_file = SITE_ROOT / source.strip("/") / "index.html"
        require(redirect_file.is_file(), f"Redirect {source} is missing.", errors)
        require((SITE_ROOT / target.strip("/") / "index.html").is_file(), f"Redirect target {target} is missing.", errors)
        if redirect_file.is_file():
            html_text = redirect_file.read_text(encoding="utf-8")
            require(target in html_text, f"Redirect {source} does not point to {target}.", errors)

    for classic_post in (SITE_ROOT / "classic" / "post").rglob("index.html"):
        source = "/" + classic_post.relative_to(SITE_ROOT / "classic").parent.as_posix() + "/"
        redirect_file = SITE_ROOT / source.strip("/") / "index.html"
        require(redirect_file.is_file(), f"Classic post redirect {source} is missing.", errors)

    validate_internal_links(errors)

    new_references = []
    for file_path in SITE_ROOT.rglob("*"):
        if file_path.is_file() and "classic" not in file_path.relative_to(SITE_ROOT).parts:
            try:
                if re.search(r"/new/", file_path.read_text(encoding="utf-8", errors="ignore")):
                    new_references.append(str(file_path.relative_to(SITE_ROOT)))
            except UnicodeDecodeError:
                continue
    require(not new_references, "Root output still contains /new/: " + ", ".join(new_references[:10]), errors)
    return errors


def main() -> int:
    errors = validate_site()
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    print("Static site validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
