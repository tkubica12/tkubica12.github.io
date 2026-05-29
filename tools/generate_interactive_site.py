#!/usr/bin/env python3
"""Generate the static /new/ interactive article index and navigation layer."""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sys
import unicodedata
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "interactive" / "source"
GENERATED_ROOT = ROOT / "interactive" / "generated"
INDEX_PATH = ROOT / "interactive" / "article-index.json"
SKILL_ASSET_ROOT = ROOT / ".agents" / "skills" / "interactive-article-generator" / "assets"
SITE_NEW_ROOT = ROOT / "_site" / "new"
RECENT_CARD_COUNT = 6
ARCHIVE_INITIAL_VISIBLE = 24
ARCHIVE_BATCH_SIZE = 24

THEME_SCRIPT = """<script>
(() => {
  const params = new URLSearchParams(window.location.search);
  const requested = params.get("clawpilotTheme");
  const isTheme = (value) => value === "light" || value === "dark";
  let stored = null;
  try { stored = localStorage.getItem("interactive-article-theme"); } catch {}
  const system = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  document.documentElement.setAttribute("data-theme", isTheme(requested) ? requested : isTheme(stored) ? stored : system);
})();
</script>"""

THEME_VARIABLES = """:root {
  --cp-bg: #ffffff;
  --cp-bg-elevated: #f8fafc;
  --cp-surface: #f6f8fa;
  --cp-surface-soft: #eef2f6;
  --cp-panel: #ffffff;
  --cp-text: #172033;
  --cp-text-muted: #475569;
  --cp-text-soft: #64748b;
  --cp-border: #d8dee9;
  --cp-border-strong: #b6c2cf;
  --cp-accent: #0969da;
  --cp-accent-soft: rgba(9, 105, 218, 0.08);
  --cp-link: #0969da;
  --cp-success: #1a7f37;
  --cp-warning: #9a6700;
  --cp-danger: #cf222e;
  color-scheme: light;
}

html[data-theme="dark"] {
  --cp-bg: #0d1117;
  --cp-bg-elevated: #161b22;
  --cp-surface: #161b22;
  --cp-surface-soft: #21262d;
  --cp-panel: #0d1117;
  --cp-text: #f0f6fc;
  --cp-text-muted: #c9d1d9;
  --cp-text-soft: #8b949e;
  --cp-border: #30363d;
  --cp-border-strong: #484f58;
  --cp-accent: #58a6ff;
  --cp-accent-soft: rgba(88, 166, 255, 0.13);
  --cp-link: #58a6ff;
  --cp-success: #3fb950;
  --cp-warning: #d29922;
  --cp-danger: #f85149;
  color-scheme: dark;
}"""


@dataclass(frozen=True)
class Article:
    slug: str
    year: int
    date: str
    title: str
    eyebrow: str
    subtitle: str
    url: str
    summary: str
    labels: tuple[str, ...]
    themes: tuple[str, ...]


@dataclass(frozen=True)
class Theme:
    id: str
    title: str
    summary: str
    featured_slugs: tuple[str, ...]


def e(value: object) -> str:
    return html.escape(str(value), quote=True)


def display_date(value: str) -> str:
    parsed = date.fromisoformat(value)
    return f"{parsed.day}. {parsed.month}. {parsed.year}"


def normalize(value: str) -> str:
    folded = unicodedata.normalize("NFD", value.lower())
    return "".join(ch for ch in folded if unicodedata.category(ch) != "Mn")


def tokens(article: Article) -> set[str]:
    text = " ".join([article.title, article.subtitle, article.summary, *article.labels])
    return {part for part in re.split(r"[^0-9a-zA-Zá-žÁ-Ž]+", normalize(text)) if len(part) >= 3}


def read_cache() -> tuple[list[Article], list[Theme]]:
    with INDEX_PATH.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if data.get("version") != 1:
        raise ValueError("interactive\\article-index.json must have version 1")

    themes = [
        Theme(
            id=item["id"],
            title=item["title"],
            summary=item["summary"],
            featured_slugs=tuple(item.get("featured_slugs", [])),
        )
        for item in data.get("themes", [])
    ]
    articles = [
        Article(
            slug=item["slug"],
            year=int(item["year"]),
            date=item["date"],
            title=item["title"],
            eyebrow=item.get("eyebrow", ""),
            subtitle=item["subtitle"],
            url=item["url"],
            summary=item["summary"],
            labels=tuple(item.get("labels", [])),
            themes=tuple(item.get("themes", [])),
        )
        for item in data.get("articles", [])
    ]
    return articles, themes


def parse_front_matter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not match:
        raise ValueError(f"{path} has no front matter")

    result: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line or line.startswith(" ") or ":" not in line:
            continue
        key, raw_value = line.split(":", 1)
        value = raw_value.strip()
        if value.startswith(("\"", "'")) and value.endswith(("\"", "'")):
            value = value[1:-1]
        result[key.strip()] = value
    return result


def source_articles() -> dict[str, dict[str, str]]:
    items: dict[str, dict[str, str]] = {}
    for path in SOURCE_ROOT.glob("*/*.article.md"):
        metadata = parse_front_matter(path)
        slug = metadata.get("slug")
        if not slug:
            raise ValueError(f"{path} is missing slug")
        items[slug] = metadata | {"_path": str(path.relative_to(ROOT))}
    return items


def validate(articles: list[Article], themes: list[Theme]) -> None:
    errors: list[str] = []
    source_by_slug = source_articles()
    article_by_slug = {article.slug: article for article in articles}
    theme_ids = {theme.id for theme in themes}

    if len(article_by_slug) != len(articles):
        errors.append("Duplicate article slug in interactive\\article-index.json")

    if len(theme_ids) != len(themes):
        errors.append("Duplicate theme id in interactive\\article-index.json")

    for slug in sorted(set(source_by_slug) - set(article_by_slug)):
        errors.append(f"Source article {slug} is missing from interactive\\article-index.json")

    for slug in sorted(set(article_by_slug) - set(source_by_slug)):
        errors.append(f"Cache article {slug} has no matching interactive source")

    for article in articles:
        source = source_by_slug.get(article.slug)
        if source:
            for key, expected in (("title", article.title), ("date", article.date)):
                if source.get(key) != expected:
                    errors.append(f"{article.slug}: cache {key} does not match source front matter")
        if article.year != int(article.date[:4]):
            errors.append(f"{article.slug}: year must match date year")
        if article.url != f"/new/{article.year}/{article.slug}/":
            errors.append(f"{article.slug}: url must be /new/{article.year}/{article.slug}/")
        for theme_id in article.themes:
            if theme_id not in theme_ids:
                errors.append(f"{article.slug}: unknown theme {theme_id}")
        generated_dir = GENERATED_ROOT / str(article.year) / article.slug
        for filename in ("index.html", "source.md", "caveman.md"):
            if not (generated_dir / filename).is_file():
                errors.append(f"{article.slug}: missing interactive\\generated\\{article.year}\\{article.slug}\\{filename}")

    for theme in themes:
        for slug in theme.featured_slugs:
            if slug not in article_by_slug:
                errors.append(f"{theme.id}: featured slug {slug} does not exist")

    if errors:
        raise ValueError("\n".join(errors))


def copy_public_files() -> None:
    SITE_NEW_ROOT.mkdir(parents=True, exist_ok=True)
    shutil.copytree(GENERATED_ROOT, SITE_NEW_ROOT, dirs_exist_ok=True)

    asset_target = SITE_NEW_ROOT / "assets"
    asset_target.mkdir(parents=True, exist_ok=True)
    for filename in ("interactive-article.css", "interactive-article.js"):
        shutil.copy2(SKILL_ASSET_ROOT / filename, asset_target / filename)


def theme_lookup(themes: list[Theme]) -> dict[str, Theme]:
    return {theme.id: theme for theme in themes}


def related_articles(articles: list[Article], themes: list[Theme]) -> dict[str, tuple[Article, str]]:
    by_theme = theme_lookup(themes)
    token_cache = {article.slug: tokens(article) for article in articles}
    recommendations: dict[str, tuple[Article, str]] = {}

    for article in articles:
        candidates: list[tuple[int, str, Article, set[str], set[str]]] = []
        article_themes = set(article.themes)
        article_labels = {normalize(label) for label in article.labels}
        article_tokens = token_cache[article.slug]

        for candidate in articles:
            if candidate.slug == article.slug:
                continue
            shared_themes = article_themes & set(candidate.themes)
            shared_labels = article_labels & {normalize(label) for label in candidate.labels}
            shared_tokens = article_tokens & token_cache[candidate.slug]
            score = len(shared_themes) * 8 + len(shared_labels) * 2 + min(len(shared_tokens), 6)
            candidates.append((score, candidate.date, candidate, shared_themes, shared_labels))

        best_score, _, best_article, shared_themes, shared_labels = max(candidates, key=lambda item: (item[0], item[1]))
        if shared_themes:
            theme_title = by_theme[sorted(shared_themes)[0]].title
            reason = f"Navazuje na stejné téma: {theme_title}."
        elif shared_labels:
            reason = f"Sdílí praktický kontext: {sorted(shared_labels)[0]}."
        elif best_score > 0:
            reason = "Má podobný slovník a praktický kontext."
        else:
            reason = "Je to další aktuální text z interaktivní série."
        recommendations[article.slug] = (best_article, reason)

    return recommendations


def index_article_url(article: Article) -> str:
    return f"{article.year}/{article.slug}/"


def article_link(article: Article, class_name: str = "ia-index-card") -> str:
    return f"""
<article class="{class_name}">
  <p class="ia-index-date"><time datetime="{e(article.date)}">{e(display_date(article.date))}</time></p>
  <h3><a href="{e(index_article_url(article))}">{e(article.title)}</a></h3>
  <p>{e(article.summary)}</p>
</article>""".strip()


def archive_item(article: Article, index: int) -> str:
    return (
        f'<li data-ia-archive-item data-archive-index="{index}">'
        f'<time datetime="{e(article.date)}">{e(display_date(article.date))}</time>'
        f'<a href="{e(index_article_url(article))}">{e(article.title)}</a>'
        "</li>"
    )


def theme_card(theme: Theme, articles: list[Article]) -> str:
    selected = [article for article in articles if theme.id in article.themes]
    selected_by_slug = {article.slug: article for article in selected}
    ordered: list[Article] = []
    for slug in theme.featured_slugs:
        if slug in selected_by_slug:
            ordered.append(selected_by_slug.pop(slug))
    ordered.extend(sorted(selected_by_slug.values(), key=lambda article: article.date, reverse=True))

    panel_id = f"theme-{theme.id}"
    links = "\n".join(
        f'<li><a href="{e(index_article_url(article))}">{e(article.title)}</a> <span>{e(display_date(article.date))}</span></li>'
        for article in ordered[:5]
    )
    return f"""
<article class="ia-card ia-theme-card" data-ia-card>
  <button class="ia-card-head" type="button" aria-expanded="false" aria-controls="{e(panel_id)}" data-ia-card-button>
    <span class="ia-card-title">{e(theme.title)}</span>
    <span class="ia-card-toggle" aria-hidden="true">▾</span>
  </button>
  <div class="ia-card-body" id="{e(panel_id)}" data-ia-card-panel>
    <div class="ia-card-body-clip">
      <div class="ia-card-content">
        <p>{e(theme.summary)}</p>
        <ul class="ia-theme-links">{links}</ul>
      </div>
    </div>
  </div>
</article>""".strip()


def build_search_payload(articles: list[Article], themes: list[Theme]) -> list[dict[str, object]]:
    by_theme = theme_lookup(themes)
    payload = []
    for article in sorted(articles, key=lambda item: item.date, reverse=True):
        payload.append(
            {
                "title": article.title,
                "subtitle": article.subtitle,
                "summary": article.summary,
                "date": article.date,
                "url": index_article_url(article),
                "labels": list(article.labels),
                "themes": [by_theme[theme_id].title for theme_id in article.themes],
            }
        )
    return payload


def search_payload_json(articles: list[Article], themes: list[Theme]) -> str:
    return json.dumps(build_search_payload(articles, themes), ensure_ascii=False, separators=(",", ":"))


def generate_index(articles: list[Article], themes: list[Theme]) -> None:
    recent = sorted(articles, key=lambda article: article.date, reverse=True)
    all_by_year: dict[int, list[Article]] = defaultdict(list)
    for article in recent:
        all_by_year[article.year].append(article)

    recent_cards = "\n".join(article_link(article) for article in recent[:RECENT_CARD_COUNT])
    theme_cards = "\n".join(theme_card(theme, recent) for theme in themes[:5])
    archive_index = 0
    archive_has_more = len(recent) > ARCHIVE_INITIAL_VISIBLE
    archive_button = (
        f'<button class="ia-control ia-archive-more" type="button" data-ia-archive-more data-batch-size="{ARCHIVE_BATCH_SIZE}" hidden>'
        "Zobrazit další články</button>"
        if archive_has_more
        else ""
    )
    archive_sections: list[str] = []
    archive_index = 0
    for year, items in sorted(all_by_year.items(), reverse=True):
        list_items = "".join(archive_item(article, archive_index + index) for index, article in enumerate(items))
        archive_index += len(items)
        archive_sections.append(
            f"""
<section class="ia-year-group" aria-labelledby="year-{year}">
  <h3 id="year-{year}">{year}</h3>
  <ol class="ia-article-list">
    {list_items}
  </ol>
</section>""".strip()
        )
    archive = "\n".join(archive_sections)
    html_text = f"""<!doctype html>
<html lang="cs-CZ">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{THEME_SCRIPT}
<style>
{THEME_VARIABLES}
</style>
<link rel="stylesheet" href="assets/interactive-article.css">
<title>AI, vývoj a cloud | Tomáš Kubica</title>
<meta name="description" content="Prakticky o AI, vývoji, cloudu a o tom, co se mi při stavbě moderních systémů osvědčilo.">
<link rel="canonical" href="/new/">
</head>
<body>
<div class="ia-controls" aria-label="Ovládání stránky">
  <button class="ia-control theme" type="button" data-theme-toggle>Tmavý režim</button>
</div>
<div class="ia-page ia-index-page">
<header class="ia-header ia-index-hero">
  <p class="ia-eyebrow">AI, vývoj a cloud</p>
  <h1 class="ia-title">Tomáš Kubica</h1>
  <p class="ia-subtitle">Prakticky o AI, vývoji, cloudu a o tom, co se mi při stavbě moderních systémů osvědčilo.</p>
  <nav class="ia-links" aria-label="Navigace">
    <a href="../">Starší články najdete na mém klasickém blogu</a>
    <a href="../feed.xml">RSS</a>
  </nav>
</header>
<main>
  <section class="ia-group" aria-labelledby="recent-title">
    <h2 class="ia-group-title" id="recent-title">Nejnovější</h2>
    <div class="ia-index-grid">
      {recent_cards}
    </div>
  </section>

  <section class="ia-group ia-index-search" aria-labelledby="search-title" data-ia-index-search>
    <details class="ia-search-disclosure">
      <summary class="ia-search-summary" id="search-title"><span aria-hidden="true">⌕</span> Hledat v článcích</summary>
      <div class="ia-search-panel">
        <label class="ia-search-label" for="ia-search-input">Hledat v názvech, shrnutích, tématech a štítcích</label>
        <input class="ia-search-input" id="ia-search-input" type="search" autocomplete="off" placeholder="Například tokeny, GenUI, skills..." data-search-src="search.json">
        <p class="ia-search-status" data-ia-search-status>Vyhledávací index se načte až při psaní.</p>
        <ol class="ia-search-results" data-ia-search-results></ol>
      </div>
    </details>
  </section>

  <section class="ia-group" aria-labelledby="themes-title">
    <h2 class="ia-group-title" id="themes-title">Témata</h2>
    <div class="ia-card-list ia-theme-list">
      {theme_cards}
    </div>
  </section>

  <section class="ia-group" aria-labelledby="all-title">
    <h2 class="ia-group-title" id="all-title">Všechny články</h2>
    <p class="ia-section-note">Stránka je statická; při větším počtu článků se starší položky jen postupně odkrývají po dávkách.</p>
    <div data-ia-archive data-initial-visible="{ARCHIVE_INITIAL_VISIBLE}">
    {archive}
    </div>
    {archive_button}
  </section>
</main>
<footer class="ia-footer">
  <p>Starší články najdete na <a href="../">mém klasickém blogu</a> · <a href="../feed.xml">RSS</a></p>
</footer>
</div>
<script src="assets/interactive-article.js"></script>
</body>
</html>
"""
    (SITE_NEW_ROOT / "index.html").write_text(html_text, encoding="utf-8")


def generate_search_json(articles: list[Article], themes: list[Theme]) -> None:
    (SITE_NEW_ROOT / "search.json").write_text(search_payload_json(articles, themes), encoding="utf-8")


def relative_article_url(from_article: Article, to_article: Article) -> str:
    return f"../../{to_article.year}/{to_article.slug}/"


def article_footer(article: Article, related: Article, reason: str) -> str:
    related_url = relative_article_url(article, related)
    return f"""<footer class="ia-footer">
<div class="ia-article-nav">
  <a href="../../">← Všechny interaktivní články</a>
</div>
<section class="ia-related" aria-labelledby="related-title">
  <p class="ia-related-kicker">Doporučeno dál</p>
  <h2 id="related-title"><a href="{e(related_url)}">{e(related.title)}</a></h2>
  <p>{e(reason)} {e(related.summary)}</p>
  <p class="ia-related-meta"><time datetime="{e(related.date)}">{e(display_date(related.date))}</time></p>
</section>
<p>Agent-friendly verze: <a href="./source.md">source.md</a> · <a href="./caveman.md">caveman.md</a></p>
</footer>"""


def patch_article_nav(text: str, article: Article) -> str:
    pattern = re.compile(r'(<nav class="ia-links"[^>]*>)(.*?</nav>)', re.S)
    for match in pattern.finditer(text):
        block = match.group(0)
        if "./source.md" not in block or "./caveman.md" not in block:
            continue

        opening = re.sub(r'aria-label="[^"]*"', 'aria-label="Navigace článku"', match.group(1), count=1)
        replacement = f'{opening}\n<a href="../../">← Všechny interaktivní články</a>\n{match.group(2)}'
        return text[: match.start()] + replacement + text[match.end() :]

    raise ValueError(f"{article.slug}: could not patch article navigation")


def normalize_article_card_defaults(text: str) -> str:
    card_index = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal card_index
        is_first = card_index == 0
        card_index += 1
        classes = [part for part in match.group(2).split() if part != "is-open"]
        if is_first:
            classes.append("is-open")
        aria_value = "true" if is_first else "false"
        return f'{match.group(1)}{" ".join(classes)}{match.group(3)}{aria_value}{match.group(5)}'

    return re.sub(
        r'(<article class=")([^"]*)(" data-ia-card>.*?<button class="ia-card-head"[^>]*aria-expanded=")(true|false)(")',
        replace,
        text,
        flags=re.S,
    )


def patch_article_pages(articles: list[Article], themes: list[Theme]) -> None:
    recommendations = related_articles(articles, themes)
    for article in articles:
        path = SITE_NEW_ROOT / str(article.year) / article.slug / "index.html"
        text = path.read_text(encoding="utf-8")
        text = patch_article_nav(text, article)
        text = normalize_article_card_defaults(text)
        related, reason = recommendations[article.slug]
        text, footer_count = re.subn(
            r"<footer class=\"ia-footer\">.*?</footer>",
            article_footer(article, related, reason),
            text,
            count=1,
            flags=re.S,
        )
        if footer_count != 1:
            raise ValueError(f"{article.slug}: could not patch article footer")

        path.write_text(text, encoding="utf-8")


def run(output_root: Path) -> None:
    global SITE_NEW_ROOT
    SITE_NEW_ROOT = output_root
    articles, themes = read_cache()
    validate(articles, themes)
    copy_public_files()
    generate_index(articles, themes)
    generate_search_json(articles, themes)
    patch_article_pages(articles, themes)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the static /new/ interactive site artifacts.")
    parser.add_argument("--output", type=Path, default=SITE_NEW_ROOT, help="Output directory for /new/ artifacts.")
    args = parser.parse_args()
    try:
        run(args.output.resolve())
    except Exception as exc:
        print(f"generate_interactive_site.py: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
