#!/usr/bin/env python3
"""Generate the Publications page from references.bib (stdlib only).

Quarto runs this script before rendering the website. Add/edit BibTeX records
in references.bib; do not edit the generated _publications_list.qmd file.
"""

from __future__ import annotations

import html
import re
import unicodedata
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse, quote

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "references.bib"
OUTPUT = ROOT / "_publications_list.qmd"

ENTRY_START = re.compile(r"(?m)^[ \t]*@([A-Za-z][A-Za-z0-9_-]*)\s*\{")
FIELD_START = re.compile(r"\s*,?\s*([A-Za-z][A-Za-z0-9_-]*)\s*=", re.S)
LATEX_ACCENT = re.compile(r"\\([\'\`\^\"~=\.uvHckbdtr])\s*(?:\{([^{}])\}|([A-Za-z]))")
ACCENTS = {
    "'": "\u0301", "`": "\u0300", "^": "\u0302", '"': "\u0308",
    "~": "\u0303", "=": "\u0304", ".": "\u0307", "u": "\u0306",
    "v": "\u030c", "H": "\u030b", "c": "\u0327", "k": "\u0328",
    "b": "\u0331", "d": "\u0323", "t": "\u0361", "r": "\u030a",
}
PREPRINT_VENUES = {"biorxiv", "medrxiv", "psyarxiv", "arxiv", "socarxiv", "ssrn", "osf preprints", "research square"}


def scan_braces(text: str, opener: int) -> int:
    """Index of matching } with nested braces and escaped brace support."""
    if text[opener] != "{":
        raise ValueError("Expected opening brace")
    depth = 1
    i = opener + 1
    while i < len(text):
        char = text[i]
        if char == "\\":
            i += 2
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    raise ValueError("Unclosed brace in references.bib")


def read_value(text: str, at: int) -> tuple[str, int]:
    """Read a BibTeX value (including quoted/braced and # concatenation)."""
    pieces = []
    pos = at
    while True:
        while pos < len(text) and text[pos].isspace():
            pos += 1
        if pos >= len(text):
            break
        if text[pos] == "{":
            end = scan_braces(text, pos)
            pieces.append(text[pos + 1 : end])
            pos = end + 1
        elif text[pos] == '"':
            start = pos + 1
            pos = start
            while pos < len(text) and (text[pos] != '"' or text[pos - 1] == "\\"):
                pos += 1
            if pos == len(text):
                raise ValueError("Unclosed quoted BibTeX field")
            pieces.append(text[start:pos])
            pos += 1
        else:
            start = pos
            while pos < len(text) and text[pos] not in ",#\r\n \t":
                pos += 1
            if pos == start:
                break
            pieces.append(text[start:pos])
        while pos < len(text) and text[pos].isspace():
            pos += 1
        if pos < len(text) and text[pos] == "#":
            pos += 1
            continue
        break
    return "".join(pieces).strip(), pos


def parse_bib(text: str) -> list[dict[str, str]]:
    """Parse BibTeX entries without requiring an installed Python package.

    Only lines beginning with @ introduce records, so %@article comment blocks
    in the supplied bibliography do not become visible publications.
    """
    entries = []
    keys = set()
    cursor = 0
    while match := ENTRY_START.search(text, cursor):
        kind = match.group(1).lower()
        opening = match.end() - 1
        closing = scan_braces(text, opening)
        cursor = closing + 1
        if kind in {"comment", "preamble", "string"}:
            continue
        body = text[opening + 1 : closing]
        citation_key, sep, content = body.partition(",")
        key = citation_key.strip()
        if not sep or not key:
            raise ValueError(f"Malformed @{kind} record near position {opening}")
        if key in keys:
            raise ValueError(f"Duplicate BibTeX citation key: {key}")
        keys.add(key)
        fields = {"entrytype": kind, "key": key}
        offset = 0
        while field_match := FIELD_START.match(content, offset):
            field = field_match.group(1).lower()
            value, offset = read_value(content, field_match.end())
            fields[field] = value
        entries.append(fields)
    return entries


def latex_to_text(value: str) -> str:
    """Convert common BibTeX text and LaTeX accents to readable Unicode."""
    value = re.sub(r"\\(?:textbf|textit|emph|textsc)\s*\{([^{}]*)\}", r"\1", value)

    def accent(match: re.Match[str]) -> str:
        return unicodedata.normalize("NFC", (match.group(2) or match.group(3)) + ACCENTS[match.group(1)])

    value = LATEX_ACCENT.sub(accent, value)
    value = re.sub(r"\\([%&_#{}$])", r"\1", value)
    value = value.replace("~", " ").replace("---", "—").replace("--", "–")
    # Braces in BibTeX usually protect capitalization, not visible punctuation.
    value = value.replace("{", "").replace("}", "")
    return " ".join(value.split())


def format_authors(raw: str) -> str:
    people = re.split(r"\s+and\s+", raw, flags=re.I)
    formatted = []
    for person in people:
        person = person.strip()
        featured = "\\textbf" in person
        clean = latex_to_text(person)
        if "," in clean:
            pieces = [part.strip() for part in clean.split(",")]
            if len(pieces) == 2:
                clean = f"{pieces[1]} {pieces[0]}"
            elif len(pieces) >= 3:  # BibTeX 'Last, Jr, First' convention
                clean = f"{pieces[2]} {pieces[0]}, {pieces[1]}"
        name = html.escape(clean)
        if featured:
            name = f"<strong>{name}</strong>"
        formatted.append(name)
    if not formatted:
        return ""
    if len(formatted) == 1:
        return formatted[0]
    if len(formatted) == 2:
        return " and ".join(formatted)
    return ", ".join(formatted[:-1]) + ", and " + formatted[-1]


def year_of(entry: dict[str, str]) -> str:
    date = entry.get("year") or entry.get("date", "")
    match = re.match(r"\s*(\d{4})\b", date)
    if not match:
        raise ValueError(f"Publication '{entry['key']}' needs a year or date (YYYY).")
    return match.group(1)


def safe_http_url(value: str) -> str:
    url = latex_to_text(value).strip()
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return ""
    return url


def normalized_doi(entry: dict[str, str]) -> str:
    """Return a valid DOI identifier, whether BibTeX stores an ID or DOI URL.

    This deliberately does not guess missing DOIs from article titles. Only the
    `doi` field in references.bib is used for the on-site DOI link.
    """
    value = latex_to_text(entry.get("doi", "")).strip()
    value = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", value, flags=re.I)
    if not re.fullmatch(r"10\.\d{4,9}/[^\s<>\"']+", value, flags=re.I):
        return ""
    return value


def doi_link(entry: dict[str, str]) -> str:
    """HTML link with a readable DOI identifier and a precise source label."""
    doi = normalized_doi(entry)
    if not doi:
        return ""
    venue = latex_to_text(entry.get("journaltitle") or entry.get("journal") or "").lower()
    if venue in PREPRINT_VENUES or doi.lower().startswith("10.48550/arxiv."):
        label = "Preprint DOI"
    elif doi.lower().startswith("10.5281/zenodo."):
        label = "Manuscript DOI"
    else:
        label = "DOI"
    url = "https://doi.org/" + quote(doi, safe="/._-;()")
    return (f'<a class="pub-doi" href="{html.escape(url, quote=True)}">'
            f'{label}: {html.escape(doi)}</a>')


def url_link(entry: dict[str, str]) -> str:
    """Link to the bibliographic URL only when no valid DOI is available."""
    url = safe_http_url(entry.get("url", ""))
    if not url:
        return ""
    return f'<a class="pub-url" href="{html.escape(url, quote=True)}">Publication</a>'


def format_venue(entry: dict[str, str]) -> str:
    source = entry.get("journaltitle") or entry.get("journal") or entry.get("booktitle") or ""
    base = f"<em>{html.escape(latex_to_text(source))}</em>" if source else ""
    volume = latex_to_text(entry.get("volume", ""))
    number = latex_to_text(entry.get("number", ""))
    pages = latex_to_text(entry.get("pages") or entry.get("eid") or "")
    if volume:
        volume = html.escape(volume)
        if number:
            volume += f"({html.escape(number)})"
    elif number:
        volume = html.escape(number)
    extras = ", ".join(part for part in (volume, html.escape(pages)) if part)
    if base and extras:
        base += ", " + extras
    elif extras:
        base = extras
    if entry.get("pubstate", "").strip().lower() == "forthcoming" or "forthcoming" in entry.get("keywords", "").lower():
        base += ". Forthcoming" if base else "Forthcoming"
    return base.rstrip(".") + "." if base else ""


def render_entry(entry: dict[str, str]) -> str:
    title = html.escape(latex_to_text(entry["title"]))
    authors = format_authors(entry["author"])
    venue = format_venue(entry)
    lines = ['<div class="pub-entry">', f'<div class="pub-title">{title}</div>']
    if venue:
        lines.append(f"<p>{authors}.<br>\n{venue}</p>")
    else:
        lines.append(f"<p>{authors}.</p>")
    link = doi_link(entry) or url_link(entry)
    if link:
        lines.append(f'<p class="pub-links">{link}</p>')
    elif entry.get("pubstate", "").strip().lower() == "forthcoming":
        lines.append('<p class="pub-doi-pending">DOI not yet available</p>')
    lines.append('</div>')
    return "\n".join(lines)


def generate_markdown(entries: list[dict[str, str]]) -> str:
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for entry in entries:
        if not entry.get("title") or not entry.get("author"):
            raise ValueError(f"Publication '{entry['key']}' needs title and author fields.")
        groups[year_of(entry)].append(entry)
    lines = ["<!-- AUTO-GENERATED from references.bib; do not edit this file. -->", ""]
    for year in sorted(groups, reverse=True):
        lines.extend((f"## {year}", ""))
        for entry in groups[year]:
            lines.extend((render_entry(entry), ""))
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    entries = parse_bib(SOURCE.read_text(encoding="utf-8"))
    if not entries:
        raise ValueError(f"No BibTeX publication entries found in {SOURCE}")
    result = generate_markdown(entries)
    # Don't update the mtime when content is unchanged; helps Quarto previews.
    if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != result:
        OUTPUT.write_text(result, encoding="utf-8")
    print(f"Generated Publications page from {len(entries)} BibTeX entries.")


if __name__ == "__main__":
    main()
