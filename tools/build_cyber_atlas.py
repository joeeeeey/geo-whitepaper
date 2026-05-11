#!/usr/bin/env python3
"""Post-process docs/pages/*.md into the Cyber Atlas Jekyll site.

For each chapter file we:
  1. Strip the inherited "上一页 | 目录 | 下一页" footer paragraph.
  2. Inject Jekyll frontmatter (layout, section, ord, prev/next, read time, word count).
For the site as a whole we:
  3. Emit _data/structure.yml (sections + flattened page list).
  4. Generate one Markdown section landing page per section under docs/sections/.

Idempotent: running again on already-processed files only refreshes the frontmatter
block, never touching the body text below the closing ``---``.
"""
from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - PyYAML is in stdlib of most CI envs
    yaml = None


# ---------- Section classification ----------
# Each tuple: (page_num_min, page_num_max_inclusive)
SECTIONS = [
    {
        "id": "01",
        "slug": "learning-guide",
        "name": "学习指南",
        "short": "学习",
        "headline": "从 SEO 到 GEO：基础认知",
        "blurb": "为什么需要 GEO、它和传统 SEO 的差别、商业价值与底层逻辑——所有学习者的起点。",
        "range": (1, 11),
        "color": "#7eff9e",
        "angle_deg": -120,
        "radius": 170,
    },
    {
        "id": "02",
        "slug": "geo-qa",
        "name": "GEO 问答",
        "short": "问答",
        "headline": "九个层面，理解 GEO 全貌",
        "blurb": "从基础认知到行业应用、效果衡量与未来趋势——一份覆盖九个维度的系统性问答。",
        "range": (12, 20),
        "color": "#b194ff",
        "angle_deg": -60,
        "radius": 200,
    },
    {
        "id": "03",
        "slug": "compliance",
        "name": "GEO 合规",
        "short": "合规",
        "headline": "2026 合规治理：风险与资产",
        "blurb": "从 315 晚会案例到组织保障与技术机制——GEO 合规不只是防御，更是品牌资产。",
        "range": (21, 28),
        "color": "#ffc46b",
        "angle_deg": 0,
        "radius": 210,
    },
    {
        "id": "04",
        "slug": "field-notes",
        "name": "GEO 随记",
        "short": "随记",
        "headline": "实战手记：策略、监测与方法论",
        "blurb": "围绕监测指标、内容方法论、平台机会与一线经验展开的实战随笔。",
        "range": (29, 42),
        "color": "#ff8fb5",
        "angle_deg": 60,
        "radius": 200,
    },
    {
        "id": "05",
        "slug": "papers",
        "name": "GEO 论文",
        "short": "论文",
        "headline": "学术视角：GEO 与生成式信息检索",
        "blurb": "十余篇与 GEO 直接相关的前沿论文摘读：从 Search-o1 到 RAG，从信任研究到电商搜索。",
        "range": (43, 55),
        "color": "#9cc7ff",
        "angle_deg": 120,
        "radius": 200,
    },
    {
        "id": "06",
        "slug": "cases-and-refs",
        "name": "案例与参考",
        "short": "案例",
        "headline": "海内外案例 + AI 论文深读",
        "blurb": "国内外 GEO 实战案例与 AI 时代关键论文（Transformer、WebGPT、RAG、Word2Vec 等）的人话解读合集。",
        "range": (56, 84),
        "color": "#6ef3ff",
        "angle_deg": -180,
        "radius": 170,
    },
]

# Pages picked for the homepage "featured" grid.
FEATURED = {2, 6, 21, 22, 30, 35, 44, 57, 81}


PAGE_FILE_RE = re.compile(r"^(\d{3})-(.+)\.md$")
FRONTMATTER_RE = re.compile(r"\A---\s*\n.*?\n---\s*\n", re.DOTALL)
PAGER_LINE_RE = re.compile(r"^.*\|?\s*\[目录\]\([^)]+\)\s*\|.*$", re.MULTILINE)
TRAILING_HR_RE = re.compile(r"\n---\s*\n\s*$", re.DOTALL)
# A standalone numbered-list line that is really a Q&A section heading:
#   "1. 什么是 X？"  →  "## 什么是 X？"
# Heuristic: the paragraph is a single line matching `1. TEXT?` where the question
# mark (CJK or ASCII) signals it's a heading, not a list-item embedded in prose.
QA_HEAD_RE = re.compile(r"(?m)^([0-9]+)\.\s+(.+?[？\?])\s*$")


def find_section(num: int) -> dict | None:
    for s in SECTIONS:
        lo, hi = s["range"]
        if lo <= num <= hi:
            return s
    return None


def page_title_from_file(path: Path) -> str:
    # Match the H1 if present; fall back to the filename stem.
    text = path.read_text(encoding="utf-8")
    body = FRONTMATTER_RE.sub("", text, count=1)
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    stem = path.stem
    m = PAGE_FILE_RE.match(path.name)
    if m:
        return m.group(2).replace("-", " ").strip()
    return stem


def estimate_read_min(body: str) -> tuple[int, int]:
    # Chinese: ~450 chars/min, ignoring whitespace.
    cleaned = re.sub(r"\s+", "", body)
    chars = len(cleaned)
    minutes = max(2, round(chars / 450))
    return minutes, chars


def slug_for_chapter(num: int, name: str) -> str:
    # Mirror the existing filename → URL mapping (Jekyll's pretty permalink).
    safe = re.sub(r"[\\s/:：*?\"<>|]+", "-", name).strip("-")
    return f"{num:03d}-{safe}"


def write_yaml(path: Path, data: object) -> None:
    if yaml is None:
        # Fallback: write a minimal subset; should not be needed in CI.
        raise SystemExit("PyYAML required (pip install pyyaml)")
    path.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


def promote_qa_headings(text: str) -> str:
    """Promote orphan ``1. 什么是 X？`` paragraphs into ``## 什么是 X？`` H2 headings.

    The Feishu export renders Q&A section titles as one-item ordered lists; that
    fights the article layout (no outline entries, ugly inline numbers). We promote
    them to real H2s only when the paragraph is a single line ending with a question
    mark — that's the safe, surgical signal we have.
    """
    # Split on blank-line paragraph boundaries.
    paragraphs = re.split(r"(\n\s*\n)", text)
    out: list[str] = []
    for chunk in paragraphs:
        if "\n" in chunk.strip() or not chunk.strip():
            out.append(chunk)
            continue
        m = QA_HEAD_RE.fullmatch(chunk.strip())
        if m and m.group(2).endswith(("?", "？")):
            out.append("## " + m.group(2))
        else:
            out.append(chunk)
    return "".join(out)


def clean_body(text: str) -> tuple[str, str]:
    """Strip frontmatter (if any) and inherited pager line.

    Returns (body, h1_title).
    """
    text = FRONTMATTER_RE.sub("", text, count=1)
    # Drop the trailing "上一页 | [目录](../index.md) | 下一页" paragraph.
    text = PAGER_LINE_RE.sub("", text)
    # Remove dangling separator that wrapped the pager line.
    lines = text.splitlines()
    while lines and lines[-1].strip() in {"", "---"}:
        lines.pop()
    text = "\n".join(lines) + "\n"
    # Strip the H1 from the body — the layout supplies it.
    h1_title = ""
    new_lines: list[str] = []
    h1_done = False
    for line in text.splitlines():
        if not h1_done and line.startswith("# "):
            h1_title = line[2:].strip()
            h1_done = True
            continue
        new_lines.append(line)
    body = "\n".join(new_lines).lstrip("\n")
    body = promote_qa_headings(body)
    return body, h1_title


def build(docs_dir: Path) -> None:
    pages_dir = docs_dir / "pages"
    if not pages_dir.is_dir():
        raise SystemExit(f"missing {pages_dir}")

    md_paths = sorted(p for p in pages_dir.glob("*.md") if PAGE_FILE_RE.match(p.name))
    if not md_paths:
        raise SystemExit("no chapter pages found")

    pages_meta: list[dict] = []
    sections_data: dict[str, dict] = {s["id"]: dict(s, count=0, read_min=0) for s in SECTIONS}

    # First pass: read & classify.
    raw: list[dict] = []
    for path in md_paths:
        m = PAGE_FILE_RE.match(path.name)
        assert m is not None
        num = int(m.group(1))
        text = path.read_text(encoding="utf-8")
        body, h1_title = clean_body(text)
        title = h1_title or m.group(2)
        read_min, word_count = estimate_read_min(body)
        sec = find_section(num)
        if sec is None:
            raise SystemExit(f"page {num} is outside any section range")
        raw.append(
            {
                "path": path,
                "num": num,
                "title": title,
                "body": body,
                "read_min": read_min,
                "word_count": word_count,
                "section": sec,
            }
        )

    # Second pass: compute ord ("01.3") per section.
    within_idx: dict[str, int] = {}
    for entry in raw:
        sid = entry["section"]["id"]
        within_idx[sid] = within_idx.get(sid, 0) + 1
        entry["ord"] = f"{sid}.{within_idx[sid]}"
        sec = sections_data[sid]
        sec["count"] += 1
        sec["read_min"] += entry["read_min"]

    # Third pass: write frontmatter back, link prev/next.
    for i, entry in enumerate(raw):
        path = entry["path"]
        sec = entry["section"]
        prev_entry = raw[i - 1] if i > 0 else None
        next_entry = raw[i + 1] if i + 1 < len(raw) else None

        url = "/pages/" + path.stem + "/"

        fm: dict = {
            "layout": "article",
            "title": entry["title"],
            "permalink": url,
            "page_num": entry["num"],
            "section_id": sec["id"],
            "section_name": sec["name"],
            "section_slug": sec["slug"],
            "ord": entry["ord"],
            "read_min": entry["read_min"],
            "word_count": entry["word_count"],
            "is_featured": entry["num"] in FEATURED,
        }
        if prev_entry:
            fm["prev_url"] = "/pages/" + prev_entry["path"].stem + "/"
            fm["prev_title"] = prev_entry["title"]
        if next_entry:
            fm["next_url"] = "/pages/" + next_entry["path"].stem + "/"
            fm["next_title"] = next_entry["title"]

        # Write back: YAML frontmatter + body
        rendered = "---\n" + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False) + "---\n\n" + entry["body"].lstrip("\n")
        path.write_text(rendered, encoding="utf-8")
        pages_meta.append(
            {
                "num": entry["num"],
                "title": entry["title"],
                "ord": entry["ord"],
                "section_id": sec["id"],
                "section_name": sec["name"],
                "section_slug": sec["slug"],
                "url": url,
                "read_min": entry["read_min"],
                "word_count": entry["word_count"],
                "is_featured": entry["num"] in FEATURED,
                "tag": "核心" if entry["num"] in FEATURED else "阅读",
            }
        )

    # Build structure data for Liquid.
    structure_sections = []
    for s in SECTIONS:
        sid = s["id"]
        sec = sections_data[sid]
        first_in_section = next((p for p in pages_meta if p["section_id"] == sid), None)
        structure_sections.append(
            {
                "id": sid,
                "slug": s["slug"],
                "name": s["name"],
                "short": s["short"],
                "headline": s["headline"],
                "blurb": s["blurb"],
                "color": s["color"],
                "count": sec["count"],
                "read_hours": max(1, round(sec["read_min"] / 60)),
                "angle": round(math.radians(s["angle_deg"]), 4),
                "radius": s["radius"],
                "first_chapter_url": first_in_section["url"] if first_in_section else None,
                "first_chapter_title": first_in_section["title"] if first_in_section else None,
                "first_chapter_ord": first_in_section["ord"] if first_in_section else None,
            }
        )

    total_read_min = sum(p["read_min"] for p in pages_meta)
    structure = {
        "sections": structure_sections,
        "pages": pages_meta,
        "total_read_minutes": total_read_min,
        "total_read_hours": max(1, round(total_read_min / 60)),
    }

    data_dir = docs_dir / "_data"
    data_dir.mkdir(parents=True, exist_ok=True)
    write_yaml(data_dir / "structure.yml", structure)

    # Generate section landing pages.
    sections_dir = docs_dir / "sections"
    sections_dir.mkdir(parents=True, exist_ok=True)
    for s in structure_sections:
        sec_path = sections_dir / f"{s['slug']}.md"
        fm = {
            "layout": "section",
            "title": s["name"],
            "permalink": f"/sections/{s['slug']}/",
            "section_id": s["id"],
            "section_slug": s["slug"],
            "section_headline": s["headline"],
            "section_blurb": s["blurb"],
            "chapter_count": s["count"],
            "first_chapter_url": s["first_chapter_url"],
            "first_chapter_title": s["first_chapter_title"],
            "first_chapter_ord": s["first_chapter_ord"],
        }
        sec_path.write_text(
            "---\n" + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False) + "---\n",
            encoding="utf-8",
        )

    # Remove the obsolete legacy index.md (we now have index.html).
    legacy_index = docs_dir / "index.md"
    if legacy_index.exists():
        legacy_index.unlink()

    print(f"processed {len(raw)} pages, {len(SECTIONS)} sections")
    for s in structure_sections:
        print(f"  {s['id']} {s['name']}: {s['count']} 章, ~{s['read_hours']}h")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--docs", default="docs", help="path to docs/")
    args = parser.parse_args(argv)
    build(Path(args.docs).resolve())
    return 0


if __name__ == "__main__":
    sys.exit(main())
