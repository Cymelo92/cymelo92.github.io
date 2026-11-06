"""Source and pre-rendered GitHub Pages must expose the same site features."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class WebsiteFeaturesTests(unittest.TestCase):
    def test_nav_has_no_cv_tab(self):
        config = (ROOT / '_quarto.yml').read_text(encoding='utf-8')
        self.assertNotIn('href: cv.qmd', config)
        for path in (ROOT / 'docs').glob('*.html'):
            html = path.read_text(encoding='utf-8')
            self.assertIsNone(re.search(r'<a[^>]+href="(?:\./|/)cv\.html"[^>]*>\s*<span class="menu-text">CV</span>', html), path.name)

    def test_home_cv_is_downloadable(self):
        pdf = ROOT / 'files' / 'Carlo_Meloni_CV.pdf'
        rendered_pdf = ROOT / 'docs' / 'files' / 'Carlo_Meloni_CV.pdf'
        self.assertTrue(pdf.is_file())
        self.assertEqual(pdf.read_bytes(), rendered_pdf.read_bytes())
        for path in (ROOT / 'index.qmd', ROOT / 'docs/index.html'):
            html = path.read_text(encoding='utf-8')
            self.assertIn('href="files/Carlo_Meloni_CV.pdf"', html)
            self.assertIn('download="Carlo_Meloni_CV.pdf"', html)

    def test_sitewide_theme_toggle_is_present(self):
        config = (ROOT / '_quarto.yml').read_text(encoding='utf-8')
        self.assertIn('include-in-header: includes/theme-head.html', config)
        theme = (ROOT / 'includes/theme-head.html').read_text(encoding='utf-8')
        self.assertIn("'cymelo92-theme'", theme)
        self.assertIn('prefers-color-scheme: dark', theme)
        self.assertIn('academic-theme-toggle', theme)
        self.assertIn('data-bs-theme', theme)
        for page in (ROOT / 'docs').glob('*.html'):
            content = page.read_text(encoding='utf-8')
            self.assertIn("'cymelo92-theme'", content, page.name)
            self.assertIn('academic-theme-toggle', content, page.name)

    def test_built_publications_have_doi_links(self):
        built = (ROOT / 'docs/publications.html').read_text(encoding='utf-8')
        self.assertEqual(built.count('class="pub-entry"'), 9)
        self.assertEqual(built.count('class="pub-doi"'), 7)
        self.assertEqual(built.count('class="pub-url"'), 1)
        self.assertNotIn('>Preprint</a>', built)
        self.assertIn('href="https://escholarship.org/uc/item/4hz9j5f8"', built)
        self.assertIn('DOI not yet available', built)


if __name__ == '__main__':
    unittest.main()
