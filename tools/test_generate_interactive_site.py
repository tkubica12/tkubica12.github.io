from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import generate_interactive_site as site


class ArticlePublicationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.article = site.Article(
            slug="test",
            year=2026,
            date="2026-09-15",
            title="Test",
            eyebrow="Test",
            subtitle="Test",
            url="/2026/test/",
            summary="Test",
            labels=(),
            themes=(),
        )

    def test_translation_notice_is_idempotent(self) -> None:
        page = "<html><header>Title</header><main>Article</main></html>"
        sources = {self.article.slug: self.article}
        rendered = site.patch_translation_notice(page, self.article, sources)
        self.assertEqual(rendered.count('class="ia-callout warning ia-translation-notice"'), 1)
        self.assertIn("Machine translation from Czech", rendered)
        for _ in range(3):
            self.assertEqual(site.patch_translation_notice(rendered, self.article, sources), rendered)

    def test_copy_preserves_bytes_and_rewrites_legacy_links(self) -> None:
        for newline in ("\n", "\r\n"):
            with self.subTest(newline=repr(newline)), TemporaryDirectory(prefix="site-copy-test-") as directory:
                root = Path(directory)
                generated = root / "generated"
                article_dir = generated / "2026" / "test"
                article_dir.mkdir(parents=True)
                source = f"Czech: \u017elu\u0165ou\u010dk\u00fd.{newline}".encode("utf-8")
                summary = f"/new/2026/test/{newline}".encode("utf-8")
                page = f'/new/2026/test/{newline}<img src="../../../../images/chart.png">{newline}'.encode("utf-8")
                (article_dir / "source.md").write_bytes(source)
                (article_dir / "caveman.md").write_bytes(summary)
                (article_dir / "index.html").write_bytes(page)
                output = root / "output"
                site.copy_article_files(output, [self.article], "/en/", generated, "en")
                result = output / "en" / "2026" / "test"
                self.assertEqual((result / "source.md").read_bytes(), source)
                self.assertEqual((result / "caveman.md").read_bytes(), summary.replace(b"/new/", b"/en/"))
                expected_page = page.replace(b"/new/", b"/en/").replace(b"../../../../images/", b"../../../images/")
                self.assertEqual((result / "index.html").read_bytes(), expected_page)


if __name__ == "__main__":
    unittest.main()
