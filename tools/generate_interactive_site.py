#!/usr/bin/env python3
"""Generate the static interactive article index and navigation layer."""

from __future__ import annotations

import argparse
import hashlib
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
TRANSLATION_ROOT = ROOT / "interactive" / "translations"
GENERATED_ROOT = ROOT / "interactive" / "generated"
INDEX_PATH = ROOT / "interactive" / "article-index.json"
EN_INDEX_PATH = ROOT / "interactive" / "article-index.en.json"
SKILL_ASSET_ROOT = ROOT / ".agents" / "skills" / "interactive-article-generator" / "assets"
AVATAR_SOURCE = ROOT / "assets" / "img" / "avatar.png"
INDEX_AVATAR_SRC = "assets/img/avatar.png"
EN_INDEX_AVATAR_SRC = "../assets/img/avatar.png"
ARTICLE_AVATAR_SRC = "../../assets/img/avatar.png"
EN_ARTICLE_AVATAR_SRC = "../../../assets/img/avatar.png"
SITE_ROOT = ROOT / "_site"
DEFAULT_PUBLIC_BASE = "/"
DEFAULT_CLASSIC_BASE = "/classic/"
SITE_URL = "https://tomaskubica.cz"
RECENT_CARD_COUNT = 6
ARCHIVE_INITIAL_VISIBLE = 24
ARCHIVE_BATCH_SIZE = 24
TRANSLATION_NOTICE_CURRENT = "Machine translation from Czech"
TRANSLATION_NOTICE_STALE = (
    "Machine translation from Czech. The Czech original has changed since this translation was generated "
    "and is the authoritative version."
)

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
    source_slug: str = ""
    translated_from_hash: str = ""
    translation_status: str = ""


@dataclass(frozen=True)
class Theme:
    id: str
    title: str
    summary: str
    featured_slugs: tuple[str, ...]


@dataclass(frozen=True)
class LocaleConfig:
    code: str
    html_lang: str
    public_base: str
    output_subdir: str
    generated_subdir: str
    index_avatar_src: str
    article_avatar_src: str
    title: str
    description: str
    eyebrow: str
    subtitle: str
    navigation_label: str
    theme_button_label: str
    classic_link_text: str
    rss_text: str
    llms_text: str
    language_switch_label: str
    current_language_label: str
    other_language_label: str
    recent_title: str
    search_summary: str
    search_label: str
    search_placeholder: str
    search_status: str
    themes_title: str
    all_title: str
    section_note: str
    archive_more: str
    back_to_index: str
    related_kicker: str
    agent_friendly: str
    article_navigation_label: str
    related_same_theme: str
    related_shared_context: str
    related_shared_tokens: str
    related_default: str


CS_LOCALE = LocaleConfig(
    code="cs",
    html_lang="cs-CZ",
    public_base="/",
    output_subdir="",
    generated_subdir="",
    index_avatar_src=INDEX_AVATAR_SRC,
    article_avatar_src=ARTICLE_AVATAR_SRC,
    title="AI, vývoj a cloud | Tomáš Kubica",
    description="Prakticky o AI, vývoji, cloudu a o tom, co se mi při stavbě moderních systémů osvědčilo.",
    eyebrow="AI, vývoj a cloud",
    subtitle="Prakticky o AI, vývoji, cloudu a o tom, co se mi při stavbě moderních systémů osvědčilo.",
    navigation_label="Navigace",
    theme_button_label="Tmavý režim",
    classic_link_text="Starší články najdete na mém klasickém blogu",
    rss_text="RSS",
    llms_text="llms.txt",
    language_switch_label="Jazyk",
    current_language_label="CZ",
    other_language_label="EN",
    recent_title="Nejnovější",
    search_summary="⌕ Hledat v článcích",
    search_label="Hledat v názvech, shrnutích, tématech a štítcích",
    search_placeholder="Například tokeny, GenUI, skills...",
    search_status="Vyhledávací index se načte až při psaní.",
    themes_title="Témata",
    all_title="Všechny články",
    section_note="Stránka je statická; při větším počtu článků se starší položky jen postupně odkrývají po dávkách.",
    archive_more="Zobrazit další články",
    back_to_index="← Všechny interaktivní články",
    related_kicker="Doporučeno dál",
    agent_friendly="Agent-friendly verze",
    article_navigation_label="Navigace článku",
    related_same_theme="Navazuje na stejné téma: {theme}.",
    related_shared_context="Sdílí praktický kontext: {label}.",
    related_shared_tokens="Má podobný slovník a praktický kontext.",
    related_default="Je to další aktuální text z interaktivní série.",
)

EN_LOCALE = LocaleConfig(
    code="en",
    html_lang="en",
    public_base="/en/",
    output_subdir="en",
    generated_subdir="en",
    index_avatar_src=EN_INDEX_AVATAR_SRC,
    article_avatar_src=EN_ARTICLE_AVATAR_SRC,
    title="AI, development and cloud | Tomas Kubica",
    description="Practical writing about AI, development, cloud and what works when building modern systems.",
    eyebrow="AI, development and cloud",
    subtitle="Practical writing about AI, development, cloud and what works when building modern systems.",
    navigation_label="Navigation",
    theme_button_label="Dark mode",
    classic_link_text="Older Czech articles are on my classic blog",
    rss_text="RSS",
    llms_text="llms.txt",
    language_switch_label="Language",
    current_language_label="EN",
    other_language_label="CZ",
    recent_title="Latest",
    search_summary="⌕ Search articles",
    search_label="Search titles, summaries, topics and labels",
    search_placeholder="For example tokens, GenUI, skills...",
    search_status="The search index loads when you start typing.",
    themes_title="Topics",
    all_title="All articles",
    section_note="This page is static; as the archive grows, older items are progressively revealed in batches.",
    archive_more="Show more articles",
    back_to_index="← All interactive articles",
    related_kicker="Recommended next",
    agent_friendly="Agent-friendly version",
    article_navigation_label="Article navigation",
    related_same_theme="Continues the same topic: {theme}.",
    related_shared_context="Shares practical context: {label}.",
    related_shared_tokens="Uses similar vocabulary and practical context.",
    related_default="Another recent article from the interactive series.",
)


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


def read_cache(index_path: Path = INDEX_PATH) -> tuple[list[Article], list[Theme]]:
    with index_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if data.get("version") != 1:
        raise ValueError(f"{index_path.relative_to(ROOT)} must have version 1")

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
            source_slug=item.get("source_slug", item["slug"]),
            translated_from_hash=item.get("translated_from_hash", ""),
            translation_status=item.get("translation_status", ""),
        )
        for item in data.get("articles", [])
    ]
    return articles, themes


def read_optional_cache(index_path: Path) -> tuple[list[Article], list[Theme]]:
    if not index_path.is_file():
        return [], []
    return read_cache(index_path)


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


def source_hash(slug: str) -> str:
    for candidate in SOURCE_ROOT.glob(f"*/{slug}.article.md"):
        return hashlib.sha256(candidate.read_bytes()).hexdigest()
    raise FileNotFoundError(f"Missing Czech source for {slug}")


def normalize_url_base(value: str) -> str:
    if not value:
        return "/"
    normalized = "/" + value.strip("/") + "/"
    return "/" if normalized == "//" else normalized


def join_url(base: str, *parts: object) -> str:
    normalized = normalize_url_base(base)
    suffix = "/".join(str(part).strip("/") for part in parts if str(part).strip("/"))
    if not suffix:
        return normalized
    return f"{normalized}{suffix}/"


def absolute_public_url(path: str) -> str:
    if path.startswith(("http://", "https://")):
        return path
    return f"{SITE_URL}/{path.lstrip('/')}"


def root_relative_url(path: str) -> str:
    return path.lstrip("/")


def validate_articles(
    articles: list[Article],
    themes: list[Theme],
    public_base: str,
    generated_root: Path,
    cache_path: Path,
) -> None:
    errors: list[str] = []
    source_by_slug = source_articles()
    article_by_slug = {article.slug: article for article in articles}
    theme_ids = {theme.id for theme in themes}
    cache_name = str(cache_path.relative_to(ROOT))

    if len(article_by_slug) != len(articles):
        errors.append(f"Duplicate article slug in {cache_name}")

    if len(theme_ids) != len(themes):
        errors.append(f"Duplicate theme id in {cache_name}")

    if cache_path == INDEX_PATH:
        for slug in sorted(set(source_by_slug) - set(article_by_slug)):
            errors.append(f"Source article {slug} is missing from interactive\\article-index.json")

        for slug in sorted(set(article_by_slug) - set(source_by_slug)):
            errors.append(f"Cache article {slug} has no matching interactive source")

    for article in articles:
        source = source_by_slug.get(article.source_slug or article.slug)
        if source:
            if cache_path == INDEX_PATH:
                for key, expected in (("title", article.title), ("date", article.date)):
                    if source.get(key) != expected:
                        errors.append(f"{article.slug}: cache {key} does not match source front matter")
        if article.year != int(article.date[:4]):
            errors.append(f"{article.slug}: year must match date year")
        expected_url = join_url(public_base, article.year, article.slug)
        if article.url != expected_url:
            errors.append(f"{article.slug}: url must be {expected_url}")
        for theme_id in article.themes:
            if theme_id not in theme_ids:
                errors.append(f"{article.slug}: unknown theme {theme_id}")
        generated_dir = generated_root / str(article.year) / article.slug
        for filename in ("index.html", "source.md", "caveman.md"):
            if not (generated_dir / filename).is_file():
                errors.append(f"{article.slug}: missing {generated_dir.relative_to(ROOT)}\\{filename}")

    for theme in themes:
        for slug in theme.featured_slugs:
            if slug not in article_by_slug:
                errors.append(f"{theme.id}: featured slug {slug} does not exist")

    if errors:
        raise ValueError("\n".join(errors))


def validate_translations(en_articles: list[Article], en_themes: list[Theme], cs_articles: list[Article]) -> None:
    if not en_articles:
        return

    errors: list[str] = []
    source_by_slug = source_articles()
    cs_by_slug = {article.slug: article for article in cs_articles}
    validate_articles(en_articles, en_themes, EN_LOCALE.public_base, GENERATED_ROOT / "en", EN_INDEX_PATH)

    for article in en_articles:
        source_slug = article.source_slug or article.slug
        if source_slug not in cs_by_slug:
            errors.append(f"{article.slug}: English article source_slug {source_slug} has no Czech article")
        if source_slug not in source_by_slug:
            errors.append(f"{article.slug}: English article source_slug {source_slug} has no Czech source")

        translation_path = TRANSLATION_ROOT / "en" / str(article.year) / f"{article.slug}.article.md"
        if not translation_path.is_file():
            errors.append(f"{article.slug}: missing {translation_path.relative_to(ROOT)}")
            continue

        metadata = parse_front_matter(translation_path)
        expected = {
            "language": "en",
            "source_language": "cs-CZ",
            "source_slug": source_slug,
            "translation": "machine",
        }
        for key, value in expected.items():
            if metadata.get(key) != value:
                errors.append(f"{article.slug}: translation front matter {key} must be {value}")
        if not metadata.get("translated_from_hash"):
            errors.append(f"{article.slug}: translation front matter is missing translated_from_hash")
        if article.translated_from_hash and metadata.get("translated_from_hash") != article.translated_from_hash:
            errors.append(f"{article.slug}: article-index.en.json translated_from_hash does not match translation source")

    if errors:
        raise ValueError("\n".join(errors))


def copy_assets(output_root: Path) -> None:
    output_root.mkdir(parents=True, exist_ok=True)

    asset_target = output_root / "assets"
    asset_target.mkdir(parents=True, exist_ok=True)
    for filename in ("interactive-article.css", "interactive-article.js"):
        shutil.copy2(SKILL_ASSET_ROOT / filename, asset_target / filename)
    if not AVATAR_SOURCE.is_file():
        raise FileNotFoundError(f"Author avatar is missing: {AVATAR_SOURCE.relative_to(ROOT)}")
    avatar_target = asset_target / "img" / "avatar.png"
    avatar_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(AVATAR_SOURCE, avatar_target)


def copy_article_files(
    output_root: Path,
    articles: list[Article],
    public_base: str,
    generated_root: Path,
    output_subdir: str = "",
) -> None:
    target_root = output_root / output_subdir if output_subdir else output_root
    target_root.mkdir(parents=True, exist_ok=True)

    for article in articles:
        source_dir = generated_root / str(article.year) / article.slug
        article_dir = target_root / str(article.year) / article.slug
        shutil.copytree(source_dir, article_dir, dirs_exist_ok=True)
        public_url = join_url(public_base, article.year, article.slug)
        legacy_url = f"/new/{article.year}/{article.slug}/"
        for filename in ("index.html", "source.md", "caveman.md"):
            path = article_dir / filename
            if path.is_file():
                text = path.read_text(encoding="utf-8").replace(legacy_url, public_url)
                if filename == "index.html":
                    image_prefix = "../../../images/" if output_subdir else "../../images/"
                    text = text.replace("../../../../images/", image_prefix)
                path.write_text(text, encoding="utf-8")


def theme_lookup(themes: list[Theme]) -> dict[str, Theme]:
    return {theme.id: theme for theme in themes}


def related_articles(articles: list[Article], themes: list[Theme], locale: LocaleConfig) -> dict[str, tuple[Article, str]]:
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

        if not candidates:
            continue
        best_score, _, best_article, shared_themes, shared_labels = max(candidates, key=lambda item: (item[0], item[1]))
        if shared_themes:
            theme_title = by_theme[sorted(shared_themes)[0]].title
            reason = locale.related_same_theme.format(theme=theme_title)
        elif shared_labels:
            reason = locale.related_shared_context.format(label=sorted(shared_labels)[0])
        elif best_score > 0:
            reason = locale.related_shared_tokens
        else:
            reason = locale.related_default
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


def llms_text(value: str) -> str:
    return value.replace("\n", " ").replace("[", r"\[").replace("]", r"\]").strip()


def llms_article_link(article: Article, prefix: str, filename: str, label: str) -> str:
    url = absolute_public_url(f"{prefix}{article.year}/{article.slug}/{filename}")
    return f"- [{llms_text(label)}: {llms_text(article.title)}]({url}): {llms_text(article.summary)}"


def llms_section(title: str, articles: list[Article], prefix: str, filename: str, label: str) -> str:
    if not articles:
        return ""
    links = "\n".join(llms_article_link(article, prefix, filename, label) for article in articles)
    return f"## {title}\n\n{links}"


def generate_llms_txt(cs_articles: list[Article], en_articles: list[Article], output_root: Path) -> None:
    cs_recent = sorted(cs_articles, key=lambda article: article.date, reverse=True)
    en_recent = sorted(en_articles, key=lambda article: article.date, reverse=True)
    sections = [
        llms_section("Czech source articles", cs_recent, "", "source.md", "CZ source.md"),
        llms_section("Czech caveman summaries", cs_recent, "", "caveman.md", "CZ caveman.md"),
        llms_section("English source articles", en_recent, "en/", "source.md", "EN source.md"),
        llms_section("English caveman summaries", en_recent, "en/", "caveman.md", "EN caveman.md"),
    ]
    body = "\n\n".join(section for section in sections if section)
    text = f"""# Tomáš Kubica

> Interactive Czech and English articles about AI, development, cloud, and practical engineering experience.

Use `source.md` links for faithful article sources and `caveman.md` links for compact agent-friendly summaries. Czech articles are the originals; English articles are machine translations when available.

{body}
"""
    (output_root / "llms.txt").write_text(text, encoding="utf-8")


def index_root_relative(path: str, locale: LocaleConfig) -> str:
    relative = root_relative_url(path)
    return f"../{relative}" if locale.output_subdir else relative


def index_language_switch(locale: LocaleConfig, has_english: bool) -> str:
    if locale.code == "cs":
        if not has_english:
            return ""
        return f'<a href="en/" lang="en" hreflang="en">{e(locale.other_language_label)}</a>'
    return f'<a href="../" lang="cs-CZ" hreflang="cs-CZ">{e(locale.other_language_label)}</a>'


def generate_index(
    articles: list[Article],
    themes: list[Theme],
    output_root: Path,
    public_base: str,
    classic_base: str,
    locale: LocaleConfig,
    has_english: bool = False,
) -> None:
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
        f"{e(locale.archive_more)}</button>"
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
    classic_link = index_root_relative(classic_base, locale)
    feed_link = index_root_relative("/", locale) + "feed.xml"
    llms_link = index_root_relative("/", locale) + "llms.txt"
    hero_avatar = (
        f'<img class="ia-avatar ia-avatar-hero" src="{e(locale.index_avatar_src)}" alt="" '
        'width="112" height="112" aria-hidden="true" decoding="async">'
    )
    language_link = index_language_switch(locale, has_english)
    language_nav = ""
    if language_link:
        language_nav = f"""
      <nav class="ia-links" aria-label="{e(locale.language_switch_label)}">
        <a href="./" aria-current="page">{e(locale.current_language_label)}</a>
        {language_link}
      </nav>""".rstrip()
    asset_prefix = "../" if locale.output_subdir else ""
    output_dir = output_root / locale.output_subdir if locale.output_subdir else output_root
    output_dir.mkdir(parents=True, exist_ok=True)
    html_text = f"""<!doctype html>
<html lang="{e(locale.html_lang)}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{THEME_SCRIPT}
<style>
{THEME_VARIABLES}
</style>
<link rel="stylesheet" href="{asset_prefix}assets/interactive-article.css">
<title>{e(locale.title)}</title>
<meta name="description" content="{e(locale.description)}">
<link rel="canonical" href="{e(normalize_url_base(public_base))}">
</head>
<body>
<div class="ia-controls" aria-label="{e(locale.navigation_label)}">
  <button class="ia-control theme" type="button" data-theme-toggle>{e(locale.theme_button_label)}</button>
</div>
<div class="ia-page ia-index-page">
<header class="ia-header ia-index-hero">
  <div class="ia-author-hero">
    {hero_avatar}
    <div class="ia-author-copy">
      <p class="ia-eyebrow">{e(locale.eyebrow)}</p>
      <h1 class="ia-title">Tomáš Kubica</h1>
      <p class="ia-subtitle">{e(locale.subtitle)}</p>
      <nav class="ia-links" aria-label="{e(locale.navigation_label)}">
        <a href="{e(classic_link)}">{e(locale.classic_link_text)}</a>
        <a href="{e(feed_link)}">{e(locale.rss_text)}</a>
        <a href="{e(llms_link)}">{e(locale.llms_text)}</a>
      </nav>
      {language_nav}
    </div>
  </div>
</header>
<main>
  <section class="ia-group" aria-labelledby="recent-title">
    <h2 class="ia-group-title" id="recent-title">{e(locale.recent_title)}</h2>
    <div class="ia-index-grid">
      {recent_cards}
    </div>
  </section>

  <section class="ia-group ia-index-search" aria-labelledby="search-title" data-ia-index-search>
    <details class="ia-search-disclosure">
      <summary class="ia-search-summary" id="search-title">{e(locale.search_summary)}</summary>
      <div class="ia-search-panel">
        <label class="ia-search-label" for="ia-search-input">{e(locale.search_label)}</label>
        <input class="ia-search-input" id="ia-search-input" type="search" autocomplete="off" placeholder="{e(locale.search_placeholder)}" data-search-src="search.json">
        <p class="ia-search-status" data-ia-search-status>{e(locale.search_status)}</p>
        <ol class="ia-search-results" data-ia-search-results></ol>
      </div>
    </details>
  </section>

  <section class="ia-group" aria-labelledby="themes-title">
    <h2 class="ia-group-title" id="themes-title">{e(locale.themes_title)}</h2>
    <div class="ia-card-list ia-theme-list">
      {theme_cards}
    </div>
  </section>

  <section class="ia-group" aria-labelledby="all-title">
    <h2 class="ia-group-title" id="all-title">{e(locale.all_title)}</h2>
    <p class="ia-section-note">{e(locale.section_note)}</p>
    <div data-ia-archive data-initial-visible="{ARCHIVE_INITIAL_VISIBLE}">
    {archive}
    </div>
    {archive_button}
  </section>
</main>
<footer class="ia-footer">
  <p><a href="{e(classic_link)}">{e(locale.classic_link_text)}</a> · <a href="{e(feed_link)}">{e(locale.rss_text)}</a> · <a href="{e(llms_link)}">{e(locale.llms_text)}</a></p>
</footer>
</div>
<script src="{asset_prefix}assets/interactive-article.js"></script>
</body>
</html>
"""
    (output_dir / "index.html").write_text(html_text, encoding="utf-8")


def generate_search_json(articles: list[Article], themes: list[Theme], output_root: Path, locale: LocaleConfig) -> None:
    output_dir = output_root / locale.output_subdir if locale.output_subdir else output_root
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "search.json").write_text(search_payload_json(articles, themes), encoding="utf-8")


def relative_article_url(from_article: Article, to_article: Article) -> str:
    return f"../../{to_article.year}/{to_article.slug}/"


def article_footer(article: Article, related: Article | None, reason: str, locale: LocaleConfig) -> str:
    related_block = ""
    if related is not None:
        related_url = relative_article_url(article, related)
        related_block = f"""
<section class="ia-related" aria-labelledby="related-title">
  <p class="ia-related-kicker">{e(locale.related_kicker)}</p>
  <h2 id="related-title"><a href="{e(related_url)}">{e(related.title)}</a></h2>
  <p>{e(reason)} {e(related.summary)}</p>
  <p class="ia-related-meta"><time datetime="{e(related.date)}">{e(display_date(related.date))}</time></p>
</section>""".rstrip()
    return f"""<footer class="ia-footer">
<div class="ia-article-nav">
  <a href="../../">{e(locale.back_to_index)}</a>
</div>
{related_block}
<p>{e(locale.agent_friendly)}: <a href="./source.md">source.md</a> · <a href="./caveman.md">caveman.md</a></p>
</footer>"""


def article_language_links(
    article: Article,
    locale: LocaleConfig,
    translations_by_source: dict[str, Article],
    cs_by_slug: dict[str, Article],
) -> str:
    if locale.code == "cs":
        translated = translations_by_source.get(article.slug)
        if not translated:
            return ""
        return (
            f'<a href="./" aria-current="page" lang="cs-CZ" hreflang="cs-CZ">{e(locale.current_language_label)}</a>\n'
            f'<a href="../../en/{translated.year}/{translated.slug}/" lang="en" hreflang="en">{e(locale.other_language_label)}</a>'
        )

    source = cs_by_slug.get(article.source_slug or article.slug)
    if not source:
        return ""
    return (
        f'<a href="../../../{source.year}/{source.slug}/" lang="cs-CZ" hreflang="cs-CZ">{e(locale.other_language_label)}</a>\n'
        f'<a href="./" aria-current="page" lang="en" hreflang="en">{e(locale.current_language_label)}</a>'
    )


def patch_article_nav(
    text: str,
    article: Article,
    locale: LocaleConfig,
    translations_by_source: dict[str, Article],
    cs_by_slug: dict[str, Article],
) -> str:
    candidates = [
        (
            re.compile(r'(<nav\b(?=[^>]*\bclass="[^"]*\bia-links\b[^"]*")[^>]*>)(.*?</nav>)', re.S),
            None,
        ),
        (
            re.compile(r'(<div\b(?=[^>]*\bclass="[^"]*\bia-actions\b[^"]*")[^>]*>)(.*?</div>)', re.S),
            "div",
        ),
    ]
    for pattern, fallback_tag in candidates:
        for match in pattern.finditer(text):
            block = match.group(0)
            if "./source.md" not in block or "./caveman.md" not in block:
                continue

            if fallback_tag == "div":
                opening = f'<nav class="ia-links" aria-label="{e(locale.article_navigation_label)}">'
                body = re.sub(r"</div>\s*$", "</nav>", match.group(2), count=1)
            else:
                opening = re.sub(
                    r'aria-label="[^"]*"',
                    f'aria-label="{e(locale.article_navigation_label)}"',
                    match.group(1),
                    count=1,
                )
                if opening == match.group(1):
                    opening = opening[:-1] + f' aria-label="{e(locale.article_navigation_label)}">'
                body = match.group(2)

            language_links = article_language_links(article, locale, translations_by_source, cs_by_slug)
            language_block = f"\n{language_links}" if language_links else ""
            replacement = f'{opening}\n<a href="../../">{e(locale.back_to_index)}</a>{language_block}\n{body}'
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


def article_avatar_markup(locale: LocaleConfig) -> str:
    return (
        f'<img class="ia-avatar ia-avatar-small" src="{e(locale.article_avatar_src)}" alt="Tomáš Kubica" '
        'width="40" height="40" decoding="async">'
    )


def patch_article_avatar(text: str, article: Article, locale: LocaleConfig) -> str:
    if 'class="ia-avatar ia-avatar-small"' in text:
        return text

    match = re.search(r'<p class="ia-eyebrow">.*?</p>', text, flags=re.S)
    if not match:
        raise ValueError(f"{article.slug}: could not patch article avatar")

    wrapped = f'<div class="ia-author-row">{article_avatar_markup(locale)}{match.group(0)}</div>'
    return text[: match.start()] + wrapped + text[match.end() :]


def patch_head_language_metadata(
    text: str,
    article: Article,
    locale: LocaleConfig,
    translations_by_source: dict[str, Article],
    cs_by_slug: dict[str, Article],
) -> str:
    text = re.sub(r'<html lang="[^"]*"', f'<html lang="{e(locale.html_lang)}"', text, count=1)
    text = re.sub(
        r'<link rel="canonical" href="[^"]*">',
        f'<link rel="canonical" href="{e(article.url)}">',
        text,
        count=1,
    )

    alternates = ""
    if locale.code == "cs":
        translated = translations_by_source.get(article.slug)
        if translated:
            alternates = f"""
<link rel="alternate" hreflang="cs-CZ" href="{e(article.url)}">
<link rel="alternate" hreflang="en" href="{e(translated.url)}">
<link rel="alternate" hreflang="x-default" href="{e(article.url)}">""".rstrip()
    else:
        source = cs_by_slug.get(article.source_slug or article.slug)
        if source:
            alternates = f"""
<link rel="alternate" hreflang="cs-CZ" href="{e(source.url)}">
<link rel="alternate" hreflang="en" href="{e(article.url)}">
<link rel="alternate" hreflang="x-default" href="{e(source.url)}">""".rstrip()

    text = re.sub(r'\n<link rel="alternate" hreflang="[^"]+" href="[^"]+">', "", text)
    if alternates and "</head>" in text:
        text = text.replace("</head>", f"{alternates}\n</head>", 1)
    return text


def translation_is_stale(article: Article) -> bool:
    return bool(article.translated_from_hash) and article.translated_from_hash != source_hash(article.source_slug or article.slug)


def patch_translation_notice(text: str, article: Article, cs_by_slug: dict[str, Article]) -> str:
    if 'class="ia-translation-notice"' in text:
        return text
    source = cs_by_slug.get(article.source_slug or article.slug)
    if not source:
        raise ValueError(f"{article.slug}: translation source article is missing")
    source_url = f"../../../{source.year}/{source.slug}/"
    notice = f'{e(TRANSLATION_NOTICE_CURRENT)} <a href="{e(source_url)}">original</a>.'
    if translation_is_stale(article):
        notice = (
            f"{notice} Czech original has changed since this translation was generated "
            "and is the authoritative version."
        )
    block = f"""
<aside class="ia-callout warning ia-translation-notice">
  <p>{notice}</p>
</aside>""".rstrip()
    if "</header>" not in text:
        raise ValueError(f"{article.slug}: could not insert translation notice")
    return text.replace("</header>", f"</header>\n{block}", 1)


def patch_article_pages(
    articles: list[Article],
    themes: list[Theme],
    output_root: Path,
    locale: LocaleConfig,
    translations_by_source: dict[str, Article],
    cs_by_slug: dict[str, Article],
) -> None:
    recommendations = related_articles(articles, themes, locale)
    base_dir = output_root / locale.output_subdir if locale.output_subdir else output_root
    for article in articles:
        path = base_dir / str(article.year) / article.slug / "index.html"
        text = path.read_text(encoding="utf-8")
        text = patch_head_language_metadata(text, article, locale, translations_by_source, cs_by_slug)
        text = patch_article_avatar(text, article, locale)
        text = patch_article_nav(text, article, locale, translations_by_source, cs_by_slug)
        if locale.code == "en":
            text = patch_translation_notice(text, article, cs_by_slug)
        text = normalize_article_card_defaults(text)
        related_item = recommendations.get(article.slug)
        related, reason = related_item if related_item else (None, "")
        text, footer_count = re.subn(
            r"<footer class=\"ia-footer\">.*?</footer>",
            article_footer(article, related, reason, locale),
            text,
            count=1,
            flags=re.S,
        )
        if footer_count != 1:
            raise ValueError(f"{article.slug}: could not patch article footer")

        path.write_text(text, encoding="utf-8")


def run(output_root: Path, public_base: str = DEFAULT_PUBLIC_BASE, classic_base: str = DEFAULT_CLASSIC_BASE) -> None:
    public_base = normalize_url_base(public_base)
    classic_base = normalize_url_base(classic_base)
    articles, themes = read_cache()
    en_articles, en_themes = read_optional_cache(EN_INDEX_PATH)
    cs_by_slug = {article.slug: article for article in articles}
    translations_by_source = {article.source_slug or article.slug: article for article in en_articles}

    cs_locale = LocaleConfig(**(CS_LOCALE.__dict__ | {"public_base": public_base}))
    en_locale = EN_LOCALE

    validate_articles(articles, themes, public_base, GENERATED_ROOT, INDEX_PATH)
    validate_translations(en_articles, en_themes, articles)
    copy_assets(output_root)
    copy_article_files(output_root, articles, public_base, GENERATED_ROOT)
    if en_articles:
        copy_article_files(output_root, en_articles, en_locale.public_base, GENERATED_ROOT / "en", en_locale.output_subdir)
    generate_llms_txt(articles, en_articles, output_root)

    generate_index(articles, themes, output_root, public_base, classic_base, cs_locale, has_english=bool(en_articles))
    generate_search_json(articles, themes, output_root, cs_locale)
    patch_article_pages(articles, themes, output_root, cs_locale, translations_by_source, cs_by_slug)
    if en_articles:
        generate_index(en_articles, en_themes, output_root, en_locale.public_base, classic_base, en_locale, has_english=True)
        generate_search_json(en_articles, en_themes, output_root, en_locale)
        patch_article_pages(en_articles, en_themes, output_root, en_locale, translations_by_source, cs_by_slug)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the static interactive site artifacts.")
    parser.add_argument("--output", type=Path, default=SITE_ROOT, help="Output directory for interactive site artifacts.")
    parser.add_argument("--public-base", default=DEFAULT_PUBLIC_BASE, help="Public URL base for the interactive site.")
    parser.add_argument("--classic-base", default=DEFAULT_CLASSIC_BASE, help="Public URL base for the classic Jekyll site.")
    args = parser.parse_args()
    try:
        run(args.output.resolve(), public_base=args.public_base, classic_base=args.classic_base)
    except Exception as exc:
        print(f"generate_interactive_site.py: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
