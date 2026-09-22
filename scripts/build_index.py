#!/usr/bin/env python3
"""Generate index pages for the GitHub Pages site.

Builds three levels of listing — years at the site root, subjects under each
year, and material pages under each subject — all styled with the shared
`material.css` so they read as part of the same publication as the lecture
pages themselves.

Metadata is recovered from each page's existing markup (`<title>`, the
`.eyebrow` affiliation line, `<h1>`) rather than from a separate manifest, so
pages written by hand are listed on equal terms with generated ones.

Usage:
    build_index.py SITE_DIR

SITE_DIR is the staged site (`<year>/<subject>/` directories), not the
repository's `output/`, where year and subject share one directory name.
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
YEAR_RE = re.compile(r"^\d{4}$")

TITLE_RE = re.compile(r"<title>(.*?)</title>", re.DOTALL | re.IGNORECASE)
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.DOTALL | re.IGNORECASE)
EYEBROW_RE = re.compile(
    r'<p class="eyebrow"[^>]*>(.*?)</p>', re.DOTALL | re.IGNORECASE
)
TAG_RE = re.compile(r"<[^>]+>")

SCHOOL = "弓削商船高等専門学校"


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
    name: str
    affiliation: str
    materials: list[Material]


@dataclass
class Year:
    dir_name: str
    subjects: list[Subject]


def parse_material(path: Path, subject_dir: Path) -> Material | None:
    """Read one lecture page, or return None if it cannot be read."""
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


def collect_subject(subject_dir: Path) -> Subject | None:
    pages = sorted(
        p
        for p in subject_dir.rglob("*.html")
        if p.name != "index.html"
        and "assets" not in p.relative_to(subject_dir).parts
    )
    if not pages:
        return None

    materials = [m for p in pages if (m := parse_material(p, subject_dir))]
    if not materials:
        return None
    materials.sort(key=lambda m: m.sort_key)

    return Subject(
        dir_name=subject_dir.name,
        name=subject_dir.name,
        affiliation=parse_affiliation(pages),
        materials=materials,
    )


def collect(site_dir: Path) -> list[Year]:
    years: list[Year] = []

    for year_dir in sorted(p for p in site_dir.iterdir() if p.is_dir()):
        if not YEAR_RE.match(year_dir.name):
            continue

        subjects = [
            s
            for d in sorted(p for p in year_dir.iterdir() if p.is_dir())
            if (s := collect_subject(d))
        ]
        if not subjects:
            continue

        subjects.sort(key=lambda s: _collate(s.name))
        years.append(Year(dir_name=year_dir.name, subjects=subjects))

    years.sort(key=lambda y: y.dir_name, reverse=True)
    return years


def _collate(value: str) -> str:
    """Sort key that groups the kana forms of a name together."""
    return unicodedata.normalize("NFKC", value)


def e(value: str) -> str:
    return html.escape(value, quote=True)


def page(title: str, asset_prefix: str, body: str) -> str:
    """Wrap body markup in the shared page chrome."""
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<link rel="icon" href="{e(asset_prefix)}kousho.svg">
<link rel="stylesheet" href="{e(asset_prefix)}material.css">
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


def crumbs(trail: list[tuple[str, str]]) -> str:
    """Render the ancestor trail; the current page is not a link."""
    parts = [f'<a href="{e(href)}">{e(label)}</a>' for label, href in trail]
    return f'<nav class="idx-crumbs">{" ／ ".join(parts)}</nav>'


def material_items(materials: list[Material], prefix: str, indent: str) -> str:
    items = []
    for material in materials:
        weeks = (
            f'<span class="idx-week">{e(material.weeks)}</span>' if material.weeks else ""
        )
        items.append(
            f'{indent}<li><a class="idx-link" href="{e(prefix + material.href)}">{weeks}'
            f'<span class="idx-title">{e(material.theme)}</span></a></li>'
        )
    return "\n".join(items)


def subject_index(year: Year, subject: Subject) -> str:
    affiliation = (
        f"{crest('assets/')}{e(subject.affiliation)}<br>" if subject.affiliation else ""
    )
    body = f"""
{crumbs([("授業資料", "../../"), (f"{year.dir_name}年度", "../")])}

<header class="doc-head">
  <p class="eyebrow">{affiliation}授業資料</p>
  <h1>{e(subject.name)}</h1>
  <p class="doc-meta">{e(year.dir_name)}年度 ／ 全{len(subject.materials)}件</p>
</header>

<section>
  <h2><span class="num">◆</span>資料一覧</h2>
  <ul class="idx-list">
{material_items(subject.materials, "", "    ")}
  </ul>
</section>

<footer class="doc-foot">
  <p><a href="../">{e(year.dir_name)}年度の科目一覧へ戻る</a></p>
</footer>
"""
    return page(f"{subject.name} 授業資料一覧", "assets/", body)


def year_index(year: Year) -> str:
    blocks = []
    for subject in year.subjects:
        heading = e(subject.name)
        affiliation = (
            f'  <p class="idx-affil">{e(subject.affiliation)}</p>'
            if subject.affiliation
            else ""
        )
        blocks.append(
            f"""<section>
  <h2><span class="num">◆</span>{heading}</h2>
{affiliation}
  <ul class="idx-list">
{material_items(subject.materials, f"{subject.dir_name}/", "    ")}
  </ul>
  <p class="idx-more"><a href="{e(subject.dir_name)}/">{heading}の一覧ページ</a></p>
</section>"""
        )

    body = f"""
{crumbs([("授業資料", "../")])}

<header class="doc-head">
  <p class="eyebrow">{crest('')}{SCHOOL}</p>
  <h1>{e(year.dir_name)}年度 授業資料</h1>
  <p class="doc-meta">全{len(year.subjects)}科目</p>
</header>

{chr(10).join(blocks)}

<footer class="doc-foot">
  <p><a href="../">年度一覧へ戻る</a></p>
</footer>
"""
    return page(f"{year.dir_name}年度 授業資料 | {SCHOOL}", "", body)


def root_index(years: list[Year]) -> str:
    blocks = []
    for year in years:
        items = []
        for subject in year.subjects:
            href = f"{year.dir_name}/{subject.dir_name}/"
            count = len(subject.materials)
            items.append(
                f'    <li><a class="idx-link" href="{e(href)}">'
                f'<span class="idx-title">{e(subject.name)}</span>'
                f'<span class="idx-count">{count}件</span></a></li>'
            )
        blocks.append(
            f"""<section>
  <h2><span class="num">◆</span>{e(year.dir_name)}年度</h2>
  <ul class="idx-list">
{chr(10).join(items)}
  </ul>
  <p class="idx-more"><a href="{e(year.dir_name)}/">{e(year.dir_name)}年度の一覧ページ</a></p>
</section>"""
        )

    empty = "<section><p>公開中の資料はありません。</p></section>"
    body = f"""
<header class="doc-head">
  <p class="eyebrow">{crest('')}{SCHOOL}</p>
  <h1>授業資料</h1>
</header>

{chr(10).join(blocks) if blocks else empty}

<footer class="doc-foot">
  <p>{crest('')}{SCHOOL}</p>
</footer>
"""
    return page(f"授業資料 | {SCHOOL}", "", body)


INDEX_CSS = """
/* Index-page additions layered on top of material.css. */

.idx-crumbs {
  font-size: 0.75rem;
  color: var(--c-muted);
  padding: 1.2rem 0 0;
}

.idx-crumbs a { color: var(--c-accent); }

.idx-crumbs + .doc-head { padding-top: 0.6rem; }

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

.idx-count {
  flex: none;
  font-size: 0.76rem;
  color: var(--c-muted);
  font-variant-numeric: tabular-nums;
}

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


def stylesheet_targets(site_dir: Path, years: list[Year]) -> list[Path]:
    targets = [site_dir / "material.css"]
    for year in years:
        targets.append(site_dir / year.dir_name / "material.css")
        for subject in year.subjects:
            targets.append(
                site_dir / year.dir_name / subject.dir_name / "assets" / "material.css"
            )
    return targets


def place_shared_assets(site_dir: Path, years: list[Year]) -> None:
    """Copy the shared assets to each level that has an index page."""
    if not years:
        return
    first = years[0]
    source = site_dir / first.dir_name / first.subjects[0].dir_name / "assets"

    destinations = [site_dir] + [site_dir / y.dir_name for y in years]
    for name in ("material.css", "kousho.svg"):
        candidate = source / name
        if not candidate.is_file():
            continue
        payload = candidate.read_bytes()
        for destination in destinations:
            (destination / name).write_bytes(payload)


def write_index_css(site_dir: Path, years: list[Year]) -> None:
    """Append the index styles to each stylesheet the index pages load."""
    marker = "/* Index-page additions layered on top of material.css. */"
    for target in stylesheet_targets(site_dir, years):
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

    years = collect(site_dir)

    place_shared_assets(site_dir, years)
    write_index_css(site_dir, years)

    (site_dir / "index.html").write_text(root_index(years), encoding="utf-8")
    print(f"wrote: index.html ({len(years)} years)")

    for year in years:
        target = site_dir / year.dir_name / "index.html"
        target.write_text(year_index(year), encoding="utf-8")
        print(f"wrote: {year.dir_name}/index.html ({len(year.subjects)} subjects)")

        for subject in year.subjects:
            target = site_dir / year.dir_name / subject.dir_name / "index.html"
            target.write_text(subject_index(year, subject), encoding="utf-8")
            print(
                f"wrote: {year.dir_name}/{subject.dir_name}/index.html "
                f"({len(subject.materials)} pages)"
            )

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
