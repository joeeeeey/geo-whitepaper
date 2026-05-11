#!/usr/bin/env python3
import argparse
import json
import re
import shutil
from pathlib import Path
from typing import Optional


DOC_ID = "Jv85dXAeZoKJ7exJi4Yc4Edrnhf"


def text_from_block(block: dict) -> str:
    data = block.get("data", {})
    text = data.get("text", {})
    initial = text.get("initialAttributedTexts", {}).get("text", {})
    if isinstance(initial, dict):
        return "".join(str(initial[key]) for key in sorted(initial.keys(), key=lambda x: int(x) if str(x).isdigit() else str(x))).strip()
    if isinstance(initial, str):
        return initial.strip()
    return ""


def slugify(value: str, fallback: str) -> str:
    value = re.sub(r"[\\s/\\\\:：*?\"<>|]+", "-", value.strip())
    value = re.sub(r"-+", "-", value).strip("-")
    return value[:90] or fallback


def collect_order(block_map: dict, root_id: str) -> list[str]:
    root = block_map.get(root_id)
    if not root:
        return [key for key in block_map.keys() if key != root_id]

    ordered = []

    def visit(block_id: str):
        if block_id != root_id:
            ordered.append(block_id)
        for child_id in block_map.get(block_id, {}).get("data", {}).get("children", []) or []:
            visit(child_id)

    for child_id in root.get("data", {}).get("children", []) or []:
        visit(child_id)
    return ordered


def block_to_markdown(block: dict, block_map: dict) -> str:
    data = block.get("data", {})
    typ = data.get("type")
    text = text_from_block(block)

    if typ == "heading1":
        return f"# {text}" if text else ""
    if typ == "heading2":
        return f"## {text}" if text else ""
    if typ == "heading3":
        return f"### {text}" if text else ""
    if typ == "heading4":
        return f"#### {text}" if text else ""
    if typ == "heading5":
        return f"##### {text}" if text else ""
    if typ == "heading6":
        return f"###### {text}" if text else ""
    if typ == "bullet":
        return f"- {text}" if text else ""
    if typ == "ordered":
        return f"1. {text}" if text else ""
    if typ == "divider":
        return "---"
    if typ == "callout":
        return f"> {text}" if text else "> [callout]"
    if typ == "table":
        rows = []
        for child_id in data.get("children", []) or []:
            child = block_map.get(child_id, {})
            cell_text = text_from_block(child)
            if cell_text:
                rows.append(cell_text)
        if rows:
            return "\n".join(f"| {row} |" for row in rows)
        return ""
    if typ == "table_cell":
        return text
    if typ == "image":
        return "![image]()"
    if typ in {"isv"}:
        return f"> [{typ} block omitted]"
    if typ == "text":
        return text
    return text


def normalize_lines(lines: list[str]) -> str:
    output = []
    previous_blank = False
    for line in lines:
        line = line.rstrip()
        blank = not line
        if blank and previous_blank:
            continue
        output.append(line)
        previous_blank = blank
    return "\n".join(output).strip() + "\n"


def navigation(previous_page: Optional[dict], next_page: Optional[dict]) -> list:
    prev_link = f"[上一页]({previous_page['filename']})" if previous_page else "上一页"
    next_link = f"[下一页]({next_page['filename']})" if next_page else "下一页"
    return [f"{prev_link} | [目录](../index.md) | {next_link}", ""]


def split_long_sections(sections: list, max_content_lines: int) -> list:
    split_sections = []
    for section in sections:
        content = section["lines"][2:]
        chunks = []
        current = []
        for line in content:
            if len(current) >= max_content_lines and not line.strip():
                chunks.append(current)
                current = []
                continue
            current.append(line)
        if current:
            chunks.append(current)

        if len(chunks) <= 1:
            split_sections.append(section)
            continue

        for index, chunk in enumerate(chunks, start=1):
            split_sections.append(
                {
                    "title": f"{section['title']}（{index}/{len(chunks)}）",
                    "group": section["group"],
                    "filename": "",
                    "lines": [f"# {section['title']}（{index}/{len(chunks)}）", ""] + chunk,
                }
            )
    return split_sections


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert merged Feishu blocks to Markdown.")
    parser.add_argument("--raw", default="raw/merged_blocks.json")
    parser.add_argument("--docs", default="docs")
    args = parser.parse_args()

    raw = json.loads(Path(args.raw).read_text())
    block_map = raw["block_map"]
    root_id = raw.get("doc_id", DOC_ID)
    out_dir = Path(args.docs)
    pages_dir = out_dir / "pages"
    out_dir.mkdir(parents=True, exist_ok=True)
    if pages_dir.exists():
        shutil.rmtree(pages_dir)
    stale_chapters = out_dir / "chapters"
    if stale_chapters.exists():
        shutil.rmtree(stale_chapters)
    pages_dir.mkdir(parents=True, exist_ok=True)

    title = "《GEO白皮书：AI搜索时代的品牌增长新范式》"
    order = collect_order(block_map, root_id)
    sections = []
    current = None
    current_group = "文档说明"

    def start_section(heading: str, group: str):
        filename = f"{len(sections) + 1:03d}-{slugify(heading, str(len(sections) + 1))}.md"
        section = {
            "title": heading,
            "group": group,
            "filename": filename,
            "lines": [f"# {heading}", ""],
        }
        sections.append(section)
        return section

    current = start_section("文档说明", current_group)

    for block_id in order:
        block = block_map.get(block_id)
        if not block:
            continue
        typ = block.get("data", {}).get("type")
        md = block_to_markdown(block, block_map)
        if not md:
            continue

        if typ == "heading1":
            current_group = text_from_block(block) or current_group
            current["lines"].extend([f"## {current_group}", ""])
            continue

        if typ in {"heading2", "heading3"}:
            heading = text_from_block(block)
            current = start_section(heading, current_group)
            continue

        current["lines"].extend([md, ""])

    sections = [section for section in sections if len([line for line in section["lines"] if line.strip()]) > 1]
    sections = split_long_sections(sections, max_content_lines=260)
    for index, section in enumerate(sections, start=1):
        section["filename"] = f"{index:03d}-{slugify(section['title'], str(index))}.md"

    index_lines = [
        f"# {title}",
        "",
        f"- 来源文档：`{root_id}`",
        f"- Block 数量：`{len(block_map)}`",
        f"- 拆分页数：`{len(sections)}`",
        "",
        "## 页面目录",
        "",
    ]
    last_group = None
    for section in sections:
        if section["group"] != last_group:
            index_lines.extend([f"### {section['group']}", ""])
            last_group = section["group"]
        index_lines.append(f"- [{section['title']}](pages/{section['filename']})")
    (out_dir / "index.md").write_text(normalize_lines(index_lines))

    summary_lines = [
        "# 文档目录",
        "",
        f"- 来源文档：{root_id}",
        f"- Block 数量：{len(block_map)}",
        f"- 页面数量：{len(sections)}",
        "",
        "## 页面",
        "",
    ]
    for section in sections:
        summary_lines.append(f"- [{section['title']}](pages/{section['filename']})")
    (out_dir / "README.md").write_text(normalize_lines(summary_lines))

    for index, section in enumerate(sections):
        previous_page = sections[index - 1] if index > 0 else None
        next_page = sections[index + 1] if index + 1 < len(sections) else None
        page_lines = section["lines"][:]
        page_lines.extend(["---", ""])
        page_lines.extend(navigation(previous_page, next_page))
        (pages_dir / section["filename"]).write_text(normalize_lines(page_lines))

    print(f"wrote {out_dir / 'index.md'} and {len(sections)} page files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
