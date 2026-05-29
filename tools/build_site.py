#!/usr/bin/env python3
"""Build the deployed GitHub Pages artifact."""

from __future__ import annotations

import argparse
import html
import json
import shutil
import subprocess
import sys
from pathlib import Path

import generate_interactive_site


ROOT = Path(__file__).resolve().parents[1]
SITE_ROOT = ROOT / "_site"
CLASSIC_ROOT = SITE_ROOT / "classic"
REDIRECT_OVERRIDES = ROOT / "redirects" / "legacy-overrides.json"
COMPATIBILITY_DIRS = ("assets", "images", ".well-known")
LEGACY_ROOT_FILES = ("feed.xml",)


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
    for filename in LEGACY_ROOT_FILES:
        source = CLASSIC_ROOT / filename
        if source.is_file():
            shutil.copy2(source, SITE_ROOT / filename)


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
