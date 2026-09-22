#!/usr/bin/env python3
"""Generate index pages for the GitHub Pages site.

Builds a site-root index listing every subject and a per-subject index listing
that subject's material pages, both styled with the shared `material.css` so
they read as part of the same publication as the lecture pages themselves.

Metadata is recovered from each page's existing markup (`<title>`, the
`.eyebrow` affiliation line, `<h1>`) rather than from a separate manifest, so
pages written by hand are listed on equal terms with generated ones.

Usage:
    build_index.py SITE_DIR

SITE_DIR is the staged site (subject directories at its top level), not the
repository's `output/`.
"""

from __future__ import annotations

import html
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path

# Week numbers in `class01-02_theme.html` / `class01_theme.html` filenames.
WEEK_RE = re.compile(r"^class(\d+)(?:-(\d+))?_(.+)$")
# Subject directory names: `2026_コンパイラ`.
SUBJECT_RE = re.compile(r"^(\d{4})_(.+)$")

TITLE_RE = re.compile(r"<title>(.*?)</title>", re.DOTALL | re.IGNORECASE)
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.DOTALL | re.IGNORECASE)
EYEBROW_RE = re.compile(
    r'<p class="eyebrow"[^>]*>(.*?)</p>', re.DOTALL | re.IGNORECASE
)
TAG_RE = re.compile(r"<[^>]+>")


def text_of(markup: str) -> str:
    """Collapse an HTML fragment to its plain text."""
    # <br> separates the affiliation from the subject name; keep that boundary
    # visible so the two do not run together into one word.
    markup = re.sub(r"<br\s*/?>", "\n", markup, flags=re.IGNORECASE)
    return html.unescape(TAG_RE.sub("", markup)).strip()


@dataclass
class Material:
    href: str
    theme: str
    weeks: str
    sort_key: tuple[int, int, str]


@dataclass
class Subject:
    dir_name: str
    year: str
    name: str
    affiliation: str
    materials: list[Material]


def parse_material(path: Path, subject_dir: Path) -> Material | None:
    """Read one lecture page, or return None if it is not one."""
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    stem = path.stem
    match = WEEK_RE.match(stem)

    theme = ""
    if h1 := H1_RE.search(source):
        theme = text_of(h1.group(1))
    if not theme and (title := TITLE_RE.search(source)):
        # `<title>theme | subject</title>` — keep the part before the divider.
        theme = text_of(title.group(1)).split("|")[0].strip()
    if not theme:
        theme = match.group(3) if match else stem

    if match:
        start = int(match.group(1))
        end = int(match.group(2)) if match.group(2) else start
        weeks = f"第{start}回" if start == end else f"第{start}–{end}回"
        sort_key = (0, start, stem)
    else:
        # Pages outside the `classNN_` convention still belong on the list;
        # sort them after the numbered ones instead of dropping them.
        weeks = ""
        sort_key = (1, 0, stem)

    return Material(
        href=path.relative_to(subject_dir).as_posix(),
        theme=theme,
        weeks=weeks,
        sort_key=sort_key,
    )


def parse_affiliation(pages: list[Path]) -> str:
    """Recover the school/department line shared by a subject's pages."""
    for path in pages:
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if eyebrow := EYEBROW_RE.search(source):
            # The eyebrow holds affiliation then subject, split by <br>.
            first = text_of(eyebrow.group(1)).split("\n")[0]
            if first:
                return first
    return ""


def collect(site_dir: Path) -> list[Subject]:
    subjects: list[Subject] = []

    for subject_dir in sorted(p for p in site_dir.iterdir() if p.is_dir()):
        pages = sorted(
            p
            for p in subject_dir.rglob("*.html")
            if p.name != "index.html" and "assets" not in p.relative_to(subject_dir).parts
        )
        if not pages:
            continue

        materials = [m for p in pages if (m := parse_material(p, subject_dir))]
        if not materials:
            continue
        materials.sort(key=lambda m: m.sort_key)

        match = SUBJECT_RE.match(subject_dir.name)
        year, name = (match.group(1), match.group(2)) if match else ("", subject_dir.name)

        subjects.append(
            Subject(
                dir_name=subject_dir.name,
                year=year,
                name=name,
                affiliation=parse_affiliation(pages),
                materials=materials,
            )
        )

    # Newest year first, then by subject name in the reading order of Japanese
    # text rather than by raw code point.
    subjects.sort(key=lambda s: (_negated_year(s.year), _collate(s.name)))
    return subjects


def _negated_year(year: str) -> int:
    return -int(year) if year.isdigit() else 0


def _collate(value: str) -> str:
    """Sort key that groups the kana forms of a name together."""
    return unicodedata.normalize("NFKC", value)


def e(value: str) -> str:
    return html.escape(value, quote=True)


def page(title: str, asset_prefix: str, body: str) -> str:
    """Wrap body markup in the shared page chrome."""
    css = f"{asset_prefix}material.css"
    icon = f"{asset_prefix}kousho.svg"
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<link rel="icon" href="{e(icon)}">
<link rel="stylesheet" href="{e(css)}">
</head>
<body>
<div class="wrap">
{body}
</div>
</body>
</html>
"""


def crest(asset_prefix: str) -> str:
    return (
        f'<img class="crest" src="{e(asset_prefix)}kousho.svg" alt="" aria-hidden="true">'
    )


def subject_index(subject: Subject) -> str:
    items = []
    for material in subject.materials:
        weeks = (
            f'<span class="idx-week">{e(material.weeks)}</span>' if material.weeks else ""
        )
        items.append(
            f'    <li><a class="idx-link" href="{e(material.href)}">{weeks}'
            f'<span class="idx-title">{e(material.theme)}</span></a></li>'
        )

    affiliation = (
        f"{crest('assets/')}{e(subject.affiliation)}<br>" if subject.affiliation else ""
    )
    year_line = f"{e(subject.year)}年度" if subject.year else ""
    count = len(subject.materials)

    body = f"""
<header class="doc-head">
  <p class="eyebrow">{affiliation}授業資料</p>
  <h1>{e(subject.name)}</h1>
  <p class="doc-meta">{year_line} ／ 全{count}件</p>
</header>

<section>
  <h2><span class="num">◆</span>資料一覧</h2>
  <ul class="idx-list">
{chr(10).join(items)}
  </ul>
</section>

<footer class="doc-foot">
  <p><a href="../">授業資料トップへ戻る</a></p>
</footer>
"""
    title = f"{subject.name} 授業資料一覧"
    return page(title, "assets/", body)


def root_index(subjects: list[Subject]) -> str:
    blocks = []
    for subject in subjects:
        items = []
        for material in subject.materials:
            href = f"{subject.dir_name}/{material.href}"
            weeks = (
                f'<span class="idx-week">{e(material.weeks)}</span>'
                if material.weeks
                else ""
            )
            items.append(
                f'      <li><a class="idx-link" href="{e(href)}">{weeks}'
                f'<span class="idx-title">{e(material.theme)}</span></a></li>'
            )

        heading = e(subject.name)
        year_badge = (
            f'<span class="idx-year">{e(subject.year)}年度</span>' if subject.year else ""
        )
        affiliation = (
            f'  <p class="idx-affil">{e(subject.affiliation)}</p>'
            if subject.affiliation
            else ""
        )
        blocks.append(
            f"""<section>
  <h2><span class="num">{year_badge}</span>{heading}</h2>
{affiliation}
    <ul class="idx-list">
{chr(10).join(items)}
    </ul>
  <p class="idx-more"><a href="{e(subject.dir_name)}/">{heading}の一覧ページ</a></p>
</section>"""
        )

    empty = '<section><p>公開中の資料はありません。</p></section>'
    body = f"""
<header class="doc-head">
  <p class="eyebrow">{crest('')}弓削商船高等専門学校</p>
  <h1>授業資料</h1>
  <p class="doc-meta">担当: 瀬尾 敦生</p>
</header>

{chr(10).join(blocks) if blocks else empty}

<footer class="doc-foot">
  <p>本サイトは授業で使用する解説資料を公開しています。</p>
</footer>
"""
    return page("授業資料 | 弓削商船高等専門学校", "", body)


def pick_root_assets(site_dir: Path, subjects: list[Subject]) -> None:
    """Place a copy of the shared assets at the site root for the root index."""
    if not subjects:
        return
    source = site_dir / subjects[0].dir_name / "assets"
    for name in ("material.css", "kousho.svg", "index.css"):
        candidate = source / name
        if candidate.is_file():
            (site_dir / name).write_bytes(candidate.read_bytes())


INDEX_CSS = """
/* Index-page additions layered on top of material.css. */

.idx-list { list-style: none; padding-left: 0; margin: 0.6rem 0 0; }

.idx-list li { margin: 0.35rem 0; }

.idx-link {
  display: flex;
  gap: 0.7rem;
  align-items: baseline;
  padding: 0.55rem 0.7rem;
  border: 1px solid var(--c-line);
  border-radius: 0.35rem;
  background: var(--c-bg);
  color: var(--c-text);
  text-decoration: none;
  font-size: 0.88rem;
  line-height: 1.6;
}

.idx-link:hover {
  border-color: var(--c-accent);
  background: var(--c-accent-soft);
}

.idx-link:focus-visible {
  outline: 3px solid var(--c-accent);
  outline-offset: 2px;
}

.idx-week {
  flex: none;
  min-width: 5.2rem;
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--c-accent);
  font-variant-numeric: tabular-nums;
}

.idx-title { flex: 1; }

.idx-year {
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--c-accent);
  font-variant-numeric: tabular-nums;
}

h2 .num:has(.idx-year) { min-width: 4.6rem; }

.idx-affil {
  font-size: 0.78rem;
  color: var(--c-muted);
  margin: 0;
}

.idx-more { margin: 0.9rem 0 0; font-size: 0.8rem; }

.idx-more a, footer.doc-foot a { color: var(--c-accent); }

@media (max-width: 600px) {
  .idx-link { flex-direction: column; gap: 0.15rem; }
  .idx-week { min-width: 0; }
}
"""


def write_index_css(site_dir: Path, subjects: list[Subject]) -> None:
    """Append the index styles to each stylesheet the index pages load."""
    targets = [site_dir / "material.css"]
    targets += [site_dir / s.dir_name / "assets" / "material.css" for s in subjects]

    marker = "/* Index-page additions layered on top of material.css. */"
    for target in targets:
        if not target.is_file():
            continue
        current = target.read_text(encoding="utf-8")
        if marker in current:
            continue
        target.write_text(current.rstrip() + "\n" + INDEX_CSS, encoding="utf-8")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {Path(argv[0]).name} SITE_DIR", file=sys.stderr)
        return 2

    site_dir = Path(argv[1])
    if not site_dir.is_dir():
        print(f"not a directory: {site_dir}", file=sys.stderr)
        return 1

    subjects = collect(site_dir)

    pick_root_assets(site_dir, subjects)
    write_index_css(site_dir, subjects)

    (site_dir / "index.html").write_text(root_index(subjects), encoding="utf-8")
    print(f"wrote: index.html ({len(subjects)} subjects)")

    for subject in subjects:
        target = site_dir / subject.dir_name / "index.html"
        target.write_text(subject_index(subject), encoding="utf-8")
        print(f"wrote: {subject.dir_name}/index.html ({len(subject.materials)} pages)")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
