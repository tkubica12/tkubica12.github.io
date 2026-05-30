#!/usr/bin/env python3
"""Validate the assembled static site."""

from __future__ import annotations

import json
import hashlib
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote


ROOT = Path(__file__).resolve().parents[1]
SITE_ROOT = ROOT / "_site"
ARTICLE_INDEX = ROOT / "interactive" / "article-index.json"
ARTICLE_INDEX_EN = ROOT / "interactive" / "article-index.en.json"
SOURCE_ROOT = ROOT / "interactive" / "source"
REDIRECT_OVERRIDES = ROOT / "redirects" / "legacy-overrides.json"
SITE_URL = "https://tomaskubica.cz"
ATOM_NS = "http://www.w3.org/2005/Atom"


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


def article_entries(index_path: Path = ARTICLE_INDEX) -> list[dict[str, object]]:
    raw = json.loads(index_path.read_text(encoding="utf-8"))
    return list(raw["articles"])


def optional_article_entries(index_path: Path) -> list[dict[str, object]]:
    if not index_path.is_file():
        return []
    return article_entries(index_path)


def source_hash(slug: str) -> str:
    for candidate in SOURCE_ROOT.glob(f"*/{slug}.article.md"):
        return hashlib.sha256(candidate.read_bytes()).hexdigest()
    return ""


def redirect_overrides() -> dict[str, str]:
    raw = json.loads(REDIRECT_OVERRIDES.read_text(encoding="utf-8"))
    return {normalize_path(source): normalize_path(target) for source, target in raw.items()}


def atom_tag(name: str) -> str:
    return f"{{{ATOM_NS}}}{name}"


def root_feed_refs(errors: list[str]) -> set[str]:
    feed_path = SITE_ROOT / "feed.xml"
    require(feed_path.is_file(), "Root feed.xml is missing.", errors)
    if not feed_path.is_file():
        return set()
    try:
        root = ET.parse(feed_path).getroot()
    except ET.ParseError as exc:
        errors.append(f"Root feed.xml is not valid XML: {exc}")
        return set()

    refs: set[str] = set()
    for entry in root.findall(atom_tag("entry")):
        entry_id = entry.find(atom_tag("id"))
        if entry_id is not None and entry_id.text:
            refs.add(entry_id.text.strip())
        for link in entry.findall(atom_tag("link")):
            href = link.attrib.get("href")
            if href:
                refs.add(href)
    return refs


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


def validate_english_layer(cs_articles: list[dict[str, object]], errors: list[str]) -> None:
    en_articles = optional_article_entries(ARTICLE_INDEX_EN)
    require(not (SITE_ROOT / "classic" / "en").exists(), "Classic output must not contain an en layer.", errors)
    if not en_articles:
        require(not (SITE_ROOT / "en").exists(), "_site\\en exists without interactive\\article-index.en.json.", errors)
        return

    en_index = SITE_ROOT / "en" / "index.html"
    en_search = SITE_ROOT / "en" / "search.json"
    require(en_index.is_file(), "English index.html is missing.", errors)
    require(en_search.is_file(), "English search.json is missing.", errors)
    if en_index.is_file():
        en_index_html = en_index.read_text(encoding="utf-8")
        require('html lang="en"' in en_index_html, "English index must use lang=\"en\".", errors)
        require('href="../"' in en_index_html, "English index must link back to the Czech root.", errors)

    cs_by_slug = {str(article["slug"]): article for article in cs_articles}
    en_by_source = {str(article.get("source_slug") or article["slug"]): article for article in en_articles}

    if en_search.is_file():
        payload = json.loads(en_search.read_text(encoding="utf-8"))
        urls = {str(item.get("url")) for item in payload}
        expected_urls = {f'{article["year"]}/{article["slug"]}/' for article in en_articles}
        require(urls == expected_urls, "English search.json must contain only translated English entries.", errors)

    for article in en_articles:
        year = str(article["year"])
        slug = str(article["slug"])
        source_slug = str(article.get("source_slug") or slug)
        expected_url = f"/en/{year}/{slug}/"
        require(article["url"] == expected_url, f"{slug}: English article URL must be {expected_url}.", errors)
        require(source_slug in cs_by_slug, f"{slug}: English source_slug {source_slug} has no Czech article.", errors)

        article_dir = SITE_ROOT / "en" / year / slug
        for filename in ("index.html", "source.md", "caveman.md"):
            require((article_dir / filename).is_file(), f"{slug}: English {filename} is missing.", errors)

        html_path = article_dir / "index.html"
        if not html_path.is_file():
            continue
        html_text = html_path.read_text(encoding="utf-8")
        require('html lang="en"' in html_text, f"{slug}: English article must use lang=\"en\".", errors)
        require("ia-translation-notice" in html_text, f"{slug}: English article is missing the machine translation notice.", errors)
        require('hreflang="en"' in html_text, f"{slug}: English article is missing hreflang=en.", errors)
        require('hreflang="cs-CZ"' in html_text, f"{slug}: English article is missing hreflang=cs-CZ.", errors)
        require('hreflang="x-default"' in html_text, f"{slug}: English article is missing hreflang=x-default.", errors)
        if source_slug in cs_by_slug:
            source_article = cs_by_slug[source_slug]
            source_href = f'../../../{source_article["year"]}/{source_article["slug"]}/'
            require(source_href in html_text, f"{slug}: English article must link to the Czech original.", errors)
        if source_hash(source_slug) and str(article.get("translated_from_hash", "")) != source_hash(source_slug):
            require(
                "Czech original has changed since this translation was generated" in html_text,
                f"{slug}: stale English translation must show the stale-translation notice.",
                errors,
            )

    for source_slug, article in en_by_source.items():
        cs_article = cs_by_slug.get(source_slug)
        if not cs_article:
            continue
        cs_path = SITE_ROOT / str(cs_article["year"]) / str(cs_article["slug"]) / "index.html"
        if cs_path.is_file():
            cs_html = cs_path.read_text(encoding="utf-8")
            expected_href = f'../../en/{article["year"]}/{article["slug"]}/'
            require(expected_href in cs_html, f"{source_slug}: Czech article must link to the English translation.", errors)
            require('hreflang="en"' in cs_html, f"{source_slug}: Czech article is missing hreflang=en.", errors)


def validate_site() -> list[str]:
    errors: list[str] = []
    cs_articles = article_entries()
    root_index = SITE_ROOT / "index.html"
    classic_index = SITE_ROOT / "classic" / "index.html"
    require(root_index.is_file(), "Root index.html is missing.", errors)
    require(classic_index.is_file(), "Classic index.html is missing.", errors)
    require((SITE_ROOT / "assets" / "interactive-article.css").is_file(), "Interactive CSS is missing.", errors)
    require((SITE_ROOT / "assets" / "interactive-article.js").is_file(), "Interactive JS is missing.", errors)
    feed_refs = root_feed_refs(errors)
    if classic_index.is_file():
        require((SITE_ROOT / "classic" / "feed.xml").is_file(), "Classic feed.xml is missing.", errors)
    if root_index.is_file():
        root_html = root_index.read_text(encoding="utf-8")
        require("ia-index-page" in root_html, "Root index is not the interactive index.", errors)
        require("/new/" not in root_html, "Root index still links to /new/.", errors)
        require('href="feed.xml"' in root_html, "Root index does not link to the canonical feed.xml.", errors)

    for article in cs_articles:
        year = str(article["year"])
        slug = str(article["slug"])
        expected_url = f"/{year}/{slug}/"
        require(article["url"] == expected_url, f"{slug}: article-index URL must be {expected_url}.", errors)
        expected_feed_url = f"{SITE_URL}{expected_url}"
        require(expected_feed_url in feed_refs, f"{slug}: root feed.xml is missing {expected_feed_url}.", errors)
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

    validate_english_layer(cs_articles, errors)
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
