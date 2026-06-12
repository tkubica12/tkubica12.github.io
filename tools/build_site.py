#!/usr/bin/env python3
"""Build the deployed GitHub Pages artifact."""

from __future__ import annotations

import argparse
import copy
import html
import json
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

import generate_interactive_site


ROOT = Path(__file__).resolve().parents[1]
SITE_ROOT = ROOT / "_site"
CLASSIC_ROOT = SITE_ROOT / "classic"
REDIRECT_OVERRIDES = ROOT / "redirects" / "legacy-overrides.json"
COMPATIBILITY_DIRS = ("assets", "images", ".well-known", "dev-productivity")
SITE_URL = "https://tomaskubica.cz"
ATOM_NS = "http://www.w3.org/2005/Atom"
AUTHOR_NAME = "Tomáš Kubica"
SITE_TITLE = "Tomáš Kubica"
SITE_SUBTITLE = "AI, vývoj a cloud"
SITE_TIMEZONE = ZoneInfo("Europe/Prague")

ET.register_namespace("", ATOM_NS)


@dataclass(frozen=True)
class FeedEntry:
    element: ET.Element
    sort_date: datetime
    keys: frozenset[str]


def remove_path(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def prepare_site(skip_classic: bool) -> None:
    if skip_classic:
        if not (CLASSIC_ROOT / "index.html").is_file():
            raise RuntimeError("Cannot skip classic build because _site/classic/index.html is missing.")
        for child in SITE_ROOT.iterdir():
            if child.name != "classic":
                remove_path(child)
        return

    shutil.rmtree(SITE_ROOT, ignore_errors=True)
    SITE_ROOT.mkdir(parents=True, exist_ok=True)


def run_command(command: str) -> None:
    subprocess.run(command, cwd=ROOT, check=True, shell=True)


def build_classic() -> None:
    run_command(
        "bundle exec jekyll build "
        "--config _config.yml,_config_classic.yml "
        "--destination _site/classic"
    )


def copy_compatibility_assets() -> None:
    for dirname in COMPATIBILITY_DIRS:
        source = ROOT / dirname
        if source.is_dir():
            shutil.copytree(source, SITE_ROOT / dirname, dirs_exist_ok=True)
    image_source = ROOT / "images"
    if image_source.is_dir() and CLASSIC_ROOT.is_dir():
        shutil.copytree(image_source, CLASSIC_ROOT / "images", dirs_exist_ok=True)


def atom_tag(name: str) -> str:
    return f"{{{ATOM_NS}}}{name}"


def absolute_site_url(path: str) -> str:
    if path.startswith(("http://", "https://")):
        return path
    if not path.startswith("/"):
        path = "/" + path
    return f"{SITE_URL}{path}"


def article_datetime(value: str) -> str:
    return datetime.fromisoformat(value).replace(tzinfo=SITE_TIMEZONE).isoformat()


def parse_feed_datetime(value: str | None) -> datetime:
    if not value:
        return datetime.min.replace(tzinfo=timezone.utc)
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def add_text(parent: ET.Element, name: str, text: str) -> ET.Element:
    element = ET.SubElement(parent, atom_tag(name))
    element.text = text
    return element


def interactive_feed_entry(article: generate_interactive_site.Article) -> FeedEntry:
    url = absolute_site_url(article.url)
    published = article_datetime(article.date)
    entry = ET.Element(atom_tag("entry"))
    add_text(entry, "title", article.title)
    ET.SubElement(
        entry,
        atom_tag("link"),
        {"href": url, "rel": "alternate", "type": "text/html", "title": article.title},
    )
    add_text(entry, "published", published)
    add_text(entry, "updated", published)
    add_text(entry, "id", url)
    ET.SubElement(entry, atom_tag("content"), {"type": "text/html", "src": url})
    author = ET.SubElement(entry, atom_tag("author"))
    add_text(author, "name", AUTHOR_NAME)
    for label in article.labels:
        ET.SubElement(entry, atom_tag("category"), {"term": label})
    add_text(entry, "summary", article.summary)
    return FeedEntry(entry, parse_feed_datetime(published), frozenset({url}))


def text_of(element: ET.Element, name: str) -> str:
    child = element.find(atom_tag(name))
    return child.text.strip() if child is not None and child.text else ""


def feed_key_aliases(key: str, redirect_overrides: dict[str, str]) -> set[str]:
    aliases = {key}
    parsed = urlsplit(key)
    path = parsed.path
    if parsed.netloc == "tomaskubica.cz" and path.startswith("/classic/"):
        legacy_path = path.removeprefix("/classic")
        if legacy_path in redirect_overrides:
            aliases.add(absolute_site_url(redirect_overrides[legacy_path]))
    return aliases


def classic_feed_entries(path: Path, redirect_overrides: dict[str, str]) -> list[FeedEntry]:
    if not path.is_file():
        return []
    root = ET.parse(path).getroot()
    entries: list[FeedEntry] = []
    for entry in root.findall(atom_tag("entry")):
        keys = {text_of(entry, "id")}
        for link in entry.findall(atom_tag("link")):
            href = link.attrib.get("href", "")
            if href:
                keys.add(href)
        keys = {key for key in keys if key}
        keys = {alias for key in keys for alias in feed_key_aliases(key, redirect_overrides)}
        sort_text = text_of(entry, "updated") or text_of(entry, "published")
        entries.append(FeedEntry(copy.deepcopy(entry), parse_feed_datetime(sort_text), frozenset(keys)))
    return entries


def write_combined_feed() -> None:
    articles, _ = generate_interactive_site.read_cache()
    interactive_entries = [interactive_feed_entry(article) for article in articles]
    interactive_keys = {key for entry in interactive_entries for key in entry.keys}
    classic_entries = [
        entry
        for entry in classic_feed_entries(CLASSIC_ROOT / "feed.xml", load_redirect_overrides())
        if not entry.keys.intersection(interactive_keys)
    ]
    entries = interactive_entries + classic_entries

    deduped: list[FeedEntry] = []
    seen: set[str] = set()
    for entry in sorted(entries, key=lambda item: item.sort_date, reverse=True):
        if entry.keys and seen.intersection(entry.keys):
            continue
        deduped.append(entry)
        seen.update(entry.keys)

    updated = deduped[0].sort_date.isoformat().replace("+00:00", "Z") if deduped else datetime.now(timezone.utc).isoformat()
    feed = ET.Element(atom_tag("feed"))
    add_text(feed, "id", f"{SITE_URL}/")
    add_text(feed, "title", SITE_TITLE)
    add_text(feed, "subtitle", SITE_SUBTITLE)
    add_text(feed, "updated", updated)
    author = ET.SubElement(feed, atom_tag("author"))
    add_text(author, "name", AUTHOR_NAME)
    add_text(author, "uri", f"{SITE_URL}/")
    ET.SubElement(feed, atom_tag("link"), {"rel": "self", "type": "application/atom+xml", "href": f"{SITE_URL}/feed.xml"})
    ET.SubElement(feed, atom_tag("link"), {"rel": "alternate", "type": "text/html", "hreflang": "cs-CZ", "href": f"{SITE_URL}/"})
    generator = add_text(feed, "generator", "Python static site build")
    generator.set("uri", "https://github.com/tkubica12/tkubica12.github.io")
    add_text(feed, "rights", f"© {datetime.now(timezone.utc).year} {AUTHOR_NAME}")
    add_text(feed, "icon", f"{SITE_URL}/assets/img/favicons/favicon.ico")
    add_text(feed, "logo", f"{SITE_URL}/assets/img/favicons/favicon-96x96.png")
    for entry in deduped:
        feed.append(entry.element)

    tree = ET.ElementTree(feed)
    ET.indent(tree, space="  ")
    tree.write(SITE_ROOT / "feed.xml", encoding="utf-8", xml_declaration=True)


def normalize_path(value: str) -> str:
    if not value.startswith("/"):
        value = "/" + value
    if Path(value).suffix:
        return value
    return value if value.endswith("/") else value + "/"


def load_redirect_overrides() -> dict[str, str]:
    if not REDIRECT_OVERRIDES.is_file():
        return {}
    raw = json.loads(REDIRECT_OVERRIDES.read_text(encoding="utf-8"))
    return {normalize_path(source): normalize_path(target) for source, target in raw.items()}


def classic_html_paths() -> set[str]:
    paths: set[str] = set()
    for file_path in CLASSIC_ROOT.rglob("*.html"):
        rel = file_path.relative_to(CLASSIC_ROOT).as_posix()
        if rel == "index.html" or rel == "404.html":
            continue
        if rel.endswith("/index.html"):
            paths.add(normalize_path(rel[: -len("index.html")]))
        else:
            paths.add("/" + rel)
    return paths


def write_redirect(source_path: str, target_path: str) -> None:
    target = html.escape(target_path, quote=True)
    body = f"""<!doctype html>
<html lang="cs-CZ">
<head>
<meta charset="utf-8">
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url={target}">
<link rel="canonical" href="{target}">
<title>Přesměrování | Tomáš Kubica</title>
<script>window.location.replace({json.dumps(target_path)});</script>
</head>
<body>
<p>Stránka se přesunula na <a href="{target}">{target}</a>.</p>
</body>
</html>
"""
    source = source_path.strip("/")
    target_file = SITE_ROOT / source if source.endswith(".html") else SITE_ROOT / source / "index.html"
    target_file.parent.mkdir(parents=True, exist_ok=True)
    target_file.write_text(body, encoding="utf-8")


def generate_redirects() -> None:
    classic_paths = classic_html_paths()
    overrides = load_redirect_overrides()
    missing_sources = sorted(source for source in overrides if source not in classic_paths)
    if missing_sources:
        raise RuntimeError("Redirect overrides do not match classic pages: " + ", ".join(missing_sources))

    for source_path in sorted(classic_paths):
        target_path = overrides.get(source_path, normalize_path(f"/classic{source_path}"))
        write_redirect(source_path, target_path)


def write_root_404() -> None:
    (SITE_ROOT / "404.html").write_text(
        """<!doctype html>
<html lang="cs-CZ">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>Stránka nenalezena | Tomáš Kubica</title>
</head>
<body>
<main>
<h1>Stránka nenalezena</h1>
<p>Pokud hledáte starší blog, pokračujte na <a href="/classic/">classic verzi</a>.</p>
<p><a href="/">Zpět na hlavní stránku</a></p>
</main>
</body>
</html>
""",
        encoding="utf-8",
    )


def build(skip_classic: bool) -> None:
    prepare_site(skip_classic)
    if not skip_classic:
        build_classic()

    generate_interactive_site.run(SITE_ROOT, public_base="/", classic_base="/classic/")
    copy_compatibility_assets()
    write_combined_feed()
    generate_redirects()
    write_root_404()


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the complete GitHub Pages artifact.")
    parser.add_argument("--skip-classic", action="store_true", help="Reuse an existing _site/classic build.")
    args = parser.parse_args()
    try:
        build(skip_classic=args.skip_classic)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
