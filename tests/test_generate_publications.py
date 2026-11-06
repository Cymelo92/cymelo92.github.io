"""Sanity checks for updating Publications from the BibTeX source."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from generate_publications import (  # noqa: E402
    SOURCE,
    format_authors,
    generate_markdown,
    latex_to_text,
    normalized_doi,
    parse_bib,
)


class PublicationsTests(unittest.TestCase):
    def setUp(self):
        self.entries = parse_bib(SOURCE.read_text(encoding="utf-8"))

    def test_all_active_publications_from_attached_bib(self):
        self.assertEqual(len(self.entries), 9)
        self.assertEqual(len({e["key"] for e in self.entries}), 9)
        self.assertNotIn("meloni2025writing", [e["key"] for e in self.entries])

    def test_years_and_identifier_links(self):
        output = generate_markdown(self.entries)
        self.assertEqual(output.count('class="pub-entry"'), 9)
        self.assertNotIn('>Preprint</a>', output)
        self.assertLess(output.index("## 2026"), output.index("## 2025"))
        self.assertLess(output.index("## 2025"), output.index("## 2021"))
        self.assertEqual(output.count('class="pub-doi"'), 7)
        self.assertEqual(output.count('class="pub-url"'), 1)
        self.assertEqual(output.count('class="pub-doi-pending"'), 1)
        self.assertIn('href="https://escholarship.org/uc/item/4hz9j5f8"', output)
        self.assertNotIn('10.48550/arXiv.2602.20372', output)
        self.assertIn('DOI not yet available', output)
        self.assertEqual(output.count("Publication</a>"), 1)
        self.assertNotIn("This page lists publications", output)

    def test_accents_and_emphasized_author(self):
        self.assertEqual(latex_to_text(r"Ku{\v{c}}erov{\'{a}}"), "Kučerová")
        rendered = format_authors(r"Ku{\v{c}}erov{\'{a}}, Al{\v{z}}b{\v{e}}ta and \textbf{Meloni, Carlo Y.}")
        self.assertEqual(rendered, "Alžběta Kučerová and <strong>Carlo Y. Meloni</strong>")

    def test_new_year_requires_no_page_edit(self):
        example = """\n@article{demo2030,
          author = {Meloni, Carlo Y. and Example, Alice},
          title = {New entry from BibTeX}, year = {2030},
          journal = {bioRxiv}, keywords = {underreview},
          url = {https://example.org/preprint}}
        """
        updated = self.entries + parse_bib(example)
        output = generate_markdown(updated)
        self.assertIn("## 2030", output)
        self.assertIn('href="https://example.org/preprint"', output)
        self.assertEqual(output.count('class="pub-entry"'), 10)
        self.assertLess(output.index("## 2030"), output.index("## 2026"))

    def test_published_paper_has_doi_not_publisher_link(self):
        published = {
            "key": "fake", "title": "Published", "author": "Doe, Jane",
            "year": "2029", "journal": "Journal of Testing", "keywords": "published",
            "url": "https://publisher.example.com/paper", "doi": "10.1234/valid.123",
        }
        result = generate_markdown([published])
        self.assertIn('href="https://doi.org/10.1234/valid.123"', result)
        self.assertNotIn('href="https://publisher.example.com/paper"', result)
        published["preprint"] = "https://preprints.example.com/paper"
        self.assertEqual(generate_markdown([published]).count("<a"), 1)
        self.assertNotIn('>Preprint</a>', generate_markdown([published]))

    def test_no_doi_uses_url_and_invalid_links_are_ignored(self):
        entry = {
            "key": "without-doi", "title": "Paper without DOI", "author": "Doe, Jane",
            "year": "2029", "url": "https://example.org/paper?x=1&y=2",
        }
        result = generate_markdown([entry])
        self.assertIn('class="pub-url"', result)
        self.assertIn('href="https://example.org/paper?x=1&amp;y=2"', result)
        self.assertIn('>Publication</a>', result)
        entry["doi"] = "10.1234/valid-doi"
        result = generate_markdown([entry])
        self.assertIn('class="pub-doi"', result)
        self.assertNotIn('class="pub-url"', result)
        entry["doi"] = "invalid"
        entry["url"] = "javascript:alert(1)"
        self.assertNotIn('class="pub-links"', generate_markdown([entry]))

    def test_uppercase_bibtex_doi_and_validity(self):
        conversion = next(e for e in self.entries if e["key"] == "meloni2025transcription")
        self.assertEqual(normalized_doi(conversion), "10.15475/calcip.2025.2.6")
        self.assertEqual(normalized_doi({"doi": "https://doi.org/10.1234/ABC-22"}), "10.1234/ABC-22")
        self.assertEqual(normalized_doi({"doi": "javascript:alert(1)"}), "")
        self.assertEqual(normalized_doi({"doi": "10.x/invalid"}), "")

    def test_text_is_escaped_before_html_output(self):
        fake = {"key": "injection", "title": '<img src=x onerror="bad">',
                "author": "Doe, Jane", "year": "2028"}
        result = generate_markdown([fake])
        self.assertIn("&lt;img", result)
        self.assertNotIn("<img", result)


if __name__ == "__main__":
    unittest.main()
